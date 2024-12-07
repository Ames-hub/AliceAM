from library.storage import PostgreSQL
from library.automod import automod
from library.ai import AliceIntel
from library.botapp import bot
import lightbulb
import datetime
import hikari

# Same colour as the embed box
colourless = bot.d['colourless']

class civility_plugin(lightbulb.Plugin):
    @staticmethod
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if event.author.is_bot:
            return False

        if event.message.content == "" or event.message.content is None:
            return False

        guild_enabled = PostgreSQL.guild(event.guild_id).get_civility_filter_enabled()
        if guild_enabled is False:
            return False

        user = PostgreSQL.users(event.author_id)
        # Due to the common false-flags of the AI, The AI will only begin to search once a users Trust ratio Is >50%
        if user.get_trust() >= 50:
            # Higher than 49% will skip the AI check.
            return False

        civility_check = AliceIntel.InsultPredictor.predict(
            text=event.message.content,
            consider_trust=(True, event.author_id)
        )

        if civility_check['label'] != "OFFENSIVE":
            # Reward user for not breaking the rule
            user.modify_trust(0.5, "+")
            return False

        # An attempt to compensate for the inaccuracy of the AI.
        is_past_false_positive = automod.is_past_civility_fp(event.message.content)
        if is_past_false_positive is False:
            punish_success = await civility_plugin.punish(event)
        else:
            # Recorded as a false positive. No punishment will be issued.
            return False

        if not punish_success:
            await event.message.respond(
                hikari.Embed(
                    title='Civility Check Failed',
                    description=f'**{event.author.username}** Was uncivil in their message,'
                                'but I was unable to delete it.\n'
                                'Please intervene manually and check my permissions.',
                    color=colourless,
                    timestamp=datetime.datetime.now().astimezone()
                )
                .set_thumbnail(event.author.avatar_url)
            )

    @staticmethod
    async def punish(event: hikari.GuildMessageCreateEvent):
        # Punish the member for being uncivil
        reason = 'Was uncivil in their message.\n(Automod: Civility Filter)'

        fields = {
            "PM": {},
            "LOG": {'Crowdsourced Rating': "Was this a false positive? Let me know by reacting to this message!\n"
                                           "Use \"👍\" if I did well, or \"👎\" if I got it wrong.",},
            "ANNOUNCEMENT": {},
        }

        pub_crowdsourcing_allowed = PostgreSQL.guild(event.guild_id).pub_crowdsourced_ratings_enabled()
        if pub_crowdsourcing_allowed:
            fields["ANNOUNCEMENT"] = {
                'Message Sent by Offender': automod.censor_text(event.message.content),
                'Crowdsourced Rating': "Was this a false positive? Let me know by reacting to this message!\n"
                                       "Use \"👍\" if I did well, or \"👎\" if I got it wrong.",
            }

        result = await automod.punish(
            action='delete',
            event=event,
            additional_fields=fields,
            dm_offender=True,
            reason=reason,
        )

        PostgreSQL.audit_log(guild_id=event.guild_id).civility_logs.add_offensive_lang_handling(
            offender_id=event.author_id,
            message=event.message.content,
        )

        # If this is none, No log channel was set up.
        log_msg_id = result.get('log_msg_id')
        announcement_msg_id = result.get('announcement_msg_id')

        # Start tracking both the announcement message and the log message (if it exists)
        # This is used to crowdsource a list of false positives.
        if result.get('success') is True:
            # Wait a bit. Debug method
            if log_msg_id is not None:
                await PostgreSQL().track_new_civility_report_ratings(
                    message_id=log_msg_id,
                    down_threshold = 3,  # 3 Admins/Mods must agree that it was a false positive.
                    case_id=result.get('new_case_id'),
                    guild_id=event.guild_id
                )
            if announcement_msg_id is not None:
                if pub_crowdsourcing_allowed:
                    await PostgreSQL().track_new_civility_report_ratings(
                        message_id=announcement_msg_id,
                        down_threshold = 10,
                        case_id=result.get('new_case_id'),
                        guild_id=event.guild_id
                    )

        success = result.get('success')
        return success

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
