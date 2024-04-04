import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_data(filename):

    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def create_platform_family_mapping(rawg_data, igdb_data):
    # Create a mapping of platform family names to their IDs in both RAWG and IGDB, including unmatched families.

    platform_family_mapping = {}
    rawg_matched = set()
    igdb_matched = set()

    # Process RAWG data for matching platform families in IGDB
    for rawg_platform_family in rawg_data:
        rawg_platform_family_name = rawg_platform_family['name'].lower()

        match_found = False
        for igdb_platform_family in igdb_data:
            igdb_platform_family_name = igdb_platform_family['name'].lower()

            if rawg_platform_family_name == igdb_platform_family_name:
                # Create a mapping entry with IDs from both databases
                platform_family_mapping[rawg_platform_family['name']] = {
                    "RAWG_ID": rawg_platform_family['id'],
                    "IGDB_ID": igdb_platform_family['id']
                }
                rawg_matched.add(rawg_platform_family_name)
                igdb_matched.add(igdb_platform_family_name)
                match_found = True
                break

        if not match_found:
            # Include RAWG platform family without a match
            platform_family_mapping[rawg_platform_family['name']] = {
                "RAWG_ID": rawg_platform_family['id'],
                "IGDB_ID": None
            }

    # Include IGDB platform families not matched with RAWG
    for igdb_platform_family in igdb_data:
        igdb_platform_family_name = igdb_platform_family['name'].lower()
        if igdb_platform_family_name not in igdb_matched:
            platform_family_mapping[igdb_platform_family['name']] = {
                "RAWG_ID": None,
                "IGDB_ID": igdb_platform_family['id']
            }

    return platform_family_mapping

if __name__ == "__main__":

    rawg_platform_families = load_json_data('generated_json/platform_parents_data_rawg.json')  # Adjust the path as necessary
    igdb_platform_families = load_json_data('generated_json/platform_families_data_igdb.json')  # Adjust the path as necessary

    # Create the platform family mapping
    mapping = create_platform_family_mapping(rawg_platform_families, igdb_platform_families)

    # Save the mapping to a JSON file
    with open('generated_json/platform_family_mapping.json', 'w', encoding='utf-8') as file:
        json.dump(mapping, file, indent=4)

    print("Platform family mapping saved to platform_family_mapping.json")
