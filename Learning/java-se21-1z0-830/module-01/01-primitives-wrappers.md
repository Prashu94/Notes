# Module 1.1: Primitives and Wrapper Classes

## 📚 Table of Contents
1. [Overview](#overview)
2. [Primitive Data Types](#primitive-data-types)
3. [Wrapper Classes](#wrapper-classes)
4. [Autoboxing and Unboxing](#autoboxing-and-unboxing)
5. [Type Conversion and Casting](#type-conversion-and-casting)
6. [Numeric Promotions](#numeric-promotions)
7. [Common Pitfalls](#common-pitfalls)
8. [Best Practices](#best-practices)

---

## Overview

Java has two categories of data types:
- **Primitive types**: Basic building blocks (8 types)
- **Reference types**: Objects (including wrapper classes)

Understanding primitives and their wrapper equivalents is crucial for the Java SE 21 Developer exam.

---

## Primitive Data Types

Java has **8 primitive data types**:

### 1. Integer Types

#### byte
- **Size**: 8 bits (1 byte)
- **Range**: -128 to 127 (-2^7 to 2^7 - 1)
- **Default**: 0

```java
byte b1 = 100;
byte b2 = -128;
byte b3 = 127;
// byte b4 = 128;  // Compilation error: out of range
```

#### short
- **Size**: 16 bits (2 bytes)
- **Range**: -32,768 to 32,767 (-2^15 to 2^15 - 1)
- **Default**: 0

```java
short s1 = 32767;
short s2 = -32768;
// short s3 = 32768;  // Compilation error
```

#### int
- **Size**: 32 bits (4 bytes)
- **Range**: -2,147,483,648 to 2,147,483,647 (-2^31 to 2^31 - 1)
- **Default**: 0
- **Most commonly used** integer type

```java
int i1 = 2147483647;
int i2 = -2147483648;
int i3 = 1_000_000;  // Underscores for readability (Java 7+)
```

#### long
- **Size**: 64 bits (8 bytes)
- **Range**: -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 (-2^63 to 2^63 - 1)
- **Default**: 0L
- **Literal suffix**: L or l

```java
long l1 = 9223372036854775807L;
long l2 = 100L;
long l3 = 100;  // OK: int literal promoted to long
// long l4 = 9223372036854775807;  // Error: missing 'L' suffix
```

### 2. Floating-Point Types

#### float
- **Size**: 32 bits (4 bytes)
- **Precision**: ~6-7 decimal digits
- **Default**: 0.0f
- **Literal suffix**: F or f

```java
float f1 = 3.14f;
float f2 = 3.14F;
// float f3 = 3.14;  // Error: double cannot be converted to float
float f4 = (float) 3.14;  // OK with cast
```

#### double
- **Size**: 64 bits (8 bytes)
- **Precision**: ~15 decimal digits
- **Default**: 0.0d (or 0.0)
- **Literal suffix**: D, d, or none
- **Preferred** for floating-point calculations

```java
double d1 = 3.14;
double d2 = 3.14d;
double d3 = 3.14D;
double d4 = 1.23e-4;  // Scientific notation: 0.000123
```

### 3. Character Type

#### char
- **Size**: 16 bits (2 bytes)
- **Range**: 0 to 65,535 (Unicode characters)
- **Default**: '\u0000' (null character)
- **Literals**: Single quotes

```java
char c1 = 'A';
char c2 = 65;        // ASCII value of 'A'
char c3 = '\u0041';  // Unicode for 'A'
char c4 = '\n';      // Newline
char c5 = '\\';      // Backslash
```

**Escape Sequences:**
```java
char tab = '\t';       // Tab
char backspace = '\b'; // Backspace
char newline = '\n';   // Newline
char cr = '\r';        // Carriage return
char quote = '\'';     // Single quote
char dquote = '\"';    // Double quote (in char literal, not needed)
char backslash = '\\'; // Backslash
```

### 4. Boolean Type

#### boolean
- **Size**: Not precisely defined (JVM-dependent, typically 1 bit)
- **Values**: `true` or `false` only
- **Default**: false

```java
boolean bool1 = true;
boolean bool2 = false;
// boolean bool3 = 1;     // Error: incompatible types
// boolean bool4 = "true"; // Error: incompatible types
```

---

## Wrapper Classes

Every primitive type has a corresponding **wrapper class** (reference type):

| Primitive | Wrapper Class | Package |
|-----------|---------------|---------|
| byte      | Byte          | java.lang |
| short     | Short         | java.lang |
| int       | Integer       | java.lang |
| long      | Long          | java.lang |
| float     | Float         | java.lang |
| double    | Double        | java.lang |
| char      | Character     | java.lang |
| boolean   | Boolean       | java.lang |

### Why Use Wrapper Classes?

1. **Collections**: Generics require objects (can't use primitives)
   ```java
   List<int> list1;     // Error: primitive type not allowed
   List<Integer> list2; // OK
   ```

2. **Nullability**: Primitives can't be null
   ```java
   int i = null;     // Error
   Integer i = null; // OK
   ```

3. **Utility methods**: Wrappers provide useful methods
   ```java
   int max = Integer.MAX_VALUE;
   int min = Integer.MIN_VALUE;
   int parsed = Integer.parseInt("123");
   String binary = Integer.toBinaryString(10); // "1010"
   ```

### Creating Wrapper Objects

#### Using Constructors (Deprecated since Java 9)
```java
@Deprecated(since = "9")
Integer i1 = new Integer(100);      // Deprecated
Double d1 = new Double(3.14);       // Deprecated
```

#### Using valueOf() (Preferred)
```java
Integer i2 = Integer.valueOf(100);
Double d2 = Double.valueOf(3.14);
Boolean b1 = Boolean.valueOf(true);
Character c1 = Character.valueOf('A');
```

#### Using Autoboxing (Automatic conversion)
```java
Integer i3 = 100;        // Autoboxing
Double d3 = 3.14;        // Autoboxing
Boolean b2 = true;       // Autoboxing
```

### Useful Wrapper Methods

#### Integer Class
```java
// Constants
int max = Integer.MAX_VALUE;  // 2147483647
int min = Integer.MIN_VALUE;  // -2147483648
int size = Integer.SIZE;      // 32 (bits)
int bytes = Integer.BYTES;    // 4

// Parsing strings
int num1 = Integer.parseInt("123");
int num2 = Integer.parseInt("1010", 2);  // Binary: 10
int num3 = Integer.parseInt("FF", 16);   // Hex: 255

// Conversions
String bin = Integer.toBinaryString(10);  // "1010"
String oct = Integer.toOctalString(8);    // "10"
String hex = Integer.toHexString(255);    // "ff"

// Comparison
int result = Integer.compare(10, 20);     // -1 (10 < 20)
int result2 = Integer.compare(20, 10);    // 1 (20 > 10)
int result3 = Integer.compare(10, 10);    // 0 (10 == 10)

// Utility
int sum = Integer.sum(10, 20);            // 30
int max2 = Integer.max(10, 20);           // 20
int min2 = Integer.min(10, 20);           // 10
```

#### Double Class
```java
// Constants
double max = Double.MAX_VALUE;
double min = Double.MIN_VALUE;
double posInf = Double.POSITIVE_INFINITY;
double negInf = Double.NEGATIVE_INFINITY;
double nan = Double.NaN;

// Parsing
double d = Double.parseDouble("3.14");

// Checks
boolean isInfinite = Double.isInfinite(posInf);  // true
boolean isNaN = Double.isNaN(nan);               // true
boolean isFinite = Double.isFinite(3.14);        // true

// Comparison
int result = Double.compare(3.14, 2.71);  // 1
```

#### Boolean Class
```java
// Parsing
Boolean b1 = Boolean.parseBoolean("true");   // true
Boolean b2 = Boolean.parseBoolean("True");   // true (case-insensitive)
Boolean b3 = Boolean.parseBoolean("yes");    // false (only "true" returns true)

// Logical operations
boolean and = Boolean.logicalAnd(true, false);  // false
boolean or = Boolean.logicalOr(true, false);    // true
boolean xor = Boolean.logicalXor(true, false);  // true
```

#### Character Class
```java
// Character checks
boolean isLetter = Character.isLetter('A');       // true
boolean isDigit = Character.isDigit('5');         // true
boolean isWhitespace = Character.isWhitespace(' '); // true
boolean isUpperCase = Character.isUpperCase('A'); // true
boolean isLowerCase = Character.isLowerCase('a'); // true

// Conversions
char upper = Character.toUpperCase('a');  // 'A'
char lower = Character.toLowerCase('A');  // 'a'

// Numeric value
int numValue = Character.getNumericValue('5'); // 5
int hexValue = Character.getNumericValue('F'); // 15
```

---

## Autoboxing and Unboxing

**Autoboxing**: Automatic conversion from primitive to wrapper
**Unboxing**: Automatic conversion from wrapper to primitive

### Autoboxing Examples
```java
Integer i = 100;           // int -> Integer (autoboxing)
Double d = 3.14;           // double -> Double (autoboxing)
Boolean b = true;          // boolean -> Boolean (autoboxing)

List<Integer> list = new ArrayList<>();
list.add(10);              // Autoboxing: int -> Integer
```

### Unboxing Examples
```java
Integer i = 100;
int primitive = i;         // Integer -> int (unboxing)

Integer num = 50;
int result = num + 10;     // Unboxing num, then adding
```

### Mixed Operations
```java
Integer a = 10;
Integer b = 20;
Integer c = a + b;         // Unbox, add, then autobox result
// Equivalent to: Integer c = Integer.valueOf(a.intValue() + b.intValue());
```

### Important: NullPointerException Risk
```java
Integer num = null;
// int primitive = num;    // NullPointerException at runtime!

if (num != null) {
    int primitive = num;   // Safe
}
```

### Wrapper Caching

Java caches wrapper objects for small values to improve performance:

```java
// Integer cache: -128 to 127
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true (same cached object)

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false (different objects)

// Always use equals() for value comparison
System.out.println(c.equals(d));  // true
```

**Cached ranges:**
- **Boolean**: true and false
- **Byte**: All values (-128 to 127)
- **Character**: '\u0000' to '\u007F' (0 to 127)
- **Short, Integer, Long**: -128 to 127 (can be extended for Integer via JVM option)

---

## Type Conversion and Casting

### Widening Conversion (Implicit - No Data Loss)

Automatically converts smaller type to larger type:

```
byte -> short -> int -> long -> float -> double
       char   -> int -> long -> float -> double
```

```java
byte b = 10;
int i = b;        // Widening: byte -> int (automatic)

int num = 100;
long l = num;     // Widening: int -> long (automatic)

long big = 1000L;
float f = big;    // Widening: long -> float (automatic, may lose precision)

float fl = 3.14f;
double d = fl;    // Widening: float -> double (automatic)
```

### Narrowing Conversion (Explicit - May Lose Data)

Requires explicit cast when converting larger type to smaller:

```java
int i = 130;
byte b = (byte) i;      // Narrowing: int -> byte (requires cast)
                        // Result: -126 (overflow wraps around)

double d = 3.14;
int num = (int) d;      // Narrowing: double -> int (fractional part lost)
                        // Result: 3

long l = 100L;
int i2 = (int) l;       // Narrowing: long -> int (requires cast)

float f = 3.14f;
int i3 = (int) f;       // Result: 3 (fractional part lost)
```

### Compound Assignment and Implicit Casting

Compound assignment operators include implicit casting:

```java
int i = 10;
double d = 5.5;
// i = i + d;       // Error: incompatible types (double cannot be converted to int)
i += d;             // OK: equivalent to i = (int)(i + d);
                    // Result: i = 15
```

```java
byte b = 10;
// b = b + 1;       // Error: int cannot be converted to byte
b += 1;             // OK: equivalent to b = (byte)(b + 1);
```

### String Conversion

All types can be concatenated with String:

```java
int i = 100;
String s1 = i + "";           // "100"
String s2 = String.valueOf(i); // "100" (preferred)

double d = 3.14;
String s3 = Double.toString(d); // "3.14"
```

---

## Numeric Promotions

### Binary Numeric Promotion

When operands of different types are used in an expression:

```java
byte b = 10;
short s = 20;
int result = b + s;  // Both promoted to int, result is int

long l = 100L;
float f = 3.14f;
float result2 = l + f;  // long promoted to float, result is float

int i = 10;
double d = 5.5;
double result3 = i + d;  // int promoted to double, result is double
```

**Rules:**
1. If either operand is `double`, the other is converted to `double`
2. Otherwise, if either operand is `float`, the other is converted to `float`
3. Otherwise, if either operand is `long`, the other is converted to `long`
4. Otherwise, both are converted to `int`

### Unary Numeric Promotion

Smaller types are promoted to `int` in expressions:

```java
byte b = 10;
// byte result = -b;     // Error: int cannot be converted to byte
int result = -b;         // OK: b is promoted to int

short s = 5;
// short result2 = ~s;   // Error: bitwise complement returns int
int result2 = ~s;        // OK
```

---

## Common Pitfalls

### 1. Integer Division
```java
int a = 5;
int b = 2;
double result = a / b;        // 2.0 (not 2.5!)
double correct = (double) a / b;  // 2.5
```

### 2. Overflow
```java
int max = Integer.MAX_VALUE;
int overflow = max + 1;       // -2147483648 (wraps around)

// Use long for large values
long correct = (long) max + 1; // 2147483648
```

### 3. Floating-Point Precision
```java
double d1 = 0.1 + 0.2;
System.out.println(d1);       // 0.30000000000000004 (not 0.3!)
System.out.println(d1 == 0.3); // false

// Use BigDecimal for exact decimal arithmetic
```

### 4. Comparing Wrapper Objects with ==
```java
Integer a = 128;
Integer b = 128;
System.out.println(a == b);     // false (different objects)
System.out.println(a.equals(b)); // true (correct way)
```

### 5. NullPointerException with Unboxing
```java
Integer num = null;
// int i = num;         // NullPointerException!
int safe = (num != null) ? num : 0;
```

### 6. Compound Assignment Surprises
```java
byte b = 10;
// b = b * 2;           // Error: int cannot be converted to byte
b *= 2;                 // OK (implicit cast included)
```

---

## Best Practices

### ✅ DO:
1. **Use primitives for performance-critical code**
   ```java
   int count = 0;  // Faster than Integer
   ```

2. **Use wrappers when nullability is needed**
   ```java
   Integer nullableCount = null;  // Can represent "no value"
   ```

3. **Use wrappers in collections**
   ```java
   List<Integer> numbers = new ArrayList<>();
   ```

4. **Use valueOf() instead of constructors**
   ```java
   Integer i = Integer.valueOf(100);  // Preferred
   ```

5. **Use equals() to compare wrapper objects**
   ```java
   Integer a = 200;
   Integer b = 200;
   if (a.equals(b)) { }  // Correct
   ```

6. **Check for null before unboxing**
   ```java
   Integer num = getNumber();
   if (num != null) {
       int value = num;
   }
   ```

### ❌ DON'T:
1. **Don't use wrapper constructors**
   ```java
   Integer i = new Integer(100);  // Deprecated since Java 9
   ```

2. **Don't use == to compare wrapper objects (beyond cached range)**
   ```java
   Integer a = 200;
   Integer b = 200;
   if (a == b) { }  // Wrong! Use equals()
   ```

3. **Don't unbox without null check**
   ```java
   Integer num = null;
   int value = num;  // NullPointerException!
   ```

---

## Summary

- Java has **8 primitive types**: byte, short, int, long, float, double, char, boolean
- Each primitive has a **wrapper class** for object representation
- **Autoboxing**: primitive → wrapper (automatic)
- **Unboxing**: wrapper → primitive (automatic, but watch for NPE)
- **Widening**: smaller → larger type (automatic, safe)
- **Narrowing**: larger → smaller type (requires cast, may lose data)
- Wrappers cache small values for performance
- Always use **equals()** to compare wrapper values
- Prefer **primitives** for performance, **wrappers** when objects are needed

---

## Next Steps

Proceed to [Practice Questions](01-practice-questions.md) to test your understanding of primitives and wrapper classes!
