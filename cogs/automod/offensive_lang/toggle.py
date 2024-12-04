from library.storage import PostgreSQL
from .group import ofd_lang_group
import lightbulb, hikari, logging

@ofd_lang_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='enabled',
    description='Enable (True) or disable (False) the offensive language detection / civility system.',
    required=True,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
    )
@lightbulb.command(name="toggle", description="Turn off or On the offensive language detection / civility system.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def ofd_lang_toggle_command(ctx: lightbulb.SlashContext) -> None:
    enabled:bool = ctx.options.enabled
    guild = PostgreSQL.guild(ctx.guild_id)

    try:
        success = guild.set_civility_filter_enabled(bool(enabled))
    except TypeError:
        await ctx.respond("Input was not True or False? Please try again.")
        return
    
    if not success:
        logging.error(f"Was not able to set Civility protection to {success}!")
        await ctx.respond("Failed to set Civility protection. Please try again.")
        return
    
    await ctx.respond(
        f"Civility Enforcement is now *{'online' if enabled else 'offline'}*."
        f"{'\nCAUTION: Civility Enforcement is experimental and is less than 80% accurate.' if enabled else ''}")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
