from itemadapter import ItemAdapter
import datetime
import logging
import csv
import os
from imdbscraper.items import BoxofficeFinancialsItem, BoxofficeProductionItem, BoxofficeArticleItem, ImdbscraperItem
from .lib.postgresDB import PostgresDB
from psycopg2 import sql
from dotenv import load_dotenv

class ImdbscraperPipeline:
    def process_item(self, item, spider):
        return item


class IMDBDataCleaner:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Convert length to HH:MM:SS format
        if 'runtime' in adapter:
            adapter['runtime'] = str(datetime.timedelta(seconds=adapter['runtime']))
        
        # Handle missing certificate field
        if adapter.get('certificate') is None:
            adapter['certificate'] = "No rating"
        else:
            adapter['certificate'] = adapter['certificate'].get('rating', "No rating")

        # Replace None with 'NA'
        self.replace_none_with_na(adapter)

        return item

    @staticmethod
    def replace_none_with_na(adapter):
        for field_name, value in adapter.items():
            if value is None:
                adapter[field_name] = 'NA'


class BoxOfficeDataCleaner:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Clean financial data
        if 'domestic_revenue' in adapter:
            adapter['domestic_revenue'] = self.clean_money(adapter['domestic_revenue'])
        if 'international_revenue' in adapter:
            adapter['international_revenue'] = self.clean_money(adapter['international_revenue'])
        if 'domestic_opening' in adapter:
            adapter['domestic_opening'] = self.clean_money(adapter['domestic_opening'])
        if 'budget' in adapter:
            adapter['budget'] = self.clean_money(adapter['budget'])

        # Clean genres field
        if 'genres' in adapter:
            adapter['genres'] = self.clean_genres(adapter['genres'])

        # Cast as a comma-separated string
        if 'movie_casts' in adapter and isinstance(adapter['movie_casts'], list):
            adapter['movie_casts'] = ', '.join(adapter['movie_casts'])

        # Replace None with 'NA'
        self.replace_none_with_na(adapter)

        return item

    @staticmethod
    def clean_money(value):
        """
        Removes non-numeric characters and converts money to an integer.
        Example: "$123,456,789" -> 123456789
        """
        if value:
            return int(value.replace('$', '').replace(',', ''))
        return 'NA'

    @staticmethod
    def clean_genres(text):
        """
        Cleans and formats the genres field.
        Example: "Crime\n\n        Drama" -> "Crime, Drama"
        """
        if text and isinstance(text, str):
            parts = [part.strip() for part in text.split('\n') if part.strip()]
            capitalized_parts = [part for part in parts if part[0].isupper()]
            return ", ".join(capitalized_parts)
        return 'NA'

    @staticmethod
    def replace_none_with_na(adapter):
        for field_name, value in adapter.items():
            if value is None:
                adapter[field_name] = 'NA'


class SeparateCSVExportPipeline:
    def open_spider(self, spider):

        # Ensure the 'output' directory exists
        output_dir = './output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Open separate CSV files for each item type
        self.financials_file = open(f'{output_dir}/financials.csv', 'w', newline='', encoding='utf-8')
        self.production_file = open(f'{output_dir}/production.csv', 'w', newline='', encoding='utf-8')
        self.articles_file = open(f'{output_dir}/articles.csv', 'w', newline='', encoding='utf-8')

        # Initialize CSV writers
        self.financials_writer = None
        self.production_writer = None
        self.articles_writer = None

    def process_item(self, item, spider):
        # First, clean the item using BoxOfficeDataCleaner
        cleaner = BoxOfficeDataCleaner()
        item = cleaner.process_item(item, spider)

        # Write the cleaned item to the appropriate CSV
        if isinstance(item, BoxofficeFinancialsItem):
            if self.financials_writer is None:
                # Write header once
                self.financials_writer = csv.DictWriter(self.financials_file, fieldnames=item.keys())
                self.financials_writer.writeheader()
            self.financials_writer.writerow(item)

        elif isinstance(item, BoxofficeProductionItem):
            if self.production_writer is None:
                self.production_writer = csv.DictWriter(self.production_file, fieldnames=item.keys())
                self.production_writer.writeheader()
            self.production_writer.writerow(item)

        elif isinstance(item, BoxofficeArticleItem):
            if self.articles_writer is None:
                self.articles_writer = csv.DictWriter(self.articles_file, fieldnames=item.keys())
                self.articles_writer.writeheader()
            self.articles_writer.writerow(item)

        return item

    def close_spider(self, spider):
        # Close all open files
        self.financials_file.close()
        self.production_file.close()
        self.articles_file.close()


class PostgresPipeline:

    def __init__(self, config):
        self.config = config
        self.db = PostgresDB(self.config)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Load .env from the lib directory
        env_file_path = os.path.join(os.path.dirname(__file__), 'lib', '.env')
        load_dotenv(env_file_path)

        # Get database configuration from environment variables
        config = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

        # Raise an exception if the config is not set properly
        if not config["dbname"] or not config["user"]:
            raise NotConfigured("Database configuration not found in .env file")

        # Return an instance of PostgresPipeline with the config
        return cls(config)

    def open_spider(self, spider):
        self.db.start_connection()

    def process_item(self, item, spider):
        # Process item and insert into DB

        # Select the appropriate data cleaner based on the spider name
        if spider.name == "imdb":
            cleaner = IMDBDataCleaner()
        elif spider.name == "box_office":
            cleaner = BoxOfficeDataCleaner()
        else:
            logging.warning(f"No data cleaner found for spider: {spider.name}")
            cleaner = None

        # Clean the item if a cleaner is available
        if cleaner:
            item = cleaner.process_item(item, spider)

        # Convert the item into an adapter for flexible key-value access
        adapter = ItemAdapter(item)
        # Get the table name dynamically
        table_name = self.determine_table(item)
        columns = adapter.keys()
        values = adapter.values()

        # Construct the plain SQL query
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(values))})"
        params = tuple(values)

        # Run the query
        self.db.run_query(query, params)

        return item
    
    def close_spider(self, spider):
        self.db.end_connection()

    @staticmethod
    def determine_table(item):
        if isinstance(item, ImdbscraperItem):
            return "top_250_imdb_history"
        if isinstance(item, BoxofficeFinancialsItem):
            return "movie_financials"
        elif isinstance(item, BoxofficeProductionItem):
            return "movie_productions"
        elif isinstance(item, BoxofficeArticleItem):
            return "movie_articles"
        else:
            return "unknown_table"

