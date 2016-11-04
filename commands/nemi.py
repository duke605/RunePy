from discord.ext import commands
from secret import REDDIT_BASIC, REDDIT_PASSWORD, REDDIT_USERNAME
from datetime import datetime, timedelta
from math import floor
import re


class Nemi:

    def __init__(self, bot):
        self.bot = bot
        self.token = None
        self.expire = None

    @commands.command(aliases=['nemiforest'], pass_context=True,
                      description='Displays the most recent at least 9/9 Nemi Forest.')
    async def nemi(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        m = await self.get_map()

        # Checking if a map could be fetched
        if not m:
            await self.bot.say('Reddit\'s API could not be accessed.')
            return

        # Prepping data
        world, node_size = re.search('^[wW](?:orld\s)?(\d+?)\s-\s?(.+?)$', m['title']).groups()
        delta = (datetime.utcnow() - datetime.utcfromtimestamp(m['created_utc'])).total_seconds()
        link = m['url']

        # Formatting time
        days = floor(delta / 86400)
        hours = floor(delta % 86400 / 3600)
        minutes = floor(delta % 86400 % 3600 / 60)
        seconds = round(delta % 86400 % 3600 % 60)

        time = ''
        if days:
            time += '**{:,}** day{}'.format(days, 's' if days != 1 else '')
        if hours:
            time += ' **{:,}** hour{}'.format(hours, 's' if hours != 1 else '')
        if minutes:
            time += ' **{:,}** minute{}'.format(minutes, 's' if minutes != 1 else '')
        if seconds:
            time += ' **{:,}** second{}'.format(seconds, 's' if seconds != 1 else '')

        await self.bot.say('Active **%s** Nemi forest on **world %s**. Posted %s ago.\n'
                           '%s' % (node_size, world, time.strip(), link))

    async def get_reddit_token(self):
        """
        Gets the stupid an annoying 1 hour token from reddit
        """

        # Checking if other token is valid
        if self.expire and self.expire > datetime.now():
            return self.token

        h = {'authorization': 'basic %s' % REDDIT_BASIC}
        p = {'grant_type': 'client_credentials', 'username': REDDIT_USERNAME, 'password': REDDIT_PASSWORD}

        async with self.bot.whttp.post('https://www.reddit.com/api/v1/access_token', headers=h, data=p) as r:
            json = await r.json()

            # Checking if response was good
            if r.status != 200:
                return None

        # Caching token
        self.token = json['access_token']
        self.expire = datetime.now() + timedelta(seconds=json['expires_in']-10)
        return json['access_token']

    async def get_map(self):
        """
        Gets the latest nemi forest map from reddit
        """
        token = await self.get_reddit_token()

        # Checking if the token could be fetched
        if not token:
            return None

        headers = {
            'Authorization': 'bearer %s' % token,
            'User-Agent': 'Python:RunePy:v1.1.28 (by /u/duke605)'
        }

        # Getting posts from reddit
        async with self.bot.whttp.get('https://oauth.reddit.com/r/NemiForest/new', headers=headers) as r:
            json = await r.json()

            # Checking response
            if r.status != 200:
                return None

        # Filtering non-maps
        maps = [m['data'] for m in json['data']['children']
                if m.get('data')
                and (not m['data'].get('link_flair_css_class') or 'depleted' not in m['data']['link_flair_css_class'])
                and re.search('^[wW](?:orld\s)?\d+\s', m['data']['title'])]

        # Checking if there are any maps
        if not maps:
            return None

        return maps[0]


def setup(bot):
    bot.add_cog(Nemi(bot))
