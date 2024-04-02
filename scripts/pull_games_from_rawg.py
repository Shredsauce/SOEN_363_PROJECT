import requests
import time
import json
import configparser


def fetch_games(api_key, max_pages=10):
    base_url = "https://api.rawg.io/api/games"
    headers = {"User-Agent": "Python RAWG API Client"}
    params = {
        "key": api_key,
        "page_size": 40,  # Adjust based on the maximum allowed by the API or your preference
    }

    games = []

    for page in range(1, max_pages + 1):
        print(f"Fetching page {page}...")
        params["page"] = page
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}: HTTP {response.status_code}")
            break

        data = response.json()
        games.extend(data.get("results", []))

        # Check if there's a next page. If not, exit the loop.
        if "next" not in data or not data["next"]:
            break

        # Be respectful to the API's rate limit
        time.sleep(1)  # Adjust this delay as needed or based on the API's guidelines

    return games


def save_games_to_json(games, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(games, file, ensure_ascii=False, indent=4)
        print(f"Games data saved to {file_path}")


if __name__ == '__main__':
    settings = configparser.ConfigParser()
    settings.read('../settings.ini')

    api_key = settings.get('API_KEYS', 'rawg_api_key')
    games = fetch_games(api_key, max_pages=300)  # Set max_pages to the number you want, but be mindful of rate limits

    # Specify the path to the JSON file where you want to save the games data
    json_file_path = "generated_json/games_data_rawg.json"
    save_games_to_json(games, json_file_path)




