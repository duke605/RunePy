from discord.ext import commands
from datetime import datetime


class BigChinchompa:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['chompa', 'bigchinchompa'],
                      description='Shows the next time the Big Chinchompa will spawn.')
    async def bigchin(self):
        dt = datetime.utcnow()
        seconds_until = 3600 - (dt.minute + 30) % 60 * 60 - dt.second
        minutes_until = seconds_until // 60

        if minutes_until == 0:
            await self.bot.say('The next Big Chinchompa will start in **1** hour.')
        else:
            await self.bot.say('The next Big Chinchompa will start in **%s** minute%s.'
                               % (minutes_until, 's' if minutes_until == 1 else ''))


def setup(bot):
    bot.add_cog(BigChinchompa(bot))
