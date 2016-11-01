from secret import GOOGLE_API_KEY
from datetime import datetime
from util.arguments import Arguments
from discord.ext import commands
from shlex import split
from util.choices import enum
import re


class Portables:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['ports', 'port', 'portable'], description='Shows portable locations.')
    async def portables(self, ctx, *, msg: str = ''):
        ports = ('fletcher', 'crafter', 'brazier', 'sawmill', 'forge', 'range', 'well')

        parser = Arguments(allow_abbrev=False, prog='portables')
        parser.add_argument('portable', nargs='?',
                            type=enum(
                                fletcher=('fletchers', 'fletch'),
                                crafter=('crafters', 'craft'),
                                brazier=('braziers', 'braz'),
                                sawmill=('saw', 'mill', 'sawmills'),
                                forge=('forges'),
                                range=('ranges', 'cook'),
                                well=('wells')
                            ),
                            help='Selects a type of portable to search for.')

        await self.bot.send_typing(ctx.message.channel)

        try:
            args = parser.parse_args(split(msg))
        except SystemExit:
            await self.bot.say('```%s```' % parser.format_help())
            return
        except Exception as e:
            await self.bot.say('```%s```' % str(e))
            return

        await self.execute(args, ports)

    async def execute(self, args, ports):
        host = 'https://sheets.googleapis.com/v4/spreadsheets'
        sheet_id = '16Yp-eLHQtgY05q6WBYA2MDyvQPmZ4Yr3RHYiBCBj2Hc'
        sheet_name = 'Home'
        range = 'A16:G18'
        url = '%s/%s/values/%s!%s?key=%s' % (host, sheet_id, sheet_name, range, GOOGLE_API_KEY)

        # Getting cells
        async with self.bot.whttp.get(url) as r:

            # Checking request
            if r.status != 200:
                await self.bot.say('Google sheet could not be reached.')
                return

            json = await r.json()

        t = re.search('(\d+?)/(\d+?)/(\d+?), (\d+):(\d+)', json['values'][2][1]).groups()
        last_update = datetime.utcnow() - datetime(int(t[2]) + 2000, int(t[1]), int(t[0]), int(t[3]), int(t[4]))
        author = json['values'][2][3]

        # Formatting update
        if last_update.seconds >= 86400:
            last_update = '{:,}d'.format(round(last_update.seconds / 86400))
        elif last_update.seconds >= 3600:
            last_update = '{:,}h'.format(round(last_update.seconds / 3600))
        elif last_update.seconds >= 60:
            last_update = '{:,}m'.format(round(last_update.seconds / 60))
        else:
            last_update = '{:,}s'.format(last_update.seconds)

        # Replacing abbrev
        for i, worlds in enumerate(json['values'][1]):
            worlds = worlds.lower()

            worlds = re.sub('\sca', ' Combat Academy', worlds)
            worlds = re.sub('\sprif', ' Prifddinas', worlds)
            worlds = re.sub('\sp(?!rif)', ' Prifddinas', worlds)
            worlds = re.sub('\ssp', ' Shanty Pass', worlds)
            worlds = re.sub('\sba', ' Barbarian Assault', worlds)
            worlds = re.sub('\sbu', ' Burthrope Assault', worlds)
            worlds = re.sub('\scw', ' Castle Wars', worlds)

            json['values'][1][i] = worlds

        # Outputting only the portable the user wants
        if args.portable:
            worlds = json['values'][1][ports.index(args.portable)]

            await self.bot.say('**%ss**: %s\n**Last Updated**: %s ago by %s' % (args.portable.capitalize(), worlds,
                                                                                 last_update, author))
            return

        # Outputting all portables
        m = ''
        for i, worlds in enumerate(json['values'][1]):
            m += '**%ss**: %s\n' % (ports[i].capitalize(), worlds)

        m += '**Last Updated**: %s ago by %s' % (last_update, author)
        await self.bot.say(m)


def setup(bot):
    bot.add_cog(Portables(bot))
