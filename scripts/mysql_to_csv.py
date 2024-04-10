import pandas as pd
import os
from db_connection import create_connection
from db_connection import close_connection

output_directory = 'exported_csv'
os.makedirs(output_directory, exist_ok=True)

tables = [
    'game',
    'game_genre',
    'game_platform',
    'genre',
    'platform',
    'platform_family',
    'platform_logo'
]


def main():
    convert_mysql_to_csv()


def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)
    cursor.close()
    return df


def convert_mysql_to_csv():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    connection = create_connection()

    cursor = connection.cursor()
    cursor.execute("USE soen_project_phase_1;")

    for table_name in tables:
        os.makedirs(output_directory, exist_ok=True)

        dataframe = execute_query(connection, f"SELECT * FROM {table_name}")

        output_path = os.path.join(output_directory, f'{table_name}.csv')

        dataframe.to_csv(output_path, index=False)

    print(f"CSV files have been created successfully in '{output_directory}'.")

    close_connection(connection)


if __name__ == "__main__":
    main()