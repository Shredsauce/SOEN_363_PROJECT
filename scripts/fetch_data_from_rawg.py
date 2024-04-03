import requests
import json
import configparser
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
settings = configparser.ConfigParser()
settings.read('settings.ini')


def fetch_data_from_rawg(api_key):
    base_url = "https://api.rawg.io/api"

    # Fetching platforms
    platforms_url = f"{base_url}/platforms?key={api_key}"
    platforms_response = requests.get(platforms_url)
    platforms_data = platforms_response.json()
    with open('generated_json/platforms_data_rawg.json', 'w') as f:
        json.dump(platforms_data, f, indent=4)
    print("Platforms data saved to platforms_data.json")

    # Fetching games within a specified date range for certain platforms
    games_url = f"{base_url}/games?key={api_key}&dates=2019-09-01,2019-09-30&platforms=18,1,7"
    games_response = requests.get(games_url)
    games_data = games_response.json()
    with open('generated_json/games_data.json', 'w') as f:
        json.dump(games_data, f, indent=4)
    print("Games data saved to games_data.json")


if __name__ == "__main__":
    api_key = settings.get('API_KEYS', 'rawg_api_key')
    fetch_data_from_rawg(api_key)
