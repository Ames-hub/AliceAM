from library.storage import var
from library.botapp import bot
import lightbulb
import hikari
import os

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.command(name="dev", description="List all development commands", hidden=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def devcmds(ctx: lightbulb.PrefixContext) -> None:
    if ctx.author.id not in var.get('bot_admins'):
        return

    if ctx.guild_id is not None:
        await ctx.event.message.delete()  # Delete the command message

    embed = hikari.Embed(
        title="Developer Commands",
        description="Here are the commands that you can use to manage the bot.",
        color=0x00FF00
    )

    pathwalk = os.walk('cogs/devcmds')
    prefix = var.get('prefix')
    # Excluding __init__.py and __pycache__, its self, and only listing .py files, we will find the command names
    for root, _, files in pathwalk:
        for file in files:
            if file.endswith('.py') and not file.startswith('__') and file != 'list_cmds.py':
                # Open the file as read-only
                with open(f"{root}/{file}", 'r') as f:
                    # Read the file
                    lines = f.readlines()
                    # counts the amount of times the command decorator is found, and what line it is on
                    cmd_count = {}
                    for line_num, line in enumerate(lines):
                        if '@lightbulb.command' in line:
                            cmd_count[line_num] = line

                    # Get the command name and description
                    for line_num, line in cmd_count.items():
                        line = str(line).strip().replace("@lightbulb.command(", "")
                        is_doublequote = line[5] == '"'
                        name_index_start = 6
                        name_index_end = line.index('"', 7) if is_doublequote else line.index("'", 7)
                        cmd_name = line[name_index_start:name_index_end]

                        if is_doublequote:
                            quote = '"'
                        else:
                            quote = "'"

                        line = line.replace(f'name={quote}{cmd_name}{quote}, ', '')
                        desc_index_start = line.index('description=') + 13
                        desc_index_end = line.index(quote, desc_index_start)
                        cmd_desc = line[desc_index_start:desc_index_end]

                        embed.add_field(
                            name=f"{prefix}{cmd_name}",
                            value=f"{cmd_desc}",
                            inline=False
                        )

    await ctx.author.send(embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
