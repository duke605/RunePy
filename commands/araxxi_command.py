from math import floor
from datetime import datetime

async def execute(bot):
    araxxi_rotations = [
        'Minions',
        'Acid',
        'Darkness'
    ]

    ms = round(datetime.utcnow().timestamp() * 1000, 0)
    current_rotation = floor((((floor(floor(ms / 1000) / (24 * 60 * 60))) + 3) % (4 * len(araxxi_rotations))) / 4)
    days_until_next = 4 - ((floor((ms / 1000) / (24 * 60 * 60))) + 3) % (4 * len(araxxi_rotations)) % 4
    next_rotation = current_rotation + 1

    # Resenting next location
    next_rotation = next_rotation if next_rotation < len(araxxi_rotations) else 0

    # Building message
    m = '**Currently Closed**: Path %s - %s\n' % (current_rotation + 1, araxxi_rotations[current_rotation])
    m += '**Next Closed**: Path %s - %s in `%s` days.' % (next_rotation + 1, araxxi_rotations[next_rotation],
                                                          days_until_next)

    await bot.say(m)
