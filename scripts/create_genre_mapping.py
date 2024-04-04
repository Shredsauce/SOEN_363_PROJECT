import json
import os

# Set the working directory to the parent directory of the script file
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_data(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_genre_mapping(rawg_data, igdb_data):
    # Create a mapping of genre names to their IDs in both RAWG and IGDB, including unmatched genres.
    genre_mapping = {}
    rawg_matched = set()
    igdb_matched = set()

    # Process RAWG and IGDB data to find matches
    for rawg_genre in rawg_data:
        rawg_genre_name = rawg_genre['name'].lower()
        for igdb_genre in igdb_data:
            igdb_genre_name = igdb_genre['name'].lower()

            if rawg_genre_name == igdb_genre_name:
                genre_mapping[rawg_genre['name']] = {
                    "RAWG_ID": rawg_genre['id'],
                    "IGDB_ID": igdb_genre['id']
                }
                rawg_matched.add(rawg_genre_name)
                igdb_matched.add(igdb_genre_name)
                break

    # Include RAWG genres without a match
    for rawg_genre in rawg_data:
        if rawg_genre['name'].lower() not in rawg_matched:
            genre_mapping[rawg_genre['name']] = {
                "RAWG_ID": rawg_genre['id'],
                "IGDB_ID": None
            }

    # Include IGDB genres without a match
    for igdb_genre in igdb_data:
        if igdb_genre['name'].lower() not in igdb_matched:
            if igdb_genre['name'] not in genre_mapping:
                genre_mapping[igdb_genre['name']] = {
                    "RAWG_ID": None,
                    "IGDB_ID": igdb_genre['id']
                }
            else:
                # Update existing entry with IGDB ID if it was previously added without a match
                genre_mapping[igdb_genre['name']]['IGDB_ID'] = igdb_genre['id']

    return genre_mapping

if __name__ == "__main__":

    rawg_genres = load_json_data('generated_json/genres_data_rawg.json')
    igdb_genres = load_json_data('generated_json/genres_data_igdb.json')

    # Create the genre mapping
    mapping = create_genre_mapping(rawg_genres, igdb_genres)

    # Save the mapping to a JSON file
    with open('generated_json/genre_mapping.json', 'w', encoding='utf-8') as file:
        json.dump(mapping, file, indent=4)

    print("Genre mapping saved to genre_mapping.json")
