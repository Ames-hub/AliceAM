<div align="center">

# AliceAM
Alice **A**uto**M**oderation is at your service.<br>[Support Server](https://discord.gg/HkKAsgvCzt)
</div>

# What is Alice?
Alice Is an AutoModeration (AM) bot designed for Discord.<br>
It was built with the idea of having a main "Alice" [Which anyone at all can invite](https://discord.com/api/oauth2/authorize?client_id=1198234471804182548&permissions=8&scope=bot+applications.commands)<br>
But also a bot, which anyone can easily selfhost and add their own plugins to without much difficulty or even modify the bot's code entirely.

# Features
Alice AM has a variety of Qualities and Features, some of which include
- AutoModeration
- A Webgui (WIP)
- An API (WIP)
- Easily able to add custom commands/plugins
- No obfuscation of code
- Easy to setup

# How do I selfhost Alice?
Step 1. Have/Get a Discord Bot Token.<br>
If you don't have this token, you can get it at [The Discord Developer portal](https://discord.com/developers/applications/) by clicking "new application"

Step 2. Clone this repository into a directory of your choosing which we have permission for. <br>

Step 3. Run main.py using Python 3.11 (higher/lower versions of python untested)<br>
You can do this by running the following command in the terminal
```
python3.11 main.py
```
Step 4. It will take you through a setup process if this is the first time you've ran the program
<br>It will ask for the following information.
- The token you got in step 1
- Prefix you want the bot to use (Default is !!)
- If you want to use PostgreSQL for data storage or Json files (Postgre Recommended)<br>

Assuming you decide to setup PostgreSQL, It will ask for the following information
- Host of the PostgreSQL server
- Port of the PostgreSQL server
- The username Alice should use to connect to the database
- The password associated with the username
- The name of the database Alice should use<br>

However, if you do not use Postgre, there is no further setup.<br>
If you are unlucky, you may have to manage file restrictions however as it will default to Json files for memory.

## Setting up Data Storage
Alice Has the option of using 2 methods of storage.<br>
Option 1 is through Json files. This is the fallback should PostgreSQL not be setup.<br>
Otherwise, we have Option 2. PostgreSQL.

To setup Option 1 (Json files), Simply tell the setup that you don't want to use PostgreSQL.<br>
It'll do what's left.

To setup Option 2 (PostgreSQL Database), Tell the setup you want to use PostgreSQL<br>
It'll handle asking data from you and setting up the database for you.

## Handling setup errors
If for some reason, the setup crashes and you can't make it work, then do this handling.<br>
In a secrets.env file in the root directory<br>
Enter the following details, changing the placeholders with what they should be.
```
TOKEN=YOUR_TOKEN
DB_HOST=YOUR_HOST_MACHINES_IP_OR_DOMAIN
DB_PORT=YOUR_HOSTS_PORT
DB_USERNAME=YOUR_DB_USERNAME
DB_PASSWORD=YOUR_SECURE_PASSWORD
```
It is recommended you don't use the root account for the DB username, but I won't stop you.<br>
If you don't intend to use PostgreSQL, then you can choose not to include the DB_HOST, DB_PORT, DB_USERNAME, and DB_PASSWORD fields
or leave them as blank

Once that is done, in the root directory, make a file called `settings.json`<br>
It should look like this
```json
{
    "use_postgre": false,
    "first_start": false,
    "prefix": "!!"
}
```
Change the `use_postgre` to true if you want to use PostgreSQL, otherwise, leave it as false.<br>
Remember, If all else fails, the bot is free and open source. you can apply your own bug fix.<br>
However, if you are not too technical, you can always ask for help in the [Support Server](https://discord.gg/HkKAsgvCzt)