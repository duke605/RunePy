from argparse import ArgumentTypeError


def between(low, high):
    """
    Tests that the given input is between the low number (inclusive) and high number (exclusive)
    """

    def test(s):
        s = int(s)

        if low > s >= high:
            raise ArgumentTypeError('must be between {:,} and {:,}'.format(low, high))

        return s
    return test
