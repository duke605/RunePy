from util.globals import http
from datetime import datetime, timedelta
from secret import TWITTER_BEARER_TOKEN
import re

DISTRICTS = ('Cadarn', 'Amlodd', 'Ithell', 'Hefin', 'Meilyr', 'Trahaearn', 'Iorwerth', 'Crwys')

async def execute(bot):
    district_stats = await get_active_districts()
    potential = [d for d in DISTRICTS if d not in district_stats['active'] and d not in district_stats['previous']]

    m = '**Active districts:** %s and %s.\n' % district_stats['active']
    m += '**Previous districts:** %s and %s.\n' % district_stats['previous']
    m += '**Potential upcoming districts:** {}, {}, {}, and {}.'.format(*potential)

    await bot.say(m)

async def get_active_districts():
    """
    Gets a cached version of the district state if it's not expired or gets it directly from
    the twitter api

    :return:
    The active and previous districts
    """

    pattern = 'The Voice of Seren is now active in the (.+?) and (.+?) districts at .+? UTC.'

    # Checking if tweets still value
    if globals().get('tweets') and globals()['tweets']['expire'] > datetime.now():
        return globals()['tweets']

    # Building request
    params = {'screen_name': 'JagexClock', 'count': 10}
    headers = {'Authorization': 'Bearer %s' % TWITTER_BEARER_TOKEN}

    async with http.get('https://api.twitter.com/1.1/statuses/user_timeline.json', params=params, headers=headers) as r:

        # Checking if repose was good
        if r.status != 200:
            return None

        json = await r.json()

        # Filtering out tweets
        filtered = [t for t in json if re.search(pattern, t['text'])]
        filtered = filtered[:2]

        expire = datetime.now()
        expire = datetime(expire.year, expire.month, expire.day, expire.hour + 1, 1)

        globals()['tweets'] = {
            'active': re.search(pattern, filtered[0]['text']).groups(),
            'previous': re.search(pattern, filtered[1]['text']).groups(),
            'expire': expire
        }

        return globals()['tweets']