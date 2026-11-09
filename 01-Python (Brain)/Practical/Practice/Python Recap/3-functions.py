# 3.1 Defining & Calling
# Function Definition

def greet(name):
    return f"Hello, {name}!"

# Calling Function
print(greet("Alice"))

# 3.2 Lambda Functions
add = lambda x, y: x + y
print(add(2, 3))

# 3.3 Higher Order Functions
def shout(text):
    return text.upper()

def greet(func):
    return func("hello")

print(greet(shout))

# 3.4 *args & **kwargs
def print_args_kwargs(*args, **kwargs):
    print("Positional Arguments:", args)
    print("Keyword Arguments:", kwargs)

print_args_kwargs(1, 2, 3, name="Alice", age=30)
# print_args_kwargs(1, 2, 3, name="Alice", age=30, 3, 4, 5)