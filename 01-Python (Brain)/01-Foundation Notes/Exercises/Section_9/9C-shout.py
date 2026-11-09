# Exercise 1
import magnum
from functools import wraps # Exercise 1, 2, 3
import time # Exercise 2
import random # Exercise 3

magnum.exercise(1)

def shout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        sentence = func(*args, **kwargs)
        return sentence.upper()
    return wrapper

@shout
def greet(name: str) -> str:
    return f"Hello, {name}"

print(greet("arthur"))
print(greet.__name__)