# Automoderation functions.py
from .variables import swears, slurs
from .botapp import bot
from .storage import memory
import lightbulb, hikari, datetime, os
from difflib import SequenceMatcher
colourless = bot.d['colourless']

class automod:
    def censor_text(text:str):
        '''
        Censors text by replacing bad text with a '/'
        '''
        censored_text = ""
        for swear in swears:
            if swear in text:
                censored_text = text.replace(swear, "/"*len(swear))
        for slur in slurs:
            if slur in text:
                censored_text = text.replace(slur, "/"*len(slur))

        return censored_text

    class text_checkers:
        def __init__(self, content: str, blacklist: list[str], account_for_rep: bool, user_id: int = None) -> None:
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
            # Account for rep can be changed later using (instance).account_for_rep = False but its fine. rep class already assigned, it'll just stop it.
            if account_for_rep is True and user_id is None:
                raise ValueError(
                    "account_for_rep is True but user_id is None. Need User_ID to know who's reputation to fetch.")
            elif account_for_rep is False and user_id is not None:
                raise ValueError(
                    "account_for_rep is False but user_id is not None. Need account_for_rep to be True for fetching reputation to matter.")
            elif account_for_rep and user_id is not None:
                user = memory.user_reputation(user_id)
                self.overall_reputation = user.get_overall()
                self.user = user
            self.user_id = user_id

            # Determines if we're looking for slurs or a swear
            is_reptype_swears = True if 'fuck' in self.blacklist else False
            rep_value = self.user.get_swearing() if is_reptype_swears is True else self.user.get_slurs()

            # Determines sim ratio for sim check
            sim_ratio = 100
            for i in range(int(rep_value), 11):
                if rep_value < 0: # If rep is less than 0, make it stricter.
                    sim_ratio -= 3.2
                else:
                    sim_ratio -= 3.0
                # If the rep_value is less than -8, add a bit so they aren't attacked for every msg
            if rep_value <= -8:
                sim_ratio += 20

            self.sim_ratio = sim_ratio

        def heuristical(self) -> bool:
            '''
            Checks if a message contains a forbidden word. Returns True if it does, False if it doesn't.
            '''
            if self.content is None or self.content == "" or self.blacklist == []:
                return False

            components = automod.text_checkers.components(self.content, self.blacklist, account_for_rep=False, user_id=self.user_id, )

            if components.substring_check() is True:
                return True
            elif components.symbol_check() is True:
                return True
            elif components.equality_check() is True:
                return True
            elif components.wsw_check() is True:
                return True
            else:
                return False
    
        def repHeuristic(self) -> list:
            '''
            Much like the Heuristical checker, but instead this bases it off the stored trustability of the user.

            Returns:
                list: [bool, int, float, str]

                bool: True if a forbidden word was found, False if not.
                int: The index of the word found in the blacklist.
                float: The similarity ratio between the two strings if the similarity check was tripped. (-1 if not)
                str: The check that was tripped. (substring, symbol, equality, wsw, similarity)
            '''
            if self.content is None or self.content == "" or self.blacklist == []:
                return False

            assert self.user_id is not None, "User ID is None. Cannot check reputation without it."
            assert self.blacklist is not None, 'Blacklist must not be none'
            assert self.content is not None, 'Content must not be none'

            components = automod.text_checkers.components(
                self.content,
                self.blacklist,
                account_for_rep=True,
                user_id=self.user_id,
                sim_ratio=self.sim_ratio
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
                result = check()

                if result is False:
                    continue
                else:
                    result.append(f'check:{check.__name__.replace("_check", "")}')
                    return result
                
            return False

        class components:
            '''
            This class contains each check that we have.
            '''
            def __init__(self, content, blacklist, account_for_rep, user_id, sim_ratio=80):
                self.content = content
                self.blacklist = blacklist
                self.account_for_rep = account_for_rep
                self.user_id = user_id
                self.ratio = sim_ratio

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
                return False

            def symbol_check(self):
                '''
                Check for words with symbols/punctuation. eg, "Your such a sl!ur." Uses equality.

                Returns:
                    [bool, tuple(blacklisted_word, content_part)|-1, str]

                    bool: True if a forbidden word was found, False if not.
                    tuple: The blacklisted word and the content part that was found.
                '''
                nosymb_content = self.remove_symbols()
                # Could be None if the message was all punctuation
                if nosymb_content is not None:
                    for word in nosymb_content.split(" "):
                        for item in self.blacklist:
                            if word == item:
                                return [True, (item, word)]
                
                return False

            def equality_check(self):
                # Equality check. eg, "slur" == "slur"
                for word in self.content.split(" "):
                    for item in self.blacklist:
                        if word == item:
                            return [True, (item, word)]
                return False

            def wsw_check(self):
                content = self.content
                content_split = content.split(" ")
                content_count = len(content.split(" "))
                if content_count > 1:
                    index = 0
                    for word in content_split:
                        try:
                            part = word + content_split[index+1]
                        except IndexError:
                            break
                        for item in self.blacklist:
                            if item == part:
                                return [True, (item, part)]
                        index += 1
                    return False
                elif content_count == 1:
                    return False

            def similarity_check(self) -> list:
                '''
                Check for similarity. eg, "slur" == "sler"

                Returns:
                    list: [bool, str|None, float]

                    bool: True if a similar word was found, False if not.
                    tuple: The detected blacklisted word[0], the word which tripped it[1], and the similarity ratio[2].
                '''
                ratio = self.ratio
                assert ratio <= 100.0, f"Ratio must be less than or equal to 100. not {ratio}"
                assert ratio >= 0.0, f"Ratio must be greater than or equal to 0. not {ratio}"

                # Determines how similar 2 strings are by importing the SequenceMatcher class from difflib
                for word in self.content.split(" "):
                    for item in self.blacklist:
                        similarity = SequenceMatcher(None, a=word, b=item).ratio()
                        # Converts the similarity ratio from a range from 0-1 to a percentage from 0-100
                        similarity = similarity * 100
                        # Debug code. Uncomment to see the similarity ratio
                        # print(f"word: {word}\nitem: {item}\nsimilarity: {similarity}\nratio: {ratio}\n\nNEW CHECK\n\n")
                        if similarity >= ratio:
                            return [True, (item, word, similarity)]

                return False

    def gen_user_warning_embed(warning_title, user_id, check_result:list, is_admin=False):
        assert check_result is not None, "Check result must not be None"

        admin_warn_msg = (
            "You are an administrator on this server.\n"
            "Start acting like it and hold yourself accountable."
        )

        if check_result is None:
            return (hikari.Embed(
                    title=warning_title,
                    description="Automod has detected you broke the rules.",
                    color=colourless,
                    timestamp=datetime.datetime.now().astimezone()
                )
                .set_thumbnail(
                    os.path.abspath('library/Hammer.png')
                )
            )
        else:
            check_name = check_result[len(check_result)-1]
            word_found = check_result[1][1]

            desc = f"Automod has detected <@!{user_id}> broke the rules."
            if 'substring' in check_name:
                index_start = check_result[1][2][0]
                index_end = check_result[1][2][1]

                desc = f"<@{user_id}> You cannot say that here.\n"
                # Word found will be content if its substring check
                # Highlights the blacklisted word in the content with underlines and italics
                start_at = index_start - 10
                end_at = index_end + 10
                # Ensures there are no index errors
                if start_at < 0:
                    start_at = 0
                if end_at > len(word_found):
                    end_at = len(word_found)

                desc += f"\"{word_found[:index_start]}*__{word_found[start_at+3:end_at-3]}__*{word_found[index_end:]}\""
                # Censors the desc
                desc = automod.censor_text(desc)

            embed = (hikari.Embed(
                    title=warning_title,
                    description=desc,
                    color=colourless,
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
