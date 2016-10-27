from util.runescape import get_item_for_name, get_item_alch_prices, add_metric_suffix
from matplotlib import pyplot, ticker
from datetime import datetime
from io import BytesIO
from db.models import Item, objects
from util.image_util import upload_to_imgur
from discord.ext import commands
from util.arguments import Arguments
from shlex import split
import matplotlib


class Price:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True,
                      description='Shows price information about an item as well as price history and alch prices.')
    async def price(self, ctx, *, msg: str):
        parser = Arguments(allow_abbrev=False, prog='price')
        parser.add_argument('name', nargs='+', help='The name if the item to get the price for.')
        parser.add_argument('-u', '--units', type=int, help="Multiplies the item's price by the units given.")
        parser.add_argument('-l', '--low-alch', action='store_true', help='Displays the low alch price for the item.')
        parser.add_argument('-H', '--high-alch', action='store_true', help='Displays the high alch price for the item.')
        parser.add_argument('-c', '--chart', type=int, choices=range(1, 7),
                            help="Plots the item's price history for number of given months.")

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
        item, history = await get_item_for_name(args.name)
        hist_vals = list(history['daily'].values())

        # Getting price change
        day_change = item.price - hist_vals[-2]
        one_month_change = item.price - hist_vals[-30]
        three_month_change = item.price - hist_vals[-90]
        six_month_change = item.price - hist_vals[-180]

        day_change_per = int(day_change / hist_vals[-2] * 100)
        one_month_change_per = int(one_month_change / hist_vals[-30] * 100)
        three_month_change_per = int(three_month_change / hist_vals[-90] * 100)
        six_month_change_per = int(six_month_change / hist_vals[-180] * 100)

        # Building message
        message = '**{}**: `{:,}` GP\n' \
                  '**Change in last 24 hours**: `{:,}` GP `{}%`\n' \
                  '**Change in last 30 days**: `{:,}` GP `{}%`\n' \
                  '**Change in last 90 days**: `{:,}` GP `{}%`\n' \
                  '**Change in last 180 days**: `{:,}` GP `{}%`' \
            .format(item.name, item.price, day_change, day_change_per, one_month_change, one_month_change_per,
                    three_month_change, three_month_change_per, six_month_change, six_month_change_per)

        # Totaling
        if args.units:
            message += '\n**{:,}x =** `{:,}` GP'.format(args.units, args.units * item.price)

        m = await self.bot.say(message)

        # Getting low and/or high alch price
        if args.high_alch or args.low_alch:
            alch_prices = await get_item_alch_prices(item.name, False)

            # Check if alch prices found
            if alch_prices:

                # Adding high alch price
                if args.high_alch:
                    message += '\n**High alch price**: `{:,}` GP'.format(alch_prices['high'])

                if args.low_alch:
                    message += '\n**Low alch price**: `{:,}` GP'.format(alch_prices['low'])

            # Alch prices not successful
            else:
                message += 'Alch prices could not be fetched.'

            await self.bot.edit_message(m, message)

        # Adding chart
        if args.chart:
            link = await Price.plot_history(history, args.chart, item.name)

            # Checking if plot was uploaded to imgur
            if not link:
                message += '\nChart could not be uploaded to imgur.'
            else:
                message += '\n%s' % link

            await self.bot.edit_message(m, message)

        # Checking if item is in DB
        if not await objects.execute(Item.select().where(Item.id == item.id).limit(1)):
            r = await objects.create(Item, id=item.id, price=item.price, updated_at=item.updated_at,
                                     updated_at_rd=item.updated_at_rd, name=item.name)

    @staticmethod
    async def plot_history(history, months, name):
        # Setting up data
        x = list(history['daily'].keys())[-30 * months:]
        x_av = list(history['average'].keys())[-30 * months:]
        y = list(history['daily'].values())[-30 * months:]
        y_av = list(history['average'].values())[-30 * months:]

        x_mix = list(history['daily'].keys())[-30 * months]
        x_max = list(history['daily'].keys())[-1]

        # Setting up figure
        fig = pyplot.figure()
        fig.set_figheight(6)
        fig.set_figwidth(7)

        # Formatting figure
        fig.patch.set_antialiased(True)
        fig.suptitle('Price history for %s' % name, fontsize=14, color='white')

        # Setting up axis
        ax = fig.add_subplot(111, axisbg='#2e3136')
        ax.plot(x, y, '#e1bb34', x_av, y_av, '#b2dbee')
        pyplot.xlim((int(x_mix), int(x_max)))

        # Formatting axis
        ax.get_yaxis().grid(color='#3e4146', linestyle='-')
        ax.get_xaxis().grid(color='#3e4146', linestyle='-')

        ax.tick_params(axis='x', pad=15)
        ax.tick_params(axis='y', pad=15)

        ax.spines['bottom'].set_color('#000000')
        ax.spines['top'].set_color('#000000')
        ax.spines['left'].set_color('#000000')
        ax.spines['right'].set_color('#000000')

        ax.get_yaxis().set_major_formatter(ticker.FuncFormatter(lambda _y, p: add_metric_suffix(_y)))
        ax.get_xaxis().set_major_formatter(
            ticker.FuncFormatter(lambda _x, p: datetime.fromtimestamp(_x / 1000.0).strftime('%b %d')))

        [i.set_color('white') for i in pyplot.gca().get_xticklabels()]
        [i.set_color('white') for i in pyplot.gca().get_yticklabels()]
        matplotlib.rc('font', **{'family': 'consola', 'size': 10})

        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor="#2e3136")
        pyplot.close()

        return await upload_to_imgur(buf)

    @staticmethod
    def get_change_arrow(num: int):
        if num < 0:
            return '\U00002b07'
        elif num > 0:
            return '\U00002b06'
        else:
            return '\U000027a1'


def setup(bot):
    bot.add_cog(Price(bot))
