from discord.ext import commands
from util.checks import is_owner
import sys


class Stop:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @is_owner()
    async def stop(self):
        await self.bot.say('Stopping...')
        await self.bot.logout()
        sys.exit(99)


def setup(bot):
    bot.add_cog(Stop(bot))
