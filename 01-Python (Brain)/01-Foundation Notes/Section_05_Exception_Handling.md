## Section 5: Exception Handling

An exception is Python's way of signalling that something went wrong at runtime. Without handling exceptions, your program crashes and prints a traceback. With proper handling, you can gracefully respond to errors, clean up resources, and give meaningful messages instead.

### 5.1 `try` / `except`

Wrap code that might fail in a `try` block. If an exception is raised, execution jumps straight to the matching `except` block.

```Python
# Basic pattern
try:
    number = int(input("Enter a number: "))
    print(f"You entered: {number}")
except ValueError:
    print("That wasn't a valid number. Please try again.")

# Without exception handling, invalid input would crash with:
# ValueError: invalid literal for int() with base 10: 'abc'
```

Catching a specific exception and inspecting it:

```Python
try:
    result = 100 / 0
except ZeroDivisionError as e:
    print(f"Math error: {e}")
    # Output: Math error: division by zero
```

### 5.2 Catching Multiple Exception Types

You can catch different exceptions separately, or group several together in a tuple.

```Python
def load_save_file(filepath: str):
    try:
        with open(filepath, "r") as f:
            data = f.read()
        level = int(data.split(",")[0])
        return level
    except FileNotFoundError:
        print(f"Save file '{filepath}' not found. Starting fresh.")
        return 1
    except ValueError:
        print("Save data is corrupted. Could not parse level.")
        return 1
    except (PermissionError, OSError) as e:
        print(f"System error accessing file: {e}")
        return 1
    except Exception as e:
        # Broad catch-all — use sparingly, and only at the top level
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return 1
```

> [!NOTE]
> Always catch the **most specific** exceptions first. Python checks `except` blocks in order, top to bottom. If `except Exception` comes first, it catches everything, and your more specific handlers below it will never run.

### 5.3 Raising Exceptions

You can raise an exception deliberately with the `raise` keyword, to enforce rules and constraints in your own code.

```Python
def check_positive(value: int | float, name: str = "Value") -> None:
    """Raises ValueError if value is not positive."""
    if value < 0:
        raise ValueError(f"{name} must be a positive number. Got: {value}")

# Normal usage
check_positive(50, "Health")       # Passes silently

# This triggers the error
try:
    check_positive(-10, "Damage")
except ValueError as e:
    print(f"Caught: {e}")
    # Output: Caught: Damage must be a positive number. Got: -10

# Re-raising an exception (log it, then let it continue propagating)
try:
    result = int("corrupted_data")
except ValueError as e:
    print(f"[LOG] Conversion error: {e}")
    raise  # Re-raises the same ValueError up the call stack
```

### 5.4 Custom Exceptions

Custom exceptions let you create application-specific error types. They should inherit from `Exception` (or one of its subclasses).

```Python
# Define custom exceptions by inheriting from Exception
class GameError(Exception):
    """Base exception for all game-related errors."""
    pass

class InvalidChoiceError(GameError):
    """Raised when a player enters an option outside the valid range."""
    pass

class InsufficientGoldError(GameError):
    """Raised when a player tries to buy something they can't afford."""
    def __init__(self, required: int, available: int):
        self.required = required
        self.available = available
        super().__init__(f"Need {required} gold, but only have {available}.")


# Using custom exceptions
def purchase_item(item_cost: int, player_gold: int) -> None:
    if player_gold < item_cost:
        raise InsufficientGoldError(item_cost, player_gold)
    print("Purchase successful!")

try:
    purchase_item(500, 120)
except InsufficientGoldError as e:
    print(f"Transaction failed: {e}")
    # Output: Transaction failed: Need 500 gold, but only have 120.

# In your File I/O Practice (6B-File-IO-Practice.py), you used this pattern:
class CustomError(Exception):
    pass

def validate_menu_choice(choice: int, max_option: int) -> None:
    if choice < 1 or choice > max_option:
        raise CustomError(f"Please enter a number between 1 and {max_option}.")
```

### 5.5 `finally`

The `finally` block **always executes**, whether an exception was raised or not. Use it to guarantee cleanup code runs no matter what.

```Python
def read_config(filepath: str):
    file = None
    try:
        file = open(filepath, "r")
        return file.read()
    except FileNotFoundError:
        print("Config file missing. Using defaults.")
        return ""
    finally:
        # This runs whether the open succeeded or not
        if file:
            file.close()
        print("Config read attempt complete.")

# Even better: use 'with' (Section 6) and finally becomes unnecessary for files
```

The canonical `try/except/else/finally` structure:

```Python
try:
    result = 100 // int(input("Divisor: "))
except ValueError:
    print("Not a number.")
except ZeroDivisionError:
    print("Cannot divide by zero.")
else:
    # Runs ONLY if no exception was raised
    print(f"Result: {result}")
finally:
    # Runs ALWAYS — exception or not
    print("Operation complete.")
```

---

**Practice:**
1. Write a `try/except` block that safely converts user input to an `int`, catching `ValueError` and asking the user to try again.
2. Create a custom exception `OutOfManaError`, and raise it inside a function `cast_spell(current_mana, cost)` when `current_mana < cost`.
3. Write a `try/except/else/finally` block that divides two numbers, handles `ZeroDivisionError`, and prints `"Done"` in `finally` no matter what happens.

---
