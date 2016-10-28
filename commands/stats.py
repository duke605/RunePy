from util.runescape import get_users_stats
from util.ascii_table import Table, Column
from util.image_util import text_to_image
from discord.ext import commands
from util.arguments import Arguments
from shlex import split


class Stats:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['stat', 'hiscores'],
                      description='Shows Runescape stats for a given user.')
    async def stats(self, ctx, *, msg: str):
        parser = Arguments(allow_abbrev=False, prog='stats')
        parser.add_argument('-i', '--image', action='store_true',
                            help='Displays the table as an image. (Useful for mobile)')
        parser.add_argument('name', nargs='+', help='The name of the character to get stats for.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        args.name = ' '.join(args.name)

        await self.execute(args)

    async def execute(self, args):
        stats = await get_users_stats(args.name)

        # Checking if the request was a success
        if not stats:
            await self.bot.say('Stats for **%s** could not be retrieved.' % args.name)
            return

        table = Table()
        table.set_title('VIEWING RS3 STATS FOR %s' % args.name.upper())
        table.set_headings('Skill', 'Level', 'Experience', 'Rank')

        # Adding rows
        for key in stats.keys():
            stat = stats[key]
            table.add_row(
                key.capitalize(),
                Column(stat['level'], 2),
                Column('{:,}'.format(stat['exp']), 2),
                Column('{:,}'.format(stat['rank']), 2))

        # Plain text
        text = str(table)
        if not args.image:
            await self.bot.say('```%s```' % text)
        else:
            link = await text_to_image(text)

            # Checking if table was uploaded
            if not link:
                await self.bot.say('Table could not be uploaded as an image to imgur.')
            else:
                await self.bot.say(link)


def setup(bot):
    bot.add_cog(Stats(bot))
