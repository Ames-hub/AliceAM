import lightbulb, hikari, datetime, os
from .variables import swears, slurs
from difflib import SequenceMatcher
from .storage import PostgreSQL
from .botapp import bot

class automod:
    @staticmethod
    def censor_text(text:str):
        """
        Censors text by replacing bad text with a '/'
        """
        censored_text = ""
        for swear in swears:
            if swear in text:
                censored_text = text.replace(swear, "/"*len(swear))
        for slur in slurs:
            if slur in text:
                censored_text = text.replace(slur, "/"*len(slur))

        return censored_text

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
    def gen_user_warning_embed(warning_title, user_id, check_result:list=None, is_admin=False, guid:int=None):
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
            # TODO: Determine if this needs to be changed
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

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))
