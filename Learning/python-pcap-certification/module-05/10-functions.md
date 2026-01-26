# Module 5 Part 1: Functions - Complete Guide

## Table of Contents
1. [Introduction to Functions](#introduction-to-functions)
2. [Defining Functions](#defining-functions)
3. [Function Parameters](#function-parameters)
4. [Return Statement](#return-statement)
5. [Variable Scope](#variable-scope)
6. [Docstrings](#docstrings)
7. [Default Arguments](#default-arguments)
8. [Keyword Arguments](#keyword-arguments)
9. [Arbitrary Arguments](#arbitrary-arguments)
10. [Recursion](#recursion)

---

## Introduction to Functions

Functions are **reusable blocks of code** that perform specific tasks.

### Why Use Functions?

✅ **Code Reusability** - Write once, use many times  
✅ **Organization** - Break complex problems into smaller parts  
✅ **Maintainability** - Easier to update and debug  
✅ **Abstraction** - Hide implementation details  

```python
# Without function (repetitive)
print("=" * 40)
print("Welcome")
print("=" * 40)

print("=" * 40)
print("Goodbye")
print("=" * 40)

# With function (reusable)
def print_banner(message):
    print("=" * 40)
    print(message)
    print("=" * 40)

print_banner("Welcome")
print_banner("Goodbye")
```

---

## Defining Functions

### Basic Syntax

```python
def function_name(parameters):
    """Docstring"""
    # Function body
    return value
```

### Example 1: Simple Function

```python
def greet():
    print("Hello, World!")

# Call the function
greet()  # Output: Hello, World!
```

### Example 2: Function with Parameter

```python
def greet(name):
    print(f"Hello, {name}!")

greet("Alice")  # Hello, Alice!
greet("Bob")    # Hello, Bob!
```

### Example 3: Function with Return

```python
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # 8
```

---

## Function Parameters

### Positional Parameters

```python
def introduce(name, age, city):
    print(f"I'm {name}, {age} years old, from {city}")

introduce("Alice", 25, "NYC")
# I'm Alice, 25 years old, from NYC
```

### Multiple Parameters

```python
def calculate_area(length, width):
    return length * width

area = calculate_area(5, 3)
print(area)  # 15
```

---

## Return Statement

### Single Return Value

```python
def square(x):
    return x ** 2

result = square(5)
print(result)  # 25
```

### Multiple Return Values (Tuple)

```python
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers)

data = [1, 2, 3, 4, 5]
minimum, maximum, total = get_stats(data)
print(f"Min: {minimum}, Max: {maximum}, Total: {total}")
# Min: 1, Max: 5, Total: 15
```

### Early Return

```python
def is_even(n):
    if n % 2 == 0:
        return True
    return False

# More Pythonic
def is_even(n):
    return n % 2 == 0
```

### No Return (Returns None)

```python
def print_message(msg):
    print(msg)
    # No return statement

result = print_message("Hello")
print(result)  # None
```

---

## Variable Scope

### Local Scope

```python
def my_function():
    x = 10  # Local variable
    print(x)

my_function()  # 10
# print(x)  # NameError: x is not defined
```

### Global Scope

```python
x = 10  # Global variable

def my_function():
    print(x)  # Can read global

my_function()  # 10
```

### Global Keyword

```python
x = 10

def modify_global():
    global x
    x = 20  # Modify global variable

print(x)  # 10
modify_global()
print(x)  # 20
```

### Nonlocal Keyword (Nested Functions)

```python
def outer():
    x = 10
    
    def inner():
        nonlocal x
        x = 20  # Modify outer function's variable
    
    print(f"Before: {x}")  # 10
    inner()
    print(f"After: {x}")   # 20

outer()
```

### LEGB Rule (Scope Resolution)

**L**ocal → **E**nclosing → **G**lobal → **B**uilt-in

```python
x = "global"

def outer():
    x = "enclosing"
    
    def inner():
        x = "local"
        print(x)  # local
    
    inner()
    print(x)  # enclosing

outer()
print(x)  # global
```

---

## Docstrings

### Purpose

Document what a function does.

### Single-Line Docstring

```python
def greet(name):
    """Greet a person by name."""
    return f"Hello, {name}!"

# Access docstring
print(greet.__doc__)  # Greet a person by name.
```

### Multi-Line Docstring

```python
def calculate_bmi(weight, height):
    """
    Calculate Body Mass Index (BMI).
    
    Args:
        weight (float): Weight in kilograms
        height (float): Height in meters
    
    Returns:
        float: BMI value
    
    Example:
        >>> calculate_bmi(70, 1.75)
        22.86
    """
    return weight / (height ** 2)

print(calculate_bmi.__doc__)
```

### Help Function

```python
def add(a, b):
    """Add two numbers and return the result."""
    return a + b

help(add)
# Output shows function signature and docstring
```

---

## Default Arguments

### Basic Default Values

```python
def greet(name="Guest"):
    print(f"Hello, {name}!")

greet()          # Hello, Guest!
greet("Alice")   # Hello, Alice!
```

### Multiple Defaults

```python
def create_profile(name, age=18, city="Unknown"):
    print(f"{name}, {age}, {city}")

create_profile("Alice")                    # Alice, 18, Unknown
create_profile("Bob", 25)                  # Bob, 25, Unknown
create_profile("Charlie", 30, "NYC")       # Charlie, 30, NYC
```

### Default Must Be After Non-Default

```python
# Wrong
# def func(a=1, b):  # SyntaxError
#     pass

# Correct
def func(b, a=1):
    pass
```

### Mutable Default Pitfall

```python
# DANGEROUS - Mutable default
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - Unexpected!

# SAFE - Use None
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

print(add_item(1))  # [1]
print(add_item(2))  # [2] - Correct!
```

---

## Keyword Arguments

### Named Arguments

```python
def introduce(name, age, city):
    print(f"{name}, {age}, from {city}")

# Positional
introduce("Alice", 25, "NYC")

# Keyword arguments (order doesn't matter)
introduce(city="NYC", name="Alice", age=25)
introduce(age=25, city="NYC", name="Alice")
```

### Mixing Positional and Keyword

```python
def func(a, b, c):
    print(a, b, c)

func(1, 2, 3)           # Positional
func(1, c=3, b=2)       # Mixed
# func(a=1, 2, 3)       # SyntaxError: positional after keyword
```

---

## Arbitrary Arguments

### *args (Variable Positional Arguments)

```python
def sum_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3))        # 6
print(sum_all(1, 2, 3, 4, 5))  # 15
```

### **kwargs (Variable Keyword Arguments)

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="NYC")
# name: Alice
# age: 25
# city: NYC
```

### Combining All Types

```python
def complex_func(a, b, *args, key1="default", **kwargs):
    print(f"a: {a}, b: {b}")
    print(f"args: {args}")
    print(f"key1: {key1}")
    print(f"kwargs: {kwargs}")

complex_func(1, 2, 3, 4, 5, key1="value", x=10, y=20)
# a: 1, b: 2
# args: (3, 4, 5)
# key1: value
# kwargs: {'x': 10, 'y': 20}
```

---

## Recursion

### What is Recursion?

A function that calls itself.

### Example 1: Factorial

```python
def factorial(n):
    """Calculate factorial recursively."""
    if n == 0 or n == 1:  # Base case
        return 1
    return n * factorial(n - 1)  # Recursive call

print(factorial(5))  # 120 (5 * 4 * 3 * 2 * 1)
```

### Example 2: Fibonacci

```python
def fibonacci(n):
    """Return nth Fibonacci number."""
    if n <= 1:  # Base case
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(fibonacci(7))  # 13
# Sequence: 0, 1, 1, 2, 3, 5, 8, 13
```

### Example 3: Sum of List

```python
def sum_recursive(numbers):
    """Sum list recursively."""
    if not numbers:  # Base case
        return 0
    return numbers[0] + sum_recursive(numbers[1:])

print(sum_recursive([1, 2, 3, 4, 5]))  # 15
```

### Recursion vs Iteration

```python
# Recursive
def factorial_recursive(n):
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

# Iterative (often more efficient)
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

---

## Common Patterns

### 1. Validation Function

```python
def is_valid_email(email):
    """Check if email is valid."""
    return "@" in email and "." in email.split("@")[1]

print(is_valid_email("user@example.com"))  # True
print(is_valid_email("invalid"))            # False
```

### 2. Helper Functions

```python
def main():
    """Main program."""
    name = get_name()
    age = get_age()
    display_info(name, age)

def get_name():
    return input("Enter name: ")

def get_age():
    return int(input("Enter age: "))

def display_info(name, age):
    print(f"{name} is {age} years old")

if __name__ == "__main__":
    main()
```

### 3. Pure Functions (No Side Effects)

```python
# Pure function
def add(a, b):
    return a + b

# Impure function (modifies global state)
total = 0
def add_to_total(n):
    global total
    total += n
```

---

## Summary

| **Concept** | **Example** |
|-------------|-------------|
| Basic function | `def func(): pass` |
| With parameters | `def func(a, b): pass` |
| With return | `def func(x): return x * 2` |
| Default args | `def func(a=10): pass` |
| *args | `def func(*args): pass` |
| **kwargs | `def func(**kwargs): pass` |
| Recursion | `def fact(n): return 1 if n<=1 else n*fact(n-1)` |

### Key Concepts Checklist

✅ Function definition with `def`  
✅ Parameters and arguments  
✅ Return values (single and multiple)  
✅ Variable scope (LEGB rule)  
✅ Docstrings for documentation  
✅ Default, keyword, and arbitrary arguments  
✅ Recursion basics  

---

## Next Steps
➡️ **Module 5: Functions Practice Questions** (20 exam-style questions)  
➡️ **Module 5: Lambda and Functional Programming**
