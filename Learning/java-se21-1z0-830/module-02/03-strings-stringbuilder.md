# Module 2.1: String and StringBuilder Classes

## 📚 Table of Contents
1. [Overview](#overview)
2. [String Basics](#string-basics)
3. [String Immutability](#string-immutability)
4. [String Pool](#string-pool)
5. [String Methods](#string-methods)
6. [StringBuilder Class](#stringbuilder-class)
7. [StringBuffer vs StringBuilder](#stringbuffer-vs-stringbuilder)
8. [Performance Considerations](#performance-considerations)
9. [Best Practices](#best-practices)

---

## Overview

Strings are one of the most commonly used classes in Java. Understanding String manipulation, immutability, and the difference between String, StringBuilder, and StringBuffer is crucial for the Java SE 21 exam.

---

## String Basics

### Creating Strings

```java
// String literals
String s1 = "Hello";
String s2 = "World";

// Using new keyword
String s3 = new String("Hello");

// From char array
char[] chars = {'H', 'e', 'l', 'l', 'o'};
String s4 = new String(chars);

// From byte array
byte[] bytes = {72, 101, 108, 108, 111};
String s5 = new String(bytes);

// Empty string
String empty1 = "";
String empty2 = new String();
```

### String Concatenation

```java
// Using + operator
String full = "Hello" + " " + "World";  // "Hello World"

// Mixing types
String result = "Value: " + 42;  // "Value: 42"
String result2 = 10 + 20 + " = Total";  // "30 = Total"
String result3 = "Total = " + 10 + 20;  // "Total = 1020"

// Using concat() method
String s1 = "Hello".concat(" World");  // "Hello World"

// Using join()
String joined = String.join(", ", "Java", "Python", "C++");  
// "Java, Python, C++"
```

---

## String Immutability

**Strings are immutable** - once created, their value cannot be changed.

```java
String s = "Hello";
s.toUpperCase();  // Returns "HELLO", but doesn't change s
System.out.println(s);  // Still "Hello"

// Correct way
s = s.toUpperCase();  // Now s references "HELLO"
```

### Why Immutability?

1. **Security**: String parameters can't be modified
2. **Thread Safety**: Can be shared between threads safely
3. **String Pool**: Enables string interning for memory efficiency
4. **Hashcode Caching**: Hashcode can be cached (used in HashMap)

### Implications

```java
String s = "Java";
s = s + " SE";     // Creates new String object
s = s + " 21";     // Creates another new String object

// Each concatenation creates a new String object in memory
// Original "Java" object is eligible for garbage collection
```

---

## String Pool

Java maintains a **String pool** (in the heap) to optimize memory usage.

### String Literals vs new String()

```java
// String literals - stored in pool
String s1 = "Hello";
String s2 = "Hello";
System.out.println(s1 == s2);  // true (same object in pool)

// Using new keyword - creates new object
String s3 = new String("Hello");
System.out.println(s1 == s3);  // false (different objects)
System.out.println(s1.equals(s3));  // true (same content)
```

### intern() Method

```java
String s1 = "Hello";
String s2 = new String("Hello");
String s3 = s2.intern();  // Returns reference from pool

System.out.println(s1 == s2);  // false
System.out.println(s1 == s3);  // true (both from pool)
```

### Compile-Time Concatenation

```java
String s1 = "Java" + "SE";     // Compiled to "JavaSE"
String s2 = "JavaSE";
System.out.println(s1 == s2);  // true (same pool object)

// Runtime concatenation
String part = "Java";
String s3 = part + "SE";       // Creates new object
System.out.println(s1 == s3);  // false
```

---

## String Methods

### Length and Character Access

```java
String s = "Hello World";

// Length
int len = s.length();  // 11

// Character at index
char c = s.charAt(0);  // 'H'
char last = s.charAt(s.length() - 1);  // 'd'
// char error = s.charAt(20);  // StringIndexOutOfBoundsException

// Get characters as array
char[] chars = s.toCharArray();  // ['H','e','l','l','o',' ','W','o','r','l','d']
```

### Case Conversion

```java
String s = "Hello World";

String upper = s.toUpperCase();  // "HELLO WORLD"
String lower = s.toLowerCase();  // "hello world"

// Locale-specific (important for Turkish, etc.)
String upperTR = s.toUpperCase(Locale.forLanguageTag("tr"));
```

### Searching

```java
String s = "Hello World Hello";

// indexOf
int index1 = s.indexOf('o');      // 4 (first occurrence)
int index2 = s.indexOf("World");  // 6
int index3 = s.indexOf('o', 5);   // 7 (search from index 5)
int index4 = s.indexOf("Java");   // -1 (not found)

// lastIndexOf
int last1 = s.lastIndexOf('o');   // 13 (last occurrence)
int last2 = s.lastIndexOf("Hello");  // 12

// contains
boolean has = s.contains("World");  // true
boolean has2 = s.contains("Java");  // false
```

### Substring

```java
String s = "Hello World";

// substring(beginIndex)
String sub1 = s.substring(6);  // "World"

// substring(beginIndex, endIndex) - endIndex is exclusive
String sub2 = s.substring(0, 5);  // "Hello"
String sub3 = s.substring(6, 11);  // "World"

// Empty substring
String empty = s.substring(5, 5);  // ""
```

### Comparison

```java
String s1 = "Java";
String s2 = "Java";
String s3 = "java";

// equals - case-sensitive
boolean eq1 = s1.equals(s2);  // true
boolean eq2 = s1.equals(s3);  // false

// equalsIgnoreCase
boolean eq3 = s1.equalsIgnoreCase(s3);  // true

// compareTo - lexicographic comparison
int cmp1 = "abc".compareTo("abc");  // 0 (equal)
int cmp2 = "abc".compareTo("def");  // negative (abc < def)
int cmp3 = "def".compareTo("abc");  // positive (def > abc)

// compareToIgnoreCase
int cmp4 = "ABC".compareToIgnoreCase("abc");  // 0
```

### Checking Start/End

```java
String s = "HelloWorld.java";

// startsWith
boolean starts1 = s.startsWith("Hello");  // true
boolean starts2 = s.startsWith("World");  // false
boolean starts3 = s.startsWith("World", 5);  // true (from index 5)

// endsWith
boolean ends1 = s.endsWith(".java");  // true
boolean ends2 = s.endsWith(".txt");   // false
```

### Trimming and Stripping

```java
String s = "  Hello World  ";

// trim() - removes leading/trailing spaces
String trimmed = s.trim();  // "Hello World"

// strip() - removes leading/trailing whitespace (Unicode-aware, Java 11+)
String stripped = s.strip();  // "Hello World"

// stripLeading() - remove only leading whitespace
String stripLeft = s.stripLeading();  // "Hello World  "

// stripTrailing() - remove only trailing whitespace
String stripRight = s.stripTrailing();  // "  Hello World"
```

### Replacing

```java
String s = "Hello World";

// replace - all occurrences
String r1 = s.replace('o', 'O');  // "HellO WOrld"
String r2 = s.replace("World", "Java");  // "Hello Java"

// replaceFirst - first occurrence
String r3 = "aaa".replaceFirst("a", "b");  // "baa"

// replaceAll - using regex
String r4 = "a1b2c3".replaceAll("\\d", "X");  // "aXbXcX"
```

### Splitting

```java
String s = "Java,Python,C++";

// split
String[] parts = s.split(",");  // ["Java", "Python", "C++"]

// split with limit
String[] parts2 = "a:b:c:d".split(":", 2);  // ["a", "b:c:d"]

// split by whitespace
String sentence = "Hello World Java";
String[] words = sentence.split("\\s+");  // ["Hello", "World", "Java"]
```

### Checking Empty/Blank

```java
String s1 = "";
String s2 = "   ";
String s3 = "Hello";

// isEmpty() - checks if length is 0
boolean empty1 = s1.isEmpty();  // true
boolean empty2 = s2.isEmpty();  // false (contains spaces)
boolean empty3 = s3.isEmpty();  // false

// isBlank() - checks if empty or contains only whitespace (Java 11+)
boolean blank1 = s1.isBlank();  // true
boolean blank2 = s2.isBlank();  // true
boolean blank3 = s3.isBlank();  // false
```

### Other Useful Methods

```java
// repeat() - Java 11+
String repeated = "Ha".repeat(3);  // "HaHaHa"

// format()
String formatted = String.format("Name: %s, Age: %d", "Alice", 25);
// "Name: Alice, Age: 25"

// valueOf() - convert to String
String s1 = String.valueOf(42);     // "42"
String s2 = String.valueOf(3.14);   // "3.14"
String s3 = String.valueOf(true);   // "true"

// matches() - regex matching
boolean matches = "123".matches("\\d+");  // true
```

---

## StringBuilder Class

StringBuilder is a **mutable** sequence of characters, designed for efficient string manipulation.

### Creating StringBuilder

```java
// Empty StringBuilder
StringBuilder sb1 = new StringBuilder();

// With initial capacity
StringBuilder sb2 = new StringBuilder(50);

// From String
StringBuilder sb3 = new StringBuilder("Hello");

// From CharSequence
CharSequence cs = "World";
StringBuilder sb4 = new StringBuilder(cs);
```

### Appending

```java
StringBuilder sb = new StringBuilder("Hello");

// append
sb.append(" World");      // "Hello World"
sb.append(42);            // "Hello World42"
sb.append(true);          // "Hello World42true"
sb.append(3.14);          // "Hello World42true3.14"

// Method chaining
StringBuilder sb2 = new StringBuilder()
    .append("Java")
    .append(" ")
    .append("SE")
    .append(" ")
    .append(21);  // "Java SE 21"
```

### Inserting

```java
StringBuilder sb = new StringBuilder("Hello World");

// insert at index
sb.insert(5, ",");        // "Hello, World"
sb.insert(0, ">>> ");     // ">>> Hello, World"
```

### Deleting

```java
StringBuilder sb = new StringBuilder("Hello World");

// delete(start, end) - end is exclusive
sb.delete(5, 11);  // "Hello"

// deleteCharAt(index)
sb.deleteCharAt(0);  // "ello"
```

### Replacing

```java
StringBuilder sb = new StringBuilder("Hello World");

// replace(start, end, str)
sb.replace(6, 11, "Java");  // "Hello Java"
```

### Reversing

```java
StringBuilder sb = new StringBuilder("Hello");
sb.reverse();  // "olleH"
```

### Other Methods

```java
StringBuilder sb = new StringBuilder("Hello World");

// length
int len = sb.length();  // 11

// capacity (internal buffer size)
int cap = sb.capacity();  // typically 16 + initial string length

// charAt
char c = sb.charAt(0);  // 'H'

// setCharAt
sb.setCharAt(0, 'h');  // "hello World"

// substring
String sub = sb.substring(0, 5);  // "hello" (returns String)

// toString
String s = sb.toString();  // Convert to String
```

---

## StringBuffer vs StringBuilder

| Feature | StringBuilder | StringBuffer |
|---------|--------------|--------------|
| Thread-Safe | ❌ No | ✅ Yes (synchronized) |
| Performance | ⚡ Faster | 🐌 Slower |
| When to Use | Single-threaded | Multi-threaded |
| Since | Java 5 | Java 1.0 |

```java
// StringBuilder - faster, not thread-safe
StringBuilder sb = new StringBuilder();

// StringBuffer - slower, thread-safe
StringBuffer sbuf = new StringBuffer();

// Both have identical methods
sb.append("Hello");
sbuf.append("Hello");
```

**Recommendation**: Use StringBuilder unless thread safety is explicitly required.

---

## Performance Considerations

### String Concatenation in Loops

```java
// ❌ BAD - Creates many String objects
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i;  // Creates new String each iteration
}

// ✅ GOOD - Efficient
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);
}
String result = sb.toString();
```

### Modern Java Optimization

```java
// Java compiler optimizes simple concatenations
String s = "Hello" + " " + "World";  // Optimized at compile-time

// Runtime concatenation uses StringBuilder internally (Java 9+)
String name = "Alice";
String greeting = "Hello " + name;  // Compiler uses StringBuilder
```

---

## Best Practices

### ✅ DO:

1. **Use String for immutable text**
   ```java
   String constant = "API_KEY";
   ```

2. **Use StringBuilder for string building**
   ```java
   StringBuilder html = new StringBuilder();
   html.append("<html>").append("<body>").append("</body>").append("</html>");
   ```

3. **Use equals() to compare strings**
   ```java
   if (s1.equals(s2)) { }
   ```

4. **Check for null before calling methods**
   ```java
   if (str != null && !str.isEmpty()) { }
   ```

5. **Use String.format() or formatted() for complex strings**
   ```java
   String msg = String.format("User %s has %d points", name, points);
   ```

### ❌ DON'T:

1. **Don't use == to compare string content**
   ```java
   // Bad
   if (s1 == s2) { }
   
   // Good
   if (s1.equals(s2)) { }
   ```

2. **Don't concatenate strings in loops**
   ```java
   // Bad
   String result = "";
   for (String s : list) {
       result += s;
   }
   ```

3. **Don't use StringBuffer unless needed**
   ```java
   // Use StringBuilder instead
   StringBuilder sb = new StringBuilder();
   ```

---

## Summary

- **String** is immutable, thread-safe, stored in string pool
- **StringBuilder** is mutable, faster, not thread-safe (preferred)
- **StringBuffer** is mutable, thread-safe, slower
- Use **equals()** to compare string content, not `==`
- String concatenation in loops is inefficient - use StringBuilder
- String pool optimizes memory for string literals
- Common methods: length(), charAt(), substring(), indexOf(), replace(), split()

---

## Next Steps

Proceed to [Practice Questions](03-practice-questions.md) to test your understanding of String and StringBuilder!
