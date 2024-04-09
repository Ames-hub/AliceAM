from library.botapp import bot, permissions
from library.automod import automod
from library.storage import memory
import lightbulb
import hikari
import typing
import time

# Same colour as the embed box
colourless = bot.d['colourless']
anti_spam_dict = {}

class AntiSpamSystem:
    def __init__(self, messages_allowed: int = 2, time_window_seconds: int = 5, punishment_cooldown_seconds: int = 10):
        self.messages_allowed = messages_allowed
        self.time_window_seconds = time_window_seconds
        self.punishment_cooldown_seconds = punishment_cooldown_seconds
        self.user_timestamps: typing.Dict[int, typing.List[float]] = {}
        self.punished_users: typing.Dict[int, float] = {}

    def is_allowed(self, user_id: int) -> bool:
        current_time = time.time()

        # Check if the user is currently on cooldown
        if user_id in self.punished_users and current_time - self.punished_users[user_id] < self.punishment_cooldown_seconds:
            return False

        # Initialize timestamps for a new user if not present
        timestamps = self.user_timestamps.setdefault(user_id, [])

        # Remove timestamps older than the allowed time window
        timestamps = [timestamp for timestamp in timestamps if timestamp >= current_time - self.time_window_seconds]

        # Check if the number of messages sent by the user in the allowed time window is less than the limit
        if len(timestamps) < self.messages_allowed:
            timestamps.append(current_time)
            return True
        else:
            # Punish the user and record the punishment time
            self.punished_users[user_id] = current_time
            return False

antispam_system = AntiSpamSystem()

class antispam(lightbulb.Plugin):
    @bot.listen()
    async def listener(event: hikari.GuildMessageCreateEvent) -> bool:
        if event.author.is_bot:
            return False
        
        # Check if the guild has antispam enabled
        guild_enabled = memory.guild(event.guild_id).get_antispam_enabled()
        if guild_enabled is False:
            return False
        
        allow_send = antispam_system.is_allowed(event.author.id)

        # Check if the user is an admin, we do this after we check if they're guilty so we don't spam discord with requests
        is_admin = await permissions.check(hikari.Permissions.ADMINISTRATOR, member=event.member, guid=event.guild_id)
        if not is_admin and not allow_send:
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
