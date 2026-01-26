# Module 4 Part 2: Tuples - Complete Guide

## Table of Contents
1. [Introduction to Tuples](#introduction-to-tuples)
2. [Creating Tuples](#creating-tuples)
3. [Accessing Elements](#accessing-elements)
4. [Tuple Operations](#tuple-operations)
5. [Tuple Methods](#tuple-methods)
6. [Tuple Unpacking](#tuple-unpacking)
7. [Named Tuples](#named-tuples)
8. [Tuples vs Lists](#tuples-vs-lists)
9. [Common Use Cases](#common-use-cases)

---

## Introduction to Tuples

Tuples are **immutable, ordered collections** similar to lists but cannot be modified after creation.

### Key Characteristics

- **Immutable**: Cannot be changed after creation
- **Ordered**: Maintains insertion order
- **Indexed**: Access by position (0-based)
- **Heterogeneous**: Can contain different data types
- **Hashable**: Can be used as dictionary keys (if all elements are hashable)

```python
# Examples
numbers = (1, 2, 3, 4, 5)
mixed = (1, "hello", 3.14, True)
single = (42,)  # Note the comma!
empty = ()
```

---

## Creating Tuples

### Method 1: Parentheses

```python
fruits = ("apple", "banana", "cherry")
numbers = (1, 2, 3, 4, 5)
mixed = (1, "hello", 3.14, True)
```

### Method 2: Without Parentheses (Tuple Packing)

```python
point = 10, 20  # (10, 20)
coords = 1, 2, 3  # (1, 2, 3)
```

### Method 3: tuple() Constructor

```python
# From list
nums = tuple([1, 2, 3])  # (1, 2, 3)

# From string
chars = tuple("Python")  # ('P', 'y', 't', 'h', 'o', 'n')

# From range
evens = tuple(range(0, 10, 2))  # (0, 2, 4, 6, 8)
```

### Single Element Tuple (Important!)

```python
# WRONG - This is an integer
not_tuple = (5)     # 5
type(not_tuple)     # <class 'int'>

# CORRECT - Need comma
is_tuple = (5,)     # (5,)
type(is_tuple)      # <class 'tuple'>

# Also correct
another = 5,        # (5,)
```

### Empty Tuple

```python
empty1 = ()
empty2 = tuple()
```

---

## Accessing Elements

### Indexing

```python
fruits = ("apple", "banana", "cherry")

print(fruits[0])   # apple (first)
print(fruits[1])   # banana
print(fruits[-1])  # cherry (last)
print(fruits[-2])  # banana (second from end)
```

### Slicing

```python
numbers = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

print(numbers[2:5])      # (2, 3, 4)
print(numbers[:5])       # (0, 1, 2, 3, 4)
print(numbers[5:])       # (5, 6, 7, 8, 9)
print(numbers[::2])      # (0, 2, 4, 6, 8)
print(numbers[::-1])     # (9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
```

### Membership Testing

```python
fruits = ("apple", "banana", "cherry")

print("apple" in fruits)      # True
print("grape" in fruits)      # False
print("grape" not in fruits)  # True
```

---

## Tuple Operations

### Concatenation (+)

```python
tuple1 = (1, 2, 3)
tuple2 = (4, 5, 6)
combined = tuple1 + tuple2  # (1, 2, 3, 4, 5, 6)
```

### Repetition (*)

```python
nums = (1, 2) * 3  # (1, 2, 1, 2, 1, 2)
```

### Length

```python
fruits = ("apple", "banana", "cherry")
print(len(fruits))  # 3
```

### Min/Max/Sum

```python
numbers = (3, 1, 4, 1, 5, 9)
print(min(numbers))  # 1
print(max(numbers))  # 9
print(sum(numbers))  # 23
```

---

## Tuple Methods

Tuples have only **2 methods** (because they're immutable).

### 1. count() - Count Occurrences

```python
numbers = (1, 2, 3, 2, 4, 2, 5)
print(numbers.count(2))  # 3
print(numbers.count(99)) # 0
```

### 2. index() - Find Position

```python
fruits = ("apple", "banana", "cherry", "banana")

print(fruits.index("banana"))  # 1 (first occurrence)
print(fruits.index("cherry"))  # 2

# print(fruits.index("grape"))  # ValueError

# With start and end
print(fruits.index("banana", 2))  # 3 (search from index 2)
```

---

## Tuple Unpacking

### Basic Unpacking

```python
point = (10, 20)
x, y = point
print(x)  # 10
print(y)  # 20
```

### Multiple Values

```python
person = ("Alice", 25, "Engineer")
name, age, job = person
print(name)  # Alice
print(age)   # 25
print(job)   # Engineer
```

### Swapping Variables

```python
a = 5
b = 10
a, b = b, a
print(a)  # 10
print(b)  # 5
```

### Using * (Extended Unpacking)

```python
numbers = (1, 2, 3, 4, 5)

# Get first and rest
first, *rest = numbers
print(first)  # 1
print(rest)   # [2, 3, 4, 5]

# Get first, last, and middle
first, *middle, last = numbers
print(first)   # 1
print(middle)  # [2, 3, 4]
print(last)    # 5

# Get last and rest
*rest, last = numbers
print(rest)  # [1, 2, 3, 4]
print(last)  # 5
```

### Ignoring Values

```python
person = ("Alice", 25, "Engineer", "USA")
name, _, job, _ = person  # Ignore age and country
print(name)  # Alice
print(job)   # Engineer
```

---

## Named Tuples

Named tuples create tuple subclasses with named fields.

### Creating Named Tuples

```python
from collections import namedtuple

# Define
Point = namedtuple('Point', ['x', 'y'])

# Create instance
p = Point(10, 20)
print(p)      # Point(x=10, y=20)
print(p.x)    # 10
print(p.y)    # 20
print(p[0])   # 10 (still supports indexing)
```

### Example: Person

```python
from collections import namedtuple

Person = namedtuple('Person', ['name', 'age', 'city'])

alice = Person('Alice', 30, 'NYC')
print(alice.name)  # Alice
print(alice.age)   # 30

# Unpacking works
name, age, city = alice
```

### Converting to Dictionary

```python
alice_dict = alice._asdict()
print(alice_dict)  # OrderedDict([('name', 'Alice'), ...])
```

---

## Tuples vs Lists

| **Feature** | **Tuple** | **List** |
|-------------|-----------|----------|
| Mutability | Immutable | Mutable |
| Syntax | `(1, 2, 3)` | `[1, 2, 3]` |
| Performance | Faster | Slower |
| Memory | Less | More |
| Methods | 2 (count, index) | Many (append, remove, etc.) |
| Use case | Fixed data | Dynamic data |
| Dict key | Yes (if hashable) | No |

### Immutability Example

```python
# List - Mutable
my_list = [1, 2, 3]
my_list[0] = 99  # OK
my_list.append(4)  # OK

# Tuple - Immutable
my_tuple = (1, 2, 3)
# my_tuple[0] = 99  # TypeError
# my_tuple.append(4)  # AttributeError
```

### Performance

```python
import sys

my_list = [1, 2, 3, 4, 5]
my_tuple = (1, 2, 3, 4, 5)

print(sys.getsizeof(my_list))   # 104 bytes
print(sys.getsizeof(my_tuple))  # 80 bytes
```

---

## Common Use Cases

### 1. Multiple Return Values

```python
def get_stats(numbers):
    return min(numbers), max(numbers), sum(numbers)

data = [1, 2, 3, 4, 5]
minimum, maximum, total = get_stats(data)
print(f"Min: {minimum}, Max: {maximum}, Total: {total}")
```

### 2. Dictionary Keys

```python
# Tuple as key (OK)
locations = {
    (0, 0): "Origin",
    (1, 2): "Point A",
    (3, 4): "Point B"
}
print(locations[(1, 2)])  # Point A

# List as key (Error!)
# bad_dict = {[0, 0]: "Origin"}  # TypeError
```

### 3. Function Arguments

```python
def print_coordinates(x, y, z):
    print(f"X: {x}, Y: {y}, Z: {z}")

coords = (10, 20, 30)
print_coordinates(*coords)  # Unpacking
```

### 4. Immutable Data

```python
# Configuration (shouldn't change)
CONFIG = (
    "database.db",
    "localhost",
    5432
)

# Coordinates
point = (10.5, 20.3)
```

### 5. Enumerate

```python
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
    # enumerate returns tuples: (0, 'apple'), (1, 'banana'), ...
    print(f"{index}: {fruit}")
```

---

## Summary

### When to Use Tuples

✅ Data should not change  
✅ Need to use as dictionary key  
✅ Returning multiple values from function  
✅ Better performance than lists  
✅ Representing fixed collections (coordinates, RGB colors, etc.)  

### When to Use Lists

✅ Data needs to be modified  
✅ Need list methods (append, remove, etc.)  
✅ Dynamic collections that grow/shrink  

### Key Concepts Checklist

✅ Tuple creation (including single-element tuples)  
✅ Immutability concept  
✅ Tuple methods (count, index)  
✅ Tuple unpacking  
✅ Named tuples  
✅ Tuples vs Lists comparison  
✅ Common use cases  

---

## Next Steps
➡️ **Module 4: Tuples Practice Questions** (20 exam-style questions)  
➡️ **Module 4: Dictionaries**
