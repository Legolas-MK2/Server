import contextlib, inspect, sys, functools, io
import multiprocessing
import time
from multiprocessing import Process

from my_module import *

print_error = False
fall_in_exception = False


def debugging(myfunc):
    @functools.wraps(myfunc)
    def wrapper_func(*args, **kwargs):
        print(f"{' '.join(myfunc.__name__.split('_'))} ➤ ", end="")
        if fall_in_exception:
            process = multiprocessing.Process(target=myfunc)
            process.start()
            process.join()
            return wrapper_func
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                pass
            process = multiprocessing.Process(target=myfunc)
            process.start()
            process.join()
            print("✔")
        except Exception as e:
            print("✘")
            if print_error:
                print(e, "\n")
    return wrapper_func


if __name__ == "__main__":
    functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    for name, func in functions:
        is_decorated = hasattr(func, '__wrapped__')
        if is_decorated:
            func()
