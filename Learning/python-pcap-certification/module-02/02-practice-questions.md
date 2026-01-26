# Module 2: Practice Questions - Numbers and Operators

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output of the following code?
```python
print(7 // 2)
print(7 / 2)
```
**A)** 3 and 3  
**B)** 3.5 and 3.5  
**C)** 3 and 3.5  
**D)** 3.0 and 3.5

---

### Question 2
What is the result of: `print(-7 % 3)`
**A)** -1  
**B)** 1  
**C)** 2  
**D)** -2

---

### Question 3
What will be the output?
```python
print(2 ** 3 ** 2)
```
**A)** 64  
**B)** 512  
**C)** 256  
**D)** SyntaxError

---

### Question 4
What is the value of `x` after this code?
```python
x = 10
x += 5
x *= 2
```
**A)** 25  
**B)** 30  
**C)** 20  
**D)** 40

---

### Question 5
What will be printed?
```python
print(bool(0))
print(bool(""))
print(bool([]))
```
**A)** True, True, True  
**B)** False, False, False  
**C)** True, False, False  
**D)** False, True, True

---

### Question 6
What is the output?
```python
print(5 and 10)
print(0 or 20)
```
**A)** True, True  
**B)** 10, 20  
**C)** 5, 0  
**D)** False, 20

---

### Question 7
What is the result of: `print(10 & 12)`
**A)** 2  
**B)** 8  
**C)** 14  
**D)** 22

---

### Question 8
What will be the output?
```python
print(5 << 2)
```
**A)** 7  
**B)** 10  
**C)** 20  
**D)** 2.5

---

### Question 9
What is the result?
```python
print(1 < 2 < 3)
print(1 < 2 > 3)
```
**A)** True, True  
**B)** True, False  
**C)** False, False  
**D)** SyntaxError

---

### Question 10
What will be printed?
```python
print(5 == 5.0)
print(5 is 5.0)
```
**A)** True, True  
**B)** False, False  
**C)** True, False  
**D)** False, True

---

### Question 11
What is the output?
```python
print(round(2.5))
print(round(3.5))
```
**A)** 2, 3  
**B)** 3, 4  
**C)** 2, 4  
**D)** 3, 3

---

### Question 12
What will be the result?
```python
x = 5
y = 2
print(x ** y)
```
**A)** 7  
**B)** 10  
**C)** 25  
**D)** 32

---

### Question 13
What is the output?
```python
print(True + True + False)
```
**A)** 2  
**B)** True  
**C)** 1  
**D)** TypeError

---

### Question 14
What will be printed?
```python
print(not (5 > 3 and 2 < 4))
```
**A)** True  
**B)** False  
**C)** None  
**D)** SyntaxError

---

### Question 15
What is the result?
```python
print(10 | 12)
```
**A)** 2  
**B)** 8  
**C)** 14  
**D)** 22

---

### Question 16
What will be the output?
```python
print(int(3.9))
print(int(-3.9))
```
**A)** 4, -4  
**B)** 3, -3  
**C)** 3, -4  
**D)** 4, -3

---

### Question 17
What is the result?
```python
print(5 // 2.0)
```
**A)** 2  
**B)** 2.0  
**C)** 2.5  
**D)** 3.0

---

### Question 18
What will be printed?
```python
import math
print(math.ceil(3.2))
print(math.floor(3.8))
```
**A)** 3, 3  
**B)** 4, 3  
**C)** 4, 4  
**D)** 3, 4

---

### Question 19
What is the output?
```python
x = 5
print(x & 1 == 0)
```
**A)** True  
**B)** False  
**C)** 1  
**D)** 0

---

### Question 20
What will be the result?
```python
print(divmod(17, 5))
```
**A)** (3, 2)  
**B)** (2, 3)  
**C)** 3.4  
**D)** TypeError

---

## Answers

### Answer 1: **C) 3 and 3.5**
**Explanation**: 
- `//` is **floor division** (integer division): `7 // 2 = 3`
- `/` is **regular division** (always returns float): `7 / 2 = 3.5`

---

### Answer 2: **C) 2**
**Explanation**: In Python, the modulo result has the **sign of the divisor** (second operand).
```python
-7 % 3 = 2
# Because: -7 = 3 × (-3) + 2
```

---

### Answer 3: **B) 512**
**Explanation**: Exponentiation is **right-associative**:
```python
2 ** 3 ** 2 = 2 ** (3 ** 2) = 2 ** 9 = 512
```
Not `(2 ** 3) ** 2 = 8 ** 2 = 64`

---

### Answer 4: **B) 30**
**Explanation**: 
```python
x = 10
x += 5   # x = 10 + 5 = 15
x *= 2   # x = 15 * 2 = 30
```

---

### Answer 5: **B) False, False, False**
**Explanation**: All three are **falsy values**:
- `bool(0)` → False
- `bool("")` → False (empty string)
- `bool([])` → False (empty list)

---

### Answer 6: **B) 10, 20**
**Explanation**: 
- `5 and 10` → Returns second value if first is truthy: **10**
- `0 or 20` → Returns first truthy value: **20**

Logical operators with non-boolean values return the actual values, not True/False.

---

### Answer 7: **B) 8**
**Explanation**: Bitwise AND:
```
  1010 (10)
& 1100 (12)
------
  1000 (8)
```

---

### Answer 8: **C) 20**
**Explanation**: Left shift multiplies by 2^n:
```python
5 << 2 = 5 × 2² = 5 × 4 = 20
```

---

### Answer 9: **B) True, False**
**Explanation**: Comparison chaining:
- `1 < 2 < 3` → `(1 < 2) and (2 < 3)` → True
- `1 < 2 > 3` → `(1 < 2) and (2 > 3)` → False

---

### Answer 10: **C) True, False**
**Explanation**: 
- `==` compares **values**: 5 and 5.0 are equal → True
- `is` compares **identity** (same object): different types → False

---

### Answer 11: **C) 2, 4**
**Explanation**: Python uses **banker's rounding** (round half to even):
- `round(2.5)` → 2 (even)
- `round(3.5)` → 4 (even)

---

### Answer 12: **C) 25**
**Explanation**: `**` is the exponentiation operator:
```python
5 ** 2 = 5² = 25
```

---

### Answer 13: **A) 2**
**Explanation**: Booleans are subclass of int:
- `True` = 1
- `False` = 0
- `1 + 1 + 0 = 2`

---

### Answer 14: **B) False**
**Explanation**: 
```python
5 > 3 → True
2 < 4 → True
True and True → True
not True → False
```

---

### Answer 15: **C) 14**
**Explanation**: Bitwise OR:
```
  1010 (10)
| 1100 (12)
------
  1110 (14)
```

---

### Answer 16: **B) 3, -3**
**Explanation**: `int()` **truncates** toward zero (removes decimal part):
- `int(3.9)` → 3
- `int(-3.9)` → -3

Not rounding! Use `round()` for rounding.

---

### Answer 17: **B) 2.0**
**Explanation**: Floor division with float operand returns float:
```python
5 // 2.0 = 2.0
```
If both operands were int, result would be int.

---

### Answer 18: **B) 4, 3**
**Explanation**: 
- `math.ceil(3.2)` → Ceiling (rounds up) → 4
- `math.floor(3.8)` → Floor (rounds down) → 3

---

### Answer 19: **B) False**
**Explanation**: 
```python
x & 1  # Checks last bit: 5 = 0b101, last bit is 1
1 == 0 # False
```
This checks if number is even (last bit = 0).

---

### Answer 20: **A) (3, 2)**
**Explanation**: `divmod(a, b)` returns `(quotient, remainder)`:
```python
17 ÷ 5 = 3 remainder 2
divmod(17, 5) = (3, 2)
```

---

## Scoring Guide

**Your Score: ___ / 100**

- **90-100**: Excellent! Move to Module 2 Part 2
- **80-89**: Good! Review bitwise operations
- **70-79**: Fair. Re-read division and modulo sections
- **Below 70**: Study the module again

---

## Key Concepts to Review

### Most Commonly Missed:
1. **Floor division vs regular division**: `//` vs `/`
2. **Modulo with negative numbers**: Sign follows divisor
3. **Exponentiation associativity**: Right-to-left
4. **Logical operators returning values**: Not just True/False
5. **Bitwise operations**: AND, OR, XOR, shifts
6. **Banker's rounding**: Round half to even
7. **int() truncates**: Doesn't round

---

## Next Steps

✅ **If you scored 80+**: Proceed to **Module 2 Part 2: Strings**  
❌ **If you scored below 80**: Review [theory](./02-numbers-and-operators.md) and retake

---

**Keep practicing! 🐍**
