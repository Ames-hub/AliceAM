from library.storage import PostgreSQL
from .group import mod_group
import lightbulb, hikari
from io import BytesIO
import datetime

@mod_group.child
@lightbulb.app_command_permissions(dm_enabled=False)
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
    required=False,
    default='unfiltered',
    type=hikari.OptionType.STRING,
    choices=[
        'img-scan',
        'unfiltered',
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

    embed_404 = (
        hikari.Embed(
            title=f"404 Not found.",
            description="The case ID you provided does not exist?",
            color=ctx.bot.d['colourless']
        )
        .set_thumbnail(
            hikari.files.File('library/question_mark.png')
        )
    )

    if case_type == "img-scan":
        data = PostgreSQL.audit_log(ctx.guild_id).img_scan_logs.get_case_by_id(case_id)
        if data is None:
            await ctx.respond(
                embed_404,
                flags=hikari.MessageFlag.EPHEMERAL
            )
        offender_Id = data[2]
        img_hash = data[3]
        img_bytes = data[4]  # type: memoryview
        posix_timestamp = data[5]

        # Create a BytesIO object
        img_byte_arr = BytesIO(bytes(img_bytes))

        # Get the byte data
        img_byte_arr = img_byte_arr.getvalue()

        embed = (
            hikari.Embed(
                title=f"Image Scan Case: {case_id}",
                description=f"Offender: <@{offender_Id}>\nImage Hash: {img_hash}\nViolating image attached.",
                color=0xFF0000,
                timestamp=datetime.datetime.fromtimestamp(posix_timestamp)
            )
        )

        guild = PostgreSQL.guild(ctx.guild_id)
        attachment = hikari.Bytes(img_byte_arr, 'flagged.jpeg', spoiler=True)
        censor_nsfw = guild.get_do_censor_flagged_nsfw()

        if not censor_nsfw:
            embed.set_thumbnail(attachment)

        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL, attachment=attachment if censor_nsfw else None)
    # Grabs all cases of all types with the case_id
    elif case_type == "unfiltered":

        audit_logs = PostgreSQL.audit_log(ctx.guild_id)
        embed = (
            hikari.Embed(
                title=f"Case Identifier, {case_id}",
                description="Here are all the cases for the case ID you provided.",
                color=ctx.bot.d['colourless']
            )
        )

        img_scan_data = audit_logs.img_scan_logs.get_case_by_id(case_id)

        if img_scan_data is not None:
            img_scan = {
                "offender_id": img_scan_data[2],
                "hash": img_scan_data[3],
                "img_bytes": img_scan_data[4],
                "posix_timestamp": img_scan_data[5]
            }

            embed.add_field(
                name=f"Image Scan, Case {case_id}",
                value=f"Offender: <@{img_scan['offender_id']}>\n"
                      f"Hash: {img_scan['hash']}\n"
                      # Timestamp F = Full date/day, R = Relative (e.g. 1 hour ago)
                      f"Timestamp: <t:{img_scan['posix_timestamp']}:D> (<t:{img_scan['posix_timestamp']}:R>)\n\n"
                      "Violating image attached.",
                inline=False
            )
            embed.set_thumbnail(hikari.Bytes(img_scan['img_bytes'], 'flagged.jpeg'))

        # Pre-filtered into a dictionary. No need to do it here.
        civility_data = audit_logs.civility_logs.get_case_by_id(case_id)

        if civility_data is not None:
            embed.add_field(
                name=f"Civility, Case {case_id}",
                value=f"Offender: <@{civility_data['offender_id']}>\n"
                      f"Timestamp: <t:{civility_data['timestamp']}:D> (<t:{civility_data['timestamp']}:R>)\n"
                      f"Confirmed NPV?: {civility_data['false_positive']}\n\n"
                      f"Message: {civility_data['message']}",
                inline=False
            )

        if civility_data is None and img_scan_data is None:
            await ctx.respond(
                embed_404,
                flags=hikari.MessageFlag.EPHEMERAL
            )
            return

        await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
