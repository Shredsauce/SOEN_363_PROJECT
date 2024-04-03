import requests
import time
import json
import configparser
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fetch_platform_parents(api_key):
    base_url = "https://api.rawg.io/api/platforms/lists/parents"
    headers = {"User-Agent": "Python RAWG API Client"}
    params = {
        "key": api_key,
    }

    platform_parents = []

    response = requests.get(base_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        platform_parents.extend(data.get("results", []))
    else:
        print(f"Failed to fetch platform parents data: HTTP {response.status_code}")

    return platform_parents

def save_platform_parents_to_json(platform_parents, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(platform_parents, file, ensure_ascii=False, indent=4)
        print(f"Platform parents data saved to {file_path}")

if __name__ == '__main__':
    settings = configparser.ConfigParser()
    settings.read('settings.ini')

    api_key = settings.get('API_KEYS', 'rawg_api_key')
    platform_parents = fetch_platform_parents(api_key)  # Fetch platform parents data

    # Specify the path to the JSON file where you want to save the platform parents data
    json_file_path = "generated_json/platform_parents_data_rawg.json"
    save_platform_parents_to_json(platform_parents, json_file_path)
