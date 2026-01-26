# Module 6 Part 2: Practice Questions - Packages

## Instructions
- Answer all 20 questions
- Score: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**

---

## Questions

### Question 1
What file is required to make a directory a Python package (in Python 2)?
**A)** `__init__.py`  
**B)** `__main__.py`  
**C)** `package.py`  
**D)** `setup.py`

---

### Question 2
What is the output?
```python
# mypackage/__init__.py contains: x = 10
import mypackage
print(mypackage.x)
```
**A)** 10  
**B)** NameError  
**C)** x  
**D)** Error

---

### Question 3
Given this structure, what imports module1?
```
mypack/
    __init__.py
    module1.py
```
**A)** `import mypack.module1`  
**B)** `import module1`  
**C)** `from mypack import __init__`  
**D)** `import mypack.__init__`

---

### Question 4
What does a single dot (`.`) represent in relative imports?
**A)** Current package  
**B)** Parent package  
**C)** Root package  
**D)** Subpackage

---

### Question 5
What will be printed?
```python
# package/__init__.py contains: __all__ = ['func1']
# Also defines: func1() and func2()
from package import *
print(dir())
```
**A)** Only 'func1' appears in namespace  
**B)** Both 'func1' and 'func2' appear  
**C)** Nothing  
**D)** Error

---

### Question 6
How do you run a package as a script?
**A)** `python -m packagename`  
**B)** `python packagename`  
**C)** `run packagename`  
**D)** `exec packagename`

---

### Question 7
What file enables running a package with `python -m`?
**A)** `__main__.py`  
**B)** `__init__.py`  
**C)** `main.py`  
**D)** `run.py`

---

### Question 8
Given this structure, what imports helpers from utils?
```
myapp/
    __init__.py
    main.py
    utils/
        __init__.py
        helpers.py
```
**A)** `from myapp.utils import helpers`  
**B)** `import helpers`  
**C)** `from utils import helpers`  
**D)** All of the above

---

### Question 9
What does `..` represent in relative imports?
**A)** Parent package  
**B)** Current package  
**C)** Two levels up  
**D)** Error

---

### Question 10
What is the output?
```python
# pkg/__init__.py contains:
# __version__ = "1.0"
import pkg
print(pkg.__version__)
```
**A)** 1.0  
**B)** "1.0"  
**C)** NameError  
**D)** Error

---

### Question 11
Which import statement is absolute?
**A)** `from mypackage.module import func`  
**B)** `from . import module`  
**C)** `from .. import module`  
**D)** `from .module import func`

---

### Question 12
What will be imported?
```python
# mypack/__init__.py contains:
# __all__ = ['a', 'b']
# Also defines: a, b, c
from mypack import *
```
**A)** Only a and b  
**B)** Only a, b, and c  
**C)** All names from mypack  
**D)** Nothing

---

### Question 13
Given this in `utils/validators.py`, what's the correct import?
```python
# Need to import helpers from same package
```
**A)** `from . import helpers`  
**B)** `import helpers`  
**C)** `from .. import helpers`  
**D)** `import .helpers`

---

### Question 14
What is output?
```python
# package/__init__.py is empty
import package
print(type(package))
```
**A)** <class 'module'>  
**B)** <class 'package'>  
**C)** <class 'dict'>  
**D)** Error

---

### Question 15
What's the recommended practice for package names?
**A)** lowercase with underscores  
**B)** CamelCase  
**C)** UPPERCASE  
**D)** Any style

---

### Question 16
What will be printed?
```python
# mypack/sub/__init__.py exists but is empty
import mypack.sub
print(hasattr(mypack, 'sub'))
```
**A)** True  
**B)** False  
**C)** NameError  
**D)** Error

---

### Question 17
From `myapp/utils/helpers.py`, how to import from `myapp/main.py`?
**A)** `from ..main import function`  
**B)** `from .main import function`  
**C)** `from main import function`  
**D)** `import main.function`

---

### Question 18
What does `__init__.py` do when imported?
**A)** Executes code in the file  
**B)** Creates package object only  
**C)** Does nothing  
**D)** Raises ImportError

---

### Question 19
In Python 3.3+, is `__init__.py` required for packages?
**A)** No, but recommended  
**B)** Yes, always required  
**C)** Only for subpackages  
**D)** Never needed

---

### Question 20
What will be printed?
```python
# mypack/__init__.py contains: name = "MyPackage"
# mypack/module.py contains: name = "Module"
import mypack
import mypack.module
print(mypack.name, mypack.module.name)
```
**A)** MyPackage Module  
**B)** Module MyPackage  
**C)** MyPackage MyPackage  
**D)** Error

---

## Answers

### Answer 1: **A) `__init__.py`**
**Explanation**: `__init__.py` marks directory as package (required in Python 2, optional but recommended in Python 3.3+)

---

### Answer 2: **A) 10**
**Explanation**: Variables defined in `__init__.py` are accessible as package attributes

---

### Answer 3: **A) `import mypack.module1`**
**Explanation**: Use dot notation to access modules within packages

---

### Answer 4: **A) Current package**
**Explanation**: Single dot (`.`) refers to current package in relative imports

---

### Answer 5: **A) Only 'func1' appears in namespace**
**Explanation**: `__all__` controls what's imported with `from package import *`

---

### Answer 6: **A) `python -m packagename`**
**Explanation**: `-m` flag runs package as module (executes `__main__.py`)

---

### Answer 7: **A) `__main__.py`**
**Explanation**: `__main__.py` is executed when package is run with `python -m`

---

### Answer 8: **A) `from myapp.utils import helpers`**
**Explanation**: Use full package path for absolute import (recommended)

---

### Answer 9: **A) Parent package**
**Explanation**: Two dots (`..`) refers to parent package in relative imports

---

### Answer 10: **A) 1.0**
**Explanation**: Package attributes from `__init__.py` accessed via package name

---

### Answer 11: **A) `from mypackage.module import func`**
**Explanation**: Absolute imports use full path from package root

---

### Answer 12: **A) Only a and b**
**Explanation**: `__all__` explicitly lists what's exported with wildcard import

---

### Answer 13: **A) `from . import helpers`**
**Explanation**: Use `.` to import from same package (relative import)

---

### Answer 14: **A) <class 'module'>**
**Explanation**: Packages are module objects in Python

---

### Answer 15: **A) lowercase with underscores**
**Explanation**: PEP 8 recommends lowercase package names with underscores

---

### Answer 16: **A) True**
**Explanation**: Importing subpackage makes it an attribute of parent package

---

### Answer 17: **A) `from ..main import function`**
**Explanation**: Use `..` to go up one level to parent package

---

### Answer 18: **A) Executes code in the file**
**Explanation**: Code in `__init__.py` runs when package is imported

---

### Answer 19: **A) No, but recommended**
**Explanation**: Python 3.3+ allows namespace packages without `__init__.py`, but it's still recommended

---

### Answer 20: **A) MyPackage Module**
**Explanation**: Each module has its own namespace; `mypack.name` != `mypack.module.name`

---

## Next Steps
✅ **If you scored 80+**: Proceed to **Module 7: File Operations**  
❌ **If you scored below 80**: Review packages theory and practice more
