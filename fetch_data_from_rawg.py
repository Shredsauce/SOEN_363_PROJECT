import requests
import json


def fetch_data_from_rawg(api_key):
    base_url = "https://api.rawg.io/api"

    # Fetching platforms
    platforms_url = f"{base_url}/platforms?key={api_key}"
    platforms_response = requests.get(platforms_url)
    platforms_data = platforms_response.json()
    with open('platforms_data_rawg.json', 'w') as f:
        json.dump(platforms_data, f, indent=4)
    print("Platforms data saved to platforms_data.json")

    # Fetching games within a specified date range for certain platforms
    games_url = f"{base_url}/games?key={api_key}&dates=2019-09-01,2019-09-30&platforms=18,1,7"
    games_response = requests.get(games_url)
    games_data = games_response.json()
    with open('games_data.json', 'w') as f:
        json.dump(games_data, f, indent=4)
    print("Games data saved to games_data.json")


if __name__ == "__main__":
    api_key = "0a24c1f906b14571b145d09e787f6ecc"  # Replace YOUR_API_KEY with your actual RAWG API key
    fetch_data_from_rawg(api_key)
