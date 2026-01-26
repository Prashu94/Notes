# Module 3: Control Flow - Conditional Statements

## Table of Contents
1. [Boolean Logic Review](#boolean-logic-review)
2. [if Statement](#if-statement)
3. [if-else Statement](#if-else-statement)
4. [if-elif-else Statement](#if-elif-else-statement)
5. [Nested Conditionals](#nested-conditionals)
6. [Ternary Operator](#ternary-operator)
7. [match Statement (Python 3.10+)](#match-statement)
8. [Common Patterns](#common-patterns)

---

## 1. Boolean Logic Review

### Comparison Operators
```python
x = 10
y = 5

x == y    # Equal to: False
x != y    # Not equal: True
x > y     # Greater than: True
x < y     # Less than: False
x >= y    # Greater or equal: True
x <= y    # Less or equal: False
```

### Logical Operators
```python
# AND - both must be True
True and True     # True
True and False    # False

# OR - at least one True
True or False     # True
False or False    # False

# NOT - inverts
not True          # False
not False         # True
```

### Truthiness
```python
# Falsy values
bool(0), bool(0.0), bool(""), bool([]), bool({}), bool(None)  # All False

# Truthy values
bool(1), bool(-1), bool("text"), bool([1]), bool(" ")  # All True
```

---

## 2. if Statement

### Basic Syntax
```python
if condition:
    # Code block executes if condition is True
    statement1
    statement2
```

### Examples
```python
# Simple if
age = 18
if age >= 18:
    print("You are an adult")

# With truthy/falsy
name = "Alice"
if name:
    print(f"Hello, {name}")

# Multiple conditions
score = 85
if score >= 90:
    print("Grade: A")
    
# Compound conditions
age = 25
has_license = True
if age >= 18 and has_license:
    print("Can drive")
```

---

## 3. if-else Statement

### Syntax
```python
if condition:
    # True block
    statement1
else:
    # False block
    statement2
```

### Examples
```python
# Basic if-else
number = 7
if number % 2 == 0:
    print("Even")
else:
    print("Odd")

# With input
password = input("Enter password: ")
if password == "secret123":
    print("Access granted")
else:
    print("Access denied")

# Comparison
x, y = 10, 20
if x > y:
    print("x is greater")
else:
    print("y is greater or equal")
```

---

## 4. if-elif-else Statement

### Syntax
```python
if condition1:
    # Block 1
elif condition2:
    # Block 2
elif condition3:
    # Block 3
else:
    # Default block
```

### Examples
```python
# Grade calculator
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"
    
print(f"Grade: {grade}")

# Temperature checker
temp = 25

if temp > 30:
    print("Hot")
elif temp > 20:
    print("Warm")
elif temp > 10:
    print("Cool")
else:
    print("Cold")

# Multiple conditions
age = 16
has_permit = True

if age >= 18:
    print("Can drive alone")
elif age >= 16 and has_permit:
    print("Can drive with adult")
elif age >= 15:
    print("Can get learner's permit")
else:
    print("Too young to drive")
```

### Important: Order Matters!
```python
# WRONG - will never reach last condition
score = 95
if score >= 60:
    print("Pass")  # This executes
elif score >= 90:
    print("Excellent")  # Never reached!

# CORRECT - most specific first
if score >= 90:
    print("Excellent")  # This executes
elif score >= 60:
    print("Pass")
```

---

## 5. Nested Conditionals

### Syntax
```python
if condition1:
    if condition2:
        # Both True
    else:
        # Only condition1 True
else:
    # condition1 False
```

### Examples
```python
# Login system
username = "admin"
password = "pass123"

if username == "admin":
    if password == "pass123":
        print("Login successful")
    else:
        print("Wrong password")
else:
    print("User not found")

# Age and income check
age = 25
income = 50000

if age >= 18:
    if income >= 30000:
        print("Loan approved")
    else:
        print("Insufficient income")
else:
    print("Must be 18 or older")

# Better with logical operators
if age >= 18 and income >= 30000:
    print("Loan approved")
elif age >= 18:
    print("Insufficient income")
else:
    print("Must be 18 or older")
```

---

## 6. Ternary Operator

### Syntax
```python
value_if_true if condition else value_if_false
```

### Examples
```python
# Basic ternary
age = 20
status = "Adult" if age >= 18 else "Minor"

# Comparison
x, y = 10, 20
max_value = x if x > y else y

# With functions
def get_message(score):
    return "Pass" if score >= 60 else "Fail"

# Nested ternary (not recommended - hard to read)
score = 85
grade = "A" if score >= 90 else "B" if score >= 80 else "C"

# Better as if-elif-else
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
```

### When to Use
```python
# Good use cases
# 1. Simple value assignment
is_even = True if num % 2 == 0 else False

# 2. Default values
name = user_input if user_input else "Guest"

# 3. Simple returns
def absolute(x):
    return x if x >= 0 else -x

# Bad use cases (use regular if)
# 1. Multiple statements
# 2. Complex conditions
# 3. Nested ternary
```

---

## 7. match Statement (Python 3.10+)

### Basic Syntax
```python
match value:
    case pattern1:
        # Code for pattern1
    case pattern2:
        # Code for pattern2
    case _:
        # Default case
```

### Examples
```python
# HTTP status codes
def http_error(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:
            return "Unknown"

# Multiple values
command = "quit"
match command:
    case "quit" | "exit" | "q":
        print("Exiting...")
    case "help" | "h":
        print("Help menu")
    case _:
        print("Unknown command")

# Pattern matching with conditions
point = (0, 5)
match point:
    case (0, 0):
        print("Origin")
    case (0, y):
        print(f"On Y-axis at {y}")
    case (x, 0):
        print(f"On X-axis at {x}")
    case (x, y):
        print(f"Point at ({x}, {y})")

# With guard clauses
def categorize_age(age):
    match age:
        case n if n < 0:
            return "Invalid"
        case n if n < 13:
            return "Child"
        case n if n < 20:
            return "Teenager"
        case n if n < 60:
            return "Adult"
        case _:
            return "Senior"
```

---

## 8. Common Patterns

### Pattern 1: Range Checking
```python
score = 85

# Method 1: if-elif
if score < 0 or score > 100:
    print("Invalid")
elif score >= 90:
    print("A")
elif score >= 80:
    print("B")

# Method 2: Chained comparison
if 0 <= score <= 100:
    if score >= 90:
        print("A")
```

### Pattern 2: Input Validation
```python
while True:
    age = input("Enter age: ")
    if age.isdigit():
        age = int(age)
        if 0 < age < 150:
            break
        else:
            print("Age out of range")
    else:
        print("Invalid input")
```

### Pattern 3: Multiple Conditions
```python
# Using 'and'
if username and password and email:
    create_account()

# Using 'or'
if error1 or error2 or error3:
    handle_error()

# Complex
if (age >= 18 and has_license) or is_supervised:
    allow_driving()
```

### Pattern 4: Early Return
```python
def process_data(data):
    # Guard clauses
    if not data:
        return None
    if len(data) < 10:
        return "Too short"
    
    # Main logic
    return analyze(data)
```

### Pattern 5: Flag Checking
```python
is_admin = True
is_active = True
has_permission = False

# Logical combinations
if is_admin and is_active:
    print("Full access")
elif is_active and has_permission:
    print("Limited access")
else:
    print("No access")
```

---

## Key Takeaways for PCAP Exam

1. ✅ **Indentation**: 4 spaces, consistent throughout
2. ✅ **elif vs else if**: Python uses `elif` (not `else if`)
3. ✅ **No switch statement**: Use if-elif or match (3.10+)
4. ✅ **Ternary operator**: `x if condition else y`
5. ✅ **Comparison chaining**: `1 < x < 10` is valid
6. ✅ **Boolean evaluation**: `if x:` checks truthiness
7. ✅ **Order matters**: Most specific conditions first
8. ✅ **Default case**: Use `else` or `case _` in match
9. ✅ **Compound conditions**: Use `and`, `or`, `not`
10. ✅ **Short-circuit**: `and` stops at first False, `or` at first True

---

## Practice Examples

### Example 1: Number Classifier
```python
num = int(input("Enter number: "))

if num > 0:
    print("Positive")
elif num < 0:
    print("Negative")
else:
    print("Zero")

if num % 2 == 0:
    print("Even")
else:
    print("Odd")
```

### Example 2: Leap Year
```python
year = int(input("Enter year: "))

if year % 4 != 0:
    print("Not a leap year")
elif year % 100 != 0:
    print("Leap year")
elif year % 400 != 0:
    print("Not a leap year")
else:
    print("Leap year")

# Or using logical operators
is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
print("Leap year" if is_leap else "Not a leap year")
```

### Example 3: Login System
```python
MAX_ATTEMPTS = 3
attempts = 0

while attempts < MAX_ATTEMPTS:
    password = input("Password: ")
    
    if password == "secret123":
        print("Access granted!")
        break
    else:
        attempts += 1
        remaining = MAX_ATTEMPTS - attempts
        if remaining > 0:
            print(f"Wrong! {remaining} attempts left")
        else:
            print("Account locked!")
```

---

## Common Pitfalls

### ❌ Wrong Indentation
```python
# WRONG
if True:
print("Error")  # IndentationError

# CORRECT
if True:
    print("Success")
```

### ❌ Assignment Instead of Comparison
```python
# WRONG
if x = 5:  # SyntaxError
    print("Wrong")

# CORRECT
if x == 5:
    print("Right")
```

### ❌ Missing Colon
```python
# WRONG
if x > 5  # SyntaxError
    print("Wrong")

# CORRECT
if x > 5:
    print("Right")
```

---

## Next Steps
Proceed to: **Module 3 Part 2: Loops** - for, while, break, continue
