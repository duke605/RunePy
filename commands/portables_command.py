from secret import GOOGLE_API_KEY
from util.globals import http
from datetime import datetime
import re

PORTS = ('fletcher', 'crafter', 'brazier', 'sawmill', 'forge', 'range', 'well')
HOST = 'https://sheets.googleapis.com/v4/spreadsheets'
SHEET_ID = '16Yp-eLHQtgY05q6WBYA2MDyvQPmZ4Yr3RHYiBCBj2Hc'
SHEET_NAME = 'Home'
RANGE = 'A16:G18'
URL = '%s/%s/values/%s!%s?key=%s' % (HOST, SHEET_ID, SHEET_NAME, RANGE, GOOGLE_API_KEY)


async def execute(bot, args):

    # Getting cells
    async with http.get(URL) as r:

        # Checking request
        if r.status != 200:
            await bot.say('Google sheet could not be reached.')
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
        worlds = json['values'][1][PORTS.index(args.portable)]

        await bot.say('**%ss**: %s\n'
                      '**Last Updated**: %s ago by %s'
                      % (args.portable.capitalize(), worlds, last_update, author))
        return

    # Outputting all portables
    m = ''
    for i, worlds in enumerate(json['values'][1]):
        m += '**%ss**: %s\n' % (PORTS[i].capitalize(), worlds)

    m += '**Last Updated**: %s ago by %s' % (last_update, author)
    await bot.say(m)
