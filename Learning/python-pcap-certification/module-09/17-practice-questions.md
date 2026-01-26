# Module 9 Part 2: Practice Questions - Inheritance

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What is the output?
```python
class A:
    x = 10

class B(A):
    pass

print(B.x)
```
**A)** 10  
**B)** x  
**C)** None  
**D)** Error

---

### Question 2
What will be printed?
```python
class Animal:
    def speak(self):
        return "Sound"

class Dog(Animal):
    def speak(self):
        return "Bark"

dog = Dog()
print(dog.speak())
```
**A)** Bark  
**B)** Sound  
**C)** Both  
**D)** Error

---

### Question 3
What does super() do?
**A)** Calls parent class methods  
**B)** Creates superclass  
**C)** Deletes parent  
**D)** Defines inheritance

---

### Question 4
What is the output?
```python
class Parent:
    def __init__(self):
        self.x = 10

class Child(Parent):
    pass

c = Child()
print(c.x)
```
**A)** 10  
**B)** None  
**C)** x  
**D)** Error

---

### Question 5
What will be printed?
```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

b = B()
print(b.method())
```
**A)** B  
**B)** A  
**C)** AB  
**D)** Error

---

### Question 6
Which function checks if object is instance of a class?
**A)** isinstance()  
**B)** issubclass()  
**C)** type()  
**D)** check()

---

### Question 7
What is the output?
```python
class Animal:
    pass

class Dog(Animal):
    pass

print(issubclass(Dog, Animal))
```
**A)** True  
**B)** False  
**C)** Dog  
**D)** Error

---

### Question 8
What will be printed?
```python
class Parent:
    def __init__(self, x):
        self.x = x

class Child(Parent):
    def __init__(self, x, y):
        super().__init__(x)
        self.y = y

c = Child(10, 20)
print(c.x, c.y)
```
**A)** 10 20  
**B)** 10  
**C)** 20  
**D)** Error

---

### Question 9
What is multiple inheritance?
**A)** Inheriting from multiple parent classes  
**B)** Having multiple child classes  
**C)** Multiple methods in class  
**D)** Multiple instances

---

### Question 10
What is the output?
```python
class A:
    x = 1

class B:
    x = 2

class C(A, B):
    pass

print(C.x)
```
**A)** 1  
**B)** 2  
**C)** 3  
**D)** Error

---

### Question 11
What will be printed?
```python
class Animal:
    def speak(self):
        return "Sound"

class Dog(Animal):
    pass

dog = Dog()
print(dog.speak())
```
**A)** Sound  
**B)** None  
**C)** Dog  
**D)** Error

---

### Question 12
What is polymorphism?
**A)** Using common interface for different types  
**B)** Having many methods  
**C)** Multiple inheritance  
**D)** Method overriding

---

### Question 13
What is the output?
```python
class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    pass

s = Student("Alice")
print(s.name)
```
**A)** Alice  
**B)** None  
**C)** name  
**D)** Error

---

### Question 14
What will be printed?
```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return super().method() + "B"

b = B()
print(b.method())
```
**A)** AB  
**B)** BA  
**C)** A  
**D)** B

---

### Question 15
Which checks if class is subclass of another?
**A)** issubclass()  
**B)** isinstance()  
**C)** subclass()  
**D)** inherits()

---

### Question 16
What is the output?
```python
class Animal:
    def __init__(self):
        self.species = "Unknown"

class Dog(Animal):
    def __init__(self):
        super().__init__()
        self.species = "Canine"

dog = Dog()
print(dog.species)
```
**A)** Canine  
**B)** Unknown  
**C)** None  
**D)** Error

---

### Question 17
What will be printed?
```python
class A:
    pass

class B(A):
    pass

class C(B):
    pass

c = C()
print(isinstance(c, A))
```
**A)** True  
**B)** False  
**C)** C  
**D)** Error

---

### Question 18
What is method overriding?
**A)** Redefining parent method in child  
**B)** Having multiple methods  
**C)** Calling super()  
**D)** Creating new method

---

### Question 19
What is the output?
```python
class Base:
    x = 10

class Derived(Base):
    x = 20

print(Derived.x)
```
**A)** 20  
**B)** 10  
**C)** 30  
**D)** Error

---

### Question 20
What will be printed?
```python
class A:
    def greet(self):
        return "Hello from A"

class B(A):
    pass

b = B()
print(b.greet())
```
**A)** Hello from A  
**B)** Hello from B  
**C)** None  
**D)** Error

---

## Answers

### Answer 1: **A) 10**
**Explanation**: Child class B inherits class attribute x from parent A

---

### Answer 2: **A) Bark**
**Explanation**: Dog overrides speak() method, so "Bark" is returned

---

### Answer 3: **A) Calls parent class methods**
**Explanation**: super() is used to call methods from parent class

---

### Answer 4: **A) 10**
**Explanation**: Child inherits __init__ from Parent, which sets x=10

---

### Answer 5: **A) B**
**Explanation**: B's method() overrides A's method()

---

### Answer 6: **A) isinstance()**
**Explanation**: isinstance() checks if object is instance of class

---

### Answer 7: **A) True**
**Explanation**: Dog is a subclass of Animal

---

### Answer 8: **A) 10 20**
**Explanation**: super().__init__(x) sets x=10, then y=20 is set

---

### Answer 9: **A) Inheriting from multiple parent classes**
**Explanation**: Multiple inheritance allows class to inherit from multiple parents

---

### Answer 10: **A) 1**
**Explanation**: MRO (Method Resolution Order): C → A → B, so A.x (1) is used

---

### Answer 11: **A) Sound**
**Explanation**: Dog inherits speak() from Animal without overriding

---

### Answer 12: **A) Using common interface for different types**
**Explanation**: Polymorphism allows treating different types through common interface

---

### Answer 13: **A) Alice**
**Explanation**: Student inherits __init__ from Person, name is set to "Alice"

---

### Answer 14: **A) AB**
**Explanation**: super().method() returns "A", then "B" is appended

---

### Answer 15: **A) issubclass()**
**Explanation**: issubclass() checks if class is subclass of another

---

### Answer 16: **A) Canine**
**Explanation**: Child __init__ calls parent's (sets "Unknown"), then overwrites with "Canine"

---

### Answer 17: **A) True**
**Explanation**: C inherits from B which inherits from A, so c is instance of A

---

### Answer 18: **A) Redefining parent method in child**
**Explanation**: Method overriding is providing new implementation in child class

---

### Answer 19: **A) 20**
**Explanation**: Derived class attribute x overrides Base class attribute

---

### Answer 20: **A) Hello from A**
**Explanation**: B inherits greet() from A without overriding

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 9: Special Methods**  
❌ **If you scored below 80**: Review inheritance theory and practice more
