from library.encrpytion import encryption
from lightbulb.ext import tasks
from library.storage import var
import lightbulb
import hikari

keys = encryption()

INTENTS = hikari.Intents.ALL

bot = lightbulb.BotApp(
    token=keys.decrypt(var.get(file='settings.json', key='token')),
    prefix=var.get(file='settings.json', key='prefix'),
    intents=INTENTS
)
tasks.load(bot)
bot.d['colourless'] = hikari.Colour(0x2b2d31)
bot.d['spam_logs'] = {}
bot.d['spammers_punished'] = {}

class permissions:
    @staticmethod
    async def check(
            permission,
            member: hikari.Member = None, guild: hikari.Guild = None,  # Method 1
            uuid=str or None, guid=str or None  # Method 2
    ):

        """
        A Permission checker. this will return if the user in the guild is allowed to issue a certain command or not
        according to discord permissions policy. This will return a boolean value. True if the user is allowed, False if not.

        Example:
        ```
        if botlib.api.checkif.permitted(permission=hikari.Permissions.BAN_MEMBERS, uuid=member.id, guid=guild.id) == False:
            ctx.respond("No.")
            return
        ```
        """
        # Prevents circular imports if imported here
        from library.cache import cache
        # Assume for safety
        allowed = False

        if guild is not None:
            guid = guild.id
        if member is not None:
            uuid = member.id
            guid = member.guild_id

        if guid is None:
            raise ValueError("No guild ID was provided. Please provide a guild ID.")

        cached_perms = cache.get_permissions(uuid, guid)
        if cached_perms == -1:
            try:
                checked_member = await bot.rest.fetch_member(hikari.Snowflake(guid), hikari.Snowflake(uuid))
            except:
                return False

            try:
                checked_member = checked_member.get_top_role()
                permissions = checked_member.permissions
                cache.cache_perms(uuid, guid, permissions)
            except:
                return False
        else:
            permissions = cached_perms

        if not isinstance(permission, list):
            # If `permission` is not a list, it means it's a single permission.
            # In this case, check if this single permission is in the `permissions`.
            # The result (True or False) is stored in the `allowed` variable.
            allowed = permission in permissions
        else:
            for perm in permission:
                # If `permission` is a list, it means there are multiple permissions to check for.
                # Iterate over each permission in the `permission` list.
                allowed = perm in permissions
                if allowed:
                    break
        # If the member is the owner of the guild, they are allowed to do anything
        try:
            if not allowed:

                allowed = hikari.Permissions.ADMINISTRATOR in permissions

                if allowed is not False:
                    return allowed  # If the member is an admin, return True

                # If the member is the owner of the guild, they are allowed to do anything
                if guid is not None:
                    guild = await bot.rest.fetch_guild(hikari.Snowflake(guid))
                    if str(guild.owner_id) in str(member.id) or str(guild.owner_id) in str(uuid):
                        allowed = True
        except:
            pass

        try:
            return allowed
        except:
            return False  # Return false on any exception. This is JUST in case. It likely won't except
            # but it's better to be safe than sorry.
