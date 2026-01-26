# Module 10: Python Standard Library

## Introduction to Standard Library

The Python Standard Library is a collection of modules that come with Python. No installation required!

### Why Use Standard Library?
- **Built-in**: Available with Python installation
- **Tested**: Reliable and well-maintained
- **Efficient**: Optimized implementations
- **Cross-platform**: Works on all operating systems

---

## Math Module

Provides mathematical functions.

### Common Functions
```python
import math

# Constants
print(math.pi)       # 3.141592653589793
print(math.e)        # 2.718281828459045
print(math.inf)      # Infinity
print(math.nan)      # Not a Number

# Rounding
print(math.ceil(4.3))   # 5 (round up)
print(math.floor(4.9))  # 4 (round down)
print(math.trunc(4.9))  # 4 (truncate decimal)

# Power and roots
print(math.sqrt(16))    # 4.0
print(math.pow(2, 3))   # 8.0
print(math.exp(2))      # e^2 = 7.389...

# Logarithms
print(math.log(10))      # Natural log (ln)
print(math.log10(100))   # Base-10 log = 2.0
print(math.log2(8))      # Base-2 log = 3.0

# Trigonometry (radians)
print(math.sin(math.pi/2))    # 1.0
print(math.cos(0))            # 1.0
print(math.tan(math.pi/4))    # 1.0

# Degrees and radians
print(math.degrees(math.pi))  # 180.0
print(math.radians(180))      # 3.141...

# Factorial
print(math.factorial(5))  # 120

# GCD
print(math.gcd(48, 18))   # 6
```

---

## Random Module

Generate random numbers and make random choices.

### Random Numbers
```python
import random

# Random float [0.0, 1.0)
print(random.random())

# Random integer [a, b] (inclusive)
print(random.randint(1, 10))

# Random float [a, b]
print(random.uniform(1.0, 10.0))

# Random from range
print(random.randrange(0, 10, 2))  # Even numbers 0-8
```

### Random Choices
```python
import random

colors = ['red', 'green', 'blue', 'yellow']

# Choose one
print(random.choice(colors))

# Choose multiple (with replacement)
print(random.choices(colors, k=3))

# Choose multiple (without replacement)
print(random.sample(colors, k=2))
```

### Shuffling and Seeding
```python
import random

# Shuffle list in-place
numbers = [1, 2, 3, 4, 5]
random.shuffle(numbers)
print(numbers)  # [3, 1, 5, 2, 4] (example)

# Set seed for reproducibility
random.seed(42)
print(random.random())  # Always same value with seed 42
random.seed(42)
print(random.random())  # Same as above
```

---

## Datetime Module

Work with dates and times.

### Date Operations
```python
from datetime import date

# Current date
today = date.today()
print(today)  # 2024-01-15 (example)

# Create specific date
birthday = date(1990, 5, 15)
print(birthday)  # 1990-05-15

# Date attributes
print(today.year)   # 2024
print(today.month)  # 1
print(today.day)    # 15

# Date arithmetic
from datetime import timedelta
tomorrow = today + timedelta(days=1)
print(tomorrow)

# Difference between dates
age_days = today - birthday
print(age_days.days)  # Days old
```

### Time Operations
```python
from datetime import time

# Create time
meeting = time(14, 30, 0)  # 2:30 PM
print(meeting)  # 14:30:00

# Time attributes
print(meeting.hour)    # 14
print(meeting.minute)  # 30
print(meeting.second)  # 0
```

### DateTime Operations
```python
from datetime import datetime

# Current date and time
now = datetime.now()
print(now)  # 2024-01-15 14:30:45.123456

# Create specific datetime
event = datetime(2024, 12, 25, 10, 30)
print(event)  # 2024-12-25 10:30:00

# Formatting
print(now.strftime("%Y-%m-%d"))        # 2024-01-15
print(now.strftime("%B %d, %Y"))       # January 15, 2024
print(now.strftime("%H:%M:%S"))        # 14:30:45

# Parsing
date_str = "2024-01-15"
parsed = datetime.strptime(date_str, "%Y-%m-%d")
print(parsed)
```

---

## Collections Module

Specialized container datatypes.

### Counter
```python
from collections import Counter

# Count elements
words = ['apple', 'banana', 'apple', 'cherry', 'banana', 'apple']
count = Counter(words)
print(count)  # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# Most common
print(count.most_common(2))  # [('apple', 3), ('banana', 2)]

# Elements
print(list(count.elements()))  # ['apple', 'apple', 'apple', 'banana', ...]
```

### defaultdict
```python
from collections import defaultdict

# Dictionary with default value
dd = defaultdict(int)  # Default value is 0
dd['a'] += 1
dd['b'] += 2
print(dd)  # defaultdict(<class 'int'>, {'a': 1, 'b': 2})

# With list
dd_list = defaultdict(list)
dd_list['colors'].append('red')
dd_list['colors'].append('blue')
print(dd_list)  # defaultdict(<class 'list'>, {'colors': ['red', 'blue']})
```

### namedtuple
```python
from collections import namedtuple

# Create named tuple class
Point = namedtuple('Point', ['x', 'y'])

# Create instance
p = Point(3, 4)
print(p.x, p.y)  # 3 4

# Access by index
print(p[0], p[1])  # 3 4

# Immutable
# p.x = 5  # AttributeError
```

### deque (Double-ended queue)
```python
from collections import deque

# Create deque
dq = deque([1, 2, 3])

# Add to right
dq.append(4)  # [1, 2, 3, 4]

# Add to left
dq.appendleft(0)  # [0, 1, 2, 3, 4]

# Remove from right
dq.pop()  # Returns 4, deque is [0, 1, 2, 3]

# Remove from left
dq.popleft()  # Returns 0, deque is [1, 2, 3]

# Rotate
dq.rotate(1)  # [3, 1, 2]
dq.rotate(-1)  # [1, 2, 3]
```

---

## OS Module

Interact with operating system.

### File and Directory Operations
```python
import os

# Current working directory
print(os.getcwd())

# Change directory
os.chdir('/path/to/directory')

# List directory contents
print(os.listdir('.'))

# Create directory
os.mkdir('new_folder')

# Create nested directories
os.makedirs('parent/child/grandchild')

# Remove directory
os.rmdir('new_folder')

# Check if exists
print(os.path.exists('file.txt'))
print(os.path.isfile('file.txt'))
print(os.path.isdir('folder'))
```

### Path Operations
```python
import os

# Join paths (cross-platform)
path = os.path.join('folder', 'subfolder', 'file.txt')
print(path)  # folder/subfolder/file.txt (Unix) or folder\subfolder\file.txt (Windows)

# Get absolute path
abs_path = os.path.abspath('file.txt')

# Split path
dirname = os.path.dirname('/path/to/file.txt')  # '/path/to'
basename = os.path.basename('/path/to/file.txt')  # 'file.txt'

# Split extension
name, ext = os.path.splitext('document.pdf')  # ('document', '.pdf')

# Get file size
size = os.path.getsize('file.txt')  # Size in bytes
```

### Environment Variables
```python
import os

# Get environment variable
home = os.environ.get('HOME')
path = os.environ.get('PATH')

# Set environment variable
os.environ['MY_VAR'] = 'value'
```

---

## Sys Module

System-specific parameters and functions.

### Command Line Arguments
```python
import sys

# Access command line arguments
# python script.py arg1 arg2
print(sys.argv)  # ['script.py', 'arg1', 'arg2']
print(sys.argv[0])  # script.py (script name)
print(sys.argv[1])  # arg1 (first argument)
```

### Python Version and Path
```python
import sys

# Python version
print(sys.version)
print(sys.version_info)

# Module search path
print(sys.path)

# Platform
print(sys.platform)  # 'linux', 'win32', 'darwin' (macOS)
```

### Exit Program
```python
import sys

# Exit with status code
sys.exit(0)  # Success
sys.exit(1)  # Error
```

---

## JSON Module

Work with JSON data.

### JSON Encoding (Python to JSON)
```python
import json

# Python dict to JSON string
data = {'name': 'Alice', 'age': 30, 'city': 'NYC'}
json_str = json.dumps(data)
print(json_str)  # {"name": "Alice", "age": 30, "city": "NYC"}

# Pretty print
json_str = json.dumps(data, indent=2)
print(json_str)
```

### JSON Decoding (JSON to Python)
```python
import json

# JSON string to Python dict
json_str = '{"name": "Bob", "age": 25}'
data = json.loads(json_str)
print(data)  # {'name': 'Bob', 'age': 25}
print(data['name'])  # Bob
```

### File Operations
```python
import json

# Write to file
data = {'users': [{'name': 'Alice'}, {'name': 'Bob'}]}
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)

# Read from file
with open('data.json', 'r') as f:
    loaded_data = json.load(f)
    print(loaded_data)
```

---

## Itertools Module

Efficient iterator tools.

### Infinite Iterators
```python
import itertools

# count(start, step)
for i in itertools.count(10, 2):
    if i > 20:
        break
    print(i)  # 10, 12, 14, 16, 18, 20

# cycle(iterable)
counter = 0
for item in itertools.cycle(['A', 'B', 'C']):
    if counter >= 5:
        break
    print(item)  # A, B, C, A, B
    counter += 1

# repeat(value, times)
for item in itertools.repeat('Hello', 3):
    print(item)  # Hello, Hello, Hello
```

### Combinatoric Iterators
```python
import itertools

# permutations
print(list(itertools.permutations([1, 2, 3], 2)))
# [(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]

# combinations
print(list(itertools.combinations([1, 2, 3], 2)))
# [(1, 2), (1, 3), (2, 3)]

# product (Cartesian product)
print(list(itertools.product([1, 2], ['A', 'B'])))
# [(1, 'A'), (1, 'B'), (2, 'A'), (2, 'B')]
```

### Other Useful Functions
```python
import itertools

# chain - combine iterables
print(list(itertools.chain([1, 2], [3, 4], [5])))
# [1, 2, 3, 4, 5]

# islice - slice iterator
print(list(itertools.islice(range(10), 2, 7)))
# [2, 3, 4, 5, 6]

# groupby - group consecutive items
data = [1, 1, 2, 2, 2, 3, 1]
for key, group in itertools.groupby(data):
    print(key, list(group))
# 1 [1, 1]
# 2 [2, 2, 2]
# 3 [3]
# 1 [1]
```

---

## Practical Examples

### Example 1: Password Generator
```python
import random
import string

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

print(generate_password())  # aB3$xY9&pL2!
```

### Example 2: File Backup with Timestamp
```python
import os
import shutil
from datetime import datetime

def backup_file(filename):
    if not os.path.exists(filename):
        print("File not found!")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    backup_name = f"{name}_backup_{timestamp}{ext}"
    
    shutil.copy(filename, backup_name)
    print(f"Backup created: {backup_name}")

backup_file('important.txt')
```

### Example 3: Word Frequency Counter
```python
from collections import Counter
import re

def word_frequency(text):
    # Remove punctuation and convert to lowercase
    words = re.findall(r'\w+', text.lower())
    return Counter(words)

text = "Hello world! Hello Python. Python is great."
freq = word_frequency(text)
print(freq.most_common(3))
# [('hello', 2), ('python', 2), ('world', 1)]
```

---

## Summary

✅ **math**: Mathematical functions  
✅ **random**: Random number generation  
✅ **datetime**: Date and time operations  
✅ **collections**: Specialized containers (Counter, defaultdict, deque)  
✅ **os**: Operating system interface  
✅ **sys**: System-specific functions  
✅ **json**: JSON encoding/decoding  
✅ **itertools**: Iterator tools  

---

## Next Steps
Continue to **Module 10: Practice Questions - Standard Library**
