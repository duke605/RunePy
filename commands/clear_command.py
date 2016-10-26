from util.globals import bot
from util.arguments import Arguments
from shlex import split
import asyncio
import argparse


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
    deleted = await bot.purge_from(ctx.message.channel, limit=args.num, check=lambda m: m.author == bot.user or
                                                                            m.content.startswith(bot.command_prefix))

    # Displaying the number of messages deleted
    m = await bot.say('Deleted **{:,}** messages.'.format(len(deleted)))
    await asyncio.sleep(5)
    await bot.delete_message(m)