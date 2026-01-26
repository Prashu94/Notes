# Module 6 Part 1: Practice Questions - Modules

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
import math
print(math.sqrt(25))
```
**A)** 5.0  
**B)** 25  
**C)** 5  
**D)** Error

---

### Question 2
What will be printed?
```python
from math import pi
print(pi)
```
**A)** 3.141592653589793  
**B)** math.pi  
**C)** NameError  
**D)** Error

---

### Question 3
What is the output?
```python
import math as m
print(m.ceil(4.3))
```
**A)** 5  
**B)** 4  
**C)** 4.3  
**D)** Error

---

### Question 4
What will be printed?
```python
# mymodule.py contains: x = 10
import mymodule
print(mymodule.x)
```
**A)** 10  
**B)** x  
**C)** NameError  
**D)** Error

---

### Question 5
What is the output when running script directly?
```python
# script.py
if __name__ == "__main__":
    print("Direct")
else:
    print("Imported")
```
**A)** Direct  
**B)** Imported  
**C)** Nothing  
**D)** Error

---

### Question 6
What will be printed?
```python
import random
random.seed(42)
print(type(random.random()))
```
**A)** <class 'float'>  
**B)** <class 'int'>  
**C)** <class 'random'>  
**D)** Error

---

### Question 7
What is the output?
```python
import sys
print(type(sys.argv))
```
**A)** <class 'list'>  
**B)** <class 'tuple'>  
**C)** <class 'str'>  
**D)** Error

---

### Question 8
What will be printed?
```python
from math import sqrt, pi
print(sqrt(pi))
```
**A)** A float value around 1.77  
**B)** Error  
**C)** None  
**D)** sqrt(pi)

---

### Question 9
What is the output?
```python
import random
numbers = [1, 2, 3, 4, 5]
print(random.choice(numbers))
```
**A)** One of: 1, 2, 3, 4, or 5  
**B)** [1, 2, 3, 4, 5]  
**C)** TypeError  
**D)** Error

---

### Question 10
What will be printed?
```python
import math
print('pi' in dir(math))
```
**A)** True  
**B)** False  
**C)** 'pi'  
**D)** Error

---

### Question 11
What is the output?
```python
# When mymodule.py is imported (not run directly)
# mymodule.py:
if __name__ == "__main__":
    print("A")
else:
    print("B")
```
**A)** B  
**B)** A  
**C)** Nothing  
**D)** Error

---

### Question 12
What will be printed?
```python
import os
print(type(os.getcwd()))
```
**A)** <class 'str'>  
**B)** <class 'list'>  
**C)** <class 'path'>  
**D)** Error

---

### Question 13
What is the output?
```python
from datetime import date
today = date.today()
print(type(today))
```
**A)** <class 'datetime.date'>  
**B)** <class 'str'>  
**C)** <class 'date'>  
**D)** Error

---

### Question 14
What will be printed?
```python
import math
result = math.floor(5.9)
print(result)
```
**A)** 5  
**B)** 6  
**C)** 5.0  
**D)** Error

---

### Question 15
What is the output?
```python
import sys
print(len(sys.path) > 0)
```
**A)** True  
**B)** False  
**C)** 0  
**D)** Error

---

### Question 16
What will be printed?
```python
import random
random.seed(0)
a = random.randint(1, 10)
random.seed(0)
b = random.randint(1, 10)
print(a == b)
```
**A)** True  
**B)** False  
**C)** Sometimes True, sometimes False  
**D)** Error

---

### Question 17
What is the output?
```python
from math import factorial
print(factorial(0))
```
**A)** 1  
**B)** 0  
**C)** None  
**D)** Error

---

### Question 18
What will be printed?
```python
import os
path = os.path.join('folder', 'file.txt')
print('/' in path or '\\' in path)
```
**A)** True  
**B)** False  
**C)** Depends on OS  
**D)** Error

---

### Question 19
What is the output?
```python
# mymod.py contains: def func(): return 42
from mymod import func
print(func())
```
**A)** 42  
**B)** func()  
**C)** None  
**D)** Error

---

### Question 20
What will be printed?
```python
import math
print(math.pow(2, 3))
```
**A)** 8.0  
**B)** 8  
**C)** 6  
**D)** Error

---

## Answers

### Answer 1: **A) 5.0**
**Explanation**: math.sqrt() returns square root as float

---

### Answer 2: **A) 3.141592653589793**
**Explanation**: from...import brings name into current namespace

---

### Answer 3: **A) 5**
**Explanation**: ceil() rounds up 4.3 to 5

---

### Answer 4: **A) 10**
**Explanation**: Access module variable with module.name

---

### Answer 5: **A) Direct**
**Explanation**: When run directly, __name__ == "__main__"

---

### Answer 6: **A) <class 'float'>**
**Explanation**: random.random() returns float between 0 and 1

---

### Answer 7: **A) <class 'list'>**
**Explanation**: sys.argv is a list of command-line arguments

---

### Answer 8: **A) A float value around 1.77**
**Explanation**: sqrt(3.14159...) ≈ 1.77

---

### Answer 9: **A) One of: 1, 2, 3, 4, or 5**
**Explanation**: choice() returns random element from sequence

---

### Answer 10: **A) True**
**Explanation**: dir() lists module contents, 'pi' is in math module

---

### Answer 11: **A) B**
**Explanation**: When imported, __name__ is module name, not "__main__"

---

### Answer 12: **A) <class 'str'>**
**Explanation**: getcwd() returns current working directory as string

---

### Answer 13: **A) <class 'datetime.date'>**
**Explanation**: today() returns date object

---

### Answer 14: **A) 5**
**Explanation**: floor() rounds down to nearest integer

---

### Answer 15: **A) True**
**Explanation**: sys.path always has at least one entry

---

### Answer 16: **A) True**
**Explanation**: Same seed produces same random sequence

---

### Answer 17: **A) 1**
**Explanation**: 0! = 1 by definition

---

### Answer 18: **A) True**
**Explanation**: os.path.join() uses OS-appropriate separator

---

### Answer 19: **A) 42**
**Explanation**: Import and call function from module

---

### Answer 20: **A) 8.0**
**Explanation**: math.pow() returns float, 2³ = 8.0

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 6: Packages**  
❌ **If you scored below 80**: Review modules theory and practice more
