from util.arguments import Arguments
from shlex import split
from util import runescape
from discord.ext import commands
from util.choices import between


class Exp:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['exp'], description='Shows the amount of exp between 2 given levels.')
    async def xp(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='xp')
        parser.add_argument('level1', type=between(1, 120), help='The lower of the two levels.')
        parser.add_argument('level2', type=between(1, 120), help='The higher of the two levels.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        if args.level1 >= args.level2:
            await self.bot.say('Level1 must be less than level2.')
            return

        await self.bot.say('The total experience between levels **{:,}** and **{:,}** is **{:,}**.'
                      .format(args.level1, args.level2, runescape.exp_between_levels(args.level1, args.level2)))


def setup(bot):
    bot.add_cog(Exp(bot))
