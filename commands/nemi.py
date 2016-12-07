from discord.ext import commands
from secret import REDDIT_BASIC, REDDIT_PASSWORD, REDDIT_USERNAME
from datetime import datetime, timedelta
from math import floor
import re
import discord
import html


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
        world, node_size = re.search('^w(?:orld )?(\d+?) (?:map\s)?-? ?(.+?)$', m['title'], re.I).groups()
        delta = (datetime.utcnow() - datetime.utcfromtimestamp(m['created_utc'])).total_seconds()
        link = m['url']

        # Formatting time
        days = floor(delta / 86400)
        hours = floor(delta % 86400 / 3600)
        minutes = floor(delta % 86400 % 3600 / 60)
        seconds = round(delta % 86400 % 3600 % 60)

        time = ''
        if days:
            time += '{:,}d'.format(days)
        if hours:
            time += ' {:,}h'.format(hours)
        if minutes:
            time += ' {:,}m'.format(minutes)
        if seconds:
            time += ' {:,}s'.format(seconds)

        e = discord.Embed()
        e.colour = 0x3572a7

        e.add_field(name=html.unescape(node_size), value='World %s' % world)
        e.add_field(name='Active for', value=time)
        e.set_image(url=link)

        await self.bot.say(embed=e)

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
            'User-Agent': 'Python:RunePy:v%s (by /u/duke605)' % self.bot.cogs['About'].version
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
