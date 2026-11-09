## Section 1: Python Basics

Python is a high-level, interpreted language — meaning the code you write reads close to plain English, and Python handles translating it into something the computer can run. Before writing any real logic, it helps to get comfortable with how Python reads your code, how things should be named, and the basic tools for getting data in and out of a program. These are small habits, but they're the first thing any senior developer notices in a code review.

### 1.1 Comments

A comment is a line Python completely ignores at runtime. They exist for human readers only.

```Python
# This is a single-line comment. Use the hash symbol.

# Variables
player_health = 100  # You can also place comments at the end of a line
```

A **docstring** (documentation string) is a multi-line string literal placed at the top of a module, class, or function. Python stores it in the `__doc__` attribute, and tools like IDEs and `help()` display it automatically.

```Python
"""
This is a docstring.
It can span multiple lines.
It is used to document classes, functions, and modules.
"""

def cast_spell(spell_name):
    """
    Casts a spell by name.
    Returns a formatted string describing the action.
    """
    return f"Casting {spell_name}!"
```

> [!NOTE]
> **Single-line comments** use `#`. **Docstrings** use triple quotes `"""`. Use docstrings for functions and classes — they're documentation other tools can read automatically. Use `#` for quick inline explanations.

### 1.2 Naming Conventions

Python enforces readability through naming conventions defined in **PEP 8** — the official Python Style Guide. Every professional Python codebase follows these.

```Python
# Variables & Functions: snake_case (all lowercase, words separated by underscores)
player_health = 150
max_mana_pool = 200

def calculate_damage(base_attack, multiplier):
    return base_attack * multiplier

# Constants: UPPER_SNAKE_CASE (signals this value should never change)
MAX_PARTY_SIZE = 4
DEFAULT_SPAWN_RATE = 0.75
PI = 3.14159

# Classes: PascalCase / CamelCase (every word capitalised, no underscores)
class PlayerCharacter:
    pass

class BossEnemy:
    pass

# Private variables: _leading_underscore (convention: internal use only)
_internal_counter = 0

# Name-mangled (hard private): __double_underscore (covered in Section 7)
__secret_vault_code = 9999
```

| Type | Convention | Example |
|---|---|---|
| Variable | `snake_case` | `player_health` |
| Function | `snake_case` | `deal_damage()` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_LEVEL` |
| Class | `PascalCase` | `GameCharacter` |
| Private | `_single_underscore` | `_spawn_timer` |

### 1.3 Variables & Assignment

A variable is a name that points to a value stored in memory. Python is **dynamically typed** — you don't declare a type up front, Python figures it out from the value itself.

```Python
# Assignment
player_name  = "Arthur"
player_level = 1
player_health = 98.5
is_alive = True

# Multiple assignment in one line
x, y, z = 10, 20, 30

# Swap two variables (Python-specific shorthand — no temp variable needed)
a, b = 5, 10
a, b = b, a
print(a, b)  # Output: 10 5

# Check the type of any variable
print(type(player_name))   # Output: <class 'str'>
print(type(player_level))  # Output: <class 'int'>
print(type(is_alive))      # Output: <class 'bool'>
```

### 1.4 Output & Input

`print()` sends text to the terminal. `input()` pauses execution and waits for the user to type something — it always returns a `str`.

```Python
# Basic print
print("Welcome to the Realm!")

# print() with multiple values (separated by spaces by default)
print("Player:", "Arthur", "Level:", 5)  # Output: Player: Arthur Level: 5

# f-strings (formatted string literals) — the modern standard
player_name = "Arthur"
player_level = 5
print(f"Welcome, {player_name}! You are Level {player_level}.")

# Expressions inside f-strings
base_attack = 20
multiplier = 1.5
print(f"Critical Hit! Damage: {base_attack * multiplier:.1f}")  # Output: Critical Hit! Damage: 30.0

# input() always returns a string
name = input("Enter your character name: ")
print(f"Greetings, {name}!")

# Convert input to a number
age_str = input("Enter your age: ")
age = int(age_str)  # Convert string to integer
```

> [!NOTE]
> `input()` **always returns a string**, even if the user types a number. If you need it as an `int` or `float`, convert it explicitly: `int(input("Enter age: "))`.

### 1.5 Basic Operators

```Python
# Arithmetic Operators
print(10 + 3)   # 13  — Addition
print(10 - 3)   # 7   — Subtraction
print(10 * 3)   # 30  — Multiplication
print(10 / 3)   # 3.333... — Division (always returns a float)
print(10 // 3)  # 3   — Floor Division (rounds down, returns an int)
print(10 % 3)   # 1   — Modulo (the remainder)
print(10 ** 3)  # 1000 — Exponentiation (10 to the power of 3)

# Comparison Operators (return True or False)
print(5 == 5)   # True  — Equal to
print(5 != 3)   # True  — Not equal to
print(10 > 5)   # True  — Greater than
print(10 < 5)   # False — Less than
print(5 >= 5)   # True  — Greater than or equal to
print(5 <= 4)   # False — Less than or equal to

# Assignment Shorthand
health = 100
health += 10   # health = health + 10 → 110
health -= 25   # health = health - 25 → 85
health *= 2    # health = health * 2  → 170
health //= 3   # health = health // 3 → 56

# Logical Operators
print(True and False)  # False — Both must be True
print(True or False)   # True  — At least one must be True
print(not True)        # False — Inverts the boolean
```

---

**Practice:**
1. Create three variables — your character's `name`, `level`, and `is_alive` status — and print all three in a single f-string.
2. Write an `input()` prompt asking for the user's age, convert it to an `int`, and print whether they're old enough to enter a tavern (18+).
3. Using the shorthand operators (`+=`, `-=`, etc.), simulate a player starting at 100 health, taking 35 damage, then healing 10. Print the final health.

---
