from library.botapp import bot, permissions
from library.variables import slurs
from library.automod import automod
from library.storage import memory
import lightbulb
import hikari

# Same colour as the embed box
colourless = bot.d['colourless']

class antislur(lightbulb.Plugin):
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        guild_enabled = memory.guild(event.guild_id).get_antislur_enabled()
        if guild_enabled is False:
            return False
        
        if automod.checkers.heuristical(event.message.content, slurs) == True:
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
                title="AntiSlur Check Failed",
                description=server_msg,
                color=colourless
            )
        )

        punish_success = await antislur.punish(event)
        if punish_success is True and is_admin is False:
            await event.author.send(automod.gen_warning_embed("AntiSlur Check Failed"))

    async def punish(event: hikari.GuildMessageCreateEvent):
        # Punish the member for saying a slur
        success = False
        try:
            await event.message.delete()
            success = True
        except (hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError, hikari.UnauthorizedError):
            pass
        return success

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))