loot_list  = ["Sword", "Shield", "Potion"]

# Convert iterable into iterator
loot_iterator = iter(loot_list)

print(next(loot_iterator))
print(next(loot_iterator))
print(next(loot_iterator))