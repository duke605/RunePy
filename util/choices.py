from argparse import ArgumentTypeError


def between(low, high, number=True):
    """
    If input is supposed to be a string then it will test if the length is between the min and max
    If the input is supposed to be a number it tests if the number is between min and max
    """

    def test(s):
        s = int(s) if number else s
        length = s if number else len(s)

        # Testing length
        if length < low or length > high:
            raise ArgumentTypeError('invalid value: {} (must be between {:,} and {:,})'.format(s, low, high))

        return s
    return test


def enum(*args, **kwargs):
    """
    Tests if a given values is allowed

    :param args: Plain values that are allowed as input
    :param kwargs: Vales that are allowed as input that will be aliased the the key
    """

    def test(s):

        # Checking if value is in plain text list
        if s.lower() in args:
            return s

        # Search through kwargs for a value that matches
        for key in kwargs:
            if s.lower() in kwargs[key] or s.lower() == key:
                return key

        plain = ', '.join(args)
        kv = ', '.join(['%s=%s' % (k, kwargs[k]) for k in kwargs])
        together = '%s %s' % (plain, kv)

        # Input not found in valid choices
        raise ArgumentTypeError('invalid choice: \'%s\' (choose from %s.)' % (s, together.strip()))

    return test


def minimum(_min, number=True):
    """
    Tests if the input is above or equal to a certain number if input is supposed to be a number. Otherwise
    length is tested
    """

    def test(s):
        s = int(s) if number else s
        length = s if number else len(s)

        if length < _min:
            raise ArgumentTypeError('invalid value: {} (must be greater than or equal to {:,}.)'.format(s, _min))

        return s

    return test
