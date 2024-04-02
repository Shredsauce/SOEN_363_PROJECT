CREATE TABLE game (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    summary TEXT,
    url VARCHAR(255),
    release_date DATETIME,
    igdb_id INT UNIQUE,
    rawg_id INT
);

CREATE TABLE platform (
    platform_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_family_id INT,
    igdb_platform_id INT UNIQUE,
    name VARCHAR(255)
);

CREATE TABLE platform_family (
    platform_family_id INT AUTO_INCREMENT PRIMARY KEY,
    igdb_platform_family_id INT UNIQUE,
    name VARCHAR(255)
);

CREATE TABLE platform_platform_family (
    platform_platform_family_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_family_id INT,
    platform_id INT,
    FOREIGN KEY (platform_family_id) REFERENCES platform_family(platform_family_id),
    FOREIGN KEY (platform_id) REFERENCES platform(platform_id)
);

CREATE TABLE game_platform (
    game_platform_id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT,
    platform_id INT,
    FOREIGN KEY (game_id) REFERENCES game(game_id),
    FOREIGN KEY (platform_id) REFERENCES platform(platform_id)
);

CREATE TABLE person (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    rawg_id VARCHAR(255)
);

CREATE TABLE job (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE person_job (
    person_job_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    person_id INT,
    FOREIGN KEY (job_id) REFERENCES job(job_id),
    FOREIGN KEY (person_id) REFERENCES person(person_id)  
);
