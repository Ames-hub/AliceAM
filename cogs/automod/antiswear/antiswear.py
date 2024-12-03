from library.botapp import bot, permissions
from library.storage import PostgreSQL
from library.variables import swears
from library.automod import automod
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
        if HC_Bool is not False:
            is_admin = await permissions.check(hikari.Permissions.ADMINISTRATOR, member=event.member, guid=event.guild_id)
            # Punishes user for breaking the rule
            user.subtract_from_swearing(0.8)
        else:
            # Reward user for not breaking the rule
            user.add_to_swearing(0.05)
            return False

        server_msg = automod.gen_user_warning_embed(
            'AntiSwear Check Failed',
            is_admin=is_admin,
            check_result=Heuristic_Check,
            user_id=event.author_id
        )

        punish_success = await antiswear.punish(event)
        if punish_success:
            if is_admin:
                await event.author.send(server_msg)
            else:
                await event.message.respond(server_msg)
        else:
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
        success = False
        try:
            await event.message.delete()
            success = True
        except (hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError, hikari.UnauthorizedError):
            pass
        return success


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
