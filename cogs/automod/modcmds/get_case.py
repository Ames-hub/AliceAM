from library.storage import PostgreSQL
from .group import mod_group
import lightbulb, hikari
from io import BytesIO

@mod_group.child
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.option(
    name='case_id',
    description='The case ID to inspect.',
    required=True,
    type=hikari.OptionType.INTEGER,
    min_value=1
)
@lightbulb.option(
    name='type',
    description='The type of detection that was made.',
    required=True,
    type=hikari.OptionType.STRING,
    choices=[
        'img-scan',
        'bad-words',
    ]
)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=10, uses=1)
@lightbulb.add_checks(
    lightbulb.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES)
)
@lightbulb.command(name="inspect", description="Inspect a previous case.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def inspect_cmd(ctx: lightbulb.SlashContext) -> None:
    case_type = ctx.options.type
    case_id = ctx.options.case_id

    if case_type == "img-scan":
        data = PostgreSQL.audit_log(ctx.guild_id).get_img_scan_case_by_id(case_id)
        offender_Id = data[2]
        img_hash = data[3]
        img_bytes = data[4]  # type: memoryview

        # Create a BytesIO object
        img_byte_arr = BytesIO(bytes(img_bytes))

        # Get the byte data
        img_byte_arr = img_byte_arr.getvalue()

        embed = (
            hikari.Embed(
                title=f"Image Scan Case: {case_id}",
                description=f"Offender: <@{offender_Id}>\nImage Hash: {img_hash}\nViolating image attached.",
                color=0xFF0000
            )
            .set_thumbnail(hikari.Bytes(img_byte_arr, 'flagged.jpeg', spoiler=True))
        )

        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
