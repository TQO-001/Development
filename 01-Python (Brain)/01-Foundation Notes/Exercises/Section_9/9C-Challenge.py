import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)

        elapsed = time.perf_counter() - start_time
        print(f"Elapsed: {elapsed * 1000:.2f} ms")

        return result
    return wrapper

@timer
def sum_of_range(num):
    result = 0
    for x in range (num):
        result += x
    return result

# print(sum_of_range(2_000_000))

def require_positive(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args and args[0] <= 0:
            raise ValueError("Please enter a positive integer")
        return func(*args, **kwargs)
    return wrapper

@require_positive
def deal_damage(amount: int):
    print(f"{amount} DMG")

# deal_damage(334)
# deal_damage(-10)

def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        if args in cache:
            print("Cache Hit")
            return cache[args]

        print("Cache Miss")
        cache[args] = func(*args, **kwargs)

        return cache[args]
    return wrapper

@memoize
def slow_square(n: int): time.sleep(5); return n * n

"""
for i in range(10):
    print(slow_square(5))
"""

"""NOTE The timer start, then we check if the number is positive
    and if positive we then cache the value or return if it's 
    already in the cache
"""
@timer
@memoize
@require_positive
def cube(n: int): return n * n * n

print(cube(3))
print(cube(3))
