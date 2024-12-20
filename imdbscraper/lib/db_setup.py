from postgresDB import PostgresDB
from dotenv import load_dotenv
import os
from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

load_dotenv()

config = {
    "dbname": "postgres",  # Start with the default database
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

def setup_database():
    try:
        # Connect to the default database with psycopg2 directly to create the new database
        connection = connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"],
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Set autocommit mode

        with connection.cursor() as cursor:
            print("Creating database 'imdb_analytics'...")
            try:
                cursor.execute("CREATE DATABASE imdb_analytics;")
                print("Database 'imdb_analytics' created successfully.")
            except Exception as e:
                print(f"Database 'imdb_analytics' already exists or could not be created: {e}")

        connection.close()
    except Exception as e:
        print(f"Error creating database: {e}")

    # Update config to the newly created 'imdb_analytics' db
    config["dbname"] = "imdb_analytics"
    db = PostgresDB(config)
    db.start_connection()

    # Run the SQL file to create tables
    db.execute_sql_file("../../sql/init.sql")
    db.end_connection()

if __name__ == "__main__":
    setup_database()
