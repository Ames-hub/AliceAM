import psycopg2
import dotenv
import os

dotenv.load_dotenv('secrets.env')
db_conn_details = {
    'host': str(os.getenv('DB_HOST')),
    'port': int(os.getenv('DB_PORT')),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
}

class reputation:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def get(self) -> int:
        raise NotImplementedError

    def set(self, amount: int) -> None:
        raise NotImplementedError

    def subtract(self, amount: int) -> None:
        raise NotImplementedError

    def add(self, amount: int) -> None:
        raise NotImplementedError

class postgre:
    def __init__(self, user_id:int=None) -> None:
        conn: psycopg2.extensions.connection = psycopg2.connect(**db_conn_details)
        cur = conn.cursor()

        self.conn = conn
        self.cur = cur

        if user_id is not None:
            self.reputation = reputation(user_id)

    def query(self, query: str) -> list:
        '''
        Executes a query and returns the result.
        uses fetchall() to return all rows.
        '''
        self.cur.execute(query)
        return self.cur.fetchall()

    def __del__(self) -> None:
        self.conn.close()
        self.cur.close()