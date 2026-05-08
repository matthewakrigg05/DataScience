import pandas as pd

class DataManager:
    """
    This class is designed for loading, storing, and uploading datasets used in this project. These are kept in a database, where each 
    project has its own schema. 
    
    These are unique to the database that I am working with, and unlikely to work for others, but can be 
    used as inspiration for those who work with Postgresql DBs in their python prjects!
    """

    def __init__(self, connection_params):
        self.connection_params = connection_params
        self.connection = None


    # Connection/Internal functions
    def _connect(self):
        pass

    
    def _close(self):
        pass

    
    def _commit(self):
        pass


    def _rollback(self):
        pass


    # Metadata Functions
    def get_schema(table_name: str) -> str:
        pass


    def ensure_schema(table_name: str,
                      df: pd.DataFrame) -> str:
        pass


    def table_exists(table_name: str) -> str:
        pass
    

    # Accessing functions 
    def load_table(table_name: str) -> pd.DataFrame:
        pass


    def load_from_query(sql: str,
                        params=None) -> pd.DataFrame:
        pass


    def load_filtered(table_name: str,
                      filters: dict) -> pd.DataFrame:
        pass


    # Uploading functions
    def upload_table(table_name: str,
                     df: pd.DataFrame,
                     if_exists="replace") -> None:
        pass


    def replace_table(table_name: str,
                      df: pd.DataFrame) -> None:
        pass


    def append_to_table(table_name: str,
                        df: pd.DataFrame) -> None:
        pass


    def upsert(table_name: str,
               df: pd.DataFrame) -> None:
        pass


    def bulk_insert(table_name: str,
                    df: pd.DataFrame) -> None:
        pass


    # Table Management Functions
    def create_table(table_name: str,
                     schema: str) -> None:
        pass


    def delete_table(table_name: str) -> None:
        pass