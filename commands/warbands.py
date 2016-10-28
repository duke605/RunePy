from discord.ext import commands
from datetime import datetime, timedelta
from math import floor


class Warbands:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['wbs', 'wwbs'])
    async def warbands(self):
        monday = datetime.utcnow().replace(hour=2, minute=0, second=0, microsecond=0)
        monday -= timedelta(days=monday.weekday())
        delta = (datetime.utcnow() - monday).total_seconds() / 60 / 60 % 7

        # Getting distance
        hours = 7 - delta
        minutes = hours % 1 * 60
        seconds = minutes % 1 * 60

        # Cleaning numbers
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(floor(seconds))

        # Building message
        m = 'The next wilderness warband will being in'

        if hours:
            m += ' **%s** hour%s' % (hours, 's' if hours != 1 else '')

        if minutes:
            m += ' **%s** minute%s' % (minutes, 's' if minutes != 1 else '')

        if seconds:
            m += ' **%s** second%s' % (seconds, 's' if seconds != 1 else '')

        await self.bot.say(m + '.')


def setup(bot):
    bot.add_cog(Warbands(bot))
