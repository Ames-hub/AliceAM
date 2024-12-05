from library.storage import PostgreSQL
from library.variables import logging
from library.botapp import tasks
import lightbulb

@tasks.task(s=15, wait_before_execution=True, auto_start=True)
def update_expired_status() -> None:
    """
    Updates the expired status of infractions based on the lasts_to timestamp.
    """
    query = """
    UPDATE infraction_durations
    SET expired = TRUE
    WHERE lasts_to < EXTRACT(EPOCH FROM CURRENT_TIMESTAMP)::BIGINT
    """
    try:
        with PostgreSQL.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
    except Exception as err:
        logging.error("Could not update expired status.", err)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
