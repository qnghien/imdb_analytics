import os
import csv
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


def export_file(table_name, output_format, file_name):
    conn = None
    try:
        # Validate output format
        if output_format.lower() not in {"csv", "json"}:
            print("Invalid format specified. Please choose 'csv' or 'json'.")
            return

        # Ensure output directory exists
        os.makedirs("./output", exist_ok=True)

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Fetch all data from the specified table
            cur.execute(f"SELECT * FROM {table_name};")
            rows = cur.fetchall()

            if not rows:
                print(f"No data found in the table '{table_name}'.")
                return

            output_file = f"./output/{file_name}"

            if output_format.lower() == "csv":
                # Export to CSV
                csv_file = f"{output_file}.csv"
                with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    # Write header
                    writer.writerow(rows[0].keys())
                    # Write rows
                    for row in rows:
                        writer.writerow(row.values())
                print(f"Data exported to {csv_file}")

            elif output_format.lower() == "json":
                # Export to JSON
                json_file = f"{output_file}.json"
                with open(json_file, mode="w", encoding="utf-8") as file:
                    json.dump(rows, file, indent=4)
                print(f"Data exported to {json_file}")

    except psycopg2.Error as e:
        logging.error(f"Error accessing the database: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()
    

if __name__ == "__main__":
    env_file_path = os.path.join(os.getcwd(), 'lib', '.env')
    load_dotenv(env_file_path)
    table_name = sys.argv[1]
    output_format = sys.argv[2]
    file_name = sys.argv[3]
    export_file(table_name, output_format, file_name)
