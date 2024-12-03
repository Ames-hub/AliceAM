import lightbulb
# defines the plugin
antiswear_plugin_name = "mod"
mod = lightbulb.Plugin(antiswear_plugin_name)
@mod.command
# The title of the group and its description
@lightbulb.command("mod", "moderation commands for the bot")
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def mod_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(mod)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(mod)
