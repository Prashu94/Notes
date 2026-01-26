# Module 6 Part 1: Modules - Complete Guide

## Table of Contents
1. [Introduction to Modules](#introduction-to-modules)
2. [Importing Modules](#importing-modules)
3. [Creating Modules](#creating-modules)
4. [Module Search Path](#module-search-path)
5. [__name__ Variable](#__name__-variable)
6. [dir() Function](#dir-function)
7. [Built-in Modules](#built-in-modules)
8. [Module Best Practices](#module-best-practices)

---

## Introduction to Modules

### What is a Module?

A **file containing Python code** (functions, classes, variables) that can be imported and reused.

### Why Use Modules?

✅ **Code Organization** - Split large programs into manageable files  
✅ **Reusability** - Use code across multiple programs  
✅ **Namespace Management** - Avoid naming conflicts  
✅ **Maintainability** - Easier to update and debug  

```python
# Without modules - everything in one file
def function1():
    pass

def function2():
    pass

# ... 1000 more functions

# With modules - organized into separate files
import math_utils
import string_utils
import database_utils
```

---

## Importing Modules

### Method 1: import module_name

```python
# Import entire module
import math

print(math.pi)        # 3.141592653589793
print(math.sqrt(16))  # 4.0
```

### Method 2: from module import name

```python
# Import specific items
from math import pi, sqrt

print(pi)        # 3.141592653589793
print(sqrt(16))  # 4.0
```

### Method 3: from module import *

```python
# Import everything (NOT RECOMMENDED)
from math import *

print(pi)    # Works
print(sqrt(16))  # Works
# But pollutes namespace!
```

### Method 4: import with alias

```python
# Shorter alias
import math as m

print(m.pi)  # 3.141592653589793

# Common in data science
import numpy as np
import pandas as pd
```

### Method 5: from module import name as alias

```python
from math import sqrt as square_root

print(square_root(16))  # 4.0
```

---

## Creating Modules

### Example 1: Simple Module

Create `mymodule.py`:
```python
# mymodule.py

def greet(name):
    """Greet a person."""
    return f"Hello, {name}!"

def add(a, b):
    """Add two numbers."""
    return a + b

PI = 3.14159
```

Use the module:
```python
# main.py
import mymodule

print(mymodule.greet("Alice"))  # Hello, Alice!
print(mymodule.add(5, 3))       # 8
print(mymodule.PI)              # 3.14159
```

### Example 2: Math Utilities Module

Create `math_utils.py`:
```python
# math_utils.py

def factorial(n):
    """Calculate factorial."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def is_prime(n):
    """Check if number is prime."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def fibonacci(n):
    """Generate Fibonacci sequence."""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result
```

Use it:
```python
import math_utils

print(math_utils.factorial(5))     # 120
print(math_utils.is_prime(17))     # True
print(math_utils.fibonacci(10))    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

---

## Module Search Path

### Where Python Looks for Modules

1. **Current directory**
2. **PYTHONPATH** environment variable
3. **Standard library directories**
4. **Site-packages** (third-party packages)

### View Search Path

```python
import sys

for path in sys.path:
    print(path)
```

### Add to Search Path

```python
import sys

# Add custom directory
sys.path.append('/path/to/my/modules')

# Now you can import from that directory
import mymodule
```

---

## __name__ Variable

### Purpose

Special variable that indicates **how the module was executed**.

### Values

- `"__main__"` - if script is run directly
- `module_name` - if script is imported

### Example

Create `mymodule.py`:
```python
# mymodule.py

def greet(name):
    return f"Hello, {name}!"

# This only runs when script is executed directly
if __name__ == "__main__":
    print("Running mymodule directly")
    print(greet("World"))
```

Run directly:
```bash
$ python mymodule.py
Running mymodule directly
Hello, World!
```

Import it:
```python
import mymodule

# The if __name__ == "__main__" block does NOT run
print(mymodule.greet("Alice"))  # Hello, Alice!
```

### Common Pattern

```python
# calculator.py

def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def main():
    """Run tests when script is executed directly."""
    print("Testing calculator...")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")

if __name__ == "__main__":
    main()
```

---

## dir() Function

### Purpose

List all names (functions, variables, classes) in a module.

### Example 1: Built-in Module

```python
import math

print(dir(math))
# ['__doc__', '__loader__', '__name__', ..., 'pi', 'pow', 'sqrt', ...]
```

### Example 2: Custom Module

```python
# mymodule.py
PI = 3.14159

def area(radius):
    return PI * radius ** 2

def circumference(radius):
    return 2 * PI * radius
```

```python
import mymodule

print(dir(mymodule))
# ['PI', '__builtins__', '__cached__', '__doc__', '__file__', 
#  '__loader__', '__name__', '__package__', '__spec__', 'area', 'circumference']
```

### Filter Out Special Names

```python
import math

public_names = [name for name in dir(math) if not name.startswith('_')]
print(public_names)
# ['acos', 'acosh', 'asin', ..., 'sqrt', 'tan', 'tanh', 'tau', 'trunc']
```

---

## Built-in Modules

### math Module

```python
import math

# Constants
print(math.pi)      # 3.141592653589793
print(math.e)       # 2.718281828459045

# Functions
print(math.sqrt(16))       # 4.0
print(math.ceil(4.3))      # 5
print(math.floor(4.7))     # 4
print(math.pow(2, 3))      # 8.0
print(math.factorial(5))   # 120
```

### random Module

```python
import random

# Random float [0.0, 1.0)
print(random.random())

# Random integer
print(random.randint(1, 10))  # 1 to 10 inclusive

# Random choice
fruits = ["apple", "banana", "cherry"]
print(random.choice(fruits))

# Shuffle list
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)
```

### datetime Module

```python
from datetime import datetime, date, timedelta

# Current date and time
now = datetime.now()
print(now)  # 2024-01-15 14:30:45.123456

# Current date
today = date.today()
print(today)  # 2024-01-15

# Date arithmetic
tomorrow = today + timedelta(days=1)
next_week = today + timedelta(weeks=1)
```

### sys Module

```python
import sys

# Python version
print(sys.version)

# Command-line arguments
print(sys.argv)

# Exit program
# sys.exit()

# Platform
print(sys.platform)  # 'win32', 'linux', 'darwin'
```

### os Module

```python
import os

# Current working directory
print(os.getcwd())

# List directory contents
print(os.listdir('.'))

# Check if file/directory exists
print(os.path.exists('file.txt'))

# Join paths (platform-independent)
path = os.path.join('folder', 'subfolder', 'file.txt')
print(path)
```

---

## Module Best Practices

### 1. One Module Per File

```python
# Good - clear purpose
# string_utils.py - string manipulation functions
# math_utils.py - mathematical functions
# db_utils.py - database functions

# Bad - mixed functionality
# utils.py - everything mixed together
```

### 2. Descriptive Names

```python
# Good
import user_authentication
import email_sender
import database_connection

# Bad
import utils
import stuff
import helper
```

### 3. Avoid Circular Imports

```python
# module_a.py
import module_b  # BAD if module_b imports module_a

# Solution: restructure code or use imports inside functions
```

### 4. Use if __name__ == "__main__"

```python
# mymodule.py

def useful_function():
    return "result"

# Module can be imported AND run as script
if __name__ == "__main__":
    # Test code here
    print(useful_function())
```

### 5. Document Modules

```python
# mymodule.py

"""
This module provides utility functions for data processing.

Functions:
    clean_data(data): Clean and preprocess data
    validate_data(data): Validate data format
    export_data(data, filename): Export data to file
"""

def clean_data(data):
    """Clean and preprocess data."""
    pass
```

---

## Summary

| **Import Style** | **Usage** | **Namespace** |
|------------------|-----------|---------------|
| `import module` | `module.function()` | Clean |
| `from module import name` | `name()` | Selective |
| `from module import *` | `name()` | Polluted (avoid) |
| `import module as alias` | `alias.function()` | Clean, shorter |

### Key Concepts Checklist

✅ Importing modules (import, from...import)  
✅ Creating custom modules  
✅ Module search path (sys.path)  
✅ __name__ == "__main__" pattern  
✅ dir() function  
✅ Common built-in modules (math, random, datetime, sys, os)  
✅ Module best practices  

---

## Next Steps
➡️ **Module 6: Modules Practice Questions** (20 exam-style questions)  
➡️ **Module 6: Packages**
