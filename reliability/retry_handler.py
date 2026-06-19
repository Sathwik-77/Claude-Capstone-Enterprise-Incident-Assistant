import time
import functools


def with_retry(max_retries: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    Decorator that retries a function on failure.

    Args:
        max_retries: maximum number of retry attempts
        delay: initial delay between retries in seconds
        backoff: multiplier for delay after each retry

    Example:
        @with_retry(max_retries=3, delay=2.0)
        def call_claude(...):
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        print(f"[Retry] Attempt {attempt}/{max_retries} failed: {e}")
                        print(f"[Retry] Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f"[Retry] All {max_retries} attempts failed.")

            raise last_exception

        return wrapper

    return decorator


def retry_call(func, *args, max_retries: int = 3, delay: float = 2.0, backoff: float = 2.0, **kwargs):
    """
    Retry a function call without using the decorator.

    Args:
        func: function to call
        *args: positional arguments for func
        max_retries: maximum retry attempts
        delay: initial delay in seconds
        backoff: delay multiplier
        **kwargs: keyword arguments for func

    Returns:
        Result of the function call
    """
    current_delay = delay
    last_exception = None

    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                print(f"[Retry] Attempt {attempt}/{max_retries} failed: {e}")
                print(f"[Retry] Retrying in {current_delay}s...")
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                print(f"[Retry] All {max_retries} attempts failed.")

    raise last_exception