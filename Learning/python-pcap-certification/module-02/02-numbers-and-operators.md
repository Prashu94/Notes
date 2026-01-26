# Module 2: Numbers and Operators

## Table of Contents
1. [Numeric Data Types](#numeric-data-types)
2. [Arithmetic Operators](#arithmetic-operators)
3. [Comparison Operators](#comparison-operators)
4. [Logical Operators](#logical-operators)
5. [Bitwise Operators](#bitwise-operators)
6. [Assignment Operators](#assignment-operators)
7. [Identity and Membership Operators](#identity-and-membership-operators)
8. [Operator Precedence](#operator-precedence)
9. [Type Conversion](#type-conversion)
10. [Math Functions and Module](#math-functions-and-module)

---

## 1. Numeric Data Types

### Integer (`int`)
Whole numbers without decimal point, unlimited precision.

```python
# Integer literals
positive = 42
negative = -17
zero = 0

# Different bases
binary = 0b1010      # Binary (base 2) = 10
octal = 0o12         # Octal (base 8) = 10
hexadecimal = 0xA    # Hexadecimal (base 16) = 10

# Large numbers (underscores for readability)
million = 1_000_000
billion = 1_000_000_000

# Verify type
print(type(42))  # <class 'int'>
```

### Floating Point (`float`)
Numbers with decimal point, based on IEEE 754 double precision.

```python
# Float literals
pi = 3.14159
negative = -2.5
zero_float = 0.0

# Scientific notation
speed_of_light = 3e8      # 3 × 10^8 = 300000000.0
planck = 6.626e-34        # 6.626 × 10^-34

# Special values
infinity = float('inf')
neg_infinity = float('-inf')
not_a_number = float('nan')

print(type(3.14))  # <class 'float'>
```

### Complex Numbers (`complex`)
Numbers with real and imaginary parts.

```python
# Complex literals
z1 = 3 + 4j
z2 = complex(5, 6)  # 5 + 6j

# Access real and imaginary parts
print(z1.real)      # 3.0
print(z1.imag)      # 4.0

# Complex arithmetic
z3 = z1 + z2        # (8+10j)
z4 = z1 * z2        # (-9+38j)

print(type(3+4j))   # <class 'complex'>
```

---

## 2. Arithmetic Operators

### Basic Arithmetic
```python
# Addition
result = 10 + 5        # 15

# Subtraction
result = 10 - 5        # 5

# Multiplication
result = 10 * 5        # 50

# Division (always returns float)
result = 10 / 5        # 2.0
result = 7 / 2         # 3.5

# Floor Division (integer division)
result = 7 // 2        # 3 (rounds down)
result = -7 // 2       # -4 (rounds down toward negative infinity)

# Modulo (remainder)
result = 7 % 2         # 1
result = 10 % 3        # 1

# Exponentiation
result = 2 ** 3        # 8 (2^3)
result = 5 ** 2        # 25 (5^2)
result = 9 ** 0.5      # 3.0 (square root)
```

### Division Behavior
```python
# Regular division always returns float
print(10 / 5)          # 2.0
print(10 / 3)          # 3.3333333333333335

# Floor division returns int (if both operands are int)
print(10 // 3)         # 3
print(10.0 // 3)       # 3.0 (float operand = float result)

# Negative numbers
print(-10 // 3)        # -4 (rounds toward negative infinity)
print(-10 / 3)         # -3.3333333333333335
```

### Modulo with Negative Numbers
```python
print(7 % 3)           # 1
print(-7 % 3)          # 2
print(7 % -3)          # -2
print(-7 % -3)         # -1

# Formula: a % b has the sign of b
# 7 % 3: 7 = 3*2 + 1 → 1
# -7 % 3: -7 = 3*(-3) + 2 → 2
```

### Unary Operators
```python
x = 5

# Unary plus (no effect)
result = +x            # 5

# Unary minus (negation)
result = -x            # -5

# Double negation
result = --x           # 5
```

---

## 3. Comparison Operators

### Relational Operators
```python
# Equal to
print(5 == 5)          # True
print(5 == 6)          # False

# Not equal to
print(5 != 6)          # True
print(5 != 5)          # False

# Greater than
print(10 > 5)          # True
print(5 > 10)          # False

# Less than
print(5 < 10)          # True
print(10 < 5)          # False

# Greater than or equal to
print(10 >= 10)        # True
print(10 >= 5)         # True

# Less than or equal to
print(5 <= 10)         # True
print(5 <= 5)          # True
```

### Chaining Comparisons
```python
# Multiple comparisons in one expression
x = 5
print(1 < x < 10)      # True (equivalent to: 1 < x and x < 10)
print(10 > x >= 5)     # True

# More complex chains
print(1 < 2 < 3 < 4)   # True
print(1 < 2 > 3)       # False (2 is not > 3)
```

### Comparing Different Types
```python
# Comparing int and float
print(5 == 5.0)        # True (values are equal)
print(5 is 5.0)        # False (different types)

# Comparing with bool
print(1 == True)       # True
print(0 == False)      # True
print(2 == True)       # False
```

---

## 4. Logical Operators

### Boolean Operators
```python
# AND - Both must be True
print(True and True)      # True
print(True and False)     # False
print(False and False)    # False

# OR - At least one must be True
print(True or False)      # True
print(False or False)     # False

# NOT - Inverts the boolean value
print(not True)           # False
print(not False)          # True
```

### Short-Circuit Evaluation
```python
# AND stops at first False
result = False and (1/0)  # No error! Doesn't evaluate second part
print(result)             # False

# OR stops at first True
result = True or (1/0)    # No error!
print(result)             # True

# Practical example
x = 10
if x > 0 and x < 100:     # Both conditions checked
    print("Valid")
```

### Logical Operators with Non-Boolean Values
```python
# AND returns first falsy value or last value
print(5 and 10)           # 10
print(0 and 10)           # 0
print(None and 5)         # None

# OR returns first truthy value or last value
print(5 or 10)            # 5
print(0 or 10)            # 10
print(None or 0)          # 0

# Practical use: default values
name = ""
display_name = name or "Guest"  # "Guest"
```

### Truthiness and Falsiness
```python
# Falsy values (evaluate to False)
bool(0)                   # False
bool(0.0)                 # False
bool("")                  # False
bool([])                  # False
bool({})                  # False
bool(())                  # False
bool(None)                # False
bool(False)               # False

# Truthy values (everything else)
bool(1)                   # True
bool(-1)                  # True
bool("text")              # True
bool([1])                 # True
bool(" ")                 # True (non-empty string)
```

---

## 5. Bitwise Operators

### Binary Representation
```python
# View binary representation
print(bin(10))            # 0b1010
print(bin(5))             # 0b101

# Convert binary to int
print(int('1010', 2))     # 10
```

### Bitwise AND (`&`)
```python
# AND: Both bits must be 1
#   1010 (10)
# & 1100 (12)
# ------
#   1000 (8)
result = 10 & 12          # 8
print(bin(result))        # 0b1000
```

### Bitwise OR (`|`)
```python
# OR: At least one bit must be 1
#   1010 (10)
# | 1100 (12)
# ------
#   1110 (14)
result = 10 | 12          # 14
```

### Bitwise XOR (`^`)
```python
# XOR: Bits must be different
#   1010 (10)
# ^ 1100 (12)
# ------
#   0110 (6)
result = 10 ^ 12          # 6

# XOR trick: swap without temp variable
a, b = 5, 10
a = a ^ b
b = a ^ b
a = a ^ b
print(a, b)               # 10, 5
```

### Bitwise NOT (`~`)
```python
# NOT: Inverts all bits (two's complement)
# ~x = -(x + 1)
result = ~10              # -11
result = ~-5              # 4
```

### Bit Shifts
```python
# Left shift (<<): Multiply by 2^n
result = 5 << 1           # 10 (5 * 2^1)
result = 5 << 2           # 20 (5 * 2^2)

# Right shift (>>): Divide by 2^n (floor division)
result = 20 >> 1          # 10 (20 / 2^1)
result = 20 >> 2          # 5 (20 / 2^2)

# Negative numbers
result = -10 >> 1         # -5
```

### Practical Uses
```python
# Check if number is even/odd
def is_even(n):
    return n & 1 == 0     # Last bit is 0 for even

# Fast multiplication/division by powers of 2
x = 7 << 3                # 7 * 8 = 56
y = 64 >> 2               # 64 / 4 = 16

# Flags and permissions
READ = 1                  # 0b001
WRITE = 2                 # 0b010
EXECUTE = 4               # 0b100

permissions = READ | WRITE  # 0b011 = 3
has_write = permissions & WRITE != 0  # True
```

---

## 6. Assignment Operators

### Compound Assignment
```python
x = 10

# Arithmetic
x += 5     # x = x + 5
x -= 3     # x = x - 3
x *= 2     # x = x * 2
x /= 4     # x = x / 4
x //= 2    # x = x // 2
x %= 3     # x = x % 3
x **= 2    # x = x ** 2

# Bitwise
x &= 0b1100   # x = x & 0b1100
x |= 0b0011   # x = x | 0b0011
x ^= 0b1010   # x = x ^ 0b1010
x <<= 2       # x = x << 2
x >>= 1       # x = x >> 1
```

### Walrus Operator (`:=`) - Python 3.8+
```python
# Assignment expression
if (n := len([1, 2, 3])) > 2:
    print(f"List has {n} items")

# In while loops
while (line := input("Enter: ")) != "quit":
    print(f"You entered: {line}")

# In list comprehensions
data = [1, 2, 3, 4, 5]
squares = [y for x in data if (y := x**2) > 10]
```

---

## 7. Identity and Membership Operators

### Identity Operators (`is`, `is not`)
```python
# is: Same object in memory
a = [1, 2, 3]
b = a
c = [1, 2, 3]

print(a is b)             # True (same object)
print(a is c)             # False (different objects)
print(a == c)             # True (same values)

# Small integers are cached
x = 256
y = 256
print(x is y)             # True (cached)

x = 257
y = 257
print(x is y)             # False (not cached) - implementation dependent

# None comparison
value = None
print(value is None)      # True (correct way)
print(value == None)      # True (but use 'is')
```

### Membership Operators (`in`, `not in`)
```python
# in: Check if item exists
print(3 in [1, 2, 3])     # True
print(4 in [1, 2, 3])     # False

# Strings
print('a' in 'apple')     # True
print('z' in 'apple')     # False

# not in
print(5 not in [1, 2, 3]) # True
```

---

## 8. Operator Precedence

### Precedence Table (High to Low)
```python
# 1. Parentheses
result = (2 + 3) * 4      # 20

# 2. Exponentiation
result = 2 ** 3 ** 2      # 512 (right-associative: 2^(3^2))

# 3. Unary +, -, ~
result = -2 ** 2          # -4 (-(2**2))
result = (-2) ** 2        # 4

# 4. *, /, //, %
result = 10 + 2 * 3       # 16

# 5. +, -
result = 5 - 2 + 1        # 4

# 6. <<, >>
result = 8 >> 1 + 1       # 2 (8 >> 2)

# 7. &
result = 5 & 3 | 1        # 1

# 8. ^
# 9. |
# 10. Comparisons
# 11. not
# 12. and
# 13. or
```

### Complex Expression
```python
result = 2 + 3 * 4 ** 2 / 8 - 1
# Step by step:
# 4 ** 2 = 16
# 3 * 16 = 48
# 48 / 8 = 6.0
# 2 + 6.0 = 8.0
# 8.0 - 1 = 7.0
print(result)             # 7.0
```

---

## 9. Type Conversion

### Implicit Conversion (Coercion)
```python
# int + float → float
result = 5 + 2.0          # 7.0

# int + complex → complex
result = 5 + 2j           # (5+2j)

# bool + int → int
result = True + 5         # 6
result = False + 10       # 10
```

### Explicit Conversion
```python
# To int
int(3.14)                 # 3 (truncates)
int("100")                # 100
int("1010", 2)            # 10 (binary)
int("FF", 16)             # 255 (hex)
int(True)                 # 1

# To float
float(5)                  # 5.0
float("3.14")             # 3.14
float("inf")              # inf

# To complex
complex(5)                # (5+0j)
complex(3, 4)             # (3+4j)

# To bool
bool(0)                   # False
bool(1)                   # True
bool("")                  # False
bool("text")              # True
```

### Rounding
```python
# round()
round(3.7)                # 4
round(3.14159, 2)         # 3.14
round(1234, -2)           # 1200

# Banker's rounding (round half to even)
round(2.5)                # 2
round(3.5)                # 4

# abs()
abs(-5)                   # 5
abs(-3.14)                # 3.14
abs(3+4j)                 # 5.0 (magnitude)

# divmod()
quotient, remainder = divmod(17, 5)  # (3, 2)
```

---

## 10. Math Functions and Module

### Built-in Functions
```python
# min, max
min(1, 5, 3)              # 1
max([1, 5, 3])            # 5

# sum
sum([1, 2, 3, 4])         # 10
sum([1, 2, 3], 10)        # 16 (start value)

# pow
pow(2, 3)                 # 8
pow(2, 3, 5)              # 3 (2^3 % 5)
```

### Math Module
```python
import math

# Constants
math.pi                   # 3.141592653589793
math.e                    # 2.718281828459045
math.inf                  # infinity
math.nan                  # Not a Number

# Rounding
math.ceil(3.2)            # 4
math.floor(3.8)           # 3
math.trunc(3.8)           # 3 (toward zero)

# Power and logarithm
math.sqrt(16)             # 4.0
math.pow(2, 3)            # 8.0
math.log(math.e)          # 1.0
math.log10(100)           # 2.0
math.log2(8)              # 3.0

# Trigonometry (radians)
math.sin(math.pi/2)       # 1.0
math.cos(0)               # 1.0
math.tan(math.pi/4)       # 1.0

# Conversions
math.degrees(math.pi)     # 180.0
math.radians(180)         # 3.141592653589793

# Other
math.factorial(5)         # 120
math.gcd(48, 18)          # 6
math.isnan(float('nan'))  # True
math.isinf(float('inf'))  # True
```

---

## Key Takeaways for PCAP Exam

1. ✅ **Division**: `/` always returns float, `//` returns floor division
2. ✅ **Modulo**: Result has the sign of the divisor
3. ✅ **Exponentiation**: `**` is right-associative: `2**3**2` = `2**(3**2)`
4. ✅ **Comparison chaining**: `1 < x < 10` is valid
5. ✅ **Logical operators**: `and`, `or`, `not` (short-circuit evaluation)
6. ✅ **Bitwise operators**: `&`, `|`, `^`, `~`, `<<`, `>>`
7. ✅ **Identity**: Use `is` for None comparison
8. ✅ **Truthiness**: `0`, `""`, `[]`, `{}`, `None` are falsy
9. ✅ **Type conversion**: `int()`, `float()`, `bool()`, `str()`
10. ✅ **Operator precedence**: `()` > `**` > `*/` > `+-`

---

## Practice Examples

### Example 1: Temperature Converter
```python
celsius = float(input("Celsius: "))
fahrenheit = celsius * 9/5 + 32
kelvin = celsius + 273.15
print(f"{celsius}°C = {fahrenheit}°F = {kelvin}K")
```

### Example 2: Even/Odd Checker
```python
number = int(input("Enter number: "))
if number % 2 == 0:
    print("Even")
else:
    print("Odd")

# Or using bitwise
print("Even" if number & 1 == 0 else "Odd")
```

### Example 3: BMI Calculator
```python
weight = float(input("Weight (kg): "))
height = float(input("Height (m): "))
bmi = weight / height ** 2
print(f"BMI: {bmi:.2f}")
```

---

## Next Steps
After mastering this module, proceed to:
- **Module 2 Part 2: Strings and Text** - String operations and methods
