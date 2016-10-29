from discord.ext import commands
from util.checks import is_owner
import sys
import discord


class Restart:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @is_owner()
    async def restart(self):
        await self.bot.say('Restarting...')

        # Telling bot log
        await self.bot.send_message(discord.Object(id='241984924616359936'), 'Restarting...')

        await self.bot.logout()
        await sys.exit(98)


def setup(bot):
    bot.add_cog(Restart(bot))
