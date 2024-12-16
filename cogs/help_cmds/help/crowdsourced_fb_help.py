from library.botapp import bot
from .group import help_group
import lightbulb, hikari

@help_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.command(name="crowdratings", description="Get information about the crowdsourced feedback module.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def help_cmd(ctx: lightbulb.SlashContext) -> None:
    embed = (
        hikari.Embed(
            title="Crowdsourced Feedback",
            description="The crowdsourced feedback module is a module that is designed to allow users to provide feedback on the bot.",
            color=bot.d['colourless']
        )
        .add_field(
            name="How to use",
            value="You can react with thumbs up (👍) to tell the bot that the AI's detection is good,"
                  "or thumbs down (👎) to deny the AI's detection.",
        )
        .add_field(
            name="When can I use this?",
            value="You can use this when prompted by the bot after it made a moderation action.\n"
                  "Once you react, the bot will log your feedback and adjust its detection accordingly.",
        )
        .add_field(
            name="Why should I use this?",
            value="By providing feedback, you can help the bot improve its detection accuracy over time for all users.",
        )
        .add_field(
            name="Is it anonymous?",
            value="Mostly. the bot logs that it is You who provided the feedback\n"
                  "But this data is never shared with anyone, and is hardly ever even looked at.\n"
                  "The only reason it is logged is to prevent abuse of the system for when someone tries to spam bad feedback "
                  "(this way, we can block them)",
        )
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
