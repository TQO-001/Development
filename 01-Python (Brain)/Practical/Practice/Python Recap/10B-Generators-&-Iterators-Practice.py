import random
# --------------------- 10.1 The enemy generator function -------------------- #
def inifinite_enemy_generator():
    enemies = ["Goblin", "Orc", "Troll"]
    enemy_count = 1

    while True:
        yield f"Enemy ID #[{enemy_count}]: [{random.choice(enemies)}]"
        enemy_count += 1

# ------------------------- 10.3 The manual execution ------------------------ #
print("#", "---"*8, "Manual Execution", "---"*8, "#")
spawn_enemy = inifinite_enemy_generator()

print(next(spawn_enemy))
print(next(spawn_enemy))
print(next(spawn_enemy))
print(next(spawn_enemy))

# -------------------------- 10.1 The loop execution ------------------------- #
print("---"*8, "Automated Execution", "---"*8, "#")
[print(next(spawn_enemy)) for x in range(1, 6)]


# -------------------- Practicing Iterators and Generators ------------------- #
# Iterators
print("---"*8, "Iterators", "---"*8, "#")
class Dice:
    def __init__(self, rolls):
        self.rolls = rolls
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.count <= self.rolls:
            self.count += 1
            return random.randint(1, 7)
        else:
            raise StopIteration

dice = Dice(3)
for die in dice:
    print(die)

# Generators
# without using a generator
print("---"*8, "Generators", "---"*8, "#")
def count_to(n):
    numbers = []
    count = 1
    while count <= n:
        numbers.append(count)
        count += 1
    return numbers

number = int(input("Enter a number to count to: "))

for n in count_to(number):
    print(n)

# with a generator
print("---"*8, "Generators", "---"*8, "#")
def count_to(n):
    count = 1
    while count <= n:
        yield count
        count += 1

number = int(input("Enter a number to count to: "))

for n in count_to(number):
    print(n)
