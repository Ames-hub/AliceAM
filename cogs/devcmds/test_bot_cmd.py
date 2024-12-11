from library.storage import var
from library.botapp import bot
import lightbulb
import traceback
import hikari

from cogs.plugins.join_behavior import on_guild_join

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='targetcmd',
    type=str,
    description='The command to test.',
    required=True,
    choices=[
        'on_guild_join',
    ]
)
@lightbulb.command(name="dev_test_cmd", description="Test a command that'd usually be difficult to trigger.", hidden=True, pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def devcmds(ctx: lightbulb.PrefixContext, targetcmd: str) -> None:
    if ctx.author.id not in var.get('bot_admins'):
        return

    if ctx.guild_id is not None:
        await ctx.event.message.delete()  # Delete the command message

    if targetcmd == 'on_guild_join':
        try:
            # noinspection PyTypeChecker
            await on_guild_join(
                # This is a mock event object
                sys_channel_id=ctx.channel_id
            )
        except Exception as err:
            await ctx.respond(
                hikari.Embed(
                    title='Command Test',
                    description=f'Tested command: `{targetcmd}`\n\nError: {err}',
                    color=bot.d['colourless'],
                )
                .add_field(name='Error', value=f'```{traceback.format_exc()}```')
                .set_footer(text=f'Requested by {ctx.author.username}', icon=ctx.author.avatar_url)
            )
            return

    embed = (
        hikari.Embed(
            title='Command Test',
            description=f'Tested command: `{targetcmd}`',
            color=bot.d['colourless'],
        )
        .set_footer(text=f'Requested by {ctx.author.username}', icon=ctx.author.avatar_url)
    )

    await ctx.author.send(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
