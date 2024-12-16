import lightbulb
# defines the plugin
antiswear_plugin_name = "faq"
faq_plugin = lightbulb.Plugin(antiswear_plugin_name)
@faq_plugin.command
# The title of the group and its description
@lightbulb.command("faq", "Get faq with the functionality of the bot.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def faq_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(faq_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(faq_plugin)
