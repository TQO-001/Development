## Section 4: Control Flow

Control flow is how you make decisions, repeat actions, and direct the path of execution through your program. Python's control flow tools are expressive and read almost like plain English.

### 4.1 Conditionals (`if` / `elif` / `else`)

```Python
health = int(input("Enter current health: "))

if health >= 75:
    status = "Healthy"
elif health >= 40:
    status = "Wounded"
elif health > 0:
    status = "Critical"
else:
    status = "Dead"

print(f"Player status: {status}")
```

Conditions can be combined with `and`, `or`, and `not`:

```Python
level = 10
has_sword = True

if level >= 10 and has_sword:
    print("You may enter the dungeon.")
elif level >= 10 or has_sword:
    print("You may enter, but proceed carefully.")
else:
    print("You are not ready.")
```

### 4.2 Ternary Operator

A **ternary expression** is a one-line `if/else` that evaluates to a value. Use it for simple assignments — not for complex logic.

```Python
# Syntax: value_if_true if condition else value_if_false

health = 45
status = "Alive" if health > 0 else "Dead"
print(status)  # Output: Alive

# Inline in a print statement
age = 20
print(f"Access: {'Granted' if age >= 18 else 'Denied'}")  # Output: Access: Granted
```

### 4.3 `for` Loops

A `for` loop iterates over any iterable — lists, strings, ranges, dictionaries, and more.

```Python
# Iterating over a list
party = ["Arthur", "Merlin", "Lancelot"]
for hero in party:
    print(f"{hero} enters the dungeon.")

# range() — generates a sequence of integers
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):       # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 20, 5):   # 0, 5, 10, 15 (start, stop, step)
    print(i)

# enumerate() — gives you the index AND the value
for index, hero in enumerate(party, start=1):
    print(f"  {index}. {hero}")
# Output:
#   1. Arthur
#   2. Merlin
#   3. Lancelot

# zip() — iterates over two lists in parallel
names   = ["Arthur", "Merlin"]
weapons = ["Excalibur", "Staff of Light"]
for hero, weapon in zip(names, weapons):
    print(f"{hero} wields {weapon}")

# Iterating over a dictionary
character_stats = {"health": 250, "mana": 100, "attack": 35}
for stat, value in character_stats.items():
    print(f"{stat}: {value}")
```

### 4.4 `while` Loops

A `while` loop repeats as long as its condition is `True`. Use it when you don't know in advance how many iterations you need.

```Python
# Basic while loop
count = 0
while count < 5:
    print(f"Round {count + 1}")
    count += 1

# Game loop pattern
game_running = True
health = 100

while game_running:
    action = input("Enter action (attack/quit): ")

    if action == "attack":
        health -= 25
        print(f"Took damage! Health: {health}")
        if health <= 0:
            print("You have been defeated.")
            game_running = False
    elif action == "quit":
        print("Exiting game...")
        game_running = False
    else:
        print("Unknown action.")
```

### 4.5 Loop Control: `break`, `continue`, `pass`

```Python
# break — exits the loop immediately
for item in ["Potion", "Sword", "Key", "Map", "Shield"]:
    if item == "Key":
        print(f"Found the {item}! Stopping search.")
        break                         # Exits the loop — "Map" and "Shield" are skipped
    print(f"Checked: {item}")

# continue — skips the rest of the current iteration and moves to the next
for item in ["Potion", None, "Sword", None, "Shield"]:
    if item is None:
        continue                      # Skip this iteration — don't process None
    print(f"Equipping: {item}")

# pass — does nothing, used as a placeholder when syntax requires a block
class FutureFeature:
    pass  # Not implemented yet — will add later

def stub_function():
    pass  # Placeholder until implementation is ready
```

### 4.6 Comprehensions

**Comprehensions** are a Pythonic, one-line syntax for building lists, dictionaries, or sets from an iterable. They combine looping and filtering into a single readable expression.

```Python
# List Comprehension: [expression for item in iterable if condition]
levels = [1, 5, 3, 8, 2, 9, 4]

# All levels doubled
doubled = [level * 2 for level in levels]

# Only levels above 4
high_levels = [level for level in levels if level > 4]
print(high_levels)  # [5, 8, 9]

# Combine: double only the high levels
high_doubled = [level * 2 for level in levels if level > 4]
print(high_doubled)  # [10, 16, 18] — only 5, 8, and 9 were above 4, each doubled

# Dictionary Comprehension: {key: value for item in iterable}
heroes = ["Arthur", "Merlin", "Lancelot"]
hero_hp = {name: 100 for name in heroes}
# {'Arthur': 100, 'Merlin': 100, 'Lancelot': 100}

# Set Comprehension: {expression for item in iterable}
names_with_duplicates = ["Goblin", "Orc", "Goblin", "Troll"]
unique_names = {name.upper() for name in names_with_duplicates}
# {'GOBLIN', 'ORC', 'TROLL'}
```

> [!NOTE]
> Comprehensions are syntactic sugar over `for` loops — faster to write and easier to read for simple transformations. But if the logic gets complex (more than one `if`, nested loops), switch back to a regular `for` loop with `append()` for clarity. A comprehension that needs a comment to explain it has usually outgrown its format.

---

**Practice:**
1. Write an `if/elif/else` chain that assigns a `rank` (`"Bronze"`, `"Silver"`, `"Gold"`) based on a `score` variable.
2. Use a `for` loop with `enumerate()` to print a numbered list of your party members.
3. Write a `while` loop that counts down from 5 to 1, then prints `"Liftoff!"`.
4. Write a list comprehension that filters a list of enemy levels down to only those above 10, then doubles each one.

---
