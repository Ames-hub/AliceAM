<div align="center">

# AliceAM

![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)

Alice **A**uto**M**oderation is at your service.<br>[Support Server](https://discord.gg/HkKAsgvCzt)
</div>

# What is Alice?
Alice Is an AutoModeration (AM) bot designed for Discord.<br>
It was built with the idea of having a main "Alice" [Which anyone at all can invite](https://discord.com/api/oauth2/authorize?client_id=1198234471804182548&permissions=8&scope=bot+applications.commands)<br>
But also a bot, which anyone can easily selfhost and add their own plugins to without much difficulty or even modify the bot's code entirely.

# Features
AliceAM has a variety of Qualities and Features, some of which include
- AutoModeration (Experimental)
- A Webgui (WIP)
- An API (WIP)
- Easily able to add custom commands/plugins
- No obfuscation of code
- Easy to set up

[Click me to see the full feature list](https://github.com/Ames-hub/AliceAM/blob/main/documentation/FEATURES.md)

# How do I selfhost Alice?
Step 1. Have/Get a Discord Bot Token.<br>
If you don't have this token, you can get it at [The Discord Developer portal](https://discord.com/developers/applications/) by clicking "new application"

Step 2. Clone this repository into a directory of your choosing which we have permission for. <br>

Step 3. Run main.py using Python 3.12 (higher/lower versions of python untested)<br>
You can do this by running the following command in the terminal
```
python3.12 main.py
```
Step 4. It will take you through a setup process if this is the first time you've run the program
<br>It will ask for the following information.
- The token you got in step 1
- Prefix you want the bot to use (Default is //)