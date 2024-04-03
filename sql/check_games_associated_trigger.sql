DELIMITER $$

CREATE TRIGGER Check_Games_Associated
BEFORE DELETE ON platform
FOR EACH ROW
BEGIN
    DECLARE game_count INT;
    SELECT COUNT(*) INTO game_count FROM game_platform WHERE platform_id = OLD.platform_id;
    IF game_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete platform as there are releases associated to it.';
    END IF;
END$$

DELIMITER ;