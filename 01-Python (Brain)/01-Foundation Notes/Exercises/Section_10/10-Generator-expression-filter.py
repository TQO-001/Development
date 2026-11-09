"""NOTE - We use () so that it remains a generator expression,
    generating a value everytime we call next().
        - If we used [] then it would be a list compression and would
    immediately generate a list with the results
"""
even_test = (f"{x}: {x**2}" for x in range(1, 51) if x % 2 == 0)
even = (x**2 for x in range(1, 51) if x % 2 == 0)

manual1 = next(even)
manual2 = next(even)

print(manual1)
print(manual2)

even_list = [manual1, manual2, *even]

print(even_list)