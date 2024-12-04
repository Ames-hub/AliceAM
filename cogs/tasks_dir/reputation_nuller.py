from library.storage import PostgreSQL
from library.botapp import tasks
import lightbulb
import datetime

@tasks.task(h=24, auto_start=True)
def null_rep():
    """
    A function which slowly moves the reputation of all to 0.
    """
    user_list = PostgreSQL.list_known_users()  # A list of ID's of all known users.

    for user_id in user_list:
        user = PostgreSQL.users(user_id)

        last_cooldown_time = datetime.datetime.fromtimestamp(user.get_trust_last_modified())
        if last_cooldown_time < datetime.datetime.now() - datetime.timedelta(hours=12):
            user.modify_trust(5, "-")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
