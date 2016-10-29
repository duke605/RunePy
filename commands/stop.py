from discord.ext import commands
from util.checks import is_owner
import sys
import discord


class Stop:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @is_owner()
    async def stop(self):
        await self.bot.say('Stopping...')

        # Telling bot log
        await self.bot.send_message(discord.Object(id=241984924616359936), 'Stopping...')

        await self.bot.logout()
        sys.exit(99)


def setup(bot):
    bot.add_cog(Stop(bot))
