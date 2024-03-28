-- Display all games and their platforms as well as the platform families. Include games whose platform does not have a platform family
USE soen_project_phase_1;

SELECT * FROM soen_project_phase_1.game
JOIN game_platform ON game_platform.game_id = game.game_id
JOIN platform ON platform.platform_id = game_platform.platform_id
LEFT JOIN platform_platform_family ON platform.platform_id = platform_platform_family.platform_id
LEFT JOIN platform_family ON platform_family.platform_family_id = platform_platform_family.platform_family_id