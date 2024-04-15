LOAD CSV WITH HEADERS FROM 'file:///game.csv' AS row
WITH toInteger(row.game_id) AS game_id,
row.name AS name,
row.summary AS summary,
row.url AS url,
date(left(row.release_date, 10)) AS release_date,
toInteger(row.igdb_id) AS igdb_id,
toInteger(row.rawg_id) AS rawg_id
MERGE (ga:Game {game_id:game_id})
    SET ga.name = name,
	ga.summary = summary,
	ga.url = url,
	ga.release_date = release_date,
	ga.igdb_id = igdb_id,
	ga.rawg_id = rawg_id
Return count(ga);

LOAD CSV WITH HEADERS FROM 'file:///genre.csv' AS row
WITH toInteger(row.genre_id) AS genre_id,
toInteger(row.igdb_genre_id) AS igdb_genre_id,
toInteger(row.rawg_genre_id) AS rawg_genre_id,
row.name AS name
MERGE (ge:Genre {genre_id:genre_id})
    SET ge.igdb_genre_id = igdb_genre_id,
	ge.rawg_genre_id = rawg_genre_id,
	ge.name = name
Return count(ge);

LOAD CSV WITH HEADERS FROM 'file:///game_genre.csv' AS row
MATCH (ga:Game { game_id: toInteger(row.game_id) })
MATCH (ge:Genre { genre_id: toInteger(row.genre_id) })
MERGE (ga)-[:HAS_GENRE]->(ge);

LOAD CSV WITH HEADERS FROM 'file:///platform.csv' AS row
WITH toInteger(row.platform_id) AS platform_id,
toInteger(row.platform_family_id) AS platform_family_id,
toInteger(row.igdb_platform_id) AS igdb_platform_id,
toInteger(row.rawg_platform_id) AS rawg_platform_id,
row.name AS name
MERGE (p:Platform {platform_id:platform_id})
    SET p.platform_family_id = platform_family_id,
	p.igdb_platform_id = igdb_platform_id,
	p.rawg_platform_id = rawg_platform_id,
	p.name = name
Return count(p);

LOAD CSV WITH HEADERS FROM 'file:///platform_family.csv' AS row
WITH toInteger(row.platform_family_id) AS platform_family_id,
toInteger(row.igdb_platform_family_id) AS igdb_platform_family_id,
toInteger(row.rawg_platform_family_id) AS rawg_platform_family_id,
row.name AS name
MERGE (pf:Platform_Family {platform_family_id:platform_family_id})
    SET pf.igdb_platform_family_id = igdb_platform_family_id,
	pf.rawg_platform_family_id = rawg_platform_family_id,
	pf.name = name
Return count(pf);

LOAD CSV WITH HEADERS FROM 'file:///game_platform.csv' AS row
MATCH (ga:Game { game_id: toInteger(row.game_id) })
MATCH (p:Platform { platform_id: toInteger(row.platform_id) })
MERGE (ga)-[:HAS_PLATFORM]->(p);

LOAD CSV WITH HEADERS FROM 'file:///platform_logo.csv' AS row
WITH toInteger(row.platform_logo_id) AS platform_logo_id,
row.image_url AS image_url,
toInteger(row.height) AS height,
toInteger(row.width) AS width,
toInteger(row.platform_id) AS platform_id
MERGE (pl:Platform_Logo {platform_logo_id:platform_logo_id})
    SET pl.platform_logo_id = platform_logo_id,
	pl.image_url = image_url,
	pl.height = height,
	pl.width = width,
	pl.platform_id = platform_id
Return count(p);

MATCH (p:Platform { platform_id:platform_id })
MATCH (pl:Platform_Logo { platform_logo_id:platform_logo_id })
MERGE(p)-[:HAS_PLATFORM_LOGO]->(pl);