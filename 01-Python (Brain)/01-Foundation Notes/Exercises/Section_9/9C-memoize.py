import time
from functools import wraps

def memoize(func):
    squares = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args in squares:
            print("Cache Hit")
            return squares[args]

        print("Cache Miss")
        squares[args] = func(*args, **kwargs)

        return squares[args]
    return wrapper

@memoize
def slow_square(n): time.sleep(5); return n * n

for i in range(10):
    print(slow_square(5))