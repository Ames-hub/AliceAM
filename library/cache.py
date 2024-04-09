# A Cache system for the bot. Reduces the amount of requests to the DB and to Discord.
from library.botapp import bot

class cache:
    '''
    Always returns -1 if the cache is empty for the requested data.
    '''
    def cache_perms(uuid, guid, permissions):
        bot.d['permissions_cache'][f'{uuid}-{guid}'] = permissions

    def get_permissions(uuid, guid):
        try:
            data = bot.d['permissions_cache'][f'{uuid}-{guid}'] 
            return data # Returns the permissions if they exist
        except:
            return -1
        
    def clear_cache():
        bot.d['permissions_cache'] = {}
