# Automoderation functions.py
from .botapp import bot
from .postgre import postgre
import lightbulb, hikari, datetime, os
colourless = bot.d['colourless']

class automod:
    class checkers:
        def heuristical(content:str, blacklist:list[str]) -> bool:
            '''
            Checks if a message contains a forbidden word. Returns True if it does, False if it doesn't.
            '''
            if content == None or content == "" or blacklist == []:
                return False

            return False
    
        def repHeuristic(content:str, blacklist:list[str], user_id) -> bool:
            '''
            Much like the Heuristical checker, but instead this bases it off the stored trustability of the user.
            '''
        
        class components:
            '''
            This class contains each check that we have.
            '''
            def __init__(self, content: str, blacklist: list[str], account_for_rep: bool, user_id:int=None) -> None:
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
                    raise ValueError("account_for_rep is True but user_id is None. Need User_ID to know who's reputation to fetch.")
                elif account_for_rep is False and user_id is not None:
                    raise ValueError("account_for_rep is False but user_id is not None. Need account_for_rep to be True for fetching reputation to matter.")
                elif account_for_rep and user_id is not None:
                    self.reputation = postgre.reputation.get(user_id)
                self.user_id = user_id

            def remove_symbols(self):
                content = self.content
                nosymb_content = None
                for word in content:
                    if word.isalnum() is False:
                        nosymb_content = content.replace(word, '')
                return nosymb_content
            
            def substring_check(self):
                # Basic 'substring' check. eg "slur" in "You ufw**slur**jig"
                for word in self.blacklist:
                    if word in self.content:
                        return True

            def punct_check(self):
                '''
                Check for words with punctuation. eg, "Your such a sl!ur"
                '''
                nosymb_content = self.remove_symbols()
                # Could be None if the message was all punctuation
                if nosymb_content is not None:
                    for word in self.blacklist:
                        if word in nosymb_content:
                            return True

            def equality_check(self):
                # Equality check. eg, "slur" == "slur"
                if self.content in self.blacklist:
                    return True
                nosymb_content = self.remove_symbols()
                if nosymb_content is not None:
                    if nosymb_content in self.blacklist:
                        return True

            def wsw_check(self):
                # Check for words with spaces. eg, "Your such a sl ur For real!"
                # 'WsW check' (word, space, word check)
                content = self.content
                if len(content.split(" ")) > 1:
                    for word in content:
                        # From content[0] and onwards, join the next part of the string and check for equality
                        if word == " ":
                            continue
                        else:
                            try:
                                part = word + content[content.index(word)+1]
                                for item in self.blacklist:
                                    if item == part:
                                        return True
                            except IndexError:
                                pass
                else:
                    content = content.split(" ")
                    content = f"{content[0]}{content[1]}"
                    for word in self.blacklist:
                        if word == content:
                            return True

    def gen_warning_embed(warning_title):
        ethics_msg = [
            "If this is a false positive/Mistake, please contact the server staff.",
            "Otherwise, Please be mindful that these are real people you are talking to and not just text on a screen. ",
            "\n*They deserve the respect you would like to be given yourself.* So please respect them enough to follow rules."
        ]

        return (hikari.Embed(
                title=warning_title,
                description="Automod has detected you broke the rules.",
                color=colourless,
                timestamp=datetime.datetime.now().astimezone()
            )
            .add_field(
                name="Ethics of You",
                value=" ".join(ethics_msg)
            )
            .set_thumbnail(
                os.path.abspath('library/Hammer.png')
            )
        )

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(lightbulb.Plugin(__name__))