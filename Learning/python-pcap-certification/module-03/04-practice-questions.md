# Module 3 Part 2: Practice Questions - Conditional Statements

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
x = 5
if x > 3:
    print("A")
if x > 7:
    print("B")
else:
    print("C")
```
**A)** A  
**B)** A C  
**C)** B  
**D)** C

---

### Question 2
What will be printed?
```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
print(grade)
```
**A)** A  
**B)** B  
**C)** C  
**D)** NameError

---

### Question 3
What is the output?
```python
x = 10
result = "Even" if x % 2 == 0 else "Odd"
print(result)
```
**A)** Even  
**B)** Odd  
**C)** True  
**D)** SyntaxError

---

### Question 4
What will be printed?
```python
if 0:
    print("True")
else:
    print("False")
```
**A)** True  
**B)** False  
**C)** 0  
**D)** Nothing

---

### Question 5
What is the output?
```python
age = 16
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teen")
elif age >= 5:
    print("Child")
else:
    print("Toddler")
```
**A)** Adult  
**B)** Teen  
**C)** Child  
**D)** Toddler

---

### Question 6
What will be printed?
```python
x, y = 5, 10
if x > y:
    print("X")
elif x < y:
    print("Y")
elif x == y:
    print("Equal")
```
**A)** X  
**B)** Y  
**C)** Equal  
**D)** Nothing

---

### Question 7
What is the output?
```python
num = 0
if num:
    print("Truthy")
else:
    print("Falsy")
```
**A)** Truthy  
**B)** Falsy  
**C)** 0  
**D)** Error

---

### Question 8
What will be printed?
```python
x = 5
if x > 0:
    if x < 10:
        print("Between 0 and 10")
else:
    print("Not in range")
```
**A)** Between 0 and 10  
**B)** Not in range  
**C)** Nothing  
**D)** Error

---

### Question 9
What is the output?
```python
status = True
message = "Active" if status else "Inactive"
print(message)
```
**A)** Active  
**B)** Inactive  
**C)** True  
**D)** status

---

### Question 10
What will be printed?
```python
x = []
if x:
    print("Has items")
else:
    print("Empty")
```
**A)** Has items  
**B)** Empty  
**C)** []  
**D)** Error

---

### Question 11
What is the output?
```python
age = 25
if age >= 18 and age < 65:
    print("Working age")
```
**A)** Working age  
**B)** Nothing  
**C)** True  
**D)** Error

---

### Question 12
What will be printed?
```python
x = 10
y = 5
max_val = x if x > y else y
print(max_val)
```
**A)** 10  
**B)** 5  
**C)** True  
**D)** x

---

### Question 13
What is the output?
```python
num = 15
if 10 < num < 20:
    print("In range")
else:
    print("Out of range")
```
**A)** In range  
**B)** Out of range  
**C)** True  
**D)** SyntaxError

---

### Question 14
What will be printed?
```python
if False or True and False:
    print("A")
else:
    print("B")
```
**A)** A  
**B)** B  
**C)** True  
**D)** False

---

### Question 15
What is the output?
```python
x = 5
if x:
    if x > 3:
        print("Greater")
```
**A)** Greater  
**B)** 5  
**C)** True  
**D)** Nothing

---

### Question 16
What will be printed?
```python
password = ""
if not password:
    print("Enter password")
else:
    print("Valid")
```
**A)** Enter password  
**B)** Valid  
**C)** False  
**D)** Nothing

---

### Question 17
What is the output?
```python
x = 7
if x % 2:
    print("Odd")
else:
    print("Even")
```
**A)** Odd  
**B)** Even  
**C)** 1  
**D)** 7

---

### Question 18
What will be printed?
```python
score = 95
if score >= 90:
    print("A")
if score >= 80:
    print("B")
```
**A)** A  
**B)** B  
**C)** A B  
**D)** Nothing

---

### Question 19
What is the output?
```python
x = None
if x is None:
    print("Null")
else:
    print("Value")
```
**A)** Null  
**B)** Value  
**C)** None  
**D)** Error

---

### Question 20
What will be printed?
```python
num = 100
result = "Big" if num > 100 else "Small" if num < 100 else "Equal"
print(result)
```
**A)** Big  
**B)** Small  
**C)** Equal  
**D)** SyntaxError

---

## Answers

### Answer 1: **B) A C**
**Explanation**: Two separate if statements:
- First if: `5 > 3` is True → prints "A"
- Second if-else: `5 > 7` is False → prints "C"

---

### Answer 2: **B) B**
**Explanation**: 
- `85 >= 90` → False
- `85 >= 80` → True → grade = "B" (stops here)

---

### Answer 3: **A) Even**
**Explanation**: Ternary operator:
- `10 % 2 == 0` → True
- Returns "Even"

---

### Answer 4: **B) False**
**Explanation**: `0` is falsy in Python → executes else block

---

### Answer 5: **B) Teen**
**Explanation**:
- `16 >= 18` → False
- `16 >= 13` → True → prints "Teen"

---

### Answer 6: **B) Y**
**Explanation**:
- `5 > 10` → False
- `5 < 10` → True → prints "Y"
- Third elif never checked

---

### Answer 7: **B) Falsy**
**Explanation**: `0` is a falsy value → executes else

---

### Answer 8: **A) Between 0 and 10**
**Explanation**: Both conditions true:
- `5 > 0` → True
- `5 < 10` → True

---

### Answer 9: **A) Active**
**Explanation**: `True` is truthy → returns "Active"

---

### Answer 10: **B) Empty**
**Explanation**: Empty list `[]` is falsy

---

### Answer 11: **A) Working age**
**Explanation**: Both conditions true:
- `25 >= 18` → True
- `25 < 65` → True

---

### Answer 12: **A) 10**
**Explanation**:
- `10 > 5` → True
- Returns x which is 10

---

### Answer 13: **A) In range**
**Explanation**: Chained comparison:
- `10 < 15 < 20` → True

---

### Answer 14: **B) B**
**Explanation**: Operator precedence (and before or):
- `True and False` → False
- `False or False` → False
- Executes else

---

### Answer 15: **A) Greater**
**Explanation**: Both nested conditions true

---

### Answer 16: **A) Enter password**
**Explanation**: 
- `not ""` → True (empty string is falsy)

---

### Answer 17: **A) Odd**
**Explanation**:
- `7 % 2` → 1 (truthy)
- Executes if block

---

### Answer 18: **C) A B**
**Explanation**: Two independent if statements:
- `95 >= 90` → prints "A"
- `95 >= 80` → prints "B"

---

### Answer 19: **A) Null**
**Explanation**: `None is None` → True

---

### Answer 20: **C) Equal**
**Explanation**: Nested ternary:
- `100 > 100` → False
- `100 < 100` → False
- Returns "Equal"

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 3: Loops**  
❌ **If you scored below 80**: Review conditional statements theory
