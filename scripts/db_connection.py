import mysql.connector
import configparser

config_path = 'config.ini'


def create_connection():
    config = configparser.ConfigParser()
    config.read(config_path)

    db_config = {
        'user': config.get('database', 'user'),
        'password': config.get('database', 'password'),
        'host': config.get('database', 'host'),
        'raise_on_warnings': config.getboolean('database', 'raise_on_warnings')
    }

    return mysql.connector.connect(**db_config)


def close_connection(connection):
    cursor = connection.cursor()
    cursor.close()
    connection.close()
