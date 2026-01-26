# Module 1.2: Math API and Boolean/Arithmetic Expressions

## 📚 Table of Contents
1. [Overview](#overview)
2. [Arithmetic Operators](#arithmetic-operators)
3. [Math Class Methods](#math-class-methods)
4. [Boolean Expressions](#boolean-expressions)
5. [Operator Precedence](#operator-precedence)
6. [Bitwise Operators](#bitwise-operators)
7. [Best Practices](#best-practices)

---

## Overview

The Java Math API (`java.lang.Math`) provides methods for mathematical operations. Combined with understanding arithmetic operators, boolean expressions, and operator precedence, this knowledge is essential for the Java SE 21 exam.

---

## Arithmetic Operators

Java provides five basic arithmetic operators:

### 1. Addition (+)
```java
int sum = 10 + 5;           // 15
double result = 3.5 + 2.5;  // 6.0
String concat = "Hello" + " World";  // "HelloWorld" (String concatenation)
```

### 2. Subtraction (-)
```java
int difference = 10 - 5;    // 5
double result = 7.5 - 2.5;  // 5.0
```

### 3. Multiplication (*)
```java
int product = 10 * 5;       // 50
double result = 2.5 * 4;    // 10.0
```

### 4. Division (/)
```java
// Integer division
int quotient1 = 10 / 3;     // 3 (not 3.333...)
int quotient2 = 10 / 4;     // 2

// Floating-point division
double result1 = 10.0 / 3;  // 3.3333333333333335
double result2 = (double) 10 / 3;  // 3.3333333333333335

// Division by zero
int error = 10 / 0;         // ArithmeticException: / by zero
double inf = 10.0 / 0.0;    // Infinity (no exception for floating-point)
```

### 5. Modulus/Remainder (%)
```java
int remainder1 = 10 % 3;    // 1
int remainder2 = 15 % 4;    // 3
int remainder3 = 20 % 5;    // 0

// With negative numbers
int result1 = 10 % -3;      // 1 (sign follows dividend)
int result2 = -10 % 3;      // -1
int result3 = -10 % -3;     // -1

// Modulus by zero
int error = 10 % 0;         // ArithmeticException
double nan = 10.0 % 0.0;    // NaN (Not a Number)
```

### Unary Operators

```java
int a = 5;
int positive = +a;          // 5 (unary plus)
int negative = -a;          // -5 (unary minus)

// Increment/Decrement
int b = 10;
int preInc = ++b;           // b=11, preInc=11 (increment first, then use)
int postInc = b++;          // postInc=11, b=12 (use first, then increment)

int c = 10;
int preDec = --c;           // c=9, preDec=9
int postDec = c--;          // postDec=9, c=8
```

**Important Pre vs Post Increment:**
```java
int x = 5;
int y = ++x;  // x=6, y=6 (x incremented before assignment)

int a = 5;
int b = a++;  // a=6, b=5 (a incremented after assignment)
```

---

## Math Class Methods

The `java.lang.Math` class provides static methods for mathematical operations.

### Constants

```java
double pi = Math.PI;        // 3.141592653589793
double e = Math.E;          // 2.718281828459045
```

### Basic Mathematical Functions

#### Absolute Value
```java
int abs1 = Math.abs(-10);       // 10
double abs2 = Math.abs(-3.14);  // 3.14
long abs3 = Math.abs(-100L);    // 100L

// Special case
int abs4 = Math.abs(Integer.MIN_VALUE);  // Integer.MIN_VALUE (overflow!)
```

#### Power and Square Root
```java
double power = Math.pow(2, 3);      // 8.0 (2^3)
double power2 = Math.pow(5, 2);     // 25.0 (5^2)
double power3 = Math.pow(9, 0.5);   // 3.0 (square root)

double sqrt = Math.sqrt(16);        // 4.0
double sqrt2 = Math.sqrt(2);        // 1.4142135623730951
double sqrt3 = Math.sqrt(-1);       // NaN (negative input)

double cbrt = Math.cbrt(27);        // 3.0 (cube root)
```

#### Exponential and Logarithm
```java
double exp = Math.exp(1);           // 2.718281828459045 (e^1)
double exp2 = Math.exp(2);          // 7.38905609893065 (e^2)

double log = Math.log(Math.E);      // 1.0 (natural log)
double log2 = Math.log(10);         // 2.302585092994046

double log10 = Math.log10(100);     // 2.0 (log base 10)
double log10_2 = Math.log10(1000);  // 3.0
```

### Rounding Functions

#### ceil() - Round Up
```java
double ceil1 = Math.ceil(3.1);      // 4.0
double ceil2 = Math.ceil(3.9);      // 4.0
double ceil3 = Math.ceil(-3.1);     // -3.0 (rounds toward positive infinity)
```

#### floor() - Round Down
```java
double floor1 = Math.floor(3.1);    // 3.0
double floor2 = Math.floor(3.9);    // 3.0
double floor3 = Math.floor(-3.1);   // -4.0 (rounds toward negative infinity)
```

#### round() - Round to Nearest
```java
long round1 = Math.round(3.4);      // 3 (rounds down)
long round2 = Math.round(3.5);      // 4 (rounds up)
long round3 = Math.round(3.6);      // 4 (rounds up)

// Returns long for double, int for float
int round4 = Math.round(3.5f);      // 4 (float -> int)
long round5 = Math.round(3.5);      // 4 (double -> long)

// Negative numbers
long round6 = Math.round(-3.5);     // -3 (rounds toward positive infinity)
long round7 = Math.round(-3.6);     // -4
```

#### rint() - Round to Nearest Even
```java
double rint1 = Math.rint(2.5);      // 2.0 (rounds to even)
double rint2 = Math.rint(3.5);      // 4.0 (rounds to even)
double rint3 = Math.rint(4.5);      // 4.0 (rounds to even)
```

### Min and Max

```java
int min1 = Math.min(10, 20);        // 10
double min2 = Math.min(3.14, 2.71); // 2.71

int max1 = Math.max(10, 20);        // 20
double max2 = Math.max(3.14, 2.71); // 3.14

// Can be chained
int min3 = Math.min(Math.min(5, 3), 7);  // 3
```

### Random Numbers

```java
// Returns double in range [0.0, 1.0)
double random = Math.random();      // e.g., 0.7234567

// Random int in range [0, 10)
int randomInt = (int) (Math.random() * 10);  // 0 to 9

// Random int in range [min, max]
int min = 10;
int max = 20;
int randomInRange = (int) (Math.random() * (max - min + 1)) + min;  // 10 to 20
```

### Trigonometric Functions

```java
// Input in radians
double sin = Math.sin(Math.PI / 2);     // 1.0 (sin 90°)
double cos = Math.cos(Math.PI);         // -1.0 (cos 180°)
double tan = Math.tan(Math.PI / 4);     // 1.0 (tan 45°)

// Inverse functions
double asin = Math.asin(1);             // π/2
double acos = Math.acos(-1);            // π
double atan = Math.atan(1);             // π/4

// Degree/Radian conversion
double radians = Math.toRadians(180);   // π
double degrees = Math.toDegrees(Math.PI);  // 180.0
```

### Hyperbolic Functions

```java
double sinh = Math.sinh(0);             // 0.0
double cosh = Math.cosh(0);             // 1.0
double tanh = Math.tanh(0);             // 0.0
```

### Other Useful Methods

```java
// Sign
double signum1 = Math.signum(10);       // 1.0 (positive)
double signum2 = Math.signum(-10);      // -1.0 (negative)
double signum3 = Math.signum(0);        // 0.0 (zero)

// Copy sign
double copySign = Math.copySign(5.0, -2.0);  // -5.0

// Hypotenuse (Pythagorean theorem)
double hypotenuse = Math.hypot(3, 4);   // 5.0 (sqrt(3^2 + 4^2))

// Next floating-point value
double next = Math.nextAfter(1.0, 2.0); // 1.0000000000000002
double next2 = Math.nextUp(1.0);        // 1.0000000000000002
double next3 = Math.nextDown(1.0);      // 0.9999999999999999

// Floating-point remainder
double IEEEremainder = Math.IEEEremainder(10.0, 3.0);  // 1.0

// Exact arithmetic (throws ArithmeticException on overflow)
int exactAdd = Math.addExact(Integer.MAX_VALUE - 1, 1);  // OK
// int overflow = Math.addExact(Integer.MAX_VALUE, 1);  // ArithmeticException

int exactSubtract = Math.subtractExact(10, 5);      // 5
int exactMultiply = Math.multiplyExact(100, 200);   // 20000
int exactNegate = Math.negateExact(-10);            // 10
```

---

## Boolean Expressions

### Relational Operators

```java
int a = 10, b = 20;

boolean isEqual = (a == b);         // false
boolean notEqual = (a != b);        // true
boolean greater = (a > b);          // false
boolean less = (a < b);             // true
boolean greaterOrEqual = (a >= b);  // false
boolean lessOrEqual = (a <= b);     // true
```

### Logical Operators

#### AND (&&) - Short-circuit
```java
boolean result1 = true && true;     // true
boolean result2 = true && false;    // false
boolean result3 = false && true;    // false

// Short-circuit: second operand not evaluated if first is false
int x = 0;
boolean result4 = (x != 0) && (10 / x > 1);  // false (no ArithmeticException)
```

#### OR (||) - Short-circuit
```java
boolean result1 = true || false;    // true
boolean result2 = false || true;    // true
boolean result3 = false || false;   // false

// Short-circuit: second operand not evaluated if first is true
int x = 0;
boolean result4 = (x == 0) || (10 / x > 1);  // true (no ArithmeticException)
```

#### NOT (!)
```java
boolean result1 = !true;            // false
boolean result2 = !false;           // true
boolean result3 = !(10 > 5);        // false
```

#### Bitwise Logical Operators (Non-short-circuit)

```java
// Bitwise AND (&) - evaluates both operands
boolean result1 = true & false;     // false
int x = 0;
// boolean result2 = (x != 0) & (10 / x > 1);  // ArithmeticException!

// Bitwise OR (|) - evaluates both operands
boolean result3 = true | false;     // true

// Bitwise XOR (^) - true if exactly one operand is true
boolean result4 = true ^ false;     // true
boolean result5 = true ^ true;      // false
boolean result6 = false ^ false;    // false
```

### Ternary Operator (Conditional Operator)

```java
// Syntax: condition ? valueIfTrue : valueIfFalse
int max = (10 > 5) ? 10 : 5;        // 10

String result = (true) ? "Yes" : "No";  // "Yes"

// Can be nested (but avoid for readability)
int grade = 85;
String letter = (grade >= 90) ? "A" :
                (grade >= 80) ? "B" :
                (grade >= 70) ? "C" : "F";  // "B"
```

---

## Operator Precedence

Operators are evaluated in the following order (highest to lowest):

| Precedence | Operators | Description |
|------------|-----------|-------------|
| 1 | `()` `[]` `.` | Parentheses, array access, member access |
| 2 | `++` `--` `+` `-` `!` `~` `(type)` | Unary operators, cast |
| 3 | `*` `/` `%` | Multiplicative |
| 4 | `+` `-` | Additive |
| 5 | `<<` `>>` `>>>` | Shift |
| 6 | `<` `<=` `>` `>=` `instanceof` | Relational |
| 7 | `==` `!=` | Equality |
| 8 | `&` | Bitwise AND |
| 9 | `^` | Bitwise XOR |
| 10 | `\|` | Bitwise OR |
| 11 | `&&` | Logical AND |
| 12 | `\|\|` | Logical OR |
| 13 | `?:` | Ternary |
| 14 | `=` `+=` `-=` `*=` `/=` `%=` etc. | Assignment |

### Examples

```java
// Example 1: Multiplication before addition
int result1 = 2 + 3 * 4;            // 14 (not 20)
// Equivalent to: 2 + (3 * 4)

// Example 2: Parentheses override precedence
int result2 = (2 + 3) * 4;          // 20

// Example 3: Unary operators have high precedence
int result3 = -2 * 3;               // -6
// Equivalent to: (-2) * 3

// Example 4: Relational before logical
boolean result4 = 10 > 5 && 20 < 30;  // true
// Equivalent to: (10 > 5) && (20 < 30)

// Example 5: Equality after relational
boolean result5 = 10 > 5 == true;   // true
// Equivalent to: (10 > 5) == true

// Example 6: Complex expression
int result6 = 10 + 20 * 3 / 2 - 5;  // 10 + (20 * 3 / 2) - 5
                                    // 10 + (60 / 2) - 5
                                    // 10 + 30 - 5 = 35
```

### Associativity

Most operators are **left-to-right** associative:
```java
int result = 10 - 5 - 2;            // (10 - 5) - 2 = 3 (not 10 - (5 - 2) = 7)
```

Assignment operators are **right-to-left** associative:
```java
int a, b, c;
a = b = c = 10;                     // Equivalent to: a = (b = (c = 10))
```

---

## Bitwise Operators

Bitwise operators work on individual bits of integer types.

### Bitwise AND (&)

```java
int a = 12;  // 1100 in binary
int b = 10;  // 1010 in binary
int result = a & b;  // 1000 in binary = 8
```

### Bitwise OR (|)

```java
int a = 12;  // 1100 in binary
int b = 10;  // 1010 in binary
int result = a | b;  // 1110 in binary = 14
```

### Bitwise XOR (^)

```java
int a = 12;  // 1100 in binary
int b = 10;  // 1010 in binary
int result = a ^ b;  // 0110 in binary = 6

// Useful property: x ^ x = 0, x ^ 0 = x
int x = 5;
int zero = x ^ x;    // 0
int same = x ^ 0;    // 5
```

### Bitwise Complement (~)

```java
int a = 12;  // 00000000000000000000000000001100 (32-bit)
int result = ~a;  // 11111111111111111111111111110011 = -13
// Rule: ~x = -(x + 1)
```

### Shift Operators

#### Left Shift (<<)
```java
int a = 5;   // 101 in binary
int result = a << 2;  // 10100 in binary = 20
// Equivalent to: a * 2^2 = 5 * 4 = 20
```

#### Right Shift (>>)
```java
int a = 20;  // 10100 in binary
int result = a >> 2;  // 101 in binary = 5
// Equivalent to: a / 2^2 = 20 / 4 = 5

// With negative numbers (sign-extension)
int b = -8;
int result2 = b >> 2;  // -2 (sign bit preserved)
```

#### Unsigned Right Shift (>>>)
```java
int a = -8;
int result = a >>> 2;  // Shifts in zeros from left, ignoring sign
// Result: Large positive number (sign bit not preserved)
```

---

## Best Practices

### ✅ DO:

1. **Use parentheses for clarity**
   ```java
   int result = (a + b) * c;  // Clear intent
   ```

2. **Use Math.addExact() to prevent overflow**
   ```java
   try {
       int result = Math.addExact(Integer.MAX_VALUE, 1);
   } catch (ArithmeticException e) {
       // Handle overflow
   }
   ```

3. **Use Math methods for complex calculations**
   ```java
   double hypotenuse = Math.hypot(3, 4);  // Better than Math.sqrt(3*3 + 4*4)
   ```

4. **Check for division by zero**
   ```java
   if (divisor != 0) {
       int result = dividend / divisor;
   }
   ```

### ❌ DON'T:

1. **Don't rely on floating-point equality**
   ```java
   // Bad
   if (0.1 + 0.2 == 0.3) { }  // false!
   
   // Good
   double epsilon = 0.0001;
   if (Math.abs((0.1 + 0.2) - 0.3) < epsilon) { }
   ```

2. **Don't ignore operator precedence**
   ```java
   // Confusing
   int result = a + b * c / d - e;
   
   // Clear
   int result = a + ((b * c) / d) - e;
   ```

3. **Don't use bitwise operators for boolean logic (usually)**
   ```java
   // Use && for short-circuit evaluation
   if (obj != null && obj.isValid()) { }
   
   // Don't use & (both sides evaluated)
   if (obj != null & obj.isValid()) { }  // NullPointerException if obj is null!
   ```

---

## Summary

- **Arithmetic operators**: +, -, *, /, %
- **Math class** provides static methods for mathematical operations
- **Boolean expressions** use relational (==, !=, <, >, <=, >=) and logical (&&, ||, !) operators
- **Operator precedence** determines evaluation order (use parentheses for clarity)
- **Bitwise operators** work on individual bits of integers
- **Short-circuit evaluation** in && and || can prevent errors

---

## Next Steps

Proceed to [Practice Questions](02-practice-questions.md) to test your understanding of the Math API and expressions!
