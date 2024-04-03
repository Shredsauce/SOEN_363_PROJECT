class PlatformFamily:
    def __init__(self, igdb_platform_family_id, rawg_platform_family_id, name):
        self.igdb_platform_family_id = igdb_platform_family_id
        self.rawg_platform_family_id = rawg_platform_family_id
        self.name = name
        self.internal_genre_id = -1