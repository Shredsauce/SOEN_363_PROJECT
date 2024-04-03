class Game:
    """
    Game object to hold all of the game info
    """
    def __init__(self, name, summary, url, release_date, igdb_id, rawg_id):
        self.name = name
        self.summary = summary
        self.url = url
        self.release_date = release_date
        self.igdb_id = igdb_id
        self.rawg_id = rawg_id

    def __repr__(self):
        """

        Used for neatly printing this game's info.

        """
        to_string = f"Game name: {self.name}\n"
        to_string += f"Summary: {self.summary}\n"
        to_string += f"URL: {self.url}\n"
        to_string += f"Release date: {self.release_date}\n"
        to_string += f"IGDB id: {self.igdb_id}\n"
        to_string += f"Rawg id: {self.rawg_id}\n"

        return to_string

    def to_dict(self):
        """

        Returns: The game object to be used in a dict.

        """
        return {
            "name": self.name,
            "summary": self.summary,
            "url": self.url,
            "release_date": self.release_date,
            "igdb_id": self.igdb_id,
            "rawg_id": self.rawg_id,
        }
