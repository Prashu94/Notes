# Module 4 Part 2: Practice Questions - Tuples

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
t = (1, 2, 3)
print(type(t))
```
**A)** <class 'list'>  
**B)** <class 'tuple'>  
**C)** <class 'set'>  
**D)** <class 'dict'>

---

### Question 2
What will be printed?
```python
t = (5)
print(type(t))
```
**A)** <class 'tuple'>  
**B)** <class 'int'>  
**C)** <class 'str'>  
**D)** Error

---

### Question 3
What is the output?
```python
t = (5,)
print(type(t))
```
**A)** <class 'int'>  
**B)** <class 'tuple'>  
**C)** <class 'list'>  
**D)** Error

---

### Question 4
What will be printed?
```python
t = (1, 2, 3)
t[0] = 99
print(t)
```
**A)** (99, 2, 3)  
**B)** (1, 2, 3)  
**C)** TypeError  
**D)** Error

---

### Question 5
What is the output?
```python
t = (1, 2, 3, 4, 5)
print(t[1:4])
```
**A)** (1, 2, 3, 4)  
**B)** (2, 3, 4)  
**C)** (2, 3, 4, 5)  
**D)** [2, 3, 4]

---

### Question 6
What will be printed?
```python
t = (1, 2, 3, 2, 4, 2)
print(t.count(2))
```
**A)** 1  
**B)** 2  
**C)** 3  
**D)** 4

---

### Question 7
What is the output?
```python
t = ("a", "b", "c", "b")
print(t.index("b"))
```
**A)** 1  
**B)** 3  
**C)** [1, 3]  
**D)** Error

---

### Question 8
What will be printed?
```python
t1 = (1, 2)
t2 = (3, 4)
t3 = t1 + t2
print(t3)
```
**A)** (1, 2, 3, 4)  
**B)** [(1, 2), (3, 4)]  
**C)** (4, 6)  
**D)** Error

---

### Question 9
What is the output?
```python
t = (1, 2) * 3
print(t)
```
**A)** (1, 2, 3)  
**B)** (1, 2, 1, 2, 1, 2)  
**C)** (3, 6)  
**D)** Error

---

### Question 10
What will be printed?
```python
x, y = (10, 20)
print(x)
```
**A)** (10, 20)  
**B)** 10  
**C)** 20  
**D)** Error

---

### Question 11
What is the output?
```python
a, b, c = (1, 2, 3, 4)
print(a)
```
**A)** 1  
**B)** (1, 2, 3)  
**C)** ValueError  
**D)** None

---

### Question 12
What will be printed?
```python
first, *rest = (1, 2, 3, 4)
print(rest)
```
**A)** (2, 3, 4)  
**B)** [2, 3, 4]  
**C)** 2  
**D)** Error

---

### Question 13
What is the output?
```python
t = (1, 2, 3)
print(len(t))
```
**A)** 2  
**B)** 3  
**C)** 4  
**D)** Error

---

### Question 14
What will be printed?
```python
t = (5, 2, 8, 1, 9)
print(max(t))
```
**A)** 5  
**B)** 9  
**C)** 1  
**D)** Error

---

### Question 15
What is the output?
```python
t = (1, 2, 3)
print(2 in t)
```
**A)** True  
**B)** False  
**C)** 1  
**D)** Error

---

### Question 16
What will be printed?
```python
t = tuple([1, 2, 3])
print(t)
```
**A)** [1, 2, 3]  
**B)** (1, 2, 3)  
**C)** {1, 2, 3}  
**D)** Error

---

### Question 17
What is the output?
```python
t = (1, 2, 3, 4, 5)
print(t[::-1])
```
**A)** (1, 2, 3, 4, 5)  
**B)** (5, 4, 3, 2, 1)  
**C)** [5, 4, 3, 2, 1]  
**D)** Error

---

### Question 18
What will be printed?
```python
t = ()
print(len(t))
```
**A)** 0  
**B)** 1  
**C)** None  
**D)** Error

---

### Question 19
What is the output?
```python
a = 5
b = 10
a, b = b, a
print(a)
```
**A)** 5  
**B)** 10  
**C)** (5, 10)  
**D)** Error

---

### Question 20
What will be printed?
```python
t = tuple("Hi")
print(t)
```
**A)** ('Hi',)  
**B)** ('H', 'i')  
**C)** 'Hi'  
**D)** Error

---

## Answers

### Answer 1: **B) <class 'tuple'>**
**Explanation**: Parentheses create a tuple

---

### Answer 2: **B) <class 'int'>**
**Explanation**: Without comma, it's just an integer in parentheses, not a tuple

---

### Answer 3: **B) <class 'tuple'>**
**Explanation**: Comma makes it a single-element tuple

---

### Answer 4: **C) TypeError**
**Explanation**: Tuples are immutable, cannot modify elements

---

### Answer 5: **B) (2, 3, 4)**
**Explanation**: Slice from index 1 to 4 (exclusive), returns tuple

---

### Answer 6: **C) 3**
**Explanation**: `count()` returns number of occurrences, 2 appears 3 times

---

### Answer 7: **A) 1**
**Explanation**: `index()` returns first occurrence position

---

### Answer 8: **A) (1, 2, 3, 4)**
**Explanation**: Concatenation creates new tuple

---

### Answer 9: **B) (1, 2, 1, 2, 1, 2)**
**Explanation**: Repetition operator repeats tuple 3 times

---

### Answer 10: **B) 10**
**Explanation**: Tuple unpacking, x gets first value

---

### Answer 11: **C) ValueError**
**Explanation**: Too many values to unpack (4 values, 3 variables)

---

### Answer 12: **B) [2, 3, 4]**
**Explanation**: Extended unpacking, `*rest` creates a list (not tuple)

---

### Answer 13: **B) 3**
**Explanation**: `len()` returns number of elements

---

### Answer 14: **B) 9**
**Explanation**: `max()` returns largest element

---

### Answer 15: **A) True**
**Explanation**: Membership test, 2 is in the tuple

---

### Answer 16: **B) (1, 2, 3)**
**Explanation**: `tuple()` constructor converts list to tuple

---

### Answer 17: **B) (5, 4, 3, 2, 1)**
**Explanation**: Slice with step -1 reverses tuple

---

### Answer 18: **A) 0**
**Explanation**: Empty tuple has length 0

---

### Answer 19: **B) 10**
**Explanation**: Tuple unpacking swaps values, a becomes 10

---

### Answer 20: **B) ('H', 'i')**
**Explanation**: `tuple()` converts string to tuple of characters

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 4: Dictionaries**  
❌ **If you scored below 80**: Review tuples theory and practice more
