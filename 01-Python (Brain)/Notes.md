## Section 7: Object-Oriented Programming (OOP)

OOP is a paradigm that allows you to bundle properties (attributes) and behaviors (methods) into individual objects. Think of a Class as a blueprint, and an Object as the actual house built from that blueprint.

### 7.1 Classes & Objects & 7.2 The `__init__()` Function

You define a class using the `class` keyword (remember your CamelCase convention from note 1!). The `__init__` method is the constructor—it runs automatically whenever you create a new instance (object) of that class. The `self` parameter represents the specific object you are currently creating or modifying.

```Python
class Character:
    # 7.2 The Constructor
    def __init__(self, name, role):
        self.name = name    # Instance Attribute
        self.role = role    # Instance Attribute
        self.level = 1      # Default value attribute

# Creating Objects (Instances)
hero1 = Character("Arthur", "Warrior")
hero2 = Character("Merlin", "Mage")

print(hero1.name)  # Output: Arthur
```

### 7.3 Attributes & Methods

- **Attributes:** Variables bound to an object (the object's data).
- **Methods:** Functions defined inside a class that operate on the object's data. They _must_ take `self` as their first argument to access instance attributes.

```Python
class Character:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.level = 1

    # 7.3 Method
    def level_up(self):
        self.level += 1
        return f"{self.name} reached level {self.level}!"

hero1 = Character("Arthur", "Warrior")
print(hero1.level_up())  # Output: Arthur reached level 2!
```

### 7.4 Inheritance

Inheritance allows a new class (Child/Subclass) to adopt attributes and methods from an existing class (Parent/Superclass), preventing you from repeating code. You use `super().__init__()` to pass data back up to the parent's constructor.

```Python
# Parent Class
class NPC:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} says hello."

# Child Class inherits from NPC
class Blacksmith(NPC):
    def __init__(self, name, shop_name):
        super().__init__(name) # Calls parent constructor
        self.shop_name = shop_name

vendor = Blacksmith("Andre", "Firelink Shrine")
print(vendor.speak())  # Output: Andre says hello. (Inherited method!)
```

### 7.5 Special Methods (`__str__`, `__repr__`)

Also called **Dunder Methods** (Double Underscore), these let you define how your objects behave with built-in Python operations.

- `__str__` controls what displays when you `print()` the object (user-friendly).
- `__repr__` controls the official string representation used for debugging.

```Python
class Weapon:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage

    def __str__(self):
        return f"{self.name} (Deals {self.damage} DMG)"

    def __repr__(self):
        return f"Weapon('{self.name}', {self.damage})"

sword = Weapon("Excalibur", 99)
print(sword)         # Triggers __str__ -> Output: Excalibur (Deals 99 DMG)
print(repr(sword))   # Triggers __repr__ -> Output: Weapon('Excalibur', 99)
```

### 7.6 Class vs. Instance Attributes

- **Instance Attributes:** Unique to each specific object (defined inside `__init__` using `self`).
- **Class Attributes:** Shared equally across _all_ instances of that class (defined directly in the class body).

```Python
class Game:
    # 7.6 Class Attribute (shared by all)
    difficulty = "Hard"

    def __init__(self, player_name):
        # Instance Attribute (unique to this player)
        self.player_name = player_name

p1 = Game("Alice")
p2 = Game("Bob")

print(p1.difficulty)  # Output: Hard
Game.difficulty = "Nightmare"  # Changing it changes it for EVERYONE
print(p2.difficulty)  # Output: Nightmare
```

### 7.7 Class Methods & Static Methods

- `@classmethod`: Receives the class (`cls`) instead of the object instance (`self`). Often used for creating alternative constructors.
- `@staticmethod`: Doesn't receive `self` or `cls`. It behaves like a normal function but lives inside the class namespace because it's logically related.

```Python
class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    @classmethod
    def new_guest(cls, name):
        # Returns a new instance with a default score of 0
        return cls(name, 0)

    @staticmethod
    def is_valid_name(name):
        # A utility function that doesn't need data from the class or object
        return len(name) > 2

# Using the class method to build an object
guest = Player.new_guest("Newbie") 
print(guest.score)  # Output: 0

# Using static method without instantiating an object
print(Player.is_valid_name("X"))  # Output: False
```

### 7.8 Polymorphism

Polymorphism means "many forms." It allows different classes to have methods with the exact same name but different behaviors.

```Python
class Mage:
    def attack(self): return "casts Fireball! 🔥"

class Archer:
    def attack(self): return "shoots an Arrow! 🏹"

# A unified interface handling different classes smoothly
def execute_attack(character_object):
    print(character_object.attack())

execute_attack(Mage())   # Output: casts Fireball! 🔥
execute_attack(Archer()) # Output: shoots an Arrow! 🏹
```

### 7.9 Encapsulation (Private variables)

Encapsulation restricts direct access to an object's data to prevent accidental modification.

- `_variable`: **Protected** (A gentle warning to other developers: "Please don't touch this outside the class").
- `__variable`: **Private** (Triggers Name Mangling, making it much harder to access externally).

```Python
class Vault:
    def __init__(self):
        self.public_data = "Open to everyone"
        self._protected_gold = 100  # Internal convention
        self.__private_code = 4321  # Enforced privacy

v = Vault()
print(v.public_data)      # Works fine
print(v._protected_gold)  # Works, but frowned upon

# print(v.__private_code) # Crashes! Raises AttributeError

# If you REALLY need to bypass name mangling (for debugging):
print(v._Vault__private_code)  # Output: 4321
```

## Section 8: There is none


## Section 9: Decorators

Decorators are a design pattern in Python that lets you modify or extend the behavior of a function without permanently changing the original function's source code. They are built on two core Python concepts:

- Functions are **first-class citizens**, meaning they can be stored in variables, passed into other functions, and returned from functions.
- Python supports **Higher-Order Functions**, which are functions that either accept other functions as arguments or return them.

A decorator wraps another function inside additional logic, then returns the modified version.

### 9.1 Function Decorators

A basic decorator takes a function as input, defines an inner wrapper function containing extra behavior, and returns that wrapper. You apply the decorator using the `@decorator_name` syntax above the target function.

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

Multiple decorators can be stacked on the same function. Python applies them from the bottom upward, wrapping the function layer by layer.

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

> [!NOTE] #### Python Decorators: The Importance of `return func()`
> When writing or stacking decorators (like `@boost_power` and `@apply_poison`), including the `return` keyword before invoking the inner function (`return func()`) is critical for preserving data flow.
> ##### Why It Matters:
>
>* **Preserves Return Values:** If the base function calculates and returns a value (e.g., damage numbers, health points), omitting `return` will cause the wrapper to drop the data, resulting in `None`.
>* **Enables Decorator Stacking:** Decorators pass control down a chain. Each wrapper must return the result of the next function so the final output can successfully bubble back up to the main program.
>* **Universal Best Practice:** Even if a function currently only prints text, always using `return func()` ensures the decorator remains compatible if the underlying function is updated to handle math or data later on.

### 9.3 Decorators with Arguments (`*args` and `**kwargs`)

If the original function accepts parameters, the wrapper function must also accept arbitrary positional and keyword arguments using `*args` and `**kwargs`. This allows the decorator to forward all arguments safely to the original function.

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

When a function is wrapped by a decorator, Python replaces the original function metadata (`__name__`, `__doc__`, etc.) with the wrapper function's metadata. To preserve the original function identity, Python provides `functools.wraps`.

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

Without `@wraps`, the function name would incorrectly appear as `"wrapper"`.

### 9.5 Common Use Cases

Decorators are heavily used in real-world software systems because they allow reusable behaviour to be attached to many functions cleanly and consistently.

- **Logging:** Tracking function calls, arguments, return values, and execution time.
- **Authorization / Permissions:** Verifying user roles or admin access before running protected functions.
- **Caching:** Storing expensive function results to avoid repeated computation.
- **Validation:** Checking inputs before the main function executes.
- **Performance Monitoring:** Measuring execution duration for debugging and optimization.

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

Many major Python frameworks rely heavily on decorators.

#### Flask Route Decorators

```Python
from flask import Flask

app = Flask(__name__)

@app.route("/home")
def home():
    return "Welcome Home!"
```

Here, `@app.route("/home")` registers the function as a web route.

#### FastAPI Validation Decorators

```Python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users():
    return {"users": []}
```

The decorator tells FastAPI which HTTP method and endpoint should trigger the function.

### 9.7 Closures and Decorators

Decorators work because Python supports **closures**. A closure happens when an inner function remembers variables from its outer function even after the outer function has finished executing.

```Python
def multiplier(x):

    def multiply(y):
        return x * y

    return multiply

double = multiplier(2)

print(double(5))  # Output: 10
```

The inner `multiply()` function still remembers the value of `x` even after `multiplier()` has completed.

Decorators rely on this exact behavior to remember the original function being wrapped.

### 9.8 Decorator Execution Flow

A decorated function call follows this sequence:

1. The original function is passed into the decorator.
2. The decorator creates a wrapper function.
3. The decorator returns the wrapper.
4. The original function reference is replaced with the wrapper.
5. Calling the function now actually calls the wrapper first.

```Python
@my_decorator
def attack():
    print("Strike!")

# Equivalent to:
attack = my_decorator(attack)
```

---
### Your Assignment Checklist

1. **The Core Function:** Write a simple function called `deal_damage(enemy_name, damage)` that prints: `"{enemy_name} takes {damage} raw damage!"`.
2. **The Cheat Decorator:** Write a decorator function called `@double_damage`.
    - It must accept any arguments passed to the core function using `*args` and `kwargs`.
    - Inside its wrapper, it needs to look at the arguments, **multiply the damage integer by 2**, and pass the upgraded damage into the original function.
    - Use `@wraps` from the `functools` module to ensure the core function doesn't lose its identity.
3. **The Execution:** Apply the decorator to your function, run it, and check its `__name__` attribute to make sure it still says `"deal_damage"`.

### The Starter Template

Here is a skeleton structure to get you moving. Copy this into a new scratch file (like `9B-decorators-practice.py`) and fill in the blanks:

```Python
from functools import wraps

def double_damage(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("⚡ [Cheat Code Activated]: Doubling outgoing damage values!")
        
        # TODO: Modify the damage argument before passing it along.
        # Hint: If you pass positional arguments, args[0] is enemy_name, args[1] is damage.
        
        return func(*args, **kwargs)
    return wrapper

# TODO: Apply your decorator here
def deal_damage(enemy_name, damage):
    print(f"💥 {enemy_name} takes {damage} raw damage!")

# --- Test Execution ---
# 1. Call the function with an enemy name and a base damage number
deal_damage("Goblin King", 50)

# 2. Verify metadata preservation
print(f"Function Name Verified: {deal_damage.__name__}")
```

Give this a quick run in your terminal. If you hit a wall modifying the positional tuple, or if you want to see how to handle it cleanly via keyword arguments instead, throw your code up here and we'll break down the indexing! What approach are you thinking of using to catch that damage variable?


## Section 10: Generators & Iterators

Generators and Iterators are Python tools designed for efficient looping and memory management. Instead of loading entire datasets into RAM all at once, they process values one at a time only when needed.

This concept is called **lazy evaluation** — values are generated on demand rather than precomputed immediately.

---

### 10.1 Generator Functions & 10.2 Generator Expressions

A normal function stops permanently when it reaches `return`.

A **Generator Function** uses the `yield` keyword instead. When Python encounters `yield`, the function pauses execution, saves its internal state, and outputs a value. The next time the generator is called, execution resumes exactly where it left off.

```Python
# 10.1 Generator Function
def enemy_spawner():
    yield "Goblin 🧟"
    yield "Orc 👹"
    yield "Dragon 🐉"

# Creating the generator object
spawner = enemy_spawner()

print(next(spawner))  # Output: Goblin 🧟
print(next(spawner))  # Output: Orc 👹
print(next(spawner))  # Output: Dragon 🐉
```

Unlike lists, generators do not store all values in memory simultaneously.

A **Generator Expression** (10.2) is the shorthand version of a generator function. It looks similar to a list comprehension but uses parentheses `()` instead of square brackets `[]`.

```Python
# Generator Expression
gold_drops = (f"{x} Gold Pieces" for x in range(1, 10001))

print(next(gold_drops))  # Output: 1 Gold Pieces
print(next(gold_drops))  # Output: 2 Gold Pieces
```

If this were written with square brackets:

```Python
gold_drops = [f"{x} Gold Pieces" for x in range(1, 10001)]
```

Python would immediately create all 10,000 strings in memory.

---

### 10.3 `iter()` & `next()`

To fully understand generators, you need to understand Python's iteration system.

#### Iterable

An **Iterable** is any object that can be looped over.

Examples:

- Lists
- Tuples
- Strings
- Dictionaries
- Sets

Iterables contain an internal `__iter__()` method.

#### Iterator

An **Iterator** is the object responsible for actually moving through the sequence one item at a time using the `__next__()` method.

You create an iterator using `iter()`.

You manually retrieve items using `next()`.

```Python
loot_list = ["Sword", "Shield", "Potion"]

# Convert iterable into iterator
loot_iterator = iter(loot_list)

print(next(loot_iterator))  # Output: Sword
print(next(loot_iterator))  # Output: Shield
print(next(loot_iterator))  # Output: Potion
```

If `next()` is called again after the iterator is exhausted:

```Python
print(next(loot_iterator))
```

Python raises a:

```text
StopIteration
```

This exception signals that there are no more values remaining.

---

### 10.4 The `for` Loop Behind the Scenes

A Python `for` loop secretly uses `iter()` and `next()` internally.

This:

```Python
for item in [1, 2, 3]:
    print(item)
```

Roughly behaves like this underneath:

```Python
iterator = iter([1, 2, 3])

while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

The `for` loop automatically catches the `StopIteration` exception and exits cleanly.

---

### 10.5 Creating Custom Iterators

If you want your own class to work inside a `for` loop, you must implement the **Iterator Protocol**:

- `__iter__()` → Returns the iterator object
- `__next__()` → Returns the next value

```Python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration

        num = self.current
        self.current -= 1

        return num

for count in Countdown(3):
    print(count)
```

**Output:**

```text
3
2
1
```

The `StopIteration` exception tells Python when to stop looping.

---

### 10.6 Generators vs Lists

The key difference is memory usage.

#### List

```Python
numbers = [x for x in range(1000000)]
```

- Creates ALL one million values immediately
- Uses large amounts of RAM
- Faster repeated access

#### Generator

```Python
numbers = (x for x in range(1000000))
```

- Generates values one at a time
- Uses extremely little memory
- Slightly slower access due to dynamic generation

Generators trade speed for memory efficiency.

---

### 10.7 Infinite Generators

Generators can theoretically run forever because they only generate values when requested.

```Python
def infinite_mana():

    mana = 100

    while True:
        yield mana
        mana += 10

mana_stream = infinite_mana()

print(next(mana_stream))  # 100
print(next(mana_stream))  # 110
print(next(mana_stream))  # 120
```

This never stores an infinite list in memory.

Infinite generators are heavily used in:

- Real-time event streams
- Game loops
- Sensor monitoring systems
- Live analytics dashboards

---

### 10.8 Memory Efficiency in Real Systems

Generators are extremely important in production systems dealing with large datasets.

#### Example: Reading Massive Log Files

Bad approach:

```Python
with open("huge_log.txt") as file:
    data = file.readlines()
```

This loads the ENTIRE file into RAM.

Better approach:

```Python
def read_logs(filepath):

    with open(filepath) as file:
        for line in file:
            yield line.strip()

for log in read_logs("huge_log.txt"):
    print(log)
```

Only one line exists in memory at a time.

This is how production ETL pipelines and log processors safely handle files that are multiple gigabytes in size.

---

### 10.9 Generator Execution Flow

A generator follows this lifecycle:

1. The generator function is called.
2. Python creates a generator object.
3. No code runs yet.
4. `next()` starts execution until the first `yield`.
5. State is paused and saved.
6. Future `next()` calls resume execution from the previous pause point.
7. Once no more `yield` statements remain, Python raises `StopIteration`.

```Python
def demo():
    print("Start")
    yield 1

    print("Middle")
    yield 2

    print("End")

g = demo()

print(next(g))
print(next(g))
```

**Output:**

```text
Start
1
Middle
2
```

The `"End"` line never prints because execution stops once the generator is exhausted.

---

### 🤔 When to Use Generators?

Generators are ideal when:

- Working with massive datasets
- Streaming real-time data
- Reading large files
- Processing API pagination
- Building pipelines
- Creating infinite sequences
- Reducing RAM usage

Use lists when:

- You need random access (`my_list[500]`)
- You need the data multiple times
- The dataset is small enough to fit comfortably in memory
```