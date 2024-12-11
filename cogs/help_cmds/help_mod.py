from library.botapp import bot
from .group import help_group
import lightbulb, hikari

@help_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='information',
    description='What information would you like to know about the bot?',
    required=True,
    type=hikari.OptionType.STRING,
    choices=[
        "antispam",
        "antiswear",
        "antislur",
        "auditlog",
        "civility filter",
        "image filter",
        "distrust system",
    ],
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.command(name="moderation", description="Get information about the moderation modules.", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def help_cmd(ctx: lightbulb.SlashContext, information) -> None:
    if information == "antispam":
        embed = (
            hikari.Embed(
                title="Antispam",
                description="The antispam module is a module that is designed to prevent users from spamming the chat.",
                color=bot.d['colourless']
            )
            .add_field(
                name="Under Development",
                value="This module is currently under development, and does not work as intended.",
            )
            .add_field(
                name="Accuracy",
                value="This module is extremely inaccurate, and its actions consist mostly of false positives.\n"
                      "It is not recommended to use this module.",
            )
        )
    elif information == "antiswear":
        embed = (
            hikari.Embed(
                title="Antiswear",
                description="The antiswear module is a module that is designed to prevent users from using swear words in the chat.",
                color=bot.d['colourless'],
            )
            .add_field(
                name="Accuracy",
                value="This module is quite accurate, and has few false positives.",
            )
        )
    elif information == "antislur":
        embed = (
            hikari.Embed(
                title="Antislur",
                description="The antislur module is a module that is designed to prevent users from using slurs in the chat.",
                color=bot.d['colourless'],
            )
            .add_field(
                name="Accuracy",
                value="This module is quite accurate, and has few false positives.",
            )
        )
    elif information == "auditlog":
        embed = (
            hikari.Embed(
                title="Internal Audit Log",
                description="The audit log is an internal function of the bot that is designed to log all actions taken by the bot.\n"
                            "You most likely won't notice the existence of this.",
                color=bot.d['colourless'],
            )
        )
    elif information == "civility filter":
        embed = (
            hikari.Embed(
                title="Civility Filter",
                description="The civility filter is a module that is designed to prevent users from being uncivil in the chat.",
                color=bot.d['colourless'],
            )
            .add_field(
                name="AI Recognition",
                value="This module uses an AI by Falconsai to detect offensive speech in the chat.",
            )
            .add_field(
                name="Distrust Toggle",
                value="This module toggled on and off per user when their overall trust is >50%"
            )
            .add_field(
                name="Crowdsourced Feedback",
                value="This module uses a crowdsourced feedback system to determine the accuracy of the AI's detection.\n"
                      "If you believe the AI has made a mistake, you can react with thumbs up (👍) to confirm the AI's detection, "
                      "or thumbs down (👎) to deny the AI's detection.",
            )
        )
    elif information == "image filter":
        embed = (
            hikari.Embed(
                title="Image Filter",
                description="The image filter is a module that is designed to prevent users from sending inappropriate images in the chat.",
                color=bot.d['colourless'],
            )
            .add_field(
                name="AI Recognition",
                value="This module uses an AI by Falconsai to detect NSFW images in the chat.",
            )
            .add_field(
                name="Crowdsourced Feedback",
                value="This module uses a crowdsourced feedback system to determine the accuracy of the AI's detection.\n"
                      "If you believe the AI has made a mistake, you can react with thumbs up (👍) to confirm the AI's detection, "
                      "or thumbs down (👎) to deny the AI's detection.",
            )
        )
    elif information == "distrust system":
        embed = (
            hikari.Embed(
                title="Distrust System",
                description="The trust-distrust system is a reputation system that is designed to assign a trust level to a user based on their behavior in the chat.",
                color=bot.d['colourless'],
            )
            .add_field(
                name="Distrust Level",
                value="The distrust level is a value between 0-100 that is assigned to a user based on their behavior in the chat.\n"
                      "The higher the distrust level, the more likely the user is to be punished by the bot for their behavior.",
            )
            .add_field(
                name="How much does Alice Trust me?",
                value="You can use `/trust` to see how much Alice trusts you.",
            )
        )
    else:
        embed = (
            hikari.Embed(
                title="Error",
                description="The information you requested does not exist.",
                color=bot.d['colourless'],
            )
        )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
