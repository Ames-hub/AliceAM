from library.storage import PostgreSQL
from library.variables import swears
from library.automod import automod
from library.botapp import bot
import lightbulb
import datetime
import hikari

# Same colour as the embed box
colourless = bot.d['colourless']

class antiswear(lightbulb.Plugin):
    @staticmethod
    @bot.listen(hikari.GuildMessageCreateEvent)
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if event.author.is_bot:
            return False

        if event.message.content == "" or event.message.content is None:
            return False

        guild_enabled = PostgreSQL.guild(event.guild_id).get_antiswear_enabled()
        if guild_enabled is False:
            return False

        Heuristic_Check = automod.text_checkers(
            content=event.message.content,
            blacklist=swears,
            account_for_rep=True,
            user_id=event.author_id,
            guild_id=event.guild_id
        ).rep_heuristic()

        HC_Bool = Heuristic_Check[0]

        user = PostgreSQL.users(event.author_id)
        if HC_Bool is False:
            # Reward user for not breaking the rule
            user.modify_trust(0.5, "+")
            return False

        punish_success = await antiswear.punish(event)
        if not punish_success:
            await event.message.respond(
                hikari.Embed(
                    title='AntiSwear Check Failed',
                    description=f'**{event.author.username}** Swore in their message,'
                                'but I was unable to delete it.\n'
                                'Please intervene manually and check my permissions.',
                    color=colourless,
                    timestamp=datetime.datetime.now().astimezone()
                )
                .set_thumbnail(event.author.avatar_url)
            )

    @staticmethod
    async def punish(event: hikari.GuildMessageCreateEvent):
        # Punish the member for saying a Swear
        result = await automod.punish(
            action='delete',
            event=event,
            dm_offender=False,
            reason='Swore in their message.\n(Automod: AntiSwear)',
        )
        success = result.get('success')
        return success


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
