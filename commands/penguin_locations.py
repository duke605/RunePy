from bs4 import BeautifulSoup
from datetime import datetime
from discord.ext import commands
import re


class PenguinLocations:

    def __init__(self, bot):
        self.bot = bot
        self.cache = {}

    @commands.command(aliases=['pengs', 'peng'], pass_context=True)
    async def penglocs(self, ctx):
        await self.bot.send_typing(ctx.message.channel)

        data = await self._get_peng_locs()

        m = '__**World 60 Penguin Locations**__:\n\n'
        m += "```py\n'%s'```\n" % data['note']
        for i, loc in enumerate(data['worlds']):
            m += '%s.) __**%s**__: %s (%s point%s)\n' \
                 '%s\n\n' % (i+1, loc['title'], loc['type'], loc['points'], 's' if loc['points'] > 1 else '', loc['desc'])

        await self.bot.say(m)

    async def _get_peng_locs(self):

        # Checking if the bot contains a valid copy
        if self.cache and self.cache['expire'] > datetime.utcnow():
            return self.cache

        self.cache = {'worlds': []}

        # Getting peng data
        async with self.bot.whttp.get('http://world60pengs.com/includes/including.php?inid=pengdata') as r:
            soup = BeautifulSoup(await r.text(), 'html.parser')

        # Getting the titles
        for i, head in enumerate(soup.find_all('div', attrs={'class': 'penghead'})):
            title, type, points = re.search('^.+?\s(.+?)\s-\s(.+?)\s\((\d+?)\s', head.text).groups()
            self.cache['worlds'].append({'title': title, 'type': type, 'points': int(points), 'desc': head.next_sibling.text})

        # Getting note
        self.cache['note'] = soup.find('div', attrs={'class': 'rednote'}).text.strip()

        # Getting expiry
        expire = soup.find('div', attrs={'class': 'contenttitle'}).text.strip()
        date, month = re.match('^(\d+?)\s(.+?)\s', expire[::-1]).groups()

        # Reversing back
        date = date[::-1]
        month = datetime.strptime(month[::-1], '%B').month

        # Month is in new year
        dt = datetime.utcnow()
        if month == 1 and dt.month == 12:
            expire = datetime(dt.year+1, month, int(date))
        else:
            expire = datetime(dt.year, month, int(date), 23, 59, 59)

        self.cache['expire'] = expire
        return self.cache


def setup(bot):
    bot.add_cog(PenguinLocations(bot))