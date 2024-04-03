import mysql.connector
from mysql.connector import Error
import configparser
import requests
from datetime import datetime
import time
from distutils.util import strtobool
import os
from Game import Game
from Genre import Genre

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config_path = 'config.ini'
create_tables_file = 'sql/create_tables.sql'
db_name = 'soen_project_phase_1'

settings = configparser.ConfigParser()
settings.read('settings.ini')


def main():
    config = configparser.ConfigParser()
    config.read(config_path)

    db_config = {
        'user': config.get('database', 'user'),
        'password': config.get('database', 'password'),
        'host': config.get('database', 'host'),
        'raise_on_warnings': config.getboolean('database', 'raise_on_warnings')
    }

    try:
        should_drop_existing_db = bool(strtobool(settings.get('DATABASE', 'drop_existing')))

        if should_drop_existing_db:
            connection = create_connection(db_config)
            drop_existing_db(connection)
            close_connection(connection)

        connection = create_connection(db_config)

        if database_exists(connection) is False:
            create_database(connection)
            create_tables(connection)
        else:
            use_table(connection)

        populate_database(connection)
        close_connection(connection)

        print("Statements executed successfully.")
    except Error as e:
        print("Error while connecting to MySQL", e)


def drop_existing_db(connection):
    cursor = connection.cursor()

    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
    except mysql.connector.Error as err:
        if err.errno == 1008:
            pass
        else:
            raise


def database_exists(connection):
    cursor = connection.cursor()
    cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{db_name}';")
    exists = cursor.fetchone()

    if exists:
        return True
    else:
        return False


def create_database(connection):
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE {db_name};")


def create_tables(connection):
    cursor = connection.cursor()
    use_table(connection)

    with open(create_tables_file, 'r') as file:
        sql_query = file.read()

    for result in cursor.execute(sql_query, multi=True):
        if result.with_rows:
            print(result.fetchall())


def use_table(connection):
    cursor = connection.cursor()
    cursor.execute(f"USE {db_name};")


def populate_database(connection):
    use_table(connection)
    insert_igdb_games(connection)


def insert_igdb_games(connection):
    num_pages_to_process = int(settings.get('IGDB_SETTINGS', 'num_pages_to_process'))
    limit_num_games = int(settings.get('IGDB_SETTINGS', 'limit_num_games'))
    start_page = int(settings.get('IGDB_SETTINGS', 'start_page'))

    for i in range(start_page-1, num_pages_to_process):
        url = "https://api.igdb.com/v4/games/"

        headers = {
            'Client-ID': settings.get('API_KEYS', 'igdb_client_id'),
            'Authorization': "Bearer " + settings.get('API_KEYS', 'igdb_bearer'),
        }

        page_offset = i*limit_num_games

        request_data = f'fields name, summary, url, genres.name, release_dates.date, platforms, platforms.name, platforms.platform_family, platforms.platform_family.name; limit {str(limit_num_games)}; offset {str(page_offset)};'

        print('New request: '+request_data)

        response = requests.post(url, headers=headers, data=request_data)

        if response.status_code == 200:
            games = response.json()

            for game in games:
                release_dates = game.get('release_dates', [])

                # Ignore IGDB games that don't have a release date (we need this to link to Rawg)
                if not release_dates or len(release_dates) == 0: continue

                release_timestamp = release_dates[0].get('date')

                if not release_timestamp: continue

                release_date = datetime.utcfromtimestamp(release_timestamp).strftime('%Y-%m-%d')
                game_name = game.get('name', 'N/A')
                igdb_id = game['id']
                summary = game.get('summary', '')
                url = game.get('url', '')

                game_obj = Game(game_name, summary, url, release_date, igdb_id, rawg_id=None)

                internal_game_id = insert_game_to_db(connection, game_obj)

                # Keep track of our internal id to use when referencing in the platform_game relationship
                game['internal_game_id'] = internal_game_id

                igdb_genres = game.get('genres')
                genres = [Genre(igdb_genre['id'], None, igdb_genre['name']) for igdb_genre in igdb_genres] if igdb_genres else []
                insert_genre_info(connection, internal_game_id, genres)

                # insert_genre_info(connection, game)
                insert_platform_info(connection, game)

            connection.commit()
        else:
            print(f"Error: {response.status_code}")

        time.sleep(0.5)


def insert_game_to_db(connection, game_obj):
    cursor = connection.cursor()

    # Set rawg_id to null for now (instead of making a new request for every IGDB game)
    insert_query = "INSERT IGNORE INTO game (name, summary, url, igdb_id, rawg_id, release_date) VALUES (%s, %s, %s, %s, %s, %s);"
    cursor.execute(insert_query, (game_obj.name, game_obj.summary, game_obj.url, game_obj.igdb_id, game_obj.rawg_id, game_obj.release_date))

    print(f"Inserting: {game_obj.name}")

    return cursor.lastrowid


def insert_genre_info(connection, internal_game_id, genres):
    cursor = connection.cursor()

    for genre in genres:
        try:
            insert_query = "INSERT IGNORE INTO genre (igdb_genre_id, rawg_genre_id, name) VALUES (%s, %s, %s);"
            cursor.execute(insert_query, (genre.igdb_genre_id, genre.rawg_genre_id, genre.name))
            internal_genre_id = cursor.lastrowid
        except mysql.connector.Error as err:
            if err.errno == 1062:
                # Entry already exists, select its internal genre_id
                select_query = """
                SELECT genre_id FROM genre 
                WHERE (igdb_genre_id = %s AND %s IS NOT NULL) 
                OR (rawg_genre_id = %s AND %s IS NOT NULL);
                """
                cursor.execute(select_query, (genre.igdb_genre_id, genre.igdb_genre_id, genre.rawg_genre_id, genre.rawg_genre_id))
                internal_genre_id = cursor.fetchone()[0]
            else:
                raise

        insert_query = "INSERT INTO game_genre (game_id, genre_id) VALUES (%s, %s);"
        cursor.execute(insert_query, (internal_game_id, internal_genre_id))

    connection.commit()


def insert_platform_info(connection, game):
    cursor = connection.cursor()

    internal_game_id = game['internal_game_id']

    igdb_platforms = game['platforms']

    for igdb_platform in igdb_platforms:
        internal_platform_id = -1
        igdb_platform_id = igdb_platform['id']
        platform_name = igdb_platform['name']
        platform_family = igdb_platform.get('platform_family', None)

        try:
            insert_query = "INSERT IGNORE INTO platform (igdb_platform_id, name) VALUES (%s, %s);"
            cursor.execute(insert_query, (igdb_platform_id, platform_name))
            internal_platform_id = cursor.lastrowid
        except mysql.connector.Error as err:
            if err.errno == 1062:
                select_query = "SELECT platform_id FROM platform WHERE igdb_platform_id = %s;"
                cursor.execute(select_query, (igdb_platform_id,))
                internal_platform_id = cursor.fetchone()[0]
            else:
                raise

        if platform_family:
            igdb_platform_family_id = igdb_platform['platform_family']['id']
            platform_family_name = igdb_platform['platform_family']['name']

            try:
                insert_query = "INSERT IGNORE INTO platform_family (igdb_platform_family_id, name) VALUES (%s, %s);"
                cursor.execute(insert_query, (igdb_platform_family_id, platform_family_name))
                internal_platform_family_id = cursor.lastrowid

                insert_query = "INSERT INTO platform_platform_family (platform_family_id, platform_id) VALUES (%s, %s);"
                cursor.execute(insert_query, (internal_platform_family_id, internal_platform_id))
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    pass
                else:
                    raise

        insert_query = "INSERT INTO game_platform (game_id, platform_id) VALUES (%s, %s);"
        cursor.execute(insert_query, (internal_game_id, internal_platform_id))

    connection.commit()


def find_rawg_game_id(game_name, release_date):
    rawg_search_url = f"https://api.rawg.io/api/games?key={settings.get('API_KEYS', 'rawg_api_key')}&search={game_name}&dates={release_date},{release_date}"
    response = requests.get(rawg_search_url)

    if response.status_code == 200:
        rawg_games = response.json().get('results', [])

        if rawg_games:
            rawg_game = rawg_games[0]
            rawg_id = rawg_game['id']

            return rawg_id
        else:
            return -1
    else:
        return -1


def create_connection(db_config):
    return mysql.connector.connect(**db_config)


def close_connection(connection):
    cursor = connection.cursor()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
