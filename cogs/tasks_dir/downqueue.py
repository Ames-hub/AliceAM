import lightbulb
from library.botapp import tasks
from library.storage import downqueue

@tasks.task(s=2, auto_start=True)
def QueueTask():
    downqueue.run()

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
