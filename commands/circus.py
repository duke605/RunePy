from math import floor
from datetime import datetime
from discord.ext import commands
import discord


class Circus:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Shows where the circus is and where the next one will be.')
    async def circus(self):
        locations = ('Tree Gnome Stronghold', "Seers' Village", 'Catherby', 'Taverley', 'Edgeville', 'Falador',
                     'Rimmington', 'Draynor Village', 'Al Kharid', 'Lumbridge', 'Lumber Yard', "Gertrude's House")

        ms = round(datetime.utcnow().timestamp() * 1000, 0)
        current_location = floor((((floor((ms / 1000) / (24 * 60 * 60))) + 1) % (7 * len(locations))) / 7)
        days_until_next = 7 - ((floor((ms / 1000) / (24 * 60 * 60))) + 1) % (7 * len(locations)) % 7
        next_location = current_location + 1

        # Start from beginning
        next_location = next_location if next_location < len(locations) else 0
        current_location = locations[current_location]
        next_location = locations[next_location]

        # Building message
        e = discord.Embed()
        e.colour = 0x3572a7

        e.add_field(name='Current Location', value=current_location, inline=False)
        e.add_field(name='Next Location', value='%s in **%s** day%s.' %
                                                (next_location, days_until_next, 's' if days_until_next == 1 else ''), inline=False)
        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(Circus(bot))
