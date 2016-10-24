from discord.ext import commands
from secret import BOT_TOKEN
from argparse import ArgumentParser
from shlex import split
from commands import stats_command, price_command
from discord import __version__

bot = commands.Bot(command_prefix='!')


class Arguments(ArgumentParser):

    def error(self, message):
        raise RuntimeError(message)


@bot.event
async def on_ready():
    print('==============================')
    print('{:^31}'.format('Connected.'))
    print('==============================')


@bot.command(pass_context=True, aliases=['stat'])
async def stats(ctx, *, msg: str):
    parser = Arguments(allow_abbrev=False, prog='stats')
    parser.add_argument('-i', '--image', action='store_true', help='Displays the table as an image. (Useful for mobile)')
    parser.add_argument('name', nargs='+', help='The name of the character to get stats for.')

    await bot.send_typing(ctx.message.channel)

    try:
        args = parser.parse_args(split(msg))
    except SystemExit:
        await bot.say('```%s```' % parser.format_help())
        return
    except Exception as e:
        await bot.say('```%s```' % str(e))
        return

    args.name = ' '.join(args.name)

    await stats_command.execute(bot, args)


@bot.command(pass_context=True)
async def price(ctx, *, msg: str):
    parser = Arguments(allow_abbrev=False, prog='price')
    parser.add_argument('name', nargs='+', help='The name if the item to get the price for.')
    parser.add_argument('-u', '--units', type=int, help="Multiplies the item's price by the units given.")
    parser.add_argument('-c', '--chart', type=int, choices=range(1, 7),
                        help="Plots the item's price history for number of given months.")

    await bot.send_typing(ctx.message.channel)

    try:
        args = parser.parse_args(split(msg))
    except SystemExit:
        await bot.say('```%s```' % parser.format_help())
        return
    except Exception as e:
        await bot.say('```%s```' % str(e))
        return

    args.name = ' '.join(args.name)

    await price_command.execute(bot, args)


@bot.command(aliases=['info'])
async def about():
    await bot.say('__Author:__ Duke605\n'
                  '__Library:__ discord.py ('+__version__+')\n'
                  '__Version:__ 1.0.0\n'
                  '__Github Repo:__ <https://github.com/duke605/RunePy>\n'
                  '__Official Server:__ <https://discord.gg/uaTeR6V>')

bot.run(BOT_TOKEN)
