from library.botapp import bot, permissions
from library.variables import swears
from library.automod import automod
from library.storage import memory
import lightbulb
import hikari

# Same colour as the embed box
colourless = bot.d['colourless']

class antiswear(lightbulb.Plugin):
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if event.author.is_bot:
            return False
        guild_enabled = memory.guild(event.guild_id).get_antiswear_enabled()
        if guild_enabled is False:
            return False

        Heuristic_check = automod.text_checkers(
                content=event.message.content,
                blacklist=swears,
                account_for_rep=True,
                user_id=event.author_id
        ).repHeuristic()

        user = memory.user_reputation(event.author_id)
        if Heuristic_check is not False:
            is_admin = await permissions.check(hikari.Permissions.ADMINISTRATOR, member=event.member, guid=event.guild_id)
            # Punishes user for breaking the rule
            user.subtractFrom_swearing(0.8)
        else:
            # Reward user for not breaking the rule
            user.addTo_swearing(0.05)
            return False

        server_msg = automod.gen_user_warning_embed(
            'AntiSwear Check Failed',
            is_admin=is_admin,
            check_result=Heuristic_check,
            user_id=event.author_id
        )

        punish_success = await antiswear.punish(event)
        if punish_success:
            if is_admin:
                await event.author.send(server_msg)
            else:
                await event.message.respond(server_msg)

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
