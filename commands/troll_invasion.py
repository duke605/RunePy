from util.arguments import Arguments
from discord.ext import commands
from util import choices
from shlex import split


class TrollInvasion:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['troll', 'trollinvasion'])
    async def invasion(self, *, msg):
        parser = Arguments(allow_abbrev=False, prog='invasion')
        parser.add_argument('level', type=choices.between(1, 120), help='The level to get the reward XP for.')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        xp = 8 * (20 / 20) * (args.level**2) - 2 * args.level + 100
        xp = int(xp) if xp % 1 == 0 else round(xp, 1)
        await self.bot.say("At level **{}**, fully completing Toll Invasion will yield **{:,}** XP.".format(args.level,
                                                                                                            xp))

def setup(bot):
    bot.add_cog(TrollInvasion(bot))
