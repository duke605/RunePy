from discord.ext import commands
from discord import __version__


class About:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['info'])
    async def about(self):
        await self.bot.say('__Author:__ Duke605\n'
                           '__Library:__ discord.py (%s)\n'
                           '__Version:__ 1.1.3\n'
                           '__Github Repo:__ <https://github.com/duke605/RunePy>\n'
                           '__Official Server:__ <https://discord.gg/uaTeR6V>' % __version__)


def setup(bot):
    bot.add_cog(About(bot))