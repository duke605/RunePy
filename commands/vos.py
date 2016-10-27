from datetime import datetime, timedelta
from secret import TWITTER_BEARER_TOKEN
from discord.ext import commands
import re


class VoiceOfSeren:

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @commands.command(pass_context=True, aliases=['voice'], description='Shows information about the voice of Seren.')
    async def vos(self, ctx):
        districts = ('Cadarn', 'Amlodd', 'Ithell', 'Hefin', 'Meilyr', 'Trahaearn', 'Iorwerth', 'Crwys')

        await self.bot.send_typing(ctx.message.channel)

        district_stats = await self._get_active_districts()
        potential = [d for d in districts if d not in district_stats['active'] and d not in district_stats['previous']]

        m = '**Active districts:** %s and %s.\n' % district_stats['active']
        m += '**Previous districts:** %s and %s.\n' % district_stats['previous']
        m += '**Potential upcoming districts:** {}, {}, {}, and {}.'.format(*potential)

        await self.bot.say(m)

    async def _get_active_districts(self):
        """
        Gets a cached version of the district state if it's not expired or gets it directly from
        the twitter api

        :return:
        The active and previous districts
        """

        pattern = 'The Voice of Seren is now active in the (.+?) and (.+?) districts at .+? UTC.'

        # Checking if tweets still value
        if self.cache and self.cache['tweets']['expire'] > datetime.now():
            return self.cache['tweets']

        # Building request
        params = {'screen_name': 'JagexClock', 'count': 10}
        headers = {'Authorization': 'Bearer %s' % TWITTER_BEARER_TOKEN}

        async with self.bot.whttp.get('https://api.twitter.com/1.1/statuses/user_timeline.json', params=params,
                                      headers=headers) \
                as r:

            # Checking if repose was good
            if r.status != 200:
                return None

            json = await r.json()

            # Filtering out tweets
            filtered = [t for t in json if re.search(pattern, t['text'])]
            filtered = filtered[:2]

            self.cache['tweets'] = {
                'active': re.search(pattern, filtered[0]['text']).groups(),
                'previous': re.search(pattern, filtered[1]['text']).groups(),
                'expire': (datetime.now() + timedelta(hours=1)).replace(minute=1, second=0)
            }

            return self.cache['tweets']


def setup(bot):
    bot.add_cog(VoiceOfSeren(bot))
