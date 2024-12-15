from library.storage import PostgreSQL
from library.variables import slurs
from library.automod import automod
from library.botapp import bot
import lightbulb
import datetime
import hikari

# Same colour as the embed box
colourless = bot.d['colourless']

class antislur(lightbulb.Plugin):
    @staticmethod
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if event.author.is_bot:
            return False

        if event.message.content == "" or event.message.content is None:
            return False

        guild_enabled = PostgreSQL.guild(event.guild_id).get_antislur_enabled()
        if guild_enabled is False:
            return False

        Heuristic_check = automod.text_checkers(
            content=event.message.content,
            blacklist=slurs,
            account_for_rep=True,
            user_id=event.author_id,
            guild_id=event.guild_id
        ).rep_heuristic()

        user = PostgreSQL.users(event.author_id)
        if Heuristic_check[0] is False:
            # Reward user for not breaking the rule
            user.modify_trust(0.5, "+")
            return False

        punish_success = await antislur.punish(event)
        if not punish_success:
            await event.message.respond(
                hikari.Embed(
                    title='AntiSlur Check Failed',
                    description=f'**{event.author.username}** Used a slur in their message,'
                                'but I was unable to delete it.\n'
                                'Please intervene manually and check my permissions.',
                    color=colourless,
                    timestamp=datetime.datetime.now().astimezone()
                )
                .set_thumbnail(event.author.avatar_url)
            )

    @staticmethod
    async def punish(event: hikari.GuildMessageCreateEvent):
        # Punish the member for saying a slur
        result = await automod.punish(
            action='delete',
            event=event,
            dm_offender=False,
            reason=f'Used a slur in their message. (Automod: AntiSlur)\nContent detected: {event.message.content}',
        )
        success = result.get('success')
        return success

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
