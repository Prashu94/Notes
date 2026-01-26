# Module 4 Part 4: Practice Questions - Sets

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
s = {1, 2, 3, 2, 1}
print(s)
```
**A)** {1, 2, 3, 2, 1}  
**B)** {1, 2, 3}  
**C)** [1, 2, 3]  
**D)** Error

---

### Question 2
What will be printed?
```python
s = {}
print(type(s))
```
**A)** <class 'set'>  
**B)** <class 'dict'>  
**C)** <class 'list'>  
**D)** Error

---

### Question 3
What is the output?
```python
s = {1, 2, 3}
s.add(4)
print(s)
```
**A)** {1, 2, 3, 4}  
**B)** {1, 2, 3, [4]}  
**C)** Error  
**D)** {4, 1, 2, 3}

---

### Question 4
What will be printed?
```python
s = {1, 2, 3}
s.remove(2)
print(s)
```
**A)** {1, 3}  
**B)** {1, 2, 3}  
**C)** {2}  
**D)** Error

---

### Question 5
What is the output?
```python
s = {1, 2, 3}
s.discard(5)
print(len(s))
```
**A)** 2  
**B)** 3  
**C)** KeyError  
**D)** 4

---

### Question 6
What will be printed?
```python
s1 = {1, 2, 3}
s2 = {3, 4, 5}
print(s1 | s2)
```
**A)** {1, 2, 3, 4, 5}  
**B)** {3}  
**C)** {1, 2, 4, 5}  
**D)** Error

---

### Question 7
What is the output?
```python
s1 = {1, 2, 3, 4}
s2 = {3, 4, 5, 6}
print(s1 & s2)
```
**A)** {1, 2, 5, 6}  
**B)** {3, 4}  
**C)** {1, 2, 3, 4, 5, 6}  
**D)** Error

---

### Question 8
What will be printed?
```python
s1 = {1, 2, 3}
s2 = {3, 4, 5}
print(s1 - s2)
```
**A)** {1, 2}  
**B)** {4, 5}  
**C)** {3}  
**D)** {1, 2, 4, 5}

---

### Question 9
What is the output?
```python
s1 = {1, 2, 3}
s2 = {3, 4, 5}
print(s1 ^ s2)
```
**A)** {3}  
**B)** {1, 2, 4, 5}  
**C)** {1, 2, 3, 4, 5}  
**D)** Error

---

### Question 10
What will be printed?
```python
s = set("hello")
print(len(s))
```
**A)** 5  
**B)** 4  
**C)** 3  
**D)** Error

---

### Question 11
What is the output?
```python
s1 = {1, 2}
s2 = {1, 2, 3, 4}
print(s1.issubset(s2))
```
**A)** True  
**B)** False  
**C)** {1, 2}  
**D)** Error

---

### Question 12
What will be printed?
```python
s1 = {1, 2, 3}
s2 = {4, 5, 6}
print(s1.isdisjoint(s2))
```
**A)** True  
**B)** False  
**C)** {}  
**D)** Error

---

### Question 13
What is the output?
```python
s = {x**2 for x in range(4)}
print(s)
```
**A)** [0, 1, 4, 9]  
**B)** {0, 1, 4, 9}  
**C)** (0, 1, 4, 9)  
**D)** Error

---

### Question 14
What will be printed?
```python
s = {1, 2, 3}
s.clear()
print(len(s))
```
**A)** 0  
**B)** 3  
**C)** None  
**D)** Error

---

### Question 15
What is the output?
```python
numbers = [1, 2, 2, 3, 3, 3]
unique = set(numbers)
print(len(unique))
```
**A)** 6  
**B)** 3  
**C)** 4  
**D)** Error

---

### Question 16
What will be printed?
```python
s = {1, 2, 3}
print(2 in s)
```
**A)** True  
**B)** False  
**C)** 1  
**D)** Error

---

### Question 17
What is the output?
```python
s = frozenset([1, 2, 3])
s.add(4)
print(s)
```
**A)** frozenset({1, 2, 3, 4})  
**B)** AttributeError  
**C)** {1, 2, 3, 4}  
**D)** TypeError

---

### Question 18
What will be printed?
```python
s1 = {1, 2, 3}
s2 = s1.copy()
s2.add(4)
print(len(s1))
```
**A)** 3  
**B)** 4  
**C)** 0  
**D)** Error

---

### Question 19
What is the output?
```python
s = {1, 2, 3}
s.update([4, 5])
print(len(s))
```
**A)** 3  
**B)** 5  
**C)** 7  
**D)** Error

---

### Question 20
What will be printed?
```python
s1 = {1, 2, 3, 4}
s2 = {3, 4}
print(s2 <= s1)
```
**A)** True  
**B)** False  
**C)** {3, 4}  
**D)** Error

---

## Answers

### Answer 1: **B) {1, 2, 3}**
**Explanation**: Sets automatically remove duplicates

---

### Answer 2: **B) <class 'dict'>**
**Explanation**: `{}` creates empty dictionary, not set. Use `set()` for empty set

---

### Answer 3: **A) {1, 2, 3, 4}**
**Explanation**: `add()` adds single element (order may vary)

---

### Answer 4: **A) {1, 3}**
**Explanation**: `remove()` removes element from set

---

### Answer 5: **B) 3**
**Explanation**: `discard()` doesn't raise error for missing elements

---

### Answer 6: **A) {1, 2, 3, 4, 5}**
**Explanation**: `|` is union operator, combines all unique elements

---

### Answer 7: **B) {3, 4}**
**Explanation**: `&` is intersection operator, returns common elements

---

### Answer 8: **A) {1, 2}**
**Explanation**: `-` is difference operator, elements in s1 but not in s2

---

### Answer 9: **B) {1, 2, 4, 5}**
**Explanation**: `^` is symmetric difference, elements in either but not both

---

### Answer 10: **B) 4**
**Explanation**: "hello" has 4 unique characters: {'h', 'e', 'l', 'o'}

---

### Answer 11: **A) True**
**Explanation**: s1 is subset of s2 (all elements of s1 are in s2)

---

### Answer 12: **A) True**
**Explanation**: Disjoint means no common elements

---

### Answer 13: **B) {0, 1, 4, 9}**
**Explanation**: Set comprehension creates set of squares

---

### Answer 14: **A) 0**
**Explanation**: `clear()` removes all elements

---

### Answer 15: **B) 3**
**Explanation**: Set removes duplicates, only {1, 2, 3} remain

---

### Answer 16: **A) True**
**Explanation**: Membership test, 2 is in the set

---

### Answer 17: **B) AttributeError**
**Explanation**: Frozen sets are immutable, no `add()` method

---

### Answer 18: **A) 3**
**Explanation**: `copy()` creates independent copy, s1 unchanged

---

### Answer 19: **B) 5**
**Explanation**: `update()` adds multiple elements: {1, 2, 3, 4, 5}

---

### Answer 20: **A) True**
**Explanation**: `<=` checks if s2 is subset of s1 (it is)

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 5: Functions**  
❌ **If you scored below 80**: Review sets theory and practice more
