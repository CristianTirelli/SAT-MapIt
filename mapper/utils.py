import time
import logging
import threading
from functools import wraps

# Thread-local storage for safe parallelism
_thread_local = threading.local()
_thread_local.tab_level = 0


def timeit(description: str, print_args: bool = False):
    """Decorator to time the execution of a function with nesting support."""

    def decorator(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            if not hasattr(_thread_local, "tab_level"):
                _thread_local.tab_level = 0

            indent = '    ' * _thread_local.tab_level
            if print_args:
                logging.info(f"{indent}{description} -- {func.__name__}({args}, {kwargs})")
            else:
                logging.info(f"{indent}{description} -- {func.__name__}")

            _thread_local.tab_level += 1
            ts = time.time()
            result = func(*args, **kwargs)
            te = time.time()

            indent = '    ' * _thread_local.tab_level
            if print_args:
                logging.info(
                    f"{indent}{func.__name__} args:[{args}, {kwargs}] took: {te - ts:2.4f} sec"
                )
            else:
                logging.info(f"{indent}{func.__name__} took {te - ts:2.4f} sec")
            _thread_local.tab_level -= 1
            return result

        return wrap

    return decorator
