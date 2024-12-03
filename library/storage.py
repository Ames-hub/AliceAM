from library.encrpytion import encryption
from library.variables import logging
from datetime import datetime
from io import BytesIO
from PIL import Image
import subprocess
import imagehash
import psycopg2
import secrets
import inspect
import json
import time
import os

keys = encryption()

# The port the PostgreSQL container will run on by default when created.
postgre_port = 9432
settings_path = 'settings.json'
DEBUG = os.environ.get('DEBUG_ALICE') == 'True'
key_seperator = '.'
connhint = psycopg2.extensions.connection

class dt:
    """
    A class of dictionaries to be put as templates in Json files for the bot to use.
    """
    # For localsetting.json
    SETTINGS = {
        'token': None,
        'use_postgre': False,
        'first_start': True,
        'prefix': "//",
        'postgre': {
            'host': None,
            'port': None,
            'database': None,
            'username': None,
            'password': None,
        },
    }


# noinspection DuplicatedCode,PyTypeChecker,PyShadowingNames
class var:
    @staticmethod
    def set(key, value, file=settings_path, dt_default=dt.SETTINGS) -> bool:
        """
        Sets the value of a key in the memory file.

        :param key: The key to set the value of.
        :param value: The value to set the key to.
        :param file: The file to set the key in.
        :param dt_default: The default dictionary to fill a json file with if the file does not exist.
        :return:
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(f'file \'{file}\' was set by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is False:
            os.makedirs(file_dir, exist_ok=True)
            with open(file, 'w+') as f:
                json.dump(dt_default, f, indent=4, separators=(',', ':'))

        with open(file, 'r+') as f:
            data = json.load(f)

        temp = data
        for k in keys[:-1]:
            if k not in temp:
                temp[k] = {}
            temp = temp[k]

        temp[keys[-1]] = value

        with open(file, 'w+') as f:
            json.dump(data, f, indent=4)

        return True

    @staticmethod
    def get(key, default=None, dt_default=dt.SETTINGS, file=settings_path) -> any:
        """
        Gets the value of a key in the memory file.

        :param key: The key to get the value of.
        :param default: The default value to return if the key does not exist.
        :param dt_default: The default dictionary to fill a json file with if the file does not exist.
        :param file: The file to get the key from.
        Set to None if you want to raise an error if the file does not exist.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            caller = f"{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}"
            logging.info(f'file \'{file}\' was retrieved from by {caller}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is True:
            with open(file, 'r+') as f:
                data = dict(json.load(f))
        else:
            if dt_default is not None:
                os.makedirs(file_dir, exist_ok=True)
                with open(file, 'w+') as f:
                    json.dump(dt_default, f, indent=4, separators=(',', ':'))
            else:
                raise FileNotFoundError(f"file '{file}' does not exist.")

            with open(file, 'r+') as f:
                data = dict(json.load(f))

        temp = data
        try:
            for k in keys[:-1]:
                if k not in temp:
                    return default
                temp = temp[k]

            return temp[keys[-1]]
        except KeyError as err:
            logging.error(f"key '{key}' not found in file '{file}'.", err)
            raise KeyError(f"key '{key}' not found in file '{file}'.")

    @staticmethod
    def delete(key, file=settings_path, default=dt.SETTINGS):
        """
        Delete a key.

        :param key: The key to delete.
        :param file: The file to delete the key from.
        :param default: The default dictionary to fill a json file with if the file does not exist.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            caller = f"{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}"
            logging.info(f'file \'{file}\' was had a key deleted by {caller}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is True:
            with open(file, 'r+') as f:
                data = dict(json.load(f))
        else:
            if default is not None:
                os.makedirs(file_dir, exist_ok=True)
                with open(file, 'w+') as f:
                    json.dump(default, f, indent=4, separators=(',', ':'))
            else:
                raise FileNotFoundError(f"file '{file}' does not exist.")

            with open(file, 'r+') as f:
                data = dict(json.load(f))

        temp = data
        for k in keys[:-1]:
            if k not in temp:
                return False
            temp = temp[k]

        if keys[-1] in temp:
            del temp[keys[-1]]
            with open(file, 'w+') as f:
                json.dump(data, f, indent=4)
            return True
        else:
            return False

    @staticmethod
    def load_all(file: str = settings_path, dt_default={}) -> dict:
        """
        Load all the keys in a file. Returns a dictionary with all the keys.
        :param file: The file to load all the keys from.
        :param dt_default:
        :return:
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(
                f'file \'{file}\' was fully loaded by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        os.makedirs(os.path.dirname(file), exist_ok=True)
        if not os.path.exists(file):
            with open(file, 'w+') as f:
                json.dump(dt_default, f, indent=4, separators=(',', ':'))

        with open(file, 'r+') as f:
            data = dict(json.load(f))

        return data

    @staticmethod
    def fill_json(file: str = settings_path, data=dt.SETTINGS):
        """
        Fill a json file with a dictionary.
        :param file: The file to fill with data.
        :param data: The data to fill the file with.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(
                f'file \'{file}\' was filled with data by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        if "/" in file or "\\" in file:
            os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w+') as f:
            json.dump(data, f, indent=4, separators=(',', ':'))

        return True

class PostgreSQL:
    @staticmethod
    def get_details() -> dict:
        """
        Returns the details of the PostgreSQL database.
        """
        return {
            'host': var.get('db.host'),
            'port': var.get('db.port'),
            'database': var.get('db.database'),
            'user': var.get('db.username'),
            'password': keys.decrypt((var.get('db.password'))),
        }

    @staticmethod
    def start_db() -> bool:
        """
        Starts the PostgreSQL container.
        :return: True if the container was started, False if it was not started.
        """
        try:
            subprocess.run(
                ["docker", "start", "AliceAM-Postgre"],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            logging.error('Could not start the container.', exc_info=True)
            return False

    @staticmethod
    def check_db_container() -> bool | int:
        """
        Checks if the PostgreSQL container exists and is running.
        :return: True if the container is running, False if it is not running, and -1 if it does not exist.
        """
        # Checks if the PostgreSQL container exists and is running
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format='{{json .State.Status}}'", "AliceAM-Postgre"],
                capture_output=True, text=True
            )
        except subprocess.CalledProcessError:
            # Container does not exist
            return -1

        if result.stdout == "'running'\n":
            return True
        elif result.stderr != "Error: No such object: AliceAM-Postgre\n":
            return -1
        else:
            return False

    @staticmethod
    def make_db_container() -> bool | None:
        """
        Makes a PostgreSQL container that AliceAM can use.
        :return: True if the container was created, False if it was not created. None if Docker is not installed.
        """
        # Uses docker to make a PostgreSQL container
        postgres_password = secrets.token_urlsafe(32)

        # Run the Docker container
        try:
            subprocess.run(
                [
                    "docker", "run", "--name", "AliceAM-Postgre",
                    "-e", f"POSTGRES_PASSWORD={postgres_password}",
                    "-p", f"{postgre_port}:5432",
                    '--restart', 'unless-stopped',
                    "-d", "postgres"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error(f'Could not create the container. {err}', )
            return False
        except FileNotFoundError:
            logging.error('Docker is not installed.')
            return None

        print("Waiting for the DB to start...")
        time.sleep(3)
        # Create the PostgreSQL schema/database
        PostgreSQL.make_alice_schema()

        # Set the password in the secrets file
        PostgreSQL.save_details({
            'host': '127.0.0.1',
            'port': postgre_port,
            'username': 'postgres',
            'password': postgres_password,
            'database': 'aliceam'
        })

        time.sleep(2)

        PostgreSQL().modernize()

        return True

    @staticmethod
    def make_alice_schema():
        # Create the PostgreSQL schema/database
        try:
            subprocess.run(
                [
                    "docker", "exec", "-i", "AliceAM-Postgre",
                    "psql", "-U", "postgres",
                    "-c", f"CREATE DATABASE aliceam;"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error('Could not create the database on PostgreSQL.', err)
            return False

    @staticmethod
    def save_details(details: dict):
        """
        Saves the details of the PostgreSQL database to the secrets file.
        :param details: The details to save.
        """
        var.set(file='settings.json', key='db.host', value=details['host'])
        var.set(file='settings.json', key='db.port', value=details['port'])
        var.set(file='settings.json', key='db.username', value=details['username'])
        var.set(file='settings.json', key='db.password', value=keys.encrypt((details['password'])))
        var.set(file='settings.json', key='db.database', value=details['database'])

    @staticmethod
    def get_connection() -> psycopg2.extensions.connection:
        try:
            return psycopg2.connect(**PostgreSQL.get_details())
        except psycopg2.OperationalError as err:
            # Try to start up the docker container for the database
            if not PostgreSQL.start_db():

                msg = 'Could not reach the database, and when I tried to start the PostgreSQL container, It failed.'
                logging.error(msg, exc_info=True)
                print(msg)

                print("Now attempting to pair with a newly-created local database as a fallback.")
                success = PostgreSQL.make_db_container()
                # Wait a bit for the database to start up
                time.sleep(2)
                if not success:
                    msg = 'Could not pair with a local database.'
                    logging.error(msg)
                    print(msg)
                    exit(1)
                else:
                    print("Successfully paired with a local database.")
                    return psycopg2.connect(**PostgreSQL.get_details())

            msg = 'The database is starting up. Please wait.'
            print(msg)
            logging.info(msg)

            if 'database "aliceam" does not exist' in str(err):
                # Create the database if it doesn't exist
                PostgreSQL.make_alice_schema()

            # Wait for the database to start up
            time_waited = 0
            while not PostgreSQL.ping_db():
                # If the database does not start up in 10 seconds, raise an error
                if time_waited > 10:
                    logging.error('The database did not start up in time.')
                    raise err
                time_waited += 1
                time.sleep(1)
            return psycopg2.connect(**PostgreSQL.get_details())

    @staticmethod
    def ping_db():
        try:
            conn = psycopg2.connect(**PostgreSQL.get_details())
            conn.close()
            return True
        except psycopg2.OperationalError:
            return False

    @staticmethod
    def modernize():
        # Using this dict, it formats the SQL query to create the tables if they don't exist
        table_dict = {
            # Table name
            'guilds': {
                # Column name: Column properties
                'guild_id': 'BIGINT NOT NULL PRIMARY KEY',
                'antiswear_enabled': 'BOOLEAN NOT NULL DEFAULT FALSE',
                'antislur_enabled': 'BOOLEAN NOT NULL DEFAULT TRUE',
                'antispam_enabled': 'BOOLEAN NOT NULL DEFAULT FALSE',
                'image_scanner_enabled': 'BOOLEAN NOT NULL DEFAULT FALSE',
                'show_censored_substrings': 'BOOLEAN NOT NULL DEFAULT FALSE',
            },
            'guild_word_whitelist': {
                'guild_id': 'BIGINT NOT NULL PRIMARY KEY',
                'word': 'TEXT NOT NULL UNIQUE',
            },
            'guild_log_channels': {
                'guild_id': 'BIGINT NOT NULL PRIMARY KEY',
                'channel_id': 'BIGINT DEFAULT NULL',
                'enabled': 'BOOLEAN NOT NULL DEFAULT FALSE',
            },
            'img_scanner_cases': {
                'case_id': 'SERIAL PRIMARY KEY',
                'guild_id': 'BIGINT NOT NULL',
                'offender_id': 'BIGINT NOT NULL',
                'img_hash': 'TEXT NOT NULL',
                'bytedata': 'BYTEA NOT NULL',
            },
            'img_scanner_exempt_channel': {
                'guild_id': 'BIGINT NOT NULL PRIMARY KEY',
                'channel_id': 'BIGINT DEFAULT NULL UNIQUE',
            },
            'users': {
                'user_id': 'BIGINT NOT NULL PRIMARY KEY',
                'rep_slurs': 'FLOAT NOT NULL DEFAULT 0.0',
                'rep_swearing': 'FLOAT NOT NULL DEFAULT 0.0',
                # The below is for the task 'reputation_nuller'. View the file for more data
                # But this is neccesary when accounting for reboots of the bot.
                'nullification_time': 'TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP',
            },
        }

        with PostgreSQL.get_connection() as conn:
            cur = conn.cursor()
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

    def img_scan_history(self, img_hash):
        """
        Returns the result of a past image scan from the database by the image hash and returns a dictionary with byte data and case ID.
        """
        query = "SELECT bytedata, case_id FROM img_scanner_cases WHERE img_hash=%s"
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (img_hash,))
                result = cur.fetchone()
            return {'bytedata': result[0], 'case_id': result[1]} if result else None
        except Exception as err:
            logging.error(f"Could not get image scan history from the database.", err)
            return None

    class db_tables:
        @staticmethod
        def ensure_user(user_id) -> bool:
            """
            Used to make sure a user exists before trying to interact with them in the DB.
            Checks if the user exists, and if they don't, adds them.

            returns True if the user exists, False if they don't

            args:
                user_id: int - The user's discord ID
            """
            conn = PostgreSQL.get_connection()
            cur = conn.cursor()

            # Check if the user exists
            cur.execute('''
                SELECT EXISTS (
                    SELECT 1
                    FROM users
                    WHERE user_id = %s
                );
            ''', (user_id,))
            user_exist = cur.fetchone()[0]

            # If the user doesn't exist, add them
            if not user_exist:
                cur.execute('INSERT INTO users (user_id) VALUES (%s);', (user_id,))
                conn.commit()
                # Return false if they didn't exist
                return False
            else:
                # Return true if they did exist
                return True

        @staticmethod
        def ensure_guild(guild_id):
            """
            Ensures the guild is in the database's guilds table.
            """
            conn = PostgreSQL.get_connection()
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

    @staticmethod
    def list_known_users():
        """
        Returns a list of all known users in the database.
        """
        query = "SELECT user_id FROM users"
        with PostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
        return [user[0] for user in result]

    # noinspection DuplicatedCode
    class guild:
        def __init__(self, guild_id: int) -> None:
            """
            Initializes the guild object.
            This object is used to interact with the guilds table in the database for a specific guild.
            """
            self.guild_id = int(guild_id)
            # Makes sure the guild is in the database
            PostgreSQL.db_tables.ensure_guild(int(guild_id))

        def get_custom_whitelist(self):
            """
            Returns the custom whitelist for the guild.
            """
            query = "SELECT word FROM guild_word_whitelist WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchall()
                return [word[0] for word in result] if result else []
            except Exception as err:
                logging.error(f"Could not get custom whitelist for guild {self.guild_id}.", err)
                return []

        def add_whitelist_word(self, word):
            """
            Adds a word to the whitelist for the guild.
            """
            query = "INSERT INTO guild_word_whitelist (guild_id, word) VALUES (%s, %s)"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id, word))
                    conn.commit()
                return True
            except psycopg2.errors.UniqueViolation:
                return -1
            except Exception as err:
                logging.error(f"Could not add word to the whitelist for guild {self.guild_id}.", err)
                return False
            
        def remove_whitelist_word(self, word):
            """
            Removes a word from the whitelist for the guild.
            """
            query = "DELETE FROM guild_word_whitelist WHERE guild_id=%s AND word=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id, word))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not remove word from the whitelist for guild {self.guild_id}.", err)
                return

        def add_exempt_img_scan_channel(self, channel_id: int) -> bool | int:
            """
            Adds a channel to the exempt list for the image scanner.
            """
            query = "INSERT INTO img_scanner_exempt_channel (guild_id, channel_id) VALUES (%s, %s)"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id, channel_id))
                    conn.commit()
                return True
            except psycopg2.errors.UniqueViolation:
                return -1
            except Exception as err:
                logging.error(f"Could not add channel to the exempt list for image scanner.", err)
                return False

        def remove_exempt_img_scan_channel(self, channel_id: int) -> bool:
            """
            Removes a channel from the exempt list for the image scanner.
            """
            query = "DELETE FROM img_scanner_exempt_channel WHERE guild_id=%s AND channel_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id, channel_id))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not remove channel from the exempt list for image scanner.", err)
                return False

        def get_exempt_img_scan_channels(self) -> list:
            """
            Returns a list of all exempt channels for the image scanner.
            """
            query = "SELECT channel_id FROM img_scanner_exempt_channel WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchall()
                return [channel[0] for channel in result] if result else []
            except Exception as err:
                logging.error(f"Could not get exempt channels for image scanner.", err)
                return []

        def get_image_scanner_enabled(self):
            """
            Returns the value of the image_scanner_enabled column in the guilds table.
            """
            query = f"SELECT image_scanner_enabled FROM guilds WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                return result[0]
            except Exception as err:
                logging.error(f"Could not get image scanner protection for {self.guild_id}.", err)
                return False

        def set_imagescanner_enabled(self, value: bool) -> bool:
            """
            Sets the value of the image_scanner_enabled column in the guilds table.
            """
            query = f"UPDATE guilds SET image_scanner_enabled=%s WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (value, self.guild_id))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not set image scanner protection to {value} for {self.guild_id}.", err)
                return False

        def get_antiswear_enabled(self) -> bool:
            """
            Returns the value of the antiswear_enabled column in the guilds table.
            """
            query = f"SELECT antiswear_enabled FROM guilds WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                    return result[0]
            except Exception as err:
                logging.error(f"Could not get antiswear protection for guid {self.guild_id}.", err)
                return False

        def set_antiswear_enabled(self, value: bool) -> bool:
            """
            Sets the value of the antiswear_enabled column in the guilds table.
            """
            query = f"UPDATE guilds SET antiswear_enabled=%s WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (value, self.guild_id))
                    conn.commit()
                    return True
            except Exception as err:
                logging.error(f"Could not set antiswear protection to {value} for {self.guild_id}.", err)
                return False

        def get_antislur_enabled(self) -> bool:
            """
            Returns the value of the antislur_enabled column in the guilds table.
            """
            query = f"SELECT antislur_enabled FROM guilds WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                return result[0]
            except Exception as err:
                logging.error(f"Could not get antislur protection for {self.guild_id}.", err)
                return False

        def set_antislur_enabled(self, value: bool) -> bool:
            """
            Sets the value of the antislur_enabled column in the guilds table.
            """
            query = f"UPDATE guilds SET antislur_enabled=%s WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (value, self.guild_id))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not set antislur protection to {value} for {self.guild_id}.", err)
                return False

        def get_antispam_enabled(self) -> bool:
            """
            Returns the value of the antispam_enabled column in the guilds table.
            """
            query = f"SELECT antispam_enabled FROM guilds WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                return result[0]
            except Exception as err:
                logging.error(f"Could not get antispam protection for {self.guild_id}.", err)
                return False

        def set_antispam_enabled(self, value: bool) -> bool:
            """
            Sets the value of the antispam_enabled column in the guilds table.
            """
            query = f"UPDATE guilds SET antispam_enabled=%s WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (value, self.guild_id))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not set antispam protection to {value} for {self.guild_id}.", err)
                return False

        def get_show_censored_substrings(self) -> bool:
            """
            Returns the value of the show_censored_substrings_ok column in the guilds table.
            """
            query = f"SELECT show_censored_substrings FROM guilds WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                return result[0]
            except Exception as err:
                logging.error(f"Could not get show_censored_substrings_ok for {self.guild_id}.", err)
                return False

        def get_auditlog_channel_id(self):
            """
            Returns the value of the log_channel_id column in the guilds table.
            """
            query = f"SELECT channel_id FROM guild_log_channels WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                return result[0] if result else None
            except Exception as err:
                logging.error(f"Could not get log channel ID for {self.guild_id}.", err)
                return None

        def set_auditlog_channel_id(self, channel_id: int) -> bool:
            """
            Sets the value of the log_channel_id column in the guild_log_channels table.
            If the row does not exist, it will be created.
            """
            query_insert = """
            INSERT INTO guild_log_channels (guild_id, channel_id)
            VALUES (%s, %s)
            ON CONFLICT (guild_id) DO UPDATE SET channel_id = EXCLUDED.channel_id;
            """
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query_insert, (self.guild_id, channel_id))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not set log channel ID to {channel_id} for {self.guild_id}.", err)
                return False

        def set_auditlog_enabled(self, value: bool) -> bool:
            """
            Sets the value of the log_channel_enabled column in the guild_log_channels table.
            If the row does not exist, it will be created.
            """
            query_insert = """
            INSERT INTO guild_log_channels (guild_id, enabled)
            VALUES (%s, %s)
            ON CONFLICT (guild_id) DO UPDATE SET enabled = EXCLUDED.enabled;
            """
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query_insert, (self.guild_id, value))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not set log channel enabled to {value} for {self.guild_id}.", err)
                return False

        def get_auditlog_enabled(self) -> bool:
            """
            Returns the value of the log_channel_enabled column in the guilds table.
            """
            query = f"SELECT enabled FROM guild_log_channels WHERE guild_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id,))
                    result = cur.fetchone()
                return result[0] if result else False
            except Exception as err:
                logging.error(f"Could not get log channel enabled for {self.guild_id}.", err)
                return False

    class audit_log:
        def __init__(self, guild_id: int) -> None:
            """
            This is a class meant to track internally what AliceAM has done in a guild.
            May not be comprehensive, but it's a start.
            """
            self.guild_id = guild_id

        def add_image_scan_handling(self, offender_id: int, img: Image) -> bool:
            """
            Records an image scan violation and what Alice did about it.
            """
            assert isinstance(offender_id, int)
            assert isinstance(img, Image.Image)

            # Convert the image to byte data
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_data = img_byte_arr.getvalue()

            # Get the hash of the image
            img_hash = imagehash.average_hash(img)

            query = "INSERT INTO img_scanner_cases (guild_id, offender_id, img_hash, bytedata) VALUES (%s, %s, %s, %s)"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id, offender_id, str(img_hash), img_byte_data))
                    conn.commit()
                return True
            except Exception as err:
                logging.error(f"Could not add image scan violation to the database.", err)
                return False

        def get_caseid_for_img_scan(self, offender_id: int, img_hash: str) -> int | None:
            """
            Returns the case ID of an image scan violation.
            """
            query = "SELECT case_id FROM img_scanner_cases WHERE guild_id=%s AND offender_id=%s AND img_hash=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (self.guild_id, offender_id, img_hash))
                    result = cur.fetchone()
                return result[0] if result else None
            except Exception as err:
                logging.error(f"Could not get image scan case ID.", err)
                return None

        # noinspection PyMethodMayBeStatic
        def get_img_scan_case_by_id(self, case_ID: int):
            """
            Returns the image scan case by the case ID.
            """
            query = "SELECT * FROM img_scanner_cases WHERE case_id=%s"
            try:
                with PostgreSQL.get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(query, (case_ID,))
                    result = cur.fetchone()
                return result
            except Exception as err:
                logging.error(f"Could not get image scan case by ID.", err)
                return None

    # Not practical to make this DRY-Compliant, as the columns are different for each reputation type.
    # noinspection DuplicatedCode
    class user_reputation:
        def __init__(self, user_id: int) -> None:
            PostgreSQL.db_tables.ensure_user(user_id) # Makes sure the user is in the database
            self.user_id = user_id

        def get_reputation(self) -> dict:
            """
            Returns the value of all reputation columns in the users table.
            Formats in a dictionary.

            You can expect the result to look like this:
            {
                'slurs': -10~10,
                'swearing': -10~10,
                (etc. dict keys are same name for each DB column name without the 'rep_' prefix)
            }
            """
            # Get all column names that start with 'rep_'
            query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name LIKE 'rep_%'"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query)
                columns = cur.fetchall()

            # Initialize a dictionary to store the results
            reps_dict = {}
            # If columns exist, fetch the contents of each column
            if columns:
                for column in columns:
                    column_name = column[0]
                    query = f"SELECT {column_name} FROM users WHERE user_id = %s"
                    with PostgreSQL.get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute(query, (self.user_id,))
                        result = cur.fetchone()
                    # Store the column contents in the reps result dictionary
                    reps_dict[column_name] = result[0]
            else:
                raise EnvironmentError("No reputation columns found in the users table. Is the table missing columns?")

            return_dict = {}
            # Takes each key and removes the suffix 'rep_' to it. Then adds it to the return_dict
            # This is to keep the data consistent with the json storage and make it look cleaner on use.
            for key in reps_dict.keys():
                return_dict[key[4:]] = reps_dict[key]
            return return_dict

        def get_last_nullification_time(self) -> datetime:
            """
            Returns the value of the rep_nullification column in the users table.
            """
            query = f"SELECT nullification_time FROM users WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()
            return result[0]

        def set_last_nullification_time(self, timedate: float) -> None:
            """
            Sets the value of the rep_nullification column in the users table.
            """
            query = f"UPDATE users SET nullification_time=%s WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (timedate, self.user_id))

        def get_overall(self) -> float:
            # Get all column names that start with 'rep_'
            query = "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name LIKE 'rep_%'"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query)
                columns = cur.fetchall()

            # Initialize a dictionary to store the results
            reps_list = []

            # If columns exist, fetch the contents of each column
            if columns:
                for column in columns:
                    column_name = column[0]
                    query = f"SELECT {column_name} FROM users WHERE user_id = %s"
                    with PostgreSQL.get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute(query, (self.user_id,))
                        result = cur.fetchone()
                    # Store the column contents in the reps result list
                    if result:
                        reps_list.append(result[0])
                    else:
                        # appends starting data if the user has no data in the column
                        reps_list.append(0.0)
            else:
                logging.warning("No reputation columns found in the users table. Is the table missing columns?")

            # Gets an overall of a value from -10.0 to +10.0 based on how often each item in rep_list is closer to -10 or +10
            return round(sum(reps_list) / len(reps_list), 2)

        def get_slurs(self) -> float:
            """
            Returns the value of the rep_slurs column in the users table.
            """
            query = f"SELECT rep_slurs FROM users WHERE user_id=%s"

            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()

            if result:
                return result[0]
            else:
                return 0.0
        
        def set_slurs(self, value: float) -> None:
            """
            Sets the value of the rep_slurs column in the users table.
            """
            # If the value is less than -10.0, set it to -10.0. Max value is 10.0, min value is -10.0
            if value >= 10.0:
                value = 10.0
            elif value <= -10.0:
                value = -10.0

            query = f"UPDATE users SET rep_slurs=%s WHERE user_id=%s"

            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (value, self.user_id))
                conn.commit()

        def add_to_slurs(self, value: float) -> None:
            """
            Adds to the value of the rep_slurs column in the users table.
            """
            query = f"SELECT rep_slurs FROM users WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()
            if result:
                amount = result[0]
            else:
                amount = 0.0

            # If the addition made the value more than 10.0, set it to 10.0. Max value is 10.0, min value is -10.0
            value = amount + value
            if value >= 10.0:
                value = 10.0
            elif value <= -10.0:
                value = -10.0

            query = f"UPDATE users SET rep_slurs=%s WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (value, self.user_id))
                conn.commit()

        def subtract_from_slurs(self, value: float) -> None:
            """
            Subtracts from the value of the rep_slurs column in the users table.
            """
            query = f"SELECT rep_slurs FROM users WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()
            if result:
                amount = result[0]
            else:
                amount = 0.0

            # If the subtraction made the value less than -10.0, set it to -10.0. Max value is 10.0, min value is -10.0
            value = amount - value
            if value >= 10.0:
                value = 10.0
            elif value <= -10.0:
                value = -10.0

            query = f"UPDATE users SET rep_slurs=%s WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (value, self.user_id))
                conn.commit()

        def get_swearing(self) -> float:
            """
            Returns the value of the rep_swearing column in the users table.
            """
            query = f"SELECT rep_swearing FROM users WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()
            if result:
                return result[0]
            else:
                return 0.0
        
        def set_swearing(self, value: float) -> None:
            """
            Sets the value of the rep_swearing column in the users table.
            """
            # If the value is less than -10.0, set it to -10.0. Max value is 10.0
            if value >= 10.0:
                value = 10.0
            elif value <= -10.0:
                value = -10.0

            query = f"UPDATE users SET rep_swearing=%s WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (value, self.user_id))
                conn.commit()

        def add_to_swearing(self, value: float) -> None:
            """
            Adds to the value of the rep_swearing column in the users table.
            """
            query = f"SELECT rep_swearing FROM users WHERE user_id=%s"

            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()

            if result:
                amount = result[0]
            else:
                amount = 0.0

            # If the addition made the value more than 10.0, set it to 10.0. Max value is 10.0
            value = amount + value
            if value >= 10.0:
                value = 10.0
            elif value <= -10.0:
                value = -10.0

            query = f"UPDATE users SET rep_swearing=%s WHERE user_id=%s"

            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (value, self.user_id))
                conn.commit()

        def subtract_from_swearing(self, value: float) -> None:
            """
            Subtracts from the value of the rep_swearing column in the users table.
            """
            query = f"SELECT rep_swearing FROM users WHERE user_id=%s"

            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (self.user_id,))
                result = cur.fetchone()

            if result:
                amount = result[0]
            else:
                amount = 0.0

            # If the subtraction made the value less than -10.0, set it to -10.0. Min value is -10.0
            value = amount - value
            if value >= 10.0:
                value = 10.0
            elif value <= -10.0:
                value = -10.0

            query = f"UPDATE users SET rep_swearing=%s WHERE user_id=%s"
            with PostgreSQL.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, (value, self.user_id))
                conn.commit()