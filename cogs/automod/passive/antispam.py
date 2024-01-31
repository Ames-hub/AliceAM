from library.botapp import bot, permissions
from library.automod import automod
from library.storage import memory
import lightbulb
import hikari

# Same colour as the embed box
colourless = bot.d['colourless']
anti_spam_dict = {}

class antispam(lightbulb.Plugin):
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if event.author.is_bot:
            return False
        
        # Check if the guild has antispam enabled
        guild_enabled = memory.guild(event.guild_id).get_antispam_enabled()
        if guild_enabled is False:
            return False
        
        try:
            AM_antispam = anti_spam_dict[event.guild_id]
        except KeyError:
            AM_antispam = automod.AntiSpamSystem(guid=event.guild_id)
            anti_spam_dict[event.guild_id]: automod.AntiSpamSystem = AM_antispam
        
        if anti_spam_dict[event.guild_id].is_allowed(event.author.id):
            return True

        # Check if the user is an admin, we do this after we check if they're guilty so we don't spam discord with requests
        is_admin = await permissions.check(hikari.Permissions.ADMINISTRATOR, member=event.member, guid=event.guild_id)
        if not is_admin:
            await antispam.punish(event)

        server_msg = automod.gen_user_warning_embed(
            warning_title="AntiSpam Check Failed"
        )
        await event.message.respond(server_msg)

    async def punish(event: hikari.GuildMessageCreateEvent):
        success = False
        try:
            await event.message.delete()
            success = True
        except (hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError, hikari.UnauthorizedError):
            pass
        return success

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))