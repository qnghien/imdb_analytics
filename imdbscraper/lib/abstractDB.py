'''
This is an abstract class for Database.
Required methods by database class will be defined here
Methods will be implemented in the subsequent child classes
'''

from abc import ABC, abstractmethod

class AbstractDB(ABC):

    def __init__(self, config):
        self.conn = None
        self.cursor = None
        if config is None:
            raise ValueError("Config must be provided for database connection")
        self.config = config

    @abstractmethod
    def start_connection(self):
        """
        Establish connection to the database
        """
        pass

    @abstractmethod
    def end_connection(self):
        """
        Close database connection
        """
        pass
    
    @abstractmethod
    def run_query(self, query: str, params: tuple = None):
        """
        Execute query that modifies the database (e.g. INSERT, UPDATE, DELETE)
        """
        pass

    @abstractmethod
    def get_data(self, query: str, params):
        """
        Fetch data from the database (e.g SELECT)
        """
        pass

    @abstractmethod
    def get_headers(self, query: str):
        """
        Fetch column headers for a query result
        """
        pass


