import psycopg2
from dotenv import load_dotenv
import os
import sys

load_dotenv()

def fetch_top_250_movie_ids():
    """Fetches the latest movie IDs from the top_250_imdb_history table."""
    conn = None
    movie_ids = []

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        with conn.cursor() as cur:
            cur.execute("SELECT movie_id FROM top_250_imdb_history ORDER BY snapshot_date DESC LIMIT 250;")
            rows = cur.fetchall()
            movie_ids = [row[0] for row in rows]
    except Exception as e:
        print(f"Error fetching movie IDs: {e}")
    finally:
        if conn:
            conn.close()

    return movie_ids


def update_top_250_imdb_table():
    """
    Updates the top_250_imdb table with the latest data from the top_250_imdb_history table.
    """
    conn = None

    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        with conn.cursor() as cur:
            # Delete movies that are no longer in the top 250
            movie_ids = fetch_top_250_movie_ids()
            if not movie_ids:
                print("No movie IDs fetched. Aborting update.")
                return

            # Update `top_250_imdb` table with the latest data
            cur.execute("""
                DELETE FROM top_250_imdb
                WHERE movie_id NOT IN %s;
                """
            , (tuple(movie_ids),))

            # Insert or update rows in the `top_250_imdb` table
            cur.execute("""
                INSERT INTO top_250_imdb (movie_id, title, ranking, release_year, runtime, rating, vote_count, certificate, description, last_updated)
                SELECT movie_id, title, ranking, release_year, runtime, rating, vote_count, certificate, description, NOW()
                FROM top_250_imdb_history
                WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM top_250_imdb_history)
                ON CONFLICT (movie_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    ranking = EXCLUDED.ranking,
                    release_year = EXCLUDED.release_year,
                    runtime = EXCLUDED.runtime,
                    rating = EXCLUDED.rating,
                    vote_count = EXCLUDED.vote_count,
                    certificate = EXCLUDED.certificate,
                    description = EXCLUDED.description,
                    last_updated = NOW();
            """)

            conn.commit()
            print("Top 250 IMDb table successfully updated.")

    except Exception as e:
        print(f"Error updating top_250_imdb table: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    env_file_path = os.path.join(os.getcwd(), 'lib', '.env')
    load_dotenv(env_file_path)
    if sys.argv[1] == 'update':
        update_top_250_imdb_table()
    else: 
        print("Command not found")