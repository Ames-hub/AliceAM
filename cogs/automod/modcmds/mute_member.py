from datetime import datetime, timedelta
from library.automod import automod
from .group import mod_group
import lightbulb, hikari

@mod_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    name='member',
    description='The member to mute.',
    required=True,
    type=hikari.OptionType.USER
)
@lightbulb.option(
    name='hours',
    description='How many hours the user should be muted for.',
    required=False,
    type=hikari.OptionType.INTEGER,
)
@lightbulb.option(
    name='days',
    description='How many days the user should be muted for.',
    required=False,
    type=hikari.OptionType.INTEGER,
)
@lightbulb.option(
    name='reason',
    description='The reason for muting the user.',
    required=False,
    default="No reason provided.",
    type=hikari.OptionType.STRING
)
@lightbulb.option(
    name='delhours',
    description='How many hours worth of messages to delete.',
    required=False,
    default=None,
    type=hikari.OptionType.INTEGER,
    # Max value is 2 weeks (336 hours). Beyond that, it's not possible to delete messages.
    max_value=336
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
)
@lightbulb.command(name="mute", description="Mute a member for a specified amount of time.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def mute_cmd(ctx: lightbulb.SlashContext) -> None:
    victim = ctx.options.member
    hours = ctx.options.hours
    days = ctx.options.days
    reason = ctx.options.reason
    delhours = ctx.options.delhours

    if hours is None and days is None:
        # Defaults to 3 days
        last_to = (datetime.now() + timedelta(days=3))
    else:
        last_to = (datetime.now() + timedelta(hours=hours, days=days))

    result = await automod.punish(
        action="mute",
        offender_id=victim.id,
        guild_id=ctx.guild_id,
        reason=reason,
        mute_lasts_to=last_to,
    )
    success = result['success']
    case_id = result['new_case_id']

    if success:
        embed = hikari.Embed(
            title="Member Muted",
            description=f"{victim.mention} has been muted until <t:{last_to}:F>\nCase ID: {case_id}",
            color=hikari.Color(0x00FF00)
        )
    else:
        embed = hikari.Embed(
            title="Error",
            description=f"An error occurred while trying to mute {victim.mention}.",
            color=hikari.Color(0xFF000)
        )

    await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

    if delhours is not None:
        await automod.batch_delete_messages(
            channel_id=ctx.channel_id,
            del_hours=delhours
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
