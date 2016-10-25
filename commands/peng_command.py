from bs4 import BeautifulSoup
from util.globals import http
import re

async def execute(bot):
    data = []

    # Getting peng data
    async with http.get('http://world60pengs.com/includes/including.php?inid=pengdata') as r:
        soup = BeautifulSoup(await r.text(), 'html.parser')

    # Getting the titles
    for i, head in enumerate(soup.find_all('div', attrs={'class': 'penghead'})):
        title, type, points = re.search('^.+?\s(.+?)\s-\s(.+?)\s\((\d+?)\s', head.text).groups()
        data.append({'title': title, 'type': type, 'points': int(points), 'desc': head.next_sibling.text})

    m = '__**World 60 Penguin Locations**__:\n\n'
    m += "```py\n'%s'```\n" % soup.find('div', attrs={'class': 'rednote'}).text.strip()
    for i, loc in enumerate(data):
        m += '%s.) __**%s**__: %s (%s point%s)\n' \
             '%s\n\n' % (i+1, loc['title'], loc['type'], loc['points'], 's' if loc['points'] > 1 else '', loc['desc'])

    await bot.say(m)
