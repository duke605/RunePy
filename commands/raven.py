from discord.ext import commands
from datetime import datetime


class Raven:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Shows if a raven is currently in Prifddinas.')
    async def raven(self):
        days_until = (datetime.utcnow() - datetime(2014, 10, 4)).days % 13

        if days_until == 0:
            m = 'There currently is a raven in Prifddinas!'
        else:
            m = 'There currently is no raven in Prifddinas. The next one spawns in **%s** day%s.' \
                % (13 - days_until, 's' if 13 - days_until != 1 else '')

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(Raven(bot))
