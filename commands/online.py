from util.runescape_util import get_players_online
from discord.ext import commands


class Online:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description='Shows the number of people playing Runescape.')
    async def online(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        players = await get_players_online()

        rs3_percent = round(players['rs3'] / players['total'] * 100, 1)
        osrs_percent = round(players['osrs'] / players['total'] * 100, 1)
        rsc_percent = round(players['rsc'] / players['total'] * 100, 1)

        await self.bot.say('**RS3 Players Online**: {:,} ({}%)\n'
                           '**OSRS Players Online**: {:,} ({}%)\n'
                           '**RS Classic Players Online**: {:,} ({}%)\n'
                           '**Total Players Online**: {:,}'
                           .format(players['rs3'], rs3_percent,
                                   players['osrs'], osrs_percent,
                                   players['rsc'], rsc_percent,
                                   players['total']))


def setup(bot):
    bot.add_cog(Online(bot))
