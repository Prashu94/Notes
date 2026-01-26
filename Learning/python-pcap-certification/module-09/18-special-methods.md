# Module 9 Part 3: Special Methods (Magic Methods/Dunder Methods)

## Introduction to Special Methods

**Special methods** (also called magic methods or dunder methods) are methods with double underscores (`__`) before and after the name. They allow classes to interact with Python's built-in functions and operators.

### Why Use Special Methods?
- Make your classes behave like built-in types
- Enable operator overloading
- Integrate with Python's protocols (iteration, context management, etc.)
- Provide custom string representations

---

## Object Initialization and Representation

### `__init__()` - Constructor
```python
class Point:
    def __init__(self, x, y):
        """Initialize point with coordinates"""
        self.x = x
        self.y = y

point = Point(3, 4)
```

### `__str__()` - User-Friendly String
Called by `str()` and `print()`.

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author
    
    def __str__(self):
        return f'"{self.title}" by {self.author}'

book = Book("1984", "George Orwell")
print(book)         # "1984" by George Orwell
print(str(book))    # "1984" by George Orwell
```

### `__repr__()` - Developer-Friendly String
Called by `repr()` and in interactive shell. Should ideally return code to recreate object.

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

## Comparison Operators

### Comparison Special Methods
```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height
    
    def __eq__(self, other):
        """Equal to (==)"""
        return self.area() == other.area()
    
    def __ne__(self, other):
        """Not equal to (!=)"""
        return self.area() != other.area()
    
    def __lt__(self, other):
        """Less than (<)"""
        return self.area() < other.area()
    
    def __le__(self, other):
        """Less than or equal (<=)"""
        return self.area() <= other.area()
    
    def __gt__(self, other):
        """Greater than (>)"""
        return self.area() > other.area()
    
    def __ge__(self, other):
        """Greater than or equal (>=)"""
        return self.area() >= other.area()

rect1 = Rectangle(5, 4)   # area = 20
rect2 = Rectangle(10, 2)  # area = 20
rect3 = Rectangle(3, 3)   # area = 9

print(rect1 == rect2)  # True
print(rect1 > rect3)   # True
print(rect3 < rect1)   # True
```

---

## Arithmetic Operators

### Arithmetic Special Methods
```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        """Addition (+)"""
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        """Subtraction (-)"""
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        """Multiplication (*)"""
        return Vector(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        """Division (/)"""
        return Vector(self.x / scalar, self.y / scalar)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(v1 + v2)   # Vector(4, 6)
print(v1 - v2)   # Vector(2, 2)
print(v1 * 2)    # Vector(6, 8)
print(v1 / 2)    # Vector(1.5, 2.0)
```

### More Arithmetic Methods
```python
class Number:
    def __init__(self, value):
        self.value = value
    
    def __floordiv__(self, other):
        """Floor division (//)"""
        return Number(self.value // other.value)
    
    def __mod__(self, other):
        """Modulo (%)"""
        return Number(self.value % other.value)
    
    def __pow__(self, other):
        """Power (**)"""
        return Number(self.value ** other.value)
    
    def __repr__(self):
        return f"Number({self.value})"

n1 = Number(10)
n2 = Number(3)

print(n1 // n2)  # Number(3)
print(n1 % n2)   # Number(1)
print(n1 ** n2)  # Number(1000)
```

---

## Container Special Methods

### `__len__()` - Length
```python
class Playlist:
    def __init__(self):
        self.songs = []
    
    def add(self, song):
        self.songs.append(song)
    
    def __len__(self):
        return len(self.songs)

playlist = Playlist()
playlist.add("Song 1")
playlist.add("Song 2")
print(len(playlist))  # 2
```

### `__getitem__()` - Indexing and Slicing
```python
class CustomList:
    def __init__(self, items):
        self.items = items
    
    def __getitem__(self, index):
        """Support indexing: obj[index]"""
        return self.items[index]
    
    def __len__(self):
        return len(self.items)

my_list = CustomList([1, 2, 3, 4, 5])
print(my_list[0])      # 1
print(my_list[1:3])    # [2, 3]
print(my_list[-1])     # 5
```

### `__setitem__()` and `__delitem__()`
```python
class SmartDict:
    def __init__(self):
        self.data = {}
    
    def __getitem__(self, key):
        """Get item: obj[key]"""
        return self.data[key]
    
    def __setitem__(self, key, value):
        """Set item: obj[key] = value"""
        self.data[key] = value
    
    def __delitem__(self, key):
        """Delete item: del obj[key]"""
        del self.data[key]
    
    def __contains__(self, key):
        """Check membership: key in obj"""
        return key in self.data

d = SmartDict()
d['name'] = 'Alice'     # Calls __setitem__
print(d['name'])        # Calls __getitem__ → Alice
print('name' in d)      # Calls __contains__ → True
del d['name']           # Calls __delitem__
```

---

## Iteration Protocol

### `__iter__()` and `__next__()`
```python
class Countdown:
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        """Return iterator object (self)"""
        return self
    
    def __next__(self):
        """Return next item or raise StopIteration"""
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for num in Countdown(5):
    print(num)  # 5, 4, 3, 2, 1
```

### Example: Custom Range
```python
class MyRange:
    def __init__(self, start, end):
        self.current = start
        self.end = end
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        result = self.current
        self.current += 1
        return result

for i in MyRange(0, 5):
    print(i)  # 0, 1, 2, 3, 4
```

---

## Context Manager Protocol

### `__enter__()` and `__exit__()`
```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        """Called when entering 'with' block"""
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Called when exiting 'with' block"""
        if self.file:
            self.file.close()
        # Return False to propagate exceptions
        return False

# Usage
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
# File automatically closed
```

---

## Callable Objects

### `__call__()` - Make Object Callable
```python
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    
    def __call__(self, value):
        """Allow object to be called like a function"""
        return value * self.factor

double = Multiplier(2)
triple = Multiplier(3)

print(double(5))   # 10
print(triple(5))   # 15
```

---

## Attribute Access

### `__getattr__()`, `__setattr__()`, `__delattr__()`
```python
class DynamicAttributes:
    def __init__(self):
        # Use object.__setattr__ to avoid recursion
        object.__setattr__(self, '_data', {})
    
    def __getattr__(self, name):
        """Called when attribute doesn't exist"""
        return self._data.get(name, f"No attribute '{name}'")
    
    def __setattr__(self, name, value):
        """Called when setting any attribute"""
        if name == '_data':
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
    
    def __delattr__(self, name):
        """Called when deleting attribute"""
        if name in self._data:
            del self._data[name]

obj = DynamicAttributes()
obj.name = 'Alice'
obj.age = 30
print(obj.name)     # Alice
print(obj.missing)  # No attribute 'missing'
del obj.age
```

---

## Boolean Context

### `__bool__()` - Truth Value Testing
```python
class Account:
    def __init__(self, balance):
        self.balance = balance
    
    def __bool__(self):
        """Object is True if balance > 0"""
        return self.balance > 0

account1 = Account(100)
account2 = Account(0)
account3 = Account(-50)

if account1:
    print("Account 1 has funds")  # Prints

if not account2:
    print("Account 2 is empty")   # Prints

if not account3:
    print("Account 3 is negative")  # Prints
```

---

## Complete Example: Custom List Class

```python
class MyList:
    def __init__(self, items=None):
        self.items = items if items is not None else []
    
    # String representation
    def __str__(self):
        return f"MyList{self.items}"
    
    def __repr__(self):
        return f"MyList({self.items!r})"
    
    # Length
    def __len__(self):
        return len(self.items)
    
    # Indexing
    def __getitem__(self, index):
        return self.items[index]
    
    def __setitem__(self, index, value):
        self.items[index] = value
    
    # Membership
    def __contains__(self, item):
        return item in self.items
    
    # Arithmetic
    def __add__(self, other):
        return MyList(self.items + other.items)
    
    # Iteration
    def __iter__(self):
        return iter(self.items)
    
    # Comparison
    def __eq__(self, other):
        return self.items == other.items
    
    # Boolean
    def __bool__(self):
        return len(self.items) > 0

# Usage
list1 = MyList([1, 2, 3])
list2 = MyList([4, 5])

print(list1)              # MyList[1, 2, 3]
print(len(list1))         # 3
print(list1[0])           # 1
print(2 in list1)         # True
print(list1 + list2)      # MyList[1, 2, 3, 4, 5]
print(list1 == list2)     # False

for item in list1:
    print(item)           # 1, 2, 3

if list1:
    print("List is not empty")
```

---

## Summary Table

| Method | Operator/Function | Description |
|--------|-------------------|-------------|
| `__init__` | `Class()` | Constructor |
| `__str__` | `str()`, `print()` | User-friendly string |
| `__repr__` | `repr()` | Developer string |
| `__len__` | `len()` | Length |
| `__getitem__` | `obj[key]` | Get item |
| `__setitem__` | `obj[key] = value` | Set item |
| `__delitem__` | `del obj[key]` | Delete item |
| `__contains__` | `in` | Membership test |
| `__iter__` | `for item in obj` | Iteration |
| `__next__` | `next()` | Next item |
| `__eq__` | `==` | Equal to |
| `__ne__` | `!=` | Not equal |
| `__lt__` | `<` | Less than |
| `__le__` | `<=` | Less or equal |
| `__gt__` | `>` | Greater than |
| `__ge__` | `>=` | Greater or equal |
| `__add__` | `+` | Addition |
| `__sub__` | `-` | Subtraction |
| `__mul__` | `*` | Multiplication |
| `__truediv__` | `/` | Division |
| `__call__` | `obj()` | Call object |
| `__enter__` | `with obj:` | Enter context |
| `__exit__` | End `with` | Exit context |
| `__bool__` | `bool()`, `if obj:` | Truth value |

---

## Next Steps
Continue to **Module 9: Practice Questions - Special Methods**
