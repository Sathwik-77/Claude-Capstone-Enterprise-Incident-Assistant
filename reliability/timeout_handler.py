import functools
import threading


class TimeoutError(Exception):
    pass


def with_timeout(seconds: float):
    """
    Decorator that raises TimeoutError if function takes too long.

    Args:
        seconds: maximum allowed execution time

    Example:
        @with_timeout(30)
        def call_claude(...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=seconds)

            if thread.is_alive():
                raise TimeoutError(
                    f"[Timeout] Function '{func.__name__}' exceeded {seconds}s limit."
                )

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper
    return decorator


def timeout_call(func, *args, seconds: float = 30.0, **kwargs):
    """
    Run a function with a timeout without using the decorator.

    Args:
        func: function to call
        *args: positional arguments
        seconds: timeout in seconds
        **kwargs: keyword arguments

    Returns:
        Result of the function

    Raises:
        TimeoutError if the function exceeds the time limit
    """
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout=seconds)

    if thread.is_alive():
        raise TimeoutError(
            f"[Timeout] Function '{func.__name__}' exceeded {seconds}s limit."
        )

    if exception[0]:
        raise exception[0]

    return result[0]