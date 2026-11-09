# Advanced Python Mechanics (The Systems Layer)

> [!TIP] ### The Shift in Thinking
> 
> Moving from basic to advanced Python means shifting your focus from _making the code work_ to making the code _scalable, memory-efficient, and easily maintainable_.

### **A. Advanced Python Techniques & Functional Programming**
- **Parameters vs. Arguments:** * _Parameters_ are the variables defined in the function signature.
    - _Arguments_ are the actual values passed when calling the function.
- **`*args` and `kwargs`:** Allow functions to accept an arbitrary number of positional (`*args`) or keyword (`kwargs`) arguments, packing them into tuples and dictionaries, respectively.

```Python
def build_profile(role, *skills, **metadata):
    # 'role' is a standard parameter. 'skills' is a tuple, 'metadata' is a dict.
    print(f"Role: {role}")
    print(f"Core Skills: {skills}")
    for key, value in metadata.items():
        print(f"{key.capitalize()}: {value}")

# Calling with arguments
build_profile("Backend Dev", "Python", "Docker", "AWS", location="KZN", active=True)
```

- **Comprehensions:** Elegant ways to construct lists, dictionaries, or sets in a single, highly readable line.
- **Lambda, Map, Filter, Reduce:** Anonymous functions (`lambda`) paired with higher-order functions for rapid data transformations.
- **Recursion:** Functions that call themselves, ideal for traversing trees or deeply nested data (like directory structures or JSON payloads).

```Python
from functools import reduce

# 1. List & Dict Comprehension
raw_scores = [45, 88, 92, 33, 76]
passed = [score for score in raw_scores if score > 50]
score_map = {f"Candidate_{i}": score for i, score in enumerate(raw_scores)}

# 2. Lambda, Map, Filter
# Double the scores of only those who passed
processed = list(map(lambda x: x * 2, filter(lambda x: x > 50, raw_scores)))

# 3. Reduce
# Aggregate a total sum from the processed list
total = reduce(lambda a, b: a + b, processed)

# 4. Recursion
def flatten_nested_list(nested_list):
    flat = []
    for item in nested_list:
        if isinstance(item, list):
            flat.extend(flatten_nested_list(item))
        else:
            flat.append(item)
    return flat
```

### **B. Advanced Regular Expressions (Regex)**

Regex is critical for parsing logs, cleaning user input, and validating data pipelines. The `re` module allows for complex pattern matching.

- **Lookarounds:** Asserting whether a pattern is preceded or followed by another pattern without including it in the match.
- **Backreferences:** Re-using a captured group later in the same regex.

```Python
import re

# Scenario 1: Check if a string starts and ends with the SAME character
# ^(.) captures the first char. .* matches anything. \1 looks for the exact captured char at the end $.
boundary_regex = r'^(.).*\1$'
print(bool(re.match(boundary_regex, "radar"))) # True
print(bool(re.match(boundary_regex, "python"))) # False

# Scenario 2: Advanced Password Validation
# Requirements: Minimum 8 chars, at least one uppercase, one lowercase, one digit, and one special char.
password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

def validate_password(pwd):
    if re.match(password_regex, pwd):
        return "Strong password"
    return "Weak password: Does not meet complexity requirements."
```

### **C. Object-Oriented Programming (OOP) Architecture**

OOP is essential for structuring large applications. It allows you to model real-world entities (like an AI job matching platform) with state and behavior.

- **Classes & Objects:** Blueprints and their instantiated entities.
- **Encapsulation:** Hiding internal states using private attributes (prefixing with `__`) and exposing them via getter/setter methods.
- **Inheritance:** Creating specialized child classes from a parent class to promote code reuse.
- **Polymorphism:** Allowing different classes to be treated as instances of the same class through a shared interface (method overriding).
- **Data Abstraction:** Hiding complex implementation details behind a simple interface (often using abstract base classes).

```Python
from abc import ABC, abstractmethod

# Abstraction: Defining a base template that must be adhered to
class Entity(ABC):
    @abstractmethod
    def display_info(self):
        pass

# Encapsulation & Class Definition
class User(Entity):
    def __init__(self, username, email):
        self.username = username
        self.__email = email # Private attribute
    
        def get_email(self):
        return self.__email

    def display_info(self):
        return f"User: {self.username}"

# Inheritance
class JobSeeker(User):
    def __init__(self, username, email, skills):
        super().__init__(username, email)
        self.skills = skills
    
        # Polymorphism: Overriding the parent method
    def display_info(self):
        return f"Candidate {self.username} specializing in {', '.join(self.skills)}"

# Usage
applicant = JobSeeker("Thulani", "t@example.com", ["Python", "AWS", "AI Agents"])
print(applicant.display_info())
# print(applicant.__email) # This would throw an AttributeError (Encapsulation)
```

### **D. Iterables, Iterators, and Generators**

For systems handling massive datasets, loading everything into memory is impossible. Lazy evaluation is the solution.

- **Iterables & Iterators:** An iterable (like a list) can be looped over. An iterator implements `__iter__()` and `__next__()`, fetching one item at a time.
- **Generators:** Functions that use `yield` instead of `return`. They pause execution, maintaining their state, and are highly memory-efficient.

```Python
# Generator for massive sequences
def infinite_id_generator(start=1000):
    current = start
    while True: # Safe because it only yields one at a time
        yield f"NAVY-ID-{current}"
        current += 1

id_gen = infinite_id_generator()
print(next(id_gen)) # NAVY-ID-1000
print(next(id_gen)) # NAVY-ID-1001
```

### **E. Closures, Decorators & Meta-Programming**

These tools allow you to modify or wrap functions dynamically without changing their core source code.

- **Closures:** A nested function that remembers the state of its enclosing scope even after the outer function has finished executing.
- **Decorators:** A syntax shortcut (`@`) for passing a function to another function to extend its behavior (e.g., logging, timing, authentication).
- **Monkey Patching:** Modifying a module, class, or function at runtime (useful for testing or hot-fixing, but should be used sparingly).

```Python
import time

# Decorator utilizing *args and **kwargs to support any function signature
def performance_tracker(func):
    def wrapper(*args, **kwargs): # Closure
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"[DEBUG] {func.__name__} executed in {end_time - start_time:.6f}s")
        return result
    return wrapper

@performance_tracker
def complex_computation(n):
    return sum(i * i for i in range(n))

complex_computation(100000)

# Monkey Patching Example
import math
def fake_sqrt(x):
    return "Patched!"
math.sqrt = fake_sqrt # Overriding standard library behavior at runtime
```

### **F. Memory Management & Optimization**

Understanding how Python handles memory prevents memory leaks and performance bottlenecks.

- **Garbage Collection & Reference Counting:** Python automatically frees memory when an object's reference count drops to zero. Cyclic references are handled by the generational garbage collector.
- **Dynamic Typing:** Variables are pointers to objects in memory; their types are evaluated at runtime.
- **Mutable vs. Immutable:** Strings, tuples, and integers are immutable (creating a new object when changed). Lists and dicts are mutable (changed in place).
- **Shallow vs. Deep Copy:** A shallow copy creates a new collection but references the same child objects. A deep copy recursively duplicates everything.
- **Optimization Tips:** Use generators instead of lists for large data, use `join()` instead of `+` for strings, and utilize built-in C-optimized functions (like `map` or `sum`).

```Python
import copy
import sys

# Memory Profiling Concept
x = [1, 2, 3]
print(f"Size of list: {sys.getsizeof(x)} bytes")

# Deep vs Shallow Copy
original_pipeline = [["Extract", "Transform"], "Load"]
shallow_copy = copy.copy(original_pipeline)
deep_copy = copy.deepcopy(original_pipeline)

original_pipeline[0][0] = "MODIFIED"

print(shallow_copy[0][0]) # Outputs: MODIFIED (Shared reference)
print(deep_copy[0][0])    # Outputs: Extract (Completely independent)
```

### **G. Testing & Quality Assurance (Pytest)**

Testing validates that your advanced logic holds up under edge cases. `pytest` is the industry standard. This example demonstrates how to test the complex concepts covered above.
```Python
# test_advanced_logic.py
import pytest

# 1. Testing a recursive function
def factorial(n):
    if n == 0: return 1
    return n * factorial(n - 1)

def test_recursion():
    assert factorial(5) == 120
    assert factorial(0) == 1

# 2. Testing with Parameters (pytest.mark.parametrize)
@pytest.mark.parametrize("inputs, expected", [
    ((2, 3), 5),
    ((10, -5, 2), 7),
    ((), 0)
])
def test_args_sum(inputs, expected):
    # Testing a lambda that takes *args
    sum_lambda = lambda *args: sum(args)
    assert sum_lambda(*inputs) == expected

# 3. Testing a Generator
def test_generator():
    def simple_gen():
        yield 1
        yield 2

    gen = simple_gen()
    assert next(gen) == 1
    assert next(gen) == 2
    with pytest.raises(StopIteration):
        next(gen)
```