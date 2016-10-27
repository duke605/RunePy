from discord.ext import commands
from datetime import datetime
from math import floor


class Sinkhole:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Shows when the next sinkhole will spawn.')
    async def sinkhole(self):
        d = datetime.utcnow()
        seconds_until = 3600 - (d.minute + 30) % 60 * 60 - d.second
        minutes_until = floor(seconds_until / 60)

        if minutes_until == 0:
            await self.bot.say('The next Sinkhole will begin in **1** hour.')
        else:
            await self.bot.say('The next Sinkhole will begin in **%s** minute%s.' % (minutes_until,
                                                                                     's' if minutes_until > 0 else ''))


def setup(bot):
    bot.add_cog(Sinkhole(bot))
