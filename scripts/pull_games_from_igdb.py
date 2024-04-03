import configparser
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
settings = configparser.ConfigParser()
settings.read('settings.ini')

if __name__ == '__main__':
    from igdb.wrapper import IGDBWrapper
    import json
    import time

    wrapper = IGDBWrapper(settings.get('API_KEYS', 'igdb_client_id'), settings.get('API_KEYS', 'igdb_bearer'))

    all_games_data = []  # Initialize an empty list to store all games data

    # Loop through all platform numbers from 3 to 200
    for platform_number in range(3, 480):
        print(f"Fetching data for platform {platform_number}...")
        # JSON API request for the current platform
        byte_array = wrapper.api_request(
            'games',
            f'fields *; offset 0; where platforms={platform_number}; limit 500;'
        )
        # Parse the byte array into JSON and append to the list
        json_data = json.loads(byte_array.decode('utf-8'))
        all_games_data.extend(json_data)  # Use extend to add the elements of json_data to all_games_data

        byte_array = wrapper.api_request(
            'games',
            f'fields *; offset 500; where platforms={platform_number}; limit 500;'
        )
        # Parse the byte array into JSON and append to the list
        json_data = json.loads(byte_array.decode('utf-8'))
        all_games_data.extend(json_data)  # Use extend to add the elements of json_data to all_games_data

        time.sleep(0.5)  # Pause for 1 second before making the next request

    # After collecting all data, write it to a single file
    with open('generated_json/all_platforms_games.json', 'w') as file:
        json.dump(all_games_data, file, indent=4)

    print("Data for all platforms written to all_platforms_games.json")
