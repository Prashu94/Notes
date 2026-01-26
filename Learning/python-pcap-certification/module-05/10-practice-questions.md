# Module 5 Part 1: Practice Questions - Functions

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
def greet():
    print("Hello")

greet()
```
**A)** Hello  
**B)** greet()  
**C)** None  
**D)** Error

---

### Question 2
What will be printed?
```python
def add(a, b):
    return a + b

result = add(3, 4)
print(result)
```
**A)** 7  
**B)** 34  
**C)** None  
**D)** Error

---

### Question 3
What is the output?
```python
def func():
    x = 10
    return x

print(func())
```
**A)** 10  
**B)** x  
**C)** None  
**D)** NameError

---

### Question 4
What will be printed?
```python
def func(x):
    return

result = func(5)
print(result)
```
**A)** 5  
**B)** None  
**C)** 0  
**D)** Error

---

### Question 5
What is the output?
```python
def greet(name="Guest"):
    print(f"Hello, {name}")

greet()
```
**A)** Hello, Guest  
**B)** Hello, name  
**C)** Hello,  
**D)** Error

---

### Question 6
What will be printed?
```python
def func(a, b=2):
    return a + b

print(func(3))
```
**A)** 5  
**B)** 3  
**C)** 2  
**D)** Error

---

### Question 7
What is the output?
```python
x = 10

def func():
    print(x)

func()
```
**A)** 10  
**B)** None  
**C)** NameError  
**D)** Error

---

### Question 8
What will be printed?
```python
def func(a, b, c):
    return a + b + c

print(func(c=3, a=1, b=2))
```
**A)** 6  
**B)** Error  
**C)** 123  
**D)** None

---

### Question 9
What is the output?
```python
def sum_all(*args):
    return sum(args)

print(sum_all(1, 2, 3, 4))
```
**A)** 10  
**B)** (1, 2, 3, 4)  
**C)** [1, 2, 3, 4]  
**D)** Error

---

### Question 10
What will be printed?
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(4))
```
**A)** 24  
**B)** 4  
**C)** 1  
**D)** Infinite recursion

---

### Question 11
What is the output?
```python
def func():
    pass

result = func()
print(result)
```
**A)** None  
**B)** pass  
**C)** 0  
**D)** Error

---

### Question 12
What will be printed?
```python
def get_values():
    return 1, 2, 3

a, b, c = get_values()
print(b)
```
**A)** 2  
**B)** (1, 2, 3)  
**C)** 1  
**D)** Error

---

### Question 13
What is the output?
```python
def func(x):
    x = x + 1
    return x

a = 5
func(a)
print(a)
```
**A)** 5  
**B)** 6  
**C)** None  
**D)** Error

---

### Question 14
What will be printed?
```python
def func(**kwargs):
    print(len(kwargs))

func(a=1, b=2, c=3)
```
**A)** 3  
**B)** 6  
**C)** {'a': 1, 'b': 2, 'c': 3}  
**D)** Error

---

### Question 15
What is the output?
```python
x = 5

def func():
    global x
    x = 10

func()
print(x)
```
**A)** 10  
**B)** 5  
**C)** None  
**D)** Error

---

### Question 16
What will be printed?
```python
def multiply(a, b=2, c=3):
    return a * b * c

print(multiply(2, 3))
```
**A)** 18  
**B)** 12  
**C)** 6  
**D)** Error

---

### Question 17
What is the output?
```python
def func(items=[]):
    items.append(1)
    return items

print(func())
print(func())
```
**A)** [1] [1]  
**B)** [1] [1, 1]  
**C)** [1, 1] [1, 1, 1]  
**D)** Error

---

### Question 18
What will be printed?
```python
def outer():
    x = 10
    def inner():
        return x
    return inner()

print(outer())
```
**A)** 10  
**B)** None  
**C)** NameError  
**D)** Error

---

### Question 19
What is the output?
```python
def func(a, *args):
    return a + len(args)

print(func(1, 2, 3, 4))
```
**A)** 4  
**B)** 10  
**C)** 1  
**D)** Error

---

### Question 20
What will be printed?
```python
def greet(name):
    """Greet a person."""
    return f"Hello, {name}"

print(type(greet.__doc__))
```
**A)** <class 'str'>  
**B)** <class 'NoneType'>  
**C)** <class 'function'>  
**D)** Error

---

## Answers

### Answer 1: **A) Hello**
**Explanation**: Function executes and prints "Hello"

---

### Answer 2: **A) 7**
**Explanation**: Function returns 3 + 4 = 7

---

### Answer 3: **A) 10**
**Explanation**: Function returns local variable x = 10

---

### Answer 4: **B) None**
**Explanation**: Empty return statement returns None

---

### Answer 5: **A) Hello, Guest**
**Explanation**: Default parameter value "Guest" is used

---

### Answer 6: **A) 5**
**Explanation**: a=3, b=2 (default), returns 3 + 2 = 5

---

### Answer 7: **A) 10**
**Explanation**: Function can read global variable x

---

### Answer 8: **A) 6**
**Explanation**: Keyword arguments: 1 + 2 + 3 = 6

---

### Answer 9: **A) 10**
**Explanation**: *args collects (1,2,3,4), sum returns 10

---

### Answer 10: **A) 24**
**Explanation**: 4! = 4 × 3 × 2 × 1 = 24

---

### Answer 11: **A) None**
**Explanation**: pass does nothing, function returns None

---

### Answer 12: **A) 2**
**Explanation**: Tuple unpacking, b gets second value (2)

---

### Answer 13: **A) 5**
**Explanation**: Function creates local copy, doesn't modify original

---

### Answer 14: **A) 3**
**Explanation**: **kwargs receives 3 key-value pairs

---

### Answer 15: **A) 10**
**Explanation**: global keyword allows modification of global x

---

### Answer 16: **A) 18**
**Explanation**: 2 × 3 × 3 = 18 (c uses default 3)

---

### Answer 17: **B) [1] [1, 1]**
**Explanation**: Mutable default argument pitfall - same list reused

---

### Answer 18: **A) 10**
**Explanation**: inner() can access enclosing function's variable

---

### Answer 19: **A) 4**
**Explanation**: a=1, args=(2,3,4), len=3, returns 1 + 3 = 4

---

### Answer 20: **A) <class 'str'>**
**Explanation**: Docstring is a string

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 5: Lambda Functions**  
❌ **If you scored below 80**: Review functions theory and practice more
