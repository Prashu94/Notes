# Module 4 Part 1: Lists - Complete Guide

## Table of Contents
1. [Introduction to Lists](#introduction-to-lists)
2. [Creating Lists](#creating-lists)
3. [Accessing Elements](#accessing-elements)
4. [List Operations](#list-operations)
5. [List Methods](#list-methods)
6. [List Slicing](#list-slicing)
7. [List Comprehensions](#list-comprehensions)
8. [Nested Lists](#nested-lists)
9. [List Copying](#list-copying)
10. [Common Patterns](#common-patterns)

---

## Introduction to Lists

Lists are **mutable, ordered collections** that can hold items of any type.

### Key Characteristics

- **Mutable**: Can be modified after creation
- **Ordered**: Maintains insertion order
- **Indexed**: Access by position (0-based)
- **Heterogeneous**: Can contain different data types
- **Dynamic**: Can grow or shrink in size

```python
# Examples
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, [1, 2]]
empty = []
```

---

## Creating Lists

### Method 1: Square Brackets

```python
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
empty = []
```

### Method 2: list() Constructor

```python
# From string
chars = list("Python")  # ['P', 'y', 't', 'h', 'o', 'n']

# From tuple
nums = list((1, 2, 3))  # [1, 2, 3]

# From range
evens = list(range(0, 10, 2))  # [0, 2, 4, 6, 8]
```

### Method 3: List Comprehension

```python
squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]
```

### Method 4: Multiplication

```python
zeros = [0] * 5  # [0, 0, 0, 0, 0]
matrix = [[0] * 3 for _ in range(2)]  # [[0,0,0], [0,0,0]]
```

---

## Accessing Elements

### Indexing (0-based)

```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])   # apple (first)
print(fruits[1])   # banana
print(fruits[-1])  # cherry (last)
print(fruits[-2])  # banana (second from end)
```

### Index Out of Range

```python
fruits = ["apple", "banana"]
# print(fruits[5])  # IndexError: list index out of range
```

### Checking Membership

```python
fruits = ["apple", "banana", "cherry"]

print("apple" in fruits)     # True
print("grape" in fruits)     # False
print("grape" not in fruits) # True
```

---

## List Operations

### Concatenation (+)

```python
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined = list1 + list2  # [1, 2, 3, 4, 5, 6]
```

### Repetition (*)

```python
nums = [1, 2] * 3  # [1, 2, 1, 2, 1, 2]
```

### Length

```python
fruits = ["apple", "banana", "cherry"]
print(len(fruits))  # 3
```

### Min/Max/Sum

```python
numbers = [3, 1, 4, 1, 5, 9]
print(min(numbers))  # 1
print(max(numbers))  # 9
print(sum(numbers))  # 23
```

---

## List Methods

### 1. append() - Add Single Item

```python
fruits = ["apple", "banana"]
fruits.append("cherry")
print(fruits)  # ['apple', 'banana', 'cherry']
```

### 2. extend() - Add Multiple Items

```python
fruits = ["apple", "banana"]
fruits.extend(["cherry", "date"])
print(fruits)  # ['apple', 'banana', 'cherry', 'date']
```

### 3. insert() - Add at Position

```python
fruits = ["apple", "cherry"]
fruits.insert(1, "banana")
print(fruits)  # ['apple', 'banana', 'cherry']
```

### 4. remove() - Remove First Occurrence

```python
fruits = ["apple", "banana", "cherry", "banana"]
fruits.remove("banana")
print(fruits)  # ['apple', 'cherry', 'banana']
```

### 5. pop() - Remove and Return

```python
fruits = ["apple", "banana", "cherry"]

last = fruits.pop()      # Removes 'cherry'
print(last)              # cherry
print(fruits)            # ['apple', 'banana']

first = fruits.pop(0)    # Removes 'apple'
print(first)             # apple
```

### 6. clear() - Remove All Items

```python
fruits = ["apple", "banana"]
fruits.clear()
print(fruits)  # []
```

### 7. index() - Find Position

```python
fruits = ["apple", "banana", "cherry"]
print(fruits.index("banana"))  # 1

# print(fruits.index("grape"))  # ValueError
```

### 8. count() - Count Occurrences

```python
numbers = [1, 2, 3, 2, 4, 2]
print(numbers.count(2))  # 3
print(numbers.count(5))  # 0
```

### 9. sort() - Sort in Place

```python
numbers = [3, 1, 4, 1, 5]
numbers.sort()
print(numbers)  # [1, 1, 3, 4, 5]

numbers.sort(reverse=True)
print(numbers)  # [5, 4, 3, 1, 1]

fruits = ["banana", "apple", "cherry"]
fruits.sort()
print(fruits)  # ['apple', 'banana', 'cherry']
```

### 10. reverse() - Reverse in Place

```python
numbers = [1, 2, 3, 4, 5]
numbers.reverse()
print(numbers)  # [5, 4, 3, 2, 1]
```

### 11. copy() - Shallow Copy

```python
original = [1, 2, 3]
duplicate = original.copy()
duplicate.append(4)

print(original)   # [1, 2, 3]
print(duplicate)  # [1, 2, 3, 4]
```

---

## List Slicing

### Basic Syntax

```python
list[start:stop:step]
```

### Examples

```python
numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

print(numbers[2:5])      # [2, 3, 4]
print(numbers[:5])       # [0, 1, 2, 3, 4] (from start)
print(numbers[5:])       # [5, 6, 7, 8, 9] (to end)
print(numbers[::2])      # [0, 2, 4, 6, 8] (every 2nd)
print(numbers[1::2])     # [1, 3, 5, 7, 9] (odd indices)
print(numbers[::-1])     # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0] (reverse)
print(numbers[-3:])      # [7, 8, 9] (last 3)
print(numbers[:-3])      # [0, 1, 2, 3, 4, 5, 6] (except last 3)
```

### Slice Assignment

```python
numbers = [0, 1, 2, 3, 4]
numbers[1:3] = [10, 20, 30]
print(numbers)  # [0, 10, 20, 30, 3, 4]

numbers[1:4] = []  # Delete elements
print(numbers)     # [0, 3, 4]
```

---

## List Comprehensions

### Basic Syntax

```python
[expression for item in iterable]
```

### Example 1: Squares

```python
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

### Example 2: With Condition

```python
evens = [x for x in range(10) if x % 2 == 0]
# [0, 2, 4, 6, 8]
```

### Example 3: String Processing

```python
words = ["hello", "world", "python"]
upper = [word.upper() for word in words]
# ['HELLO', 'WORLD', 'PYTHON']
```

### Example 4: if-else in Comprehension

```python
numbers = [1, 2, 3, 4, 5]
result = ["Even" if x % 2 == 0 else "Odd" for x in numbers]
# ['Odd', 'Even', 'Odd', 'Even', 'Odd']
```

### Example 5: Nested Comprehension

```python
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
# [[1, 2, 3], [2, 4, 6], [3, 6, 9]]
```

---

## Nested Lists

### Creating 2D Lists

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

print(matrix[0])     # [1, 2, 3]
print(matrix[1][2])  # 6
```

### Iterating 2D Lists

```python
for row in matrix:
    for element in row:
        print(element, end=" ")
    print()
```

### Flattening

```python
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [item for row in matrix for item in row]
print(flat)  # [1, 2, 3, 4, 5, 6]
```

---

## List Copying

### Shallow Copy

```python
# Method 1: copy()
original = [1, 2, 3]
copy1 = original.copy()

# Method 2: slicing
copy2 = original[:]

# Method 3: list()
copy3 = list(original)
```

### Deep Copy (Nested Lists)

```python
import copy

original = [[1, 2], [3, 4]]
shallow = original.copy()
deep = copy.deepcopy(original)

original[0][0] = 99

print(original)  # [[99, 2], [3, 4]]
print(shallow)   # [[99, 2], [3, 4]] (affected!)
print(deep)      # [[1, 2], [3, 4]] (not affected)
```

---

## Common Patterns

### 1. Finding Maximum Element

```python
numbers = [3, 1, 4, 1, 5, 9]
max_num = max(numbers)  # Built-in

# Manual
max_num = numbers[0]
for num in numbers:
    if num > max_num:
        max_num = num
```

### 2. Removing Duplicates

```python
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(numbers))  # [1, 2, 3, 4] (order not guaranteed)

# Preserve order
unique = []
for num in numbers:
    if num not in unique:
        unique.append(num)
```

### 3. Filtering

```python
numbers = [1, 2, 3, 4, 5, 6]
evens = [x for x in numbers if x % 2 == 0]  # [2, 4, 6]

# Using filter()
evens = list(filter(lambda x: x % 2 == 0, numbers))
```

### 4. Mapping

```python
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]  # [1, 4, 9, 16, 25]

# Using map()
squares = list(map(lambda x: x**2, numbers))
```

### 5. List as Stack (LIFO)

```python
stack = []
stack.append(1)  # Push
stack.append(2)
stack.append(3)
print(stack.pop())  # Pop: 3
print(stack.pop())  # Pop: 2
```

### 6. List as Queue (FIFO)

```python
from collections import deque
queue = deque()
queue.append(1)      # Enqueue
queue.append(2)
print(queue.popleft())  # Dequeue: 1
```

---

## Summary

| **Operation** | **Syntax** | **Time Complexity** |
|---------------|------------|---------------------|
| Access by index | `list[i]` | O(1) |
| Append | `list.append(x)` | O(1) |
| Insert | `list.insert(i, x)` | O(n) |
| Remove | `list.remove(x)` | O(n) |
| Pop last | `list.pop()` | O(1) |
| Pop by index | `list.pop(i)` | O(n) |
| Search | `x in list` | O(n) |
| Sort | `list.sort()` | O(n log n) |

### Key Concepts Checklist

✅ List creation methods  
✅ Indexing and slicing  
✅ List methods (append, extend, insert, remove, pop, etc.)  
✅ List comprehensions  
✅ Nested lists  
✅ Shallow vs deep copy  
✅ Common patterns (filter, map, stack, queue)  

---

## Next Steps
➡️ **Module 4: Lists Practice Questions** (20 exam-style questions)  
➡️ **Module 4: Tuples**
