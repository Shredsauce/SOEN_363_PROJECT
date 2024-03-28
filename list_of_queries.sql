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

-- Inner Join
Select P.name
From person P 
Join person_job PJ ON P.person_id=PJ.person_id
Join job J on PJ.job_id=J.job_id;

-- Left Join
Select P.name
From person P 
Left join person_job PJ ON P.person_id=PJ.person_id
Left join job J on PJ.job_id=J.job_id;

-- Right Join
Select P.name
From person P 
Right join person_job PJ ON P.person_id=PJ.person_id
Right join job J on PJ.job_id=J.job_id;

-- Full Join (MySQL doeesn't support full join)
(Select P.name
From person P 
Left join person_job PJ ON P.person_id=PJ.person_id
Left join job J on PJ.job_id=J.job_id)
Union all
(Select P.name
From person P 
Right join person_job PJ ON P.person_id=PJ.person_id
Right join job J on PJ.job_id=J.job_id);

-- Correlated Query 1. Find the game name that was the most recently released.
Select G.name, G.release_date
From game G
Where G.release_date= (Select max(G1.release_date)
From game G1
Where G.game_id=G1.game_id);

-- Correlated Query 2. Find the game names that have a platform id less than 6.

-- Correlated Query 3

-- Intersect with SET

-- Intersect without SET

-- Union with SET

-- Union without SET

-- Difference with SET

-- Difference without SET

-- View with hardcoded? 

-- Division using a regular nested query using NOT IN

-- Division using a correlated nested query using NOT EXISTS and EXCEPT

-- Overlap

-- Covering Constraint