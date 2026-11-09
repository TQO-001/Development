import random
import magnum

# ------------------------------ Core Characters ----------------------------- #
class Character:
    def __init__(self, name, health=150, max_health=150, base_attack=5):
        # Prevent health being configured higher than max_health
        self.max_health = max_health
        self.health = min(health, max_health) 
        self.name = name
        self.base_attack = base_attack
        self.vault = Vault()
        self.weapon_name = "Fists"

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        return f"{self.name} takes {amount} DMG!"

    def is_alive(self):
        return self.health > 0
    
    def equip_weapon(self, weapon_name, bonus_damage):
        self.base_attack += bonus_damage
        self.weapon_name = weapon_name
        return f"Equipped: {weapon_name} (+{bonus_damage} DMG)"

    def attack(self, target):
        # Polymorphic attack handler using instance method interaction
        damage_report = target.take_damage(self.base_attack)
        print(f"{self.name} attacks! {damage_report} -> {target.name}: {target.health}/{target.max_health} HP")

class Warrior(Character):
    def __init__(self, **kwargs):
        # Warriors start with high base stats passing up to parent constructor
        kwargs.setdefault('health', 200)
        kwargs.setdefault('max_health', 200)
        kwargs.setdefault('base_attack', 10)
        super().__init__(**kwargs)

        self.w = Weapon.warrior_weapons
        weapon_choice, bonus = random.choice(list(self.w.items()))
        self.equip_weapon(weapon_choice, bonus)

class Mage(Character):
    def __init__(self, **kwargs):
        kwargs.setdefault('health', 120)
        kwargs.setdefault('max_health', 120)
        kwargs.setdefault('base_attack', 15)
        super().__init__(**kwargs)

        self.w = Weapon.mage_weapons
        weapon_choice, bonus = random.choice(list(self.w.items()))
        self.equip_weapon(weapon_choice, bonus)

# --------------------------------- Equipment -------------------------------- #
class Weapon:
    warrior_weapons = {"Axe": 15, "Sword": 12, "Club": 10, "Dagger": 8}
    mage_weapons = {"Staff": 18, "Grimoire": 14, "Wand": 10, "Ring Of Magic": 7}

    def __init__(self, name, bonus_damage):
        self.name = name
        self.bonus_damage = bonus_damage
    
    def __str__(self):
        return f"{self.name} (+{self.bonus_damage} DMG)"
    
    def __repr__(self):
        return f"Weapon('{self.name}', {self.bonus_damage})"

# ----------------------------------- Vault ---------------------------------- #
class Vault:
    def __init__(self):
        self.__gold_balance = 0

    def add_gold(self, amount):
        self.__gold_balance += amount
        print(f"💰 {amount} Gold Added to Vault.")
    
    def get_balance(self):
        return self.__gold_balance

# --------------------------- Game Rules & Utilities -------------------------- #
class GameConfig:
    VERSION = "1.0.0"

    @classmethod
    def create_active_dummy(cls, name="Training Dummy"):
        # Creates an active opponent dummy
        return Character(name=name, health=60, max_health=60, base_attack=6)

    @staticmethod
    def validate_name(name=""):
        return bool(name.strip())

# ---------------------------------------------------------------------------- #
def character_stats(ch):
    print(f"\n--- Stats for {ch.name} ---")
    print(f"Class Weapon: {ch.weapon_name}")
    print(f"Health:       {ch.health}/{ch.max_health} HP")
    print(f"Attack Power: {ch.base_attack} ATK")
    print("-" * 25)

def start_duel(player, enemy):
    character_stats(player)
    character_stats(enemy)

    # Determine order
    turn_order = [player, enemy] if random.randint(1, 2) == 1 else [enemy, player]
    print(f"⚡ {turn_order[0].name} goes first!")

    while player.is_alive() and enemy.is_alive():
        # First Attacker turns
        turn_order[0].attack(turn_order[1])
        if not turn_order[1].is_alive():
            break
        
        # Second Attacker turns
        turn_order[1].attack(turn_order[0])
        print() # Line space for clean layout

    winner = player if player.is_alive() else enemy
    loser = enemy if player.is_alive() else player
    print(f"\n🏆 {winner.name} wins! {loser.name} has been defeated.")
    return winner.name

# ---------------------------------------------------------------------------- #
#                                   Game Flow                                  #
# ---------------------------------------------------------------------------- #
print("Welcome Traveler to...")
print(f"The Homestead Chronicles {GameConfig.VERSION}")

name = input("Enter your name: ")
while not GameConfig.validate_name(name):
    name = input("Name can't be empty! Enter valid name: ")

print("\nPlease choose a class:")
print("\t(1) Warrior\n\t(2) Mage")
chosen_class = input("Choice: ")

if chosen_class == "1":
    player = Warrior(name=name)
elif chosen_class == "2":
    player = Mage(name=name)
else:
    print("Invalid option! Defaulting to base adventurer.")
    player = Character(name=name)

print("\nAn active opponent approaches for target practice!")
enemy = GameConfig.create_active_dummy("[Nameless Goblin]")

if start_duel(player, enemy) == player.name:
    player.vault.add_gold(25)
    print(f"Vault Balance: {player.vault.get_balance()} Gold")
else:
    print("Better luck next time, warrior. 🙏")