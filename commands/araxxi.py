from math import floor
from datetime import datetime
from discord.ext import commands
import discord


class Arraxi:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['rax', 'araxxor', 'arax'], description='Shows the current rotation for Arraxi/Araxxor.')
    async def araxxi(self):
        araxxi_rotations = [
            'Minions',
            'Acid',
            'Darkness'
        ]

        ms = int(datetime.utcnow().timestamp() * 1000)
        current_rotation = floor((((floor(floor(ms / 1000) / (24 * 60 * 60))) + 3) % (4 * len(araxxi_rotations))) / 4)
        days_until_next = 4 - ((floor((ms / 1000) / (24 * 60 * 60))) + 3) % (4 * len(araxxi_rotations)) % 4
        next_rotation = current_rotation + 1

        # Resenting next location
        next_rotation = next_rotation if next_rotation < len(araxxi_rotations) else 0

        # Building message
        e = discord.Embed()
        e.colour = 0x3572a7

        e.add_field(name='Currently Closed', value='Path **%s** - **%s**' % (current_rotation + 1, araxxi_rotations[current_rotation]),
                    inline=False)
        e.add_field(name='Next Closed', value='Path **%s** - **%s** in %s days.' % (next_rotation + 1, araxxi_rotations[next_rotation],
                                                                                    days_until_next), inline=False)
        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(Arraxi(bot))
