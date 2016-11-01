from discord.ext import commands
from db.models import Configuration as Config, objects
from util.arguments import Arguments
from util.choices import between
from shlex import split


class Configuration:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['configuration', 'configure'])
    @commands.check(lambda ctx: not ctx.message.channel.is_private
                                and (ctx.message.author.id == ctx.message.channel.server.owner.id
                                     or ctx.message.author.id == '136856172203474944'
                                     or ctx.message.channel.permissions_for(ctx.message.author).administrator))
    async def config(self):
        pass

    @config.command(pass_context=True, aliases=['trigger'])
    async def prefix(self, ctx, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='config prefix')
        parser.add_argument('prefix', nargs='?', type=between(1, 3, False),
                            help='The character(s) that prefixes a command call. Leaving this argument out will reset '
                                 'the command prefix to default.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        configs = self.bot.configurations[ctx.message.channel.server.id]
        con = Config()
        con.server_id = ctx.message.channel.server.id

        # Resetting trigger
        if not args.prefix:
            configs['prefix'] = '`'
            con.prefix = None
            await objects.update(con, only=['prefix'])
            await self.bot.say('Command prefix has been **reset**.')
            return

        # Setting new trigger
        configs['prefix'] = args.prefix
        con.prefix = args.prefix
        await objects.update(con, only=['prefix'])
        await self.bot.say('Command prefix has been **updated**.')


def setup(bot):
    bot.add_cog(Configuration(bot))
