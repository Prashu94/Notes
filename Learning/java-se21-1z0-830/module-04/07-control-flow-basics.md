# Module 4.1: Control Flow Basics

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [If-Else Statements](#if-else-statements)
3. [Switch Statements](#switch-statements)
4. [Switch Expressions (Java 14+)](#switch-expressions-java-14)
5. [Pattern Matching for Switch (Java 21)](#pattern-matching-for-switch-java-21)
6. [Best Practices](#best-practices)
7. [Common Pitfalls](#common-pitfalls)

---

## Introduction

Control flow statements determine the order in which code executes. Java provides several mechanisms for conditional execution: if-else statements and switch statements/expressions.

---

## If-Else Statements

The if-else statement evaluates a boolean condition and executes code based on the result.

### Basic If Statement

```java
int age = 18;

if (age >= 18) {
    System.out.println("Adult");
}
// Prints: Adult
```

### If-Else

```java
int score = 75;

if (score >= 60) {
    System.out.println("Pass");
} else {
    System.out.println("Fail");
}
// Prints: Pass
```

### If-Else-If Ladder

```java
int score = 85;

if (score >= 90) {
    System.out.println("A");
} else if (score >= 80) {
    System.out.println("B");
} else if (score >= 70) {
    System.out.println("C");
} else if (score >= 60) {
    System.out.println("D");
} else {
    System.out.println("F");
}
// Prints: B
```

### Nested If

```java
int age = 25;
boolean hasLicense = true;

if (age >= 18) {
    if (hasLicense) {
        System.out.println("Can drive");
    } else {
        System.out.println("Need license");
    }
} else {
    System.out.println("Too young");
}
// Prints: Can drive
```

### Ternary Operator

The ternary operator is a shorthand for if-else:

```java
int age = 20;
String status = (age >= 18) ? "Adult" : "Minor";
System.out.println(status);  // Prints: Adult

// Equivalent to:
String status2;
if (age >= 18) {
    status2 = "Adult";
} else {
    status2 = Minor";
}
```

---

## Switch Statements

Switch statements provide multi-way branching based on a single value.

### Traditional Switch (Before Java 14)

```java
int day = 3;
String dayName;

switch (day) {
    case 1:
        dayName = "Monday";
        break;
    case 2:
        dayName = "Tuesday";
        break;
    case 3:
        dayName = "Wednesday";
        break;
    case 4:
        dayName = "Thursday";
        break;
    case 5:
        dayName = "Friday";
        break;
    case 6:
    case 7:
        dayName = "Weekend";
        break;
    default:
        dayName = "Invalid";
        break;
}
System.out.println(dayName);  // Prints: Wednesday
```

### Fall-Through Behavior

```java
int month = 2;
int days;

switch (month) {
    case 1: case 3: case 5: case 7: case 8: case 10: case 12:
        days = 31;
        break;
    case 4: case 6: case 9: case 11:
        days = 30;
        break;
    case 2:
        days = 28;  // Simplified
        break;
    default:
        days = 0;
        break;
}
System.out.println(days);  // Prints: 28
```

### Supported Types for Switch

Switch works with:
- **Primitives:** byte, short, char, int
- **Wrapper Classes:** Byte, Short, Character, Integer
- **Enum types**
- **String** (since Java 7)

```java
// String switch
String fruit = "apple";
switch (fruit) {
    case "apple":
        System.out.println("Red fruit");
        break;
    case "banana":
        System.out.println("Yellow fruit");
        break;
    default:
        System.out.println("Unknown fruit");
        break;
}
// Prints: Red fruit

// Enum switch
enum Day { MONDAY, TUESDAY, WEDNESDAY }
Day day = Day.MONDAY;

switch (day) {
    case MONDAY:
        System.out.println("Start of week");
        break;
    case WEDNESDAY:
        System.out.println("Mid week");
        break;
    default:
        System.out.println("Other day");
        break;
}
// Prints: Start of week
```

---

## Switch Expressions (Java 14+)

Switch expressions (introduced in Java 14) provide a more concise and safer alternative to traditional switch statements.

### Arrow Syntax

```java
int day = 3;
String dayName = switch (day) {
    case 1 -> "Monday";
    case 2 -> "Tuesday";
    case 3 -> "Wednesday";
    case 4 -> "Thursday";
    case 5 -> "Friday";
    case 6, 7 -> "Weekend";
    default -> "Invalid";
};
System.out.println(dayName);  // Prints: Wednesday
```

### Key Differences from Traditional Switch

| Feature | Traditional Switch | Switch Expression |
|---------|-------------------|-------------------|
| **Purpose** | Statement (executes code) | Expression (returns value) |
| **Break** | Required to prevent fall-through | Not needed (no fall-through) |
| **Return** | Cannot return value | Returns value |
| **Exhaustiveness** | Not required | Must be exhaustive |
| **Syntax** | case X: | case X -> |

### Multiple Labels

```java
int month = 2;
int days = switch (month) {
    case 1, 3, 5, 7, 8, 10, 12 -> 31;
    case 4, 6, 9, 11 -> 30;
    case 2 -> 28;
    default -> 0;
};
System.out.println(days);  // Prints: 28
```

### Yield for Complex Cases

When a case requires multiple statements, use a block with `yield`:

```java
int day = 5;
String result = switch (day) {
    case 1, 2, 3, 4, 5 -> {
        String type = "Weekday";
        yield type + " - Work day";
    }
    case 6, 7 -> {
        String type = "Weekend";
        yield type + " - Rest day";
    }
    default -> throw new IllegalArgumentException("Invalid day");
};
System.out.println(result);  // Prints: Weekday - Work day
```

### Mixing Styles (Not Recommended)

```java
// Traditional colon syntax in expression
int day = 3;
String result = switch (day) {
    case 1, 2, 3, 4, 5:
        yield "Weekday";
    case 6, 7:
        yield "Weekend";
    default:
        yield "Invalid";
};
// Works, but arrow syntax is preferred
```

---

## Pattern Matching for Switch (Java 21)

Java 21 introduces pattern matching for switch, allowing you to switch on types and extract values.

### Type Patterns

```java
Object obj = "Hello";

String result = switch (obj) {
    case String s -> "String: " + s;
    case Integer i -> "Integer: " + i;
    case Long l -> "Long: " + l;
    case null -> "Null value";
    default -> "Unknown type";
};
System.out.println(result);  // Prints: String: Hello
```

### Guarded Patterns

```java
Object obj = 42;

String result = switch (obj) {
    case String s when s.length() > 5 -> "Long string";
    case String s -> "Short string";
    case Integer i when i > 100 -> "Large number";
    case Integer i -> "Small number: " + i;
    case null -> "Null";
    default -> "Other";
};
System.out.println(result);  // Prints: Small number: 42
```

### Pattern Matching with Records

```java
record Point(int x, int y) {}

Object obj = new Point(3, 4);

String result = switch (obj) {
    case Point(int x, int y) when x == 0 && y == 0 -> "Origin";
    case Point(int x, int y) when x == y -> "Diagonal";
    case Point(int x, int y) -> "Point at (" + x + ", " + y + ")";
    case null -> "Null";
    default -> "Not a point";
};
System.out.println(result);  // Prints: Point at (3, 4)
```

### Null Handling

Traditional switch throws NullPointerException for null. Pattern matching switch can handle null explicitly:

```java
String str = null;

// Traditional switch - throws NPE
// switch (str) { ... }  // NullPointerException

// Pattern matching switch - handles null
String result = switch (str) {
    case null -> "It's null";
    case String s -> "It's a string: " + s;
};
System.out.println(result);  // Prints: It's null
```

### Exhaustiveness

Switch expressions must be exhaustive (cover all possible values):

```java
// Compile error - not exhaustive (missing default)
// Integer num = 5;
// String result = switch (num) {
//     case 1 -> "One";
//     case 2 -> "Two";
// };  // Error: not exhaustive

// Fixed with default
Integer num = 5;
String result = switch (num) {
    case 1 -> "One";
    case 2 -> "Two";
    case null -> "Null";
    default -> "Other";
};

// Or handle with pattern
String result2 = switch (num) {
    case Integer i when i == 1 -> "One";
    case Integer i when i == 2 -> "Two";
    case null -> "Null";
    case Integer i -> "Other: " + i;  // Exhaustive
};
```

---

## Best Practices

### 1. Prefer Switch Expressions Over Statements

```java
// Bad: Traditional switch statement
int day = 3;
String result;
switch (day) {
    case 1:
        result = "Mon";
        break;
    case 2:
        result = "Tue";
        break;
    default:
        result = "Other";
        break;
}

// Good: Switch expression
String result2 = switch (day) {
    case 1 -> "Mon";
    case 2 -> "Tue";
    default -> "Other";
};
```

### 2. Use Pattern Matching for Type Checks

```java
// Bad: instanceof with casting
Object obj = "Hello";
if (obj instanceof String) {
    String s = (String) obj;
    System.out.println(s.toUpperCase());
} else if (obj instanceof Integer) {
    Integer i = (Integer) obj;
    System.out.println(i * 2);
}

// Good: Pattern matching switch
String result = switch (obj) {
    case String s -> s.toUpperCase();
    case Integer i -> String.valueOf(i * 2);
    case null -> "null";
    default -> "unknown";
};
```

### 3. Avoid Deep Nesting

```java
// Bad: Deep nesting
if (condition1) {
    if (condition2) {
        if (condition3) {
            // code
        }
    }
}

// Good: Early returns or flat structure
if (!condition1) return;
if (!condition2) return;
if (!condition3) return;
// code
```

### 4. Be Exhaustive

```java
// Good: Always handle default case
int day = getUserInput();
String result = switch (day) {
    case 1, 2, 3, 4, 5 -> "Weekday";
    case 6, 7 -> "Weekend";
    default -> throw new IllegalArgumentException("Invalid day: " + day);
};
```

---

## Common Pitfalls

### 1. Forgetting Break in Traditional Switch

```java
int day = 2;
switch (day) {
    case 1:
        System.out.println("Mon");
        // Missing break - falls through!
    case 2:
        System.out.println("Tue");
        break;
}
// Prints both "Mon" and "Tue" if day is 1
```

### 2. Using = Instead of == in If

```java
int x = 5;
// if (x = 10) { }  // Compilation error
// Should be:
if (x == 10) { }
```

### 3. Non-Exhaustive Switch Expression

```java
// Compile error
// int num = 5;
// String result = switch (num) {
//     case 1 -> "One";
//     case 2 -> "Two";
// };  // Error: missing default

// Fixed
String result = switch (num) {
    case 1 -> "One";
    case 2 -> "Two";
    default -> "Other";
};
```

### 4. Unreachable Code After Return

```java
if (condition) {
    return;
    // System.out.println("Hello");  // Unreachable code error
}
```

### 5. Null in Traditional Switch

```java
String str = null;
// switch (str) {  // NullPointerException
//     case "A" -> System.out.println("A");
// }

// Solution: Check null first
if (str != null) {
    switch (str) {
        case "A" -> System.out.println("A");
    }
}

// Or use pattern matching switch (Java 21)
switch (str) {
    case null -> System.out.println("Null");
    case "A" -> System.out.println("A");
    default -> System.out.println("Other");
}
```

---

## Summary

### If-Else
- Used for boolean conditions
- Supports if, if-else, if-else-if ladder
- Ternary operator for simple cases

### Traditional Switch
- Requires break to prevent fall-through
- Works with byte, short, char, int, String, enum
- Cannot return value directly

### Switch Expression (Java 14+)
- Returns a value
- No fall-through (no break needed)
- Must be exhaustive
- Arrow syntax preferred

### Pattern Matching Switch (Java 21)
- Type patterns for instanceof replacement
- Guarded patterns with `when`
- Null handling support
- Record deconstruction

---

## Practice Questions

Ready to test your knowledge? Proceed to [Control Flow Practice Questions](07-practice-questions.md)!

---

**Next:** [Practice Questions - Control Flow Basics](07-practice-questions.md)  
**Previous:** [Time Zones and DST](../module-03/06-timezones-dst.md)

---

**Good luck!** ☕
