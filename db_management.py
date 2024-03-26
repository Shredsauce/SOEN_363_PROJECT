import mysql.connector
from mysql.connector import Error

initial_config_dict = {
    'user': 'root',
    'password': 'Test123',
    'host': '127.0.0.1',
    'raise_on_warnings': True
}

db_name = 'soen_project_phase_1'

try:
    connection = mysql.connector.connect(**initial_config_dict)
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")
    cursor.execute(f"CREATE DATABASE {db_name};")
    cursor.close()
    connection.close()

    connection_config_dict = initial_config_dict.copy()
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
