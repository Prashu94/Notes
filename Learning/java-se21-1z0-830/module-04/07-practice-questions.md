# Module 4.1: Control Flow Basics - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
int x = 10;
if (x > 5)
    System.out.println("A");
    System.out.println("B");
```

A) A  
B) AB (on separate lines)  
C) B  
D) Compilation error  

**Answer:** B

**Explanation:**
Without braces, only the first statement (`println("A")`) is part of the if block. `println("B")` always executes regardless of the condition. Output: A and B on separate lines.

---

### Question 2
What does the following code print?

```java
int day = 5;
String result = switch (day) {
    case 1, 2, 3, 4, 5 -> "Weekday";
    case 6, 7 -> "Weekend";
};
System.out.println(result);
```

A) Weekday  
B) Weekend  
C) Compilation error  
D) Runtime exception  

**Answer:** C

**Explanation:**
Switch expressions must be exhaustive. This switch doesn't have a default case and doesn't cover all possible int values. Compilation error.

---

### Question 3
What is the value of `result`?

```java
int score = 85;
String result = (score >= 60) ? "Pass" : "Fail";
```

A) Pass  
B) Fail  
C) true  
D) Compilation error  

**Answer:** A

**Explanation:**
The ternary operator evaluates `score >= 60` (true), so it returns "Pass".

---

### Question 4
What happens with this code?

```java
String str = null;
switch (str) {
    case "A":
        System.out.println("A");
        break;
    default:
        System.out.println("Default");
        break;
}
```

A) Prints: A  
B) Prints: Default  
C) NullPointerException  
D) Compilation error  

**Answer:** C

**Explanation:**
Traditional switch (without pattern matching) throws NullPointerException when the selector is null. This is a common pitfall.

---

### Question 5
What is the output?

```java
int num = 2;
switch (num) {
    case 1:
        System.out.println("One");
    case 2:
        System.out.println("Two");
    case 3:
        System.out.println("Three");
        break;
    default:
        System.out.println("Other");
}
```

A) Two  
B) Two Three  
C) Two Three Other  
D) Compilation error  

**Answer:** B

**Explanation:**
Missing break statements cause fall-through. When num is 2, it prints "Two", then falls through to case 3 and prints "Three", then breaks.

---

### Question 6
Which of the following types can be used in a switch statement?

A) long  
B) boolean  
C) String  
D) float  

**Answer:** C

**Explanation:**
Switch works with byte, short, char, int, their wrapper classes, String, and enum. It does NOT work with long, boolean, or float.

---

### Question 7
What is the output?

```java
int x = 10, y = 20;
if (x > 5)
    if (y > 15)
        System.out.println("A");
else
    System.out.println("B");
```

A) A  
B) B  
C) AB  
D) Nothing  

**Answer:** A

**Explanation:**
The else belongs to the nearest if (the inner one). Since both conditions are true (x > 5 and y > 15), it prints "A". The else would execute only if y <= 15.

---

### Question 8
What does the following code print?

```java
Object obj = 42;
String result = switch (obj) {
    case Integer i when i > 50 -> "Large";
    case Integer i -> "Small: " + i;
    case String s -> "String";
    default -> "Other";
};
System.out.println(result);
```

A) Large  
B) Small: 42  
C) Other  
D) Compilation error  

**Answer:** B

**Explanation:**
Pattern matching switch (Java 21). The first case has a guard (`i > 50`) which is false (42 <= 50). The second case matches (Integer without guard) and prints "Small: 42".

---

### Question 9
What is the value of `result`?

```java
int day = 3;
String result = switch (day) {
    case 1 -> "Mon";
    case 2 -> "Tue";
    case 3 -> {
        String temp = "Wed";
        yield temp + "nesday";
    }
    default -> "Other";
};
```

A) Wed  
B) Wednesday  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
When a case requires multiple statements, use a block with `yield`. The code yields "Wed" + "nesday" = "Wednesday".

---

### Question 10
What is the output?

```java
int x = 5;
if (x = 10) {
    System.out.println("True");
}
```

A) True  
B) Nothing  
C) Compilation error  
D) Runtime exception  

**Answer:** C

**Explanation:**
`x = 10` is an assignment (returns int), not a boolean comparison. The if condition requires a boolean expression. Use `x == 10` for comparison.

---

### Question 11
What does the following print?

```java
String fruit = "apple";
String result = switch (fruit) {
    case "apple", "orange" -> "Fruit";
    case "carrot" -> "Vegetable";
    default -> "Unknown";
};
System.out.println(result);
```

A) Fruit  
B) apple  
C) Unknown  
D) Compilation error  

**Answer:** A

**Explanation:**
Multiple labels in switch expression. "apple" matches the first case, which returns "Fruit".

---

### Question 12
What is the value of `result`?

```java
boolean flag = true;
String result = flag ? "Yes" : "No";
```

A) Yes  
B) No  
C) true  
D) Compilation error  

**Answer:** A

**Explanation:**
Ternary operator: `condition ? valueIfTrue : valueIfFalse`. Since flag is true, result is "Yes".

---

### Question 13
What is the output?

```java
int month = 2;
String season = switch (month) {
    case 12, 1, 2 -> "Winter";
    case 3, 4, 5 -> "Spring";
    case 6, 7, 8 -> "Summer";
    case 9, 10, 11 -> "Fall";
    default -> "Invalid";
};
System.out.println(season);
```

A) Winter  
B) Spring  
C) Invalid  
D) Compilation error  

**Answer:** A

**Explanation:**
Switch expression with multiple labels. Month 2 (February) is in the first case {12, 1, 2}, so it returns "Winter".

---

### Question 14
What happens with this code?

```java
Object obj = null;
String result = switch (obj) {
    case null -> "Null";
    case String s -> "String";
    case Integer i -> "Integer";
    default -> "Other";
};
```

A) Prints: Null  
B) NullPointerException  
C) Compilation error  
D) Prints: Other  

**Answer:** A

**Explanation:**
Pattern matching switch (Java 21) can handle null explicitly with `case null`. This is a new feature that prevents NullPointerException.

---

### Question 15
What is the output?

```java
int score = 75;
if (score >= 90)
    System.out.println("A");
else if (score >= 80)
    System.out.println("B");
else if (score >= 70)
    System.out.println("C");
else
    System.out.println("F");
```

A) A  
B) B  
C) C  
D) F  

**Answer:** C

**Explanation:**
If-else-if ladder evaluates conditions sequentially. 75 is not >= 90, not >= 80, but is >= 70, so it prints "C" and stops.

---

### Question 16
Which statement about switch expressions is FALSE?

A) They must be exhaustive  
B) They return a value  
C) They require break statements  
D) They use arrow syntax (->)  

**Answer:** C

**Explanation:**
Switch expressions do NOT require break statements (no fall-through with arrow syntax). They must be exhaustive, return a value, and commonly use arrow syntax.

---

### Question 17
What is the output?

```java
enum Day { MON, TUE, WED }
Day day = Day.TUE;
switch (day) {
    case MON:
        System.out.println("Monday");
        break;
    case TUE:
        System.out.println("Tuesday");
        break;
}
```

A) Monday  
B) Tuesday  
C) Nothing  
D) Compilation error  

**Answer:** B

**Explanation:**
Enum switch statement. Day.TUE matches the second case, printing "Tuesday". Note: Traditional switch statements don't require exhaustiveness.

---

### Question 18
What is the value of `result`?

```java
int x = 10;
int y = 20;
int result = (x > 5) ? (y > 15 ? 1 : 2) : 3;
```

A) 1  
B) 2  
C) 3  
D) Compilation error  

**Answer:** A

**Explanation:**
Nested ternary: x > 5 is true, so evaluate (y > 15 ? 1 : 2). Since y > 15 is true, result is 1.

---

### Question 19
What is the output?

```java
int day = 8;
String result = switch (day) {
    case 1, 2, 3, 4, 5 -> "Weekday";
    case 6, 7 -> "Weekend";
    default -> "Invalid day";
};
System.out.println(result);
```

A) Weekday  
B) Weekend  
C) Invalid day  
D) Compilation error  

**Answer:** C

**Explanation:**
Day 8 doesn't match any case, so the default case executes, returning "Invalid day".

---

### Question 20
What does the following code print?

```java
Object obj = "Hello";
String result = switch (obj) {
    case String s when s.length() > 10 -> "Long";
    case String s when s.length() > 3 -> "Medium";
    case String s -> "Short";
    case null -> "Null";
    default -> "Other";
};
System.out.println(result);
```

A) Long  
B) Medium  
C) Short  
D) Other  

**Answer:** B

**Explanation:**
Pattern matching with guards. "Hello" length is 5. First guard (length > 10) is false. Second guard (length > 3) is true, so it returns "Medium".

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered control flow basics.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Missing braces in if** - only first statement is conditional
2. **Forgetting break in traditional switch** - causes fall-through
3. **Using = instead of ==** - assignment vs comparison
4. **Null in traditional switch** - throws NullPointerException
5. **Non-exhaustive switch expression** - missing default case
6. **Wrong else pairing** - else belongs to nearest if
7. **Unsupported types** - switch doesn't work with long, boolean, float

---

## Next Steps

✅ **Scored 16+?** Move to [Loops and Iteration](08-loops-iteration.md)

⚠️ **Scored below 16?** Review [Control Flow Basics Theory](07-control-flow-basics.md) and retake this quiz.

---

**Good luck!** ☕
