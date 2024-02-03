class data_tables:
    '''
    A class of dictionaries to be put as templates in Json files for the bot to use.
    '''
    GUILD_DT = {
        'antiswear': {
            'enabled': False,
        },
        'antislur': {
            'enabled': True,
        },
        'antispam': {
            'enabled': False,
            'mps_limit': 5, # Messages per second limit
        },
    }

    USER_DT = {
        # The less the number, the more they are known to swear.
        # Descends to a minimum of -10.0 and a maximum of 10.0
        'reputation': {
            'swearing': 0.0,
            'slurs': 0.0,
        },
    }

    # For localsetting.json
    SETTINGS_DT = {
        'use_postgre': False,
        'first_start': True,
        'prefix': None
    }