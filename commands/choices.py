from util.arguments import Arguments
from discord.ext import commands
from shlex import split
import random


class Choices:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['choose'], description='Randomly picks a 1 of the given choices.')
    async def choices(self, *, msg):
        parser = Arguments(allow_abbrev=False, prog='choices')
        parser.add_argument('choices', nargs='+', help='The choices to randomly pick from.')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        choice = args.choices[random.SystemRandom().randint(0, len(args.choices) - 1)]
        await self.bot.say('**%s** has randomly been selected.' % choice)


def setup(bot):
    bot.add_cog(Choices(bot))
