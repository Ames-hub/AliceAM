from library.botapp import bot
import hikari

@bot.listen()
async def on_ready(event: hikari.ShardReadyEvent) -> None:
    print(f"Logged in as {event.my_user.username}")
    
bot.load_extensions_from("cogs/automod/")

bot.run()