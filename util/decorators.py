import sys
import traceback
from asyncio import CancelledError


def _handle_exception(exc_info):
    traceback.print_tb(exc_info)


def ignore_exceptions(exceptions=(Exception,), exception_handler=_handle_exception, default=None, ignored=(CancelledError,)):
    """
    Ignores any exceptions rasied by a function

    :param exceptions: The exceptions to ignore
    :param exception_handler: The handler that handles what to do after an exception occurs
    :param default: What will be returned if the function errors
    :param ignored: What exceptions to ignore
    """

    def decorator(func):
        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:

                # Handling error if exception not ignored
                if type(e) not in ignored:
                    exception_handler(sys.exc_info()[2])

            return default

        return new_func

    return decorator


def ignore_exceptions_async(exceptions=(Exception,), exception_handler=_handle_exception, default=None, ignored=(CancelledError,)):
    """
    Ignores any exceptions rasied by a function

    :param exceptions: The exceptions to ignore
    :param exception_handler: The handler that handles what to do after an exception occurs
    :param default: What will be returned if the function errors
    :param ignored: What exceptions to ignore
    """

    def decorator(func):
        async def new_func(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions as e:

                # Handling error if exception not ignored
                if type(e) not in ignored:
                    exception_handler(sys.exc_info()[2])

            return default

        return new_func

    return decorator
