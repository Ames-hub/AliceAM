from library.storage import var
from library.botapp import bot
import lightbulb
import secrets
import hikari

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.add_checks(
    lightbulb.dm_only
)
@lightbulb.command(name="addselfadmin", description="Add yourself as an admin to the bot. Requires 2FA", hidden=True, pass_options=True)
@lightbulb.implements(lightbulb.PrefixCommand)
async def devcmds(ctx: lightbulb.PrefixContext) -> None:
    bot_admin_list: list = var.get('bot_admins')
    if ctx.author.id in bot_admin_list:
        embed = (
            hikari.Embed(
                title="Error",
                description="You are already an admin.",
                color=hikari.Color(0xff0000)
            )
        )
        await ctx.author.send(embed)
        return

    # Prints a random 2FA Code
    code = secrets.token_hex(6)
    print(f"2FA Code: {code}")
    embed = (
        hikari.Embed(
            title="2FA Code",
            description="To complete this action, you must provide a 2FA code.\nCheck the console for the code.",
            color=hikari.Color(0x00ff00)
        )
    )
    await ctx.author.send(embed)

    # Wait for the user to provide the 2FA code
    try:
        response = await bot.wait_for(hikari.MessageCreateEvent, timeout=30.0, predicate=lambda m: m.author.id == ctx.author.id)
        if response.message.content == code:
            bot_admin_list.append(int(ctx.author.id))
            success = var.set('bot_admins', value=bot_admin_list)
            if success:
                embed = (
                    hikari.Embed(
                        title="Success",
                        description="You have been added as an admin.",
                        color=hikari.Color(0x00ff00)
                    )
                    .add_field(
                        name="Getting started",
                        value="You can now use the prefix command `//dev`"
                              "This lets you see the commands you can use to manage the bot."
                    )
                )
                await ctx.author.send(embed)
            else:
                embed = (
                    hikari.Embed(
                        title="Error",
                        description="The 2FA was right, but we still failed to add you as an admin.",
                        color=hikari.Color(0xff0000)
                    )
                )
                await ctx.author.send(embed)
            return
        else:
            embed = (
                hikari.Embed(
                    title="Error",
                    description="The 2FA code was incorrect.",
                    color=hikari.Color(0xff0000)
                )
            )
            await ctx.author.send(embed)
            return
    except TimeoutError:
        embed = (
            hikari.Embed(
                title="Error",
                description="You took too long to respond.",
                color=hikari.Color(0xff0000)
            )
        )
        await ctx.author.send(embed)
        return

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
