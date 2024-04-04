CREATE TABLE game (
    game_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    summary TEXT,
    url VARCHAR(255),
    release_date DATETIME,
    igdb_id INT UNIQUE,
    rawg_id INT
);

CREATE TABLE genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    igdb_genre_id INT UNIQUE,
    rawg_genre_id INT UNIQUE,
    name VARCHAR(255)
);

CREATE TABLE game_genre (
    game_genre_id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT,
    genre_id INT,
    FOREIGN KEY (game_id) REFERENCES game(game_id),
    FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);

CREATE TABLE platform (
    platform_id INT AUTO_INCREMENT PRIMARY KEY,
    platform_family_id INT,
    igdb_platform_id INT UNIQUE,
    rawg_platform_id INT UNIQUE,
    name VARCHAR(255)
);

CREATE TABLE platform_family (
    platform_family_id INT AUTO_INCREMENT PRIMARY KEY,
    igdb_platform_family_id INT UNIQUE,
    rawg_platform_family_id INT UNIQUE,
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

CREATE TABLE platform_logo (
    platform_logo_id INT AUTO_INCREMENT PRIMARY KEY,
    image_url TEXT,
    height int,
    width int,
    platform_id INT,
    FOREIGN KEY (platform_id) REFERENCES platform(platform_id)
);

