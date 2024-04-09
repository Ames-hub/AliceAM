# This is an example plugin for you to learn from how to get started with plugins.
# BASICALLY, you follow standard Hikari-Lightbulb syntax when making plugins/commands.

from library.botapp import bot
import lightbulb
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
# enter the lines below this with options for the command
# @lightbulb.option(
#     name='doDM',
#     description="Should we DM you the credits?"
#     required=False, # This is an example of an option you could add.
#     default=False,
#     type=hikari.OptionType.BOOLEAN
# )
# Adds a cooldown to the command (optional)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.command(name="credits", description="Who helped make me? Find out here!")
# use "slash sub command" opposed to "slash command" if it is in a group
@lightbulb.implements(lightbulb.SlashCommand)
async def credit_command(ctx: lightbulb.SlashContext) -> None:
    # do_dm = ctx.options.doDM
    # An example of how you'd get the value of an option.
    embed = (
        hikari.Embed(
              title="Credits",
              description="Here are the people who helped make me!",
              color=bot.d['colourless'],
        )
        .set_footer(
            text='https://github.com/Ames-hub/AliceAM', # add a new line and link to your own repository if desired
        )
        .add_field(
            name="Original Developer",
            value="**FriendlyFox.exe**"
        )
        # .add_field(
        #     name="Developer",
        #     value="**YOUR NAME HERE**"
        # ) # If you make your own version of the bot, you can add yourself here.
    )
    
    await ctx.respond(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
