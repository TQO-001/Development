## Section 9: Decorators

Decorators are a design pattern in Python that let you modify or extend the behaviour of a function without permanently changing that function's source code. They're built on two ideas you've already met:

- Functions are **first-class citizens** — they can be stored in variables, passed into other functions, and returned from functions, just like any other value.
- Python supports **Higher-Order Functions** (Section 3.4) — functions that either accept other functions as arguments, or return them.

A decorator wraps another function inside additional logic, then returns the modified version.

### 9.1 Function Decorators

A basic decorator takes a function as input, defines an inner wrapper function containing extra behaviour, and returns that wrapper. You apply it using the `@decorator_name` syntax directly above the target function.

```Python
# The Decorator
def my_decorator(func):
    def wrapper():
        print("⚔️ [Before] Player prepares their stance...")
        func()  # Runs the original function
        print("🛡️ [After] Player returns to defensive guard.")
    return wrapper

# Applying the decorator
@my_decorator
def perform_strike():
    print("   The Warrior swings their blade!")

# Calling the decorated function
perform_strike()
```

**Output:**

```text
⚔️ [Before] Player prepares their stance...
   The Warrior swings their blade!
🛡️ [After] Player returns to defensive guard.
```

### 9.2 Chaining Decorators

Multiple decorators can be stacked on the same function. Python applies them from the bottom upward, wrapping the function one layer at a time.

```Python
def boost_power(func):
    def wrapper():
        print("🔥 Power Boost Activated!")
        return func()
    return wrapper

def apply_poison(func):
    def wrapper():
        print("🧪 Weapon coated in Poison!")
        return func()
    return wrapper

@boost_power
@apply_poison
def basic_attack():
    print("   Attacking target!")

basic_attack()
```

**Output:**

```text
🔥 Power Boost Activated!
🧪 Weapon coated in Poison!
   Attacking target!
```

Notice that both wrappers use `return func()` rather than just `func()`. That `return` matters more than it looks: if the original function ever calculates and returns a value — damage numbers, an item ID, anything — leaving out `return` would cause the wrapper to silently discard it, and the caller would just get `None` back. It also matters for stacking: each wrapper needs to hand the result of the next function back up the chain, or the final output never makes it to the top. It's a habit worth building even on functions that only print something today, since they might return a value once you update them later.

### 9.3 Decorators with Arguments (`*args` and `**kwargs`)

If the original function accepts parameters, the wrapper function needs to accept arbitrary positional and keyword arguments too, using `*args` and `**kwargs`. This lets the decorator forward all arguments through to the original function, no matter what they are.

```Python
def combat_log(func):
    def wrapper(*args, **kwargs):
        print(f"📝 Logging action: {func.__name__} was executed.")
        return func(*args, **kwargs)
    return wrapper

@combat_log
def cast_spell(spell_name, mana_cost):
    print(f"   Casting {spell_name} for {mana_cost} MP.")

cast_spell("Fireball", 15)
```

**Output:**

```text
📝 Logging action: cast_spell was executed.
   Casting Fireball for 15 MP.
```

### 9.4 Preserving Function Metadata (`functools.wraps`)

When a function gets wrapped by a decorator, Python replaces the original function's metadata (`__name__`, `__doc__`, and so on) with the wrapper's metadata instead. `functools.wraps` fixes this by copying the original function's identity onto the wrapper.

```Python
from functools import wraps

def smart_decorator(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper

@smart_decorator
def heal():
    """Restores HP to the caster."""
    print("Healed!")

print(heal.__name__)  # Output: heal
print(heal.__doc__)   # Output: Restores HP to the caster.
```

Without `@wraps`, `heal.__name__` would incorrectly report `"wrapper"` instead — which makes debugging and introspection confusing, especially in larger codebases or anywhere that relies on a function's name (logging, testing frameworks, API routing).

### 9.5 Common Use Cases

Decorators show up constantly in real-world software because they let you attach reusable behaviour to many functions cleanly and consistently:

- **Logging** — tracking function calls, arguments, return values, and execution time.
- **Authorization** — verifying user roles or admin access before a protected function runs.
- **Caching** — storing expensive results so they don't need to be recalculated.
- **Validation** — checking inputs before the main function executes.
- **Performance monitoring** — measuring how long something takes.

```Python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()
        print(f"⏱️ Execution Time: {end - start:.5f} seconds")

        return result

    return wrapper

@timer
def heavy_attack():
    total = 0
    for i in range(1000000):
        total += i

heavy_attack()
```

### 9.6 Decorators in Real Frameworks

Many major Python frameworks lean heavily on decorators.

**Flask route decorators:**

```Python
from flask import Flask

app = Flask(__name__)

@app.route("/home")
def home():
    return "Welcome Home!"
```

Here, `@app.route("/home")` registers the function as a web route.

**FastAPI validation decorators:**

```Python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users():
    return {"users": []}
```

The decorator tells FastAPI which HTTP method and endpoint should trigger the function.

### 9.7 Closures and Decorators

Decorators work because Python supports **closures**. A closure happens when an inner function remembers variables from its outer function, even after the outer function has already finished running.

```Python
def multiplier(x):

    def multiply(y):
        return x * y

    return multiply

double = multiplier(2)

print(double(5))  # Output: 10
```

The inner `multiply()` function still remembers the value of `x`, even though `multiplier()` has already returned. Decorators rely on this exact behaviour to remember the original function they're wrapping.

### 9.8 Decorator Execution Flow

A decorated function call follows this sequence:

1. The original function is passed into the decorator.
2. The decorator creates a wrapper function.
3. The decorator returns the wrapper.
4. The original function's name now points to the wrapper instead.
5. Calling the function actually calls the wrapper first.

```Python
@my_decorator
def attack():
    print("Strike!")

# Equivalent to:
attack = my_decorator(attack)
```

---

**Practice:**
1. Write a function `deal_damage(enemy_name, damage)` that prints `"{enemy_name} takes {damage} raw damage!"`.
2. Write a decorator `@double_damage` that uses `*args` and `**kwargs` to intercept the call, doubles the `damage` value, and passes the result through to the original function. Use `@wraps` so `deal_damage.__name__` still reports correctly after decorating. (Hint: if you're working with positional arguments, `args[0]` will be the enemy name and `args[1]` will be the damage.)
3. Apply the decorator and confirm both the doubled damage output and the preserved `__name__`.

---
