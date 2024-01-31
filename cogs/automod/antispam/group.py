import lightbulb
# defines the plugin
antispam_plugin_name = "antispam"
antispam_plugin = lightbulb.Plugin(antispam_plugin_name)
@antispam_plugin.command
# The title of the group and its description
@lightbulb.command("antispam", "All about the AntiSpam system.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def antispam_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(antispam_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(antispam_plugin)