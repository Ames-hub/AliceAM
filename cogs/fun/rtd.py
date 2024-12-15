# This is an example plugin for you to learn from how to get started with plugins.
# BASICALLY, you follow standard Hikari-Lightbulb syntax when making plugins/commands.

from library.botapp import bot
import lightbulb
import random
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='include_results',
    description="Whether to include the individual die rolls in the output.",
    required=False,
    default=False,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.option(
    name='modifier',
    description="The modifier to add to the roll.",
    required=False,
    default=0,
    type=hikari.OptionType.INTEGER
)
@lightbulb.option(
    name='dice',
    description="The number of dice to roll.",
    required=False,
    default=1,
    type=hikari.OptionType.INTEGER
)
@lightbulb.option(
    name='sides',
    description="The largest die to roll.",
    required=False,
    default=6,
    type=hikari.OptionType.INTEGER
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=2, uses=1)
@lightbulb.command(name="rtd", description="Roll the dice! See your luck.")
@lightbulb.implements(lightbulb.SlashCommand)
async def rtd_cmd(ctx: lightbulb.SlashContext) -> None:
    sides = ctx.options.sides
    modifier = ctx.options.modifier
    dice = ctx.options.dice
    include_results = ctx.options.include_results

    if sides < 2:
        await ctx.respond("You need to roll a die with at least 2 sides.")
        return

    if dice < 1:
        await ctx.respond("You need to roll at least one die.")
        return

    if sides > 9999999999:
        await ctx.respond("I spawned that die, and it crushed me. :( Please roll a die with less than 10 billion sides.")
        return

    results = [random.randint(1, sides) for _ in range(dice)]
    total = sum(results) + modifier

    results_str = " + ".join(map(str, results))
    if modifier != 0:
        results_str += f" + {modifier}"

    await ctx.respond(f"The result of rolling {dice}D{sides} + {modifier} is {total} {'(' + results_str + ')' if include_results else ''}")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
