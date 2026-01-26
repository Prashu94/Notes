# Module 1.1: Primitives and Wrapper Classes - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the range of the `byte` data type in Java?

A) -256 to 255  
B) -128 to 127  
C) 0 to 255  
D) -32768 to 32767  

**Answer:** B

**Explanation:**
The `byte` data type is 8 bits (1 byte) and is signed, so its range is from -2^7 to 2^7 - 1, which equals -128 to 127.

---

### Question 2
What is the output of the following code?

```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Integer objects with values from -128 to 127 are cached by the JVM. When you create Integer objects with values in this range using autoboxing, they reference the same cached object. Therefore, `a == b` returns `true` because both variables reference the same object in the cache. Note: This would be `false` for values outside the cached range (e.g., 128).

---

### Question 3
Which of the following statements will compile without errors?

A) `byte b = 128;`  
B) `short s = 32768;`  
C) `int i = 2147483648;`  
D) `long l = 2147483648L;`  

**Answer:** D

**Explanation:**
- A is incorrect: 128 is outside the byte range (-128 to 127)
- B is incorrect: 32768 is outside the short range (-32768 to 32767)
- C is incorrect: 2147483648 is outside the int range (-2147483648 to 2147483647)
- D is correct: Adding the 'L' suffix makes it a long literal, which can hold this value

---

### Question 4
What is the result of the following code?

```java
Integer num = null;
int primitive = num;
System.out.println(primitive);
```

A) 0  
B) null  
C) Compilation error  
D) NullPointerException at runtime  

**Answer:** D

**Explanation:**
When unboxing a null wrapper object to a primitive, Java attempts to call the `intValue()` method on null, which throws a NullPointerException. This is a common pitfall when using autoboxing/unboxing.

---

### Question 5
What will be the output of the following code?

```java
double d = 5 / 2;
System.out.println(d);
```

A) 2.0  
B) 2.5  
C) 2  
D) Compilation error  

**Answer:** A

**Explanation:**
Both 5 and 2 are int literals. Integer division is performed first (5 / 2 = 2), then the result (2) is widened to double (2.0). To get 2.5, at least one operand must be a floating-point type: `double d = 5.0 / 2;` or `double d = (double) 5 / 2;`

---

### Question 6
Which wrapper class method should be used to create wrapper objects (recommended since Java 9)?

A) Constructor (e.g., `new Integer(10)`)  
B) `valueOf()` method  
C) Autoboxing  
D) Both B and C  

**Answer:** D

**Explanation:**
Since Java 9, wrapper class constructors are deprecated. The recommended approaches are:
- Using `valueOf()` method: `Integer.valueOf(10)` - explicitly creates wrapper object
- Using autoboxing: `Integer i = 10;` - implicitly creates wrapper object
Both are acceptable and utilize object caching for better performance.

---

### Question 7
What is the output of the following code?

```java
byte b = 10;
b = b + 1;
System.out.println(b);
```

A) 11  
B) 10  
C) Compilation error  
D) Runtime exception  

**Answer:** C

**Explanation:**
When performing arithmetic operations on byte, short, or char, they are promoted to int. The expression `b + 1` returns an int, which cannot be implicitly assigned back to byte. This requires an explicit cast: `b = (byte)(b + 1);` or use compound assignment: `b += 1;` (which includes implicit casting).

---

### Question 8
What will be printed by the following code?

```java
Integer a = 200;
Integer b = 200;
System.out.println(a == b);
System.out.println(a.equals(b));
```

A) true, true  
B) false, false  
C) false, true  
D) true, false  

**Answer:** C

**Explanation:**
- `a == b` is false because 200 is outside the Integer cache range (-128 to 127), so `a` and `b` reference different objects.
- `a.equals(b)` is true because the `equals()` method compares the actual integer values, which are both 200.

Always use `equals()` to compare wrapper object values!

---

### Question 9
Which of the following is the correct way to parse a String to an int?

A) `int i = (int) "123";`  
B) `int i = Integer.valueOf("123");`  
C) `int i = Integer.parseInt("123");`  
D) Both B and C  

**Answer:** D

**Explanation:**
- A is incorrect: Cannot cast String to int
- B is correct: `Integer.valueOf("123")` returns an Integer object, which is auto-unboxed to int
- C is correct: `Integer.parseInt("123")` directly returns a primitive int
- Both B and C work correctly, though C is more direct for getting a primitive int

---

### Question 10
What is the output of the following code?

```java
int i = 130;
byte b = (byte) i;
System.out.println(b);
```

A) 130  
B) 127  
C) -126  
D) Compilation error  

**Answer:** C

**Explanation:**
When narrowing an int (130) to a byte, values outside the byte range (-128 to 127) wrap around. 130 in binary is `10000010`. When interpreted as a signed byte, this becomes -126. The calculation: 130 - 256 = -126 (where 256 is the range of byte values).

---

### Question 11
Which of the following statements about primitive types is FALSE?

A) Primitives are stored on the stack  
B) Primitives have default values  
C) Primitives can be null  
D) Primitives are more memory-efficient than wrapper objects  

**Answer:** C

**Explanation:**
- A is true (for local variables): Primitives are stored on the stack
- B is true: Primitives have default values (0, 0.0, false, '\u0000')
- C is FALSE: Primitives cannot be null; only reference types (including wrappers) can be null
- D is true: Primitives use less memory than wrapper objects

---

### Question 12
What is the result of the following code?

```java
Boolean b1 = Boolean.parseBoolean("yes");
Boolean b2 = Boolean.parseBoolean("true");
System.out.println(b1 + " " + b2);
```

A) true true  
B) false true  
C) true false  
D) false false  

**Answer:** B

**Explanation:**
`Boolean.parseBoolean(String)` only returns `true` if the string is "true" (case-insensitive). Any other string, including "yes", "1", "TRUE" (mixed case), returns `false`. So:
- `b1 = false` ("yes" is not "true")
- `b2 = true` ("true" matches)

---

### Question 13
What will the following code print?

```java
float f = 3.14f;
int i = (int) f;
System.out.println(i);
```

A) 3  
B) 3.14  
C) 4  
D) Compilation error  

**Answer:** A

**Explanation:**
When casting a floating-point type to an integer type, the fractional part is truncated (not rounded). So `(int) 3.14f` becomes `3`. Note: This is truncation, not rounding. `(int) 3.9f` would also be `3`.

---

### Question 14
Which of the following will cause a compilation error?

A) `Long l = 100;`  
B) `Float f = 3.14;`  
C) `Character c = 65;`  
D) `Boolean b = true;`  

**Answer:** B

**Explanation:**
- A is correct: `100` is an int literal, which is widened to long, then autoboxed to Long
- B causes compilation error: `3.14` is a double literal, which cannot be narrowed to float implicitly. Should be `Float f = 3.14f;`
- C is correct: `65` is widened to char (character with value 65, which is 'A'), then autoboxed
- D is correct: `true` is autoboxed to Boolean

---

### Question 15
What is the output of the following code?

```java
byte b = 10;
b *= 2;
System.out.println(b);
```

A) 20  
B) 10  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Compound assignment operators (`*=`, `+=`, etc.) include an implicit cast. `b *= 2` is equivalent to `b = (byte)(b * 2)`. Even though `b * 2` returns an int, the compound operator casts the result back to byte automatically. The result is 20.

---

### Question 16
What is the value of `Integer.MAX_VALUE + 1`?

A) 2147483648  
B) Integer.MIN_VALUE  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
When an integer overflows, it wraps around to the minimum value. `Integer.MAX_VALUE` is 2,147,483,647. Adding 1 causes overflow, resulting in -2,147,483,648, which is `Integer.MIN_VALUE`. This is a common source of bugs in Java programs.

---

### Question 17
Which of the following correctly creates a Character wrapper object with value 'A'?

```java
// I
Character c1 = 'A';

// II
Character c2 = Character.valueOf('A');

// III
Character c3 = new Character('A');

// IV
Character c4 = 65;
```

A) I and II only  
B) I, II, and III  
C) I, II, and IV  
D) All of them  

**Answer:** C

**Explanation:**
- I is correct: Autoboxing converts char 'A' to Character
- II is correct: Using `valueOf()` method (recommended approach)
- III is deprecated: Constructor is deprecated since Java 9
- IV is correct: 65 is the ASCII value of 'A', autoboxed to Character (after int is narrowed to char)

For the exam, be aware that option III would compile (though deprecated), but the best answers are I and II. However, IV also works, making C the most accurate answer.

---

### Question 18
What is the output of the following code?

```java
double d = 0.1 + 0.2;
System.out.println(d == 0.3);
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
Due to floating-point precision limitations, `0.1 + 0.2` does not exactly equal `0.3`. The actual result is approximately `0.30000000000000004`. When comparing floating-point numbers, use a small epsilon value or use `BigDecimal` for exact decimal arithmetic.

---

### Question 19
What does the following code print?

```java
Integer i = 10;
Integer j = 10;
System.out.println(i.equals(j));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
The `equals()` method of the Integer class compares the actual integer values. Since both `i` and `j` have the value 10, `equals()` returns true. This is the correct way to compare wrapper object values, regardless of whether they are in the cache range or not.

---

### Question 20
What is the result of the following code?

```java
char c = 'A';
int i = c;
System.out.println(i);
```

A) A  
B) 65  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
When a `char` is assigned to an `int`, widening conversion occurs automatically. The character 'A' has a Unicode (ASCII) value of 65, so the variable `i` gets the value 65. This is a widening primitive conversion from char to int, which is allowed without casting.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered primitives and wrappers.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Comparing wrappers with ==** instead of `equals()`
2. **Forgetting about Integer caching** for values -128 to 127
3. **Not handling null** before unboxing
4. **Integer division** giving unexpected results
5. **Overflow** when exceeding max values
6. **Mixing types** without understanding promotions
7. **Using deprecated constructors** instead of `valueOf()`

---

## Next Steps

✅ **Scored 16+?** Move to [Math API and Expressions](02-math-api-expressions.md)

⚠️ **Scored below 16?** Review [Primitives and Wrappers Theory](01-primitives-wrappers.md) and retake this quiz.

---

**Good luck!** ☕
