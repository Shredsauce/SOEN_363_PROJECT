if __name__ == '__main__':
    import json

    with open('../generated_json/all_platforms_with_logos_igdb.json', 'r') as file:
        platforms_data = json.load(file)

    with open('../generated_json/all_platform_logos_igdb.json', 'r') as file:
        logos_data = json.load(file)

    # Create a mapping from logo ID to platform ID
    logo_to_platform_id = {platform["platform_logo"]: platform["id"] for platform in platforms_data if
                           "platform_logo" in platform}

    # Update logos data with platform IDs
    for logo in logos_data:
        if logo["id"] in logo_to_platform_id:
            logo["platform_id"] = logo_to_platform_id[logo["id"]]

    # Save the updated logos data back to a new JSON file
    with open('../generated_json/updated_logos_data.json', 'w') as file:
        json.dump(logos_data, file, indent=4)

    print("Updated logos data with platform IDs has been saved.")
