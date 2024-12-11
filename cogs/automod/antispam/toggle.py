from library.storage import PostgreSQL
from .group import antispam_group
import lightbulb, hikari, logging

@antispam_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='enabled',
    description='Enable (True) or disable (False) the AntiSpam system.',
    required=True,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(name="toggle", description="Turn off or On the AntiSpam system.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def anti_spam_toggle_command(ctx: lightbulb.SlashContext) -> None:
    enabled:bool = ctx.options.enabled

    # Let users disable, but not enable the system.
    # TODO: Implement the Antispam system properly.
    if enabled is True:
        await ctx.respond("Apologies, but this system has not been fully implemented yet. Please try again later.")
        return

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        success = guild.set_antispam_enabled(bool(enabled))
    except TypeError:
        await ctx.respond("Input was not True or False? Please try again.")
        return
    
    if not success:
        logging.error(f"Was not able to set AntiSpam protection to {success}!")
        await ctx.respond("Failed to set AntiSpam protection. Please try again.")
        return
    
    warning_note = "" if not enabled else "\n**Warning:** AntiSpam protection is quite experimental. Expect false-positives, but not errors."
    await ctx.respond(f"AntiSpam Protection is now *{'online' if enabled else 'offline'}*.{warning_note}")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
