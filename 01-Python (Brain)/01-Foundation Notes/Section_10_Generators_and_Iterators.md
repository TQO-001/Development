## Section 10: Generators & Iterators

Generators and iterators are Python's tools for efficient looping and memory management. Instead of loading an entire dataset into RAM all at once, they process values one at a time, only when needed. This is called **lazy evaluation** — values are generated on demand rather than computed all up front.

### 10.1 Generator Functions & 10.2 Generator Expressions

A normal function stops permanently once it reaches `return`. A **generator function** uses the `yield` keyword instead. When Python hits `yield`, the function pauses, saves exactly where it was, and hands back a value. The next time you ask the generator for another value, it picks up right where it left off.

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

Unlike a list, a generator never stores all its values in memory at the same time.

A **generator expression** (10.2) is the shorthand version of a generator function. It looks like a list comprehension, but uses parentheses `()` instead of square brackets `[]`.

```Python
# Generator Expression
gold_drops = (f"{x} Gold Pieces" for x in range(1, 10001))

print(next(gold_drops))  # Output: 1 Gold Pieces
print(next(gold_drops))  # Output: 2 Gold Pieces
```

If this were written with square brackets instead:

```Python
gold_drops = [f"{x} Gold Pieces" for x in range(1, 10001)]
```

Python would immediately build all 10,000 strings in memory before you'd even asked for the first one.

### 10.3 `iter()` & `next()`

To really understand generators, it helps to understand the iteration system underneath them.

An **iterable** is any object you can loop over — lists, tuples, strings, dictionaries, and sets are all iterables. What makes something iterable is that it knows how to produce an **iterator**: the object actually responsible for stepping through the sequence one item at a time, using a `__next__()` method.

You create an iterator from an iterable using `iter()`. You manually pull the next value from it using `next()`.

```Python
loot_list = ["Sword", "Shield", "Potion"]

# Convert the iterable into an iterator
loot_iterator = iter(loot_list)

print(next(loot_iterator))  # Output: Sword
print(next(loot_iterator))  # Output: Shield
print(next(loot_iterator))  # Output: Potion
```

If you call `next()` again after the iterator runs out:

```Python
print(next(loot_iterator))
```

Python raises:

```text
StopIteration
```

This exception is the signal that there are no more values left.

### 10.4 The `for` Loop Behind the Scenes

A Python `for` loop is secretly using `iter()` and `next()` internally the whole time. This:

```Python
for item in [1, 2, 3]:
    print(item)
```

behaves roughly like this underneath:

```Python
iterator = iter([1, 2, 3])

while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

The `for` loop automatically catches `StopIteration` for you and exits cleanly — which is exactly why you never see that exception when writing a normal `for` loop.

### 10.5 Creating Custom Iterators

If you want your own class to work inside a `for` loop, it needs to implement the **iterator protocol**: an `__iter__()` method that returns the iterator object, and a `__next__()` method that returns the next value.

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

Raising `StopIteration` inside `__next__()` is what tells Python's `for` loop when to stop.

### 10.6 Generators vs Lists

The key difference between the two comes down to memory.

A list like `numbers = [x for x in range(1000000)]` creates all one million values immediately. It uses a large amount of RAM, but once built, repeated access to its items is fast.

A generator like `numbers = (x for x in range(1000000))` generates values one at a time as you ask for them. It uses very little memory, but each access does a bit of work to produce the next value, so it's marginally slower for repeated access. In short: generators trade a little speed for a lot of memory efficiency.

### 10.7 Infinite Generators

Because generators only produce a value when asked, they can theoretically run forever without ever running out of memory.

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

This never tries to store an infinite list anywhere — it just keeps producing the next value whenever you ask. Infinite generators show up often in real-time event streams, game loops, sensor monitoring, and live analytics dashboards.

### 10.8 Memory Efficiency in Real Systems

Generators matter a lot in production systems that deal with large datasets. Consider reading a massive log file.

The bad approach loads the entire file into RAM at once:

```Python
with open("huge_log.txt") as file:
    data = file.readlines()
```

The better approach yields one line at a time:

```Python
def read_logs(filepath):

    with open(filepath) as file:
        for line in file:
            yield line.strip()

for log in read_logs("huge_log.txt"):
    print(log)
```

Only one line ever exists in memory at a time, no matter how large the file is. This is exactly how production ETL pipelines and log processors safely handle files that are many gigabytes in size.

### 10.9 Generator Execution Flow

A generator's lifecycle follows this sequence: you call the generator function, which creates a generator object — but no code inside it runs yet. Calling `next()` for the first time starts execution and runs until the first `yield`, where it pauses and saves its state. Every later `next()` call resumes from exactly that pause point. Once there are no more `yield` statements left to reach, Python raises `StopIteration`.

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

`"End"` never prints in this example, because the generator is only asked for two values — execution stops right after the second `yield`, before it ever reaches the final `print`.

### When to Use Generators

Generators are the right tool when you're working with massive datasets, streaming real-time data, reading large files, processing paginated API results, building data pipelines, creating infinite sequences, or simply trying to keep RAM usage down.

Reach for a regular list instead when you need random access (`my_list[500]`), you need to use the data more than once, or the dataset is small enough to comfortably fit in memory anyway.

---

**Practice:**
1. Write a generator function `health_potions()` that yields three different potion names, one at a time.
2. Write a generator expression that produces the squares of the numbers 1 through 20, then use `next()` to pull out the first three values.
3. Build a custom class `ManaRegen`, implementing `__iter__` and `__next__`, that yields increasing mana values up to a cap you choose, then raises `StopIteration`.
4. Write a generator function that takes a list of log lines and yields only the ones containing the word `"ERROR"`.

---
