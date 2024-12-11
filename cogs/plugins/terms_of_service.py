from library.botapp import bot
import lightbulb
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=2, uses=1)
@lightbulb.command(name="tos", description="View the terms of service.")
# use "slash sub command" opposed to "slash command" if it is in a group
@lightbulb.implements(lightbulb.SlashCommand)
async def credit_command(ctx: lightbulb.SlashContext) -> None:
    # do_dm = ctx.options.doDM
    # An example of how you'd get the value of an option.
    embed = (
        hikari.Embed(
            title="Terms of Service",
            description="To view the Terms of Service, please visit:\n"
                        "https://pastebin.com/iE13b8fA",
            color=bot.d['colourless'],
        )
    )

    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
