## Section 7: Object-Oriented Programming (OOP)

OOP is a paradigm that lets you bundle properties (attributes) and behaviours (methods) into individual objects. Think of a class as a blueprint, and an object as the actual house built from that blueprint.

### 7.1 Classes & Objects

You define a class using the `class` keyword (remember your CamelCase convention from Section 1!).

```Python
class Character:
    def __init__(self, name, role):
        self.name = name    # Instance Attribute
        self.role = role    # Instance Attribute
        self.level = 1      # Default value attribute

# Creating Objects (Instances)
hero1 = Character("Arthur", "Warrior")
hero2 = Character("Merlin", "Mage")

print(hero1.name)  # Output: Arthur
```

### 7.2 The `__init__()` Function

The `__init__` method is the constructor — it runs automatically whenever you create a new instance (object) of a class. The `self` parameter represents the specific object you're currently creating or modifying, and it's how the object refers to its own data.

```Python
class Character:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.level = 1
```

### 7.3 Attributes & Methods

**Attributes** are variables bound to an object — the object's data. **Methods** are functions defined inside a class that operate on that data. They must take `self` as their first parameter so they can access the instance's attributes.

```Python
class Character:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.level = 1

    # Method
    def level_up(self):
        self.level += 1
        return f"{self.name} reached level {self.level}!"

hero1 = Character("Arthur", "Warrior")
print(hero1.level_up())  # Output: Arthur reached level 2!
```

### 7.4 Inheritance

Inheritance lets a new class (child/subclass) adopt the attributes and methods of an existing class (parent/superclass), so you don't have to repeat code. You use `super().__init__()` to pass data back up to the parent's constructor.

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
        super().__init__(name)  # Calls the parent constructor
        self.shop_name = shop_name

vendor = Blacksmith("Andre", "Firelink Shrine")
print(vendor.speak())  # Output: Andre says hello. (Inherited method!)
```

### 7.5 Special Methods (`__str__`, `__repr__`)

Also called **dunder methods** (double underscore), these let you define how your objects behave with built-in Python operations.

- `__str__` controls what's shown when you `print()` the object — meant for a human-readable display.
- `__repr__` controls the official string representation, used for debugging.

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

**Instance attributes** are unique to each specific object (defined inside `__init__` using `self`). **Class attributes** are shared equally across *all* instances of that class (defined directly in the class body).

```Python
class Game:
    # Class Attribute (shared by all instances)
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

`@classmethod` receives the class itself (`cls`) instead of an object instance (`self`). It's often used for alternative constructors. `@staticmethod` doesn't receive `self` or `cls` at all — it behaves like a normal function that just happens to live inside the class namespace because it's logically related.

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

# Using the static method without instantiating an object
print(Player.is_valid_name("X"))  # Output: False
```

### 7.8 Polymorphism

Polymorphism means "many forms." It lets different classes have methods with the exact same name but different behaviour underneath.

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

### 7.9 Encapsulation (Private Variables)

Encapsulation restricts direct access to an object's data, to prevent accidental modification.

- `_variable`: **Protected** — a gentle convention telling other developers "please don't touch this outside the class."
- `__variable`: **Private** — triggers name mangling, making it much harder to access from outside.

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

---

**Practice:**
1. Create a `Spell` class with `name` and `damage` attributes, plus a `cast()` method that returns a description string.
2. Create a parent class `Enemy` and a child class `Boss` that inherits from it and adds an extra attribute, like `phase`.
3. Add `__str__` and `__repr__` methods to one of your classes so it prints nicely.
4. Add a `@classmethod` alternative constructor to a class of your choice (for example, `Player.new_guest()`).

---
