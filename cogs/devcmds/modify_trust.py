from library.storage import PostgreSQL, var
from library.botapp import bot
import lightbulb
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='target',
    default=None,
    type=hikari.OptionType.USER,
    description='The target user to modify the trust level of',
    required=False,
)
@lightbulb.option(
    name='value',
    type=str,
    description='The value to set the trust level to, using + or - to increase or decrease the trust level',
    required=True,
)
@lightbulb.command(name="dev_modify_trust", description="Modify the trust-distrust ratio of a user", hidden=True, pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def devcmds(ctx: lightbulb.PrefixContext, value: str, target: hikari.User) -> None:
    if ctx.author.id not in var.get('bot_admins'):
        return

    if ctx.guild_id is not None:
        await ctx.event.message.delete()  # Delete the command message

    operator = value[0]
    value = value[1:]

    if target is None:
        target = ctx.author

    successful = PostgreSQL.users(target.id).modify_trust(
        value=int(value),
        operator=operator,
        apply_cooldown=False
    )

    embed = (
        hikari.Embed(
            title="Trust Level Modified",
            description=f"Successfully modified trust level for {target.mention}.",
            color=0x00FF00
        )
        if successful
        else hikari.Embed(
            title="Trust Modification Failed",
            description=f"Failed to modify trust level for {target.mention}.",
            color=0xFF0000
        )
    )

    await ctx.author.send(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
