from library.storage import PostgreSQL
from library.botapp import tasks
import lightbulb
import datetime

@tasks.task(s=15, auto_start=True)
def null_rep():
    """
    A function which slowly moves the reputation of all to 0.
    """
    guild_list = PostgreSQL.list_known_guilds()
    for guild_id in guild_list:
        print(f"Checking guild {guild_id}")
        guild_pg = PostgreSQL.guild(guild_id)
        infraction_list = guild_pg.get_active_lt_infractions()
        print(len(infraction_list))
        for item in infraction_list:
            infraction_id = item['infraction_id']
            lasts_to = item['lasts_to']
            print(f"Infraction {infraction_id} lasts to {lasts_to}")

            if lasts_to == -1 or lasts_to is None:
                print(f"Infraction {infraction_id} is permanent.")
                continue  # Infraction is permanent.

            if lasts_to < datetime.datetime.now().timestamp():
                print(f"Infraction {infraction_id} has expired.")
                # Delete the infraction from the database.
                guild_pg.set_expired_lt_infraction(infraction_id, status=True)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
