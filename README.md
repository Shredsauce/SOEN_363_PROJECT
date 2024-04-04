# SOEN 363 Team Project Phase 1

**Team Members:**
- Malcolm Arcand Laliberté (26334792)
- Thaneekan Thankarajah (40192306)
- Hao Yi Liu (40174210)
- Jonah Ball (40178421)

In the first phase of our project for SOEN 363, our team worked on merging gaming data from two different sources: IGDB and Rawg. We ran into a few hurdles, especially with figuring out how to stitch together data from both APIs. We used tools such as MySQL Workbench, Python to automate data handling, and Git to keep all our work in sync. Our main goal was to make sure we could pull the specific data we needed from both IGDB and Rawg and then find a way to fit it all together into one database.

## APIs

### IGDB
IGDB allows for specific data requests similar to SQL queries. We could retrieve comprehensive data from a single request to the `/games` endpoint by specifying the desired fields.

### Rawg
Rawg returns platform information by default in its `/games` endpoint, leading to larger, less targeted responses. However, it provides useful filtering options which we utilized in creating our JSON mapping files.

## Tools Used

- **MySQL + Workbench:** Chosen for our team's familiarity and the availability of resources. Used MySQL Workbench for queries and data manipulation.
- **dbForge Studio:** Generated DML statements based on existing database records.
- **Postman:** Facilitated API request management and previewing JSON responses.
- **Python + JSON:** Automated data collection and preprocessing for database insertion.
- **GitHub Repository:** Enabled collaboration and version control among team members.

## Challenges

Our main challenge was mapping datasets from IGDB and Rawg for integration into a single database. We leveraged JSON to identify common attributes and relationships, enabling efficient data merging. We also faced technical challenges related to file management across different development environments (PyCharm and VS Code), which we resolved by standardizing file paths relative to the project root.

## Entity Relationship Diagram

Our ERD outlines the relationships between Game, Platform, and Genre entities, indicating many-to-many relationships and total or partial participation. It also details the ISA relationship between Platform and Platform Family entities, and the one-to-one relationship between Platform and Platform Logo entities.

## Database Design

Our MySQL schema consists of seven tables: `game`, `genre`, `platform`, `platform_family`, `platform_logo`, `game_platform`, and `game_genre`. We created unique primary keys for each table, independent of external API IDs. The `game_platform` and `game_genre` tables facilitate the relationships between games and platforms, and games and genres, respectively.

### Example DDL for game_genre table:

```sql
CREATE TABLE game_genre (
   game_id INT,
   genre_id INT,
   FOREIGN KEY (game_id) REFERENCES game(game_id),
   FOREIGN KEY (genre_id) REFERENCES genre(genre_id),
   PRIMARY KEY (game_id, genre_id)
);
