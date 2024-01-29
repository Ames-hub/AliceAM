from library.jmod import jmod
import hikari, multiprocessing, re

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
        print(f"{colours['yellow']}Please enter your bot token.{colours['reset']}")
        token = input("> ")
        print("Is this correct? (y/n)")
        print(f"Token: {token}")
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
            jmod.setvalue(json_dir='memory/settings.json',key='prefix',value=prefix)
            break
        else:
            continue

    while True:
        print(f'{colours["green"]}Do you want to use {colours["purple"]}PostgreSQL{colours["green"]} or do you want to use {colours["purple"]}Json files{colours["green"]} for long-term memory?')
        print('PostgreSQL is recommended for larger server that cant lose data. but Json files are easier to setup.')
        print(f'{colours["yellow"]}Option 1. PostgreSQL')
        print(f'Option 2. Json files{colours["reset"]}')

        do_postgre = input('> ').lower()
        do_postgre = do_postgre == '1' or do_postgre == 'postgresql' or do_postgre == "option 1"
        print('Is this correct? (y/n)')
        print(f'Use PostgreSQL: {do_postgre}')
        if input('> ').lower() == 'y':
            jmod.setvalue('use_postgre', 'memory/settings.json', do_postgre)
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
            print(f'{colours["green"]}Please enter your PostgreSQL database password.{colours["reset"]}')
            db_password = input('> ')
            print('Is this correct? (y/n)')
            print(f'Database password: {db_password}')
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

    jmod.setvalue(json_dir='memory/settings.json',key='first_start',value=False)

if jmod.getvalue(json_dir='memory/settings.json',key='first_start') == True:
    introduction()

from library.pylog import logman
if __name__ == '__main__':
    # Importing down here so that the introduction() function can look better.
    from library.botapp import bot
    from library.storage import db_tables, do_use_postgre

    logman_thread = multiprocessing.Process(
        target=logman,
        args=()
    )
    logman_thread.start()

    if do_use_postgre():
        db_tables.ensure_exists()

    @bot.listen()
    async def on_ready(event: hikari.ShardReadyEvent) -> None:
        print(f"Logged in as {event.my_user.username}")

    bot.load_extensions_from("cogs/automod/")

    bot.run()