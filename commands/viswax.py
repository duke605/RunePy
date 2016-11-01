from discord.ext import commands
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from util.ascii_table import Table, Column
import re


class VisWax:

    def __init__(self, bot):
        self.bot = bot
        self.cache = None

    @commands.command(pass_context=True, aliases=['wax'],
                      description='Shows the combination of runes needed for the Rune Goldberg Machine.')
    async def viswax(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        combo = await self.get_rune_combo()

        # Creating first rune table
        first_table = Table()
        first_table.set_title('FIRST RUNE')
        first_table.set_headings('Rune', 'Reported By')

        # Adding potential runes
        for rune, percent in combo['first']:
            first_table.add_row(rune, Column('%s%%' % percent, 2))

        # Creating first rune table
        second_table = Table()
        second_table.set_title('SECOND RUNE')
        second_table.set_headings('Rune', 'Reported By')

        # Adding potential runes
        for rune, percent in combo['second']:
            second_table.add_row(rune, Column('%s%%' % percent, 2))

        await self.bot.say('```%s\n%s```' % (str(first_table), str(second_table)))

    async def get_rune_combo(self):
        """
        Gets the rune combo from cache or direct from the site
        """

        # Checking if combo is in cache
        if self.cache and datetime.utcnow() < self.cache['expire']:
            return self.cache

        self.cache = {'first': [], 'second': []}

        # Getting html
        async with self.bot.whttp.get('http://warbandtracker.com/goldberg/index.php') as r:
            text = await r.text()

        soup = BeautifulSoup(text, 'html.parser')
        table = soup.find('h2', text='Detailed Rune Data').parent.find('table')
        first = table.find_all('tr')[1]
        second = table.find_all('tr')[3]

        # Looping through first potential runes
        for img in first.find_all('img'):
            alt_text = img.attrs['alt']
            rune, percent = re.search('^(.+?)\r\nReported by (.+?)%.$', alt_text, re.S).groups()

            self.cache['first'].append((rune, percent))

        # Looping through second potential runes
        for img in second.find_all('img'):
            alt_text = img.attrs['alt']
            rune, percent = re.search('^(.+?)\r\nReported by (.+?)%.$', alt_text, re.S).groups()

            self.cache['second'].append((rune, percent))

        self.cache['expire'] = datetime.utcnow() + timedelta(minutes=30)
        return self.cache


def setup(bot):
    bot.add_cog(VisWax(bot))
