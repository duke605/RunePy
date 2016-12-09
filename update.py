from db.models import Item, db
from urllib import parse
import requests
import re
import math

items = Item.select().order_by(Item.id).execute()
url = 'http://runescape.wikia.com/wiki/%s?action=raw'


def parse_data(text):
    block = re.search(r'\{\{Infobox Item(.+?)^\}\}', text, re.S | re.M).group(1).strip()
    data = {}

    lines = block.split('|')
    for line in lines:
        line = line.strip()
        if not line or '=' not in line:
            continue

        key, value = re.search('^(.+?)\s?=\s?(.+?)?$', line, re.M).groups()
        data[key] = value

    return data


def kill_rounding_error(n):
    return math.floor(n*1000+0.0000099)/1000


def request(name):
    while True:
        r = requests.get(url % parse.quote(name))

        if r.status_code != 200:
            print('%s code given for %s' % (r.status_code, item.name))
            return None

        redirect = re.search('#REDIRECT ?\[\[(.+)\]\]', r.text, re.I)
        if redirect:
            print('Redirecting %s to %s' % (name, redirect.group(1)))
            name = redirect.group(1)
            continue

        return r.text


def get_value_for(item, data):
    value = data.get('value', None)

    if value is not None:
        return int(value)

    if data.get('value1', None) is None:
        print('No value for %s' % item.name)
        return None

    for i in range(1000):
        if int(data.get('id%s' % i, -1)) == item.id:
            return int(data['value%s' % i])

    print('******No value for %s******' % item.name)
    return None


with db.transaction():
    for i, item in enumerate(items):
        print('---------%s [=%s==%s=]---------' % (item.name, i, item.id))
        text = request(item.name)

        if text is None:
            continue

        data = parse_data(text)
        multiplier = float(data.get('alchmultiplier', 0.6))
        alchable = data.get('alchable', None)
        value = get_value_for(item, data)
        high = data.get('high', None)
        low = data.get('low', None)

        if (alchable is not None and alchable.lower() == 'no') \
                or (high is not None and high.lower() == 'no')\
                or (low is not None and low.lower() == 'no'):
            high = -1
            low = -1
        elif value is None:
            high = -2 if high is None or high.lower() == 'no' else int(high)
            low = -2 if low is None or low.lower() == 'no' else int(low)
        else:
            high = int(value * multiplier) if high is None or high.lower() == 'no' else int(high)
            low = int(kill_rounding_error(value * (2/3) * multiplier)) if low is None or low.lower() == 'no' else int(low)

        if high == item.high_alch and low == item.low_alch:
            continue

        if high != item.high_alch:
            print('High alch different for %s. Was: %s | Now: %s' % (item.name, item.high_alch, high))

        if low != item.low_alch:
            print('Low alch different for %s. Was: %s | Now: %s' % (item.name, item.low_alch, low))

        item.high_alch = high
        item.low_alch = low
        item.save()

    print('!!!SAVING!!!')
