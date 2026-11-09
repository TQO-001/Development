# 5.1 Try/Except
try:
    print(x)
except NameError:
    print("Variable x is not defined.")
except:
    print("Something else went wrong.")

num = -5
# 5.2 Raising Exceptions
def check_positive(y):
    if y < 0:
        raise ValueError("Negative value not allowed bitch.")

check_positive(num)

"""
# 5.3 Custom Exceptions
class CustomError(Exception):
    pass

try:
    print("Raising a custom error...")
    raise CustomError("This is a custom error message.")
except CustomError as e:
    print(f"Caught a custom error: {e}")


# 5.4 Many Exceptions
def greet(name):
    try:
        print(f"Hello, {name}!")
    except NameError:
        print("Variable [name] is not defined.")
    except:
        print("Something else Went Wrong.")

greet("Alice")

# 5.5 Finally
try:
    print(x)
except: 
    print("\nSomething went wrong.")
finally:
    print("The 'try except' is finished.")
"""