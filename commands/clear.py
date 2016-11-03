from discord.ext import commands
from util.arguments import Arguments
from shlex import split
import asyncio
from util.choices import between


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

        if args.self:
            await self.delete_self(ctx, args.num)
            return

        # Getting messages
        deleted = await self.bot.purge_from(ctx.message.channel, limit=args.num,
                        check=lambda m: m.author.id == self.bot.user.id or
                        m.content.startswith(self.bot.configurations[ctx.message.channel.server.id]['prefix'] or '`'))

        # Displaying the number of messages deleted
        m = await self.bot.say('Deleted **{:,}** messages.'.format(len(deleted)))
        await asyncio.sleep(5)
        await self.bot.delete_message(m)

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
