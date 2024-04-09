from library.cache import cache
from library.botapp import tasks
import lightbulb

@tasks.task(s=15, wait_before_execution=True, auto_start=True)
def cache_clear() -> None:
    cache.clear_cache()

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
