//A basic search query on an attribute value. 
//Gives the url of the game Soldier Front 2
MATCH (ga:Game)
WHERE ga.name='Soldier Front 2'
RETURN ga.url;

//A query that provides some aggregate data
//Gives the number of games that have genre ID 1
MATCH(ga:Game) -[:HAS_GENRE]-> (ge:Genre {genre_id:1})
RETURN COUNT(ga);

//Find top n entities satisfying a criteria, sorted by an attribute
//Lists the top 3 highest game ID on platform ID 2
MATCH (ga:Game)-[:HAS_PLATFORM]->(p:Platform {platform_id:2})
RETURN ga.game_id
ORDER BY ga.game_id DESC
LIMIT 3;

//Simulate a relational group by query in NoSQL (aggregate per category)
//List the number of games per platform ID
MATCH (ga:Game)-[:HAS_PLATFORM]->(p:Platform)
WITH DISTINCT(p.platform_id) as platform_id, COUNT(ga) as numberOfGames
RETURN platform_id, numberOfGames;


// Create Indices on the previous queries to test the difference in search times.

CREATE INDEX FOR (ga:Game) ON (ga.name);

CREATE INDEX FOR (ge:Genre) ON (ge.genre_id);

CREATE INDEX FOR (ga:Game) ON (ga.game_id);

CREATE INDEX FOR (p:Platform) ON (p.platform_id);


// Full text Index created on Game.name and Game.summary
CREATE FULLTEXT INDEX gamesFullText FOR (g:Game) ON EACH [
    g.name,
    g.summary
];

// Query the Full text Index
CALL db.index.fulltext.queryNodes("gamesFullText", "ninja") YIELD node, score
RETURN node.name, node.summary, score;