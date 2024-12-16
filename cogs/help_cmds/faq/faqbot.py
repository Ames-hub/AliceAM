import datetime
import random

from library.ai import AliceIntel
from library.botapp import bot
from library.storage import PostgreSQL
from .group import faq_group
import lightbulb
import asyncio
import hikari

@faq_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='question',
    description='The question you want to ask.',
    required=True,
    type=hikari.OptionType.STRING
)
@lightbulb.option(
    name='startsession',
    description='Should we keep listening for more questions?',
    required=False,
    default=False,
    type=hikari.OptionType.BOOLEAN
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.UserBucket, length=5, uses=1)
@lightbulb.command(name="assistant", description="Ask Alice Intel a question.", auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def get_trust_score(ctx: lightbulb.SlashContext) -> None:
    question = ctx.options.question
    startsession = ctx.options.startsession

    user_pg = PostgreSQL.users(ctx.author.id)
    if not user_pg.get_faqbot_tos_accepted():
        await ctx.respond(
            "To make use of the FAQ bot, you must agree to the following terms of service, and privacy policy:\n\n"
            "(TOS and Priv Pol of 17/12/2024)\n"
            "1. The FAQ bot is an AI and may not always provide accurate information, and you agree to use it at your own risk.\n"
            "2. The FAQ bot may store the last 10 messages of your conversation until the bot restarts for chat context.\n"
            "3. The FAQ bot may store your user ID to differentiate between users.\n\n"
            "In the next 60 seconds, type 'accept' to agree to these terms and use the FAQ bot."
        )
        try:
            msg: hikari.MessageCreateEvent = await bot.wait_for(hikari.MessageCreateEvent, predicate=lambda m: m.author == ctx.author, timeout=60)
        except asyncio.TimeoutError:
            await ctx.edit_last_response("You did not accept the terms of service in time.")
            return

        if msg.content.lower() == "accept":
            await ctx.author.send(f"On <t:{int(datetime.datetime.now().timestamp())}:F>, you accepted the AliceAM FAQ bot terms of service and privacy policy.")
            user_pg.set_accepted_faqbot_tos(True)
        else:
            await ctx.edit_last_response("You did not accept the terms of service.")
            return

    LLM = AliceIntel.llm(ctx.author.id)
    response = LLM.faq_ai(question)

    # Randomly add an inaccurate notice.
    inaccurate_notice = ""
    if random.randint(1, 10) > 5:
        inaccurate_notice = "\n*Note, Alice Intel is an Artificial Intelligence and may not always provide accurate information. Check important data.*"

    if startsession:
        await ctx.respond(response + f"\n\nYou have 120 seconds to ask another question.\nType 'exit' to stop.{inaccurate_notice}")
        while True:
            try:
                new_msg: hikari.MessageCreateEvent = await bot.wait_for(hikari.MessageCreateEvent, predicate=lambda m: m.author == ctx.author, timeout=120)
            except asyncio.TimeoutError:
                break

            if new_msg.content in ['bye', 'bye!', 'goodbye', 'goodbye!', 'exit', 'quit']:
                await ctx.edit_last_response("Goodbye! If you have any more questions, feel free to ask me again.")
                break

            data = LLM.faq_ai(new_msg.content, response_only=False)
            response = data['response']
            is_done = data['chat_done']
            if is_done:
                await ctx.edit_last_response(response + f"\n*This conversation has been ended by Alice Intelligence*")
                LLM.clear_chat_history(LLM.user_id)  # Clear the chat history
                break
            await ctx.edit_last_response(response + "\n\nYou have 120 seconds to ask another question.\nType 'exit' to stop.\n")
    else:
        await ctx.respond(response)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
