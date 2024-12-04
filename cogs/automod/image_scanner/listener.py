from library.storage import PostgreSQL
from library.ai import AliceIntel
from library.botapp import bot
from io import BytesIO
from PIL import Image
import imagehash
import lightbulb
import requests
import hikari

def is_animated_webp(url):
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful
    img = Image.open(BytesIO(response.content))
    return getattr(img, "is_animated", False)

# TODO: Upgrade this to use automod.punish() instead of the current method.
@bot.listen(hikari.GuildMessageCreateEvent)
async def listener(event: hikari.events.GuildMessageCreateEvent) -> bool:
    if len(event.message.attachments) == 0:
        return False

    if event.message.author.is_bot:
        return False

    guild = PostgreSQL.guild(event.guild_id)

    if guild.get_image_scanner_enabled() is False:
        return False

    # Check if the channel is exempted
    if event.channel_id in guild.get_exempt_img_scan_channels():
        return False

    # React with an 'eyes' emoji to show that the bot is processing the image.
    await event.message.add_reaction("👀")

    total_attachments = len(event.message.attachments)
    scanned_attachments = 0
    for attachment in event.message.attachments:
        if attachment.extension not in ['png','jpg', 'jpeg', 'heic', 'webp']:
            # The file is not an image, skip it.
            scanned_attachments += 1

            if scanned_attachments == total_attachments:
                # If none of the images were scanned, remove the 'eyes' emoji as there were no images to scan.
                await event.message.remove_reaction("👀", user=bot.get_me())
                print("No images to scan. Removing 'eyes' emoji.")
                return True

            continue
        elif attachment.extension == 'webp':
            if is_animated_webp(attachment.url):
                # The file is an animated webp, skip it.
                scanned_attachments += 1

                if scanned_attachments == total_attachments:
                    # If none of the images were scanned, remove the 'eyes' emoji as there were no images to scan.
                    await event.message.remove_reaction("👀", user=bot.get_me())
                    return True

        Intel_result = AliceIntel.NsfwImagePredictor.predict(attachment.url, return_img_from_url=True)
        result = Intel_result['result']

        if result == "nsfw":
            img = Intel_result['img']
            await event.message.delete()

            embed = (
                hikari.Embed(
                    title="NSFW Image Detected",
                    description="The image you sent was detected as NSFW and was deleted.",
                    color=0xFF0000
                )
                # TODO: Add a system that teaches the AI what is NSFW and what is not by having users vote on it.
                .set_footer(text="Was this accurate? React with a thumbs up if it was!")
            )

            await event.message.respond(embed)

            # Calculate the Image Hash
            img_hash = str(imagehash.average_hash(img))

            # Save the action to the internal audit log
            audit = PostgreSQL.audit_log(guild_id=event.guild_id)
            audit.img_scan_logs.add_image_scan_handling(
                offender_id=event.message.author.id,
                img=img,
            )
            case_ID = audit.img_scan_logs.get_caseid_for_img_scan(offender_id=event.message.author.id, img_hash=str(img_hash))

            # Send the deleted image to the logs channel.
            if guild.get_auditlog_enabled():
                log_channel_id = guild.get_auditlog_channel_id()
                if log_channel_id is not None:
                    log_channel = bot.cache.get_guild_channel(log_channel_id)

                    # Create a BytesIO object
                    img_byte_arr = BytesIO()

                    # Save the image to the BytesIO object
                    img.save(img_byte_arr, format='JPEG')

                    # Get the byte data
                    img_byte_arr = img_byte_arr.getvalue()

                    embed = (
                        hikari.Embed(
                            title=f"NSFW Image Detected",
                            description=f"Case Identifier: {case_ID}\nUser: <@{event.message.author.id}>\n\nIs this incorrect?\nUse 'rectify' cmd to correct it!",
                            color=0xFF0000,
                        )
                        .set_thumbnail(hikari.Bytes(img_byte_arr, 'flagged.jpeg', spoiler=True))
                    )

                    await log_channel.send(embed=embed)

            return True
        elif result == "nsfw-history":
            await event.message.delete()

            embed = (
                hikari.Embed(
                    title="NSFW Image Detected.",
                    description="The image you sent was detected as NSFW and was deleted.",
                    color=0xFF0000
                )
            )

            await event.message.respond(embed)

            # Log that the image was sent to the logs channel.
            if guild.get_auditlog_enabled():
                log_channel_id = guild.get_auditlog_channel_id()
                if log_channel_id is not None:
                    log_channel = bot.cache.get_guild_channel(log_channel_id)

                    case_ID = Intel_result['case_id']  # This will not exist unless it was a historical image.

                    embed = (
                        hikari.Embed(
                            title=f"NSFW Image Detected (Historical)",
                            description=f"User: <@{event.message.author.id}>\nRepeat of case ID {case_ID}",
                            color=0xFF0000,
                        )
                    )

                    await log_channel.send(embed=embed)
        elif result == "normal":
            await event.message.remove_reaction("👀", user=bot.get_me())
            await event.message.add_reaction("✅")
            return True
        else:
            # Something went wrong, unexpected result.
            await event.message.remove_reaction("👀", user=bot.get_me())
            # React with a question mark to show that the bot is confused.
            await event.message.add_reaction("❓")

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))