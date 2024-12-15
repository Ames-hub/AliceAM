<div align="center">

# AliceAM Features

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

Alice **A**uto**M**oderation is at your service.<br>[Support Server](https://discord.gg/HkKAsgvCzt)
</div>

# Features

### Moderation

## Heuristic Check
- **FULLY OPERATIONAL**<br>
Definition: "proceeding to a solution by trial and error or by rules that are only loosely defined."<br>
Alice works very much on this principle.<br><br>
As it feels weird to actually swear in the documentation<br>
We will be using the word "heck" as a substitute for swear words.<br><br>
Here are the Methods Alice uses to determine behavior:
  - Equality Check:<br>
  Alice checks if a word in a message is equal to a banned word.
  - Substring Check:<br>
  Checks if a word is hidden within a message and contains a banned word. Such as "ee***heck***ee"
  - Symbol Check:<br>
  Removes symbols that may be used to hide bad language. Like "he##ck" or "#heck"
  - Word-Space-Word Check<br>
  This detects if someone tries to hide a banned word by putting spaces between the letters.<br>
    Like "he ck"
  - Similarity Check (WIP):<br>
    This detects if someone tries to hide a banned word by using similar characters such as
    "h3ck"

### Anti Swear
- **FULLY OPERATIONAL**: Automatically detects and deletes messages containing swear words.

### Anti Slur
- **FULLY OPERATIONAL**: Automatically detects and deletes messages containing racist slurs,
homophobic slurs and transphobic slurs. List may not be exhaustive, if it is not, you can
add to it by using a built-in command

### Anti Spam
- **Inoperational**: Automatically detects and deletes spam messages.
- **Work In Progress**: Currently being worked on. Too many false positives
to the point of being unusable.

### Alice Learns from you.
- **Crowdsourced Ratings**<br>
Alice uses crowdsourced ratings to filter out false positives.<br>
This means that if Alice makes a mistake, you can help her learn from it.<br> Where ever this
is possible, Alice will ask for the community's input on whether an action was correct or not.

### AI Moderation
Credit to: `Falconsai` on Huggingface for the NSFW Image AI detection models<br>
Credit to: Ollama for the Ollama3.2 LLM chat model.

- **Operational**: Alice uses AI To keep community's safe.<br>
Alice can detect messages that other moderation systems would not catch.<br>
- **Computer Vision**: Alice can use computer vision to detect NSFW images.<br>
Does not usually detect NSFL yet. (don't google it, its gore.)
- **Text classification**: Alice can detect insults using text classification.<br>
This feature is experimental, and depends upon good crowdsourced ratings of its accuracy.
<br><br>
- ***DISCLAIMER***: THIS PROJECT DOES NOT USE YOUR PRIVATE OR PUBLIC DATA TO TRAIN THE AI.
  <br><br>
  *If you have any questions or concerns about privacy,<br>please open an issue on GitHub or join the support server*
  <br><br>
  *Your privacy is respected by this project, and we intend to keep it that way.*<br><br>

### Quality of Life
### WebGUI
- **Work In Progress**: A Control Dashboard accessible via the web.<br>
Think like carlbot's dashboard, or MEE6's dashboard, but for Alice and with some additional
control's and features.
- Low priority as of now, as the bot is still in early development.

### API
- **Inoperational**: An API to interact with the bot programmatically.
There is no API yet, as for the Alice Project its self, it's not needed yet and
is a low priority.

### Custom Commands/Plugins
- **Easily Extendable**: Add your own commands and plugins with ease.

### Code Transparency
- **No Obfuscation**: The code is open and easy to understand.

### Easy Setup
- **User-Friendly**: Simple steps to get the bot up and running.

<div align="center">
  <img src="https://img.shields.io/github/stars/Ames-hub/AliceAM?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/Ames-hub/AliceAM?style=social" alt="GitHub forks">
</div>