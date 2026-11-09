dash = lambda num=8, char="-": print(char * 4 * num)

def cast_spell(spell_name, mana_cost=10):
    print(f"Casting {spell_name} (-{mana_cost}MP)")

cast_spell("Fireball")
cast_spell("Mega Fireball", mana_cost=100)

party = [
    {"name": "Arthur", "level": 15},
    {"name": "Merlin", "level": 22},
    {"name": "Lancelot", "level": 18}
]

party.sort(key=lambda member: member["level"])

for member in party:
    dash()
    for key, value in member.items():
        print(f"{key.capitalize()}: {value.capitalize()}")