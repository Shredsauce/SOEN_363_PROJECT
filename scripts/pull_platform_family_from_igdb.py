import configparser
import os
from igdb.wrapper import IGDBWrapper
# Change the working directory to the parent directory of the script file
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
settings = configparser.ConfigParser()
settings.read('settings.ini')

if __name__ == '__main__':

    import json
    import time

    wrapper = IGDBWrapper(settings.get('API_KEYS', 'igdb_client_id'), settings.get('API_KEYS', 'igdb_bearer'))

    all_platform_families_data = []  # Initialize an empty list to store all platform family data

    # Initially, we don't know the total number of platform families. Set a high enough offset to ensure we get all data.
    offset = 0
    limit = 500
    total_fetched = 0

    while True:
        print(f"Fetching platform family data with offset {offset}...")
        # JSON API request for platform families
        byte_array = wrapper.api_request(
            'platform_families',
            f'fields id,name; offset {offset}; limit {limit};'
        )
        # Parse the byte array into JSON
        json_data = json.loads(byte_array.decode('utf-8'))

        if not json_data:
            break  # If no more data is returned, exit the loop

        all_platform_families_data.extend(json_data)  # Use extend to add the elements of json_data to all_platform_families_data

        total_fetched += len(json_data)
        offset += limit  # Increase offset for the next batch
        time.sleep(0.5)  # Pause to avoid hitting the rate limit

    # After collecting all data, write it to a single file
    with open('generated_json/all_platform_families_igdb.json', 'w') as file:
        json.dump(all_platform_families_data, file, indent=4)

    print(f"Data for all platform families written to all_platform_families_igdb.json. Total platform families fetched: {total_fetched}")
