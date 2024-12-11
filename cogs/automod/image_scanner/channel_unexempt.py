from library.storage import PostgreSQL
from .group import imgscanner_group
import lightbulb, hikari, logging

@imgscanner_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name='channel',
    description='The channel to unexempt from Image Scanning.',
    required=False,
    default=None,
    type=hikari.OptionType.CHANNEL
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS),
)
@lightbulb.command(name="unexempt", description="Unexempt a channel from Image Scanning.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def scanner_exempt_command(ctx: lightbulb.SlashContext) -> None:
    channel:hikari.GuildChannel = ctx.options.channel
    if not channel:
        channel = ctx.bot.cache.get_guild_channel(ctx.channel_id)

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        if channel.type not in [
            hikari.ChannelType.GUILD_TEXT,
            hikari.ChannelType.GUILD_PRIVATE_THREAD,
            hikari.ChannelType.GUILD_PUBLIC_THREAD,
            hikari.ChannelType.GUILD_FORUM,
            hikari.ChannelType.GUILD_NEWS_THREAD,
            hikari.ChannelType.GUILD_NEWS
        ]:
            raise TypeError
        success = guild.remove_exempt_img_scan_channel(int(channel.id))
    except TypeError:
        await ctx.respond("The input was not a valid channel. Please try again.")
        return

    if not success:
        logging.error(f"Failed to set Image Scanner exemption status for {channel.id} in {ctx.guild_id}")
        await ctx.respond("Failed to set exemption status for that channel.")
        return

    await ctx.respond(f"Successfully unexempted {channel.mention} from Image Scanning.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
