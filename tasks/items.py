import util.runescape_util as rs
import util
import asyncio
import math
import sys
from db.models import Item, objects
from datetime import datetime
import util


class Items:

    def __init__(self, bot):
        self.bot = bot
        self.item_lookup = bot.loop.create_task(self.look_for_new_items())

    def _unload(self):
        self.item_lookup.cancel()

    @staticmethod
    @util.ignore_exceptions_async()
    async def _get_alpha_numbers(category):
        """
        Gets the alpha numbers for a given category
        """

        sql = 'SELECT IF(SUBSTR(name, 1, 1) REGEXP \'^[0-9]\', \'#\', LOWER(SUBSTR(name, 1, 1))) as alpha, COUNT(*) as number ' \
              'FROM _items ' \
              'WHERE category = %s ' \
              'GROUP BY alpha'

        result = await objects.execute(Item.raw(sql, category))

        # Populating all data
        ret = {chr(i): 0 for i in range(ord('a'), ord('z') + 1)}
        ret['#'] = 0

        # Inserting data
        for row in result:

            if row.alpha is None:
                continue

            ret[row.alpha] = row.number

        return ret

    @staticmethod
    @util.ignore_exceptions_async()
    async def _create_item(item, runeday):
        """
        Creates an item in the database

        :param item: The item in json form
        :param runeday: The runeday the item was fetched
        """

        alch = await util.get_alch_price(item['name'], item['id'])
        alch = alch if alch else util.ALCH_PRICES(high=-3, low=-3)

        # Preping data
        data = {
            'last_updated': datetime.utcnow(),
            'id': item['id'],
            'category': item['type'],
            'name': item['name'],
            'description': item['description'],
            'high_alch': alch.high,
            'low_alch': alch.low,
            'members': True if item['members'] == 'true' else False,
            'price': -1,
            'runeday': runeday
        }

        await objects.create(Item, **data)

    @staticmethod
    @util.ignore_exceptions_async()
    async def _create_new_items_for_alphas(category, alpha, pages, delta, runeday):
        """
        Searches through a category and alpha to get the new items
        """

        url = 'http://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category=%s&alpha=%s&page=%s'
        sql = 'SELECT id FROM _items WHERE id in (%s)'

        for i in range(1, pages + 1):
            items = (await rs.use_jca(url % (category, alpha, i)))['items']
            ids = ','.join(str(item['id']) for item in items)

            # Skipping if no items
            if len(items) == 0:
                continue

            cached_items = [i.id for i in await objects.execute(Item.raw(sql % ids))]

            # Creating items not already persisted
            for item in (item for item in items if item['id'] not in cached_items):
                await Items._create_item(item, runeday)
                delta -= 1

                # No more items to update
                if delta <= 0:
                    return

        print('Did not create all items for category %s alpha %s. %s item(s) remaining.' % (category, alpha, delta))

    @staticmethod
    @util.ignore_exceptions_async()
    async def _create_new_items_for_numbers(category, delta, runeday):
        """
        Searches through a category and alpha but in an ass backwards way because it's jagex and they can't get a simple API
        right
        """

        url = 'http://services.runescape.com/m=itemdb_rs/api/catalogue/items.json?category=%s&alpha=%s'
        sql = 'SELECT id FROM _items WHERE id in (%s)'

        for i in range(10):
            items = (await rs.use_jca(url % (category, i)))['items']
            ids = ','.join(str(item['id']) for item in items)

            # Skipping if no items
            if len(items) == 0:
                continue

            cached_items = [i.id for i in await objects.execute(Item.raw(sql % ids))]

            # Creating items not already persisted
            for item in (item for item in items if item['id'] not in cached_items):
                await Items._create_item(item, runeday)
                delta -= 1

                # No more items to update
                if delta <= 0:
                    return

        print('Did not create all items for category %s alpha %s. %s item(s) remaining.' % (category, '#', delta))

    @util.ignore_exceptions_async()
    async def look_for_new_items(self, wait=False):
        """
        Looks for new items in the catalogue
        """

        # Waiting from previous iteration
        if wait:
            await asyncio.sleep(60*60*2)

        categories = ("Miscellaneous","Ammo","Arrows","Bolts","Construction materials","Construction products","Cooking ingredients","Costumes","Crafting materials","Familiars","Farming produce","Fletching materials","Food and drink","Herblore materials","Hunting equipment","Hunting produce","Jewellery","Mage armour","Mage weapons","Melee armour - low level","Melee armour - mid level","Melee armour - high level","Melee weapons - low level","Melee weapons - mid level","Melee weapons - high level","Mining and smithing","Potions","Prayer armour","Prayer materials","Range armour","Range weapons","Runecrafting","Runes, Spells and Teleports","Seeds","Summoning scrolls","Tools and containers","Woodcutting product","Pocket items")
        runeday = (await rs.use_jca('https://secure.runescape.com/m=itemdb_rs/api/info.json'))['lastConfigUpdateRuneday']

        # Checking if needs updating
        max_runeday = (await objects.execute(Item.raw('SELECT MAX(runeday) as "last" FROM _items')))[0].last or 0
        if max_runeday >= runeday:
            self.item_lookup = self.bot.loop.create_task(self.look_for_new_items(True))
            return

        print('New items found in GE, updating...')

        # Searching all categories
        for i in range(38):
            category = categories[i]
            json = await rs.use_jca('http://services.runescape.com/m=itemdb_rs/api/catalogue/category.json?category=%s' % i)
            counts = await Items._get_alpha_numbers(category)

            # Checking if alphas are more than what we have
            for alpha in json['alpha']:
                items = alpha['items']
                letter = alpha['letter']

                # Alpha is the same or lower. Skipping
                if items <= counts[letter]:
                    continue

                # Getting new items in alpha category
                if letter != '#':
                    await Items._create_new_items_for_alphas(i, letter, math.ceil(items / 12), items - counts[letter], runeday)
                else:
                    await Items._create_new_items_for_numbers(i, items - counts[letter], runeday)

        print('Finished updating items.')
        self.item_lookup = self.bot.loop.create_task(self.look_for_new_items(True))


def setup(bot):
    bot.add_cog(Items(bot))
