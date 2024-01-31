from library.storage import memory
from library.botapp import bot
from .group import antislur_group
import lightbulb, hikari, logging

@antislur_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='enabled',
    description='Enable (True) or disable (False) the antislur system.',
    required=True, # This is an example of an option you could add.
    type=hikari.OptionType.BOOLEAN
)
\
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.command(name="toggle", description="Turn off or On the antislur system.")
# use "slash sub command" opposed to "slash command" if it is in a group
@lightbulb.implements(lightbulb.SlashSubCommand)
async def antislur_toggle_command(ctx: lightbulb.SlashContext) -> None:
    enabled:bool = ctx.options.enabled

    guild = memory.guild(ctx.guild_id)
    try:
        success = guild.set_antislur_enabled(bool(enabled))
    except TypeError:
        await ctx.respond("Input was not True or False? Please try again.")
        return
    
    if not success:
        logging.error(f"Was not able to set antislur protection to {success}!")
        await ctx.respond("Failed to set AntiSlur protection. Please try again.")
        return
    
    await ctx.respond(f"AntiSlur Protection is now *{'online' if enabled else 'offline'}*.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))