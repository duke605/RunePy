from discord.ext import commands
from datetime import datetime
from bs4 import BeautifulSoup
import discord
import re


class VisWax:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['wax'],
                      description='Shows the combination of runes needed for the Rune Goldberg Machine.')
    async def viswax(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        combo = await self.get_rune_combo()

        # Checking if updated
        if not combo:
            await self.bot.say("Today's rune combinations have no been updated yet. Please try again later.")
            return

        e = discord.Embed()
        e.colour = 0x3572a7

        e.add_field(name='First Rune', value='\n'.join(combo[0]), inline=False)
        e.add_field(name='Second Rune', value='\n'.join(combo[1]), inline=False)

        await self.bot.say(embed=e)

    async def get_rune_combo(self):
        """
        Gets the rune combo from cache or direct from the site
        """

        # Getting html
        async with self.bot.whttp.get('http://services.runescape.com/m=forum/forums.ws?75,76,387,65763383') as r:
            text = await r.text()

        soup = BeautifulSoup(text, 'html.parser')
        post = soup.find_all('span', attrs={'class': 'forum-post__body'})[1].text.lower()
        day = re.search('combination\s+for\s+.+\s+(\d+).+;', post).group(1)
        slot1, slot2 = re.search('slot 1:- (.+?) slot 2:- (.+?) slot', post).groups()

        # Checking if runes updated yet
        if int(day) != datetime.utcnow().day:
            return None

        # Cleaning up the data
        slot1 = [VisWax.clean_format(r.strip().capitalize()) for r in slot1.split('-')]
        slot2 = [VisWax.clean_format(r.strip().capitalize()) for r in slot2.split('-')]

        return slot1, slot2

    @staticmethod
    def clean_format(s: str):

        # No IM/HCIM runes to clean
        if '(' not in s:
            return s

        try:

            # Trying to parse properly formated data
            rune, alts = re.search('(.+)\s?\((.+)\)', s).groups()
        except:

            # Have to put this is because the idiot forgets to close his brackets sometimes
            # (you know who forgets to close brackets? Psychopaths that's who)
            rune, alts = re.search('(.+)\s?\((.+)', s).groups()

        alts = [a.strip().capitalize() for a in alts.split(',')]

        return '%s (%s)' % (rune, ', '.join(alts))


def setup(bot):
    bot.add_cog(VisWax(bot))
