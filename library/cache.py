# A Cache system for the bot. Reduces the amount of requests to the DB and to Discord.
from library.botapp import bot

class cache:
    """
    Always returns -1 if the cache is empty for the requested data.
    """
    @staticmethod
    def cache_perms(uuid, guid, permissions):
        bot.d['permissions_cache'][f'{uuid}-{guid}'] = permissions
        return True

    @staticmethod
    def get_permissions(uuid, guid):
        try:
            data = bot.d['permissions_cache'][f'{uuid}-{guid}'] 
            return data # Returns the permissions if they exist
        except KeyError:
            return -1

    @staticmethod
    def cache_dm_channel(user_id, channel_id):
        bot.d['dm_cache'][user_id] = channel_id
        return True

    @staticmethod
    def get_dm_channel(user_id):
        try:
            data = bot.d['dm_cache'][user_id]
            return data
        except KeyError:
            return -1

    @staticmethod
    def clear_cache():
        bot.d['permissions_cache'] = {}
