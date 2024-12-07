from library.storage import PostgreSQL, var
from library.botapp import bot
import lightbulb
import hikari

class civility_vote_listener(lightbulb.Plugin):
    @staticmethod
    @bot.listen(hikari.ReactionDeleteEvent)
    async def listener(event: hikari.ReactionDeleteEvent) -> None:
        db = PostgreSQL()

        # Gets all the message polls that are being listened to
        civility_polls = db.fetch_civility_polls()

        # Trust bot admins 100% when they vote.
        bot_admin_list = var.get('bot_admins')

        for poll in civility_polls:
            # poll: int. A Message ID
            if poll == event.message_id:
                if event.user_id in bot_admin_list:
                    db.audit_log(civility_polls[poll]['guild_id']).civility_logs.set_falsepositve_status(
                        status=False,
                        case_id=civility_polls[poll]['case_id']
                    )

                db.unvote_civility_poll(
                    case_id=civility_polls[poll]['case_id'],
                    voter_id=event.user_id,
                )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
