from library.storage import PostgreSQL
from library.botapp import bot, permissions
import lightbulb
import datetime
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='user',
    description='The user to check the trust score of.',
    required=False,
    default=None,
    type=hikari.OptionType.USER
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.command(name="trust", description="What is your trust-distrust ratio score? Find out!")
@lightbulb.implements(lightbulb.SlashCommand)
async def get_trust_score(ctx: lightbulb.SlashContext) -> None:
    was_user_requested = False
    user_requested:hikari.User = ctx.options.user

    if user_requested is not None:
        # Check if the author is a moderator
        is_mod = await permissions.check(
            uuid=ctx.author.id,
            guid=ctx.guild_id,
            permission=hikari.Permissions.MANAGE_MESSAGES
        )
        if not is_mod:
            await ctx.respond("You must be a moderator to check another user's trust score.", flags=hikari.MessageFlag.EPHEMERAL)
            return
        else:
            check_user = PostgreSQL.users(user_requested.id)
            was_user_requested = True
    else:
        check_user = PostgreSQL.users(ctx.author.id)

    trust_ratio = check_user.get_trust()

    def trust_reword(ratio, username:str|None):
        if username is not None:
            if username == bot.d['bot_username']:
                return "I'd say I'm quite trustworthy, wouldn't you agree? :D"

        infraction_count = check_user.get_infraction_count()
        if ratio >= 100:
            if infraction_count == 0:
                return "Spotless record!"
            else:
                if infraction_count < 20:
                    return "Reformed, and trustworthy as of present."
                else:
                    return "Reformed troublemaker."
        elif ratio >= 90:
            if infraction_count == 0:
                return "Consistently Trustworthy"
            else:
                if infraction_count < 15:
                    return "Mostly Trustworthy, with a few hiccups."
                else:
                    return "Trustworthy, but has a history of trouble."
        elif ratio >= 70:
            if infraction_count < 15:
                return "Trustworthy"
            else:
                return "Trustworthy, recently reformed."
        elif ratio >= 50:
            if infraction_count <= 5:
                return "Uncertain? Not enough data."
            else:
                if infraction_count >= 6:
                    return "Untrustworthy, but has potential."
                else:
                    return "Untrustworthy, potentially reformed."
        elif ratio < 50:
            return "Potential Trouble Source. AI methods implemented to identify harmful behavior." # Messages will be looked at by an AI without context.
        elif ratio <= 40:
            return "Trouble source. Messages will be monitored."  # Below 40, messages will be logged and sent with context to an AI.
        elif ratio <= 10:
            return "Trouble source. Will not follow rules. Likely troll."

    # Finds the amount for the trust ratio until it reaches 100.
    distrust_ratio = 100 - trust_ratio

    if was_user_requested:
        if user_requested.username == bot.d['bot_username']:
            # Vanity check
            trust_ratio = 100
            distrust_ratio = 0

    embed = (
        hikari.Embed(
            title=f"Trust Score : {trust_ratio}-{distrust_ratio}",
            description=trust_reword(trust_ratio, None if not was_user_requested else user_requested.username),
            color=bot.d['colourless'],
            timestamp=datetime.datetime.now().astimezone()
        )
        .set_author(
            name=ctx.author.username if not was_user_requested else user_requested.username,
            icon=ctx.author.avatar_url if not was_user_requested else user_requested.avatar_url
        )
        .set_footer(text=f"Alice's Trust-Distrust Ratio of {'you' if not was_user_requested else user_requested.username}.")
    )

    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
