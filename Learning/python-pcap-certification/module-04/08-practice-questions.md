# Module 4 Part 3: Practice Questions - Dictionaries

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
d = {"a": 1, "b": 2}
print(d["a"])
```
**A)** 1  
**B)** "a"  
**C)** {"a": 1}  
**D)** KeyError

---

### Question 2
What will be printed?
```python
d = {"a": 1}
print(d.get("b"))
```
**A)** 1  
**B)** None  
**C)** KeyError  
**D)** ""

---

### Question 3
What is the output?
```python
d = {"a": 1, "b": 2}
d["c"] = 3
print(d)
```
**A)** {"a": 1, "b": 2}  
**B)** {"a": 1, "b": 2, "c": 3}  
**C)** {"c": 3}  
**D)** Error

---

### Question 4
What will be printed?
```python
d = {"a": 1, "b": 2, "c": 3}
print(len(d))
```
**A)** 2  
**B)** 3  
**C)** 6  
**D)** Error

---

### Question 5
What is the output?
```python
d = {"a": 1, "b": 2}
del d["a"]
print(d)
```
**A)** {"a": 1, "b": 2}  
**B)** {"b": 2}  
**C)** {}  
**D)** KeyError

---

### Question 6
What will be printed?
```python
d = {"a": 1, "b": 2}
value = d.pop("b")
print(value)
```
**A)** {"a": 1}  
**B)** 2  
**C)** "b"  
**D)** None

---

### Question 7
What is the output?
```python
d = {"a": 1, "b": 2}
print(list(d.keys()))
```
**A)** [1, 2]  
**B)** ["a", "b"]  
**C)** [("a", 1), ("b", 2)]  
**D)** {"a", "b"}

---

### Question 8
What will be printed?
```python
d = {"a": 1, "b": 2}
print(list(d.values()))
```
**A)** ["a", "b"]  
**B)** [1, 2]  
**C)** [("a", 1), ("b", 2)]  
**D)** {1, 2}

---

### Question 9
What is the output?
```python
d = {"a": 1, "b": 2}
for key in d:
    print(key)
```
**A)** a b  
**B)** 1 2  
**C)** ("a", 1) ("b", 2)  
**D)** Error

---

### Question 10
What will be printed?
```python
d = {x: x**2 for x in range(3)}
print(d)
```
**A)** {0: 0, 1: 1, 2: 4}  
**B)** [0, 1, 4]  
**C)** {0, 1, 4}  
**D)** SyntaxError

---

### Question 11
What is the output?
```python
d1 = {"a": 1}
d2 = {"b": 2}
d1.update(d2)
print(d1)
```
**A)** {"a": 1}  
**B)** {"b": 2}  
**C)** {"a": 1, "b": 2}  
**D)** Error

---

### Question 12
What will be printed?
```python
d = {"a": 1, "b": 2}
print("a" in d)
```
**A)** True  
**B)** False  
**C)** 1  
**D)** "a"

---

### Question 13
What is the output?
```python
d = {}
d.setdefault("a", 10)
print(d)
```
**A)** {}  
**B)** {"a": 10}  
**C)** {"a": None}  
**D)** Error

---

### Question 14
What will be printed?
```python
d = {"a": 1, "b": 2}
d.clear()
print(d)
```
**A)** {"a": 1, "b": 2}  
**B)** None  
**C)** {}  
**D)** Error

---

### Question 15
What is the output?
```python
d = {"a": 1, "b": 2, "c": 3}
for k, v in d.items():
    print(v)
```
**A)** a b c  
**B)** 1 2 3  
**C)** (a,1) (b,2) (c,3)  
**D)** Error

---

### Question 16
What will be printed?
```python
d = dict(a=1, b=2)
print(d)
```
**A)** {"a": 1, "b": 2}  
**B)** ("a", 1, "b", 2)  
**C)** [("a", 1), ("b", 2)]  
**D)** Error

---

### Question 17
What is the output?
```python
d = dict.fromkeys(["a", "b"], 0)
print(d)
```
**A)** {"a": 0, "b": 0}  
**B)** {"a": None, "b": None}  
**C)** ["a", "b"]  
**D)** Error

---

### Question 18
What will be printed?
```python
d = {"a": 1, "b": 2}
d2 = d.copy()
d2["c"] = 3
print(len(d))
```
**A)** 2  
**B)** 3  
**C)** 0  
**D)** Error

---

### Question 19
What is the output?
```python
d = {"a": 1, "b": 2}
print(d.get("c", "default"))
```
**A)** None  
**B)** "default"  
**C)** KeyError  
**D)** ""

---

### Question 20
What will be printed?
```python
keys = ["x", "y"]
values = [1, 2]
d = dict(zip(keys, values))
print(d)
```
**A)** {"x": 1, "y": 2}  
**B)** [("x", 1), ("y", 2)]  
**C)** {"x": "y", 1: 2}  
**D)** Error

---

## Answers

### Answer 1: **A) 1**
**Explanation**: Square bracket access returns value for key "a"

---

### Answer 2: **B) None**
**Explanation**: `get()` returns None for missing keys (no error)

---

### Answer 3: **B) {"a": 1, "b": 2, "c": 3}**
**Explanation**: Adding new key-value pair to dictionary

---

### Answer 4: **B) 3**
**Explanation**: `len()` returns number of key-value pairs

---

### Answer 5: **B) {"b": 2}**
**Explanation**: `del` removes key "a" and its value

---

### Answer 6: **B) 2**
**Explanation**: `pop()` removes and returns the value

---

### Answer 7: **B) ["a", "b"]**
**Explanation**: `keys()` returns dictionary keys

---

### Answer 8: **B) [1, 2]**
**Explanation**: `values()` returns dictionary values

---

### Answer 9: **A) a b**
**Explanation**: Default iteration is over keys

---

### Answer 10: **A) {0: 0, 1: 1, 2: 4}**
**Explanation**: Dictionary comprehension creating key: square pairs

---

### Answer 11: **C) {"a": 1, "b": 2}**
**Explanation**: `update()` merges d2 into d1

---

### Answer 12: **A) True**
**Explanation**: Membership test checks if key exists

---

### Answer 13: **B) {"a": 10}**
**Explanation**: `setdefault()` adds key with default value if missing

---

### Answer 14: **C) {}**
**Explanation**: `clear()` removes all items, returns empty dict

---

### Answer 15: **B) 1 2 3**
**Explanation**: `items()` returns tuples, loop prints values

---

### Answer 16: **A) {"a": 1, "b": 2}**
**Explanation**: `dict()` with keyword arguments creates dictionary

---

### Answer 17: **A) {"a": 0, "b": 0}**
**Explanation**: `fromkeys()` creates dict with all keys having value 0

---

### Answer 18: **A) 2**
**Explanation**: `copy()` creates shallow copy, original unchanged

---

### Answer 19: **B) "default"**
**Explanation**: `get()` with default returns default for missing keys

---

### Answer 20: **A) {"x": 1, "y": 2}**
**Explanation**: `zip()` pairs elements, `dict()` creates dictionary

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 4: Sets**  
❌ **If you scored below 80**: Review dictionaries theory
