# Module 1: Practice Questions - Python Basics and Interpreter

## Instructions
- Answer all 20 questions
- Don't look at the answers until you've attempted all questions
- Score yourself: Each correct answer = 5 points (Total: 100 points)
- **Passing score: 80/100 (16 correct answers)**
- Review incorrect answers and re-read the theory

---

## Questions

### Question 1
What will be the output of the following code?
```python
>>> 5
>>> 10
>>> _
```
**A)** 5  
**B)** 10  
**C)** 15  
**D)** NameError

---

### Question 2
Which of the following is NOT a valid Python variable name?
**A)** `_private`  
**B)** `2ndPlace`  
**C)** `myVar123`  
**D)** `__init__`

---

### Question 3
What is the output of this code?
```python
x = 5
y = 10
x, y = y, x
print(x, y)
```
**A)** 5 10  
**B)** 10 5  
**C)** 15 15  
**D)** SyntaxError

---

### Question 4
What does the following command do?
```bash
python -c "print('Hello')"
```
**A)** Compiles Python code  
**B)** Executes the string as Python code  
**C)** Creates a new Python file  
**D)** Shows Python help

---

### Question 5
Which encoding is the default in Python 3?
**A)** ASCII  
**B)** Latin-1  
**C)** UTF-8  
**D)** UTF-16

---

### Question 6
What will be the output?
```python
print("A", "B", "C", sep="-", end="!")
print("D")
```
**A)** A B C!D  
**B)** A-B-C!D  
**C)** A B C D  
**D)** A-B-CD

---

### Question 7
What is the correct way to comment multiple lines in Python?
**A)** `/* comment */`  
**B)** `// comment`  
**C)** `# comment on each line`  
**D)** `<!-- comment -->`

---

### Question 8
What will be the value of `x`?
```python
x = y = z = 10
x += 5
```
**A)** 10  
**B)** 15  
**C)** 5  
**D)** NameError

---

### Question 9
Which of the following is a Python keyword?
**A)** `print`  
**B)** `elif`  
**C)** `input`  
**D)** `type`

---

### Question 10
What type of error will this code raise?
```python
if True:
print("Hello")
```
**A)** SyntaxError  
**B)** IndentationError  
**C)** NameError  
**D)** TypeError

---

### Question 11
What will be the output?
```python
age = input("Enter age: ")  # User enters: 25
print(type(age))
```
**A)** `<class 'int'>`  
**B)** `<class 'str'>`  
**C)** `<class 'float'>`  
**D)** TypeError

---

### Question 12
How do you exit the Python interactive shell? (Select all that apply)
**A)** `exit()`  
**B)** `quit()`  
**C)** Ctrl+D (Unix)  
**D)** All of the above

---

### Question 13
What is the output of this code?
```python
print(f"Result: {10 + 5}")
```
**A)** Result: 10 + 5  
**B)** Result: 15  
**C)** Result: {15}  
**D)** SyntaxError

---

### Question 14
Which operator has the highest precedence?
**A)** `+`  
**B)** `*`  
**C)** `**`  
**D)** `()`

---

### Question 15
What will be the output?
```python
x = 10
x //= 3
print(x)
```
**A)** 3.333...  
**B)** 3  
**C)** 4  
**D)** 10

---

### Question 16
Which of the following correctly converts a string to an integer?
**A)** `int("100")`  
**B)** `"100".toInt()`  
**C)** `Integer("100")`  
**D)** `convert("100", int)`

---

### Question 17
What is the correct shebang line for a Python 3 script on Unix?
**A)** `#!python3`  
**B)** `#!/usr/bin/python3`  
**C)** `#!/usr/bin/env python3`  
**D)** `#python3`

---

### Question 18
What will this code print?
```python
print(bool(0))
print(bool(1))
print(bool(""))
```
**A)** True, True, True  
**B)** False, True, False  
**C)** False, False, False  
**D)** True, False, True

---

### Question 19
How many spaces is the recommended indentation in Python (PEP 8)?
**A)** 2  
**B)** 3  
**C)** 4  
**D)** 8

---

### Question 20
What will be the output?
```python
x = 5
x **= 2
print(x)
```
**A)** 7  
**B)** 10  
**C)** 25  
**D)** Error

---

## Answers

### Answer 1: **B) 10**
**Explanation**: In Python's interactive mode, the underscore `_` holds the result of the **last expression** that was evaluated. Since `10` was the last expression, `_` equals `10`.

---

### Answer 2: **B) 2ndPlace**
**Explanation**: Variable names in Python **cannot start with a digit**. Valid names must start with a letter (a-z, A-Z) or an underscore (_).
- `_private` ✅ (starts with underscore)
- `2ndPlace` ❌ (starts with digit)
- `myVar123` ✅ (starts with letter)
- `__init__` ✅ (starts with underscore)

---

### Answer 3: **B) 10 5**
**Explanation**: This is a **swap operation** using tuple unpacking. The values of `x` and `y` are swapped simultaneously:
```python
x = 5, y = 10
x, y = y, x  # x becomes 10, y becomes 5
```

---

### Answer 4: **B) Executes the string as Python code**
**Explanation**: The `-c` option allows you to execute a Python command directly from the command line without creating a file.
```bash
python -c "print('Hello')"  # Prints: Hello
```

---

### Answer 5: **C) UTF-8**
**Explanation**: Python 3 uses **UTF-8** as the default source code encoding. This allows Unicode characters to be used directly in strings and identifiers.

---

### Answer 6: **B) A-B-C!D**
**Explanation**: 
- `sep="-"` separates the arguments with a hyphen
- `end="!"` changes the end character from newline to `!`
- The second `print("D")` continues on a new line

Output breakdown:
```
A-B-C!D
```

---

### Answer 7: **C) # comment on each line**
**Explanation**: Python does not have a multi-line comment syntax like `/* */` in C/Java. You must use `#` on each line, or use a multi-line string `"""..."""` (which is technically a docstring, not a comment).

---

### Answer 8: **B) 15**
**Explanation**: 
```python
x = y = z = 10  # All three variables are 10
x += 5          # x = x + 5 = 15
# y and z remain 10
```

---

### Answer 9: **B) elif**
**Explanation**: `elif` is a Python **keyword** (reserved word). 
- `print`, `input`, and `type` are **built-in functions**, not keywords.
- Keywords cannot be used as variable names.

Check all keywords with:
```python
import keyword
print(keyword.kwlist)
```

---

### Answer 10: **B) IndentationError**
**Explanation**: Python requires indentation after a colon `:`. The correct code should be:
```python
if True:
    print("Hello")  # Must be indented
```

---

### Answer 11: **B) `<class 'str'>`**
**Explanation**: The `input()` function **always returns a string**, regardless of what the user types. To use it as an integer, you must convert it:
```python
age = int(input("Enter age: "))  # Converts to int
```

---

### Answer 12: **D) All of the above**
**Explanation**: All three methods exit the Python interactive shell:
- `exit()` - Built-in function
- `quit()` - Built-in function
- `Ctrl+D` (Unix/Mac) or `Ctrl+Z` (Windows) - Keyboard shortcut

---

### Answer 13: **B) Result: 15**
**Explanation**: **f-strings** (formatted string literals) evaluate expressions inside `{}`:
```python
f"Result: {10 + 5}"  # Evaluates 10+5 = 15
# Output: Result: 15
```

---

### Answer 14: **D) `()`**
**Explanation**: **Parentheses** have the highest precedence in Python, forcing the enclosed expression to be evaluated first.

Precedence order (high to low):
1. `()` - Parentheses
2. `**` - Exponentiation
3. `*`, `/`, `//`, `%` - Multiplication, Division
4. `+`, `-` - Addition, Subtraction

---

### Answer 15: **B) 3**
**Explanation**: `//=` is **floor division** (integer division):
```python
x = 10
x //= 3  # x = x // 3 = 10 // 3 = 3
```
Note: Regular division `/` would give `3.333...`

---

### Answer 16: **A) `int("100")`**
**Explanation**: The `int()` function converts a string to an integer:
```python
int("100")  # Returns 100 (integer)
```
- `"100".toInt()` ❌ (not a Python method)
- `Integer("100")` ❌ (not a Python class)
- `convert()` ❌ (not a built-in function)

---

### Answer 17: **C) `#!/usr/bin/env python3`**
**Explanation**: This is the **recommended shebang line** for Python 3 scripts on Unix-like systems. It uses `env` to locate `python3` in the user's PATH, making the script more portable.

```python
#!/usr/bin/env python3
print("This script can be executed directly")
```

Make it executable: `chmod +x script.py`

---

### Answer 18: **B) False, True, False**
**Explanation**: `bool()` converts values to Boolean:
```python
bool(0)   # False (0 is falsy)
bool(1)   # True (non-zero is truthy)
bool("")  # False (empty string is falsy)
```

**Falsy values**: `0`, `0.0`, `""`, `[]`, `{}`, `()`, `None`, `False`  
**Truthy values**: Everything else

---

### Answer 19: **C) 4**
**Explanation**: **PEP 8** (Python's style guide) recommends **4 spaces** per indentation level. Never mix tabs and spaces!

---

### Answer 20: **C) 25**
**Explanation**: `**=` is the **exponentiation assignment operator**:
```python
x = 5
x **= 2  # x = x ** 2 = 5 ** 2 = 25
```
`**` is the exponentiation operator (power).

---

## Scoring Guide

**Your Score: ___ / 100**

- **90-100**: Excellent! Move to Module 2
- **80-89**: Good! Review missed questions, then proceed
- **70-79**: Fair. Re-read sections you struggled with
- **Below 70**: Study the module again before proceeding

---

## Common Mistakes Analysis

### Most Commonly Missed Questions:
1. **Question 1** (Underscore in REPL): Remember `_` stores the last evaluated expression
2. **Question 9** (Keywords vs Functions): Keywords are reserved words; functions are callable objects
3. **Question 11** (input() returns string): Always convert input() to the needed type
4. **Question 15** (Floor division): `//` gives integer result, `/` gives float

---

## Review Checklist

After completing this practice test, ensure you understand:
- [ ] How to use Python's interactive mode
- [ ] Variable naming rules and conventions
- [ ] The difference between keywords and built-in functions
- [ ] How `print()` and `input()` work
- [ ] Indentation requirements
- [ ] Operator precedence
- [ ] Type conversion (int, float, str, bool)
- [ ] Assignment operators (=, +=, -=, etc.)
- [ ] Default encoding (UTF-8)
- [ ] How to exit Python shell

---

## Next Steps

✅ **If you scored 80+**: Proceed to **Module 2: Data Types and Operations**  
❌ **If you scored below 80**: Review the [theory document](./01-python-basics-and-interpreter.md) and retake this test

---

**Keep practicing! 🐍**
