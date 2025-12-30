import os
import logging
from psycopg2 import pool
from contextlib import contextmanager
import json
import os
# TODO: REMOVE LATER
import sys
sys.path.append("/Users/saranshpandya/gitprojects/inferproject/llamaAuth/")
from packets.packet import PostgresConfig, DatabaseSchema

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_config: PostgresConfig):
        self.db_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dbname=db_config.dbname,
            user=db_config.user,
            password=db_config.password,
            host=db_config.host,
            port=db_config.port
        )
        
        with open(os.getenv("QUERY_PATH")) as file:
            self.queries = json.load(file)
    
    @contextmanager
    def get_db_conn(self):
        conn = self.db_pool.getconn()
        try:
            logging.debug("yielding connection...")
            yield conn
            conn.commit()
        
        except Exception as e:
            logger.exception(f"Error in database connection: {e}")
            conn.rollback()
            raise
        
        finally:
            logging.debug("Returning connection back to the pool")
            self.db_pool.putconn(conn)

    
    def get_user(self, username):
        try:
            with self.get_db_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(self.queries['getUserDetails'], (username,))
                    return cur.fetchall()
        
        except Exception as e:
            logger.exception(f"Error with database: {e}")
            raise RuntimeError(e)
        
    def get_user_details(self, username) -> list[DatabaseSchema]:
        try:
            with self.get_db_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(self.queries['getUserDetails'], (username,))
                    rows = cur.fetchall()

                    columns = [desc[0] for desc in cur.description]

                    return [
                        DatabaseSchema(**dict(zip(columns, row)))
                        for row in rows
                    ]

        except Exception as e:
            logger.exception(f"Error in database: {e}")
            raise RuntimeError(e)
        
    # Get all users
    def get_all_users(self) -> list[DatabaseSchema]:
        try:
            with self.get_db_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(self.queries['getAllUsers'])
                    rows = cur.fetchall()

                    columns = [desc[0] for desc in cur.description]

                    return [
                        DatabaseSchema(**dict(zip(columns, row)))
                        for row in rows
                    ]

        except Exception as e:
            logger.exception(f"Error in database: {e}")
            raise RuntimeError(e)
        
        
    # TODO: Create a database entry for new user. 
    def register_user(self, username: str, passwordHash: str):
        try:
            pass
        
        except Exception as e:
            logger.exception(f"Error in database: {e}")
            raise RuntimeError(e)    


if __name__ == "__main__":
    host = os.getenv("POSTGRES_HOST", "")
    port = int(os.getenv("POSTGRES_PORT", 5432))
    password = os.getenv("POSTGRES_PASSWORD", "")
    user = os.getenv("POSTGRES_USER", "")
    dbname = os.getenv("DBNAME", "")


    db_config = PostgresConfig(
        host = host,
        port = port,
        password = password,
        user = user,
        dbname = dbname
    )

    db_manager = DatabaseManager(db_config=db_config)

    user_details = db_manager.get_all_users()
    print(user_details)
