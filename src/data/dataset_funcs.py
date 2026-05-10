import pandas as pd
import psycopg2 as p2
from psycopg2 import sql
import os
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

    def __init__(self):
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
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST")
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


    def _rollback(self) -> None:
        """
        Roll back a transaction. This is to be used in instances where the connection will not be closed when there is an error, for example
        during batch uploads or inserts, where each batch would be committed, and any failed batches will call the rollback function, and 
        print a message to the user, saying that the batch had resulted in an error, and been rolled back.
        """
        self.connection.rollback()


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

                res = curr.fetchone()[1]

            return res
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()


    def ensure_schema(table_name: str,
                      df: pd.DataFrame) -> str:
        pass


    def table_exists(self, 
                     table_name: str) -> str:
        """
        Confirm whether or not a table exists already, to use as a check before writing to or
        trying to load tables, rather than getting an error. This finds tables regardless of
        schema. This should also not show the postgres catalog.

        Args:
            - table_name (str): Name of the table being searched for in the data_science DB

        Returns:
            - Table name, and the schema of the table being searched for, if exists.
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

                res = curr.fetchall()

            return res
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()
    

    # Accessing functions 
    def load_table(self
                   ,schema: str
                   ,table_name: str) -> pd.DataFrame:
        self._connect()

        try: 
            with self.connection.cursor() as curr:
                curr.execute(
                    sql.SQL("""
                    SELECT 
                        *
                    
                    FROM
                        {}.{};""").format(
                            sql.Identifier(schema),
                            sql.Identifier(table_name)
                        )
                    )

                res = curr.fetchall()

            return pd.DataFrame(res)
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()


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
    def create_table(self
                     ,schema: str
                     ,table_name: str) -> None:
        
        self._connect()

        try: 
            with self.connection.cursor() as curr:
                # If the table exists in a different schema, then warn user but create table anyway. This wont
                # work, tables have to contain something. The function needs to create a table based on a df.
                if self.table_exists(table_name) is None:
                    curr.execute("""
                        CREATE TABLE %(schema)s.%(table_name)s;"""
                        
                        ,{"schema": schema,
                        'table_name': table_name})

                    res = curr.fetchone()
                    
                    return True if res is not None else False
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()


    def delete_table(self
                     ,schema: str
                     ,table_name: str) -> None:
        
        exists = self.table_exists(table_name)
        self._connect()

        try: 
            with self.connection.cursor() as curr:
                # If the table exists in a different schema, then warn user but create table anyway
                if exists:
                    curr.execute(
                        sql.SQL("""
                        DROP TABLE IF EXISTS {}.{};
                                """).format(
                            sql.Identifier(schema),
                            sql.Identifier(table_name)
                                )
                    )
                    
                    self._commit()
        
        except (Exception, p2.DatabaseError) as e:
            print(e)

        finally:
            self._close()
