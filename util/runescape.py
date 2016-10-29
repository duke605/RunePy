from json import loads
from urllib.parse import quote
from collections import OrderedDict
from db.models import objects, Item
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp as http
import math
import asyncio
import re

STAT_ORDER = ('overall', 'attack', 'defence', 'strength', 'constitution', 'ranged', 'prayer', 'magic', 'cooking',
              'woodcutting', 'fletching', 'fishing', 'firemaking', 'crafting', 'smithing', 'mining', 'herblore',
              'agility', 'thieving', 'slayer', 'farming', 'runecrafting', 'hunter', 'construction', 'summoning',
              'dungeoneering', 'divination', 'invention')


async def get_players_online():

    # Getting total players
    async with http.get('http://www.runescape.com/player_count.js?varname=iPlayerCount&callback=jQuery111007968696597581173_1477635539644&_=1477635539645') as r:
        text = await r.text()

    total = int(re.search('jQuery111007968696597581173_1477635539644\((\d+)\);', text).group(1))

    # Getting classic
    async with http.get('http://www.runescape.com/classicapplet/playclassic.ws') as r:
        text = await r.text()

    soup = BeautifulSoup(text, 'html.parser')
    classic_players = 0

    # Getting classic world players
    for player_count in soup.find_all('span', attrs={'class': 'classic-worlds__players'}):
        classic_players += int(player_count.text.strip().split(' ')[0].replace(',', ''))

    # Getting OSRS players
    async with http.get('http://oldschool.runescape.com/?jptg=ia&jptv=navbar') as r:
        text = await r.text()

    soup = BeautifulSoup(text, 'html.parser')
    osrs_players = int(re.search('[0-9]+', soup.find('p', attrs={'class': 'player-count'}).text.strip()).group(0))

    return {
        'rsc': classic_players,
        'osrs': osrs_players,
        'total': total,
        'rs3': total - (classic_players + osrs_players)
    }


async def get_member_info(username: str):
    """
    Gets information about a runescape player

    :param username: The username of the player
    """

    # Getting info about memeber
    url = 'http://services.runescape.com/m=website-data/playerDetails.ws?names=["%s"]&' \
          'callback=jQuery000000000000000_0000000000&_=0'
    async with http.get(url % username) as r:
        json = await r.text()

    json = loads(re.search('jQuery000000000000000_0000000000\(\[(.*)\]\);', json).group(1))

    return {
        'recruiting': json.get('recruiting'),
        'name': json.get('name'),
        'clan': json.get('clan'),
        'title': json.get('title'),
        'isSuffix': json.get('isSuffix')
    }


async def get_users_alog(username: str, limit=10):
    """
    Gets the a user's adventurer log

    :param limit: The limit for the activties to get
    :param username: The name of the user
    """

    json = await use_jca('https://apps.runescape.com/runemetrics/profile/profile?user=%s&activities=%s'
                         % (quote(username), limit))

    # Checking if was ok
    if not json or json.get('error'):
        return None

    ret = []
    for a in json['activities']:
        ret.append({
            'title': re.sub('[0-9]+', lambda m: '{:,}'.format(int(m.group())), a['text']),
            'desc': re.sub('[0-9]+', lambda m: '{:,}'.format(int(m.group())), a['details']),
            'date': datetime.strptime(a['date'], '%d-%b-%Y %H:%M')
        })

    return ret


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
    item.updated_at = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    item.updated_at_rd = 0

    return item, history


def get_exp_between_levels(level1: int, level2: int):
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

    return math.floor(exp2 / 4) - math.floor(exp1 / 4)


def get_level_at_exp(target: int):
    """
    Gets a virtual level at the exp

    :param exp: The exp... obv
    :return:
    The virtual level for the exp
    """

    exp = 0
    for i in range(1, 120):
        exp += math.floor(i + 300 * 2**(i/7))

        # Checking if exp is at or above exp target
        if (math.floor(exp / 4) - 1) >= target:
            return i

    return 120

