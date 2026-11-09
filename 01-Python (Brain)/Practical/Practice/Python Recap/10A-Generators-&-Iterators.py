# ----------- 10.1 Generator Functions & 10.2 Generator Expressions ---------- #
# 10.1 Generator Function
def enemy_spawner():
    yield "Goblin"
    yield "Orc"
    yield "Dragon"

# Creating the generator object
spawner = enemy_spawner()

print(next(spawner))
print(next(spawner))
print(next(spawner))

# 10.2 Generator Expression
gold_drops = (f"{x} Gold Pieces" for x in range(1, 51))

print(next(gold_drops))
print(next(gold_drops))
print(next(gold_drops))

gold_drops_list = [f"{x} Gold Pieces" for x in range(1, 10001)]

# print(len(gold_drops)) # outputs error because this is a generator expression
print(f"In gold_drops_list there are ", len(gold_drops_list), " pieces of gold")

# ------------------------- 10.3 `iter()` & `next()` ------------------------- #
loot_list  = ["Sword", "Shield", "Potion"]

# Convert iterable into iterator
loot_iterator = iter(loot_list)

print(next(loot_iterator))
print(next(loot_iterator))
print(next(loot_iterator))
# print(next(loot_iterator)) # Error: cannot interate anymore

# ------------------- 10.4 The `for` loop behind the scenes ------------------ #
for item in [1, 2, 3]:
    print(item)

# ---------------------- 10.5 Creating custom iterators ---------------------- #

class Countdown:
    def __init__(self, start):
        self.current = start # Used different names to specify the diff between start and current number because will change but start will remain the same

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        
        result = self.current
        self.current -= 1

        return result

for count in Countdown(3):
    print(count)

class Countup:
    def __init__(self, start = 0, end = 0):
        self.start = start
        self.current = start
        self.end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration

        result = self.current
        self.current += 1

        return result

for count in Countup(end=10):
    print(count)

# ------------------------- 10.6 Generators vs Lists ------------------------- #
# List
numbers = [x for x in range(21)]
print(numbers)

numbers2 = (x for x in range(6))
for number in numbers2:
    print(number)

# ------------------------- 10.7 Infinite Generators ------------------------- #
def infinite_mana():

    mana = 100

    while True:
        yield mana
        mana += 10
    
mana_stream = infinite_mana()

print(next(mana_stream))
print(next(mana_stream))
print(next(mana_stream))

# This is just a test

def life():
    hearts = 1
    
    while True:
        yield hearts
        hearts += 1

lives = life()

print("+1 life (Player ate mushroom),", next(lives), " Lives left")
print("+1 life (Player ate mushroom),", next(lives), " Lives left")
print("+1 life (Player ate mushroom),", next(lives), " Lives left")

# ------------------ 10.8 Memory efficiency in real systems ------------------ #
with open("huge_log.txt", "w", encoding="utf-8") as file:
    file.write("[14:23:01] Rename folder \"image\" to \"img\".\n")
    file.write("[14:23:01] Uploaded file \"james_dean\" to github\n")

"""
# Bad Approach
with open("huge_log.txt") as file:
    data = file.readlines()
    for x in data:
        print(x)
"""

def read_logs(filepath):

    with open(filepath) as file:
        for line in file:
            yield line.strip()

for log in read_logs("huge_log.txt"):
    print(log)

# ----------------------- 10.9 Generator execution flow ---------------------- #
def demo():
    print("Start")
    yield 1

    print("Middle")
    yield 2

    print("End") # This never prints

g = demo()

print(next(g))
print(next(g))