from library.storage import var, dt, PostgreSQL
from library.WebGUI.controller import gui
from library.encrpytion import encryption
import multiprocessing, os, hikari, sys
from library.variables import logging
from typing import List
import subprocess

keys = encryption()

colours = {
    'red': '\033[31m',
    'yellow': '\033[33m',
    'green': '\033[32m',
    'purple': '\033[35m',
    'reset': '\033[0m',
}

class alice:
    class errors:
        class exited_questioning(Exception):
            def __str__(self):
                return "The user exited the questioning."

    @staticmethod
    def setup():
        print(f"{colours['green']}Welcome to the setup wizard!{colours['reset']}")
        token = alice.ask_question(
            f"{colours['yellow']}Please enter your bot token.{colours['reset']}",
            confirm_validity=True, show_default=False
        )
        var.set(
            file='settings.json',
            key="token",
            value=keys.encrypt(token)
        )

        prefix = alice.ask_question('Please enter your prefix.', default='//', confirm_validity=True)
        var.set(file='settings.json', key='prefix', value=prefix)

        docker_installed = subprocess.run(['docker', '--version'], stdout=subprocess.PIPE).returncode == 0
        print("Docker is installed:", docker_installed)
        print("We're about to install a PostgreSQL Database Container. This is required for Alice to function.")
        if not docker_installed:
            print("Please install Docker before continuing.")
            exit(1)
        else:
            answer = alice.ask_question(
                "Do you want to install the PostgreSQL Database Container? (y/n)",
                options=['y', 'n'],
                show_options=False,
                default='y'
            )
            if answer != 'y':
                print("Installation of Alice and PostgreSQL cancelled.")
                exit(0)
            else:
                print("Installing PostgreSQL Database Container...")
                PostgreSQL.make_db_container()

        var.set(file='settings.json', key='first_start', value=False)

    @staticmethod
    def ask_question(
            question: str,
            options: List[str] = [],
            exit_phrase='exit',
            confirm_validity=True,
            ask_if_valid=False,
            default=None,
            show_default: bool = True,
            filter_func=None,
            colour='green',
            allow_default: bool = True,
            show_options: bool = True,
            exit_notif_msg: str = "default",
            clear_terminal: bool = True
    ) -> str:
        """
        Asks the user a question and returns the answer.

        :param question:
        :param options: The list of acceptable answers.
        :param exit_phrase: The phrase to type to exit the question.
        :param confirm_validity: Determines if the answer must be in the options list and toggles filter_func.
        :param ask_if_valid: Asks the user if the answer is correct.
        :param default: The default answer to return if the user enters nothing.
        :param show_default: If True, shows the default answer in the prompt.
        :param filter_func: A function to filter the answer. (can be anything)
        Have it return False if the answer is bad and -1 if the answer is bad but the user shouldn't be told.
        Return true if the answer is good.
        :param colour: The colour of the prompt. eg, "red" or "green".
        :param allow_default: If True, allows the default answer to be returned.
        :param show_options: If True, shows the options list.
        :param exit_notif_msg: The message to indicate how to exit questioning.
        :param clear_terminal: If True, clears the terminal before asking the question.
        :return: The answer to the question.
        :raises: self.exited_question if the user exits the question.
        """
        # Call validation
        assert type(options) is list, f"options must be a list, not {type(options)}"
        if len(options) > 0:
            for option in options:
                assert type(option) is str, f"options must be a list of strings, not {type(option)}"
        assert type(question) is str, f"question must be a string, not {type(question)}"
        assert type(exit_phrase) is str and exit_phrase != "", "exit_phrase must be a non-empty string."
        assert type(confirm_validity) is bool, f"confirm_validity must be a boolean. Not {type(confirm_validity)}"
        assert type(ask_if_valid) is bool, f"ask_if_valid must be a boolean. Not {type(ask_if_valid)}"
        assert default is not callable, f"default must not be a callable. It is {type(default)}"
        assert type(colour) is str, f"colour must be a string. Not {type(colour)}"
        assert type(allow_default) is bool, f"allow_default must be a boolean. Not {type(allow_default)}"
        assert type(show_options) is bool, f"show_options must be a boolean. Not {type(show_options)}"
        assert type(clear_terminal) is bool, f"clear_terminal must be a boolean. Not {type(clear_terminal)}"

        # Doing it like this since the f-string doesn't work in the args
        if exit_notif_msg == "default":
            exit_notif_msg = f" | Type '{exit_phrase}' to exit."

        try:
            if clear_terminal:
                os.system('clear' if sys.platform == 'linux' else 'cls')
            while True:
                if show_options and len(options) > 0:
                    print("\n")
                    for option in options:
                        print(f"- {colours['yellow']}{option}")
                    print("(Acceptable answers above)")
                print(f"{question}{exit_notif_msg}")
                answer = input(f"{colours[colour]}{f'({default}) ' if show_default else ''}>>> ")

                # Handles specific inputs, eg, exit phrase
                if answer == "":
                    if allow_default:
                        answer = default
                if answer == exit_phrase:
                    raise alice.errors.exited_questioning

                # Check if the answer is valid
                if confirm_validity:
                    if len(options) > 0 and answer not in options:
                        print(f"{colours['red']}Invalid input.")
                        continue
                    if filter_func is not None:
                        filter_result = filter_func(answer)
                        if filter_result is False:
                            print(f"{colours['red']}That input was filtered as bad.")
                            continue
                        elif filter_result == -1:
                            # -1 is for a bad input that should be filtered but not told to the user.
                            # Eg, if the filter func tells them why it's bad itself.
                            continue

                if ask_if_valid:
                    print(f"{colours['yellow']}You entered: {answer}. Is this correct? (y/n)")
                    response = input(">>> ").lower()
                    if response not in ['y', 'yes']:
                        continue

                return answer
        except KeyboardInterrupt:
            raise alice.errors.exited_questioning

if __name__ == '__main__':
    if not os.path.exists('settings.json'):
        var.fill_json(file='settings.json', data=dt.SETTINGS)

    if var.get(file='settings.json', key='first_start'):
        alice.setup()

    PostgreSQL.modernize()

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
