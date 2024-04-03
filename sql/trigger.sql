-- Trigger to check if there are games associated to a platform before deleting it
DROP TABLE IF EXISTS TriggerMessage;
DROP TRIGGER IF EXISTS Check_Games_Associated;

CREATE TABLE TriggerMessage (
  message_id INT NOT NULL AUTO_INCREMENT,
  message VARCHAR(100),
  PRIMARY KEY (message_id)
);

DELIMITER $$
CREATE Trigger Check_Games_Associated
BEFORE DELETE ON platform
FOR EACH row
BEGIN
    DECLARE game_count INT;
    SELECT COUNT(*) into game_count
    FROM game_platform
    where platform_id=OLD.platform_id;
	IF game_count >0 THEN
		SIGNAL SQLSTATE '45000';
        INSERT INTO TriggerMessage(message) VALUES ("Cannot delete platform as there are releases associated to it.");
    END IF;
END;
$$

DELIMITER ;
