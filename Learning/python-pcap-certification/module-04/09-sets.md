# Module 4 Part 4: Sets - Complete Guide

## Table of Contents
1. [Introduction to Sets](#introduction-to-sets)
2. [Creating Sets](#creating-sets)
3. [Set Operations](#set-operations)
4. [Set Methods](#set-methods)
5. [Set Theory Operations](#set-theory-operations)
6. [Frozen Sets](#frozen-sets)
7. [Set Comprehensions](#set-comprehensions)
8. [Common Patterns](#common-patterns)

---

## Introduction to Sets

Sets are **mutable, unordered collections** of unique elements.

### Key Characteristics

- **Mutable**: Can add/remove elements (except frozenset)
- **Unordered**: No indexing or slicing
- **Unique Elements**: No duplicates allowed
- **Hashable Elements**: Only immutable types (int, str, tuple)
- **Fast Membership Testing**: O(1) average

```python
# Example
numbers = {1, 2, 3, 4, 5}
fruits = {"apple", "banana", "cherry"}
```

---

## Creating Sets

### Method 1: Curly Braces

```python
# Basic set
numbers = {1, 2, 3, 4, 5}
fruits = {"apple", "banana", "cherry"}

# Duplicates automatically removed
nums = {1, 2, 2, 3, 3, 3}
print(nums)  # {1, 2, 3}

# Empty set - MUST use set()
empty = set()  # Correct
# empty = {}   # WRONG - this is a dict!
```

### Method 2: set() Constructor

```python
# From list
nums = set([1, 2, 3, 2, 1])
print(nums)  # {1, 2, 3}

# From string
chars = set("hello")
print(chars)  # {'h', 'e', 'l', 'o'}

# From tuple
nums = set((1, 2, 3))
print(nums)  # {1, 2, 3}

# From range
evens = set(range(0, 10, 2))
print(evens)  # {0, 2, 4, 6, 8}
```

---

## Set Operations

### Adding Elements

```python
fruits = {"apple", "banana"}

# add() - Add single element
fruits.add("cherry")
print(fruits)  # {'apple', 'banana', 'cherry'}

# Adding duplicate (no effect)
fruits.add("apple")
print(fruits)  # {'apple', 'banana', 'cherry'} (unchanged)
```

### Removing Elements

```python
fruits = {"apple", "banana", "cherry"}

# remove() - Removes element, raises KeyError if not found
fruits.remove("banana")
print(fruits)  # {'apple', 'cherry'}

# fruits.remove("grape")  # KeyError!

# discard() - Removes element, no error if not found
fruits.discard("cherry")
print(fruits)  # {'apple'}

fruits.discard("grape")  # No error
print(fruits)  # {'apple'}

# pop() - Remove and return arbitrary element
fruits = {"apple", "banana", "cherry"}
item = fruits.pop()
print(item)    # e.g., 'apple' (arbitrary)
print(fruits)  # Remaining items

# clear() - Remove all elements
fruits.clear()
print(fruits)  # set()
```

### Set Size and Membership

```python
fruits = {"apple", "banana", "cherry"}

print(len(fruits))           # 3
print("apple" in fruits)     # True
print("grape" in fruits)     # False
print("grape" not in fruits) # True
```

---

## Set Methods

### 1. update() - Add Multiple Elements

```python
fruits = {"apple", "banana"}
fruits.update(["cherry", "date"])
print(fruits)  # {'apple', 'banana', 'cherry', 'date'}

# Can update with multiple iterables
fruits.update(["mango"], {"orange"}, ("grape",))
print(fruits)  # {'apple', 'banana', 'cherry', 'date', 'mango', 'orange', 'grape'}
```

### 2. copy() - Shallow Copy

```python
original = {1, 2, 3}
duplicate = original.copy()
duplicate.add(4)

print(original)   # {1, 2, 3}
print(duplicate)  # {1, 2, 3, 4}
```

---

## Set Theory Operations

### Union (|) - All Elements from Both Sets

```python
set1 = {1, 2, 3}
set2 = {3, 4, 5}

# Method 1: | operator
result = set1 | set2
print(result)  # {1, 2, 3, 4, 5}

# Method 2: union() method
result = set1.union(set2)
print(result)  # {1, 2, 3, 4, 5}

# Multiple sets
set3 = {5, 6, 7}
result = set1 | set2 | set3
print(result)  # {1, 2, 3, 4, 5, 6, 7}
```

### Intersection (&) - Common Elements

```python
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

# Method 1: & operator
result = set1 & set2
print(result)  # {3, 4}

# Method 2: intersection() method
result = set1.intersection(set2)
print(result)  # {3, 4}
```

### Difference (-) - Elements in First, Not in Second

```python
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

# Method 1: - operator
result = set1 - set2
print(result)  # {1, 2}

result = set2 - set1
print(result)  # {5, 6}

# Method 2: difference() method
result = set1.difference(set2)
print(result)  # {1, 2}
```

### Symmetric Difference (^) - Elements in Either, Not Both

```python
set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

# Method 1: ^ operator
result = set1 ^ set2
print(result)  # {1, 2, 5, 6}

# Method 2: symmetric_difference() method
result = set1.symmetric_difference(set2)
print(result)  # {1, 2, 5, 6}
```

### In-Place Operations

```python
set1 = {1, 2, 3}
set2 = {3, 4, 5}

# update() or |=
set1 |= set2  # set1 = set1 | set2
print(set1)   # {1, 2, 3, 4, 5}

# intersection_update() or &=
set1 = {1, 2, 3, 4}
set1 &= {3, 4, 5}  # set1 = set1 & {3, 4, 5}
print(set1)        # {3, 4}

# difference_update() or -=
set1 = {1, 2, 3, 4}
set1 -= {3, 4}     # set1 = set1 - {3, 4}
print(set1)        # {1, 2}

# symmetric_difference_update() or ^=
set1 = {1, 2, 3}
set1 ^= {3, 4, 5}  # set1 = set1 ^ {3, 4, 5}
print(set1)        # {1, 2, 4, 5}
```

### Subset and Superset

```python
set1 = {1, 2, 3}
set2 = {1, 2, 3, 4, 5}

# issubset() or <=
print(set1.issubset(set2))   # True
print(set1 <= set2)          # True

# issuperset() or >=
print(set2.issuperset(set1)) # True
print(set2 >= set1)          # True

# Proper subset (<) and superset (>)
print(set1 < set2)           # True (proper subset)
print(set1 == set2)          # False
```

### Disjoint Sets

```python
set1 = {1, 2, 3}
set2 = {4, 5, 6}
set3 = {3, 4, 5}

# isdisjoint() - No common elements
print(set1.isdisjoint(set2))  # True (no overlap)
print(set1.isdisjoint(set3))  # False (3 is common)
```

---

## Frozen Sets

Immutable version of sets. Can be used as dictionary keys or elements of other sets.

### Creating Frozen Sets

```python
# Basic creation
frozen = frozenset([1, 2, 3])
print(frozen)  # frozenset({1, 2, 3})

# From string
chars = frozenset("hello")
print(chars)  # frozenset({'h', 'e', 'l', 'o'})
```

### Frozen Set Properties

```python
frozen = frozenset([1, 2, 3])

# Cannot modify
# frozen.add(4)     # AttributeError
# frozen.remove(1)  # AttributeError

# Can use set operations
frozen2 = frozenset([3, 4, 5])
result = frozen | frozen2
print(result)  # frozenset({1, 2, 3, 4, 5})

# Can be dict key
d = {frozen: "value"}
print(d[frozen])  # value

# Can be set element
set_of_sets = {frozen, frozenset([4, 5, 6])}
print(set_of_sets)
```

---

## Set Comprehensions

### Basic Syntax

```python
{expression for item in iterable}
```

### Example 1: Squares

```python
squares = {x**2 for x in range(6)}
print(squares)  # {0, 1, 4, 9, 16, 25}
```

### Example 2: With Condition

```python
evens = {x for x in range(10) if x % 2 == 0}
print(evens)  # {0, 2, 4, 6, 8}
```

### Example 3: String Processing

```python
text = "Hello World"
unique_lower = {char.lower() for char in text if char.isalpha()}
print(unique_lower)  # {'h', 'e', 'l', 'o', 'w', 'r', 'd'}
```

---

## Common Patterns

### 1. Removing Duplicates

```python
numbers = [1, 2, 2, 3, 3, 3, 4, 5, 5]
unique = list(set(numbers))
print(unique)  # [1, 2, 3, 4, 5] (order not guaranteed)
```

### 2. Finding Common Elements

```python
list1 = [1, 2, 3, 4, 5]
list2 = [4, 5, 6, 7, 8]
common = set(list1) & set(list2)
print(common)  # {4, 5}
```

### 3. Finding Unique Elements

```python
list1 = [1, 2, 3, 4]
list2 = [3, 4, 5, 6]

# Only in list1
only_in_1 = set(list1) - set(list2)
print(only_in_1)  # {1, 2}

# In either, not both
unique = set(list1) ^ set(list2)
print(unique)  # {1, 2, 5, 6}
```

### 4. Membership Testing (Fast!)

```python
# List: O(n)
big_list = list(range(1000000))
print(500000 in big_list)  # Slow

# Set: O(1)
big_set = set(range(1000000))
print(500000 in big_set)  # Fast!
```

### 5. Unique Characters

```python
def has_unique_chars(text):
    return len(text) == len(set(text))

print(has_unique_chars("hello"))  # False ('l' repeats)
print(has_unique_chars("world"))  # True
```

---

## Summary

| **Operation** | **Syntax** | **Time Complexity** |
|---------------|------------|---------------------|
| Add | `set.add(x)` | O(1) average |
| Remove | `set.remove(x)` | O(1) average |
| Membership | `x in set` | O(1) average |
| Union | `set1 \| set2` | O(len(set1) + len(set2)) |
| Intersection | `set1 & set2` | O(min(len(set1), len(set2))) |
| Difference | `set1 - set2` | O(len(set1)) |

### When to Use Sets

✅ Need unique elements  
✅ Fast membership testing  
✅ Set theory operations (union, intersection, etc.)  
✅ Removing duplicates from sequences  

### Key Concepts Checklist

✅ Set creation and properties  
✅ Adding/removing elements  
✅ Set theory operations (union, intersection, difference, symmetric difference)  
✅ Subset and superset relationships  
✅ Frozen sets  
✅ Set comprehensions  
✅ Common patterns and use cases  

---

## Next Steps
➡️ **Module 4: Sets Practice Questions** (20 exam-style questions)  
➡️ **Module 5: Functions**
