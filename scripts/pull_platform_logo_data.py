import configparser
import os
import json
import time
from igdb.wrapper import IGDBWrapper

# Change the working directory to the parent directory of the script file
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
settings = configparser.ConfigParser()
settings.read('settings.ini')

if __name__ == '__main__':
    wrapper = IGDBWrapper(settings.get('API_KEYS', 'igdb_client_id'), settings.get('API_KEYS', 'igdb_bearer'))

    all_platform_data = []  # Initialize an empty list to store all platform data along with their logo references

    # Initially, we don't know the total number of platforms. Set a high enough offset to ensure we get all data.
    offset = 0
    limit = 500
    total_fetched = 0

    while True:
        print(f"Fetching platform data with offset {offset}...")
        # JSON API request for platforms including their logo references
        byte_array = wrapper.api_request(
            'platforms',
            f'fields id,name,platform_logo; offset {offset}; limit {limit};'
        )
        # Parse the byte array into JSON
        json_data = json.loads(byte_array.decode('utf-8'))

        if not json_data:
            break  # If no more data is returned, exit the loop

        all_platform_data.extend(json_data)  # Extend the list with the fetched data

        total_fetched += len(json_data)
        offset += limit  # Increase offset for the next batch
        time.sleep(0.5)  # Pause to avoid hitting the rate limit

    # After collecting all data, write it to a single file
    with open('generated_json/all_platforms_with_logos_igdb.json', 'w') as file:
        json.dump(all_platform_data, file, indent=4)

    print(f"Data for all platforms with their logo references written to all_platforms_with_logos_igdb.json. Total platforms fetched: {total_fetched}")
