import os
from psycopg2 import pool
import sys
sys.path.append("/home/saransh/gitprojects/inferproject/llamaAuth")
from packets.packet import PostgresConfig, DatabaseSchema
from contextlib import contextmanager
import logging

from dotenv import load_dotenv
load_dotenv()

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
        query = "SELECT * FROM ollama_users WHERE username = %s;"

        with self.get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (username,))
                return cur.fetchall()
    
    def get_user_details(self, username) -> list[DatabaseSchema]:
        query = """
            SELECT id, username, password, api_key, status, created_at, updated_at
            FROM ollama_users
            WHERE username = %s;
        """

        with self.get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (username,))
                rows = cur.fetchall()

                columns = [desc[0] for desc in cur.description]

                return [
                    DatabaseSchema(**dict(zip(columns, row)))
                    for row in rows
                ]
                

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

    user_details = db_manager.get_user_details(username="alice")
    print(user_details)
