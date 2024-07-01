import multiprocessing, os, hikari, sys, json
from getpass import getpass
import psycopg2

# Makes sure that needed directories exist
os.makedirs('logs', exist_ok=True)
# Import after so that the needed directories exist before neccesary files are interacted with
from library.jmod import jmod
from library.WebGUI.controller import gui
from library.variables import logging

colours = {
    'red': '\033[31m',
    'yellow': '\033[33m',
    'green': '\033[32m',
    'purple': '\033[35m',
    'reset': '\033[0m',
}

class alice:
    class errors:
        class exited_question(Exception):
            pass

    def introduction():
        while True:
            print(f"{colours['green']}Welcome to the setup wizard!{colours['reset']}")
            print(f"{colours['yellow']}Please enter your bot token. (input hidden){colours['reset']}")
            token = getpass("> ")
            print(f"Does your token end with {token[-5:]}? (y/n)")
            if input("> ").lower() == "y":
                break
            else:
                continue

        prefix = alice.ask_question('Please enter your prefix.', default='..')
        jmod.setvalue(json_dir='settings.json', key='prefix', value=prefix)

        print('PostgreSQL is recommended for larger server that cant lose data.')
        print('but Json files are easier to setup and are recommended for smaller servers.')
        print(f'{colours["yellow"]}Option 1. PostgreSQL')
        print(f'Option 2. Json files{colours["reset"]}')

        options = ['postgre', 'sql', 'postgresql', 'json', '1', '2']
        do_postgre = alice.ask_question(
            f'Which one do you want to use?',
            filter_func=lambda q: q.lower() in options
        )

        do_postgre = do_postgre == '1' or do_postgre == 'postgresql' or do_postgre == "option 1"
        print('Is this correct? (y/n)')
        print(f'Use PostgreSQL: {do_postgre}')
        jmod.setvalue('use_postgre', 'settings.json', do_postgre)

        if do_postgre:
            while True:  # Retry logic if any of the details are wrong
                db_host = alice.ask_question(f'{colours["green"]}Please enter your PostgreSQL database host.{colours["reset"]}')
                db_port = alice.ask_question(f'{colours["green"]}Please enter your PostgreSQL database port.{colours["reset"]}')
                db_username = alice.ask_question(f'{colours["green"]}Please enter your PostgreSQL database username.{colours["reset"]}')
                if db_username == 'postgre' or db_username == 'postgres' or db_username == 'root':
                    print(f'{colours["red"]}You are using the root username. This has severe security risks.')
                    print(f'Waive dangersand continue regardless? (y/n){colours["reset"]}')
                    if input('> ').lower() == 'y':
                        break
                    else:
                        continue

                db_password = alice.ask_question(
                    f'{colours["green"]}Please enter your PostgreSQL database password. (input hidden){colours["reset"]}',
                    hide_input=True
                )

                db_database = alice.ask_question(f'{colours["green"]}Please enter the Database you want us to use.{colours["reset"]}')

                # Tests the connection
                try:
                    psycopg2.connect(
                        host=db_host,
                        port=db_port,
                        user=db_username,
                        password=db_password,
                        database=db_database
                    )
                except psycopg2.OperationalError as err:
                    print(
                        f'{colours["red"]}Couldn\'t connect to database. Did you enter the right details?{colours["reset"]}')
                    print(f'{colours["red"]}Error: {err}{colours["reset"]}')
                    print("We are sending you back to retry.")
                    continue

                with open('secrets.env', 'a+') as secrets_file:
                    secrets_file.write(f'TOKEN={token}\n')
                    secrets_file.write(f'DB_HOST={db_host}\n')
                    secrets_file.write(f'DB_PORT={db_port}\n')
                    secrets_file.write(f'DB_DATABASE={db_database}\n')
                    secrets_file.write(f'DB_USERNAME={db_username}\n')
                    secrets_file.write(f'DB_PASSWORD={db_password}')
                break

        jmod.setvalue(json_dir='settings.json', key='first_start', value=False)

    def ask_question(
        question:str, options:list=None, exit_phrase='exit', confirm_validity=False, show_default=True, default=None,
        filter_func=None, colour='green', do_listing:bool=False, allow_default:bool=True, show_options:bool=True,
        hide_input=False
    ) -> str:
        assert do_listing in [True, False], "Do_listing must be a boolean."
        try:
            answers_list = []
            while True:
                print(question if not show_default else f"{question} (Default: {default})")
                if do_listing is True:
                    print("(Type 'done' to finish giving answers)")
                    if not hide_input:
                        response = input(f"({len(answers_list)}) {colours[colour]}>>> {colours['reset']}")
                    else:
                        response = getpass(f"({len(answers_list)}) {colours[colour]}>>> {colours['reset']}")
                    if response == '':
                        print(f"{colours['red']}Error: Invalid response. Cannot choose default for lists.{colours['reset']}")
                        continue
                    if response == exit_phrase:
                        raise alice.errors.exited_question

                    try:
                        if not filter_func(response):
                            print(f"{colours['red']}Error: response breaks requirement rules.{colours['reset']}")
                            continue
                    except Exception as err:
                        print("Error while trying to run data validation filters. Do you want to continue? (y/*n)")
                        retry = input(f"{colours['red']}>>> {colours['reset']}").lower()
                        if retry not in ['y', 'yes']:
                            raise alice.errors.exited_question

                    if response == 'done':
                        if len(answers_list) == 0:
                            return []
                        break
                    answers_list.append(response)
                else:
                    if show_options:
                        if options is not None:
                            print(f"Options: {', '.join(options)}")
                    if not hide_input:
                        response = input(f"{colours[colour]}>>> {colours['reset']}")
                    else:
                        response = getpass(f"{colours[colour]}>>> {colours['reset']}")

                if exit_phrase == response:
                    raise alice.errors.exited_question
                elif response == '' and allow_default is True:
                    response = default

                if options is not None:
                    if response not in options:
                        print(f"{colours['red']}Error: Invalid response.{colours['reset']}")
                        continue

                if filter_func is not None:
                    try:
                        if not filter_func(response):
                            print(f"{colours['red']}Error: response breaks requirement rules.{colours['reset']}")
                            continue
                    except Exception as err:
                        print("Error while trying to run data validation filters. Do you want to continue? (y/*n)")
                        retry = input(f"{colours['red']}>>> {colours['reset']}").lower()
                        if retry not in ['y', 'yes']:
                            raise alice.errors.exited_question

                if confirm_validity:
                    if response != default:
                        print("Is that correct? (y/*n)")
                    else:
                        print("use the default? (*y/n)")
                    valid = input().lower()
                    if valid not in ['y', 'yes']:
                        continue

                return response if not do_listing else answers_list
        except KeyboardInterrupt:
            return default

if __name__ == '__main__':
    from library.data_tables import data_tables
    if not os.path.exists('settings.json'):
        with open('settings.json', 'w') as f:
            json.dump(data_tables.SETTINGS_DT, f, indent=4, separators=(',', ': '))

    if bool(jmod.getvalue(json_dir='settings.json', key='first_start')):
        alice.introduction()

    # Importing down here so that the introduction() function can look better.
    from library.storage import db_tables, do_use_postgre
    if do_use_postgre():
        db_tables.modernize()

    from library.botapp import bot
    bot.load_extensions_from("cogs/automod/antislur/")
    bot.load_extensions_from("cogs/automod/antiswear/")
    bot.load_extensions_from("cogs/automod/antispam/")
    bot.load_extensions_from("cogs/automod/passive/")
    bot.load_extensions_from("cogs/error_handlers/")
    bot.load_extensions_from("cogs/tasks_dir/")
    if len(os.listdir("cogs/plugins/")) != 0:
        # This is for easy-implementation of your own plugins.
        # Even though if your making a plugin you probs already changed this files code.
        bot.load_extensions_from("cogs/plugins/")

    # Bot must be ran in terminal. We can't run it in the background (blocks the terminal even when ran in a different thread)
    # We will use a WebGUI Instead, and the webgui will be ran in a different thread.
    WEBGUI_THREAD = multiprocessing.Process(
        target=gui.run,
        args=()
    )
    WEBGUI_THREAD.start()

    is_linux = sys.platform == 'linux'
    os.system('clear' if is_linux else 'cls')
    logging.info("Bot is starting...")
    logging.info("Running on Linux? : " + str(is_linux) + f" ({sys.platform})")

    @bot.listen()
    async def on_ready(event: hikari.events.ShardReadyEvent):
        print(f"{colours['green']}Bot is ready!{colours['reset']}")
        print(f"{colours['yellow']}Logged in as: {event.my_user.username}{colours['reset']}")

    try:
        if bool(os.environ.get("RUN_BOT", True)) is True:
            bot.run()
        else:
            logging.info("Bot was not ran because the environment variable RUN_BOT was set to False.")
            print("Bot was not ran because the environment variable RUN_BOT was set to False. Running loop.")
            while True:
                pass
    except hikari.errors.UnauthorizedError:
        logging.error("Invalid token provided. Please check your token in secrets.env (or env variables and try again.")
        print(f"{colours['red']}Invalid token provided. Please check your token in secrets.env (or env variables and try again.{colours['reset']}")
        exit(1)
    except KeyboardInterrupt:
        logging.info("Bot was stopped by the user.")
        print(f"{colours['red']}Bot was stopped by the user.{colours['reset']}")
        exit(0)
