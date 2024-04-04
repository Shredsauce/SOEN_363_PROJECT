import requests
import time
import json
import configparser
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fetch_genres(api_key):
    base_url = "https://api.rawg.io/api/genres"
    headers = {"User-Agent": "Python RAWG API Client"}
    params = {
        "key": api_key,
        "page_size": 50,  # Adjust based on the maximum allowed by the API or your preference
    }

    genres = []

    page = 1
    while True:
        print(f"Fetching page {page}...")
        params["page"] = page
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}: HTTP {response.status_code}")
            break

        data = response.json()
        genres.extend(data.get("results", []))

        # Check if there's a next page. If not, exit the loop.
        if "next" not in data or not data["next"]:
            break

        page += 1
        # Be respectful to the API's rate limit
        time.sleep(1)

    return genres


def save_genres_to_json(genres, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(genres, file, ensure_ascii=False, indent=4)
        print(f"Genres data saved to {file_path}")


if __name__ == '__main__':
    settings = configparser.ConfigParser()
    settings.read('settings.ini')

    api_key = settings.get('API_KEYS', 'rawg_api_key')
    genres = fetch_genres(api_key)

    json_file_path = "generated_json/genres_data_rawg.json"
    save_genres_to_json(genres, json_file_path)
