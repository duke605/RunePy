from discord.ext import commands
from math import floor
from datetime import datetime


class Spotlight:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['featured', 'sl'],
                      description='Shows the currently featured minigame and that the next one will be.')
    async def spotlight(self):
        minigames = ('Pest Control', 'Soul Wars', 'Fist of Guthix', 'Barbarian Assault', 'Conquest', 'Fishing Trawler',
                     'The Great Orb Project', 'Flash Powder Factory', 'Castle Wars', 'Stealing Creation',
                     'Cabbage Facepunch Bonanza', 'Heist', 'Mobilising Armies', 'Barbarian Assault', 'Conquest',
                     'Fist of Guthix', 'Castle Wars', 'Pest Control', 'Soul Wars', 'Fishing Trawler',
                     'The Great Orb Project', 'Flash Powder Factory', 'Stealing Creation', 'Cabbage Facepunch Bonanza',
                     'Heist', 'Trouble Brewing', 'Castle Wars')

        ms = datetime.utcnow().timestamp() * 1000
        current = floor((((floor((ms / 1000) / (24 * 60 * 60))) - 49) % (3 * len(minigames))) / 3)
        days_until = 3 - ((floor((ms / 1000) / (24 * 60 * 60))) - 49) % (3 * len(minigames)) % 3
        next = current + 1 if current + 1 < len(minigames) else 0

        m = '**Current Featured**: %s.\n' % minigames[current]
        m += '**Next Featured**: %s in `%s` day%s.' % (minigames[next], days_until, 's' if days_until == 1 else '')

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(Spotlight(bot))
