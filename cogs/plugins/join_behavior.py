from library.botapp import bot
import lightbulb
import hikari

async def on_guild_join(event: hikari.GuildJoinEvent=None, sys_channel_id=None) -> None:
    if sys_channel_id is None:
        sys_channel_id = event.get_guild().system_channel_id

    if sys_channel_id is None:
        return  # No system channel to send the message to

    embed = (
        hikari.Embed(
            title='AliceAM, at your service.',
            description='Thank you for inviting me to your server!\n'
                        'AliceAM is a Moderation bot designed to help keep your server safe and clean where other bots would fail to do so.',
            color=0x00FF00  # Green color
        )
        .add_field(
            name='Getting Started',
            value="This guide will help you get started with AliceAM.\n"
        )
        .add_field(
            name="Log Configuration",
            value='To get started, lets first set the audit logging channel for your server!\n'
                  'To do this, run the app command `/config audit_channel`'
        )
        .add_field(
            name='Moderation features',
            # TODO: IMPLEMENT CONFIG SETDEFAULT COMMAND AND HELP MODERATION COMMAND. HIGH PRIORITY
            value='AliceAM has a wide variety of moderation features to help keep your server clean and safe.\n\n'
            "I'd recommend now running `help moderation` to get a full explanation of moderation commands, and which ones you'd like to enable.\n\n"
            "*However, if you'd like to skip this step, simply run `/config setdefault` to set the default moderation settings.*"
        )
        .add_field(
            name="Crowdsourced Learning",
            value="AliceAM is a learning moderation bot, and it learns primarily from your feedback. "
                  "You can help it learn by reacting with thumbs up or thumbs down when prompted to express your opinion on the algorithm's prediction."
        )
        .add_field(
            name='Support Resources',
            value='If you need any help, feel free to reach out to the support team or visit our [support server](https://discord.gg/HkKAsgvCzt) for help.'
                  '\n\nAlternatively, you can [visit our github page](https://github.com/Ames-hub/AliceAM) here and open an issue.'
        )
    )

    await bot.rest.create_message(
        sys_channel_id,
        embed
    )

class bot_plugin(lightbulb.Plugin):
    @staticmethod
    @bot.listen(hikari.GuildJoinEvent)
    async def listener(event: hikari.GuildJoinEvent) -> None:
        await on_guild_join(event)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
