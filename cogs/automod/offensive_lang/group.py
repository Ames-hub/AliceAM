import lightbulb
# defines the plugin
antislur_plugin_name = "ofd_lang_group"
antislur_plugin = lightbulb.Plugin(antislur_plugin_name)
@antislur_plugin.command
# The title of the group and its description
@lightbulb.command("civility", "Manage the offensive language detection system.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
# This is what you import V to use the group.child
async def ofd_lang_group(_) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here

# Loads the plugin. (Not the other children to the plugin)
def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(antislur_plugin)
# Unloads the plugin. (Not the other children to the plugin)
def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_plugin(antislur_plugin)
