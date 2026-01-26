# Module 6 Part 2: Python Packages

## What is a Package?

A **package** is a way of organizing related modules into a directory hierarchy. It's essentially a directory containing Python files and a special `__init__.py` file.

### Package vs Module
- **Module**: A single Python file (.py)
- **Package**: A directory containing multiple modules and an `__init__.py` file

---

## Package Structure

### Basic Package Structure
```
mypackage/
    __init__.py
    module1.py
    module2.py
    subpackage/
        __init__.py
        module3.py
```

### The `__init__.py` File
- **Required** in Python 2 and older Python 3 (before 3.3)
- **Optional** but recommended in Python 3.3+
- Marks directory as Python package
- Can contain initialization code
- Can define `__all__` variable

---

## Creating a Package

### Example: Creating a Calculator Package

**Directory Structure:**
```
calculator/
    __init__.py
    basic.py
    advanced.py
```

**calculator/__init__.py:**
```python
"""Calculator package for basic and advanced operations"""
__version__ = "1.0.0"

# Import commonly used functions
from .basic import add, subtract
from .advanced import power, factorial

# Define what's exported with "from calculator import *"
__all__ = ['add', 'subtract', 'power', 'factorial']
```

**calculator/basic.py:**
```python
"""Basic arithmetic operations"""

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract b from a"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

**calculator/advanced.py:**
```python
"""Advanced mathematical operations"""
import math

def power(base, exponent):
    """Raise base to exponent"""
    return base ** exponent

def factorial(n):
    """Calculate factorial of n"""
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    return math.factorial(n)

def sqrt(n):
    """Calculate square root"""
    if n < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(n)
```

---

## Importing from Packages

### Method 1: Import Entire Module
```python
import calculator.basic

result = calculator.basic.add(5, 3)
print(result)  # Output: 8
```

### Method 2: Import Specific Module
```python
from calculator import basic

result = basic.add(5, 3)
print(result)  # Output: 8
```

### Method 3: Import Specific Function
```python
from calculator.basic import add, multiply

print(add(5, 3))       # Output: 8
print(multiply(5, 3))  # Output: 15
```

### Method 4: Import with Alias
```python
from calculator.basic import add as addition

result = addition(10, 5)
print(result)  # Output: 15
```

### Method 5: Import Everything (Not Recommended)
```python
from calculator.basic import *

# All functions from basic.py are now available
print(add(2, 3))      # Output: 5
print(subtract(10, 4))  # Output: 6
```

---

## Subpackages

### Creating Nested Package Structure

**Directory Structure:**
```
mathtools/
    __init__.py
    arithmetic/
        __init__.py
        basic.py
        advanced.py
    geometry/
        __init__.py
        shapes.py
        areas.py
```

**mathtools/arithmetic/basic.py:**
```python
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
```

**mathtools/geometry/shapes.py:**
```python
import math

def circle_area(radius):
    return math.pi * radius ** 2

def rectangle_area(length, width):
    return length * width
```

### Importing from Subpackages
```python
# Method 1: Full path
import mathtools.arithmetic.basic
result = mathtools.arithmetic.basic.add(5, 3)

# Method 2: From subpackage
from mathtools.arithmetic import basic
result = basic.add(5, 3)

# Method 3: Direct function import
from mathtools.geometry.shapes import circle_area
area = circle_area(5)
```

---

## Relative Imports

Relative imports use dots (`.`) to specify location relative to current module.

### Syntax
- `.` = current package
- `..` = parent package
- `...` = grandparent package

### Example with Relative Imports

**Package Structure:**
```
myapp/
    __init__.py
    main.py
    utils/
        __init__.py
        helpers.py
        validators.py
```

**myapp/utils/validators.py:**
```python
from . import helpers  # Import from same package
from ..main import some_function  # Import from parent package

def validate_email(email):
    # Use helper from same package
    return helpers.check_format(email)
```

**myapp/main.py:**
```python
from .utils import validators  # Relative import

email = "test@example.com"
if validators.validate_email(email):
    print("Valid email")
```

### Absolute vs Relative Imports

**Absolute Import (Recommended):**
```python
from myapp.utils.helpers import format_name
```

**Relative Import:**
```python
from .helpers import format_name
```

**When to Use:**
- **Absolute**: More readable, works from anywhere
- **Relative**: Useful within packages, makes package self-contained

---

## The `__all__` Variable

Controls what is exported with `from package import *`

**Example:**
```python
# mypackage/__init__.py
__all__ = ['function1', 'function2']

def function1():
    pass

def function2():
    pass

def _internal_function():  # Not exported
    pass
```

**Usage:**
```python
from mypackage import *
# Only function1 and function2 are imported
# _internal_function is NOT imported
```

---

## Package Initialization

The `__init__.py` file runs when package is imported.

**Example:**
```python
# logger/__init__.py
import logging

# Configure logging when package is imported
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create package-level logger
logger = logging.getLogger(__name__)

# Package metadata
__version__ = "1.0.0"
__author__ = "Your Name"

# Import main components
from .handlers import FileHandler, ConsoleHandler
from .formatters import JSONFormatter, XMLFormatter
```

---

## Namespace Packages (Python 3.3+)

Packages without `__init__.py` that can span multiple directories.

**Structure:**
```
project1/
    mynamespace/
        module1.py

project2/
    mynamespace/
        module2.py
```

Both directories contribute to `mynamespace` package.

```python
# Can import from both
from mynamespace import module1
from mynamespace import module2
```

---

## Common Package Patterns

### 1. Single Module Package
```
mypackage/
    __init__.py  # Contains all code
```

### 2. Flat Package
```
mypackage/
    __init__.py
    module1.py
    module2.py
    module3.py
```

### 3. Nested Package
```
mypackage/
    __init__.py
    core/
        __init__.py
        engine.py
    utils/
        __init__.py
        helpers.py
```

### 4. Application Package
```
myapp/
    __init__.py
    __main__.py  # Allows: python -m myapp
    config.py
    models/
    views/
    controllers/
```

---

## The `__main__.py` File

Allows package to be run as a script.

**mypackage/__main__.py:**
```python
def main():
    print("Running mypackage")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python -m mypackage  # Runs __main__.py
```

---

## Package Best Practices

### 1. Clear Structure
```
mypackage/
    __init__.py       # Package initialization
    core.py           # Core functionality
    utils.py          # Utility functions
    exceptions.py     # Custom exceptions
    constants.py      # Constants
```

### 2. Proper Naming
- Use lowercase names
- Use underscores for multi-word names
- Avoid Python keywords

### 3. Documentation
```python
# mypackage/__init__.py
"""
MyPackage - A comprehensive toolkit

This package provides tools for:
- Data processing
- File handling
- Network operations

Example:
    >>> from mypackage import process_data
    >>> result = process_data(data)
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = ['process_data', 'handle_file']
```

### 4. Minimize `__init__.py`
```python
# Good: Minimal __init__.py
from .core import main_function
from .utils import helper_function

__all__ = ['main_function', 'helper_function']
```

### 5. Use Relative Imports Within Package
```python
# Within package, use relative imports
from .utils import helper
from ..parent_module import function
```

---

## Real-World Example: Web Framework Package

```
webframework/
    __init__.py
    server.py
    routing/
        __init__.py
        router.py
        handlers.py
    database/
        __init__.py
        connection.py
        models.py
    utils/
        __init__.py
        validators.py
        helpers.py
```

**webframework/__init__.py:**
```python
"""WebFramework - A lightweight web framework"""

__version__ = "2.0.0"

# Import main components for easy access
from .server import Server
from .routing.router import Router
from .database.connection import Database

# Define public API
__all__ = ['Server', 'Router', 'Database']

# Package-level configuration
DEFAULT_PORT = 8000
DEFAULT_HOST = '0.0.0.0'
```

**Usage:**
```python
from webframework import Server, Router

app = Server()
router = Router()

@router.route('/')
def home():
    return "Welcome!"

app.run()
```

---

## Summary

✅ **Packages** organize related modules into directories  
✅ **`__init__.py`** marks directory as package  
✅ **Import methods**: import package.module, from package import module  
✅ **Subpackages** create hierarchical structure  
✅ **Relative imports** use dots (`.`, `..`)  
✅ **`__all__`** controls wildcard imports  
✅ **`__main__.py`** allows package to run as script  

---

## Next Steps
Continue to **Module 6: Practice Questions - Packages**
