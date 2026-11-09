import time
from functools import wraps
import magnum

magnum.exercise(3)

def retry(times: int = 3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                if func(*args, **kwargs) == "Success!":
                    break
                else:
                    magnum.dash()
                    if i == times:
                        print("Failed!")
                    else:
                        print(f"Attempt {i} failed, retrying...")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@retry(times=3)
def flaky_action() -> str:
    try:
        chance = (random.random() * 100)
        if chance > 60:
            raise ValueError(f"Less than 60%, chance is {chance}")
        else:
            return "Success!"
    except ValueError() as e:
        return f"Error: {e}"

print(flaky_action())