from library.storage import PostgreSQL
from .group import config_group
import lightbulb, hikari

@config_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='enabled',
    description='Whether to enable or disable the image scanner.',
    required=True,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
)
@lightbulb.command(name="audit_toggle", description="Set if the bot should log audit logs.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def audit_log_toggle(ctx: lightbulb.SlashContext) -> None:
    enabled:bool = ctx.options.enabled

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        success = guild.set_auditlog_enabled(bool(enabled))
    except TypeError:
        await ctx.respond("The Input was not a boolean value.")
        return

    if success:
        await ctx.respond(f"Successfully {'enabled' if enabled else 'disabled'} the auditing.")
    else:
        await ctx.respond(f"Failed to toggle the auditing.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
