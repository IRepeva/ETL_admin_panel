import logging
from functools import wraps
from time import sleep

logger = logging.getLogger(__name__)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, logger=None):
    """
    A function to re-execute the function after some time if an error occurs.
    Uses exponential growth of the repeat time up to the boundary sleep time

    Formula:
    t = start_sleep_time * 2^(n) if t < border_sleep_time else border_sleep_time

    :param start_sleep_time: start repeat time
    :param factor: the exponent
    :param border_sleep_time: limit waiting time
    :return: function execution result
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time, n = start_sleep_time, 1
            while sleep_time < border_sleep_time:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.info(f'During execution the error occurred: \n {e}')
                    sleep(sleep_time)
                    sleep_time = start_sleep_time * (factor ** n)
                n += 1
            raise Exception(
                f'Max sleep time {border_sleep_time} seconds '
                f'for {func.__qualname__} function was achieved'
            )
        return inner

    return func_wrapper
