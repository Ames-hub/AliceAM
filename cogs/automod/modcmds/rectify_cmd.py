from .group import mod_group
import lightbulb, hikari

@mod_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='case_id',
    description='The case ID of the image to rectify.',
    required=True,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.option(
    name='reason',
    description='The reason for rectifying the image.',
    required=False,
    default="No reason provided.",
    type=hikari.OptionType.STRING
)
@lightbulb.option(
    name='punish',
    description='The new punishment to apply to the user.',
    required=True,
    type=hikari.OptionType.STRING,
    choices=[
        'kick',
        'ban',
        'mute',
        'warn',
        'none'
    ]
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
)
@lightbulb.command(name="rectify", description="Rectify an image scan.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def rectify_cmd(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond("This command is not implemented yet.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
