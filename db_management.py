import mysql.connector
from mysql.connector import Error
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

db_config = {
    'user': config.get('database', 'user'),
    'password': config.get('database', 'password'),
    'host': config.get('database', 'host'),
    'raise_on_warnings': config.getboolean('database', 'raise_on_warnings')
}

db_name = 'soen_project_phase_1'

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
    cursor.execute(f"CREATE DATABASE {db_name};")
    cursor.close()
    connection.close()

    connection_config_dict = db_config.copy()
    connection_config_dict['database'] = db_name
    connection = mysql.connector.connect(**connection_config_dict)
    cursor = connection.cursor()

    ddl_sql_query = """
    USE soen_project_phase_1;

    CREATE TABLE game (
        game_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        igdb_key VARCHAR(255)
    );
    """

    for result in cursor.execute(ddl_sql_query, multi=True):
        if result.with_rows:
            print(result.fetchall())

    dml_sql_query = """
    INSERT INTO game (name, igdb_key) VALUES ('some name', 'some_ig_somekey');
    """

    for result in cursor.execute(dml_sql_query, multi=True):
        if result.with_rows:
            print(result.fetchall())

    connection.commit()

    print("Statements executed successfully.")

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
