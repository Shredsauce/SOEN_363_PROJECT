CREATE TABLE game (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    release_date DATETIME,
    igdb_id INT,
    rawg_id INT
);

CREATE TABLE platform (
    platform_id INT PRIMARY KEY,
    name VARCHAR(255)
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
    job_id INT,
    person_id INT,
    PRIMARY KEY (job_id, person_id),
    FOREIGN KEY (job_id) REFERENCES job(job_id),
    FOREIGN KEY (person_id) REFERENCES person(person_id)  
);
