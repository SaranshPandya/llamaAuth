import os
import logging
from psycopg2 import pool, errors
from contextlib import contextmanager
import json
import os


from schemas.packet import PostgresConfig, DatabaseSchema

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

        except errors.UniqueViolation as e:
            logger.exception(f"UNIQUE ERROR by me username already exists: {e}")
        
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
    def register_user(self, username: str, passwordHash: str, email: str, age: int):
        try:
            with self.get_db_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(self.queries['registerUsers'], (username, email, passwordHash, age,))
                    id = cur.fetchone()
                    return id
        
        except errors.UniqueViolation as e:
            logger.exception(f"Username: {username} already exists.") 
        
        except Exception as e:
            logger.exception(f"Error in database: {e}")
            raise RuntimeError(e)
        
    def authenticate_user(self, username: str = None, email: str = None):
        try:
            if username:
                auth_key = username
            
            elif email:
                auth_key = email
            
            else:
                raise ValueError("Neither username or email provided")
            
            with self.get_db_conn() as conn:
                with conn.cursor() as curr:
                    curr.execute(self.queries["getUsersDetailNameorEmail"], (auth_key, auth_key, ))    

                    rows = curr.fetchone()
                    
                    if not rows:
                        return
                     
                    columns = [desc[0] for desc in curr.description]
                    
                    # Since this will only give one row, list in output is not needed.
                    # Optimize later. 
                    return [
                        DatabaseSchema(**dict(zip(columns, rows))) 
                    ]
                    
        except Exception as e:
            logger.exception(f"Error occured while fetching user details for authentication.")
            raise RuntimeError(e)

    # Add generated api key to user's entry
    def update_api_key(self, api_key_hash: str, id: int):
        try:
            with self.get_db_conn() as conn:
                with conn.cursor() as curr:
                    curr.execute(self.queries["setAPIKey"], (api_key_hash, id,))
                    
                    rows = curr.fetchone()
                    
                    return rows    
        
        except Exception as e:
            logger.exception(f"Error occured while updating API key in database: {e}")
            raise RuntimeError(e)
        
    def authenticateAPIKey(self, api_key_hash: str):
        try:
            with self.get_db_conn() as conn:
                with conn.cursor() as curr:
                    curr.execute(self.queries['authenticateAPIKey'], (api_key_hash,))
                    
                    rows = curr.fetchone()
                    
                    return rows
        
        except Exception as e:
            logger.exception(f"Error getting response from database for API authentication")


def load_postgres_config() -> PostgresConfig:
    try:
        return PostgresConfig(
            host=os.environ["POSTGRES_HOST"],
            port=int(os.environ.get("POSTGRES_PORT", 5432)),
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            dbname=os.environ["DBNAME"],
            sslmode=os.environ.get("POSTGRES_SSLMODE", "prefer"),
        )
    except Exception as e:
        logger.exception(f"Unable to load postgres configs: {e}")
        raise RuntimeError(f"Unable to load postgres configs: {e}")

# only initialized once.
_db_manager = DatabaseManager(db_config=load_postgres_config())

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

    # user_details = db_manager.register_user(username="Saransh", passwordHash="this is password", email="its.saranshpandya@gmail.com", age=23)
    api_key = db_manager.authenticateAPIKey(api_key_hash="c7b66625cf416bd6a23ca4309220849d23c413e735295b7c25626309c74d724e")
    print(api_key)
