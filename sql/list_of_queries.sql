-- Display all games and their platforms as well as the platform families. Include games whose platform does not have a platform family
USE soen_project_phase_1;

SELECT * FROM soen_project_phase_1.game
JOIN game_platform ON game_platform.game_id = game.game_id
JOIN platform ON platform.platform_id = game_platform.platform_id
LEFT JOIN platform_platform_family ON platform.platform_id = platform_platform_family.platform_id
LEFT JOIN platform_family ON platform_family.platform_family_id = platform_platform_family.platform_family_id;

-- List all games
Select *
From game;

-- List the number of games per platform 
Select platform_id, count(GP.game_id)
From game_platform GP
Group by platform_id;

-- List the number of games per platform (Include the platform name)
Select p.platform_id, p.name, count(gp.game_id)
From game_platform gp
JOIN platform p ON gp.platform_id = p.platform_id
Group by platform_id;

-- List all games that have both a Rawg ID and IGDB ID
SELECT *
FROM game
WHERE rawg_id IS NOT NULL AND igdb_id IS NOT NULL;

-- List all the platforms that have at least 2 games
Select platform_id, count(GP.game_id) as gameCount
From game_platform GP
Group by platform_id
Having gameCount >= 2;

-- List all the game names that run on Xbox One 
Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='Xbox One';

-- List all the game names that run on a platform
Select G.name
From game G 
Join game_platform GP ON G.game_id=GP.game_id
Join platform P on P.platform_id=GP.platform_id;

-- List all genres
SELECT * 
from genre;

--List all games with at least 2 genres
SELECT game_id, count(GG.genre_id) as genreCOUNT
FROM game_genre GG
Group by game_id
Having genreCOUNT >=2;

--Trigger to check if there are games associated to a platform before deleting it
CREATE Trigger Check_Games_Associated
BEFORE DELETE ON platform
FOR EACH row
BEGIN
    DECLARE game_count INT
    SELECT COUNT(*) into game_count
    FROM game_platform
    where platform_id=OLD.platform_id
if game_count >0 THEN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE = "Cannot delete platform as there are releases associated to it."
    END IF;
END;

-- Inner Join
Select G.game_id, G.name, G.release_date, Ge.name
From game G 
Join game_genre GG ON G.game_id=GG.game_id
Join genre Ge on GG.genre_id=Ge.genre_id;

-- Left Join
Select *
From game G
LEFT JOIN game_genre
on G.game_id = game_genre.game_id
ORDER BY G.game_id	

-- Right Join
Select G.game_id, Ge.name
From game G 
Right join game_genre GG ON G.game_id=GG.game_id
Right join genre Ge on GG.genre_id=Ge.genre_id;

-- Full Join (MySQL doeesn't support full join)
(Select G.game_id, G.name, G.summary, Ge.genre_id, Ge.name
From game G 
Left join game_genre GG ON G.game_id=GG.game_id
Left join genre Ge on GG.genre_id=Ge.genre_id)
Union all
(Select G.game_id, G.name, G.summary, Ge.genre_id, Ge.name
From game G 
Right join game_genre GG ON G.game_id=GG.game_id
Right join genre Ge on GG.genre_id=Ge.genre_id);

-- Correlated Query 1. Find the game name that was the most recently released.
Select G1.name, G1.release_date
From game G1
Where G1.release_date = (
Select MAX(G2.release_date)
From game G2
);

-- Correlated Query 2. Find the game id that have a platform id less than the average platform id.
Select GP.game_id, GP.platform_id
From game_platform GP
Where GP.platform_id < (
Select AVG(GP2.platform_id)
From game_platform GP2
);

-- Correlated Query 3. Find the number of platforms each game runs on.
Select G.name,
(Select count(*)
From game_platform GP
Where GP.game_id=G.game_id) as number_of_platforms
From game G;

-- Intersect with SET
(Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='Xbox One')
intersect
(Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='Xbox Series X|S');

-- Intersect without set operation. List all the game names that run on Xbox One and on Xbox Series X|S
Select G.name as xboxGames
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id
and GP.platform_id=P.platform_id
and P.name = 'Xbox One'
and G.name in (
Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id
and GP.platform_id=P.platform_id
and P.name = 'Xbox Series X|S');

-- Union with SET. List all the game names that run on Xbox One or on iOS
(Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='Xbox One')
union
(Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='iOS');

-- Union without SET. List all the game names that run on Xbox One or on iOS
Select G.name as xboxOneOrIOS
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and (P.name='Xbox One' or P.name='iOS');

-- Difference with SET. List all the game names that run on Xbox One but not on iOS.
(Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='Xbox One')
except
(Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id and P.platform_id=GP.platform_id and P.name='iOS');

-- Difference without SET. List all the game names that run on Xbox One but not on iOS.
Select G.name as xboxNotIOS
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id
and GP.platform_id=P.platform_id
and P.name = 'Xbox One'
and G.name NOT IN (
Select G.name
From game G, game_platform GP, platform P
Where G.game_id=GP.game_id
and GP.platform_id=P.platform_id
and P.name = 'iOS');

-- View with hardcoded? 
Drop view if exists ios_platform;
Create View ios_platform as
(select * from platform where platform_id=1);

-- Division using a regular nested query using NOT IN (what game is on all platforms)
SELECT * FROM game_platform
Where game_id NOT IN (SELECT game_id FROM ( (SELECT game_id, platform_id FROM (select platform_id from platform) as P 
CROSS JOIN
     (SELECT distinct game_id FROM game_platform) as UniqueGames)
EXCEPT
(SELECT game_id, platform_id FROM game_platform)) AS ExceptResult
);

-- Equivalent query that runs in MySQL (doesn't use EXCEPT)
SELECT gp.game_id, g.name
FROM game_platform gp
JOIN game g ON g.game_id = gp.game_id
GROUP BY gp.game_id
HAVING COUNT(DISTINCT gp.platform_id) = (SELECT COUNT(*) FROM platform);

-- Division using a correlated nested query using NOT EXISTS and EXCEPT (what game is on all platforms)
SELECT * FROM game_platform AS gp
WHERE NOT EXISTS (
    (SELECT p.platform_id FROM platform AS p)
    EXCEPT
    (SELECT sp.platform_id FROM game_platform as sp WHERE sp.game_id = gp.game_id)
);

-- Overlap. List the platforms that belong to more than one platform family.
Select P.name as moreThanOnePlatformFamily
From platform P, platform_family PF, platform_platform_family PPF
Where P.platform_id=PPF.platform_id
and PF.platform_family_id=PPF.platform_family_id
Group by moreThanOnePlatformFamily
Having count(PF.platform_family_id) > 1;

-- Covering Constraint. List the platforms that don't belong to a platform family.
Select P.name as noFamily
From platform P
Where NOT Exists(
Select *
From platform_platform_family PPF
Where P.platform_id=PPF.platform_id);
