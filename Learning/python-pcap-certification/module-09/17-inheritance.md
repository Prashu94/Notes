# Module 9 Part 2: Inheritance

## Introduction to Inheritance

**Inheritance** allows a class to inherit attributes and methods from another class, promoting code reuse and hierarchical relationships.

### Key Terms
- **Parent Class** (Base Class, Superclass): Class being inherited from
- **Child Class** (Derived Class, Subclass): Class that inherits
- **Override**: Redefine parent method in child class
- **Extend**: Add new functionality to inherited class

---

## Basic Inheritance Syntax

```python
class ParentClass:
    # Parent class code
    pass

class ChildClass(ParentClass):
    # Child class code
    pass
```

### Example 1: Simple Inheritance
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        print(f"{self.name} makes a sound")

class Dog(Animal):  # Dog inherits from Animal
    pass

dog = Dog("Buddy")
dog.speak()  # Buddy makes a sound (inherited method)
```

### Example 2: Adding New Methods
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def bark(self):  # New method specific to Dog
        return f"{self.name} barks: Woof!"

dog = Dog("Max")
print(dog.speak())  # Inherited: Max makes a sound
print(dog.bark())   # New method: Max barks: Woof!
```

---

## Overriding Methods

Child class can provide its own implementation of parent's method.

### Example: Method Override
```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def speak(self):  # Override parent method
        return f"{self.name} barks: Woof!"

class Cat(Animal):
    def speak(self):  # Override parent method
        return f"{self.name} meows: Meow!"

dog = Dog("Buddy")
cat = Cat("Whiskers")

print(dog.speak())  # Buddy barks: Woof!
print(cat.speak())  # Whiskers meows: Meow!
```

---

## The `super()` Function

`super()` calls methods from the parent class, useful for extending rather than completely overriding.

### Example 1: Using super() in __init__()
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def display(self):
        print(f"Name: {self.name}, Age: {self.age}")

class Student(Person):
    def __init__(self, name, age, student_id):
        super().__init__(name, age)  # Call parent __init__
        self.student_id = student_id  # Add new attribute
    
    def display(self):
        super().display()  # Call parent display
        print(f"Student ID: {self.student_id}")

student = Student("Alice", 20, "S12345")
student.display()
# Output:
# Name: Alice, Age: 20
# Student ID: S12345
```

### Example 2: Extending Methods
```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class ColoredRectangle(Rectangle):
    def __init__(self, width, height, color):
        super().__init__(width, height)  # Initialize parent
        self.color = color
    
    def describe(self):
        area = super().area()  # Use parent method
        return f"{self.color} rectangle with area {area}"

rect = ColoredRectangle(5, 3, "Red")
print(rect.describe())  # Red rectangle with area 15
```

---

## Multiple Inheritance

Python supports inheriting from multiple parent classes.

### Syntax
```python
class Child(Parent1, Parent2, Parent3):
    pass
```

### Example: Multiple Inheritance
```python
class Flyer:
    def fly(self):
        return "Flying high!"

class Swimmer:
    def swim(self):
        return "Swimming fast!"

class Duck(Flyer, Swimmer):  # Inherits from both
    def quack(self):
        return "Quack quack!"

duck = Duck()
print(duck.fly())    # Flying high!
print(duck.swim())   # Swimming fast!
print(duck.quack())  # Quack quack!
```

### Diamond Problem and MRO
```python
class A:
    def method(self):
        return "A"

class B(A):
    def method(self):
        return "B"

class C(A):
    def method(self):
        return "C"

class D(B, C):  # Inherits from both B and C
    pass

d = D()
print(d.method())  # B (follows MRO: D -> B -> C -> A)
print(D.__mro__)   # Shows Method Resolution Order
```

---

## Method Resolution Order (MRO)

Python uses C3 Linearization algorithm to determine method lookup order.

### Checking MRO
```python
class A:
    pass

class B(A):
    pass

class C(A):
    pass

class D(B, C):
    pass

# View MRO
print(D.__mro__)
# (<class '__main__.D'>, <class '__main__.B'>, <class '__main__.C'>, 
#  <class '__main__.A'>, <class 'object'>)

# Or use mro() method
print(D.mro())
```

---

## Using `isinstance()` and `issubclass()`

### `isinstance()` - Check Object Type
```python
class Animal:
    pass

class Dog(Animal):
    pass

dog = Dog()
print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True (Dog is subclass of Animal)
print(isinstance(dog, str))     # False
```

### `issubclass()` - Check Class Inheritance
```python
class Animal:
    pass

class Dog(Animal):
    pass

print(issubclass(Dog, Animal))  # True
print(issubclass(Animal, Dog))  # False
print(issubclass(Dog, Dog))     # True
```

---

## Abstract Base Classes (ABC)

Define interfaces that child classes must implement.

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        """Must be implemented by child classes"""
        pass
    
    @abstractmethod
    def perimeter(self):
        """Must be implemented by child classes"""
        pass

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def perimeter(self):
        return 2 * (self.width + self.height)

# Cannot instantiate abstract class
# shape = Shape()  # TypeError

# Can instantiate concrete implementation
rect = Rectangle(5, 3)
print(rect.area())       # 15
print(rect.perimeter())  # 16
```

---

## Polymorphism

Different classes can be used interchangeably through a common interface.

### Example: Polymorphic Behavior
```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class Cow(Animal):
    def speak(self):
        return "Moo!"

def make_animal_speak(animal):
    """Works with any Animal subclass"""
    print(animal.speak())

animals = [Dog(), Cat(), Cow()]
for animal in animals:
    make_animal_speak(animal)
# Output:
# Woof!
# Meow!
# Moo!
```

---

## Practical Examples

### Example 1: Employee Hierarchy
```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
    
    def display(self):
        print(f"Name: {self.name}")
        print(f"Salary: ${self.salary}")

class Developer(Employee):
    def __init__(self, name, salary, programming_language):
        super().__init__(name, salary)
        self.programming_language = programming_language
    
    def display(self):
        super().display()
        print(f"Language: {self.programming_language}")

class Manager(Employee):
    def __init__(self, name, salary, team_size):
        super().__init__(name, salary)
        self.team_size = team_size
    
    def display(self):
        super().display()
        print(f"Team Size: {self.team_size}")

dev = Developer("Alice", 80000, "Python")
mgr = Manager("Bob", 100000, 5)

dev.display()
print()
mgr.display()
```

### Example 2: Vehicle Hierarchy
```python
class Vehicle:
    def __init__(self, brand, model, year):
        self.brand = brand
        self.model = model
        self.year = year
    
    def start(self):
        return f"{self.brand} {self.model} is starting..."
    
    def stop(self):
        return f"{self.brand} {self.model} is stopping..."

class Car(Vehicle):
    def __init__(self, brand, model, year, num_doors):
        super().__init__(brand, model, year)
        self.num_doors = num_doors
    
    def honk(self):
        return "Beep beep!"

class Motorcycle(Vehicle):
    def __init__(self, brand, model, year, has_sidecar):
        super().__init__(brand, model, year)
        self.has_sidecar = has_sidecar
    
    def wheelie(self):
        return "Doing a wheelie!"

car = Car("Toyota", "Camry", 2024, 4)
bike = Motorcycle("Harley", "Sportster", 2024, False)

print(car.start())   # Toyota Camry is starting...
print(car.honk())    # Beep beep!
print(bike.start())  # Harley Sportster is starting...
print(bike.wheelie())  # Doing a wheelie!
```

### Example 3: Bank Account Hierarchy
```python
class BankAccount:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return self.balance
        raise ValueError("Amount must be positive")
    
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance
    
    def get_balance(self):
        return self.balance

class SavingsAccount(BankAccount):
    def __init__(self, account_number, balance=0, interest_rate=0.02):
        super().__init__(account_number, balance)
        self.interest_rate = interest_rate
    
    def apply_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        return interest

class CheckingAccount(BankAccount):
    def __init__(self, account_number, balance=0, overdraft_limit=100):
        super().__init__(account_number, balance)
        self.overdraft_limit = overdraft_limit
    
    def withdraw(self, amount):
        if amount > self.balance + self.overdraft_limit:
            raise ValueError("Exceeds overdraft limit")
        self.balance -= amount
        return self.balance

savings = SavingsAccount("SAV123", 1000, 0.03)
checking = CheckingAccount("CHK456", 500, 200)

savings.deposit(500)
interest = savings.apply_interest()
print(f"Savings balance: ${savings.get_balance()}, Interest: ${interest}")

checking.withdraw(600)  # Allowed with overdraft
print(f"Checking balance: ${checking.get_balance()}")
```

---

## Composition vs Inheritance

**Composition**: "Has-a" relationship (using objects of other classes)
**Inheritance**: "Is-a" relationship (extending a base class)

### Example: Composition
```python
class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
    
    def start(self):
        return "Engine started"

class Car:
    def __init__(self, brand, engine):
        self.brand = brand
        self.engine = engine  # Composition: Car HAS-A Engine
    
    def start(self):
        return f"{self.brand}: {self.engine.start()}"

engine = Engine(200)
car = Car("Toyota", engine)
print(car.start())  # Toyota: Engine started
```

**When to use:**
- **Inheritance**: Clear "is-a" relationship (Dog IS-A Animal)
- **Composition**: "Has-a" relationship (Car HAS-A Engine)

---

## Summary

✅ **Inheritance** allows classes to inherit from parent classes  
✅ **Child classes** can override parent methods  
✅ **super()** calls parent class methods  
✅ **Multiple inheritance** allows inheriting from multiple parents  
✅ **MRO** (Method Resolution Order) determines method lookup  
✅ **isinstance()** checks object type  
✅ **issubclass()** checks class inheritance  
✅ **ABC** creates abstract base classes  
✅ **Polymorphism** allows treating different types uniformly  
✅ **Composition** is alternative to inheritance  

---

## Next Steps
Continue to **Module 9: Practice Questions - Inheritance**
