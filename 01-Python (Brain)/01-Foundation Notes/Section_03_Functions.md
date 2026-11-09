## Section 3: Functions

A function is a named, reusable block of code that performs a specific task. Functions are the primary tool for keeping code **DRY** (Don't Repeat Yourself). Good functions do one thing, do it well, and communicate clearly through their name and parameters.

### 3.1 Defining & Calling

You define a function with the `def` keyword. You call it by using its name followed by parentheses.

```Python
# Basic function definition
def greet_player(name):
    return f"Welcome back, {name}!"

# Calling the function
message = greet_player("Arthur")
print(message)  # Output: Welcome back, Arthur!

# Function with no parameters
def display_divider():
    print("-" * 40)

display_divider()

# Function with multiple parameters
def calculate_damage(base_attack, multiplier):
    return base_attack * multiplier

dmg = calculate_damage(50, 1.5)
print(dmg)  # Output: 75.0
```

### 3.2 Default Parameters & Type Hints

**Default parameters** give a parameter a fallback value when no argument is passed. **Type hints** annotate the expected type — Python doesn't enforce them, but IDEs and linters use them to catch mistakes early.

```Python
# Default parameters
def spawn_enemy(name, health=100, attack=10):
    return f"{name} spawned — HP: {health}, ATK: {attack}"

print(spawn_enemy("Goblin"))                 # Uses defaults: HP=100, ATK=10
print(spawn_enemy("Orc", health=250))        # Overrides health only
print(spawn_enemy("Dragon", 1000, 75))       # All provided

# Type hints (annotations)
def heal_player(player_name: str, amount: int) -> str:
    return f"{player_name} recovered {amount} HP."

def get_party_size() -> int:
    return 4

# Type hints do NOT enforce types at runtime — they are hints only
# heal_player("Arthur", "lots")  # Python won't crash here — but mypy/pylance will flag it
```

> [!NOTE]
> Default parameters must always come **after** required parameters. `def f(a, b=10)` is valid. `def f(a=10, b)` raises a `SyntaxError`.

### 3.3 Lambda Functions

A **lambda** is a single-expression anonymous function. Use them for short, throwaway logic — especially when passing a function as an argument.

```Python
# Syntax: lambda parameters: expression

# Equivalent named function
def add(x, y):
    return x + y

# Equivalent lambda
add = lambda x, y: x + y
print(add(3, 4))  # Output: 7

# Common pattern: sorting by a custom key
party = [
    {"name": "Arthur", "level": 15},
    {"name": "Merlin", "level": 22},
    {"name": "Lancelot", "level": 18}
]

# Sort party list by level (ascending)
party.sort(key=lambda member: member["level"])
print(party[0]["name"])  # Output: Arthur (lowest level first)

# Sort descending
party.sort(key=lambda member: member["level"], reverse=True)
print(party[0]["name"])  # Output: Merlin
```

### 3.4 Higher-Order Functions

A **Higher-Order Function (HOF)** is a function that either accepts another function as an argument, or returns a function as its result. `map()`, `filter()`, and `sorted()` are the most common built-in HOFs.

```Python
def shout(text: str) -> str:
    return text.upper()

def greet(func):
    """Accepts a function and uses it to transform a greeting."""
    return func("hello, adventurer")

result = greet(shout)
print(result)  # Output: HELLO, ADVENTURER

# --- Built-in HOFs ---

enemy_names = ["goblin", "orc", "troll", "dragon"]

# map() — applies a function to every item in an iterable
uppercased = list(map(str.upper, enemy_names))
print(uppercased)  # ['GOBLIN', 'ORC', 'TROLL', 'DRAGON']

# filter() — keeps only items where the function returns True
long_names = list(filter(lambda name: len(name) > 3, enemy_names))
print(long_names)  # ['goblin', 'troll', 'dragon']

# sorted() with a key function
by_length = sorted(enemy_names, key=len)
print(by_length)  # ['orc', 'goblin', 'troll', 'dragon']
```

### 3.5 `*args` & `**kwargs`

`*args` collects extra **positional** arguments into a tuple. `**kwargs` collects extra **keyword** arguments into a dictionary. Together, they let a function accept a flexible number of inputs.

```Python
# *args — variable positional arguments
def total_damage(*hits):
    """Accepts any number of damage values and returns the total."""
    print(f"Hits received: {hits}")  # hits is a tuple
    return sum(hits)

print(total_damage(10, 25, 5))        # Hits received: (10, 25, 5) → 40
print(total_damage(100))              # Hits received: (100,) → 100
print(total_damage(10, 20, 30, 40))   # Hits received: (10, 20, 30, 40) → 100

# **kwargs — variable keyword arguments
def create_character(**stats):
    """Accepts any character stats as named arguments."""
    print(f"Stats received: {stats}")  # stats is a dict
    return stats

hero = create_character(name="Arthur", level=10, gold=500)
# Output: Stats received: {'name': 'Arthur', 'level': 10, 'gold': 500}

# Combining all types — order matters: regular → *args → keyword defaults → **kwargs
def battle_report(title: str, *combatants, location="Unknown", **details):
    print(f"Battle: {title}")
    print(f"Combatants: {combatants}")
    print(f"Location: {location}")
    print(f"Details: {details}")

battle_report(
    "The Final Stand",
    "Arthur", "Merlin", "Goblin King",
    location="Camelot",
    duration="3 hours",
    outcome="Victory"
)
```

---

**Practice:**
1. Write a function `cast_spell(spell_name, mana_cost=10)` using a default parameter, then call it twice — once using the default, once overriding it.
2. Write a lambda that sorts a list of party member dictionaries by level.
3. Write a function `total_loot(*items)` that accepts any number of items using `*args` and returns how many were collected.
4. Write a function `build_character(**stats)` that accepts any number of keyword arguments and prints each one out.

---
