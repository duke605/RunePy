from discord.ext import commands
from util.checks import is_owner
import sys


class Restart:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @is_owner()
    async def restart(self):
        await self.bot.say('Restarting...')
        await self.bot.logout()
        await sys.exit()


def setup(bot):
    bot.add_cog(Restart(bot))
