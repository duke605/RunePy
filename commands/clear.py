from discord.ext import commands
from util.arguments import Arguments
from shlex import split
from util.choices import between
from collections import Counter
import re
import asyncio
import discord


class Clear:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['clean'],
                      description='Clears any messages from this bot as well as command calls.')
    async def clear(self, ctx, *, msg='100'):
        parser = Arguments(allow_abbrev=False, prog='clear')
        parser.add_argument('num', nargs='?', type=between(1, 100), default=100
                            , help='The number of messages to search through.')
        parser.add_argument('-s', '--self', action='store_true', help='Only deletes messages from this bot.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        # Only deleting messages from bot
        if args.self:
            await self.delete_self(ctx, args.num)
            return

        def check(m):
            """Checks if the message should be deleted"""

            pattern = '^(?:%s)' % '|'.join(re.escape(c) for c in self.bot.command_prefix(self.bot, ctx.message))
            return m.author.id == self.bot.user.id or m.id == ctx.message.id or re.search(pattern, m.content)

        # Getting messages
        deleted = Counter(m.author.id for m in await self.bot.purge_from(ctx.message.channel, limit=args.num, check=check))
        total = sum(deleted.values())
        server = ctx.message.channel.server

        # Displaying the number of messages deleted
        e = discord.Embed()
        e.colour = 0x3572a7
        e.title = 'Deleted {:,} message{}.'.format(total, 's' if total != 1 else '')
        e.description = '\n'.join('**{:,}** {}'.format(c[1], server.get_member(c[0]).name) for c in deleted.most_common())

        await self.bot.say(embed=e, delete_after=5)

    async def delete_self(self, ctx, limit):
        counter = 0

        # Getting messages from this bot
        async for m in self.bot.logs_from(ctx.message.channel, limit):
            if m.author.id == self.bot.user.id:
                await self.bot.delete_message(m)
                counter += 1

        m = await self.bot.say('Deleted **{:,}** messages.'.format(counter))
        await asyncio.sleep(5)
        await self.bot.delete_message(m)


def setup(bot):
    bot.add_cog(Clear(bot))
