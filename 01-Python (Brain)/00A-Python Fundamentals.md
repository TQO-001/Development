## 1. Core Python Fundamentals (The Mechanics)

> [!TIP] ### Autism For Evil
>  **Goal: Master the "grammar" of the language in 1 day before moving to AI-specific logic.**

### **A1. Variables, Input & Output**
- **Variable:** Variables are containers for storing data values.
- **Output:** You can use the `print()` function to display text or output values
- **Input:** You can use the `input()` function but you have to store the input in a variable

``` python
# Variables
x = 5  
y = "John"  

# Output
print(x)  
print(y)

# Input
x = 69    # x is no longer 5, it is now 69

print(x)  # output: 69
```

### **A2. Data Types & Basic Operators**

- **Numerics:** Integers, Floats.    
- **Strings:** Formatting, Slicing, and Methods.    
- **Booleans:** Truthiness and comparison.    
- **Operators:** Arithmetic (`+`, `-`, `*`, `/`, `//`, `%`, ) and Logical (`and`, `or`, `not`).

``` python
# Numerics & Arithmetic
price = 19.99
quantity = 3
total = (price * quantity) // 1  # Floor division results in 59.0

# Strings & Formatting
name = "Gemini"
greeting = f"Hello, {name.upper()}!" # F-string with method

# Booleans & Logical Operators
is_valid = True
can_access = is_valid and (total > 50)
```

### **B. Data Structures**

- **Lists & Tuples:** Mastery of indexing, slicing, and understanding mutability vs. immutability.    
- **Dictionaries:** Key-value mapping for representing data objects and configurations.    
- **Sets:** Understanding uniqueness, membership testing, and set operations (union, intersection).

``` python
# Lists (Mutable)
layers = [64, 128, 256]
layers.append(512)

# Dictionaries (Mapping)
model_config = {"lr": 0.001, "batch_size": 32}

# Sets (Uniqueness)
tags = {"ai", "ml", "ai"} # Becomes {'ai', 'ml'}
```

### **C. Logic & Flow Control**

- **Conditional Statements:** `if`, `elif`, `else`.    
- **Loops:** Iterating over sequences with `for` and conditional repetition with `while`.

``` python
# Loops & Conditionals
for node in layers:
    if node > 200:
        print(f"Large layer detected: {node}")
    else:
        print("Standard layer.")
```

### **D. Functions & Modules**

- **Reusable Code:** Defining functions with `def`, positional/keyword arguments, and return values.    
- **Packaging:** Managing environments with `venv`, installing packages via `pip`, and using `import`.

``` python
def calculate_loss(y_true, y_pred):
    return (y_true - y_pred) ** 2

import numpy as np # Importing a module
```

### **E. File & API Handling**

- **File I/O:** Reading and writing `.csv`, `.json`, and `.txt` files using the `with` statement.    
- **APIs:** Using the `requests` library to interface with external services (OpenAI, Hugging Face).

``` python
# File I/O
import json
with open("config.json", "w") as f:
    json.dump(model_config, f)

# APIs
import requests
# response = requests.get("https://api.example.com/data")
```

