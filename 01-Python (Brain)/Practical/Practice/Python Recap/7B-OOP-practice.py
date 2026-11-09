# ---------------------------------------------------------------------------- #
#                         The Homestead Chronicles v1.0                        #
# ---------------------------------------------------------------------------- #
# NOTE To further improve on this code you could... = Toffy
# ---------------------------------------------------------------------------- #
import random
import magnum

# ------------------------------ Core Characters ----------------------------- #
""" TODO
Toffy use a dataclass
"""
class Character():
    def __init__(self, name, health=150, max_health=150, base_attack=5):
        self.name = name
        self.health = health
        self.max_health = max_health
        self.base_attack = base_attack
        self.vault = Vault()

        """ TODO
        Toffy make sure to check if 'health' is higher than
        the 'max_health' and issue an error if otherwise
        """

    """ NOTE
    I have a problem with this being an instance method
    """
    def take_damage(self, amount):
        self.health -= amount
        return f"{self.name} (takes {amount} DMG)"

    """ NOTE
    why is this here
    """
    def inflict_damage(target):
        target.health -= amount
        return f"{name} (takes {amount} DMG)"
    
    def is_alive(self):
        if (self.health > 0):
            return True
        else:
            return False
    
    def equip_weapon(self, weapon_name, bonus_damage):
        self.base_attack += bonus_damage
        """ NOTE 
        The rest of this method is optional as it wasn't 
        asked for only the above was, but I added it for 
        better context to the user
        """
        self.equiped = Weapon(weapon_name, bonus_damage)
        return f"Equiped: {self.equiped}"

    """ NOTE
    Do more research on Polymorphism
    """

    """ FIXME
    I think there is a logical bug with the attack method
    while damage is taken, the health is incorrect
    """
    def attack(self, target):
        target.health -= self.base_attack
        print(f"{target.name} {target.health}/{target.max_health} (takes {self.base_attack} DMG)")

class Warrior(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health = 100
        self.max_health = self.health

        # Making sure the warrior always starts with a weapon
        self.w = Weapon.warrior_weapons
        self.weapon_name, self.bonus_damage = random.choice(list(self.w.items()))
        
        self.equip_weapon(self.weapon_name, self.bonus_damage)

    def attack(self, target):
        super().attack(target)
        return f"{self.name} slashes with [{self.weapon_name}]"

class Mage(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health = 100
        self.max_health = self.health

        # Making sure the warrior always starts with a weapon
        self.w = Weapon.mage_weapons
        self.weapon_name, self.bonus_damage = random.choice(list(self.w.items()))
        
        self.equip_weapon(self.weapon_name, self.bonus_damage)

    def attack(self, target):
        super().attack(target)
        return f"{self.name} casts Fireball"

# --------------------------------- Equipment -------------------------------- #
class Weapon:
    warrior_weapons = {
        "Axe": 150,
        "Sword": 100,
        "Club": 80,
        "Dagger": 50
    }

    mage_weapons = {
        "Staff": 150,
        "Grimoire": 100,
        "Wand": 80,
        "Ring Of Magic": 50
    }

    def __init__(self, name, bonus_damage):
        self.name = name
        self.bonus_damage = bonus_damage
    
    def __str__(self):
        return f"{self.name} (+{self.bonus_damage} DMG)"
    
    def _repr__(self):
        return f"Weapon({self.name}, {self.bonus_damage})"

# ----------------------------------- Vault ---------------------------------- #
class Vault:
    def __init__(self):
        self.__gold_balance = 0

    def add_gold(self, amount):
        self.__gold_balance += amount
        print(f"{amount} Gold Added")
    
    def get_balance(self):
        return self.__gold_balance


# --------------------------- Game Rules & Utlities -------------------------- #

class GameConfig:
    VERSION = "1.0.0"

    """ NOTE TODO
    Change the 'create_training_dummy' method to create
    an active opponent, I know that's not what the instructions
    say but it makes it easier to creaate dummies that attack
    which we want because why not...
    """
    @classmethod
    def create_training_dummy(cls):
        dummy = Character("Training Dummy", health=50, max_health=50 )
        return dummy

    @staticmethod
    def validate_name(name=""):
        # I know I don't have to use not but still... I like True first
        if not (name == "" or name == " "):
            return True
        else:
            return False

# ---------------------------------------------------------------------------- #

def character_stats(ch):
    magnum.title("Character Stats", 1)
    print("Name: ", ch.name,
        "\nHealth:", f"{ch.health}/{ch.max_health} HP",
        "\nATK Power:", ch.base_attack)
    magnum.dash(12)

def start_duel(player, enemy):
    winner = ""
    def duel_progress(attacker, target):
        attacker.attack(target)
        if not target.is_alive():
            winner = attacker.name
            print(f"{attacker.name}({attacker.health} HP) is the winner and has slain {target.name}(0 HP)")
            return True

        return False

    first_attack = random.randint(1, 2)
    duelling = True

    character_stats(player)
    character_stats(enemy)

    if first_attack == 1:
        while (duelling):
            if duel_progress(player, enemy):
                break
            elif duel_progress(enemy, player):
                break
    elif first_attack == 2:
        while (duelling):
            if duel_progress(enemy, player):
                break
            elif duel_progress(player, enemy):
                break

    character_stats(player)
    character_stats(enemy)
    return winner

"""
player = Character("Jeff", 150, 150, 8)
mage1 = Mage(name="Finn")
           
start_duel(player, mage1)
"""

# ---------------------------------------------------------------------------- #
#                                   Game Flow                                  #
# ---------------------------------------------------------------------------- #

greeting = f"Welcome Traveler to..."
player_classes = [
    "Warrior",
    "Mage"
] 
print(greeting)
magnum.title(f"The Homestead Chronicles {GameConfig.VERSION}", 2)
name = input("Enter your name: ")

print("Please choose a class (enter the number only):")
for index, player_class in enumerate(player_classes, start=1):
    print(f"\t({index}) {player_class}")

chosen_class = int(input("Choice:"))

if (chosen_class == 1):
    print(f"A {player_classes[chosen_class-1]}!, great choice")
    player = Warrior(name=name)
    character_stats(player)
elif (chosen_class == 2):
    print(f"A {player_classes[chosen_class-1]}!, great choice")
    player = Mage(name=name)
    character_stats(player)
else:
    raise ValueError("Invalid Option")

print("Let's have you duel an Opponent as Practice")
enemy = Character(name="[Nameless Goblin]", health=20, max_health=20, base_attack=2)

""" NOTE
refer to GameConfig NOTE commment
dummy = GameConfig.create_training_dummy(base_attack=8)
"""

game_running = True
while(game_running):
    winner = start_duel(player, enemy)

    if winner == player.name:
        player.vault.add_gold(25)
        game_running = False
        break
    elif winner == enemy.name:
        print("Respectfully KYS bro 🙏")
        game_running = False
        break
    else:
        print("Something went wrong...")
