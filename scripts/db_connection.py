import os
import mysql.connector
import configparser
from neo4j import GraphDatabase

config_path = 'config.ini'


class DBConfig:
    _config = None

    @classmethod
    def get_config(cls):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(base_dir)

        if cls._config is None:
            config = configparser.ConfigParser()
            config.read(config_path)
            cls._config = {
                'user': config.get('database', 'user'),
                'password': config.get('database', 'password'),
                'host': config.get('database', 'host'),
                'raise_on_warnings': config.getboolean('database', 'raise_on_warnings'),
                'neo4j_import_folder': config.get('neo4j', 'neo4j_import_folder'),
                'neo4j_uri': config.get('neo4j', 'uri'),
                'neo4j_username': config.get('neo4j', 'username'),
                'neo4j_password': config.get('neo4j', 'password')
            }
        return cls._config


def create_connection():
    db_config = DBConfig.get_config()
    mysql_config = {
        'user': db_config['user'],
        'password': db_config['password'],
        'host': db_config['host'],
        'raise_on_warnings': db_config['raise_on_warnings']
    }
    return mysql.connector.connect(**mysql_config)


def close_connection(connection):
    cursor = connection.cursor()
    cursor.close()
    connection.close()


def neo4j_import_folder():
    return DBConfig.get_config()['neo4j_import_folder'].strip()


def get_neo4j_driver():
    uri = DBConfig.get_config()['neo4j_uri']
    username = DBConfig.get_config()['neo4j_username']
    password = DBConfig.get_config()['neo4j_password']

    driver = GraphDatabase.driver(uri, auth=(username, password))
    return driver


