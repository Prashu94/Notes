# Module 3 Part 3: Loops (for and while)

## Table of Contents
1. [Introduction to Loops](#introduction-to-loops)
2. [While Loops](#while-loops)
3. [For Loops](#for-loops)
4. [Range Function](#range-function)
5. [Break Statement](#break-statement)
6. [Continue Statement](#continue-statement)
7. [Else Clause with Loops](#else-clause-with-loops)
8. [Nested Loops](#nested-loops)
9. [Loop Control Best Practices](#loop-control-best-practices)

---

## Introduction to Loops

Loops allow you to execute a block of code repeatedly. Python provides two types of loops:

1. **while loop**: Repeats while a condition is true
2. **for loop**: Iterates over a sequence

### Why Use Loops?

```python
# Without loop (repetitive)
print("Hello")
print("Hello")
print("Hello")

# With loop (efficient)
for i in range(3):
    print("Hello")
```

---

## While Loops

### Basic Syntax

```python
while condition:
    # code block
    # must eventually make condition False
```

### Example 1: Basic Counter

```python
count = 1
while count <= 5:
    print(f"Count: {count}")
    count += 1

# Output:
# Count: 1
# Count: 2
# Count: 3
# Count: 4
# Count: 5
```

### Example 2: User Input Validation

```python
password = ""
while len(password) < 6:
    password = input("Enter password (min 6 chars): ")
print("Password accepted!")
```

### Example 3: Sum Until Condition

```python
total = 0
num = 1
while num <= 10:
    total += num
    num += 1
print(f"Sum: {total}")  # 55
```

### Infinite Loops (Caution!)

```python
# DANGEROUS - Never ends!
# while True:
#     print("Forever")

# SAFE - With break condition
while True:
    response = input("Continue? (yes/no): ")
    if response.lower() == "no":
        break
```

---

## For Loops

### Basic Syntax

```python
for variable in sequence:
    # code block
```

### Example 1: Iterate Over String

```python
for char in "Python":
    print(char)

# Output: P y t h o n (each on new line)
```

### Example 2: Iterate Over List

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}")
```

### Example 3: Iterate Over Dictionary

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# Keys only
for key in student:
    print(key)

# Values only
for value in student.values():
    print(value)

# Key-value pairs
for key, value in student.items():
    print(f"{key}: {value}")
```

---

## Range Function

The `range()` function generates a sequence of numbers.

### Syntax Variations

```python
range(stop)           # 0 to stop-1
range(start, stop)    # start to stop-1
range(start, stop, step)  # with custom step
```

### Example 1: range(stop)

```python
for i in range(5):
    print(i)

# Output: 0 1 2 3 4
```

### Example 2: range(start, stop)

```python
for i in range(1, 6):
    print(i)

# Output: 1 2 3 4 5
```

### Example 3: range(start, stop, step)

```python
# Even numbers
for i in range(0, 11, 2):
    print(i)  # 0 2 4 6 8 10

# Countdown
for i in range(10, 0, -1):
    print(i)  # 10 9 8 7 6 5 4 3 2 1
```

### Example 4: List Indexing

```python
fruits = ["apple", "banana", "cherry"]
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Better way:
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

---

## Break Statement

The `break` statement exits the loop immediately.

### Example 1: Search and Stop

```python
numbers = [1, 5, 8, 12, 15]
for num in numbers:
    if num > 10:
        print(f"Found: {num}")
        break
    print(f"Checking: {num}")

# Output:
# Checking: 1
# Checking: 5
# Checking: 8
# Found: 12
```

### Example 2: While with Break

```python
count = 0
while True:
    count += 1
    if count == 5:
        break
    print(count)

# Output: 1 2 3 4
```

### Example 3: Nested Loop Break

```python
for i in range(3):
    for j in range(3):
        if i == j == 1:
            break
        print(f"i={i}, j={j}")
    # break only exits inner loop
```

---

## Continue Statement

The `continue` statement skips the current iteration and moves to the next.

### Example 1: Skip Even Numbers

```python
for i in range(1, 11):
    if i % 2 == 0:
        continue  # Skip even numbers
    print(i)

# Output: 1 3 5 7 9
```

### Example 2: Skip Specific Values

```python
for letter in "Python":
    if letter in "th":
        continue
    print(letter)

# Output: P y o n
```

### Example 3: While with Continue

```python
count = 0
while count < 5:
    count += 1
    if count == 3:
        continue
    print(count)

# Output: 1 2 4 5
```

---

## Else Clause with Loops

Python loops can have an `else` clause that executes when the loop completes normally (not via `break`).

### For Loop with Else

```python
for i in range(5):
    print(i)
else:
    print("Loop completed normally")

# Output: 0 1 2 3 4 Loop completed normally
```

### While Loop with Else

```python
count = 0
while count < 3:
    print(count)
    count += 1
else:
    print("While loop done")

# Output: 0 1 2 While loop done
```

### Else NOT Executed (Break)

```python
for i in range(10):
    if i == 5:
        break
    print(i)
else:
    print("This won't print")

# Output: 0 1 2 3 4
```

### Practical Example: Prime Number Check

```python
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False  # Found divisor
    else:
        return True  # No divisors found

print(is_prime(17))  # True
print(is_prime(20))  # False
```

---

## Nested Loops

Loops inside loops.

### Example 1: Multiplication Table

```python
for i in range(1, 6):
    for j in range(1, 6):
        print(f"{i} x {j} = {i*j}")
    print("---")
```

### Example 2: Pattern Printing

```python
# Right triangle
for i in range(1, 6):
    for j in range(i):
        print("*", end="")
    print()

# Output:
# *
# **
# ***
# ****
# *****
```

### Example 3: 2D List Traversal

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

for row in matrix:
    for element in row:
        print(element, end=" ")
    print()

# Output:
# 1 2 3 
# 4 5 6 
# 7 8 9
```

### Example 4: Breaking Nested Loops

```python
# Using flag
found = False
for i in range(5):
    for j in range(5):
        if i * j > 10:
            found = True
            break
    if found:
        break
```

---

## Loop Control Best Practices

### 1. Avoid Infinite Loops

```python
# BAD
# while True:
#     print("Forever")

# GOOD
max_attempts = 100
count = 0
while count < max_attempts:
    # code
    count += 1
```

### 2. Use For Instead of While When Possible

```python
# Less Pythonic
i = 0
while i < len(items):
    print(items[i])
    i += 1

# More Pythonic
for item in items:
    print(item)
```

### 3. Don't Modify List While Iterating

```python
# WRONG
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num % 2 == 0:
        numbers.remove(num)  # Dangerous!

# CORRECT
numbers = [1, 2, 3, 4, 5]
numbers = [num for num in numbers if num % 2 != 0]
```

### 4. Use enumerate() for Index + Value

```python
# Less elegant
fruits = ["apple", "banana"]
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# Better
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

### 5. Use zip() for Parallel Iteration

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 90, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

---

## Summary

| **Loop Type** | **Use Case** |
|---------------|--------------|
| `while` | Unknown iterations, condition-based |
| `for` | Known iterations, iterate sequences |
| `break` | Exit loop early |
| `continue` | Skip current iteration |
| `else` | Execute after normal completion |

### Key Concepts Checklist

✅ While loop syntax and usage  
✅ For loop with sequences  
✅ range() function variations  
✅ break and continue statements  
✅ else clause with loops  
✅ Nested loops  
✅ Loop control best practices  

---

## Practice

Create a program that:
1. Prints numbers 1-10 using while loop
2. Prints even numbers 0-20 using for loop
3. Finds first number > 100 that's divisible by 7
4. Prints multiplication table (1-5)

---

## Next Steps
➡️ **Module 3: Loops Practice Questions** (20 exam-style questions)  
➡️ **Module 4: Data Structures - Lists**
