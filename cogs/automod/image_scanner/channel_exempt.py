from library.storage import PostgreSQL
from .group import imgscanner_group
import lightbulb, hikari, logging

@imgscanner_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='channel',
    description='The channel to exempt from Image Scanning.',
    required=False,
    default=None,
    type=hikari.OptionType.CHANNEL
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_CHANNELS),
)
@lightbulb.command(name="exempt", description="Exempt a channel from Image Scanning.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def scanner_exempt_command(ctx: lightbulb.SlashContext) -> None:
    channel:hikari.GuildChannel = ctx.options.channel
    if not channel:
        channel = ctx.bot.cache.get_guild_channel(ctx.channel_id)

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        success = guild.add_exempt_img_scan_channel(int(channel.id))
    except TypeError:
        await ctx.respond("Input was not True or False? Please try again.")
        return
    
    if not success:
        logging.error(f"Failed to set Image Scanner exemption status for {channel.id} in {ctx.guild_id}")
        await ctx.respond("Failed to set exemption status for that channel.")
        return

    if success == -1:
        await ctx.respond(f"{channel.mention} is already exempt from Image Scanning.")
        return
    await ctx.respond(f"Successfully exempted {channel.mention} from Image Scanning.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
