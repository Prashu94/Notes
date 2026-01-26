# Module 1: Python Basics and Interpreter

## Table of Contents
1. [Introduction to Python](#introduction-to-python)
2. [Installing Python](#installing-python)
3. [Python Interpreter](#python-interpreter)
4. [Interactive Mode](#interactive-mode)
5. [Python Scripts](#python-scripts)
6. [Source Code Encoding](#source-code-encoding)
7. [Comments](#comments)
8. [Basic Syntax Rules](#basic-syntax-rules)
9. [Variables and Assignment](#variables-and-assignment)
10. [Input and Output](#input-and-output)

---

## 1. Introduction to Python

### What is Python?
Python is a **high-level, interpreted, object-oriented programming language** with:
- **Dynamic typing**: No need to declare variable types
- **Automatic memory management**: Garbage collection
- **Rich standard library**: "Batteries included" philosophy
- **Multi-paradigm**: Supports procedural, OOP, and functional programming

### Why Python?
- **Easy to learn**: Simple, readable syntax
- **Versatile**: Web development, data science, automation, AI/ML
- **Large community**: Extensive libraries and frameworks
- **Cross-platform**: Runs on Windows, macOS, Linux

### Python Versions
- **Python 2.x**: Legacy (end of life January 2020)
- **Python 3.x**: Current version (3.8+)
- **PCAP focuses on Python 3.x**

---

## 2. Installing Python

### Download and Installation
```bash
# Check if Python is installed
python --version
# or
python3 --version

# Install on macOS (using Homebrew)
brew install python3

# Install on Ubuntu/Debian
sudo apt-get install python3

# Install on Windows
# Download from https://www.python.org/downloads/
```

### Python PATH
Ensure Python is in your system PATH to run from any directory.

```bash
# Windows
set PATH=%PATH%;C:\Python311

# macOS/Linux
export PATH="/usr/local/bin/python3:$PATH"
```

---

## 3. Python Interpreter

### What is an Interpreter?
The Python interpreter **executes Python code line by line** (unlike compiled languages).

### Invoking the Interpreter
```bash
# Start interactive Python shell
python
# or
python3

# Run a Python script
python script.py
python3 script.py

# Execute code directly
python -c "print('Hello, World!')"

# Run module as script
python -m module_name
```

### Interpreter Options
```bash
# Display version
python --version

# Display help
python --help

# Run in interactive mode after script
python -i script.py

# Unbuffered output (useful for logging)
python -u script.py

# Optimize bytecode
python -O script.py

# Verbose mode
python -v script.py
```

---

## 4. Interactive Mode

### Python REPL (Read-Eval-Print Loop)
```python
>>> 2 + 2
4
>>> name = "Python"
>>> print(f"Hello, {name}!")
Hello, Python!
>>> import sys
>>> sys.version
'3.11.4 (main, ...'
```

### Primary Prompt (`>>>`) and Secondary Prompt (`...`)
```python
>>> # Primary prompt
>>> if True:
...     print("True")  # Secondary prompt
... 
True
```

### Special Variables in Interactive Mode
```python
>>> 5 + 3
8
>>> _  # Last result
8
>>> _ * 2
16
```

### Exiting Interactive Mode
```python
>>> exit()
# or
>>> quit()
# or press Ctrl+D (Unix) or Ctrl+Z (Windows)
```

---

## 5. Python Scripts

### Creating a Python File
```python
# hello.py
print("Hello, World!")
```

### Running a Script
```bash
python hello.py
```

### Shebang Line (Unix-like systems)
```python
#!/usr/bin/env python3
print("This script can be executed directly")
```

```bash
# Make executable
chmod +x hello.py

# Run directly
./hello.py
```

### Script Arguments
```python
# args.py
import sys

print("Script name:", sys.argv[0])
print("Arguments:", sys.argv[1:])
```

```bash
python args.py arg1 arg2 arg3
# Output:
# Script name: args.py
# Arguments: ['arg1', 'arg2', 'arg3']
```

---

## 6. Source Code Encoding

### Default Encoding
Python 3 uses **UTF-8** by default.

### Specifying Encoding
```python
# -*- coding: utf-8 -*-
# This is the default, but can be specified

# For other encodings:
# -*- coding: latin-1 -*-
```

### Unicode Support
```python
# UTF-8 allows Unicode characters
name = "Pythön"
emoji = "🐍"
chinese = "蟒蛇"
print(name, emoji, chinese)
```

---

## 7. Comments

### Single-Line Comments
```python
# This is a comment
x = 5  # This is an inline comment
```

### Multi-Line Comments
```python
"""
This is a multi-line comment
or docstring if used in specific places
"""

'''
You can also use single quotes
for multi-line comments
'''
```

### Docstrings (Documentation Strings)
```python
def greet(name):
    """
    Greet a person by name.
    
    Args:
        name (str): The name of the person
    
    Returns:
        str: A greeting message
    """
    return f"Hello, {name}!"

# Access docstring
print(greet.__doc__)
```

---

## 8. Basic Syntax Rules

### Indentation
**Python uses indentation to define code blocks** (not braces like C/Java).

```python
# Correct
if True:
    print("Indented")
    print("Same block")

# Incorrect - IndentationError
if True:
print("Not indented")
```

**Standard: 4 spaces per indentation level**

### Line Continuation
```python
# Implicit (inside brackets)
numbers = [1, 2, 3,
           4, 5, 6]

# Explicit (backslash)
total = 1 + 2 + 3 + \
        4 + 5 + 6

# String continuation
message = ("This is a long "
           "string spread across "
           "multiple lines")
```

### Multiple Statements on One Line
```python
# Semicolon separator (not recommended)
x = 5; y = 10; z = 15

# Better style - separate lines
x = 5
y = 10
z = 15
```

### Blank Lines
```python
# Two blank lines before top-level functions/classes
def function1():
    pass


def function2():
    pass
```

---

## 9. Variables and Assignment

### Variable Naming Rules
1. **Must start** with letter (a-z, A-Z) or underscore (_)
2. **Can contain** letters, digits (0-9), underscores
3. **Case-sensitive**: `name`, `Name`, `NAME` are different
4. **Cannot use** Python keywords

```python
# Valid names
name = "Alice"
age_1 = 25
_private = True
CamelCase = "value"

# Invalid names
# 1name = "Error"      # Starts with digit
# first-name = "Error" # Contains hyphen
# class = "Error"      # Keyword
```

### Python Keywords (Reserved Words)
```python
import keyword
print(keyword.kwlist)

# Output: ['False', 'None', 'True', 'and', 'as', 'assert', 
#          'async', 'await', 'break', 'class', 'continue', 
#          'def', 'del', 'elif', 'else', 'except', 'finally', 
#          'for', 'from', 'global', 'if', 'import', 'in', 
#          'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 
#          'raise', 'return', 'try', 'while', 'with', 'yield']
```

### Naming Conventions (PEP 8)
```python
# Variables and functions: lowercase with underscores
first_name = "John"
def calculate_total():
    pass

# Constants: UPPERCASE with underscores
MAX_SIZE = 100
PI = 3.14159

# Classes: CamelCase
class MyClass:
    pass

# Private: leading underscore
_internal_var = 42

# Special methods: double underscores
def __init__(self):
    pass
```

### Dynamic Typing
```python
# Variable can change type
x = 5        # int
print(type(x))  # <class 'int'>

x = "Hello"  # str
print(type(x))  # <class 'str'>

x = [1, 2, 3]  # list
print(type(x))  # <class 'list'>
```

### Multiple Assignment
```python
# Multiple variables, one value
x = y = z = 0

# Multiple variables, multiple values
a, b, c = 1, 2, 3

# Swapping
x, y = 10, 20
x, y = y, x  # Now x=20, y=10

# Unpacking
numbers = [1, 2, 3]
a, b, c = numbers
```

### Assignment Operators
```python
# Basic assignment
x = 10

# Augmented assignment
x += 5   # x = x + 5
x -= 3   # x = x - 3
x *= 2   # x = x * 2
x /= 4   # x = x / 4
x //= 2  # x = x // 2 (floor division)
x %= 3   # x = x % 3
x **= 2  # x = x ** 2 (exponentiation)
```

---

## 10. Input and Output

### Output with `print()`
```python
# Basic print
print("Hello, World!")

# Multiple arguments (separated by space)
print("Python", "is", "awesome")
# Output: Python is awesome

# Custom separator
print("a", "b", "c", sep="-")
# Output: a-b-c

# Custom end character (default is \n)
print("Line 1", end=" | ")
print("Line 2")
# Output: Line 1 | Line 2

# Print to file
with open("output.txt", "w") as f:
    print("Hello", file=f)
```

### String Formatting
```python
name = "Alice"
age = 30

# f-strings (Python 3.6+) - RECOMMENDED
print(f"Name: {name}, Age: {age}")

# format() method
print("Name: {}, Age: {}".format(name, age))
print("Name: {n}, Age: {a}".format(n=name, a=age))

# % operator (old style)
print("Name: %s, Age: %d" % (name, age))

# Formatting numbers
pi = 3.14159
print(f"Pi: {pi:.2f}")     # Pi: 3.14
print(f"Pi: {pi:.4f}")     # Pi: 3.1416
```

### Input with `input()`
```python
# Basic input (returns string)
name = input("Enter your name: ")
print(f"Hello, {name}!")

# Converting input
age = int(input("Enter your age: "))
height = float(input("Enter your height in meters: "))

# Multiple inputs on one line
x, y = input("Enter two numbers: ").split()
x = int(x)
y = int(y)

# Or more concisely
x, y = map(int, input("Enter two numbers: ").split())
```

### Handling Input Errors
```python
try:
    age = int(input("Enter your age: "))
    print(f"You are {age} years old")
except ValueError:
    print("Invalid input! Please enter a number.")
```

---

## Important Concepts for PCAP Exam

### 1. Literal Types
```python
# Integer literals
decimal = 100
binary = 0b1100100      # Binary
octal = 0o144           # Octal
hexadecimal = 0x64      # Hexadecimal

# Float literals
float1 = 3.14
float2 = 3.14e2  # Scientific notation: 314.0

# String literals
string1 = 'Single quotes'
string2 = "Double quotes"
string3 = '''Triple
quotes'''

# Boolean literals
bool1 = True
bool2 = False

# None literal
nothing = None
```

### 2. Type Conversion
```python
# Explicit conversion
int("123")      # 123
float("3.14")   # 3.14
str(100)        # "100"
bool(1)         # True
bool(0)         # False

# Implicit conversion
x = 5 + 2.0     # 7.0 (int + float = float)
```

### 3. Operators Precedence (Highest to Lowest)
```python
1. ()                    # Parentheses
2. **                    # Exponentiation
3. +x, -x, ~x           # Unary plus, minus, bitwise NOT
4. *, /, //, %          # Multiplication, Division, Floor division, Modulo
5. +, -                  # Addition, Subtraction
6. <<, >>               # Bitwise shifts
7. &                     # Bitwise AND
8. ^                     # Bitwise XOR
9. |                     # Bitwise OR
10. ==, !=, <, <=, >, >=, is, is not, in, not in  # Comparisons
11. not                  # Boolean NOT
12. and                  # Boolean AND
13. or                   # Boolean OR
```

---

## Practice Examples

### Example 1: Hello World Variations
```python
# Simple
print("Hello, World!")

# With user input
name = input("Enter your name: ")
print(f"Hello, {name}!")

# Formatted
print("=" * 40)
print("Welcome to Python PCAP Preparation")
print("=" * 40)
```

### Example 2: Calculator
```python
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

print(f"Addition: {num1 + num2}")
print(f"Subtraction: {num1 - num2}")
print(f"Multiplication: {num1 * num2}")
print(f"Division: {num1 / num2}")
print(f"Floor Division: {num1 // num2}")
print(f"Modulo: {num1 % num2}")
print(f"Exponentiation: {num1 ** num2}")
```

### Example 3: Temperature Converter
```python
celsius = float(input("Enter temperature in Celsius: "))
fahrenheit = (celsius * 9/5) + 32
kelvin = celsius + 273.15

print(f"{celsius}°C = {fahrenheit}°F = {kelvin}K")
```

---

## Key Takeaways for PCAP Exam

1. ✅ Python is **interpreted**, **dynamically typed**, and uses **indentation**
2. ✅ Use `print()` for output, `input()` for input (returns string)
3. ✅ Variables don't need type declaration
4. ✅ Comments use `#` (single-line) or `"""..."""` (multi-line)
5. ✅ Indentation is **4 spaces** (not tabs)
6. ✅ Variable names: start with letter/underscore, no keywords
7. ✅ f-strings are the modern way to format strings
8. ✅ `type()` function returns the type of an object
9. ✅ Always convert `input()` to appropriate type (int, float, etc.)
10. ✅ Understand operator precedence

---

## Common Pitfalls

### ❌ Indentation Errors
```python
# Wrong
if True:
print("Error")  # IndentationError

# Correct
if True:
    print("Success")
```

### ❌ Undefined Variables
```python
# Wrong
print(name)  # NameError: name 'name' is not defined

# Correct
name = "Alice"
print(name)
```

### ❌ Type Errors
```python
# Wrong
age = input("Enter age: ")
next_year = age + 1  # TypeError: can't add str and int

# Correct
age = int(input("Enter age: "))
next_year = age + 1
```

---

## Next Steps
After mastering this module, proceed to:
- **Module 2: Data Types and Operations** - Deep dive into numbers, strings, and operators

---

**Practice thoroughly before moving to the next module!**
