from discord.ext import commands
from datetime import datetime
from util.ascii_table import Table, Column
from math import floor
import discord


class RiseOfTheSix:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['riseofthesix'], description='Shows the current rotation for Rise of the Six.')
    async def rots(self):
        names = {
            'A': 'Ahrim',
            'D': 'Dharok',
            'G': 'Guthan',
            'K': 'Karil',
            'T': 'Torag',
            'V': 'Verac'
        }

        # Sweet baby jesus those rotations...
        rotations = (
            ((names['D'], names['T'], names['V']), (names['K'], names['A'], names['G'])),
            ((names['K'], names['T'], names['G']), (names['A'], names['D'], names['V'])),
            ((names['K'], names['G'], names['V']), (names['A'], names['T'], names['D'])),
            ((names['G'], names['T'], names['V']), (names['K'], names['A'], names['D'])),
            ((names['K'], names['T'], names['V']), (names['A'], names['G'], names['D'])),
            ((names['A'], names['G'], names['D']), (names['K'], names['T'], names['V'])),
            ((names['K'], names['A'], names['D']), (names['G'], names['T'], names['V'])),
            ((names['A'], names['T'], names['D']), (names['K'], names['G'], names['V'])),
            ((names['A'], names['D'], names['V']), (names['K'], names['T'], names['G'])),
            ((names['K'], names['A'], names['G']), (names['T'], names['D'], names['V'])),
            ((names['A'], names['T'], names['G']), (names['K'], names['D'], names['V'])),
            ((names['A'], names['G'], names['V']), (names['K'], names['T'], names['D'])),
            ((names['K'], names['A'], names['T']), (names['G'], names['D'], names['V'])),
            ((names['K'], names['A'], names['V']), (names['D'], names['T'], names['G'])),
            ((names['A'], names['T'], names['V']), (names['K'], names['D'], names['G'])),
            ((names['K'], names['D'], names['G']), (names['A'], names['T'], names['V'])),
            ((names['D'], names['T'], names['G']), (names['K'], names['A'], names['V'])),
            ((names['G'], names['D'], names['V']), (names['K'], names['A'], names['T'])),
            ((names['K'], names['T'], names['D']), (names['A'], names['G'], names['V'])),
            ((names['K'], names['D'], names['V']), (names['A'], names['T'], names['G']))
        )

        ms = round(datetime.utcnow().timestamp() * 1000)
        current = floor((ms / 1000) / (24 * 60 * 60)) % 20

        # Creating table
        e = discord.Embed()
        e.colour = 0x3572a7

        e.add_field(name='West', value='\n'.join(rotations[current][0]))
        e.add_field(name='East', value='\n'.join(rotations[current][1]))

        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(RiseOfTheSix(bot))
