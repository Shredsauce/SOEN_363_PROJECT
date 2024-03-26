import mysql.connector
from mysql.connector import Error
import configparser

config_path = 'config.ini'
db_name = 'soen_project_phase_1'


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

    sql_query = f"""
    USE {db_name};

    CREATE TABLE game (
        game_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        igdb_key VARCHAR(255)
    );
    """

    for result in cursor.execute(sql_query, multi=True):
        if result.with_rows:
            print(result.fetchall())


def populate_database(connection):
    cursor = connection.cursor()

    dml_sql_query = """
    INSERT INTO game (name, igdb_key) VALUES ('some name', 'some_ig_somekey');
    """

    for result in cursor.execute(dml_sql_query, multi=True):
        if result.with_rows:
            print(result.fetchall())

    connection.commit()


def create_connection(db_config):
    return mysql.connector.connect(**db_config)


def close_connection(connection):
    cursor = connection.cursor()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
