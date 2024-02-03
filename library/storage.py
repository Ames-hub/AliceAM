import psycopg2
import dotenv
import os
import random
from .jmod import jmod
from .data_tables import data_tables
from library.variables import logging

dotenv.load_dotenv('secrets.env')
db_conn_details = {
    'host': str(os.getenv('DB_HOST')),
    'port': int(os.getenv('DB_PORT')),
    'database': os.getenv('DB_DATABASE'),
    'user': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
}

def do_use_postgre():
    return jmod.getvalue(
        json_dir='memory/settings.json',
        key='use_postgre',
        dt=data_tables.SETTINGS_DT,
    )

class connmanager:
    def __init__(self) -> None:
        if do_use_postgre():
            self.latest_conn = self.renew()
        else:
            self.latest_conn = None

    def fetch(self) -> psycopg2.extensions.connection:
        '''
        Fetch the latest Connection variable to execute queries to
        '''
        if self.latest_conn is None:
            self.renew()

        return self.latest_conn

    def renew(self):
        '''
        Renew the latest Connection variable to execute queries to.
        (Replaces old latest.conn)
        '''
        try:
            self.latest_conn: psycopg2.extensions.connection = psycopg2.connect(**db_conn_details)
            # Don't have it return True here, no clue why but that makes fetch return True instead of the connection
        except psycopg2.OperationalError as err:
            print("Could not connect to database. I suggest you check your credentials and ensure the Schema/Database exists with a valid host and port.")
            logging.error("Couldn't connect to DB. Check your credentials and ensure the Schema/Database exists with a valid host and port.")
            return False

connman = connmanager()

class down_queue:
    '''
    A queue for storing queries that couldn't be executed due to a connection error.
    '''
    def __init__(self) -> None:
        self.queue = []

    def add(self, query: str, args: tuple) -> None:
        '''
        Adds a query to the queue.
        '''
        Query_ID = random.randint(1,99999999999999999999)
        self.queue.append((query, args, Query_ID))

    def remove(self, Query_ID) -> None:
        '''
        Removes a query from the queue.
        '''
        for query, args, ID in self.queue:
            if ID == Query_ID:
                # Note, this is not calling itself, it's calling the method of the type class 'list'
                self.queue.remove((query, args, ID))

    def run(self) -> None:
        '''
        Executes all queries in the queue.
        Intended to be ran as a task
        '''
        for query, args, ID in self.queue:
            success = postgre.query(query, args, do_commit=True, return_success_only=True)
            if success:
                self.remove(ID)

downqueue = down_queue()

class db_tables:
    def ensure_exists():
        conn = None
        # Fetch a database connection
        conn = connman.fetch()
        cur = conn.cursor()

        # Using this dict, it formats the SQL query to create the tables if they don't exist
        table_dict = {
            # Table name
            'guilds': {
                # Column name: Column properties
                'guild_id': 'BIGINT NOT NULL PRIMARY KEY',
                'antiswear_enabled': 'BOOLEAN NOT NULL DEFAULT FALSE',
                'antislur_enabled': 'BOOLEAN NOT NULL DEFAULT TRUE',
                'antispam_enabled': 'BOOLEAN NOT NULL DEFAULT FALSE',
            },
            'users': {
                'user_id': 'BIGINT NOT NULL PRIMARY KEY',
                'rep_slurs': 'FLOAT NOT NULL DEFAULT 0.0',
                'rep_swearing': 'FLOAT NOT NULL DEFAULT 0.0',
            },
        }

        for table_name, columns in table_dict.items():
            # Check if the table exists
            cur.execute('''
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = %s
                );
            ''', (table_name,))
            table_exist = cur.fetchone()[0]

            # If the table exists, check and update columns
            if table_exist:
                for column_name, column_properties in columns.items():
                    # Check if the column exists
                    cur.execute('''
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_name = %s AND column_name = %s
                        );
                    ''', (table_name, column_name))
                    column_exist = cur.fetchone()[0]

                    # If the column doesn't exist, add it
                    if not column_exist:
                        cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_properties};')

            # If the table doesn't exist, create it with columns
            else:
                columns_str = ', '.join([f'{column_name} {column_properties}' for column_name, column_properties in columns.items()])
                cur.execute(f'CREATE TABLE {table_name} ({columns_str});')

        # Commit the changes
        conn.commit()

    def ensure_guild(guild_id):
        '''
        Ensures the guild is in the database's guilds table.
        '''
        conn = connman.fetch()
        cur = conn.cursor()

        # Check if the guild exists
        cur.execute('''
            SELECT EXISTS (
                SELECT 1
                FROM guilds
                WHERE guild_id = %s
            );
        ''', (guild_id,))
        guild_exist = cur.fetchone()[0]

        # If the guild doesn't exist, add it
        if not guild_exist:
            cur.execute('INSERT INTO guilds (guild_id) VALUES (%s);', (guild_id,))
            conn.commit()

class postgre:
    def query(query: str, args: tuple, do_commit:bool=True, return_success_only=False) -> list:
        '''
        Executes a query and returns the result.
        uses fetchall() to return all rows.

        If data is empty, returns True.
        If the query was unsuccessful, returns False.
        '''
        conn: psycopg2.extensions.connection = connman.fetch()
        cur = conn.cursor()

        if return_success_only:
            try:
                cur.execute(query, args)
                if do_commit:
                    conn.commit()
                return True
            except:
                return False
        else:
            cur.execute(query, args)

        if do_commit:
            conn.commit()
        try:
            data = cur.fetchall()
            # print(f"\n{query}\n{data}\n") # Debug code for checking queries
            return data
        except psycopg2.ProgrammingError:
            return []
        except psycopg2.OperationalError as err:
            logging.error(f"Couldn't connect to DB. Check your credentials and ensure the Schema/Database exists with a valid host and port. {err}")
            if 'connect' in str(err): # Filters out the error message to see if it's a connection error
                # Add the query to the queue to be executed later when the connection is re-established
                downqueue.add(query, args)
                
                # Renegotiate the connection
                connman.renew()
    class guild:
        def __init__(self, guild_id: int) -> None:
            self.guild_id = guild_id
            # Makes sure the guild is in the database
            db_tables.ensure_guild(guild_id)
            
        def get_antiswear_enabled(self) -> bool:
            '''
            Returns the value of the antiswear_enabled column in the guilds table.
            '''
            query = f"SELECT antiswear_enabled FROM guilds WHERE guild_id=%s"
            result = postgre.query(query, args=(self.guild_id,), do_commit=False)
            return result[0][0]
        def set_antiswear_enabled(self, value: bool) -> None:
            '''
            Sets the value of the antiswear_enabled column in the guilds table.
            '''
            query = f"UPDATE guilds SET antiswear_enabled=%s WHERE guild_id=%s"
            return postgre.query(query, args=(value, self.guild_id), return_success_only=True)

        def get_antislur_enabled(self) -> bool:
            '''
            Returns the value of the antislur_enabled column in the guilds table.
            '''
            query = f"SELECT antislur_enabled FROM guilds WHERE guild_id=%s"
            result = postgre.query(query, args=(self.guild_id,), do_commit=False)
            return result[0][0]
        def set_antislur_enabled(self, value: bool) -> None:
            '''
            Sets the value of the antislur_enabled column in the guilds table.
            '''
            query = f"UPDATE guilds SET antislur_enabled=%s WHERE guild_id=%s"
            return postgre.query(query, args=(value, self.guild_id), return_success_only=True)

        def get_antispam_enabled(self) -> bool:
            '''
            Returns the value of the antispam_enabled column in the guilds table.
            '''
            query = f"SELECT antispam_enabled FROM guilds WHERE guild_id=%s"
            result = postgre.query(query, args=(self.guild_id,), do_commit=False)
            return result[0][0]
        def set_antispam_enabled(self, value: bool) -> None:
            '''
            Sets the value of the antispam_enabled column in the guilds table.
            '''
            query = f"UPDATE guilds SET antispam_enabled=%s WHERE guild_id=%s"
            return postgre.query(query, args=(value, self.guild_id), return_success_only=True)

    class user_reputation:
        def __init__(self, user_id: int) -> None:
            self.user_id = user_id

        def get_slurs(self) -> float:
            '''
            Returns the value of the rep_slurs column in the users table.
            '''
            query = f"SELECT rep_slurs FROM users WHERE user_id=%s"
            result = postgre.query(query, args=(self.user_id,), do_commit=False)
            return result[0][0]
        
        def set_slurs(self, value: float) -> None:
            '''
            Sets the value of the rep_slurs column in the users table.
            '''
            query = f"UPDATE users SET rep_slurs=%s WHERE user_id=%s"
            return postgre.query(query, args=(value, self.user_id))

        def addTo_slurs(self, value: float) -> None:
            '''
            Adds to the value of the rep_slurs column in the users table.
            '''
            query = f"SELECT rep_slurs FROM users WHERE user_id=%s"
            result = postgre.query(query, args=(self.user_id,))
            amount = result[0][0]
            query = f"UPDATE users SET rep_slurs=%s WHERE user_id=%s"
            return postgre.query(query, args=(amount + value, self.user_id))

        def subtractFrom_slurs(self, value: float) -> None:
            '''
            Subtracts from the value of the rep_slurs column in the users table.
            '''
            query = f"SELECT rep_slurs FROM users WHERE user_id=%s"
            result = postgre.query(query, args=(self.user_id,))
            amount = result[0][0]
            query = f"UPDATE users SET rep_slurs=%s WHERE user_id=%s"
            return postgre.query(query, args=(amount - value, self.user_id))

        def get_swearing(self) -> float:
            '''
            Returns the value of the rep_swearing column in the users table.
            '''
            query = f"SELECT rep_swearing FROM users WHERE user_id=%s"
            result = postgre.query(query, args=(self.user_id,), do_commit=False)
            return result[0][0]
        
        def set_swearing(self, value: float) -> None:
            '''
            Sets the value of the rep_swearing column in the users table.
            '''
            query = f"UPDATE users SET rep_swearing=%s WHERE user_id=%s"
            return postgre.query(query, args=(value, self.user_id))

        def addTo_swearing(self, value: float) -> None:
            '''
            Adds to the value of the rep_swearing column in the users table.
            '''
            query = f"SELECT rep_swearing FROM users WHERE user_id=%s"
            result = postgre.query(query, args=(self.user_id,))
            amount = result[0][0]
            query = f"UPDATE users SET rep_swearing=%s WHERE user_id=%s"
            return postgre.query(query, args=(amount + value, self.user_id))

        def subtractFrom_swearing(self, value: float) -> None:
            '''
            Subtracts from the value of the rep_swearing column in the users table.
            '''
            query = f"SELECT rep_swearing FROM users WHERE user_id=%s"
            result = postgre.query(query, args=(self.user_id,))
            amount = result[0][0]
            query = f"UPDATE users SET rep_swearing=%s WHERE user_id=%s"
            return postgre.query(query, args=(amount - value, self.user_id))

class json_storage:
    def get_guild_dir(guid, make_dirs:bool=True):
        path = os.path.abspath(f'memory/guilds/{guid}/')
        if make_dirs:
            os.makedirs(path, exist_ok=True)
        return path
    
    def get_users_dir(uuid, make_dirs:bool=True):
        path = os.path.abspath(f'memory/uuid/{uuid}/')
        if make_dirs:
            os.makedirs(path, exist_ok=True)
        return path

    class guild:
        def __init__(self, guild_id) -> None:
            self.guild_id = guild_id
        
        def get_antiswear_enabled(self):
            return jmod.getvalue(
                key='antiswear.enabled',
                dt=data_tables.GUILD_DT,
                json_dir=json_storage.get_guild_dir(self.guild_id),
            )
        def set_antiswear_enabled(self, value: bool):
            jmod.setvalue(
                key='antiswear.enabled',
                dt=data_tables.GUILD_DT,
                value=value,
                json_dir=json_storage.get_guild_dir(self.guild_id),
            )
            return True

        def get_antislur_enabled(self):
            return jmod.getvalue(
                key='antislur.enabled',
                dt=data_tables.GUILD_DT,
                json_dir=json_storage.get_guild_dir(self.guild_id)
            )
        def set_antislur_enabled(self, value: bool):
            jmod.setvalue(
                key='antislur.enabled',
                dt=data_tables.GUILD_DT,
                value=value,
                json_dir=json_storage.get_guild_dir(self.guild_id),
            )
            return True

        def get_antispam_enabled(self):
            return jmod.getvalue(
                key='antispam.enabled',
                dt=data_tables.GUILD_DT,
                json_dir=json_storage.get_guild_dir(self.guild_id),
            )
        def set_antispam_enabled(self, value: bool):
            jmod.setvalue(
                key='antispam.enabled',
                dt=data_tables.GUILD_DT,
                value=value,
                json_dir=json_storage.get_guild_dir(self.guild_id),
            )
            return True

    class user_reputation:
        def __init__(self, user_id:int) -> None:
            self.user_id = user_id

        def get_slurs(self) -> float:
            return jmod.getvalue(
                key='reputation.slurs',
                dt=data_tables.USER_DT,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
        def set_slurs(self, value: float) -> None:
            jmod.setvalue(
                key='reputation.slurs',
                dt=data_tables.USER_DT,
                value=value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
        def addTo_slurs(self, value: float) -> None:
            amount = jmod.getvalue(
                key='reputation.slurs',
                dt=data_tables.USER_DT,
                value=value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
            jmod.setvalue(
                key='reputation.slurs',
                dt=data_tables.USER_DT,
                value=amount + value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
         
        def subtractFrom_slurs(self, value: float) -> None:
            amount = jmod.getvalue(
                key='reputation.slurs',
                dt=data_tables.USER_DT,
                value=value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
            jmod.setvalue(
                key='reputation.slurs',
                dt=data_tables.USER_DT,
                value=amount - value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )

        def get_swearing(self) -> float:
            return jmod.getvalue(
                key='reputation.swearing',
                dt=data_tables.USER_DT,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
        def set_swearing(self, value: float) -> None:
            jmod.setvalue(
                key='reputation.swearing',
                dt=data_tables.USER_DT,
                value=value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
        def addTo_swearing(self, value: float) -> None:
            amount = jmod.getvalue(
                key='reputation.swearing',
                dt=data_tables.USER_DT,
                value=value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
            jmod.setvalue(
                key='reputation.swearing',
                dt=data_tables.USER_DT,
                value=amount + value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )

        def subtractFrom_swearing(self, value: float) -> None:
            amount = jmod.getvalue(
                key='reputation.swearing',
                dt=data_tables.USER_DT,
                value=value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )
            jmod.setvalue(
                key='reputation.swearing',
                dt=data_tables.USER_DT,
                value=amount - value,
                json_dir=json_storage.get_users_dir(self.user_id),
            )

class memory:
    '''
    A class for storing data in permanent memory.
    Auto-switches between json_storage and postgre depending on the value of use_postgre in data_tables.SETTINGS_DT 
    '''        
    class guild:
        def __init__(self, guild_id) -> None:
            self.guild_id = guild_id
            if do_use_postgre():
                self.mem_method = postgre.guild(guild_id)
            else:
                self.mem_method = json_storage.guild(guild_id)

        def get_antiswear_enabled(self):
            return self.mem_method.get_antiswear_enabled()
        def set_antiswear_enabled(self, value: bool):
            return self.mem_method.set_antiswear_enabled(value)
        
        def get_antislur_enabled(self):
            return self.mem_method.get_antislur_enabled()
        def set_antislur_enabled(self, value: bool):
            return self.mem_method.set_antislur_enabled(value)

        def get_antispam_enabled(self):
            return self.mem_method.get_antispam_enabled()
        def set_antispam_enabled(self, value: bool):
            return self.mem_method.set_antispam_enabled(value)

    class user_reputation:
        def __init__(self, user_id) -> None:
            self.user_id = user_id
            if do_use_postgre():
                self.mem_method = postgre.user_reputation(user_id)
            else:
                self.mem_method = json_storage.user_reputation(user_id)

        def get_slurs(self) -> float:
            return self.mem_method.get_slurs()
        def set_slurs(self, value: float) -> None:
            self.mem_method.set_slurs(value)
        def addTo_slurs(self, value: float) -> None:
            self.mem_method.addTo_slurs(value)
        def subtractFrom_slurs(self, value: float) -> None:
            self.mem_method.subtractFrom_slurs(value)

        def get_swearing(self) -> float:
            return self.mem_method.get_swearing()
        def set_swearing(self, value: float) -> None:
            self.mem_method.set_swearing(value)
        def addTo_swearing(self, value: float) -> None:
            self.mem_method.addTo_swearing(value)
        def subtractFrom_swearing(self, value: float) -> None:
            self.mem_method.subtractFrom_swearing(value)