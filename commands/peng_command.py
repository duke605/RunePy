from bs4 import BeautifulSoup
from util.globals import http
from datetime import datetime
import re

async def execute(bot):
    data = await _get_peng_locs(bot)

    m = '__**World 60 Penguin Locations**__:\n\n'
    m += "```py\n'%s'```\n" % data['note']
    for i, loc in enumerate(data['worlds']):
        m += '%s.) __**%s**__: %s (%s point%s)\n' \
             '%s\n\n' % (i+1, loc['title'], loc['type'], loc['points'], 's' if loc['points'] > 1 else '', loc['desc'])

    await bot.say(m)

async def _get_peng_locs(bot):
    data = bot.pengdata if hasattr(bot, 'pengdata') else None

    # Checking if the bot contains a valid copy
    if data and data['expire'] > datetime.utcnow():
        return data

    data = {'worlds': []}

    # Getting peng data
    async with http.get('http://world60pengs.com/includes/including.php?inid=pengdata') as r:
        soup = BeautifulSoup(await r.text(), 'html.parser')

    # Getting the titles
    for i, head in enumerate(soup.find_all('div', attrs={'class': 'penghead'})):
        title, type, points = re.search('^.+?\s(.+?)\s-\s(.+?)\s\((\d+?)\s', head.text).groups()
        data['worlds'].append({'title': title, 'type': type, 'points': int(points), 'desc': head.next_sibling.text})

    # Getting note
    data['note'] = soup.find('div', attrs={'class': 'rednote'}).text.strip()

    # Getting expiry
    expire = soup.find('div', attrs={'class': 'contenttitle'}).text.strip()
    date, month = re.match('^(\d+?)\s(.+?)\s', expire[::-1]).groups()

    # Reversing back
    date = date[::-1]
    month = datetime.strptime(month[::-1], '%B').month

    # Month is in new year
    dt = datetime.utcnow()
    if month == 1 and dt.month == 12:
        expire = datetime(dt.year+1, month, int(date))
    else:
        expire = datetime(dt.year, month, int(date), 23, 59, 59)

    data['expire'] = expire
    bot.pengdata = data
    return data