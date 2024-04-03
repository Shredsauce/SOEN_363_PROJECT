class Genre:
    def __init__(self, igdb_genre_id, name):
        self.igdb_genre_id = igdb_genre_id
        self.name = name
        self.internal_genre_id = -1