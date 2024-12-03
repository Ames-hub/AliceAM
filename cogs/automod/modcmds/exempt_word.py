from library.storage import PostgreSQL
from .group import mod_group
import lightbulb, hikari

@mod_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='word',
    description='The word to exempt from detections.',
    required=True,
    type=hikari.OptionType.STRING,
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
)
@lightbulb.command(name="exempt_word", description="Exempt a word from detections.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def unexempt_cmd(ctx: lightbulb.SlashContext) -> None:
    word_affected = ctx.options.word

    guild = PostgreSQL.guild(ctx.guild_id)
    success = guild.add_whitelist_word(word_affected)
    if success:
        await ctx.respond(
            f"Successfully added the word `{word_affected}` to the whitelist.",
            flags=hikari.MessageFlag.EPHEMERAL
        )
    elif success == -1:
        await ctx.respond(
            f"The word `{word_affected}` is already in the blacklist.",
            flags=hikari.MessageFlag.EPHEMERAL
        )
    else:
        await ctx.respond(
            f"The word `{word_affected}` is already in the whitelist.",
            flags=hikari.MessageFlag.EPHEMERAL
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
