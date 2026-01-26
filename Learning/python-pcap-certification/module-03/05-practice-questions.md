# Module 3 Part 3: Practice Questions - Loops

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
for i in range(3):
    print(i)
```
**A)** 1 2 3  
**B)** 0 1 2  
**C)** 0 1 2 3  
**D)** 1 2

---

### Question 2
What will be printed?
```python
count = 0
while count < 3:
    print(count)
    count += 1
```
**A)** 0 1 2  
**B)** 1 2 3  
**C)** 0 1 2 3  
**D)** Infinite loop

---

### Question 3
What is the output?
```python
for i in range(2, 5):
    print(i)
```
**A)** 2 3 4  
**B)** 2 3 4 5  
**C)** 3 4 5  
**D)** 2 3

---

### Question 4
What will be printed?
```python
for i in range(10, 0, -2):
    print(i)
```
**A)** 10 8 6 4 2  
**B)** 10 8 6 4 2 0  
**C)** 8 6 4 2 0  
**D)** 10 9 8...1

---

### Question 5
What is the output?
```python
for i in range(5):
    if i == 3:
        break
    print(i)
```
**A)** 0 1 2  
**B)** 0 1 2 3  
**C)** 0 1 2 3 4  
**D)** 1 2 3

---

### Question 6
What will be printed?
```python
for i in range(5):
    if i % 2 == 0:
        continue
    print(i)
```
**A)** 0 2 4  
**B)** 1 3  
**C)** 0 1 2 3 4  
**D)** 2 4

---

### Question 7
What is the output?
```python
for i in range(3):
    print(i)
else:
    print("Done")
```
**A)** 0 1 2  
**B)** 0 1 2 Done  
**C)** Done  
**D)** SyntaxError

---

### Question 8
What will be printed?
```python
for i in range(5):
    if i == 2:
        break
else:
    print("Complete")
```
**A)** Complete  
**B)** 0 1 Complete  
**C)** Nothing  
**D)** 0 1 2

---

### Question 9
What is the output?
```python
count = 3
while count > 0:
    print(count)
    count -= 1
```
**A)** 3 2 1  
**B)** 3 2 1 0  
**C)** 2 1 0  
**D)** Infinite loop

---

### Question 10
What will be printed?
```python
for char in "Hi":
    print(char)
```
**A)** Hi  
**B)** H i  
**C)** H (newline) i  
**D)** SyntaxError

---

### Question 11
What is the output?
```python
nums = [1, 2, 3]
for i in nums:
    print(i * 2)
```
**A)** 1 2 3  
**B)** 2 4 6  
**C)** [2, 4, 6]  
**D)** 11 22 33

---

### Question 12
What will be printed?
```python
for i in range(0, 10, 3):
    print(i)
```
**A)** 0 3 6 9  
**B)** 0 3 6 9 12  
**C)** 3 6 9  
**D)** 0 3 6

---

### Question 13
What is the output?
```python
i = 0
while i < 3:
    i += 1
print(i)
```
**A)** 0  
**B)** 1  
**C)** 2  
**D)** 3

---

### Question 14
What will be printed?
```python
for i in range(3):
    for j in range(2):
        print(i, j)
```
**A)** 6 lines of output  
**B)** 5 lines of output  
**C)** 2 lines of output  
**D)** Error

---

### Question 15
What is the output?
```python
for i in [1, 2, 3]:
    pass
print("Done")
```
**A)** 1 2 3 Done  
**B)** Done  
**C)** Nothing  
**D)** Error

---

### Question 16
What will be printed?
```python
total = 0
for i in range(1, 4):
    total += i
print(total)
```
**A)** 3  
**B)** 6  
**C)** 10  
**D)** 0

---

### Question 17
What is the output?
```python
while False:
    print("Hello")
print("World")
```
**A)** Hello World  
**B)** World  
**C)** Hello  
**D)** Nothing

---

### Question 18
What will be printed?
```python
for i in range(5, 5):
    print(i)
print("End")
```
**A)** 5 End  
**B)** End  
**C)** 5  
**D)** Nothing

---

### Question 19
What is the output?
```python
n = 5
while n:
    print(n)
    n -= 1
```
**A)** 5 4 3 2 1  
**B)** 5 4 3 2 1 0  
**C)** 4 3 2 1 0  
**D)** Infinite loop

---

### Question 20
What will be printed?
```python
for i in range(3):
    if i == 1:
        continue
    print(i)
print("Done")
```
**A)** 0 2 Done  
**B)** 0 1 2 Done  
**C)** 1 Done  
**D)** 0 2

---

## Answers

### Answer 1: **B) 0 1 2**
**Explanation**: `range(3)` generates 0, 1, 2 (stop value excluded)

---

### Answer 2: **A) 0 1 2**
**Explanation**: Loop runs while count < 3, printing 0, 1, 2

---

### Answer 3: **A) 2 3 4**
**Explanation**: `range(2, 5)` generates 2, 3, 4 (5 excluded)

---

### Answer 4: **A) 10 8 6 4 2**
**Explanation**: Start=10, stop=0 (excluded), step=-2

---

### Answer 5: **A) 0 1 2**
**Explanation**: Loop breaks when i==3, so prints 0, 1, 2

---

### Answer 6: **B) 1 3**
**Explanation**: `continue` skips even numbers (0, 2, 4), prints odd (1, 3)

---

### Answer 7: **B) 0 1 2 Done**
**Explanation**: Loop completes normally, else executes

---

### Answer 8: **C) Nothing**
**Explanation**: Loop breaks at i==2, else doesn't execute after break

---

### Answer 9: **A) 3 2 1**
**Explanation**: Counts down from 3 to 1, stops when count=0 (falsy)

---

### Answer 10: **C) H (newline) i**
**Explanation**: Each character printed on new line by default

---

### Answer 11: **B) 2 4 6**
**Explanation**: Each element multiplied by 2: 1*2=2, 2*2=4, 3*2=6

---

### Answer 12: **A) 0 3 6 9**
**Explanation**: Start=0, step=3, stop=10 (excluded): 0, 3, 6, 9

---

### Answer 13: **D) 3**
**Explanation**: Loop runs 3 times (i=1,2,3), final value is 3

---

### Answer 14: **A) 6 lines of output**
**Explanation**: Outer loop 3 times × inner loop 2 times = 6 iterations

---

### Answer 15: **B) Done**
**Explanation**: `pass` does nothing, loop completes, prints "Done"

---

### Answer 16: **B) 6**
**Explanation**: 0 + 1 + 2 + 3 = 6

---

### Answer 17: **B) World**
**Explanation**: `False` condition → while body never executes

---

### Answer 18: **B) End**
**Explanation**: `range(5, 5)` is empty, loop doesn't run

---

### Answer 19: **A) 5 4 3 2 1**
**Explanation**: `n` becomes 0 (falsy) after 5 iterations

---

### Answer 20: **A) 0 2 Done**
**Explanation**: Skips i=1 via continue, prints 0, 2, Done

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 4: Lists**  
❌ **If you scored below 80**: Review loops theory and practice more
