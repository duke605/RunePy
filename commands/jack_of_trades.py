from discord.ext import commands
from util.arguments import Arguments
from util import choices
from shlex import split


class JackOfTrades:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='Shows the amount of exp gained from using a Jack of Trades aura.')
    async def jot(self, *, msg):
        parser = Arguments(allow_abbrev=False, prog='jot')
        parser.add_argument('type', choices=['legendary', 'normal', 'master', 'supreme'], help='The type the aura.')
        parser.add_argument('level', type=choices.between(1, 120),
                            help='The level the amount of exp will be granted to.')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        factor = {
            'normal': 1.5,
            'master': 2,
            'supreme': 2.5,
            'legendary':  5
        }

        xp = factor[args.type] * ((args.level**2) - (2 * args.level) + 100)
        m = "At level **{}** from a **{}** Jack of Trades aura, you'd gain **{:,}** XP.".format(args.level, args.type, xp)
        await self.bot.say(m)


def setup(bot):
    bot.add_cog(JackOfTrades(bot))
