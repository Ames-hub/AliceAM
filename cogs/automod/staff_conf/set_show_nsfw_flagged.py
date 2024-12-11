import logging

from library.storage import PostgreSQL
from .group import config_group
import lightbulb, hikari

@config_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name='hide',
    description='Should we hide the flagged images when requested?',
    required=True,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
)
@lightbulb.command(name="show_flagged", description="Toggle whether to show flagged images when requested.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def set_show_flagged_nsfw(ctx: lightbulb.SlashContext) -> None:
    do_show:bool = ctx.options.hide

    guild = PostgreSQL.guild(ctx.guild_id)
    try:
        success = guild.set_do_censor_flagged_nsfw(do_show)
        if success:
            await ctx.respond(f"Flagged images are now to {'be shown' if do_show else 'not be shown'} in audit logs.")
        else:
            raise TypeError("An error occurred while trying to set the show flagged NSFW images.")
    except TypeError as err:
        await ctx.respond(f"An error occurred while trying to do that!")
        logging.error(
            f"An error occurred while trying to set the show flagged NSFW images to {do_show}: {err}",
            exc_info=err
        )
        return

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
