from library.storage import PostgreSQL
from .group import config_group
import lightbulb, hikari

@config_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='channel',
    description='The channel to log actions to.',
    required=True,
    type=hikari.OptionType.CHANNEL
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
)
@lightbulb.command(name="audit_channel", description="Set the log channel for the server.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def audit_log_set(ctx: lightbulb.SlashContext) -> None:
    channel:hikari.GuildChannel = ctx.options.channel

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        if channel.type != hikari.ChannelType.GUILD_TEXT:
            raise TypeError

        success = guild.set_auditlog_channel_id(int(channel))
    except TypeError:
        await ctx.respond("The Input was not a text-channel. Please try again.")
        return

    if success:
        await ctx.respond(f"Successfully set the audit log channel to {channel.mention}.")
    else:
        await ctx.respond("An error occurred while setting the audit log channel. Please try again.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
