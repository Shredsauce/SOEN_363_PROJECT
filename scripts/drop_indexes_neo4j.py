from db_connection import get_neo4j_driver


def drop_indexes_on_property():
    driver = get_neo4j_driver()
    with driver.session() as session:

        result = session.run("SHOW INDEXES")

        indexes = [record["name"] for record in result]

        for index_name in indexes:
            drop_command = f"DROP INDEX `{index_name}`"
            session.run(drop_command)
            print(f"Dropped index: {index_name}")


if __name__ == "__main__":
    drop_indexes_on_property()