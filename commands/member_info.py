from util.arguments import Arguments
from discord.ext import commands
from shlex import split
from util.runescape import get_member_info


class MemberInfo:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['userinfo'], pass_context=True, description='Shows information about a user.')
    async def memberinfo(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='memberinfo')
        parser.add_argument('username', nargs='+', help='The name of the user to the the info of.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        # Gluing username together
        args.username = ' '.join(args.username)
        info = await get_member_info(args.username)

        # Building message
        m = '**Username**: %s\n' % info['name']

        if info['title']:

            # Attaching to end
            if info['isSuffix']:
                formatt = '{}{}' if info['title'].startswith(',') else '{} {}'

            # Attaching to start
            else:
                formatt = formatt = '{1}{0}' if info['title'].endswith(',') else '{1} {0}'

            full_name = formatt.format(info['name'], info['title'])
            m += '**Full Name**: %s\n' % full_name
            m += '**Title**: %s\n' % info['title']

        if info['clan']:
            m += '**Clan**: %s (%s)' % (info['clan'], 'Recruiting' if info['recruiting'] else 'Not recruiting')

        await self.bot.say(m)


def setup(bot):
    bot.add_cog(MemberInfo(bot))