from discord.ext import commands
from util.arguments import Arguments
from shlex import split
from util.runescape import get_users_alog
from util.ascii_table import Table


class AdventureLog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['adventurelog', 'advlog'],
                      description='Shows the adventurers log for a given user.')
    async def alog(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='alog')
        parser.add_argument('username', nargs='+', help='Your Runescape username.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        args.username = ' '.join(args.username)
        items = await get_users_alog(args.username)

        # Checking if alog could be fetched
        if not items:
            await self.bot.say('**%s\'s** adventure log could not be fetched.' % args.username)
            return

        table = Table()
        table.set_title('VIEWING ADVENTURE LOG FOR %s' % args.username.upper())
        table.set_headings('Achievement', 'Date')

        # Adding items to rows
        for item in items:
            table.add_row(item['title'], item['date'].strftime('%a, %d %b %Y'))

        await self.bot.say('```%s```' % str(table))


def setup(bot):
    bot.add_cog(AdventureLog(bot))
