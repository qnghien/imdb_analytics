-- Create database
--CREATE DATABASE imdb_analytics WITH OWNER = postgres;
--GRANT ALL PRIVILEGES ON DATABASE "imdb_analytics" TO postgres;

-- -- Connect to the database (if using psql CLI)
-- \c imdb_analytics;

-- Create top_250_imdb table
CREATE TABLE top_250_imdb (
    movie_id VARCHAR(10) PRIMARY KEY,
    title TEXT NOT NULL,
    ranking INT NOT NULL,
    release_year INT,
    runtime VARCHAR(8),
    rating DECIMAL(3, 2),
    vote_count INT,
    "certificate" TEXT,
    "description" TEXT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Create movie_financials table
CREATE TABLE movie_financials (
    movie_id VARCHAR(10) PRIMARY KEY,
    domestic_opening BIGINT,
    domestic_revenue BIGINT,
    international_revenue BIGINT,
    budget BIGINT,
    last_updated TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (movie_id) REFERENCES top_250_imdb (movie_id)
);

-- Create movie_productions table
CREATE TABLE movie_productions (
    movie_id VARCHAR(10) PRIMARY KEY,
    domestic_distributor VARCHAR(255),
    genres TEXT,
    director TEXT,
    movie_casts TEXT,
    FOREIGN KEY (movie_id) REFERENCES top_250_imdb (movie_id)
);

-- Create movie_articles table
CREATE TABLE movie_articles (
    movie_id VARCHAR(10),
    article_title TEXT,
    article_id VARCHAR(14) PRIMARY KEY,
    article_link TEXT,
    publication_date DATE,
    FOREIGN KEY (movie_id) REFERENCES top_250_imdb (movie_id)
);

-- Create top_250_imdb_history table
CREATE TABLE top_250_imdb_history (
    id SERIAL PRIMARY KEY,
    movie_id VARCHAR(10),
    title TEXT NOT NULL,
    ranking INT NOT NULL,
    release_year INT,
    runtime VARCHAR(8),
    rating DECIMAL(3, 2),
    vote_count INT,
    "certificate" TEXT,
    "description" TEXT,
    snapshot_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (movie_id) REFERENCES top_250_imdb (movie_id),
    CONSTRAINT unique_snapshot UNIQUE (movie_id, snapshot_date)
);

-- Add indexes for performance
CREATE INDEX idx_movie_financials_movie_id ON movie_financials (movie_id);
CREATE INDEX idx_movie_productions_movie_id ON movie_productions (movie_id);
CREATE INDEX idx_movie_articles_movie_id ON movie_articles (movie_id);
CREATE INDEX idx_imdb_history_movie_id ON top_250_imdb_history (movie_id);
