from library.storage import PostgreSQL
from library.automod import automod
from .group import config_group
import lightbulb, hikari

@config_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=5, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.ADMINISTRATOR)
)
@lightbulb.command(name="setdefault", description="Set the default configuration for the server.", auto_defer=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def audit_log_set(ctx: lightbulb.SlashContext) -> None:
    action_list = []

    guild = PostgreSQL.guild(ctx.guild_id)
    if guild.get_log_channel_id() is None:
        # Create a new log channel
        try:
            channel = await ctx.bot.rest.create_guild_text_channel(
                ctx.guild_id,
                "alice-logs",
                category=None,
                topic="This channel is used to log moderation actions taken by the bot AliceAM.",
                reason="User request the bot to set its self up.",
            )
            await channel.edit_overwrite(
                # Deny all perms to @everyone, only the bot and admins can see it.
                target=ctx.guild_id,
                target_type=hikari.PermissionOverwriteType.ROLE,
                deny=hikari.Permissions.all_permissions(),
            )
        except hikari.ForbiddenError:
            await ctx.respond("I do not have permission to create a new log channel. Please create one yourself, and use /config audit_channel to set it.")
            return
        action_list.append(f"Created a new log channel: {channel.mention}")
        guild.set_log_channel_id(channel.id)

    # Enables/disables the modules for the server.
    guild.set_antislur_enabled(True)
    action_list.append("Enabled the antislur module for the server.")
    guild.set_antispam_enabled(False)
    guild.set_antiswear_enabled(False)
    action_list.append("Left the antiswear module disabled for the server.")
    guild.set_imagescanner_enabled(True)
    action_list.append("Enabled the nsfw image detector for the server. (This will delete nsfw images)")
    guild.set_do_censor_flagged_nsfw(False)  # When the img scanner shows nsfw in a fetched case, it will not censor it.
    action_list.append("Set it so that nsfw images when a mod fetches them from audit logs will not be censored.")
    guild.set_civility_filter_enabled(True)
    action_list.append("Enabled the civility filter for the server, to force only untrustworthy users (users who are on record to be causing problems) to be more civil.")

    # Creates and sets the default mute role
    roles_list = await ctx.bot.rest.fetch_roles(ctx.guild_id)

    # Finds if a pre-existing muted role exists, and sets it.
    for role in roles_list:
        if role.name == "muted":
            await automod.set_mute_role(role.id)
            action_list.append(f"Set the mute role for the server to be {role.mention}")
            break
    else:
        action_list.append("Created a new muted role for the server, and set it.")
        await automod.set_mute_role(ctx.guild_id)

    action_str = ""
    iterance = 1
    for action in action_list:
        action_str += f"{iterance}. {action}\n"
        iterance += 1

    embed = (
        hikari.Embed(
            title="Default Configuration Set",
            description="The default configuration has been set for the server.",
            color=0x00FF00
        )
        .add_field(
            name="Actions Taken",
            value=action_str
        )
    )

    await ctx.respond(embed=embed)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
