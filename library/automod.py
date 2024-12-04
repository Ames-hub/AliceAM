import lightbulb, hikari, datetime, os
from .variables import swears, slurs
from difflib import SequenceMatcher
from .storage import PostgreSQL
from library import errors
from .botapp import bot

class automod:
    @staticmethod
    def censor_text(text: str) -> str:
        """
        Censors text by replacing bad text with a '/'
        """
        censored_text = text.lower()
        for swear in swears:
            if swear in censored_text:
                censored_text = censored_text.replace(swear, "/" * len(swear))
        for slur in slurs:
            if slur in censored_text:
                censored_text = censored_text.replace(slur, "/" * len(slur))

        return censored_text

    @staticmethod
    async def send_log_msg(content:str | hikari.Embed, guild_id:int) -> bool:
        """
        Sends a message to the guild's log channel.

        Args:
            :param content: (str | hikari.Embed): The content to be sent.
            :param guild_id: (int): The ID of the guild to send the message to.

        Returns:
            bool: True if the message was sent successfully, False if not.
        """
        guild = PostgreSQL.guild(guild_id)
        if not guild.get_auditlog_enabled():
            return False

        channel_id = guild.get_auditlog_channel_id()
        if channel_id is None:
            return False

        await bot.rest.create_message(
            channel=hikari.Snowflake(channel_id),
            content=content
        )
        return True

    @staticmethod
    async def send_member_dm(content:str | hikari.Embed, user_id:int) -> bool:
        raise NotImplementedError

    @staticmethod
    async def punish(
            action,
            reason:str = "No reason provided.",
            dm_offender:bool = False,
            say_in_channel:bool = True,
            moderator_id:int = None,
            ctx: lightbulb.SlashContext = None,  # Not likely to be used, but may as well.
            event: hikari.events.GuildMessageCreateEvent = None,  # Type-hint assumed. Most likely will be this.
            offender_id: int = None,
            guild_id: int = None,
            msg_id_for_deletion: int = None,
            custom_embed: hikari.Embed = None
    ) -> dict:
        """
        Basically a wrapper function.
        This function lets Alice punish users for whatever reason and is used in place of the normal punishment function
        because it handles the following additional jobs:

        - Logging the punishment to DB and the guild's log channel.
        - Sending a message to the user (if specified to do so).
        - Ensures two or more conflicting punishments are not executed at the same time.
        - Handles degrading their trust score if they break the rules.

        This function fixes a problem with, for example, the civility check and heuristic check. If a user was uncivil,
        said a slur, the user would be punished for being uncivil and then punished again for saying a slur by the
        heuristic check. Causing an error, as it tries to delete the message twice, or ban the user twice.
        This is the prime reason for the fact that this function exists.

        Handles the following placeholders:
        - {user} - The user who broke the rules.
        - {moderator} - The moderator who punished the user.
        - {case_id} - The ID of the case in the database.

        Args:
            :param action: (str): The action to be taken. (delete, ban, mute)
            :param reason: (str): The reason for the punishment.
            :param dm_offender: (bool): Whether to DM the offender of the punishment.
            :param say_in_channel: (bool): Whether to say the punishment in the channel.
            :param moderator_id: (int): The ID of the moderator who issued the punishment. Default is the bot.
            :param ctx: (lightbulb.SlashContext): The context of the command.
            :param event: (hikari.events.GuildMessageCreateEvent): The event that triggered the punishment.
            :param offender_id: (int): The ID of the user to be punished. An alternative to providing ctx/event.
            :param guild_id: (int): The ID of the guild the user is in. An alternative to providing ctx/event.
            :param msg_id_for_deletion: (int): The ID of the message to be deleted
            if the action is 'delete' and ctx/event is None
            :param custom_embed: (hikari.Embed): A custom embed to be sent to the log channel.

        Returns:
            {
                'success': bool,

                'error': Exception | None,

                'logging_success': bool,

                'announcement_successful': bool,

                'pm_success': bool, (pm: Private Message)

                'new_case_id': int | None,
            }

        Raises:
            AssertionError: If the action is not valid.
            AssertionError: If both ctx and event are None, and user_id and guild_id are None.
            AssertionError: If both guild_id and user_id are None, and ctx/event is None.
            alice.errors.conflicting_punishment: if the action would result in being punished in an invalid way.
            alice.errors.impossible_punishment: If you try to perform an action that's impossible.
            Such as deleting a message from a slash command.

        """

        valid_actions = [
            'ban',
            'kick',
            'mute',
            'delete',
        ]

        action = action.lower()  # Case insensitivity
        assert action in valid_actions, f"Action must be one of {valid_actions}. Not {action}"
        assert (ctx is not None or event is not None) or (offender_id is not None and guild_id is not None), \
        "Both ctx and event are None, and user_id and guild_id are None."

        if moderator_id is None:
            moderator_id = bot.d['bot_id']

        if event is not None:
            offender_id = event.author.id
            guild_id = event.guild_id
        elif ctx is not None:
            if offender_id is None:
                raise AttributeError("Offender ID must not be None if ctx is not None.")

        # Check if the user is already being punished the same way or in a conflicting way
        conflicting_punishments = {
            'delete': [], # No conflicting punishments
            'kick': [
                'mute',
                'ban'
            ],
            'ban': [
                'mute',
                'kick'
            ],
            # TODO: Make mute 'sticky' so a user can't leave and rejoin to get around it.
            # TODO: Implement muting
            'mute': [
                'ban',
                'kick'
            ],
        }

        offender_data = PostgreSQL.users(offender_id)

        # Get the current punishment of the user if they are being punished
        active_punishments = offender_data.get_active_punishments(guild_id)

        for punishment in active_punishments:
            if punishment['action'] in conflicting_punishments[action]:
                raise errors.conflicting_punishments()

        # It's not conflicting. Mark the user as being punished
        offender_data.begin_quickact_punishment(
            guild_id=str(guild_id),
            action=action,
        )

        # Degrade user trust for breaking the rules
        offender_data.modify_trust(4, "-")

        if reason is None:  # Double-check the reason
            reason = "No reason provided."

        offender = await bot.rest.fetch_member(user=hikari.Snowflake(offender_id), guild=hikari.Snowflake(guild_id))

        # Punish the user
        if action == 'delete':
            # Delete the message
            try:
                if event is not None:
                    await event.message.delete()
                    offender_id = event.author.id
                elif ctx is not None:
                    if msg_id_for_deletion is not None:
                        await ctx.bot.rest.delete_message(
                            channel=hikari.Snowflake(ctx.channel_id),
                            message=hikari.Snowflake(msg_id_for_deletion)
                        )
                    offender_id = ctx.author.id
                else:
                    if msg_id_for_deletion is not None:
                        await ctx.bot.rest.delete_message(
                            channel=hikari.Snowflake(ctx.channel_id),
                            message=hikari.Snowflake(msg_id_for_deletion)
                        )
            except (
                    hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError, hikari.UnauthorizedError,
                    errors.impossible_punishment, errors.conflicting_punishments
            ) as err:
                return {
                    'success': False,
                    'error': err,
                    'logging_success': False,
                    'pm_success': False,
                    'announced_successfully': False,
                    'new_case_id': None
                }

            if custom_embed is None:
                embed = (
                    hikari.Embed(
                        title="Message Deleted",
                        description=f"<@{moderator_id}> deleted a message that was sent in <#{event.message.channel_id}>.",
                        color=bot.d['colourless'],
                        timestamp=datetime.datetime.now().astimezone()
                    )
                    .set_author(  # Author is who got punished
                        name=f"Author: {offender.username}",
                        icon=offender.avatar_url
                    )
                    .add_field(
                        name="Reason provided",
                        value=f'"{reason}"',
                        inline=False
                    )
                    .add_field(
                        name="Content",
                        value=f"\"{automod.censor_text(event.message.content)}\"",
                    )
                )
            else:
                embed = custom_embed

            # Remember the infraction in the database
            case_id = PostgreSQL.users(offender_id).add_infraction(
                reason=reason,
                moderator_id=moderator_id,
                infraction_type=action,
                guild_id=guild_id,
                return_case_id=True
            )

            log_success = await automod.send_log_msg(content=embed, guild_id=guild_id)

            if dm_offender:
                pm_success = await automod.send_member_dm(content=embed, user_id=offender_id)
            else:
                pm_success = False

            announced_successfully = False
            if say_in_channel:
                if event is not None:
                    announcement_embed = (
                        hikari.Embed(
                            title="Message Deleted",
                            description=f"This message has been deleted.",
                            color=0xFF0000,
                            timestamp=datetime.datetime.now().astimezone()
                        )
                    )

                    await event.message.respond(announcement_embed)
                    announced_successfully = True

            return {
                'success': True,
                'error': None,
                'logging_success': log_success,
                'pm_success': pm_success,
                'announced_successfully': announced_successfully,
                'new_case_id': case_id
            }
        elif action == 'ban':
            if custom_embed is None:
                embed = (
                    hikari.Embed(
                        title="Member Banned",
                        description=f"A member was banned by <@{moderator_id}>.",
                        color=bot.d['colourless'],
                        timestamp=datetime.datetime.now().astimezone()
                    )
                    .set_author(  # Author is who got punished
                        name=f"Offender: <@{offender_id}>",
                        icon=offender.avatar_url
                    )
                    .add_field(
                        name="Reason provided",
                        value=reason,
                        inline=False
                    )
                )
            else:
                embed = custom_embed

            # PM Them before banning them since we can't PM them after they're banned
            if dm_offender:
                pm_success = await automod.send_member_dm(content=embed, user_id=offender_id)
            else:
                pm_success = False

            try:
                # Ban the user
                if event is not None:
                    await event.member.ban(
                        reason=reason,
                        delete_message_seconds=604800  # 1 week
                    )
                elif ctx is not None:
                    if offender_id is not None:
                        await ctx.bot.rest.ban_member(
                            guild=hikari.Snowflake(guild_id),
                            user=hikari.Snowflake(offender_id),
                            delete_message_seconds=604800,  # 1 week
                            reason=reason
                        )
                    else:
                        raise errors.impossible_punishment("Banning a user from a slash command is not possible.")
                else:
                    if offender_id is None or guild_id is None:
                        raise AttributeError("Offender ID and Guild ID must not be None if ctx and event are None.")

                await bot.rest.ban_member(
                    guild=hikari.Snowflake(guild_id),
                    user=hikari.Snowflake(offender_id),
                    delete_message_seconds=604800,  # 1 week
                    reason=reason
                )
            except (
                    hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError, hikari.UnauthorizedError,
                    errors.impossible_punishment, errors.conflicting_punishments
            ) as err:
                return {
                    'success': False,
                    'error': err,
                    'logging_success': False,
                    'pm_success': False,
                    'announced_successfully': False,
                    'new_case_id': None
                }

            # Remember the infraction in the database
            case_id = PostgreSQL.users(offender_id).add_infraction(
                reason=reason,
                moderator_id=moderator_id,
                infraction_type=action,
                guild_id=guild_id,
                return_case_id=True
            )

            log_success = await automod.send_log_msg(content=embed, guild_id=guild_id)

            announced_successfully = False
            if say_in_channel:
                if event is not None:
                    announcement_embed = (
                        hikari.Embed(
                            title="Member Banned",
                            description=f"<@{offender_id}> has been banned.",
                            color=0xFF0000,
                            timestamp=datetime.datetime.now().astimezone()
                        )
                    )

                    await event.message.respond(announcement_embed)
                    announced_successfully = True

            return {
                'success': True,
                'error': None,
                'logging_success': log_success,
                'pm_success': pm_success,
                'announced_successfully': announced_successfully,
                'new_case_id': case_id
            }
        elif action == 'kick':
            if custom_embed is None:
                embed = (
                    hikari.Embed(
                        title="Member Kicked",
                        description=f"A member was kicked by <@{moderator_id}>.",
                        color=bot.d['colourless'],
                        timestamp=datetime.datetime.now().astimezone()
                    )
                    .set_author(  # Author is who got punished
                        name=f"Offender: {offender.username}",
                        icon=offender.avatar_url
                    )
                    .add_field(
                        name="Reason provided",
                        value=reason,
                        inline=False
                    )
                )
            else:
                embed = custom_embed

            # PM Them before kicking them since we can't PM them after they're kicked
            if dm_offender:
                pm_success = await automod.send_member_dm(content=embed, user_id=offender_id)
            else:
                pm_success = False

            try:
                # Kick the user
                if event is not None:
                    await event.member.kick(reason=reason)
                elif ctx is not None:
                    if offender_id is not None:
                        await ctx.bot.rest.kick_member(
                            guild=hikari.Snowflake(guild_id),
                            user=hikari.Snowflake(offender_id),
                            reason=reason
                        )
                    else:
                        raise errors.impossible_punishment("Kicking a user from a slash command is not possible.")
                else:
                    if offender_id is None or guild_id is None:
                        raise AttributeError("Offender ID and Guild ID must not be None if ctx and event are None.")

                    await bot.rest.kick_member(
                        guild=hikari.Snowflake(guild_id),
                        user=hikari.Snowflake(offender_id),
                        reason=reason
                    )
            except (
                    hikari.ForbiddenError, hikari.NotFoundError, hikari.BadRequestError, hikari.UnauthorizedError,
                    errors.impossible_punishment, errors.conflicting_punishments
            ) as err:
                return {
                    'success': False,
                    'error': err,
                    'logging_success': False,
                    'pm_success': False,
                    'announced_successfully': False,
                    'new_case_id': None
                }

            # Remember the infraction in the database
            case_id = PostgreSQL.users(offender_id).add_infraction(
                reason=reason,
                moderator_id=moderator_id,
                infraction_type=action,
                guild_id=guild_id,
                return_case_id=True
            )

            log_success = await automod.send_log_msg(content=embed, guild_id=guild_id)

            announced_successfully = False
            if say_in_channel:
                if event is not None:
                    announcement_embed = (
                        hikari.Embed(
                            title="Member Kicked",
                            description=f"<@{offender_id}> has been kicked.",
                            color=0xFF0000,
                            timestamp=datetime.datetime.now().astimezone()
                        )
                    )

                    await event.message.respond(announcement_embed)
                    announced_successfully = True

            return {
                'success': True,
                'error': None,
                'logging_success': log_success,
                'pm_success': pm_success,
                'announced_successfully': announced_successfully,
                'new_case_id': case_id
            }
        elif action == 'mute':
            # Mute the user
            raise NotImplementedError("Muting a user is not yet implemented.")


    class text_checkers:
        def __init__(self, content: str, blacklist: list[str], account_for_rep: bool, user_id: int = None, guild_id: int = None) -> None:
            """
            Initializes the Automod class.

            Args:
                content (str): The content to be moderated.
                blacklist (list[str]): A list of words to be blacklisted.
                account_for_rep (bool): Indicates whether to account for reputation which sets the 'guilty' threshold.

            Returns:
                None
            """
            # Make sure everything is lowercase to avoid case sensitivity
            self.content = content.lower()
            for word in blacklist:
                # Updates the word in the list to be word.lower()
                blacklist[blacklist.index(word)] = word.lower()

            self.blacklist = blacklist
            self.account_for_rep = account_for_rep
            self.user_id = user_id
            self.guild_id = guild_id

        def heuristical(self) -> list:
            """
            Checks if a message contains a forbidden word. Returns True if it does, False if it doesn't.
            """
            if self.content is None or self.content == "" or self.blacklist == []:
                return []

            custom_whitelist = []
            if self.guild_id is not None:
                custom_whitelist = PostgreSQL.guild(self.guild_id).get_custom_whitelist()

            components = automod.text_checkers.components(
                content=self.content,
                blacklist=self.blacklist,
                account_for_rep=self.account_for_rep,
                user_id=self.user_id,
                additional_whitelist=custom_whitelist
            )

            checks_list = [
                components.equality_check,
                components.substring_check,
                components.symbol_check,
                components.wsw_check,
                components.similarity_check
            ]

            for check in checks_list:
                # noinspection PyArgumentList
                result:list = check()
                assert result is not None, "Result must not be None."

                if result[0] is False:
                    continue
                else:
                    result.append(f'check:{check.__name__.replace("_check", "")}')
                    return result
            return [False, None, None, None]
    
        def rep_heuristic(self) -> list:
            """
            Much like the Heuristical checker, but instead this bases it off the stored trustability of the user.

            Returns:
                list: [bool, int, float, str]

                bool: True if a forbidden word was found, False if not.
                int: The index of the word found in the blacklist.
                float: The similarity ratio between the two strings if the similarity check was tripped. (-1 if not)
                str: The check that was tripped. (substring, symbol, equality, wsw, similarity)
            """
            if self.content is None or self.content == "" or self.blacklist == []:
                return [False, None, None, None]

            assert self.user_id is not None, "User ID is None. Cannot check reputation without it."
            assert self.blacklist is not None, 'Blacklist must not be none'
            assert self.content is not None, 'Content must not be none'

            custom_whitelist = []
            if self.guild_id is not None:
                custom_whitelist = PostgreSQL.guild(self.guild_id).get_custom_whitelist()

            components = automod.text_checkers.components(
                self.content,
                self.blacklist,
                account_for_rep=self.account_for_rep,
                user_id=self.user_id,
                additional_whitelist=custom_whitelist
            )

            checks_list = [
                components.equality_check,
                components.substring_check,
                components.symbol_check,
                components.wsw_check,
                components.similarity_check
            ]

            for check in checks_list:
                # noinspection PyArgumentList
                result:list = check()
                assert result is not None, "Result must not be None."

                if result[0] is False:
                    continue
                else:
                    result.append(f'check:{check.__name__.replace("_check", "")}')
                    return result
            return [False, None, None, None]

        class components:
            """
            This class contains each check that we have.
            """
            def __init__(self, content, blacklist, account_for_rep, user_id, additional_whitelist:list=None):
                self.content = content
                self.blacklist = blacklist
                self.account_for_rep = account_for_rep
                self.user_id = user_id
                self.user_trust = PostgreSQL.users(user_id).get_trust()

                # Get the whitelist text file.
                with open(os.path.abspath('library/whitelist.txt'), 'r') as f:
                    self.whitelist = f.read().split("\n")

                # If there is an additional whitelist, add it to the whitelist
                if additional_whitelist is not None:
                    for word in additional_whitelist:
                        self.whitelist.append(word)

                # Get user reputation
                if account_for_rep:
                    user = PostgreSQL.users(user_id)
                    self.overall_reputation = user.get_trust()
                    self.user_rep = user

            def remove_symbols(self):
                nosymb_content = ''
                for letter in self.content:
                    if str(letter).isalnum() or letter == " ":
                        nosymb_content += letter
                return nosymb_content

            def substring_check(self):
                # Basic 'substring' check. eg "slur" in "You ufw**slur**jig"
                for item in self.blacklist:
                    if item in self.content:
                        # Finds the index start and end of the word in the blacklist
                        start = self.content.index(item)
                        end = start + len(item)

                        return [True, (item, self.content, (start, end))]
                return [False, (None, None, None)]

            def symbol_check(self)-> list:
                """
                Check for words with symbols/punctuation. eg, "Your such a sl!ur." Uses equality.

                Returns:
                    [bool, tuple(blacklisted_word, content_part) | -1, str]

                    bool: True if a forbidden word was found, False if not.
                    tuple: The blacklisted word and the content part that was found. (-1 if not found)
                    str: The check that was tripped. (substring, symbol, equality, wsw, similarity)
                """
                nosymb_content = self.remove_symbols()
                # Could be None if the message was all punctuation
                if nosymb_content is not None:
                    for word in nosymb_content.split(" "):
                        for item in self.blacklist:
                            if word == item:
                                if word in self.whitelist:
                                    continue
                                return [True, (item, word)]
                return [False, (None, None)]

            def equality_check(self) -> list:
                """
                Check for equality. eg, "slur" == "slur"

                Returns:
                    list: [bool, tuple(blacklisted_word, matched_word) | -1, str]

                    bool: True if a forbidden word was found, False if not.
                    tuple: The blacklisted word and the content part that was found. (-1 if not found)
                    str: The check that was tripped. (substring, symbol, equality, wsw, similarity)
                """
                for word in self.content.split(" "):
                    if word in self.whitelist:
                        continue
                    for item in self.blacklist:
                        if word == item:
                            return [True, (item, word)]
                return [False, (None, None)]

            def wsw_check(self) -> list:
                """
                Check for words with spaces.

                eg, "slur" == "sl ur" but "I had one growing" does not trip because
                of the would-be false-positive slur that reveals its self
                when you remove the space between 'one' and 'growing'.

                Returns:
                    list: [bool, tuple(blacklisted_word, content_part) | -1, str]

                    bool: True if a forbidden word was found, False if not.
                    tuple: The blacklisted word and the content part that was found. (-1 if not found)
                    str: The check that was tripped. (substring, symbol, equality, wsw, similarity)
                """
                # Get the content and split it into words
                content = self.content
                content_split = content.split(" ")
                content_count = len(content_split)

                # Check if there is more than one word
                if content_count > 1:
                    index = 0
                    for word in content_split:
                        try:
                            # Combine the current word with the next word
                            part = word + content_split[index + 1]
                        except IndexError:
                            # Break the loop if there is no next word
                            break
                        # Check if the combined word is in the blacklist
                        for item in self.blacklist:
                            if item == part:
                                return [True, (item, part)]
                        index += 1
                    return [False, (None, None)]
                # If there is only one word, return False
                elif content_count == 1:
                    return [False, (None, None)]

            def similarity_check(self) -> list:
                """
                Check for similarity. eg, "slur" == "sler"

                Returns:
                    list: [bool, str|None, float]

                    bool: True if a similar word was found, False if not.
                    tuple: The detected blacklisted word[0], the word which tripped it[1], and the similarity ratio[2].
                """
                assert self.user_trust <= 100.0, f"Ratio must be less than or equal to 100. not {self.user_trust}"
                assert self.user_trust >= 0.0, f"Ratio must be greater than or equal to 0. not {self.user_trust}"

                # Determines how similar 2 strings are by importing the SequenceMatcher class from difflib
                for word in self.content.split(" "):
                    for item in self.blacklist:
                        similarity = SequenceMatcher(None, a=word, b=item).ratio()
                        # Converts the similarity ratio to a number that users can understand and is not too punishing
                        # Eg, 0.8 * 90 = 72% similarity and needs >72% trust to be tripped
                        similarity = similarity * 90

                        # Debug code. Uncomment to see the similarity ratio
                        # print(f"word: {word}\nitem: {item}\nsimilarity: {similarity}\nratio: {ratio}\n\nNEW CHECK\n\n")
                        if similarity >= self.user_trust:
                            if word in self.whitelist:
                                continue

                            return [True, (item, word, similarity)]

                return [False, (None, None, -1)]

    @staticmethod
    def gen_user_warning_embed(
            warning_title,
            user_id,
            check_result=None,
            is_admin=False,
            guid:int=None,
            check_type='heuristic',  # Default to this for anti-slur and anti-swear. Other checks will need to specify this.
    ):
        assert check_result is not None, "Check result must not be None"

        admin_warn_msg = (
            "You are an administrator on this server.\n"
            "Start acting like it and hold yourself accountable."
        )

        if check_result is None:
            return (hikari.Embed(
                    title=warning_title,
                    description="Automod has detected you broke the rules.",
                    color=bot.d['colourless'],
                    timestamp=datetime.datetime.now().astimezone()
                )
                .set_thumbnail(
                    os.path.abspath('library/Hammer.png')
                )
            )
        else:
            if check_type == 'heuristic':
                check_name = check_result[len(check_result)-1]
                word_found = check_result[1][1]

                desc = f"Automod has detected <@!{user_id}> broke the rules."
                if 'substring' in check_name:
                    index_start = check_result[1][2][0]  # Index of the start of the word
                    index_end = check_result[1][2][1]  # Index of the end of the word from the result of substring_check

                    desc = f"<@{user_id}> You cannot say that here.\n"
                    # Word found will be content if its substring check

                    if guid is not None:
                        # check if the server is ok with the censored substring being shown
                        if PostgreSQL.guild(guid).get_show_censored_substrings():
                            desc += f"\"{word_found[:index_start]}*__{word_found[index_start:index_end]}__*{word_found[index_end:]}\""

                    desc += f"\"{word_found[:index_start]}*__{word_found[index_start:index_end]}__*{word_found[index_end:]}\""
                    # Censors the desc
                    desc = automod.censor_text(desc)

                embed = (hikari.Embed(
                        title=warning_title,
                        description=desc,
                        color=bot.d['colourless'],
                        timestamp=datetime.datetime.now().astimezone()
                    )
                    .set_thumbnail(
                        os.path.abspath('library/Hammer.png')
                    )
                    .set_footer(
                        text=check_name # Check name will always be the last item in the list
                    )
                )
                if is_admin:
                    embed.add_field(
                        name="Upholding the rules",
                        value=admin_warn_msg,
                        inline=False
                    )
                return embed
            elif check_type == 'civility':
                # An AI check. This will be different from the heuristic check.
                trust_score:float = check_result['trust_score']
                label = check_result['label']

                embed = (
                    hikari.Embed(
                        title=warning_title,
                        description=f"The civility filter has detected you became \'{label}\' in your message.",
                        color=bot.d['colourless'],
                        timestamp=datetime.datetime.now().astimezone()
                    )
                    .set_footer(f'{label} | Trust Score: {str(trust_score)[:7]}')
                    .set_thumbnail(os.path.abspath('library/Hammer.png'))
                )
                if is_admin:
                    embed.add_field(
                        name="Upholding the rules",
                        value=(
                            "You are an administrator on this server.\n"
                            "Please remember it may be a good idea to keep calm and respectful."
                        ),
                        inline=False
                    )
                return embed

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
