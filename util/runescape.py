from json import loads
from urllib.parse import quote
from collections import OrderedDict
from db.models import objects, Item
from datetime import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree
import aiohttp as http
import math
import asyncio
import re

STAT_ORDER = ('overall', 'attack', 'defence', 'strength', 'constitution', 'ranged', 'prayer', 'magic', 'cooking',
              'woodcutting', 'fletching', 'fishing', 'firemaking', 'crafting', 'smithing', 'mining', 'herblore',
              'agility', 'thieving', 'slayer', 'farming', 'runecrafting', 'hunter', 'construction', 'summoning',
              'dungeoneering', 'divination', 'invention')


async def get_users_alog(username: str):
    """
    Gets the a user's adventurer log

    :param username: The name of the user
    """

    url = 'http://services.runescape.com/m=adventurers-log/a=13/rssfeed?searchName=%s'
    async with http.get(url % username) as r:

        # Checking if user found
        if r.status != 200:
            return None

        text = await r.text()

    xml = ElementTree.fromstring(text)[0]
    items = []

    # Looping through all items
    for item in xml.iter('item'):

        i = {
            'title': re.sub(r'[0-9]+', lambda m: '{:,}'.format(int(m.group())), item[0].text),
            'description': re.sub(r'[0-9]+', lambda m: '{:,}'.format(int(m.group())), item[1].text.strip()),
            'date': datetime.strptime(item[3].text, '%a, %d %b %Y %H:%M:%S %Z')
        }

        items.append(i)

    return items


def add_metric_suffix(num: int):
    """
    Adds the classic (b, m, k) suffixes to the end of a number

    :param num: The number to add the suffix to
    """

    # Billion
    if num >= 1000000000:
        x = num / 1000000000
        return '{:,}b'.format(int(x) if 1 % x == 0 else round(x, 1))

    # Million
    if num >= 1000000:
        x = num / 1000000
        return '{:,}m'.format(int(x) if 1 % x == 0 else round(x, 1))

    # Thousand
    if num >= 1000:
        x = num / 1000
        return '{:,}m'.format(int(x) if 1 % x == 0 else round(x, 1))

    return '{:,}m'.format(int(num))

async def get_item_alch_prices(item_name: str, fuzzy_name=True):
    """
    Gets the high and low alch price of an item

    :param item_name: The item name to get the alch prices for
    :param fuzzy_name: True if the name mame be fuzzy
    """

    # Getting name if might be fuzzy
    if fuzzy_name:
        item = await fuzzy_match_name(item_name)

        # Checking if the id was found
        if not item_name:
            return None

        item_name = item['name']

    # Getting high alch price
    async with http.get('http://runescape.wikia.com/wiki/%s' % item_name.replace(' ', '_')) as r:
        text = await r.text()

    soup = BeautifulSoup(text, 'html.parser')
    table = soup.find('table', attrs={'class': 'infobox-item'})
    high_alch = int(table.find('a', attrs={'title': 'High Level Alchemy'}).parent.parent.find('td').text.strip()\
        .split(' ')[0].replace(',', ''))
    low_alch = int(table.find('a', attrs={'title': 'Low Level Alchemy'}).parent.parent.find('td').text.strip()\
        .split(' ')[0].replace(',', ''))

    return {
        'high': high_alch,
        'low': low_alch
    }


async def get_users_stats(username: str):
    """
    Gets the stats of a user

    :param username: The name of the user
    :return:
    A dict containing the user's stats
    """

    resp = await use_jca('http://services.runescape.com/m=hiscore/index_lite.ws?player=%s' % quote(username), False)

    # Checking if the response was ok
    if not resp:
        return None

    # Parsing response
    stats = OrderedDict()
    lines = resp.split('\n')
    for i, o in enumerate(STAT_ORDER):
        line = lines[i].split(',')

        stats[o] = {
            'rank': int(line[0]),
            'level': int(line[1]),
            'exp': int(line[2])
        }

    return stats


async def use_jca(endpoint: str, json=True):
    """
    Uses Jagex's crappy crappy api

    :param endpoint: The endpoint to get the data from
    :param json: Whether to get the response as json
    :return:
    the response or none if the request was not found
    """

    # Looping til valid data
    while True:
        async with http.get(endpoint) as r:

            # Checking if request was found
            if r.status == 404:
                return None

            text = await r.text()

            # Checking if data is valid
            if not text:
                await asyncio.sleep(4)
                continue

            return loads(text, object_pairs_hook=OrderedDict) if json else text

async def fuzzy_match_name(name: str):
    """
    Fuzzy matches a "Maybe" partial name

    :param name: The name to match
    :return:
    The item and name of the matched item or none if the name was not matched
    """

    # Checking DB first
    ret = await objects.execute(
        Item.raw('SELECT Name, Id '
                 'FROM items '
                 'WHERE Name = %s '
                 'OR SOUNDEX(Name) LIKE SOUNDEX(%s) '
                 'ORDER BY sys.jaro_winkler(Name, %s) DESC '
                 'LIMIT 1', name, name, name))

    # Returning if name was matched to something
    if ret:
        return {
            'name': ret[0].name,
            'id': ret[0].id
        }

    # Checking rscript
    async with http.get('http://rscript.org/lookup.php?type=ge&search=%s&exact=1' % quote(name)) as r:
        text = await r.text()
        results = re.search('^RESULTS:\s(\d+?)$', text, re.M)

        # WE HAVE A MATCH!! :D
        if results and int(results.group(1)):
            return {
                'name': re.search('^ITEM:\s\d+?\s(.+?)\s', text, re.M).group(1),
                'id': re.search('^IID:\s(\d+?)$', text, re.M).group(1)
            }

    # Slowly fuzzy matching DB
    ret = await objects.execute(
        Item.raw('SELECT Name, Id '
                 'FROM items '
                 'ORDER BY sys.jaro_winkler(Name, %s) DESC '
                 'LIMIT 1', name))

    if not ret:
        return None

    return {
        'name': ret[0].name,
        'id': ret[0].id
    }

async def get_item_for_name(name: str):
    """
    Gets an item by name

    :param name: The name of the item to get
    :return:
    The item or None if the item was not found
    """

    resolved = await fuzzy_match_name(name)

    # Checking if the name could be resolved
    if not resolved:
        return None

    # Building URL
    url = 'http://services.runescape.com/m=itemdb_rs/api/graph/%s.json' % resolved['id']
    history = await use_jca(url)

    item = Item()
    item.price = list(history['daily'].values())[-1]
    item.name = resolved['name']
    item.id = resolved['id']
    item.updated_at = datetime.utcnow().date()
    item.updated_at_rd = 0

    return item, history


def exp_between_levels(level1: int, level2: int):
    """
    Gets the amoount of exp between two levels

    :param level1: The low level
    :param level2: The high level
    """

    exp1 = 0
    exp2 = 0

    for i in range(1, level2):
        if i < level1:
            exp1 += math.floor(i + 300 * 2**(i/7))
        exp2 += math.floor(i + 300 * 2**(i/7))

    return math.floor(exp2 / 4) - math.floor(2/4)
