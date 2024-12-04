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
        civility_check = AliceIntel.InsultPredictor.predict(
            text=event.message.content,
            consider_trust=(True, event.author_id)
        )

        if civility_check['label'] != "OFFENSIVE":
            # Reward user for not breaking the rule
            user.modify_trust(0.5, "+")
            return False

        punish_success = await civility_plugin.punish(event)
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
        result = await automod.punish(
            action='delete',
            event=event,
            dm_offender=True,
            reason='Was uncivil in their message.\n(Automod: Civility Filter)',
        )
        success = result.get('success')
        return success

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
