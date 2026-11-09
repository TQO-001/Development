## Section 2: Data Types

Python has two broad categories of data types: **primitives**, which hold a single value, and **collections**, which hold multiple values. Knowing which type to reach for, and what operations it supports, is the foundation of writing clean logic.

### 2.1 Primitive Types

Python has four core primitives:

```Python
# int — whole numbers (positive, negative, or zero)
gold_coins   = 500
floor_damage = -15
player_score = 0

# float — decimal numbers
movement_speed = 4.75
crit_chance    = 0.25
pi             = 3.14159

# str — text, enclosed in single or double quotes (both work identically)
player_name  = "Arthur"
enemy_title  = 'Goblin King'
battle_shout = f"{player_name} charges into battle!"

# bool — True or False (capital first letter — they are Python keywords)
is_alive    = True
has_shield  = False
game_over   = not is_alive  # False (not True → False)

# None — represents the absence of a value (like null in other languages)
equipped_weapon = None
print(equipped_weapon)  # Output: None
```

### 2.2 String Methods

Strings are one of the most-used types. Python strings are **immutable** — string methods return a new string, they never modify the original.

```Python
name = "  Arthur Pendragon  "

# Whitespace
print(name.strip())     # "Arthur Pendragon"  — removes leading/trailing whitespace
print(name.lstrip())    # "Arthur Pendragon  " — left side only
print(name.rstrip())    # "  Arthur Pendragon" — right side only

name = "Arthur Pendragon"

# Case
print(name.upper())     # "ARTHUR PENDRAGON"
print(name.lower())     # "arthur pendragon"
print(name.title())     # "Arthur Pendragon" (first letter of each word)

# Search
print(name.startswith("Arthur"))   # True
print(name.endswith("dragon"))     # True (case-sensitive)
print("Pendragon" in name)         # True — membership check

# Replace & Split
print(name.replace("Arthur", "Merlin"))  # "Merlin Pendragon"
parts = name.split(" ")                  # ["Arthur", "Pendragon"]
print(" | ".join(parts))                 # "Arthur | Pendragon"

# Find
print(name.find("Pend"))  # 7 — index of first occurrence, -1 if not found
print(len(name))          # 17 — character count
```

### 2.3 Lists

A `list` is an ordered, **mutable** collection of items. Items can be of any type, and duplicates are allowed.

```Python
# Creating a list
inventory = ["Sword", "Shield", "Potion", "Map"]

# Indexing (zero-based)
print(inventory[0])   # "Sword"   — first item
print(inventory[-1])  # "Map"     — last item (negative index counts from the end)
print(inventory[1:3]) # ["Shield", "Potion"] — slice (start inclusive, end exclusive)

# Modifying
inventory.append("Torch")            # Adds to the end
inventory.insert(1, "Dagger")        # Inserts at index 1
inventory.remove("Map")              # Removes first occurrence of "Map"
popped = inventory.pop()             # Removes & returns last item
popped_at = inventory.pop(0)         # Removes & returns item at index 0

# Querying
print(len(inventory))                # Number of items
print("Sword" in inventory)          # True — membership check
print(inventory.index("Shield"))     # Index of "Shield"
print(inventory.count("Potion"))     # Number of occurrences

# Sorting
inventory.sort()                     # Sorts in-place (modifies the list)
sorted_copy = sorted(inventory)      # Returns a new sorted list

# List operations
enemies  = ["Goblin", "Orc"]
bosses   = ["Dragon", "Lich"]
all_foes = enemies + bosses          # Concatenate lists
doubled  = enemies * 2               # Repeat list: ["Goblin", "Orc", "Goblin", "Orc"]
```

### 2.4 Tuples

A `tuple` is an ordered, **immutable** collection. Once created, it can't be changed. Use tuples for data that should never be modified — coordinates, RGB values, function return data.

```Python
# Creating a tuple (parentheses are optional but conventional)
player_position = (42, 17)       # x, y coordinates
rgb_colour      = (255, 165, 0)  # Orange

# Accessing — same indexing as lists
print(player_position[0])    # 42
print(player_position[1])    # 17

# Unpacking — assigns each element to a variable
x, y = player_position
print(f"Player is at x={x}, y={y}")

# Tuples are immutable — this raises a TypeError:
# player_position[0] = 99  # TypeError: 'tuple' object does not support item assignment

# A single-element tuple needs a trailing comma
one_item = ("Excalibur",)    # This is a tuple
not_a_tuple = ("Excalibur")  # This is just a string
print(type(one_item))    # <class 'tuple'>
print(type(not_a_tuple)) # <class 'str'>
```

### 2.5 Sets

A `set` is an **unordered**, **mutable** collection of **unique** items. Duplicates are automatically removed. Sets are optimised for membership checks and mathematical set operations.

```Python
# Creating a set
active_buffs = {"Strength", "Haste", "Shield", "Strength"}  # Duplicate removed
print(active_buffs)  # {'Strength', 'Haste', 'Shield'} — order not guaranteed

# Modifying
active_buffs.add("Regen")          # Add a single item
active_buffs.discard("Haste")      # Remove if it exists (no error if missing)
active_buffs.remove("Shield")      # Remove — raises KeyError if missing

# Membership check (faster than lists for large collections)
print("Regen" in active_buffs)    # True

# Set Operations
class_a_skills = {"Slash", "Block", "Parry"}
class_b_skills = {"Slash", "Fireball", "Teleport"}

print(class_a_skills | class_b_skills)  # Union — all unique skills from both
print(class_a_skills & class_b_skills)  # Intersection — skills in BOTH
print(class_a_skills - class_b_skills)  # Difference — in A but not B
```

### 2.6 Dictionaries

A `dict` is an ordered (Python 3.7+), **mutable** collection of **key-value pairs**. Keys must be unique and immutable (strings, numbers, tuples). Values can be anything.

```Python
# Creating a dictionary
player = {
    "name":        "Arthur",
    "level":       15,
    "health":      250,
    "is_alive":    True,
    "inventory":   ["Sword", "Potion"]
}

# Accessing values
print(player["name"])           # "Arthur"
print(player.get("level"))      # 15
print(player.get("mana", 0))    # 0 — default value if key missing (no KeyError)

# Modifying
player["level"] = 16            # Update existing key
player["mana"] = 100            # Add new key
del player["is_alive"]          # Delete a key

# Checking existence
print("name" in player)         # True — checks keys

# Iterating
for key in player:
    print(key)                  # Iterates over keys

for key, value in player.items():
    print(f"{key}: {value}")    # Iterates over key-value pairs

for value in player.values():
    print(value)                # Iterates over values only

# Useful methods
keys   = list(player.keys())    # All keys as a list
values = list(player.values())  # All values as a list

# Nested dictionaries
party = {
    "warrior": {"name": "Arthur", "hp": 250},
    "mage":    {"name": "Merlin", "hp": 120}
}
print(party["mage"]["name"])   # "Merlin"
```

### 2.7 Type Conversion

```Python
# String → Number
age_str   = "25"
age_int   = int(age_str)     # 25
price_str = "19.99"
price_flt = float(price_str) # 19.99

# Number → String
level    = 15
level_str = str(level)        # "15"

# To Boolean
print(bool(0))       # False — zero is falsy
print(bool(1))       # True  — any non-zero number is truthy
print(bool(""))      # False — empty string is falsy
print(bool("hello")) # True  — non-empty string is truthy
print(bool(None))    # False — None is falsy
print(bool([]))      # False — empty list is falsy

# Conversion between collections
my_list  = [1, 2, 2, 3, 3]
my_set   = set(my_list)       # {1, 2, 3} — removes duplicates
my_tuple = tuple(my_set)      # (1, 2, 3) — order not guaranteed from a set
back_to_list = list(my_tuple) # [1, 2, 3]

# isinstance() — safer than type() for checking types
print(isinstance(age_int, int))    # True
print(isinstance(price_flt, (int, float)))  # True — checks against multiple types
```

---

**Practice:**
1. Create a list called `inventory` for your party. Add an item, remove an item, and print the final list.
2. Create a `player` dictionary with `name`, `level`, and `hp` keys. Loop through it and print each key-value pair.
3. Create two sets of skills for two different character classes, and print their union, intersection, and difference.
4. Take a string like `"42"`, convert it to an `int`, and use `isinstance()` to confirm the conversion worked.

---
