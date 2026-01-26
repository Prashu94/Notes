# Module 9 Part 1: Practice Questions - Classes and Objects

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
class Dog:
    species = "Canine"

dog1 = Dog()
dog2 = Dog()
print(dog1.species == dog2.species)
```
**A)** True  
**B)** False  
**C)** None  
**D)** Error

---

### Question 2
What will be printed?
```python
class Person:
    def __init__(self, name):
        self.name = name

person = Person("Alice")
print(person.name)
```
**A)** Alice  
**B)** name  
**C)** self.name  
**D)** Error

---

### Question 3
What is the purpose of `__init__()`?
**A)** Initialize instance attributes  
**B)** Delete object  
**C)** Create class  
**D)** Define methods

---

### Question 4
What is the output?
```python
class Counter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1

c = Counter()
c.increment()
c.increment()
print(c.count)
```
**A)** 2  
**B)** 0  
**C)** 1  
**D)** Error

---

### Question 5
What does `self` represent?
**A)** Current instance  
**B)** Class itself  
**C)** Parent class  
**D)** Module

---

### Question 6
What is the output?
```python
class Example:
    x = 10

print(Example.x)
```
**A)** 10  
**B)** x  
**C)** None  
**D)** Error

---

### Question 7
What will be printed?
```python
class Test:
    def __init__(self, value):
        self.value = value

obj = Test(5)
print(obj.value)
```
**A)** 5  
**B)** value  
**C)** Test  
**D)** Error

---

### Question 8
Which decorator is used for class methods?
**A)** @classmethod  
**B)** @class  
**C)** @method  
**D)** @static

---

### Question 9
What is the output?
```python
class Math:
    @staticmethod
    def add(a, b):
        return a + b

print(Math.add(3, 4))
```
**A)** 7  
**B)** 34  
**C)** None  
**D)** Error

---

### Question 10
What will be printed?
```python
class Book:
    def __init__(self, title):
        self.title = title
    
    def __str__(self):
        return self.title

book = Book("Python")
print(book)
```
**A)** Python  
**B)** <Book object>  
**C)** Book  
**D)** Error

---

### Question 11
What is a class attribute?
**A)** Shared by all instances  
**B)** Unique to each instance  
**C)** Only in __init__  
**D)** Always private

---

### Question 12
What is the output?
```python
class Circle:
    pi = 3.14
    
    def __init__(self, radius):
        self.radius = radius

c = Circle(5)
print(c.pi)
```
**A)** 3.14  
**B)** 5  
**C)** pi  
**D)** Error

---

### Question 13
What will be printed?
```python
class Test:
    count = 0
    
    def __init__(self):
        Test.count += 1

t1 = Test()
t2 = Test()
print(Test.count)
```
**A)** 2  
**B)** 1  
**C)** 0  
**D)** Error

---

### Question 14
Which creates an instance method?
**A)** `def method(self):`  
**B)** `def method(cls):`  
**C)** `@staticmethod`  
**D)** `@classmethod`

---

### Question 15
What is the output?
```python
class Example:
    def __init__(self):
        self._value = 10

e = Example()
print(e._value)
```
**A)** 10  
**B)** AttributeError  
**C)** None  
**D)** _value

---

### Question 16
What decorator creates a property?
**A)** @property  
**B)** @attribute  
**C)** @getter  
**D)** @field

---

### Question 17
What is the output?
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

p = Point(3, 4)
print(repr(p))
```
**A)** Point(3, 4)  
**B)** (3, 4)  
**C)** <Point object>  
**D)** Error

---

### Question 18
What will be printed?
```python
class Car:
    wheels = 4

c1 = Car()
c2 = Car()
Car.wheels = 6
print(c1.wheels)
```
**A)** 6  
**B)** 4  
**C)** None  
**D)** Error

---

### Question 19
What parameter does a class method receive?
**A)** cls (the class)  
**B)** self (the instance)  
**C)** None  
**D)** Both A and B

---

### Question 20
What is the output?
```python
class Example:
    def __init__(self, x):
        self.x = x

e1 = Example(10)
e2 = Example(10)
print(e1.x == e2.x)
```
**A)** True  
**B)** False  
**C)** None  
**D)** Error

---

## Answers

### Answer 1: **A) True**
**Explanation**: Class attribute `species` is shared by all instances

---

### Answer 2: **A) Alice**
**Explanation**: Instance attribute `name` is set to "Alice" in __init__

---

### Answer 3: **A) Initialize instance attributes**
**Explanation**: __init__() is the constructor that initializes new objects

---

### Answer 4: **A) 2**
**Explanation**: increment() called twice, count increases from 0 to 2

---

### Answer 5: **A) Current instance**
**Explanation**: self refers to the instance calling the method

---

### Answer 6: **A) 10**
**Explanation**: Class attributes can be accessed via class name

---

### Answer 7: **A) 5**
**Explanation**: Instance attribute value is set to 5 in constructor

---

### Answer 8: **A) @classmethod**
**Explanation**: @classmethod decorator defines class methods

---

### Answer 9: **A) 7**
**Explanation**: Static method adds two numbers: 3 + 4 = 7

---

### Answer 10: **A) Python**
**Explanation**: __str__() returns the title, which is printed

---

### Answer 11: **A) Shared by all instances**
**Explanation**: Class attributes are defined at class level and shared

---

### Answer 12: **A) 3.14**
**Explanation**: Instance can access class attribute via self or instance name

---

### Answer 13: **A) 2**
**Explanation**: Each instantiation increments class attribute count

---

### Answer 14: **A) `def method(self):`**
**Explanation**: Instance methods take self as first parameter

---

### Answer 15: **A) 10**
**Explanation**: Single underscore is convention for "protected" but still accessible

---

### Answer 16: **A) @property**
**Explanation**: @property decorator creates managed attributes

---

### Answer 17: **A) Point(3, 4)**
**Explanation**: __repr__() returns developer-friendly string representation

---

### Answer 18: **A) 6**
**Explanation**: Changing class attribute affects all instances

---

### Answer 19: **A) cls (the class)**
**Explanation**: Class methods receive class (cls) as first parameter

---

### Answer 20: **A) True**
**Explanation**: Both instances have x=10, so comparison is True

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 9: Inheritance**  
❌ **If you scored below 80**: Review classes and objects theory and practice more
