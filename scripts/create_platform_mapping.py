import json
import os

# Change directory to the parent directory of the script file
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_data(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_platform_mapping(rawg_data, igdb_data):
    # Create a mapping of platform names to their IDs in both RAWG and IGDB, including unmatched platforms.
    platform_mapping = {}
    rawg_matched = set()
    igdb_matched = set()

    # Process RAWG data for matching platforms in IGDB
    for rawg_platform in rawg_data['results']:
        rawg_platform_name = rawg_platform['name'].lower()

        match_found = False
        for igdb_platform in igdb_data:
            igdb_platform_name = igdb_platform['name'].lower()

            if rawg_platform_name == igdb_platform_name:
                platform_mapping[rawg_platform['name']] = {
                    "RAWG_ID": rawg_platform['id'],
                    "IGDB_ID": igdb_platform['id']
                }
                rawg_matched.add(rawg_platform_name)
                igdb_matched.add(igdb_platform_name)
                match_found = True
                break

        if not match_found:
            platform_mapping[rawg_platform['name']] = {
                "RAWG_ID": rawg_platform['id'],
                "IGDB_ID": None
            }

    # Include IGDB platforms not matched with RAWG
    for igdb_platform in igdb_data:
        igdb_platform_name = igdb_platform['name'].lower()
        if igdb_platform_name not in igdb_matched:
            if igdb_platform['name'] not in platform_mapping:
                platform_mapping[igdb_platform['name']] = {
                    "RAWG_ID": None,
                    "IGDB_ID": igdb_platform['id']
                }
            else:
                # Update existing entry with IGDB ID if it was previously added without a match
                platform_mapping[igdb_platform['name']]['IGDB_ID'] = igdb_platform['id']

    return platform_mapping

if __name__ == "__main__":

    rawg_platforms = load_json_data('generated_json/platforms_data_rawg.json')
    igdb_platforms = load_json_data('generated_json/platforms_data_igdb.json')

    # Create the platform mapping
    mapping = create_platform_mapping(rawg_platforms, igdb_platforms)

    # Save the mapping to a JSON file
    with open('generated_json/platform_mapping.json', 'w', encoding='utf-8') as file:
        json.dump(mapping, file, indent=4)

    print("Platform mapping saved to platform_mapping.json")
