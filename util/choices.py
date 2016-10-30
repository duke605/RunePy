from argparse import ArgumentTypeError


def between(low, high):
    """
    Tests that the given input is between the low number (inclusive) and high number (exclusive)
    """

    def test(s):
        s = int(s)

        if low > s or s > high:
            raise ArgumentTypeError('must be between {:,} and {:,}'.format(low, high))

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
        raise ArgumentTypeError('invalid choice: \'%s\' (choose from %s).' % (s, together.strip()))

    return test


def minimum(_min):
    """
    Tests if the input is above or equal to a certain number

    :param _min: The minimum value the input can be
    """

    def test(s):
        s = int(s)

        if s < _min:
            return 'invalid value: %s (must be greater than or equal to %s.)' % (s, _min)

        return s

    return test