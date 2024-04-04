import mysql.connector
from mysql.connector import Error
import configparser
import requests
from datetime import datetime
import time
from distutils.util import strtobool
import os
import json
from Game import Game
from Genre import Genre
from Platform import Platform
from PlatformFamily import PlatformFamily


os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config_path = 'config.ini'
create_tables_file = 'sql/create_tables.sql'
check_games_associated_trigger_file = 'sql/check_games_associated_trigger.sql'
db_name = 'soen_project_phase_1'

settings = configparser.ConfigParser()
settings.read('settings.ini')

platform_mapping_file = 'generated_json/platform_mapping.json'
with open(platform_mapping_file, 'r') as file:
    platform_mapping = json.load(file)

platform_family_mapping_file = 'generated_json/platform_family_mapping.json'
with open(platform_family_mapping_file, 'r') as file:
    platform_family_mapping = json.load(file)

all_platforms_with_logos_igdb_file = 'generated_json/all_platforms_with_logos_igdb.json'
with open(all_platforms_with_logos_igdb_file, 'r') as file:
    all_platforms_with_logos_igdb = json.load(file)

all_platform_logos_igdb_file = 'generated_json/all_platform_logos_igdb.json'
with open(all_platform_logos_igdb_file, 'r') as file:
    all_platform_logos_igdb = json.load(file)


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

    execute_sql_file(check_games_associated_trigger_file, connection)


def execute_sql_file(filename, connection):
    # Open and read the SQL file
    with open(filename, 'r') as file:
        sql_file_content = file.read()

    sql_statements = [stmt for stmt in sql_file_content.split('$$') if not stmt.strip().lower().startswith('delimiter')]

    cursor = connection.cursor()
    for statement in sql_statements:
        if statement.strip() == '':
            continue

        try:
            cursor.execute(statement.strip())
            connection.commit()
        except mysql.connector.Error as err:
            print(f"An error occurred: {err}")
            connection.rollback()

    cursor.close()


def use_table(connection):
    cursor = connection.cursor()
    cursor.execute(f"USE {db_name};")


def populate_database(connection):
    use_table(connection)
    insert_igdb_games(connection)
    insert_rawg_games(connection)
    insert_fake_games(connection)


def insert_igdb_games(connection):
    num_pages_to_process = int(settings.get('IGDB_SETTINGS', 'num_pages_to_process'))
    limit_num_games = int(settings.get('IGDB_SETTINGS', 'limit_num_games'))
    start_page = int(settings.get('IGDB_SETTINGS', 'start_page'))

    for i in range(start_page-1, num_pages_to_process):
        page = i+1
        print(f'Fetching IGDB page {page}')

        url = "https://api.igdb.com/v4/games/"

        headers = {
            'Client-ID': settings.get('API_KEYS', 'igdb_client_id'),
            'Authorization': "Bearer " + settings.get('API_KEYS', 'igdb_bearer'),
        }

        page_offset = i*limit_num_games

        request_data = f'fields name, summary, url, genres.name, release_dates.date, platforms, platforms.name, platforms.platform_family, platforms.platform_family.name; limit {str(limit_num_games)}; offset {str(page_offset)};'

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

                # Keep track of our internal id to use when referencing in the game_genre and game_platform relationships
                internal_game_id = insert_game_to_db(connection, game_obj)

                igdb_genres = game.get('genres')
                genres = [Genre(igdb_genre['id'], None, igdb_genre['name']) for igdb_genre in igdb_genres] if igdb_genres else []
                insert_genre_info(connection, internal_game_id, genres)

                igdb_platforms = game.get('platforms')

                platforms = []
                if igdb_platforms:
                    for igdb_platform in igdb_platforms:
                        platform_family = None

                        if 'platform_family' in igdb_platform and igdb_platform['platform_family']:
                            pf = igdb_platform['platform_family']
                            igdb_platform_family_id = pf.get('id', None)

                            rawg_platform_family_id = None
                            platform_family_name = pf.get('name', None)

                            platform_family = PlatformFamily(igdb_platform_family_id, rawg_platform_family_id, platform_family_name)

                        platform = Platform(igdb_platform['id'], None, igdb_platform['name'], platform_family)
                        platforms.append(platform)

                insert_platform_info(connection, internal_game_id, platforms)

            connection.commit()
        else:
            print(f"Error: {response.status_code}")

        time.sleep(0.5)


def insert_rawg_games(connection):
    platform_parents_data_file = 'generated_json/platform_parents_data_rawg.json'

    with open(platform_parents_data_file, 'r') as file:
        platform_parents_data = json.load(file)

    cursor = connection.cursor()

    num_pages_to_process = int(settings.get('RAWG_SETTINGS', 'num_pages_to_process'))
    limit_num_games = int(settings.get('RAWG_SETTINGS', 'limit_num_games'))
    start_page = int(settings.get('RAWG_SETTINGS', 'start_page'))
    rawg_api_key = settings.get('API_KEYS', 'rawg_api_key')

    base_url = "https://api.rawg.io/api/games"
    params = {
        "key": rawg_api_key,
        "page_size": limit_num_games,
    }

    for page in range(start_page, num_pages_to_process+1):
        print(f"Fetching RAWG page {page}")
        params["page"] = page
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}: HTTP {response.status_code}")
            break

        data = response.json()
        games = data.get("results", [])

        for game in games:
            game_name = str(game.get('name', 'N/A'))
            rawg_id = game['id']
            summary = game.get('description', '')
            url = game.get('website', '')
            release_date = str(game.get('released'))

            game_obj = Game(game_name, summary, url, release_date, None, rawg_id)

            search_term = f"{game_name}"
            select_query = "SELECT game_id, name FROM game g WHERE UPPER(g.name) LIKE UPPER(%s) AND YEAR(g.release_date) = YEAR(%s);"

            cursor.execute(select_query, (search_term, release_date))

            found_match = False
            matched_games = cursor.fetchall()
            if matched_games:
                for matched_game in matched_games:
                    game_id = matched_game[0]

                    print(f"Found IGDB game match: {str(matched_game)}. Set rawg_id to {str(rawg_id)} at game_id {str(game_id)}")

                    update_query = """
                    UPDATE game g
                    SET rawg_id = %s
                    WHERE g.game_id = %s;
                    """

                    cursor.execute(update_query, (rawg_id, game_id))
                    connection.commit()

                    found_match = True
                    break

            # Already found match, don't try to insert again
            if found_match:
                continue

            internal_game_id = insert_game_to_db(connection, game_obj)

            rawg_genres = game.get('genres')
            genres = [Genre(None, rawg_genre['id'], rawg_genre['name']) for rawg_genre in rawg_genres] if rawg_genres else []
            insert_genre_info(connection, internal_game_id, genres)

            rawg_platforms = game.get('platforms')
            rawg_platform_families = game.get('parent_platforms')

            platforms = []
            if rawg_platforms:
                for rawg_platform in rawg_platforms:
                    rawg_platform_id = rawg_platform['platform']['id']
                    platform_name = rawg_platform['platform']['name']

                    rawg_platform_family = find_rawg_platform_family(platform_parents_data, platform_name)

                    platform = Platform(None, rawg_platform_id, platform_name, rawg_platform_family)
                    platforms.append(platform)

            insert_platform_info(connection, internal_game_id, platforms)

        # Check if there's a 'next' page
        if "next" not in data or not data["next"]:
            break

        time.sleep(0.5)


def find_rawg_platform_family(platform_data, platform_name):
    for item in platform_data:
        if 'platforms' in item and isinstance(item['platforms'], list):
            for platform in item['platforms']:
                if platform.get('name') == platform_name:
                    platform_family = PlatformFamily(None, item.get('id'), item.get('name'))
                    return platform_family
    return None

def insert_fake_games(connection):
    game_name = 'The One True Multi-platform game'
    summary = 'Just the craziest game available on every platform EVER.'
    url = 'https://shredsauce.com'
    release_date = datetime(2012, 8, 7)
    rawg_id = 999998
    igdb_id = 999999

    game_obj = Game(game_name, summary, url, release_date, igdb_id, rawg_id)

    internal_game_id = insert_game_to_db(connection, game_obj)

    igdb_genres = [
        {'id': 14, 'name': 'Sport'}
    ]

    genres = [Genre(igdb_genre['id'], None, igdb_genre['name']) for igdb_genre in igdb_genres] if igdb_genres else []
    insert_genre_info(connection, internal_game_id, genres)

    cursor = connection.cursor()

    # Grab every platform
    select_query = "SELECT platform_id FROM platform;"
    cursor.execute(select_query)
    platform_ids = cursor.fetchall()

    insert_query = "INSERT INTO game_platform (game_id, platform_id) VALUES (%s, %s);"

    for (platform_id,) in platform_ids:
        cursor.execute(insert_query, (internal_game_id, platform_id))

    connection.commit()


def insert_game_to_db(connection, game_obj):
    cursor = connection.cursor()

    # Set rawg_id to null for now (instead of making a new request for every IGDB game)
    insert_query = "INSERT IGNORE INTO game (name, summary, url, igdb_id, rawg_id, release_date) VALUES (%s, %s, %s, %s, %s, %s);"
    cursor.execute(insert_query, (game_obj.name, game_obj.summary, game_obj.url, game_obj.igdb_id, game_obj.rawg_id, game_obj.release_date))

    return cursor.lastrowid


def insert_genre_info(connection, internal_game_id, genres):
    cursor = connection.cursor()

    genre_mapping_file = 'generated_json/genre_mapping.json'

    with open(genre_mapping_file) as file:
        genre_mapping = json.load(file)

    for genre in genres:
        genre_mapping_for_genre = genre_mapping.get(genre.name)

        if genre_mapping_for_genre:
            genre.igdb_genre_id = genre.igdb_genre_id or genre_mapping_for_genre.get('IGDB_ID')
            genre.rawg_genre_id = genre.rawg_genre_id or genre_mapping_for_genre.get('RAWG_ID')

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


def insert_platform_info(connection, internal_game_id, platforms):
    cursor = connection.cursor()

    for platform in platforms:
        igdb_platform_id = platform.igdb_platform_id
        rawg_platform_id = platform.rawg_platform_id
        platform_name = platform.name
        platform_family = platform.platform_family

        platform_family_internal_id = insert_platform_family_info(connection, platform_family)

        platform_mapping_pair = platform_mapping.get(platform_name)

        if platform_mapping_pair:
            igdb_platform_id = igdb_platform_id or platform_mapping_pair.get('IGDB_ID')
            rawg_platform_id = rawg_platform_id or platform_mapping_pair.get('RAWG_ID')

        try:
            insert_query = "INSERT IGNORE INTO platform (platform_family_id, igdb_platform_id, rawg_platform_id, name) VALUES (%s, %s, %s, %s);"
            cursor.execute(insert_query, (platform_family_internal_id, igdb_platform_id, rawg_platform_id, platform_name))
            platform.internal_platform_id = cursor.lastrowid
        except mysql.connector.Error as err:
            if err.errno == 1062:
                select_query = "SELECT platform_id FROM platform WHERE igdb_platform_id = %s OR rawg_platform_id = %s;"
                cursor.execute(select_query, (igdb_platform_id, rawg_platform_id))
                platform.internal_platform_id = cursor.fetchone()[0]

                update_query = """
                UPDATE platform
                SET igdb_platform_id = %s, rawg_platform_id = %s
                WHERE platform_id = %s;
                """
                cursor.execute(update_query, (igdb_platform_id, rawg_platform_id, platform.internal_platform_id))
            else:
                raise

        insert_query = "INSERT INTO game_platform (game_id, platform_id) VALUES (%s, %s);"
        cursor.execute(insert_query, (internal_game_id, platform.internal_platform_id))

    insert_platform_logo(connection, platform)

    connection.commit()


def insert_platform_logo(connection, platform):
    cursor = connection.cursor()

    platform_name = platform.name
    platform_logo = next((item for item in all_platforms_with_logos_igdb if item['name'] == platform_name), None)

    if platform_logo:
        platform_logo_id = platform_logo.get('platform_logo')
        logo_entry = next((item for item in all_platform_logos_igdb if item['id'] == platform_logo_id), None)

        if logo_entry:
            image_url = logo_entry['url']
            height = logo_entry['height']
            width = logo_entry['width']
            platform_id = platform.internal_platform_id
            platform_logo_id = logo_entry['id']  # Use IGDB's platform logo id

            try:
                insert_query = "INSERT INTO platform_logo (platform_logo_id, image_url, height, width, platform_id) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(insert_query, (platform_logo_id, image_url, height, width, platform_id))
            except mysql.connector.Error as err:
                if err.errno == 1062:  # Platform logo already inserted
                    pass
                else:
                    raise


def insert_platform_family_info(connection, platform_family):
    cursor = connection.cursor()

    internal_platform_family_id = None

    if platform_family:
        igdb_platform_family_id = platform_family.igdb_platform_family_id
        rawg_platform_family_id = platform_family.rawg_platform_family_id

        platform_family_name = platform_family.name

        platform_family_mapping_pair = platform_family_mapping.get(platform_family_name)

        if platform_family_mapping_pair:
            igdb_platform_family_id = platform_family_mapping_pair.get('IGDB_ID', igdb_platform_family_id)
            rawg_platform_family_id = platform_family_mapping_pair.get('RAWG_ID', rawg_platform_family_id)

        try:
            insert_query = "INSERT IGNORE INTO platform_family (igdb_platform_family_id, rawg_platform_family_id, name) VALUES (%s, %s, %s);"
            cursor.execute(insert_query, (igdb_platform_family_id, rawg_platform_family_id, platform_family_name))
            internal_platform_family_id = cursor.lastrowid
        except mysql.connector.Error as err:
            if err.errno == 1062:
                select_query = "SELECT platform_family_id FROM platform_family WHERE igdb_platform_family_id = %s OR rawg_platform_family_id = %s;"
                cursor.execute(select_query, (igdb_platform_family_id, rawg_platform_family_id))
                internal_platform_family_id = cursor.fetchone()[0]

                update_query = """
                UPDATE platform_family
                SET igdb_platform_family_id = %s, rawg_platform_family_id = %s
                WHERE platform_family_id = %s;
                """
                cursor.execute(update_query, (igdb_platform_family_id, rawg_platform_family_id, internal_platform_family_id))
            else:
                raise

    return internal_platform_family_id


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
