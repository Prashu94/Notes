# Module 9 Part 1: Classes and Objects (OOP Basics)

## Introduction to Object-Oriented Programming

**Object-Oriented Programming (OOP)** is a programming paradigm based on the concept of "objects" that contain data (attributes) and code (methods).

### Key OOP Concepts
- **Class**: Blueprint for creating objects
- **Object**: Instance of a class
- **Attributes**: Variables that belong to a class/object
- **Methods**: Functions that belong to a class
- **Encapsulation**: Bundling data and methods together
- **Inheritance**: Creating new classes from existing ones
- **Polymorphism**: Using a common interface for different types

---

## Defining Classes

### Basic Class Syntax

```python
class ClassName:
    """Class docstring"""
    # Class body
    pass
```

### Example: Simple Class
```python
class Dog:
    """A simple dog class"""
    pass

# Create instance (object)
my_dog = Dog()
print(type(my_dog))  # <class '__main__.Dog'>
```

---

## Class Attributes vs Instance Attributes

### Class Attributes
Shared by all instances of the class.

```python
class Dog:
    # Class attribute (shared by all instances)
    species = "Canis familiaris"
    
dog1 = Dog()
dog2 = Dog()

print(dog1.species)  # Canis familiaris
print(dog2.species)  # Canis familiaris

# Shared by all
Dog.species = "Canine"
print(dog1.species)  # Canine
print(dog2.species)  # Canine
```

### Instance Attributes
Unique to each instance.

```python
class Dog:
    def __init__(self, name, age):
        # Instance attributes (unique to each instance)
        self.name = name
        self.age = age

dog1 = Dog("Buddy", 3)
dog2 = Dog("Lucy", 5)

print(dog1.name)  # Buddy
print(dog2.name)  # Lucy
```

---

## The `__init__()` Method (Constructor)

The `__init__()` method is called automatically when creating a new instance.

### Syntax
```python
class ClassName:
    def __init__(self, parameters):
        # Initialize instance attributes
        self.attribute = value
```

### Example 1: Basic Constructor
```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person = Person("Alice", 30)
print(person.name)  # Alice
print(person.age)   # 30
```

### Example 2: Constructor with Default Values
```python
class Rectangle:
    def __init__(self, width=1, height=1):
        self.width = width
        self.height = height

rect1 = Rectangle()           # Uses defaults: 1, 1
rect2 = Rectangle(5, 3)       # 5, 3
rect3 = Rectangle(width=10)   # 10, 1
```

### Example 3: Validation in Constructor
```python
class BankAccount:
    def __init__(self, balance=0):
        if balance < 0:
            raise ValueError("Balance cannot be negative!")
        self.balance = balance

account = BankAccount(100)  # OK
# account = BankAccount(-50)  # ValueError
```

---

## Understanding `self`

`self` represents the instance of the class and must be the first parameter of instance methods.

### What is `self`?
- Reference to the current instance
- Allows access to instance attributes and methods
- **Convention**: Name is `self` (not mandatory, but strongly recommended)

```python
class Counter:
    def __init__(self):
        self.count = 0
    
    def increment(self):
        self.count += 1  # Access instance attribute
    
    def get_count(self):
        return self.count

counter = Counter()
counter.increment()
counter.increment()
print(counter.get_count())  # 2
```

### Why `self` is Needed
```python
class Example:
    def __init__(self, value):
        self.value = value  # Instance attribute
    
    def show(self):
        print(self.value)  # Access instance attribute

obj1 = Example(10)
obj2 = Example(20)

obj1.show()  # 10 (self refers to obj1)
obj2.show()  # 20 (self refers to obj2)
```

---

## Instance Methods

Functions defined inside a class that operate on instances.

### Syntax
```python
class ClassName:
    def method_name(self, parameters):
        # Method body
        pass
```

### Example 1: Simple Methods
```python
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, num):
        self.result += num
    
    def subtract(self, num):
        self.result -= num
    
    def get_result(self):
        return self.result

calc = Calculator()
calc.add(10)
calc.add(5)
calc.subtract(3)
print(calc.get_result())  # 12
```

### Example 2: Methods with Return Values
```python
class Circle:
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
    
    def circumference(self):
        return 2 * 3.14159 * self.radius

circle = Circle(5)
print(f"Area: {circle.area()}")              # Area: 78.53975
print(f"Circumference: {circle.circumference()}")  # Circumference: 31.4159
```

### Example 3: Methods Calling Other Methods
```python
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
    
    def get_letter_grade(self):
        if self.grade >= 90:
            return 'A'
        elif self.grade >= 80:
            return 'B'
        elif self.grade >= 70:
            return 'C'
        elif self.grade >= 60:
            return 'D'
        else:
            return 'F'
    
    def display_info(self):
        letter = self.get_letter_grade()  # Call another method
        print(f"{self.name}: {self.grade}% ({letter})")

student = Student("Bob", 85)
student.display_info()  # Bob: 85% (B)
```

---

## Class Methods

Methods that work with the class itself, not instances. Use `@classmethod` decorator.

### Syntax
```python
class ClassName:
    @classmethod
    def method_name(cls, parameters):
        # Method body
        pass
```

### Example: Alternative Constructors
```python
class Date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    
    @classmethod
    def from_string(cls, date_string):
        """Create Date from string 'YYYY-MM-DD'"""
        year, month, day = map(int, date_string.split('-'))
        return cls(year, month, day)  # cls() calls __init__
    
    def display(self):
        print(f"{self.year}-{self.month:02d}-{self.day:02d}")

# Regular constructor
date1 = Date(2024, 1, 15)

# Class method constructor
date2 = Date.from_string("2024-01-15")

date1.display()  # 2024-01-15
date2.display()  # 2024-01-15
```

---

## Static Methods

Methods that don't access instance or class data. Use `@staticmethod` decorator.

### Syntax
```python
class ClassName:
    @staticmethod
    def method_name(parameters):
        # Method body (no self or cls)
        pass
```

### Example: Utility Methods
```python
class Math:
    @staticmethod
    def is_even(num):
        return num % 2 == 0
    
    @staticmethod
    def is_prime(num):
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True

# Call without instance
print(Math.is_even(4))    # True
print(Math.is_prime(17))  # True

# Can also call with instance (but not common)
math = Math()
print(math.is_even(5))    # False
```

---

## Properties and Encapsulation

### Private Attributes (Convention)
Python uses naming conventions for "private" attributes:

```python
class BankAccount:
    def __init__(self, balance):
        self._balance = balance  # "Protected" (single underscore)
        self.__pin = 1234        # "Private" (double underscore)
    
    def get_balance(self):
        return self._balance

account = BankAccount(1000)
print(account._balance)    # Can access (but shouldn't)
# print(account.__pin)     # AttributeError
```

### Using `@property` Decorator
Create computed attributes and controlled access.

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        """Get radius"""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Set radius with validation"""
        if value < 0:
            raise ValueError("Radius cannot be negative!")
        self._radius = value
    
    @property
    def area(self):
        """Computed property"""
        return 3.14159 * self._radius ** 2

circle = Circle(5)
print(circle.radius)    # 5 (calls getter)
print(circle.area)      # 78.53975 (computed)

circle.radius = 10      # Calls setter
print(circle.area)      # 314.159

# circle.radius = -5    # ValueError
```

---

## String Representation of Objects

### `__str__()` Method
Returns user-friendly string representation.

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
    
    def __str__(self):
        return f"{self.title} by {self.author}"

book = Book("1984", "George Orwell")
print(book)  # 1984 by George Orwell
print(str(book))  # 1984 by George Orwell
```

### `__repr__()` Method
Returns developer-friendly representation (ideally code to recreate object).

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"

point = Point(3, 4)
print(point)        # (3, 4) - uses __str__
print(repr(point))  # Point(3, 4) - uses __repr__
```

---

## Practical Examples

### Example 1: Shopping Cart
```python
class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, item, price):
        self.items.append({'item': item, 'price': price})
    
    def remove_item(self, item):
        self.items = [i for i in self.items if i['item'] != item]
    
    def total(self):
        return sum(item['price'] for item in self.items)
    
    def display(self):
        for item in self.items:
            print(f"{item['item']}: ${item['price']}")
        print(f"Total: ${self.total()}")

cart = ShoppingCart()
cart.add_item("Apple", 0.99)
cart.add_item("Banana", 0.59)
cart.add_item("Orange", 1.29)
cart.display()
```

### Example 2: Temperature Converter
```python
class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius
    
    @property
    def celsius(self):
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        return (self._celsius * 9/5) + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5/9

temp = Temperature(25)
print(f"{temp.celsius}°C = {temp.fahrenheit}°F")  # 25°C = 77.0°F

temp.fahrenheit = 98.6
print(f"{temp.celsius}°C = {temp.fahrenheit}°F")  # 37°C = 98.6°F
```

---

## Summary

✅ **Classes** are blueprints for creating objects  
✅ **`__init__()`** method initializes new instances  
✅ **`self`** refers to the current instance  
✅ **Instance attributes** are unique to each object  
✅ **Class attributes** are shared by all instances  
✅ **Instance methods** operate on specific objects  
✅ **Class methods** use `@classmethod` decorator  
✅ **Static methods** use `@staticmethod` decorator  
✅ **`@property`** creates managed attributes  
✅ **`__str__()`** and `__repr__()`** control string representation  

---

## Next Steps
Continue to **Module 9: Practice Questions - Classes and Objects**
