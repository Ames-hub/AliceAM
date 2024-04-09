# WebGUI Documentation
Basic Data about the WebGUI:
- Port: 7575
- ssl: Not in use
- Not usefully functional at the moment

The WebGUI will provide users an easy way to manage the bot.<br>
And ideally, an easy way to manage members of their guilds as well.

## Intended Features
- Easy to use interface
- Guild member management
- Logs viewer for guild events and bot events
- Bot Settings Management

## Not intended features
- The ability to turn off/on the bot.<br>
This is because bot.run is a blocking function (on all levels, even when in another process somehow.)<br>
So if the bot stops, everything stops. If I particularly hate myself one day, I might try to find a way around this.

# Current State
The WebGUI is not functional at the moment.<br>
It runs on port 0.0.0.0:7575, but has no content at all.