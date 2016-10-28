from discord.ext import commands
from util.arguments import Arguments
from shlex import split
import asyncio
import argparse


class Clear:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['clean'],
                      description='Clears any messages from this bot as well as command calls.')
    async def clear(self, ctx, *, msg='100'):

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

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        # Getting messages
        deleted = await self.bot.purge_from(ctx.message.channel, limit=args.num,
                                            check=lambda m: m.author.id == self.bot.user.id or
                                                            m.content.startswith(self.bot.command_prefix))

        # Displaying the number of messages deleted
        m = await self.bot.say('Deleted **{:,}** messages.'.format(len(deleted)))
        await asyncio.sleep(5)
        await self.bot.delete_message(m)


def setup(bot):
    bot.add_cog(Clear(bot))
