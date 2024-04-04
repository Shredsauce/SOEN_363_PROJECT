class Platform:
    def __init__(self, igdb_platform_id, rawg_platform_id, name, platform_family):
        self.igdb_platform_id = igdb_platform_id
        self.rawg_platform_id = rawg_platform_id
        self.name = name
        self.platform_family = platform_family
        self.internal_platform_id = None