from library.storage import PostgreSQL
from .group import antiswear_group
import lightbulb, hikari, logging

@antiswear_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='enabled',
    description='Enable (True) or disable (False) the antiswear system.',
    required=True,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
    )
@lightbulb.command(name="toggle", description="Turn off or On the antiswear system.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def antiswear_toggle_command(ctx: lightbulb.SlashContext) -> None:
    enabled:bool = ctx.options.enabled

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        success = guild.set_antiswear_enabled(bool(enabled))
    except TypeError:
        await ctx.respond("Input was not True or False? Please try again.")
        return
    
    if not success:
        logging.error(f"Was not able to set antiswear protection to {success}!")
        await ctx.respond("Failed to set AntiSwear protection. Please try again.")
        return
    
    await ctx.respond(f"AntiSwear Protection is now *{'online' if enabled else 'offline'}*.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
