from secret import GOOGLE_API_KEY
from datetime import datetime
from util.arguments import Arguments
from discord.ext import commands
from shlex import split
from util.choices import enum
from collections import namedtuple
import re
import urllib
import discord


class Portables:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _format_time_detla(delta):
        """
        Formats a time delta to look like twitter stye "ago"
        """

        if delta.seconds >= 86400:
            delta = '{:,}d'.format(round(delta.seconds / 86400))
        elif delta.seconds >= 3600:
            delta = '{:,}h'.format(round(delta.seconds / 3600))
        elif delta.seconds >= 60:
            delta = '{:,}m'.format(round(delta.seconds / 60))
        else:
            delta = '{:,}s'.format(delta.seconds)

        return delta

    @staticmethod
    def _format_data(json):
        date_format = '%d %b, %H:%M'
        struct = namedtuple('Portable', ['author', 'last_updated', 'locations', 'time'])

        # Populating portables
        time = datetime.strptime(json['values'][2][1], date_format).replace(year=datetime.utcnow().year)
        author = json['values'][2][3]
        last_updated = Portables._format_time_detla(datetime.utcnow() - time)
        locations = {'fletchers': {}, 'crafters': {}, 'braziers': {}, 'sawmills': {}, 'forges': {}, 'ranges': {}, 'wells': {}}

        # Finding all worlds for portables
        for i in range(7):
            worlds = locations[json['values'][0][i].strip().lower()]
            locs = json['values'][1][i]

            # Checking if no worlds
            if 'host needed' in locs.lower() or 'n/a' in locs.lower():
                continue

            # Separating locations
            for location in re.findall('\d+.+?(?:CA|MG|PRIFF|PRIF|P|BU|SP|CW|BA)', locs.upper()):
                name = location.split(' ')[-1]
                name = re.sub('(?:PRIFF|PRIF)', 'P', name, re.I)
                worlds[name] = re.findall('\d+', location)

        return struct(author=author, locations=locations, last_updated=last_updated, time=time)

    @staticmethod
    async def _get_portables(http):
        """
        Gets data from the google spreadsheet
        """

        host = 'https://sheets.googleapis.com/v4/spreadsheets'
        sheet_id = '16Yp-eLHQtgY05q6WBYA2MDyvQPmZ4Yr3RHYiBCBj2Hc'
        sheet_name = 'Home'
        range = 'A16:G18'
        url = '%s/%s/values/%s!%s?key=%s' % (host, sheet_id, sheet_name, range, GOOGLE_API_KEY)

        # Getting cells
        async with http.get(url) as r:
            # Checking request
            if r.status != 200:
                return None

            return Portables._format_data(await r.json())

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

        # Get portables from google sheet
        portables = await Portables._get_portables(self.bot.whttp)
        if not portables:
            await self.bot.say('Google sheet could not be reached.')
            return

        # Building message
        e = discord.Embed()
        e.colour = 0x3572a7
        e.timestamp = portables.time
        e.set_footer(text='Updated %s' % portables.last_updated)
        e.set_author(name=portables.author,
                     icon_url='http://services.runescape.com/m=avatar-rs/%s/chat.png' % urllib.parse.quote(portables.author))

        # Adding portable locations
        for portable, locations in portables.locations.items():

            # Skipping if no the portable requested
            if args.portable and args.portable not in portable:
                continue

            # No location for portable
            if not locations:
                e.add_field(name=portable.capitalize(), value='N/A')
                continue

            value = '\n'.join(['%s %s' % (', '.join(worlds), location) for location, worlds in locations.items()])
            e.add_field(name=portable.capitalize(), value=value)

        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(Portables(bot))
