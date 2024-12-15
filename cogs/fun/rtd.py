# This is an example plugin for you to learn from how to get started with plugins.
# BASICALLY, you follow standard Hikari-Lightbulb syntax when making plugins/commands.

from library.botapp import bot
import lightbulb
import random
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='sides',
    description="The larged die to roll.",
    required=False,
    default=6,
    type=hikari.OptionType.INTEGER
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=2, uses=1)
@lightbulb.command(name="rtd", description="Roll the dice! See your luck.")
# use "slash sub command" opposed to "slash command" if it is in a group
@lightbulb.implements(lightbulb.SlashCommand)
async def rtd_cmd(ctx: lightbulb.SlashContext) -> None:
    sides = ctx.options.sides

    if sides < 2:
        await ctx.respond("You need to roll a die with at least 2 sides.")
        return

    result = random.randint(1, sides)

    if result != sides:
        await ctx.respond(f"The D{sides} rolled a {result}")
    else:
        await ctx.respond(f"✨ *The D{sides} rolled maximum, a {result}!* ✨")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
