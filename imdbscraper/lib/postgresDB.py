import psycopg2
from .abstractDB import AbstractDB
import logging
from psycopg2.extras import RealDictCursor
from pdb import set_trace

# Ensure logging is configured
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

class PostgresDB(AbstractDB):
    def __init__(self, config):
        super().__init__(config = config)
        self.config = config
        self.conn = None
        self.cursor = None

    def start_connection(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            print("Postgres connection is established.")
        except Exception as e:
            print(f"Error occurred while attempting to connect to Postgres DB: {e}")
            set_trace()

    def end_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Postgres DB session closed.")

    def run_query(self, query, params=None):
        """
        Executes a query on the PostgreSQL database.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): Parameters to pass to the query.
        """
        try:  # Ensure the connection is in a valid state before executing
            if query.strip().upper().startswith("CREATE DATABASE"):
                self.cursor.execute(query)  # CREATE DATABASE must not run in a transaction block
            else:
                self.cursor.execute(query, params or ())
                self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Error running query on PostgreSQL: {e}")
            if self.conn:
                self.conn.rollback()
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            if self.conn:
                self.conn.rollback()


    def execute_sql_file(self, file_path):
        try:
            with open(file_path, 'r') as sql_file:
                sql_commands = sql_file.read()
                self.cursor.execute(sql_commands)
                print("SQL file executed successfully.")
            self.conn.commit()
        except Exception as e:
            print(f"Error executing SQL file: {e}")
            set_trace()
            self.conn.rollback()

    def get_data(self, query, params):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching data from PostgreSQL: {e}")
            set_trace()
            return []
    
    def get_headers(self, query):
        try:
            self.cursor.execute(query)
            return [desc[0] for desc in self.cursor.description]
        except Exception as e:
            print(f"Error fetching headers from PostgreSQL: {e}")
            return []