from library.botapp import bot, permissions
from library.variables import  swears
from library.automod import automod
from library.pylog import pylog
import lightbulb
import hikari

pylogger = pylog()

# Same colour as the embed box
colourless = bot.d['colourless']

class antiswear(lightbulb.Plugin):
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if automod.checkers.heuristical(event.message.content, swears) == True:
            is_admin = await permissions.check(hikari.Permissions.ADMINISTRATOR, member=event.member, guid=event.guild_id) # TODO: switch this to use cache
        else:
            return False

        if is_admin:
            server_msg = (
                "You are an administrator on this server.\n"
                "Start acting like it and hold yourself accountable."
            )
        else:
            server_msg = "Check failed. Such an action is forbidden on this server.\nWe have taken ethics action."

        await event.author.send(
            hikari.Embed(
                title="AntiSwear Check Failed",
                description=server_msg,
                color=colourless
            )
        )

        punish_success = await antiswear.punish(event)
        if punish_success is True and is_admin is False:
            await event.author.send(automod.gen_warning_embed("AntiSwear Check Failed"))

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