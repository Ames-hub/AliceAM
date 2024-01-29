import lightbulb
import hikari
import dotenv
import os

dotenv.load_dotenv("secrets.env")
INTENTS = hikari.Intents.ALL

TOKEN = os.environ.get("TOKEN")
if TOKEN == None:
    from main import introduction
    introduction()
    print("Please restart the bot.")
    exit()
bot = lightbulb.BotApp(
    token=TOKEN,
    prefix="//",
    intents=INTENTS
)
bot.d['colourless'] = hikari.Colour(0x2b2d31)

class permissions:
    async def check(
            permission, 
            member: hikari.Member = None, guild: hikari.Guild = None, # Method 1
            uuid=str or None, guid=str or None # Method 2
            ):

        '''
        A Permission checker. this will return if the user in the guild is allowed to issue a certain command or not
        according to discord permissions policy. This will return a boolean value. True if the user is allowed, False if not.

        Example:
        ```
        if botlib.api.checkif.permitted(permission=hikari.Permissions.BAN_MEMBERS, uuid=member.id, guid=guild.id) == False:
            ctx.respond("No.")
            return
        ```
        '''

        if guild != None:
            guid = guild.id
        if member != None:
            uuid = member.id
            guid = member.guild_id

        if guid == None:
            raise ValueError("No guild ID was provided. Please provide a guild ID.")

        try:
            checked_member = await bot.rest.fetch_member(hikari.Snowflake(guid), hikari.Snowflake(uuid))
        except:
            return False

        try:
            checked_member = checked_member.get_top_role()
        except:
            return False

        if type(permission) != list:
            allowed = permission in checked_member.permissions
        else:
            for perm in permission:
                allowed = perm in checked_member.permissions
                if allowed == True:
                    break
        # If the member is the owner of the guild, they are allowed to do anything
        try:
            if allowed == False:

                allowed = hikari.Permissions.ADMINISTRATOR in checked_member.permissions

                if allowed != False:
                    return allowed # If the member is an admin, return True

                if guid != None:
                    guild = await bot.rest.fetch_guild(hikari.Snowflake(guid))
                    if str(guild.owner_id) in str(member.id) or str(guild.owner_id) in str(uuid):
                        allowed = True
        except:
            pass

        try:
            return allowed
        except:
            return False # Return false on any exception. This is JUST in case. It likely won't except
            # but it's better to be safe than sorry.