CREATE DATABASE IF NOT EXISTS recommend_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE recommend_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    nickname VARCHAR(64) DEFAULT '',
    role VARCHAR(16) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    content TEXT,
    category VARCHAR(32) DEFAULT 'general',
    source VARCHAR(128) DEFAULT '',
    image_url VARCHAR(512) DEFAULT '',
    view_count INT DEFAULT 0,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS music (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    artist VARCHAR(128) DEFAULT '',
    album VARCHAR(128) DEFAULT '',
    genre VARCHAR(32) DEFAULT 'pop',
    duration INT DEFAULT 0,
    cover_url VARCHAR(512) DEFAULT '',
    play_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS user_behaviors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_type VARCHAR(16) NOT NULL,
    item_id INT NOT NULL,
    action_type VARCHAR(16) NOT NULL,
    rating FLOAT DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_type (user_id, item_type),
    INDEX idx_item (item_type, item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS recommendation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_type VARCHAR(16) NOT NULL,
    item_id INT NOT NULL,
    score FLOAT DEFAULT 0.0,
    algorithm VARCHAR(32) DEFAULT 'collaborative_filtering',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    module VARCHAR(32) NOT NULL,
    action VARCHAR(32) NOT NULL,
    detail VARCHAR(512) DEFAULT '',
    ip VARCHAR(64) DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
