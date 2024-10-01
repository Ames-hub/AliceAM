from library.storage import PostgreSQL
from library.botapp import tasks
import lightbulb
import datetime
import random

@tasks.task(h=24, auto_start=True)
def null_rep():
    """
    A function which slowly moves the reputation of all to 0.
    """
    user_list = PostgreSQL.list_known_users()

    for user_id in user_list:
        user = PostgreSQL.user_reputation(user_id)
        last_nulled = user.get_last_nullification_time()

        # Calculate the time difference since the last nullification
        timenow = datetime.datetime.now()
        time_difference = timenow - last_nulled

        # If the time difference is greater than 2 days (172800 seconds), nullify the reputation
        if time_difference.total_seconds() >= 172800:
            # Gets the user's reputation details
            user_rep_dict = user.get_reputation()

            swearing_rep = user_rep_dict['swearing']
            slur_rep = user_rep_dict['slurs']

            # Handles nulling swearing reputation.
            # noinspection PyTypeChecker
            def calc_null_amount(rep):
                if rep >= 0:
                    return max(0, min(0.5, 1 - abs(rep) / 20))  # Moves towards 0 for positive rep
                else:
                    return min(0, max(-0.5, -1 + abs(rep) / 20))  # Moves towards 0 for negative rep

            if swearing_rep != 0:
                amount = calc_null_amount(swearing_rep)
                if swearing_rep == -8:
                    continue # Don't save those with the lowest reputation.

                if swearing_rep <= -5:
                    # 50% chance of not nullifying the reputation.
                    # Makes it harder for those with very low reputation to get out of it.
                    if random.randint(0, 1) == 1:
                        continue

                user.subtract_from_swearing(amount)

            if slur_rep != 0:
                amount = calc_null_amount(slur_rep)
                if slur_rep <= -8:
                    continue # Don't save those with the lowest reputation.

                if slur_rep <= -5:
                    # 50% chance of not nullifying the reputation.
                    # Makes it harder for those with very low reputation to get out of it.
                    if random.randint(0, 1) == 1:
                        continue

                user.subtract_from_slurs(amount)

            # Updates last nulled value so that the user doesn't get nullified again too soon.
            user.set_last_nullification_time(timenow.timestamp())

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
