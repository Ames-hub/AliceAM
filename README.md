<div align="center">

# AliceAM
Alice **A**uto**M**oderation is at your service.
</div>

# What is Alice?
Alice Is an AutoModeration (AM) bot designed for Discord.<br>
It was built with the idea of having a main "Alice" [Which anyone at all can invite](https://discord.com/api/oauth2/authorize?client_id=1198234471804182548&permissions=8&scope=bot+applications.commands)<br>
But also a bot, which anyone can easily selfhost and add their own plugins to without much difficulty or even modify the bot's code entirely.

# How do I selfhost Alice?
The first step is to, in the root folder of the project, make a file called 'secrets.env'<br>
Then enter in this text to the file we just made, replacing YOUR_TOKEN with your discord application's bot token.
```
TOKEN=YOUR_TOKEN
```
If you don't have this token, you can get it at [The Discord Developer portal](https://discord.com/developers/applications/) by clicking "new application"

Now onto the topic of running the bot.<br>
The most recommended way is through the use of a Python 3.11 Docker container.<br>
(I will make my own docker build file for AliceAM soon- Probably- 24/1/2024 is the date I promised this)

Otherwise, you can just run the python file and it'll take you through a basic setup. This works fine.

## Setting up Data Storage
Alice Has the option of using 2 methods of storage.<br>
Option 1 is through Json files. This is the fallback should PostgreSQL not be setup.<br>
Otherwise, we have Option 2. PostgreSQL.

To setup Option 1 (Json files), Simply tell the setup that you don't want to use PostgreSQL.<br>
It'll do what's left.

To setup Option 2 (PostgreSQL Database), Tell the setup you want to use PostgreSQL and then in the secrets.env file<br>
Enter the following details, changing the placeholders with what they should be. The relevant ones are all-caps
```
TOKEN=The token you entered beforehand
DB_HOST=YOUR_HOST_MACHINES_IP_OR_DOMAIN
DB_PORT=YOUR_HOSTS_PORT
DB_USER=YOUR_DB_USERNAME
DB_PASSWORD=YOUR_SECURE_PASSWORD
```
It is recommended you don't use the root account for the DB username, but I won't stop you.

