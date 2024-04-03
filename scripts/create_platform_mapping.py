import json
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_data(filename):
    """Load JSON data from a file."""
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)


def create_platform_mapping(rawg_data, igdb_data):
    """Create a mapping of platform names to their IDs in both RAWG and IGDB."""
    platform_mapping = {}

    # Process RAWG data
    for rawg_platform in rawg_data['results']:
        # Normalize the platform name for comparison
        rawg_platform_name = rawg_platform['name'].lower()

        # Search for a corresponding platform in IGDB data
        for igdb_platform in igdb_data:
            igdb_platform_name = igdb_platform['name'].lower()

            if rawg_platform_name == igdb_platform_name:
                # Create a mapping entry with IDs from both databases
                platform_mapping[rawg_platform['name']] = {
                    "RAWG_ID": rawg_platform['id'],
                    "IGDB_ID": igdb_platform['id']
                }
                # If platform versions are required, you'd need to dig into the 'versions' field here for IGDB
                break  # Found a match, no need to continue this inner loop

    return platform_mapping


if __name__ == "__main__":
    # Load platform data from JSON files
    rawg_platforms = load_json_data('generated_json/platforms_data_rawg.json')  # Adjust the path as necessary
    igdb_platforms = load_json_data('generated_json/platforms_data_igdb.json')  # Adjust the path as necessary

    # Create the platform mapping
    mapping = create_platform_mapping(rawg_platforms, igdb_platforms)

    # Save the mapping to a JSON file
    with open('generated_json/platform_mapping.json', 'w', encoding='utf-8') as file:
        json.dump(mapping, file, indent=4)

    print("Platform mapping saved to platform_mapping.json")
