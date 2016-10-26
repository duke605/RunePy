from commands.lamp import Lamp
from discord.ext import commands
from util.arguments import Arguments
from shlex import split
from util.runescape import get_users_stats


class Statues:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def statues(self, *, msg):
        parser = Arguments(allow_abbrev=False, prog='statues')
        parser.add_argument('username', help='Your runescape username.')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        stats = await get_users_stats(args.username)

        # Checking if request was good
        if not stats:
            await self.bot.say('Stats for **%s** could not be retrieved.' % args.name)
            return

        # Getting exp rates
        lamps = Lamp.get_lamp_dict()
        con_xp = lamps['large'][min(stats['construction']['level'] - 1, 97)]
        prayer_xp = lamps['medium'][min(stats['prayer']['level'] - 1, 97)]
        slayer_xp = lamps['medium'][min(stats['slayer']['level'] - 1, 97)]

        # Building message
        m = '**Construction XP**: {:,}\n'.format(con_xp)
        m += '**Prayer XP**: {:,}\n'.format(prayer_xp)
        m += '**Slayer XP**: {:,}\n'.format(slayer_xp)
        m += 'For a total of **{:,}** Construction XP and either **{:,}** Prayer XP or **{:,}** Slayer XP when all 5 ' \
             'statues have been completed.'.format(con_xp * 5, prayer_xp * 5, slayer_xp * 5)

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(Statues(bot))
