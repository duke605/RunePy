from json import loads
from collections import OrderedDict
from datetime import datetime
import aiohttp
import asyncio

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
        async with aiohttp.get(endpoint) as r:

            # Checking if request was found
            if r.status == 404:
                return None

            text = await r.text()

            # Checking if data is valid
            if not text:
                await asyncio.sleep(4)
                continue

            return loads(text, object_pairs_hook=OrderedDict) if json else text

async def get_price_history(item):
    """
    Gets price history for item

    :param item: The item to get the price history for
    """

    # Building URL
    url = 'http://services.runescape.com/m=itemdb_rs/api/graph/%s.json' % item.id
    history = await use_jca(url)

    # Updating the items price
    item.price = list(history['daily'].values())[-1]
    item.updated_at = datetime.utcnow()

    return history
