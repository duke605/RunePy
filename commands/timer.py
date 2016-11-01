from discord.ext import commands
import asyncio
from util.arguments import Arguments
from shlex import split
import re


class Timer:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['remind', 'reminder'], pass_context=True,
                      description='Sets a timer with an optional note to remind you of something.')
    async def timer(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='timer')
        parser.add_argument('time', help='How long to set the timer for.\n'
                                         'h = hours\n'
                                         'm = minutes\n'
                                         's = seconds\n'
                                         'Eg. 14h5m17s is will notify you in 14 hours 17 minutes and 17 seconds.')
        parser.add_argument('note', nargs='*', help='An optional message that will be displayed when the time is up.')

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        # Getting offsets
        hours = (int(re.search('(\d+)h', args.time).group(1)) if re.search('(\d+)h', args.time) else 0)
        minutes = (int(re.search('(\d+)m', args.time).group(1)) if re.search('(\d+)m', args.time) else 0)
        seconds = (int(re.search('(\d+)s', args.time).group(1)) if re.search('(\d+)s', args.time) else 0)

        m = 'Timer set for'
        if hours:
            m += ' {:,} hour{}'.format(hours, 's' if hours != 1 else '')
        if minutes:
            m += ' {:,} minute{}'.format(minutes, 's' if minutes != 1 else '')
        if seconds:
            m += ' {:,} second{}'.format(seconds, 's' if seconds != 1 else '')

        await self.bot.say(m + '.')
        await asyncio.sleep((hours * 3600) + (minutes * 60) + seconds)

        if args.note:
            await self.bot.say('%s, Your timer is up: **%s**' % (ctx.message.author.mention, ' '.join(args.note)))
        else:
            await self.bot.say('%s, Your timer is up' % ctx.message.author.mention)


def setup(bot):
    bot.add_cog(Timer(bot))
