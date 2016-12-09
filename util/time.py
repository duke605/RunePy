from collections import OrderedDict


def _subtract_previous(seconds, include, up_to):
    """
    Deduct previous units of time measurement

    :param seconds: The total number of seconds
    :param include: What is included in the final timestring
    :param up_to: Deducts time up to a unit
    """

    times = OrderedDict()
    times['years'] = 31536000
    times['months'] = 2592000
    times['weeks'] = 604800
    times['days'] = 86400
    times['hours'] = 3600
    times['minutes'] = 60

    # Deducting time
    for key, value in times.items():

        # Skipping if unit not in included
        if key not in include:
            continue

        # Stopping if up to reached
        if up_to == key:
            break

        seconds %= value

    return seconds


def format_timedelta(delta, include=('hours', 'minutes', 'seconds'), short_names=False):
    """
    Formats a time delta to a time string

    :param delta: The delta to format
    :param include: What units to include in the time string
    :param short_names: Use short names like m, s, y, w, etc...
    """

    seconds = delta.total_seconds()
    time_string = ''
    times = OrderedDict()
    times['years'] = (31536000, lambda num: 'y' if short_names else (' year' if num == 1 else ' years'))
    times['months'] = (2592000, lambda num: 'M' if short_names else (' month' if num == 1 else ' months'))
    times['weeks'] = (604800, lambda num: 'w' if short_names else (' week' if num == 1 else ' weeks'))
    times['days'] = (86400, lambda num: 'd' if short_names else (' day' if num == 1 else ' days'))
    times['hours'] = (3600, lambda num: 'h' if short_names else (' hour' if num == 1 else ' hours'))
    times['minutes'] = (60, lambda num: 'm' if short_names else (' minute' if num == 1 else ' minutes'))
    times['seconds'] = (1, lambda num: 's' if short_names else (' second' if num == 1 else ' seconds'))

    # Looping through units
    for key, value in times.items():

        # Skipping if unit not in included
        if key not in include:
            continue

        unit = int(_subtract_previous(seconds, include, key) / value[0])
        time_string += ' {:,}{}'.format(unit, value[1](unit))

    return time_string.strip()

