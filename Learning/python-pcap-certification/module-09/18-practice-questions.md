# Module 9 Part 3: Practice Questions - Special Methods

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
Which method is called by print(obj)?
**A)** `__str__()`  
**B)** `__repr__()`  
**C)** `__print__()`  
**D)** `__display__()`

---

### Question 2
What is the output?
```python
class Point:
    def __init__(self, x):
        self.x = x
    
    def __str__(self):
        return f"Point({self.x})"

p = Point(5)
print(p)
```
**A)** Point(5)  
**B)** 5  
**C)** <Point object>  
**D)** Error

---

### Question 3
Which method implements obj[key]?
**A)** `__getitem__()`  
**B)** `__get__()`  
**C)** `__index__()`  
**D)** `__access__()`

---

### Question 4
What will be printed?
```python
class MyList:
    def __init__(self, items):
        self.items = items
    
    def __len__(self):
        return len(self.items)

lst = MyList([1, 2, 3])
print(len(lst))
```
**A)** 3  
**B)** [1, 2, 3]  
**C)** MyList  
**D)** Error

---

### Question 5
Which method implements + operator?
**A)** `__add__()`  
**B)** `__plus__()`  
**C)** `__sum__()`  
**D)** `__op_add__()`

---

### Question 6
What is the output?
```python
class Number:
    def __init__(self, val):
        self.val = val
    
    def __eq__(self, other):
        return self.val == other.val

n1 = Number(5)
n2 = Number(5)
print(n1 == n2)
```
**A)** True  
**B)** False  
**C)** None  
**D)** Error

---

### Question 7
Which method makes object callable?
**A)** `__call__()`  
**B)** `__callable__()`  
**C)** `__exec__()`  
**D)** `__run__()`

---

### Question 8
What will be printed?
```python
class Container:
    def __init__(self, items):
        self.items = items
    
    def __contains__(self, item):
        return item in self.items

c = Container([1, 2, 3])
print(2 in c)
```
**A)** True  
**B)** False  
**C)** 2  
**D)** Error

---

### Question 9
Which method is for iteration?
**A)** `__iter__()`  
**B)** `__loop__()`  
**C)** `__iterate__()`  
**D)** `__for__()`

---

### Question 10
What is the output?
```python
class MyClass:
    def __bool__(self):
        return False

obj = MyClass()
if obj:
    print("True")
else:
    print("False")
```
**A)** False  
**B)** True  
**C)** None  
**D)** Error

---

### Question 11
Which method implements obj[key] = value?
**A)** `__setitem__()`  
**B)** `__set__()`  
**C)** `__assign__()`  
**D)** `__put__()`

---

### Question 12
What will be printed?
```python
class Vector:
    def __init__(self, x):
        self.x = x
    
    def __add__(self, other):
        return Vector(self.x + other.x)
    
    def __repr__(self):
        return f"Vector({self.x})"

v1 = Vector(3)
v2 = Vector(4)
print(v1 + v2)
```
**A)** Vector(7)  
**B)** 7  
**C)** Vector(3) + Vector(4)  
**D)** Error

---

### Question 13
Which method is called by repr(obj)?
**A)** `__repr__()`  
**B)** `__str__()`  
**C)** `__display__()`  
**D)** `__show__()`

---

### Question 14
What is the output?
```python
class Num:
    def __init__(self, val):
        self.val = val
    
    def __lt__(self, other):
        return self.val < other.val

n1 = Num(5)
n2 = Num(10)
print(n1 < n2)
```
**A)** True  
**B)** False  
**C)** 5 < 10  
**D)** Error

---

### Question 15
Which implements del obj[key]?
**A)** `__delitem__()`  
**B)** `__delete__()`  
**C)** `__remove__()`  
**D)** `__del__()`

---

### Question 16
What will be printed?
```python
class Counter:
    def __init__(self):
        self.count = 0
    
    def __call__(self):
        self.count += 1
        return self.count

c = Counter()
print(c())
print(c())
```
**A)** 1  
     2  
**B)** 0  
     1  
**C)** Counter  
**D)** Error

---

### Question 17
Which method implements * operator?
**A)** `__mul__()`  
**B)** `__mult__()`  
**C)** `__times__()`  
**D)** `__multiply__()`

---

### Question 18
What is the output?
```python
class Box:
    def __init__(self, items):
        self.items = items
    
    def __getitem__(self, index):
        return self.items[index]

box = Box([10, 20, 30])
print(box[1])
```
**A)** 20  
**B)** 10  
**C)** 1  
**D)** Error

---

### Question 19
Which methods implement context manager?
**A)** `__enter__` and `__exit__`  
**B)** `__start__` and `__end__`  
**C)** `__open__` and `__close__`  
**D)** `__begin__` and `__finish__`

---

### Question 20
What will be printed?
```python
class MyRange:
    def __init__(self, end):
        self.current = 0
        self.end = end
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        result = self.current
        self.current += 1
        return result

for i in MyRange(3):
    print(i, end=' ')
```
**A)** 0 1 2  
**B)** 1 2 3  
**C)** 0 1 2 3  
**D)** Error

---

## Answers

### Answer 1: **A) `__str__()`**
**Explanation**: print() calls __str__() method for string representation

---

### Answer 2: **A) Point(5)**
**Explanation**: __str__() returns "Point(5)" which is printed

---

### Answer 3: **A) `__getitem__()`**
**Explanation**: __getitem__() implements bracket notation for getting items

---

### Answer 4: **A) 3**
**Explanation**: len() calls __len__() which returns length of items list

---

### Answer 5: **A) `__add__()`**
**Explanation**: __add__() implements + operator

---

### Answer 6: **A) True**
**Explanation**: __eq__() compares values: 5 == 5 is True

---

### Answer 7: **A) `__call__()`**
**Explanation**: __call__() allows object to be called like a function

---

### Answer 8: **A) True**
**Explanation**: __contains__() implements 'in' operator, 2 is in [1,2,3]

---

### Answer 9: **A) `__iter__()`**
**Explanation**: __iter__() makes object iterable (used in for loops)

---

### Answer 10: **A) False**
**Explanation**: __bool__() returns False, so condition evaluates to False

---

### Answer 11: **A) `__setitem__()`**
**Explanation**: __setitem__() implements bracket notation for setting items

---

### Answer 12: **A) Vector(7)**
**Explanation**: __add__() adds x values (3+4=7), __repr__() formats output

---

### Answer 13: **A) `__repr__()`**
**Explanation**: repr() function calls __repr__() method

---

### Answer 14: **A) True**
**Explanation**: __lt__() implements < operator: 5 < 10 is True

---

### Answer 15: **A) `__delitem__()`**
**Explanation**: __delitem__() implements deletion using bracket notation

---

### Answer 16: **A) 1\n2**
**Explanation**: __call__() makes object callable; increments count each call

---

### Answer 17: **A) `__mul__()`**
**Explanation**: __mul__() implements * (multiplication) operator

---

### Answer 18: **A) 20**
**Explanation**: __getitem__(1) returns items[1] which is 20

---

### Answer 19: **A) `__enter__` and `__exit__`**
**Explanation**: Context managers (with statement) use __enter__ and __exit__

---

### Answer 20: **A) 0 1 2**
**Explanation**: __iter__() and __next__() create iterator yielding 0, 1, 2

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 10: Standard Library**  
❌ **If you scored below 80**: Review special methods theory and practice more
