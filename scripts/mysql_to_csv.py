import csv
import os
from db_connection import create_connection
from db_connection import close_connection
from db_connection import neo4j_import_folder


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
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    cursor.close()
    return columns, data

def convert_mysql_to_csv():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    connection = create_connection()

    cursor = connection.cursor()
    cursor.execute("USE soen_project_phase_1;")

    import_folder = neo4j_import_folder()
    if neo4j_import_folder:
        output_directory = import_folder

    for table_name in tables:
        os.makedirs(output_directory, exist_ok=True)

        columns, data = execute_query(connection, f"SELECT * FROM {table_name}")
        output_path = os.path.join(output_directory, f'{table_name}.csv')

        with open(output_path, mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(columns)  # Write the headers
            csv_writer.writerows(data)  # Write the data

    print(f"CSV files have been created successfully in '{output_directory}'.")

    close_connection(connection)

if __name__ == "__main__":
    main()
