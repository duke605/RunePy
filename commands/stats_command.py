from util.runescape import get_users_stats
from util.ascii_table import Table, Row, Column
from util.image_util import text_to_image

async def execute(bot, args):
    stats = await get_users_stats(args.name)

    # Checking if the request was a success
    if not stats:
        await bot.say('Stats for **%s** could not be retrieved.' % args.name)
        return

    table = Table()
    table.set_title('VIEWING RS3 STATS FOR %s' % args.name.upper())
    table.set_headings('Skill', 'Level', 'Experience', 'Rank')

    # Adding rows
    for key in stats.keys():
        stat = stats[key]
        table.add_row(
            key.capitalize(),
            Column(stat['level'], 2),
            Column('{:,}'.format(stat['exp']), 2),
            Column('{:,}'.format(stat['rank']), 2))

    # Plain text
    text = str(table)
    if not args.image:
        await bot.say('```%s```' % text)
    else:
        link = await text_to_image(text)

        # Checking if table was uploaded
        if not link:
            await bot.say('Table could not be uploaded as an image to imgur.')
        else:
            await bot.say(link)
