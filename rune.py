from discord.ext import commands
from secret import BOT_TOKEN
from argparse import ArgumentParser
from shlex import split
from commands import stats_command, price_command, vos_command, portables_command
from discord import __version__
import asyncio

bot = commands.Bot(command_prefix='`')


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


@bot.command(pass_context=True, aliases=['voice'])
async def vos(ctx):
    await bot.send_typing(ctx.message.channel)
    await vos_command.execute(bot)


@bot.command(aliases=['info'])
async def about():
    await bot.say('__Author:__ Duke605\n'
                  '__Library:__ discord.py ('+__version__+')\n'
                  '__Version:__ 1.0.0\n'
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
async def clear(ctx):
    counter = 0

    # Getting messages
    async for m in bot.logs_from(ctx.message.channel):

        # Deleting my messages
        if m.author == bot.user:
            counter += 1
            await bot.delete_message(m)

    # Displaying the number of messages deleted
    m = await bot.say('Deleted **{:,}** messages.'.format(counter))
    await asyncio.sleep(5)
    await bot.delete_message(m)

bot.run(BOT_TOKEN)
