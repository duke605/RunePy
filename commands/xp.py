from util.arguments import Arguments
from shlex import split
from util import runescape
from discord.ext import commands


class Exp:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['exp'])
    async def xp(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='xp')
        parser.add_argument('level1', type=int, help='The lower of the two levels.')
        parser.add_argument('level2', type=int, help='The higher of the two levels.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        # Validating
        if args.level1 < 1 or args.level1 > 120:
            await self.bot.say('Level1 must be between 1 and 120.')
            return

        if args.level2 < 1 or args.level2 > 120:
            await self.bot.say('Level1 must be between 1 and 120.')
            return

        if args.level1 >= args.level2:
            await self.bot.say('Level1 must be less than level2.')
            return

        await self.bot.say('The total experience between levels **{:,}** and **{:,}** is **{:,}**.'
                      .format(args.level1, args.level2, runescape.exp_between_levels(args.level1, args.level2)))


def setup(bot):
    bot.add_cog(Exp(bot))