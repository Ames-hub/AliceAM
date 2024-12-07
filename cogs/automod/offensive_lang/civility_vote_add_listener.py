# This is an example plugin for you to learn from how to get started with plugins.
# BASICALLY, you follow standard Hikari-Lightbulb syntax when making plugins/commands.

from library.storage import PostgreSQL, var
from library.automod import automod
from library.botapp import bot
import lightbulb
import hikari

class civility_vote_listener(lightbulb.Plugin):
    @staticmethod
    @bot.listen(hikari.ReactionAddEvent)
    async def listener(event: hikari.ReactionAddEvent) -> None:
        good = "👍"
        is_good = event.emoji_name == good

        db = PostgreSQL()

        # If user's trust ratio is below 50%, they can't vote.
        # This is because when at >50% trust, the AI begins to watch the user.
        # So it's a way to prevent users from messing with the system's data by saying, "No really! I'm trustworthy!"
        user = db.users(event.user_id)
        if user.get_trust() < 50:
            # Remove their reaction.
            await event.app.rest.delete_reaction(
                channel=event.channel_id,
                message=event.message_id,
                user=event.user_id,
                emoji=event.emoji_name
            )

        # Gets all the message polls that are being listened to
        civility_polls = db.fetch_civility_polls()

        for poll in civility_polls:
            # poll: int. A Message ID
            if poll == event.message_id:
                # Checks if the user has voted for this before.
                if db.fetch_civility_polls_voters(civility_polls[poll]['case_id']):
                    # If the user has voted before, invalidate their previous vote and update it anew.
                    success = db.unvote_civility_poll(
                        case_id=civility_polls[poll]['case_id'],
                        voter_id=event.user_id
                    )
                    if not success:
                        # If we can't remove the vote, we can't add a new one.
                        embed = (
                            hikari.Embed(
                                title="Error",
                                description="You have already voted on this poll.\n"
                                            "Please undo your previous vote before voting again.",
                                color=hikari.Color(0xff0000)
                            )
                        )

                        await automod.send_member_dm(
                            content=embed,
                            user_id=event.user_id
                        )
                        return

                # Trust bot admins 100% when they vote.
                bot_admin_list = var.get('bot_admins')

                if is_good:
                    if event.user_id in bot_admin_list:
                        db.audit_log(civility_polls[poll]['guild_id']).civility_logs.set_falsepositve_status(
                            status=False,
                            case_id=civility_polls[poll]['case_id']
                        )

                    db.vote_civility_poll(
                        case_id=civility_polls[poll]['case_id'],
                        voter_id=event.user_id,
                        rating="ACCURATE"
                    )
                else:
                    if event.user_id in bot_admin_list:
                        db.audit_log(civility_polls[poll]['guild_id']).civility_logs.set_falsepositve_status(
                            status=True,
                            case_id=civility_polls[poll]['case_id']
                        )
                    db.vote_civility_poll(
                        case_id=civility_polls[poll]['case_id'],
                        voter_id=event.user_id,
                        rating="INCORRECT"
                    )
                break

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
