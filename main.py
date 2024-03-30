import multiprocessing, os, hikari, sys, json
from getpass import getpass
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

    while True:
        print(f"{colours['green']}Please enter your prefix. (Default: !!){colours['reset']}")
        prefix = input("> ")
        if prefix == "":
            prefix = "!!"
        print("Is this correct? (y/n)")
        print(f"Prefix: {prefix}")
        if input("> ").lower() == "y":
            jmod.setvalue(json_dir='settings.json',key='prefix',value=prefix)
            break
        else:
            continue

    while True:
        print(f'{colours["green"]}Do you want to use {colours["purple"]}PostgreSQL{colours["green"]} or do you want to use {colours["purple"]}Json files{colours["green"]} for long-term memory?')
        print('PostgreSQL is recommended for larger server that cant lose data. but Json files are easier to setup and are recommended for small servers.')
        print(f'{colours["yellow"]}Option 1. PostgreSQL')
        print(f'Option 2. Json files{colours["reset"]}')

        do_postgre = input('> ').lower()
        do_postgre = do_postgre == '1' or do_postgre == 'postgresql' or do_postgre == "option 1"
        print('Is this correct? (y/n)')
        print(f'Use PostgreSQL: {do_postgre}')
        if input('> ').lower() == 'y':
            jmod.setvalue('use_postgre', 'settings.json', do_postgre)
            break
        else:
            continue
    
    if do_postgre:
        while True:
            print(f'{colours["green"]}Please enter the DB Name you want us to use.{colours["reset"]}')
            db_database = input('> ')
            print('Is this correct? (y/n)')
            print(f'Database: {db_database}')
            if input('> ').lower() == 'y':
                break
            else:
                continue

        while True:
            print(f'{colours["green"]}Please enter your PostgreSQL database username.{colours["reset"]}')
            db_username = input('> ')
            print('Is this correct? (y/n)')
            print(f'Database username: {db_username}')
            if input('> ').lower() == 'y':
                break
            else:
                continue

        while True:
            print(f'{colours["green"]}Please enter your PostgreSQL database password. (input hidden){colours["reset"]}')
            db_password = getpass('> ')
            print('Is this correct? (y/n)')
            print(f'Does your DB password end with: {db_password[-5:]}')
            if input('> ').lower() == 'y':
                break
            else:
                continue

        while True:
            print(f'{colours["green"]}Please enter your PostgreSQL database host.{colours["reset"]}')
            db_host = input('> ')
            print('Is this correct? (y/n)')
            print(f'Database host: {db_host}')
            if input('> ').lower() == 'y':
                break
            else:
                continue

        while True:
            print(f'{colours["green"]}Please enter your PostgreSQL database port.{colours["reset"]}')
            db_port = input('> ')
            print('Is this correct? (y/n)')
            print(f'Database port: {db_port}')
            if input('> ').lower() == 'y':
                break
            else:
                continue

    with open('secrets.env', 'a+') as f:
        f.write(f'TOKEN={token}\n')
        f.write(f'DB_HOST={db_host}\n')
        f.write(f'DB_PORT={db_port}\n')
        f.write(f'DB_DATABASE={db_database}\n')
        f.write(f'DB_USERNAME={db_username}\n')
        f.write(f'DB_PASSWORD={db_password}')

    jmod.setvalue(json_dir='settings.json',key='first_start',value=False)

if __name__ == '__main__':
    from library.data_tables import data_tables
    with open('settings.json', 'w') as f:
        json.dump(data_tables.SETTINGS_DT, f, indent=4, separators=(',', ': '))

    if jmod.getvalue(json_dir='settings.json',key='first_start') == True:
        introduction()

    # Importing down here so that the introduction() function can look better.
    from library.storage import db_tables, do_use_postgre
    if do_use_postgre():
        db_tables.ensure_exists()

    from library.botapp import bot
    bot.load_extensions_from("cogs/automod/antislur/")
    bot.load_extensions_from("cogs/automod/antiswear/")
    bot.load_extensions_from("cogs/automod/antispam/")
    bot.load_extensions_from("cogs/automod/passive/")
    bot.load_extensions_from("cogs/error_handlers/")
    bot.load_extensions_from("cogs/tasks_dir/")
    if len(os.listdir("cogs/plugins/")) != 0: # Without this line, it will except since there are no plugins.
        bot.load_extensions_from("cogs/plugins/") # This is for easy-implementation of your own plugins.

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

    # My own integration to report to pterodactyl panel that the bot is ready. Recommended to remove if you're not using pterodactyl.
    if os.environ.get('IS_PTERODACTYL', None) == 'yes':
        print('pterodactyl:ok')

    bot.run()