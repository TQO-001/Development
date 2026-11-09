# -------------------------- 9.1 Function Decorators ------------------------- #
# The Decorator definition
def my_decorator(func):
    def wrapper():
        print("[Before] Player prepares their stance...")
        func()
        print("[After] Player returns to defensive guard.")
    return wrapper

# Applying the decorator
@my_decorator
def perform_strike():
    print("\tThe Warrior swings their blade!")

# Calling the decorated function
perform_strike()

# -------------------------- 9.2 Chaining Decorators ------------------------- #
def boost_power(func):
    def wrapper():
        print("Power Boost Activated!")
        return func()
    return wrapper

def apply_poison(func):
    def wrapper():
        print("Weapon coated in Poison!")
        return func()
    return wrapper

@boost_power
@apply_poison
def basic_attack():
    print("\tAttacking target!")

basic_attack()

# ------------ 9.3 Decorators with Arguments (*args and **kwargs) ------------ #
def combat_log(func):
    def wrapper(*args, **kwargs):
        print(f"Logging Action: {func.__name__} was executed.")
        return func(*args, **kwargs)
    return wrapper

@combat_log
def cast_spell(spell_name, mana_cost):
    print(f"\tCasting {spell_name} for {mana_cost} MP.")

cast_spell("Fireball", 15)

# ------------ 9.4 Preserving Function Metadata (functools.wraps) ------------ #
from functools import wraps

def smart_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"LOGGING ACTION: [{func.__name__}] was executed.")
        print(func.__doc__)
        """NOTE: This is a test"""
        return func(*args, **kwargs)
    
    return wrapper

@smart_decorator
def heal():
    """ NOTE: Restores HP to the caster.
        It can be modified to restore the HP 
        of other characters
    """
    print("Healed!")

heal()

print(heal.__name__)
print(heal.__doc__)

# --------------------------- 9.5 Common Use Cases --------------------------- #
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()
        print(f"Execution Time: {end - start:.5f} seconds")

        return result

    return wrapper

@timer
def heavy_attack():
    total = 0
    for i in range(1000000):
        total += i

heavy_attack()

# --------------------- 9.6 Decorators in Real Frameworks -------------------- #
## Flask Route Decorators
from flask import Flask

app = Flask(__name__)

@app.route("/home")
def home():
    return "Welcome Home!"

home()

## FastAPI Validation Decorators
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users():
    return {"users": []}

# ------------------------ 9.7 Closures and Decorators ----------------------- #
def multiplier(x):

    def multiply(y):
        return x * y
    return multiply

double = multiplier(2)

print(double(5))

# ----------------------- 9.8 Decorator Execution Flow ----------------------- #
def my_decorator2(func):
    def wrapper():
        print("[Before] Player prepares their stance...")
        func()
        print("[After] Player returns to defensive guard.")
    return wrapper

@my_decorator2
def attack():
    print("Strike!")

# Equivalent to:
attack = my_decorator2("attack")

print(attack)