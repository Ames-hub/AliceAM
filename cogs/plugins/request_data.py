from library.storage import PostgreSQL
from library.botapp import bot
import lightbulb
import datetime
import asyncio
import logging
import hikari
import base64
import io

def format_user_data_to_string(user_pg, user_infractions_pg, infraction_durations_pg, civility_votes_pg, civility_cases_pg, img_cases_pg):
    formatted_data = []

    # Format user data
    if user_pg:
        formatted_data.append("User data table:")
        formatted_data.append(f"    Your user ID: {user_pg[0]}")
        formatted_data.append(f"    Your trust ratio: {user_pg[1]}%")
        formatted_data.append(f"    Trust last modified: {datetime.datetime.fromtimestamp(user_pg[2]).strftime('%Y-%m-%d %H:%M:%S')}")
        formatted_data.append("")

    # Format user infractions
    formatted_data.append("Infractions data table:")
    if len(user_infractions_pg) != 0:
        for infraction in user_infractions_pg:
            formatted_data.append(f"    Infraction ID: {infraction[0]}")
            formatted_data.append(f"    Timestamp: {datetime.datetime.fromtimestamp(infraction[1]).strftime('%Y-%m-%d %H:%M:%S')}")
            formatted_data.append(f"    Offender ID: {infraction[2]}")
            formatted_data.append(f"    Moderator ID: {infraction[3]}")
            formatted_data.append(f"    Guild ID: {infraction[4]}")
            formatted_data.append(f"    Reason: {infraction[5]}")
            formatted_data.append("")
    else:
        formatted_data.append("    No infractions found.")
        formatted_data.append("")

    # Format infraction durations
    formatted_data.append("Infraction Durations data table:")
    if len(infraction_durations_pg) != 0:
        for duration in infraction_durations_pg:
            formatted_data.append(f"    Infraction ID: {duration[0]}")
            formatted_data.append(f"    Lasts To: {datetime.datetime.fromtimestamp(duration[1]).strftime('%Y-%m-%d %H:%M:%S')}")
            formatted_data.append(f"    Expired: {duration[2]}")
            formatted_data.append(f"    Action: {duration[3]}")
            formatted_data.append(f"    Offender ID: {duration[4]}")
            formatted_data.append("")
    else:
        formatted_data.append("    No infraction durations found.")
        formatted_data.append("")

    # Format civility votes
    formatted_data.append("Civility Votes data table:")
    if len(civility_votes_pg) != 0:
        for vote in civility_votes_pg:
            formatted_data.append(f"    Rating ID: {vote[0]}")
            formatted_data.append(f"    Case ID: {vote[1]}")
            formatted_data.append(f"    Rating: {vote[2]}")
            formatted_data.append(f"    Voter ID: {vote[3]}")
            formatted_data.append(f"    Timestamp: {datetime.datetime.fromtimestamp(vote[4]).strftime('%Y-%m-%d %H:%M:%S')}")
            formatted_data.append("")
    else:
        formatted_data.append("    No civility votes found.")
        formatted_data.append("")

    # Format civility cases
    formatted_data.append("Civility Cases data table:")
    if len(civility_cases_pg) != 0:
        for case in civility_cases_pg:
            formatted_data.append(f"    Case ID: {case[0]}")
            formatted_data.append(f"    Guild ID: {case[1]}")
            formatted_data.append(f"    Offender ID: {case[2]}")
            formatted_data.append(f"    Message: {case[3]}")
            formatted_data.append(f"    Timestamp: {datetime.datetime.fromtimestamp(case[4]).strftime('%Y-%m-%d %H:%M:%S')}")
            formatted_data.append(f"    Known FP?: {case[5]}")
            formatted_data.append("")
    else:
        formatted_data.append("    No civility cases found.")
        formatted_data.append("")

    # Format image scan cases
    formatted_data.append("Image Scan Cases data table:")
    img_cases_pg_count = len(img_cases_pg)
    if img_cases_pg_count != 0:
        for img_case in img_cases_pg:
            formatted_data.append(f"    Case ID: {img_case[0]}")
            formatted_data.append(f"    Guild ID: {img_case[1]}")
            formatted_data.append(f"    Offender ID: {img_case[2]}")
            formatted_data.append(f"    Image Hash: {img_case[3]}")

            # Converts img bytes to a Base64 string. img_case[4] is a memoryview object.
            if img_cases_pg_count < 200:
                img_bytes = base64.b64encode(img_case[4].tobytes()).decode("utf-8")
            else:
                # Discord limits us to ~5mb for an attachment, so we can't send too many images' byte data.
                img_bytes = "Too many images to display :("

            formatted_data.append(f"    Image Bytes (BASE64): {img_bytes}")
            formatted_data.append(f"    Timestamp: {datetime.datetime.fromtimestamp(img_case[5]).strftime('%Y-%m-%d %H:%M:%S')}")
            formatted_data.append("")
    else:
        formatted_data.append("    No image scan cases found.")
        formatted_data.append("")

    return "\n".join(formatted_data)

@bot.command
@lightbulb.app_command_permissions(dm_enabled=True)
@lightbulb.add_cooldown(bucket=lightbulb.buckets.GuildBucket, length=15, uses=1)
@lightbulb.command(name="datarequest", description="Request data your discord account from the bot.", auto_defer=True)
# use "slash sub command" opposed to "slash command" if it is in a group
@lightbulb.implements(lightbulb.SlashCommand)
async def data_request(ctx: lightbulb.SlashContext) -> None:
    # do_dm = ctx.options.doDM
    # An example of how you'd get the value of an option.
    embed = (
        hikari.Embed(
            title="Data Request | TIMER, 60 SECONDS",
            description="You are about to request data identifiable to your discord account from the bot.\n"
                        "Are you sure you want to continue? Respond with `yes` or `no`.",
            color=bot.d['colourless'],
        )
    )

    await ctx.respond("Check your DMs for the data request.", flags=hikari.MessageFlag.EPHEMERAL)
    await ctx.author.send(embed=embed)

    try:
        confirm_msg = await bot.wait_for(hikari.DMMessageCreateEvent, predicate=lambda m: m.author == ctx.author, timeout=60)
    except asyncio.TimeoutError:
        await ctx.author.send("Data request timed out.")
        return

    if confirm_msg.content.lower() == "yes":

        conn = PostgreSQL.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE user_id = %s", (ctx.author.id,))
        user_pg = cur.fetchone()

        cur.execute("SELECT * FROM user_infractions WHERE offender_id = %s", (ctx.author.id,))
        user_infractions_pg = cur.fetchall()

        cur.execute("SELECT * FROM infraction_durations WHERE offender_id = %s", (ctx.author.id,))
        infraction_durations_pg = cur.fetchall()

        cur.execute("SELECT * FROM offensive_lang_result_ratings WHERE voter_id = %s", (ctx.author.id,))
        civility_votes_pg = cur.fetchall()

        cur.execute("SELECT * FROM offensive_lang_cases WHERE offender_id = %s", (ctx.author.id,))
        civility_cases_pg = cur.fetchall()

        cur.execute("SELECT * FROM img_scanner_cases WHERE offender_id = %s", (ctx.author.id,))
        img_cases_pg = cur.fetchall()

        conn.close()

        formatted_data = format_user_data_to_string(
            user_pg,
            user_infractions_pg,
            infraction_durations_pg,
            civility_votes_pg,
            civility_cases_pg,
            img_cases_pg,
        )

        # Converts to a bytesIO object
        data = io.BytesIO(formatted_data.encode("utf-8"))

        logging.info("Data request sent to user: %s", ctx.author.id)

        # Send the data
        await ctx.author.send(
            "Here is the data you requested.",
            attachment=hikari.Bytes(data, f"{ctx.author.id}_data.txt", "text/plain", spoiler=False),
        )
    else:
        await ctx.author.send("Data request cancelled.")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
