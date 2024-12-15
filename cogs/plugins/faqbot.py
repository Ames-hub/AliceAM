from library.ai import AliceIntel
from library.botapp import bot
import lightbulb
import asyncio
import hikari

@bot.command
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
@lightbulb.command(name="faqbot", description="Ask Alice Intel a question.", auto_defer=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def get_trust_score(ctx: lightbulb.SlashContext) -> None:
    question = ctx.options.question
    startsession = ctx.options.startsession

    LLM = AliceIntel.llm(ctx.author.id)
    response = LLM.faq_ai(question)

    if startsession:
        await ctx.respond(response + "\n\nYou have 120 seconds to ask another question.\nType 'exit' to stop.\n"
                                     "*Note, Alice Intel is an Artificial Intelligence and may not always provide accurate information.*")
        while True:
            try:
                new_msg: hikari.MessageCreateEvent = await bot.wait_for(hikari.MessageCreateEvent, predicate=lambda m: m.author == ctx.author, timeout=120)
            except asyncio.TimeoutError:
                break

            if new_msg.content in ['bye', 'bye!', 'goodbye', 'goodbye!', 'exit', 'quit']:
                await ctx.edit_last_response("Goodbye! If you have any more questions, feel free to ask me again.")
                break

            response = LLM.faq_ai(new_msg.content)
            await ctx.edit_last_response(response + "\n\nYou have 120 seconds to ask another question.\nType 'exit' to stop.\n"
                                                    "*Note, Alice Intel is an Artificial Intelligence and may not always provide accurate information.*")
    else:
        await ctx.respond(response)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
