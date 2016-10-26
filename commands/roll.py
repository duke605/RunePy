from discord.ext import commands
from util.arguments import Arguments
from util import choices
from shlex import split
import random


class Roll:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, *, msg):
        parser = Arguments(allow_abbrev=True, prog='roll')
        parser.add_argument('number', type=choices.between(2, 2**31-1),
                            help='The maximum number the roll can be (inclusive.)')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        x = random.SystemRandom().randint(1, args.number)
        await self.bot.say('\U0001f3b2 Rolled a **{:,}**'.format(x))


def setup(bot):
    bot.add_cog(Roll(bot))
