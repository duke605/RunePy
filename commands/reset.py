from discord.ext import commands
from datetime import datetime
import math


class Reset:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Shows daily reset is.')
    async def reset(self):
        now = datetime.utcnow()
        then = datetime.utcnow().replace(hour=23, minute=59, second=59)
        delta = (then - now).seconds

        # Getting hours
        hours = math.floor(delta / 60 / 60)
        delta -= hours * 60 * 60

        # Getting minutes
        minutes = math.floor(delta / 60)
        delta -= minutes * 60

        # Getting seconds
        seconds = delta

        # Building message
        m = ''
        if hours > 0:
            m += ' **{:,}** hour{}'.format(hours, 's' if hours == 1 else '')

        if minutes > 0:
            m += ' **{:,}** minute{}'.format(minutes, 's' if minutes == 1 else '')

        if seconds > 0:
            m += ' **{:,}** second{}'.format(seconds, 's' if seconds == 1 else '')

        await self.bot.say('The game will reset in%s.' % m)


def setup(bot):
    bot.add_cog(Reset(bot))
