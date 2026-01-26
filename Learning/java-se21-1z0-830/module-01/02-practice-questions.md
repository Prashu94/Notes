# Module 1.2: Math API and Expressions - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output of the following code?

```java
int result = 10 + 5 * 2;
System.out.println(result);
```

A) 30  
B) 20  
C) 15  
D) Compilation error  

**Answer:** B

**Explanation:**
Due to operator precedence, multiplication is performed before addition. The expression evaluates as: `10 + (5 * 2)` = `10 + 10` = `20`. To get 30, you would need parentheses: `(10 + 5) * 2`.

---

### Question 2
What will the following code print?

```java
double result = Math.ceil(3.1);
System.out.println(result);
```

A) 3  
B) 3.0  
C) 4  
D) 4.0  

**Answer:** D

**Explanation:**
`Math.ceil()` returns a `double` (not an int) that is the smallest value greater than or equal to the argument. `Math.ceil(3.1)` returns `4.0`.

---

### Question 3
What is the result of the following expression?

```java
int result = 10 / 3;
System.out.println(result);
```

A) 3  
B) 3.333333  
C) 3.0  
D) Compilation error  

**Answer:** A

**Explanation:**
When both operands are integers, Java performs integer division, which truncates the decimal part. `10 / 3` = `3` (not 3.333...). To get the decimal result, at least one operand must be a floating-point type.

---

### Question 4
What does `Math.floor(-3.7)` return?

A) -3.0  
B) -4.0  
C) -3  
D) -4  

**Answer:** B

**Explanation:**
`Math.floor()` returns the largest double value that is less than or equal to the argument (rounds toward negative infinity). For -3.7, the largest value ≤ -3.7 is -4.0.

---

### Question 5
What is the output of the following code?

```java
int x = 5;
int y = ++x;
System.out.println(x + " " + y);
```

A) 5 5  
B) 6 5  
C) 5 6  
D) 6 6  

**Answer:** D

**Explanation:**
`++x` is pre-increment, which increments `x` first (x becomes 6), then assigns the value to `y` (y becomes 6). So both `x` and `y` are 6.

---

### Question 6
What will be printed by the following code?

```java
int x = 5;
int y = x++;
System.out.println(x + " " + y);
```

A) 5 5  
B) 6 5  
C) 5 6  
D) 6 6  

**Answer:** B

**Explanation:**
`x++` is post-increment, which assigns the current value of `x` to `y` first (y becomes 5), then increments `x` (x becomes 6). So `x` is 6 and `y` is 5.

---

### Question 7
What is the result of `10 % 3`?

A) 1  
B) 3  
C) 3.333  
D) 0  

**Answer:** A

**Explanation:**
The modulus operator `%` returns the remainder after division. `10 / 3` = 3 with a remainder of 1, so `10 % 3` = `1`.

---

### Question 8
What does the following code print?

```java
double result = Math.round(2.5);
System.out.println(result);
```

A) 2  
B) 2.0  
C) 3  
D) 3.0  

**Answer:** C

**Explanation:**
`Math.round()` for a double argument returns a `long` (not a double). It rounds to the nearest integer. `Math.round(2.5)` = `3` (rounds up). Note: This rounds to the nearest even number when exactly halfway (banker's rounding), but 2.5 rounds to 3.

---

### Question 9
What is the value of `Math.pow(2, 3)`?

A) 6  
B) 8  
C) 6.0  
D) 8.0  

**Answer:** D

**Explanation:**
`Math.pow(base, exponent)` returns a `double`. `Math.pow(2, 3)` calculates 2³ = 8, returning `8.0`.

---

### Question 10
What will the following code output?

```java
int result = 10 / 0;
System.out.println(result);
```

A) 0  
B) Infinity  
C) ArithmeticException  
D) Compilation error  

**Answer:** C

**Explanation:**
Integer division by zero throws an `ArithmeticException` at runtime. Note: Floating-point division by zero (`10.0 / 0.0`) returns `Infinity` without throwing an exception.

---

### Question 11
What is the output of the following code?

```java
boolean result = 10 > 5 && 20 < 15;
System.out.println(result);
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
The AND operator (`&&`) requires both operands to be true. `10 > 5` is true, but `20 < 15` is false, so the overall result is false.

---

### Question 12
What does `Math.abs(-10)` return?

A) -10  
B) 10  
C) -10.0  
D) 10.0  

**Answer:** B

**Explanation:**
`Math.abs()` returns the absolute value. When the argument is an `int`, it returns an `int`. `Math.abs(-10)` = `10`.

---

### Question 13
What is the result of the following expression?

```java
int result = 7 << 1;
System.out.println(result);
```

A) 3  
B) 7  
C) 14  
D) 28  

**Answer:** C

**Explanation:**
The left shift operator (`<<`) shifts bits to the left. `7 << 1` is equivalent to multiplying by 2¹. `7 * 2` = `14`. In binary: 111 (7) becomes 1110 (14).

---

### Question 14
What will the following code print?

```java
double result = Math.sqrt(16);
System.out.println(result);
```

A) 4  
B) 4.0  
C) 256  
D) 256.0  

**Answer:** B

**Explanation:**
`Math.sqrt()` returns the square root as a `double`. √16 = 4.0.

---

### Question 15
What is the output of the following code?

```java
int x = 10;
int y = 5;
boolean result = x > 5 || y++ > 5;
System.out.println(y);
```

A) 5  
B) 6  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
The OR operator (`||`) uses short-circuit evaluation. Since `x > 5` is true, the second operand `y++ > 5` is not evaluated. Therefore, `y` is not incremented and remains 5.

---

### Question 16
What does `Math.max(10, 20)` return?

A) 10  
B) 20  
C) 30  
D) 10.0  

**Answer:** B

**Explanation:**
`Math.max()` returns the larger of two values. `Math.max(10, 20)` = `20`. The return type matches the argument types (int in this case).

---

### Question 17
What is the result of the following code?

```java
double result = 10.0 / 0.0;
System.out.println(result);
```

A) 0.0  
B) ArithmeticException  
C) Infinity  
D) NaN  

**Answer:** C

**Explanation:**
Unlike integer division by zero, floating-point division by zero does not throw an exception. `10.0 / 0.0` returns `Double.POSITIVE_INFINITY` (printed as "Infinity").

---

### Question 18
What will the following code print?

```java
int result = (int) Math.round(3.6);
System.out.println(result);
```

A) 3  
B) 4  
C) 3.0  
D) 4.0  

**Answer:** B

**Explanation:**
`Math.round(double)` returns a `long`, which is then cast to `int`. `Math.round(3.6)` = `4L`, cast to `4`.

---

### Question 19
What is the value of `10 % -3`?

A) 1  
B) -1  
C) 2  
D) -2  

**Answer:** A

**Explanation:**
The result of the modulus operation has the sign of the dividend (the left operand). `10 % -3` = `1` (positive because 10 is positive). The calculation: 10 = -3 × (-3) + 1.

---

### Question 20
What does the following expression evaluate to?

```java
int result = 5 & 3;
System.out.println(result);
```

A) 1  
B) 3  
C) 5  
D) 8  

**Answer:** A

**Explanation:**
The bitwise AND operator (`&`) compares bits:
```
  101 (5)
& 011 (3)
-----
  001 (1)
```
Result is `1`.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered the Math API and expressions.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Integer division** returning int instead of decimal
2. **Operator precedence** - multiplication before addition
3. **Pre vs post increment** - when the increment happens
4. **Division by zero** - throws exception for int, returns Infinity for double
5. **Math method return types** - ceil/floor return double, round returns long
6. **Short-circuit evaluation** - && and || don't evaluate second operand if not needed
7. **Modulus sign** - result takes sign of dividend
8. **Bitwise vs logical operators** - & vs &&, | vs ||

---

## ✅ Module 1 Complete!

Congratulations! You've completed Module 1 covering:
- ✅ Primitive data types and wrapper classes
- ✅ Autoboxing and unboxing
- ✅ Type conversion and casting
- ✅ Math API methods
- ✅ Arithmetic and boolean expressions
- ✅ Operator precedence
- ✅ Bitwise operators

**Next Module:** [Module 2: Strings and Text Blocks](../module-02/03-strings-stringbuilder.md)

---

**Good luck!** ☕
