from math import floor
from datetime import datetime
from util.globals import bot


@bot.command()
async def circus():
    locations = ('Tree Gnome Stronghold', "Seers' Village", 'Catherby', 'Taverley', 'Edgeville', 'Falador',
                 'Rimmington', 'Draynor Village', 'Al Kharid', 'Lumbridge', 'Lumber Yard', "Gertrude's House")

    ms = round(datetime.utcnow().timestamp() * 1000, 0)
    current_location = floor((((floor((ms / 1000) / (24 * 60 * 60))) + 1) % (7 * len(locations))) / 7)
    days_until_next = 7 - ((floor((ms / 1000) / (24 * 60 * 60))) + 1) % (7 * len(locations)) % 7
    next_location = current_location + 1

    # Start from beginning
    next_location = next_location if next_location < len(locations) else 0

    # Building message
    m = 'The circus is currently located at **%s**.\n' % locations[current_location]
    m += 'The next location will be **%s** in **%s** day%s.\n' % (locations[next_location], days_until_next,
                                                                  's' if days_until_next > 1 else '')

    await bot.say(m)
