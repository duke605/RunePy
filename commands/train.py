from discord.ext import commands
from util.runescape import get_users_stats, get_exp_between_levels
from util.arguments import Arguments
from util.choices import between, enum, minimum
from shlex import split
from db.models import Method, objects
from util.ascii_table import Table, Column
from math import ceil


class Train:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['training'])
    async def train(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='train')

        parser.add_argument('skill', type=enum(
            agility=['agil'], crafting=['craft'], firemaking=['fm'], herblore=['herb'], mining=['mine'],
            smithing=['smith'], woodcutting=['wc'], construction=['con'], divination=['div'], fishing=['fish'],
            hunter=['hunt'], prayer=['pray'], summoning=['summon', 'sum', 'summ'], cooking=['cook'],
            farming=['farm'], fletching=['fletch'], magic=['mage'], runecrafting=['rc'], thieving=['thiev', 'theiving']
        ), help='The name of the skill you wish to train.')

        parser.add_argument('level', type=between(2, 120), help='The level you wish to reach.')
        parser.add_argument('username', nargs='+', help='Your Runescape username.')
        parser.add_argument('-l', '--limit', type=between(1, 15), default=10,
                            help='The number of training methods per page.')
        parser.add_argument('-p', '--page', type=minimum(1), default=1, help='The page of results to return.')
        parser.add_argument('-i', '--image', type=minimum(1), default=1,
                            help='Displays the table as an image. (Useful for mobile).')
        parser.add_argument('-s', '--order', nargs='+', type=enum('number-', 'number', 'level', 'level-', 'exp', 'exp-',
                                                                 'name', 'name-'),
                            help='Sorts the results in the order specified. Add a \'-\' to the end of the order string '
                                 'to specify descending. Eg. number-', default=['number'])

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
        await self.execute(args)

    async def execute(self, args):
        stats = await get_users_stats(args.username)

        # Checking if username found
        if not stats:
            await self.bot.say('Stats for **%s** could not be retrieved.' % args.username)
            return

        stat = stats[args.skill]

        # Doing db stuff
        exp_needed = get_exp_between_levels(1, args.level)
        exp_needed -= stat['exp']
        count = await objects.count(Method
                                    .select()
                                    .where(Method.skill == args.skill)
                                    .where(Method.level <= stat['level']))

        training_methods = await objects.execute(
            Method.raw(
                'SELECT id, skill, level, name, exp, '
                'CEIL((%s/exp)) as "number" '
                'FROM methods '
                'WHERE skill = %s '
                'AND level <= %s '
                'ORDER BY {} '
                'LIMIT %s,%s'.format(Train.build_order_by_query(args.order)),
                exp_needed,
                args.skill,
                stat['level'],
                (args.page - 1) * args.limit,
                args.limit
            )
        )
        total_pages = int(ceil(count/args.limit))

        table = Table()
        table.set_title('SHOWING METHODS FOR {} ({:,}/{:,})'.format(args.skill.upper(), args.page, total_pages))
        table.set_headings('Number', 'Name', 'Level', 'XP')

        # Adding rows
        for method in training_methods:
            table.add_row(
                Column('{:,}'.format(int(method.number)), 2),
                method.name,
                Column(method.level, 2),
                Column('{:,}'.format(method.exp), 2)
            )

        await self.bot.say('```%s```' % str(table))

    @staticmethod
    def build_order_by_query(order):
        query = ''

        # Looping through orders
        for i, o in enumerate(order):

            # DESC
            if o.endswith('-'):
                query += '%s DESC' % o[:-1]
            elif o.endswith('+'):
                query += '%s ASC' % o[:-1]
            else:
                query += '%s ASC' % o

            if i < len(order) - 1:
                query += ', '

        return query


def setup(bot):
    bot.add_cog(Train(bot))
