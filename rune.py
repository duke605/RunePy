from discord.ext import commands
from secret import BOT_TOKEN
from shlex import split
from commands import stats_command, price_command, vos_command, portables_command, peng_command, circus_command
from discord import __version__
from util import runescape
from datetime import datetime
import math
import asyncio
import argparse

bot = commands.Bot(command_prefix='`')


class Arguments(argparse.ArgumentParser):

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


@bot.command(pass_context=True, aliases=['voice'])
async def vos(ctx):
    await bot.send_typing(ctx.message.channel)
    await vos_command.execute(bot)


@bot.command(aliases=['info'])
async def about():
    await bot.say('__Author:__ Duke605\n'
                  '__Library:__ discord.py ('+__version__+')\n'
                  '__Version:__ 1.0.8\n'
                  '__Github Repo:__ <https://github.com/duke605/RunePy>\n'
                  '__Official Server:__ <https://discord.gg/uaTeR6V>')


@bot.command(pass_context=True, aliases=['ports', 'port', 'portable'])
async def portables(ctx, *, msg: str=''):
    parser = Arguments(allow_abbrev=False, prog='portables')
    parser.add_argument('portable', nargs='?', choices=portables_command.PORTS, type=str.lower,
                        help='Selects a type of portable to search for.')

    await bot.send_typing(ctx.message.channel)

    try:
        args = parser.parse_args(split(msg))
    except SystemExit:
        await bot.say('```%s```' % parser.format_help())
        return
    except Exception as e:
        await bot.say('```%s```' % str(e))
        return

    await portables_command.execute(bot, args)


@bot.command(pass_context=True, aliases=['clean'])
async def clear(ctx, *, msg='100'):

    # Tests if a number is between certain constraints
    def test(s):
        s = int(s)

        # Checking if the number is within range
        if s < 1 or s > 100:
            raise argparse.ArgumentTypeError('must be between 1 and 100.')

        return s

    parser = Arguments(allow_abbrev=False, prog='clear')
    parser.add_argument('num', nargs='?', type=test, default=100
                        , help='The number of messages to search through.')

    await bot.send_typing(ctx.message.channel)

    try:
        args = parser.parse_args(split(msg))
    except SystemExit:
        await bot.say('```%s```' % parser.format_help())
        return
    except Exception as e:
        await bot.say('```%s```' % str(e))
        return

    # Getting messages
    counter = 0
    async for m in bot.logs_from(ctx.message.channel, args.num):

        # Deleting my messages
        if m.author == bot.user:
            counter += 1
            await bot.delete_message(m)

    # Displaying the number of messages deleted
    m = await bot.say('Deleted **{:,}** messages.'.format(counter))
    await asyncio.sleep(5)
    await bot.delete_message(m)


@bot.command(aliases=['pengs', 'peng'], pass_context=True)
async def penglocs(ctx):
    await bot.send_typing(ctx.message.channel)
    await peng_command.execute(bot)


@bot.command(pass_context=True, aliases=['exp'])
async def xp(ctx, *, msg):
    parser = Arguments(allow_abbrev=False,prog='xp')
    parser.add_argument('level1', type=int, help='The lower of the two levels.')
    parser.add_argument('level2', type=int, help='The higher of the two levels.')

    await bot.send_typing(ctx.message.channel)

    try:
        args = parser.parse_args(split(msg))
    except SystemExit:
        await bot.say('```%s```' % parser.format_help())
        return
    except Exception as e:
        await bot.say('```%s```' % str(e))
        return

    # Validating
    if args.level1 < 1 or args.level1 > 120:
        await bot.say('Level1 must be between 1 and 120.')
        return

    if args.level2 < 1 or args.level2 > 120:
        await bot.say('Level1 must be between 1 and 120.')
        return

    if args.level1 >= args.level2:
        await bot.say('Level1 must be less than level2.')
        return

    await bot.say('The total experience between levels **{:,}** and **{:,}** is **{:,}**.'
                  .format(args.level1, args.level2, runescape.exp_between_levels(args.level1, args.level2)))


@bot.command()
async def invite():
    await bot.say('https://discordapp.com/oauth2/authorize?client_id=%s&scope=bot&permissions=84992' % bot.user.id)


@bot.command()
async def reset():
    now = datetime.utcnow()
    then = datetime.utcnow().replace(hour=23, minute=59, second=59)
    delta = (then - now).seconds

    # Getting hours
    hours = math.floor(delta / 60 / 60)
    delta -= hours * 60 * 60

    # Getting minutes
    minutes = math.floor(delta / 60)
    delta -= minutes * 60

    # Getting seconds
    seconds = delta

    # Building message
    m = ''
    if hours > 0:
        m += ' **{:,}** hour{}'.format(hours, 's' if hours > 1 else '')

    if minutes > 0:
        m += ' **{:,}** minute{}'.format(minutes, 's' if minutes > 1 else '')

    if seconds > 0:
        m += ' **{:,}** second{}'.format(seconds, 's' if seconds > 1 else '')

    await bot.say('The game will reset in%s.' % m)


@bot.command()
async def circus():
    await circus_command.execute(bot)

bot.run(BOT_TOKEN)
