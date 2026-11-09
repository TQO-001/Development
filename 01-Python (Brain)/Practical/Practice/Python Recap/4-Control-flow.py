# 4.1 Conditionals
age = int(input("Enter your age: "))

if age >= 18:
    status = "Adult"
elif age > 12:
    status = "Teenager"
else:
    status = "Child"

print(f"You are a {status}.")

# 4.2 Ternary Operator
can_vote = "yes" if age >= 8 else "no"
print(f"Can you vote? {can_vote}")

# 4.3 For Loops
for item in [1, 2, 3]:
    print(item)

# 4.4 While Loops
count = 0
while count < 5:
    print(count)
    count += 1
    
    if count == 3:
        break

