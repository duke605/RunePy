from collections import namedtuple
from urllib import parse
from ..decorators import ignore_exceptions, ignore_exceptions_async
import aiohttp
import re
import math

ALCH_PRICES = namedtuple('AlchPrices', ['high', 'low'])


def _kill_rounding_error(n):
    return math.floor(n*1000+0.0000099)/1000


@ignore_exceptions()
def _parse_infobox_data(text):
    """
    Parses data from the wiki infobox into a dict

    :param text: The data from the wiki
    """

    block = re.search(r'\{\{Infobox Item(.+?)^\}\}', text, re.S | re.M).group(1).strip()
    data = {}

    lines = block.split('|')
    for line in lines:

        # Skipping erroneous entries
        line = line.strip()
        if not line or '=' not in line:
            continue

        key, value = re.search('^(.+?)\s?=\s?(.+?)?$', line, re.M).groups()
        data[key] = value

    return data


@ignore_exceptions_async()
async def _get_infobox_data(name):
    """
    Gets information about the item from the wiki

    :param name:
    :return:
    """

    url = 'http://runescape.wikia.com/wiki/%s?action=raw'

    while True:
        async with aiohttp.get(url % parse.quote(name)) as r:

            if r.status != 200:
                return None

            text = await r.text()
            redirect = re.search('#REDIRECT ?\[\[(.+)\]\]', text, re.I)
            if redirect:
                name = redirect.group(1)
                continue

            return _parse_infobox_data(text)


def _get_subitem_id(item_id, infobox_data):
    """
    Gets the id of a subitem

    :param item_id: The item id
    :param infobox_data: The dict containing info about the item
    """

    # Checking if item has no subitems
    if infobox_data.get('id', -1) == item_id:
        return -1

    # Trying to get the id for the right sub item
    for i in range(1000):
        if int(infobox_data.get('id%s' % i, -1)) == item_id:
            return i

    return None


@ignore_exceptions(ignored=(TypeError,))
def _get_value(item_id, infobox_data):
    """
    Gets value for an item

    :param item_id: The item id to get the value for
    :param infobox_data: The dict containing information about the item
    """

    sub_id = _get_subitem_id(item_id, infobox_data)
    value = infobox_data.get('value', None)
    if value:
        return int(value)
    else:
        return int(infobox_data.get('value%s' % sub_id, None))


@ignore_exceptions()
def _is_alchable(item_id, infobox_data):
    """
    Checks if the item is alchable

    :param item_id:
    :param infobox_data: The dict containing info about the items
    """

    # Trying proper attribute
    alchable = infobox_data.get('alchable', None)
    if alchable and alchable.lower() == 'no':
        return False

    # Checking high attribute
    alchable = infobox_data.get('high', None)
    if alchable and alchable.lower() == 'no':
        return False

    # Checking low attribute
    alchable = infobox_data.get('low', None)
    if alchable and alchable.lower() == 'no':
        return False

    # Checking if item has sub id
    sub_id = _get_subitem_id(item_id, infobox_data)
    if sub_id and sub_id == -1:
        return True

    # Trying proper attribute
    alchable = infobox_data.get('alchable%s' % sub_id, None)
    if alchable and alchable.lower() == 'no':
        return False

    # Checking high attribute
    alchable = infobox_data.get('high%s' % sub_id, None)
    if alchable and alchable.lower() == 'no':
        return False

    # Checking low attribute
    alchable = infobox_data.get('low%s' % sub_id, None)
    if alchable and alchable.lower() == 'no':
        return False

    return True


def _get_high(item_id, infobox_data):
    """
    Gets the high alch price for the item

    :param item_id:
    :param infobox_data:
    :return:
    """

    sub_id = _get_subitem_id(item_id, infobox_data)
    multi = infobox_data.get('alchmultiplier', infobox_data.get('alchmultiplier%s' % sub_id, 0.6))

    # Checking if alchable
    if not _is_alchable(item_id, infobox_data):
        return -1

    # Checking deprecated attributes
    price = infobox_data.get('high', None)
    if price:
        return price

    # Checking deprecated attribute with sub id
    price = infobox_data.get('high%s' % sub_id, None)
    if price:
        return price

    # Checking if value is known
    value = _get_value(item_id, infobox_data)
    if not value:
        return -2

    # Calculating
    return int(value * multi)


def _get_low(item_id, infobox_data):
    """
    Gets the low alch price of an item

    :param item_id: The id of the item
    :param infobox_data: The dict containing information about the item
    """

    sub_id = _get_subitem_id(item_id, infobox_data)
    multi = infobox_data.get('alchmultiplier', infobox_data.get('alchmultiplier%s' % sub_id, 0.6))

    # Checking if alchable
    if not _is_alchable(item_id, infobox_data):
        return -1

    # Checking deprecated attributes
    price = infobox_data.get('low', None)
    if price:
        return price

    # Checking deprecated attribute with sub id
    price = infobox_data.get('low%s' % sub_id, None)
    if price:
        return price

    # Checking if value is known
    value = _get_value(item_id, infobox_data)
    if not value:
        return -2

    # Calculating
    return int(_kill_rounding_error(value * multi * (2 / 3)))

async def get_alch_price(name: str, id: int):
    """
    Gets aht ealchmey low and high price for a item name

    :param name: The name of the item
    :param id: The id of the item
    """

    request = await _get_infobox_data(name)
    if not request:
        return None

    return ALCH_PRICES(high=_get_high(id, request), low=_get_low(id, request))