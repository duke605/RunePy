from db.models import Alias, db, Item, objects

async def _quick_match_name(name: str):
    """
    Quickly matches a partial item name

    :param name: The partial name to fuzzy match
    """

    params = (name,) * 3
    sql = 'SELECT * ' \
          'FROM _items ' \
          'WHERE name LIKE %s ' \
          'OR SOUNDEX(name) LIKE SOUNDEX(%s) ' \
          'ORDER BY sys.jaro_winkler(Name, %s) DESC ' \
          'LIMIT 1'
    item = await objects.execute(Item.raw(sql, *params))
    return item[0] if item else None

async def _alias_match_name(name: str):
    """
    Searches the alias table for aliases that match the name

    :param name: The name to find the alias of
    """

    params = (name,) * 2
    sql = 'SELECT * ' \
          'FROM aliases ' \
          'JOIN _items ON item_id = id ' \
          'WHERE alias LIKE %s ' \
          'OR SOUNDEX(alias) LIKE SOUNDEX(%s) ' \
          'LIMIT 1'
    alias = await objects.execute(Alias.raw(sql, *params))

    # No alis found
    if not alias:
        return None

    # Building item from join
    item = Item()
    item.name = alias.name
    item.id = alias.id
    item.members = alias.members
    item.high_alch = alias.high_alch
    item.low_alch = alias.low_alch
    item.description = alias.description
    item.price = alias.price
    item.category = alias.category
    item.last_updated = alias.last_updated
    item.runeday = alias.runeday

    return item

async def _jaro_winkler_name(name: str):
    """
    Matches the partial name via jaro winkler. This is SLOW

    :param name: The name of the item to jaro winkler match
    """

    params = (name,)
    sql = 'SELECT * ' \
          'FROM _items ' \
          'WHERE name LIKE \'%%{}%%\'' \
          'ORDER BY sys.jaro_winkler(name, %s) DESC ' \
          'LIMIT 1'.format(db.get_conn().escape_string(name))
    item = await objects.execute(Item.raw(sql, *params))
    return item[0] if item else None

async def fuzzy_match_name(name: str):
    """
    Fuzzy matches a "Maybe" partial name

    :param name: The name to match
    :return: The item and name of the matched item or none if the name was not matched
    """

    # Trying to quickly match the name
    item = await _quick_match_name(name)
    if item:
        return item

    # Trying aliases
    item = await _alias_match_name(name)
    if item:
        return item

    # Slowly fuzzy matching DB
    return await _jaro_winkler_name(name)
