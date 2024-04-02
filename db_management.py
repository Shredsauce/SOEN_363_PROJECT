import mysql.connector
from mysql.connector import Error
import configparser
import requests
from datetime import datetime

config_path = 'config.ini'
create_tables_file = 'create_tables.sql'
db_name = 'soen_project_phase_1'

limit_num_games = 20

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
        connection = create_connection(db_config)
        drop_existing_db(connection)
        close_connection(connection)

        connection = create_connection(db_config)
        create_database(connection)
        create_tables(connection)
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


def create_database(connection):
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE {db_name};")


def create_tables(connection):
    cursor = connection.cursor()

    cursor.execute(f"USE {db_name};")

    with open(create_tables_file, 'r') as file:
        sql_query = file.read()

    for result in cursor.execute(sql_query, multi=True):
        if result.with_rows:
            print(result.fetchall())


def populate_database(connection):
    cursor = connection.cursor()
    cursor.execute(f"USE {db_name};")

    insert_games(connection, cursor)


def insert_games(connection, cursor):
    url = "https://api.igdb.com/v4/games/"

    headers = {
        'Client-ID': settings.get('API_KEYS', 'igdb_client_id'),
        'Authorization': "Bearer " + settings.get('API_KEYS', 'igdb_bearer'),
    }

    response = requests.post(url, headers=headers, data='fields name, release_dates.date, platforms, platforms.name, platforms.platform_family,  platforms.platform_family.name; limit '+str(limit_num_games)+';')
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

            rawg_id = find_rawg_game_id(game_name, release_date)

            if rawg_id < 0: continue

            insert_query = "INSERT INTO game (name, igdb_id, rawg_id, release_date) VALUES (%s, %s, %s, %s);"
            cursor.execute(insert_query, (game_name, igdb_id, rawg_id, release_date))

            # Keep track of our internal id to use when referencing in the platform_game relationship
            game['internal_game_id'] = cursor.lastrowid
            insert_platform_info(connection, game)

            print(f"Inserting: {game_name}")

        connection.commit()
    else:
        print(f"Error: {response.status_code}")


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
