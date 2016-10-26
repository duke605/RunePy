from discord.ext import commands
from datetime import datetime


class BigChinchompa:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['chompa', 'bigchinchompa'])
    async def bigchin(self):
        dt = datetime.utcnow()
        seconds_unti = 3600 - (dt.minute + 30) % 60 * 60 - dt.second
        minutes_unti = seconds_unti // 60

        if minutes_unti == 0:
            await self.bot.say('The next Big chinchompa will start in **1** hour.')
        else:
            await self.bot.say('The next Big chinchompa will start in **%s** minute%s.'
                               % (minutes_unti, 's' if minutes_unti > 1 else ''))


def setup(bot):
    bot.add_cog(BigChinchompa(bot))
