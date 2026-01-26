# Module 8: Exception Handling

## Introduction to Exceptions

An **exception** is an error that occurs during program execution. Instead of crashing, Python allows you to handle these errors gracefully.

### What are Exceptions?
- Runtime errors that interrupt normal program flow
- Raised when Python encounters an error
- Can be caught and handled to prevent crashes

### Common Exception Types

| Exception | Cause |
|-----------|-------|
| `ZeroDivisionError` | Division by zero |
| `ValueError` | Invalid value for operation |
| `TypeError` | Invalid type for operation |
| `IndexError` | List index out of range |
| `KeyError` | Dictionary key not found |
| `FileNotFoundError` | File doesn't exist |
| `AttributeError` | Attribute doesn't exist |
| `NameError` | Variable not defined |
| `ImportError` | Module import failed |

---

## Basic Exception Handling: `try-except`

### Syntax
```python
try:
    # Code that might raise exception
    risky_code()
except ExceptionType:
    # Handle the exception
    handle_error()
```

### Example 1: Handling Division by Zero
```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
    result = None
```

### Example 2: Handling Invalid Input
```python
try:
    age = int(input("Enter age: "))
except ValueError:
    print("Please enter a valid number!")
    age = 0
```

### Example 3: Handling Multiple Operations
```python
try:
    numbers = [1, 2, 3]
    print(numbers[10])  # IndexError
except IndexError:
    print("Index out of range!")
```

---

## Catching Multiple Exceptions

### Method 1: Multiple `except` Blocks
```python
try:
    num = int(input("Enter number: "))
    result = 100 / num
except ValueError:
    print("Invalid input! Please enter a number.")
except ZeroDivisionError:
    print("Cannot divide by zero!")
```

### Method 2: Single `except` with Tuple
```python
try:
    num = int(input("Enter number: "))
    result = 100 / num
except (ValueError, ZeroDivisionError):
    print("Invalid input or division by zero!")
```

### Method 3: Catching Exception Object
```python
try:
    num = int(input("Enter number: "))
    result = 100 / num
except (ValueError, ZeroDivisionError) as e:
    print(f"Error occurred: {e}")
```

---

## The `else` Clause

Executes only if **no exception** was raised in the `try` block.

```python
try:
    num = int(input("Enter number: "))
except ValueError:
    print("Invalid input!")
else:
    print(f"You entered: {num}")
    # This runs only if no exception occurred
```

### Example: File Processing
```python
try:
    with open('data.txt', 'r') as file:
        data = file.read()
except FileNotFoundError:
    print("File not found!")
else:
    print("File successfully read!")
    process_data(data)
```

---

## The `finally` Clause

**Always executes**, whether exception occurred or not. Used for cleanup.

```python
try:
    file = open('data.txt', 'r')
    data = file.read()
except FileNotFoundError:
    print("File not found!")
else:
    print("File read successfully!")
finally:
    print("Cleanup: Closing resources")
    # This ALWAYS runs
```

### Example: Database Connection
```python
db = None
try:
    db = connect_to_database()
    db.execute_query()
except DatabaseError:
    print("Database error!")
else:
    print("Query successful!")
finally:
    if db:
        db.close()  # Always close connection
    print("Database connection closed")
```

### Complete try-except-else-finally Example
```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Cannot divide by zero!")
        return None
    except TypeError:
        print("Invalid types for division!")
        return None
    else:
        print("Division successful!")
        return result
    finally:
        print("Division operation completed")

print(divide(10, 2))   # Success
print(divide(10, 0))   # ZeroDivisionError
print(divide(10, "2")) # TypeError
```

---

## Raising Exceptions

### Using `raise` Keyword

**Syntax:**
```python
raise ExceptionType("Error message")
```

### Example 1: Raising Built-in Exception
```python
def check_age(age):
    if age < 0:
        raise ValueError("Age cannot be negative!")
    if age > 150:
        raise ValueError("Age seems unrealistic!")
    return age

try:
    age = check_age(-5)
except ValueError as e:
    print(f"Error: {e}")
```

### Example 2: Re-raising Exception
```python
try:
    value = int(input("Enter number: "))
except ValueError:
    print("Invalid input! Re-raising exception...")
    raise  # Re-raises the same exception
```

### Example 3: Raising During Exception Handling
```python
try:
    num = int(input("Enter positive number: "))
    if num < 0:
        raise ValueError("Number must be positive!")
except ValueError as e:
    print(f"Error: {e}")
```

---

## Creating Custom Exceptions

### Basic Custom Exception
```python
class CustomError(Exception):
    pass

# Usage
raise CustomError("Something went wrong!")
```

### Custom Exception with Custom Message
```python
class NegativeValueError(Exception):
    def __init__(self, value):
        self.value = value
        self.message = f"Negative value not allowed: {value}"
        super().__init__(self.message)

# Usage
try:
    balance = -100
    if balance < 0:
        raise NegativeValueError(balance)
except NegativeValueError as e:
    print(e.message)
```

### Example: Bank Account Exception
```python
class InsufficientFundsError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        message = f"Insufficient funds: Balance={balance}, Requested={amount}"
        super().__init__(message)

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
    
    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFundsError(self.balance, amount)
        self.balance -= amount
        return self.balance

# Usage
account = BankAccount(100)
try:
    account.withdraw(150)
except InsufficientFundsError as e:
    print(e)
```

---

## Exception Hierarchy

Python exceptions are organized in a hierarchy:

```
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   ├── OverflowError
    │   └── FloatingPointError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── TypeError
    ├── ValueError
    ├── NameError
    ├── AttributeError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    └── ... many more
```

### Catching Base Exception
```python
try:
    # Some code
    risky_operation()
except Exception as e:
    # Catches all exceptions except SystemExit, KeyboardInterrupt
    print(f"An error occurred: {e}")
```

⚠️ **Warning**: Avoid catching `BaseException` as it includes `SystemExit` and `KeyboardInterrupt`!

---

## Exception Chaining

### Using `from` to Chain Exceptions
```python
try:
    value = int("abc")
except ValueError as original_error:
    raise RuntimeError("Failed to process value") from original_error
```

Output shows both exceptions:
```
ValueError: invalid literal for int() with base 10: 'abc'

The above exception was the direct cause of the following exception:

RuntimeError: Failed to process value
```

---

## Best Practices

### 1. Be Specific with Exceptions
```python
# Good: Specific exception
try:
    value = int(input("Enter number: "))
except ValueError:
    print("Invalid number!")

# Avoid: Too broad
try:
    value = int(input("Enter number: "))
except Exception:  # Catches everything!
    print("Something went wrong!")
```

### 2. Don't Catch Everything
```python
# Bad: Silently ignores all errors
try:
    risky_operation()
except:
    pass  # Never do this!

# Good: Handle specific errors
try:
    risky_operation()
except SpecificError:
    handle_specific_error()
```

### 3. Use Finally for Cleanup
```python
file = None
try:
    file = open('data.txt', 'r')
    process(file)
finally:
    if file:
        file.close()

# Better: Use context manager
with open('data.txt', 'r') as file:
    process(file)
# File closes automatically
```

### 4. Provide Meaningful Error Messages
```python
# Good
if age < 0:
    raise ValueError(f"Age must be positive, got {age}")

# Less helpful
if age < 0:
    raise ValueError("Invalid age")
```

### 5. Log Exceptions
```python
import logging

try:
    risky_operation()
except Exception as e:
    logging.error(f"Operation failed: {e}")
    # Handle or re-raise
```

---

## Practical Examples

### Example 1: Safe Division Function
```python
def safe_divide(a, b):
    """Safely divide two numbers"""
    try:
        return a / b
    except ZeroDivisionError:
        print("Error: Division by zero!")
        return None
    except TypeError:
        print("Error: Both arguments must be numbers!")
        return None

print(safe_divide(10, 2))    # 5.0
print(safe_divide(10, 0))    # None (error message)
print(safe_divide(10, "2"))  # None (error message)
```

### Example 2: File Reader with Error Handling
```python
def read_file(filename):
    """Read file with comprehensive error handling"""
    try:
        with open(filename, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return None
    except PermissionError:
        print(f"Error: Permission denied for '{filename}'!")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

content = read_file('data.txt')
if content:
    print(content)
```

### Example 3: Input Validation Loop
```python
def get_positive_integer(prompt):
    """Keep asking until valid positive integer is entered"""
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                raise ValueError("Number must be positive!")
            return value
        except ValueError as e:
            print(f"Invalid input: {e}")
            print("Please try again.")

age = get_positive_integer("Enter your age: ")
print(f"Age: {age}")
```

### Example 4: List Access with Error Handling
```python
def safe_get(lst, index, default=None):
    """Safely get item from list"""
    try:
        return lst[index]
    except IndexError:
        return default
    except TypeError:
        print("Error: First argument must be a list!")
        return default

numbers = [1, 2, 3]
print(safe_get(numbers, 1))      # 2
print(safe_get(numbers, 10))     # None
print(safe_get(numbers, 10, -1)) # -1 (custom default)
```

### Example 5: Multiple Operations with Validation
```python
def calculate(x, y, operation):
    """Perform calculation with error handling"""
    try:
        x = float(x)
        y = float(y)
    except ValueError:
        raise ValueError("x and y must be numbers!")
    
    try:
        if operation == 'add':
            return x + y
        elif operation == 'subtract':
            return x - y
        elif operation == 'multiply':
            return x * y
        elif operation == 'divide':
            if y == 0:
                raise ZeroDivisionError("Cannot divide by zero!")
            return x / y
        else:
            raise ValueError(f"Unknown operation: {operation}")
    except Exception as e:
        print(f"Calculation error: {e}")
        return None

# Usage
try:
    result = calculate("10", "2", "divide")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Summary

✅ **try-except** catches and handles exceptions  
✅ **Multiple exceptions** can be caught separately or together  
✅ **else** clause runs if no exception occurred  
✅ **finally** clause always executes (cleanup)  
✅ **raise** keyword raises exceptions manually  
✅ **Custom exceptions** created by inheriting from Exception  
✅ **Exception hierarchy** organizes exception types  
✅ **Best practices**: Be specific, don't catch everything, use meaningful messages  

---

## Next Steps
Continue to **Module 8: Practice Questions - Exception Handling**
