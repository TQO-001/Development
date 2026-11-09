# 7.1 Classes & Objects & 7.2 The `__init__()` function (Object Constructor)
class Character:
    def __init__(self, name, role):
        # 7.3 Attributes & Methods
        self.name = name
        self.role = role
        self.level = 1
    
    def level_up(self):
        self.level += 1
        return f"{self.name} reached level {self.level}!"

# Instantiating Objects
hero1 = Character("Adrianna", "Warrior")

# 7.4 Inheritance
class Blacksmith(Character): # Inherits from Character class
    def __init__(self, name, shop_name):
        super().__init__(name, role="Merchant") # Pass data up to parent
        self.shop_name = shop_name

# 7.5 Special Methods (`__str__`, `__repr__`)
class Weapon:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage
    
    def __str__(self):
        return f"{self.name} ({self.damage} DMG)"
    
    def __repr__(self):
        return f"Weapon('{self.name}', {self.damage})"

# 7.6 Class vs. Instance Attributes
class Game:
    difficulty = "Hard" # Class Attribute (shared)

    def __init__(self, player_name):
        self.player_name = player_name # Instance Attribute (Unique)

# 7.7 Class Methods & Static Methods
class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    @classmethod
    def new_guest(cls, name):
        return cls(name, 0) # Alternative constructor
    
    @staticmethod
    def is_valid_name(name):
        return len(name) > 2 # Utility method

# 7.8 Polymorphism
class Mage:
    def attack(self): return "casts Fireball!"

class Archer:
    def attack(self): return "shoots an Arrow!"

# One interface to handle different types of objects smoothly
def execute_attack(character):
    print(character.attack())

# 7.9 Encapsulation (Private variables)
class Vault:
    def __init__(self):
        self.public_data = "Everyone can see this"
        self.protected_gold = 100 # Internal use indicator
        self.__private_code = 4321 # Enforced privacy via name mangling
