# Module 5 Part 2: Lambda and Functional Programming

## Table of Contents
1. [Lambda Functions](#lambda-functions)
2. [Map Function](#map-function)
3. [Filter Function](#filter-function)
4. [Reduce Function](#reduce-function)
5. [List Comprehensions vs Lambda](#list-comprehensions-vs-lambda)
6. [Sorting with Lambda](#sorting-with-lambda)
7. [Closures](#closures)
8. [Best Practices](#best-practices)

---

## Lambda Functions

### What is Lambda?

**Anonymous, inline functions** defined with `lambda` keyword.

### Syntax

```python
lambda parameters: expression
```

### Example 1: Basic Lambda

```python
# Regular function
def square(x):
    return x ** 2

# Lambda equivalent
square_lambda = lambda x: x ** 2

print(square(5))         # 25
print(square_lambda(5))  # 25
```

### Example 2: Multiple Parameters

```python
# Regular function
def add(a, b):
    return a + b

# Lambda
add_lambda = lambda a, b: a + b

print(add_lambda(3, 4))  # 7
```

### Example 3: No Parameters

```python
greet = lambda: "Hello, World!"
print(greet())  # Hello, World!
```

### When to Use Lambda

✅ **Short, simple operations**  
✅ **One-time use functions**  
✅ **As arguments to higher-order functions**  

❌ **Complex logic** (use regular functions)  
❌ **Multiple statements** (lambda only allows single expression)  

---

## Map Function

### Purpose

Apply a function to **every item** in an iterable.

### Syntax

```python
map(function, iterable)
```

### Example 1: Square Numbers

```python
numbers = [1, 2, 3, 4, 5]

# With lambda
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# With regular function
def square(x):
    return x ** 2

squared = list(map(square, numbers))
print(squared)  # [1, 4, 9, 16, 25]
```

### Example 2: Convert to Uppercase

```python
words = ["hello", "world", "python"]

# Using lambda
upper = list(map(lambda s: s.upper(), words))
print(upper)  # ['HELLO', 'WORLD', 'PYTHON']

# Using str.upper method
upper = list(map(str.upper, words))
print(upper)  # ['HELLO', 'WORLD', 'PYTHON']
```

### Example 3: Multiple Iterables

```python
list1 = [1, 2, 3]
list2 = [10, 20, 30]

# Add corresponding elements
result = list(map(lambda x, y: x + y, list1, list2))
print(result)  # [11, 22, 33]
```

### Example 4: Type Conversion

```python
str_numbers = ["1", "2", "3", "4", "5"]
int_numbers = list(map(int, str_numbers))
print(int_numbers)  # [1, 2, 3, 4, 5]
```

---

## Filter Function

### Purpose

**Filter items** based on a condition (returns True/False).

### Syntax

```python
filter(function, iterable)
```

### Example 1: Even Numbers

```python
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# With lambda
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4, 6, 8, 10]
```

### Example 2: Filter Strings

```python
words = ["", "hello", "", "world", "python", ""]

# Remove empty strings
non_empty = list(filter(lambda s: len(s) > 0, words))
print(non_empty)  # ['hello', 'world', 'python']

# Simpler (empty string is falsy)
non_empty = list(filter(None, words))
print(non_empty)  # ['hello', 'world', 'python']
```

### Example 3: Filter by Condition

```python
numbers = [15, 8, 23, 42, 7, 16, 50]

# Numbers greater than 20
result = list(filter(lambda x: x > 20, numbers))
print(result)  # [23, 42, 50]
```

### Example 4: Filter Objects

```python
students = [
    {"name": "Alice", "grade": 85},
    {"name": "Bob", "grade": 72},
    {"name": "Charlie", "grade": 90}
]

# Students with grade >= 80
top_students = list(filter(lambda s: s["grade"] >= 80, students))
print(top_students)
# [{'name': 'Alice', 'grade': 85}, {'name': 'Charlie', 'grade': 90}]
```

---

## Reduce Function

### Purpose

**Accumulate** values by applying a function cumulatively.

### Import Required

```python
from functools import reduce
```

### Syntax

```python
reduce(function, iterable[, initializer])
```

### Example 1: Sum All Numbers

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Sum using reduce
total = reduce(lambda x, y: x + y, numbers)
print(total)  # 15

# Equivalent to:
# ((((1 + 2) + 3) + 4) + 5)
```

### Example 2: Product

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

product = reduce(lambda x, y: x * y, numbers)
print(product)  # 120 (1 * 2 * 3 * 4 * 5)
```

### Example 3: Maximum Value

```python
from functools import reduce

numbers = [3, 7, 2, 9, 1]

maximum = reduce(lambda x, y: x if x > y else y, numbers)
print(maximum)  # 9

# Better: use built-in max()
print(max(numbers))  # 9
```

### Example 4: Concatenate Strings

```python
from functools import reduce

words = ["Hello", " ", "World", "!"]

sentence = reduce(lambda x, y: x + y, words)
print(sentence)  # Hello World!

# Better: use ''.join()
print(''.join(words))  # Hello World!
```

### With Initial Value

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# Start with initial value 10
total = reduce(lambda x, y: x + y, numbers, 10)
print(total)  # 25 (10 + 1 + 2 + 3 + 4 + 5)
```

---

## List Comprehensions vs Lambda

### List Comprehension (Preferred)

```python
# Map equivalent
numbers = [1, 2, 3, 4, 5]
squared = [x ** 2 for x in numbers]

# Filter equivalent
evens = [x for x in numbers if x % 2 == 0]

# Map + Filter
squared_evens = [x ** 2 for x in numbers if x % 2 == 0]
```

### Lambda with map/filter

```python
numbers = [1, 2, 3, 4, 5]

# Map
squared = list(map(lambda x: x ** 2, numbers))

# Filter
evens = list(filter(lambda x: x % 2 == 0, numbers))

# Map + Filter
squared_evens = list(map(lambda x: x ** 2, 
                         filter(lambda x: x % 2 == 0, numbers)))
```

### When to Use Which?

**List Comprehensions:**
- ✅ More Pythonic
- ✅ More readable
- ✅ Slightly faster

**Lambda with map/filter:**
- ✅ Functional programming style
- ✅ When you already have a function
- ✅ Working with existing code

---

## Sorting with Lambda

### Sort List with key Parameter

```python
# Sort by absolute value
numbers = [-5, -2, -8, 3, 1, -7]
sorted_nums = sorted(numbers, key=lambda x: abs(x))
print(sorted_nums)  # [1, -2, 3, -5, -7, -8]
```

### Sort List of Tuples

```python
students = [
    ("Alice", 85),
    ("Bob", 72),
    ("Charlie", 90)
]

# Sort by grade (second element)
by_grade = sorted(students, key=lambda x: x[1])
print(by_grade)
# [('Bob', 72), ('Alice', 85), ('Charlie', 90)]

# Reverse order (highest first)
by_grade_desc = sorted(students, key=lambda x: x[1], reverse=True)
print(by_grade_desc)
# [('Charlie', 90), ('Alice', 85), ('Bob', 72)]
```

### Sort List of Dictionaries

```python
students = [
    {"name": "Alice", "age": 25, "grade": 85},
    {"name": "Bob", "age": 22, "grade": 90},
    {"name": "Charlie", "age": 23, "grade": 78}
]

# Sort by grade
by_grade = sorted(students, key=lambda x: x["grade"])

# Sort by age
by_age = sorted(students, key=lambda x: x["age"])

# Sort by name length
by_name_len = sorted(students, key=lambda x: len(x["name"]))
```

### Sort Strings

```python
words = ["apple", "Banana", "cherry", "Date"]

# Case-insensitive sort
sorted_words = sorted(words, key=lambda s: s.lower())
print(sorted_words)  # ['apple', 'Banana', 'cherry', 'Date']

# By length
by_length = sorted(words, key=lambda s: len(s))
print(by_length)  # ['Date', 'apple', 'cherry', 'Banana']
```

---

## Closures

### What is a Closure?

A function that **remembers variables** from its enclosing scope.

### Example 1: Basic Closure

```python
def outer(x):
    def inner(y):
        return x + y  # inner remembers x
    return inner

add_5 = outer(5)
print(add_5(3))  # 8
print(add_5(10)) # 15
```

### Example 2: Multiplier Function

```python
def make_multiplier(n):
    return lambda x: x * n

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

### Example 3: Counter

```python
def counter():
    count = 0
    
    def increment():
        nonlocal count
        count += 1
        return count
    
    return increment

c1 = counter()
print(c1())  # 1
print(c1())  # 2
print(c1())  # 3

c2 = counter()
print(c2())  # 1 (separate counter)
```

---

## Best Practices

### 1. Keep Lambda Simple

```python
# Good - simple, readable
square = lambda x: x ** 2

# Bad - too complex for lambda
# complex = lambda x: x ** 2 if x > 0 else -x ** 2 if x < 0 else 0

# Better - use regular function
def complex(x):
    if x > 0:
        return x ** 2
    elif x < 0:
        return -x ** 2
    else:
        return 0
```

### 2. Prefer List Comprehensions

```python
numbers = [1, 2, 3, 4, 5]

# Lambda
doubled = list(map(lambda x: x * 2, numbers))

# List comprehension (preferred)
doubled = [x * 2 for x in numbers]
```

### 3. Named Functions for Reusability

```python
# If used once - lambda is fine
sorted_nums = sorted(numbers, key=lambda x: abs(x))

# If used multiple times - name it
def by_absolute_value(x):
    return abs(x)

sorted_nums = sorted(numbers, key=by_absolute_value)
filtered_nums = filter(by_absolute_value, numbers)
```

### 4. Use Built-ins When Possible

```python
# Instead of reduce for sum
from functools import reduce
total = reduce(lambda x, y: x + y, numbers)

# Use built-in
total = sum(numbers)

# Instead of filter/map for type conversion
ints = list(map(int, strings))

# Use list comprehension
ints = [int(s) for s in strings]
```

---

## Summary

| **Function** | **Purpose** | **Returns** |
|--------------|-------------|-------------|
| `lambda` | Anonymous function | Function object |
| `map()` | Apply function to all | Iterator |
| `filter()` | Select items by condition | Iterator |
| `reduce()` | Accumulate values | Single value |

### Key Concepts Checklist

✅ Lambda syntax and usage  
✅ map() for transformations  
✅ filter() for selections  
✅ reduce() for accumulation  
✅ Sorting with key parameter  
✅ Closures and enclosing scope  
✅ When to use lambda vs regular functions  

---

## Next Steps
➡️ **Module 5: Lambda Practice Questions** (20 exam-style questions)  
➡️ **Module 6: Modules and Packages**
