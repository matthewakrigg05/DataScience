import pandas as pd
import psycopg2 as p2
import os

from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

class DataManager:
    """
    This class is designed for loading, storing, and uploading datasets used in this project. These are kept in a database, where each 
    project has its own schema. Connections and use of a Postgresql database uses the psycopg2 package; for docs on this package, follow
    this link: https://www.psycopg.org/docs/connection.html.
    
    These are unique to the database that I am working with, and unlikely to work for others, but can be 
    used as inspiration for those who work with Postgresql DBs in their python prjects!
    """

    connection = None
    dbname=os.getenv("DB_NAME")
    user=os.getenv("DB_USER")
    password=os.getenv("DB_PASSWORD")
    current_server_address = None

    def __init__(self, current_server_address=None):
        if current_server_address is None:
            self.current_server_address = os.getenv("DB_HOST")
        else:
            self.current_server_address = current_server_address

        self._connect()
        self._close()


    # Connection/Internal functions
    def _connect(self) -> None:
        """
        This is a helper function for connecting to the Postgresql database hosting the datasets to be used. This connection function 
        is expected to be used for each high level transaction, and closed in the same transaction, for example in load_table, or 
        load_filtered. This will be used in combination with the other helper methods, which should also appear in each of the other
        functions.
        """
        try:
            self.connection = p2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.current_server_address
            )
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

    
    def _close(self) -> None:
        """
        Helper function for closing the connection to the Postgresql database. This should be used in every transaction, either at the 
        end, when a transaction has been completed, or in any exceptions, which will implicitly call a rollback function.
        """
        self.connection.close()

    
    def _commit(self) -> None:
        """
        Finalise a transaction, committing the change to the DB. 
        """
        self.connection.commit()


    def _create_identifier(self
                           ,schema: str
                           ,table_name: str):
        
        identifier = sql.SQL('{}.{}').format(
                        sql.Identifier(schema),
                        sql.Identifier(table_name)
                    )
        
        return identifier

    # Metadata Functions
    def get_schema(self, 
                   table_name: str) -> str:
        """
        Accesses metadata, finding the scema of a given table. Useful helper for context in projects,
        and ensuring that projects are using the same schemas.
        """

        self._connect()

        try: 
            with self.connection.cursor() as curr:
                curr.execute("""
                    SELECT table_catalog
                            ,table_schema
                            ,table_name
                    
                    FROM
                        information_schema.tables
                            
                    WHERE 
                        table_name = %(table_name)s;"""
                    
                    ,{'table_name': table_name})

                res = curr.fetchall()[1]

            return res
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()


    def ensure_schema(table_name: str,
                      df: pd.DataFrame) -> str:
        pass


    def table_exists(self 
                     ,table_name: str) -> bool:
        """
        Confirm whether or not a table exists already, to use as a check before writing to or
        trying to load tables, rather than getting an error. This finds tables regardless of
        schema. This should also not show the postgres catalog.

        Args:
            - table_name (str): Name of the table being searched for in the data_science DB

        Returns:
            - (bool) True if exists, false otherwise
        """

        self._connect()

        try: 
            with self.connection.cursor() as curr:
                curr.execute("""
                    SELECT 
                        table_schema
                        ,table_name
                    
                    FROM
                        information_schema.tables
                            
                    WHERE 
                        table_name = %(table_name)s
                        AND table_catalog != 'postgres';"""
                    
                    ,{'table_name': table_name})

                res = curr.fetchone()

            return True if res is not None else False
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()
    

    # Accessing functions 
    def load_table(self
                   ,schema: str
                   ,table_name: str) -> pd.DataFrame:
        
        if not self.table_exists(table_name):
            return("Table does not exist.")

        self._connect()

        table_identifier = self._create_identifier(schema, table_name)

        try: 
            with self.connection.cursor() as curr:
                curr.execute(
                    sql.SQL("""
                    SELECT 
                        *
                    
                    FROM
                        {};""").format(table_identifier)
                    )

                res = curr.fetchall()

            return pd.DataFrame(res)
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()


    def execute_custom_query(self
                        ,query: str) -> pd.DataFrame:
        """
        Funciton which allows me to execute my own queries, should what I need not already be a function,
        including dropping, creating, and selecting from tables.

        Args:
            - query (str): The custom query

        Returns:
            - Result of the query with no transformations
        """
        self._connect()

        try: 
            with self.connection.cursor() as curr:
                curr.execute(sql.SQL(query))
                                        
                return curr.fetchall()
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()


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
    def create_table_from_csv(self 
                              ,schema:str
                              ,table_name: str
                              ,file_path: str) -> None:
        """
        Create a table in the PostgreSQL database using a csv file.

        Args:
            - schema (str): Schema of table being created.
            - table_name (str): Name of table being created.
        """
        if self.table_exists(table_name):
            return "Table already exists!"

        table_identifier = self._create_identifier(schema, table_name)

        dtype_map = {
            'int64': 'BIGINT', 'Int64': 'BIGINT',
            'int32': 'INTEGER', 'Int32': 'INTEGER',
            'float64': 'DOUBLE PRECISION', 'float32': 'REAL',
            'bool': 'BOOLEAN', 'boolean': 'BOOLEAN',
            'object': 'TEXT', 'string': 'TEXT',
            'datetime64[ns]': 'TIMESTAMP', 'category': 'TEXT',
        }

        sample = pd.read_csv(file_path, nrows=1_000)
        columns = ', '.join(
            f'"{col}" {dtype_map.get(str(dtype), "TEXT")}'
            for col, dtype in sample.dtypes.items()
        )

        self._connect()
        try:
            with self.connection.cursor() as curr:

                curr.execute(
                    sql.SQL('CREATE TABLE {} ({});').format(
                        table_identifier,
                        sql.SQL(columns)
                    )
                )

                with open(file_path, 'r', encoding='utf-8') as f:
                    curr.copy_expert(
                        sql.SQL("COPY {} FROM STDIN WITH CSV HEADER DELIMITER ',' QUOTE '\"'")
                        .format(table_identifier)
                        .as_string(self.connection),
                        f
                    )

                self._commit()

                print("SUCCESS: Table created and copied.")

        except (Exception, p2.DatabaseError) as e:
            print(e)
        finally:
            self._close()


    def delete_table(self
                     ,schema: str
                     ,table_name: str) -> None:
        """
        Delete a table from database, requires schema and table name, to ensure deletion of the
        correct table.

        Args:
            - schema (str): Schema of the table to be deleted
            - table_name (str): Name of table to be deleted
        """
        
        if not self.table_exists(table_name):
            return "Table does not exist..."
        
        self._connect()

        table_identifier = self._create_identifier(schema, table_name)

        try: 
            with self.connection.cursor() as curr:
                curr.execute(
                    sql.SQL("""DROP TABLE IF EXISTS {};""")
                    .format(table_identifier)
                )
                
                self._commit()

                print("SUCCESS: Table deleted.")
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()
