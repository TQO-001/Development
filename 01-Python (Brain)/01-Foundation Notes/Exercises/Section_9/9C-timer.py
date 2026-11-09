import time
from functools import wraps
import magnum

magnum.exercise(2)

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        print(f"Elapsed: {elapsed * 1000:.2f}")

        return result
    return wrapper

@timer
def sum_of_range(num: int) -> int:
    result = 0
    for i in range(num):
        result += i
    return result

print(sum_of_range(2_000_000))
print(sum_of_range.__name__)
