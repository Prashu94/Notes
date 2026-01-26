# Module 4 Part 3: Dictionaries - Complete Guide

## Table of Contents
1. [Introduction to Dictionaries](#introduction-to-dictionaries)
2. [Creating Dictionaries](#creating-dictionaries)
3. [Accessing Elements](#accessing-elements)
4. [Adding and Modifying](#adding-and-modifying)
5. [Dictionary Methods](#dictionary-methods)
6. [Iterating Dictionaries](#iterating-dictionaries)
7. [Dictionary Comprehensions](#dictionary-comprehensions)
8. [Nested Dictionaries](#nested-dictionaries)
9. [Common Patterns](#common-patterns)

---

## Introduction to Dictionaries

Dictionaries are **mutable, unordered collections** of key-value pairs.

### Key Characteristics

- **Mutable**: Can be modified after creation
- **Unordered**: No guaranteed order (Python 3.7+ maintains insertion order)
- **Key-Value Pairs**: Each key maps to a value
- **Unique Keys**: Keys must be unique and immutable
- **Fast Lookup**: O(1) average time complexity

```python
# Example
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}
```

---

## Creating Dictionaries

### Method 1: Curly Braces

```python
# Empty dictionary
empty = {}

# With data
person = {
    "name": "Bob",
    "age": 25,
    "city": "NYC"
}

# Mixed types
mixed = {
    "number": 42,
    "name": "Alice",
    "scores": [90, 85, 88],
    "active": True
}
```

### Method 2: dict() Constructor

```python
# From keyword arguments
person = dict(name="Charlie", age=30, city="LA")

# From list of tuples
pairs = [("name", "Dave"), ("age", 35)]
person = dict(pairs)

# From two lists (using zip)
keys = ["name", "age", "city"]
values = ["Eve", 28, "SF"]
person = dict(zip(keys, values))
```

### Method 3: fromkeys()

```python
# Create dict with same value for all keys
keys = ["a", "b", "c"]
d = dict.fromkeys(keys, 0)
print(d)  # {'a': 0, 'b': 0, 'c': 0}

# Default value is None
d = dict.fromkeys(keys)
print(d)  # {'a': None, 'b': None, 'c': None}
```

---

## Accessing Elements

### Using Square Brackets

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

print(student["name"])   # Alice
print(student["age"])    # 20

# KeyError if key doesn't exist
# print(student["city"])  # KeyError
```

### Using get() Method (Safer)

```python
student = {"name": "Alice", "age": 20}

print(student.get("name"))       # Alice
print(student.get("city"))       # None (no error!)
print(student.get("city", "NYC")) # NYC (default value)
```

### Checking Key Existence

```python
student = {"name": "Alice", "age": 20}

print("name" in student)     # True
print("city" in student)     # False
print("city" not in student) # True
```

---

## Adding and Modifying

### Adding/Updating Single Item

```python
student = {"name": "Alice"}

# Add new key
student["age"] = 20
print(student)  # {'name': 'Alice', 'age': 20}

# Modify existing key
student["age"] = 21
print(student)  # {'name': 'Alice', 'age': 21}
```

### Removing Items

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

# del - Remove specific key
del student["grade"]
print(student)  # {'name': 'Alice', 'age': 20}

# pop() - Remove and return value
age = student.pop("age")
print(age)      # 20
print(student)  # {'name': 'Alice'}

# popitem() - Remove and return last item (Python 3.7+)
student = {"name": "Alice", "age": 20, "grade": "A"}
item = student.popitem()
print(item)     # ('grade', 'A')
print(student)  # {'name': 'Alice', 'age': 20}

# clear() - Remove all items
student.clear()
print(student)  # {}
```

---

## Dictionary Methods

### 1. keys() - Get All Keys

```python
student = {"name": "Alice", "age": 20, "grade": "A"}
keys = student.keys()
print(keys)         # dict_keys(['name', 'age', 'grade'])
print(list(keys))   # ['name', 'age', 'grade']
```

### 2. values() - Get All Values

```python
values = student.values()
print(values)       # dict_values(['Alice', 20, 'A'])
print(list(values)) # ['Alice', 20, 'A']
```

### 3. items() - Get All Key-Value Pairs

```python
items = student.items()
print(items)
# dict_items([('name', 'Alice'), ('age', 20), ('grade', 'A')])

for key, value in student.items():
    print(f"{key}: {value}")
```

### 4. update() - Merge Dictionaries

```python
student = {"name": "Alice", "age": 20}
new_data = {"grade": "A", "city": "NYC"}

student.update(new_data)
print(student)
# {'name': 'Alice', 'age': 20, 'grade': 'A', 'city': 'NYC'}

# Overwrite existing keys
student.update({"age": 21, "major": "CS"})
print(student)
# {'name': 'Alice', 'age': 21, 'grade': 'A', 'city': 'NYC', 'major': 'CS'}
```

### 5. setdefault() - Get or Set Default

```python
student = {"name": "Alice"}

# Get existing key
name = student.setdefault("name", "Unknown")
print(name)  # Alice

# Set default for missing key
age = student.setdefault("age", 18)
print(age)      # 18
print(student)  # {'name': 'Alice', 'age': 18}
```

### 6. copy() - Shallow Copy

```python
original = {"a": 1, "b": 2}
duplicate = original.copy()
duplicate["c"] = 3

print(original)   # {'a': 1, 'b': 2}
print(duplicate)  # {'a': 1, 'b': 2, 'c': 3}
```

---

## Iterating Dictionaries

### Iterate Over Keys (Default)

```python
student = {"name": "Alice", "age": 20, "grade": "A"}

for key in student:
    print(key)
# name
# age
# grade
```

### Iterate Over Values

```python
for value in student.values():
    print(value)
# Alice
# 20
# A
```

### Iterate Over Key-Value Pairs

```python
for key, value in student.items():
    print(f"{key}: {value}")
# name: Alice
# age: 20
# grade: A
```

---

## Dictionary Comprehensions

### Basic Syntax

```python
{key_expr: value_expr for item in iterable}
```

### Example 1: Squares

```python
squares = {x: x**2 for x in range(1, 6)}
print(squares)  # {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

### Example 2: With Condition

```python
even_squares = {x: x**2 for x in range(1, 11) if x % 2 == 0}
print(even_squares)  # {2: 4, 4: 16, 6: 36, 8: 64, 10: 100}
```

### Example 3: From Two Lists

```python
keys = ["a", "b", "c"]
values = [1, 2, 3]
d = {k: v for k, v in zip(keys, values)}
print(d)  # {'a': 1, 'b': 2, 'c': 3}
```

### Example 4: String Processing

```python
words = ["apple", "banana", "cherry"]
lengths = {word: len(word) for word in words}
print(lengths)  # {'apple': 5, 'banana': 6, 'cherry': 6}
```

### Example 5: Swap Keys and Values

```python
original = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in original.items()}
print(swapped)  # {1: 'a', 2: 'b', 3: 'c'}
```

---

## Nested Dictionaries

### Creating Nested Dictionaries

```python
students = {
    "student1": {
        "name": "Alice",
        "age": 20,
        "grades": [90, 85, 88]
    },
    "student2": {
        "name": "Bob",
        "age": 22,
        "grades": [78, 82, 85]
    }
}
```

### Accessing Nested Data

```python
print(students["student1"]["name"])        # Alice
print(students["student2"]["grades"][0])   # 78
```

### Iterating Nested Dictionaries

```python
for student_id, info in students.items():
    print(f"\n{student_id}:")
    for key, value in info.items():
        print(f"  {key}: {value}")
```

---

## Common Patterns

### 1. Counting Occurrences

```python
text = "hello world"
count = {}
for char in text:
    count[char] = count.get(char, 0) + 1
print(count)
# {'h': 1, 'e': 1, 'l': 3, 'o': 2, ' ': 1, 'w': 1, 'r': 1, 'd': 1}

# Using setdefault
count = {}
for char in text:
    count.setdefault(char, 0)
    count[char] += 1
```

### 2. Grouping Data

```python
students = [
    {"name": "Alice", "grade": "A"},
    {"name": "Bob", "grade": "B"},
    {"name": "Charlie", "grade": "A"}
]

by_grade = {}
for student in students:
    grade = student["grade"]
    by_grade.setdefault(grade, []).append(student["name"])

print(by_grade)
# {'A': ['Alice', 'Charlie'], 'B': ['Bob']}
```

### 3. Merging Dictionaries

```python
# Python 3.9+
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
merged = dict1 | dict2  # {' a': 1, 'b': 2, 'c': 3, 'd': 4}

# Older Python
merged = {**dict1, **dict2}

# Using update
merged = dict1.copy()
merged.update(dict2)
```

### 4. Default Dictionary (collections)

```python
from collections import defaultdict

# Automatically creates default values
count = defaultdict(int)
for char in "hello":
    count[char] += 1  # No need for get() or setdefault()
print(dict(count))  # {'h': 1, 'e': 1, 'l': 2, 'o': 1}

# With lists
groups = defaultdict(list)
groups["A"].append("Alice")
groups["A"].append("Andy")
print(dict(groups))  # {'A': ['Alice', 'Andy']}
```

### 5. Sorting Dictionary

```python
scores = {"Alice": 90, "Bob": 85, "Charlie": 95}

# Sort by key
sorted_by_key = dict(sorted(scores.items()))
print(sorted_by_key)  # {'Alice': 90, 'Bob': 85, 'Charlie': 95}

# Sort by value
sorted_by_value = dict(sorted(scores.items(), key=lambda x: x[1]))
print(sorted_by_value)  # {'Bob': 85, 'Alice': 90, 'Charlie': 95}

# Sort by value (descending)
sorted_desc = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
print(sorted_desc)  # {'Charlie': 95, 'Alice': 90, 'Bob': 85}
```

---

## Summary

| **Operation** | **Syntax** | **Time Complexity** |
|---------------|------------|---------------------|
| Access | `dict[key]` | O(1) average |
| Add/Update | `dict[key] = value` | O(1) average |
| Delete | `del dict[key]` | O(1) average |
| Check key | `key in dict` | O(1) average |
| Get keys | `dict.keys()` | O(1) |
| Get values | `dict.values()` | O(1) |
| Get items | `dict.items()` | O(1) |

### Key Concepts Checklist

✅ Dictionary creation methods  
✅ Accessing and modifying elements  
✅ Dictionary methods (get, keys, values, items, update, etc.)  
✅ Iterating dictionaries  
✅ Dictionary comprehensions  
✅ Nested dictionaries  
✅ Common patterns (counting, grouping, merging, sorting)  

---

## Next Steps
➡️ **Module 4: Dictionaries Practice Questions** (20 exam-style questions)  
➡️ **Module 4: Sets**
