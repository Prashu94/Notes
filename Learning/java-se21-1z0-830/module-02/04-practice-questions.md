# Module 2.2: Text Blocks - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
Which Java version introduced text blocks as a standard feature?

A) Java 11  
B) Java 13  
C) Java 15  
D) Java 17  

**Answer:** C

**Explanation:**
Text blocks were introduced as a preview feature in Java 13 and 14, and became a standard feature in Java 15.

---

### Question 2
What is the output of the following code?

```java
String text = """
    Hello
    World
    """;
System.out.println(text.length());
```

A) 11  
B) 12  
C) 13  
D) Compilation error  

**Answer:** B

**Explanation:**
The text block contains "Hello\nWorld\n" (Hello + newline + World + newline), which is 5 + 1 + 5 + 1 = 12 characters.

---

### Question 3
Which of the following is a valid text block?

A) `String s = """Hello""";`  
B) `String s = """Hello World""";`  
C) `String s = """\nHello\n""";`  
D) `String s = """`  
`Hello`  
`""";`  

**Answer:** D

**Explanation:**
Text blocks require a line terminator after the opening delimiter `"""`. Options A and B don't have line terminators. Option C has content on the same line as the opening delimiter. Only option D is valid.

---

### Question 4
What does the backslash at the end of a line do in a text block?

```java
String text = """
    Line 1 \
    Line 2
    """;
```

A) Creates a tab  
B) Escapes the newline  
C) Adds a backslash to the string  
D) Causes a compilation error  

**Answer:** B

**Explanation:**
The backslash (`\`) at the end of a line in a text block escapes the newline character, allowing the text to continue on the next line without including a newline in the resulting string.

---

### Question 5
What is the result of this code?

```java
String text = """
        Hello
        World
    """;
System.out.println(text);
```

A) `Hello\nWorld\n`  
B) `    Hello\n    World\n`  
C) `        Hello\n        World\n`  
D) Compilation error  

**Answer:** B

**Explanation:**
The closing delimiter is indented 4 spaces. This determines the incidental whitespace that gets removed. The content lines are indented 8 spaces, so 4 spaces are removed from each, leaving 4 spaces of indentation on each line.

---

### Question 6
Which method is used to format text blocks with variables?

A) `format()`  
B) `formatted()`  
C) `interpolate()`  
D) `substitute()`  

**Answer:** B

**Explanation:**
The `formatted()` method (introduced in Java 15) is used to format text blocks with variables. For example: `"""Hello %s""".formatted(name)`.

---

### Question 7
What is the output?

```java
String text = """
    Line 1   
    Line 2   
    """;
System.out.println(text.equals("Line 1\nLine 2\n"));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Trailing whitespace is automatically removed from each line in a text block (unless escaped with `\s`). So "Line 1   " becomes "Line 1". The resulting string is "Line 1\nLine 2\n".

---

### Question 8
How do you preserve trailing whitespace in a text block?

A) Use double backslash `\\`  
B) Use `\t`  
C) Use `\s`  
D) It's preserved automatically  

**Answer:** C

**Explanation:**
To preserve trailing whitespace in a text block, use the `\s` escape sequence at the end of the line. Without it, trailing spaces are automatically removed.

---

### Question 9
What is the main advantage of text blocks over traditional strings?

A) Better performance  
B) Smaller memory footprint  
C) Improved readability for multi-line strings  
D) Automatic null checking  

**Answer:** C

**Explanation:**
The primary advantage of text blocks is improved readability when working with multi-line strings, especially for HTML, JSON, SQL, etc. Performance and memory usage are similar to traditional strings.

---

### Question 10
What is the output?

```java
String json = """
    {
      "name": "%s"
    }
    """.formatted("Alice");
System.out.println(json.contains("Alice"));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
The `formatted()` method replaces `%s` with "Alice", so the resulting string contains `"name": "Alice"`. The `contains()` method returns true.

---

### Question 11
Which statement is TRUE about text blocks?

A) They are mutable  
B) They are a different type from String  
C) They are immutable like regular strings  
D) They don't support escape sequences  

**Answer:** C

**Explanation:**
Text blocks are just a syntactic feature for creating String objects. They are immutable and behave exactly like regular strings. They fully support escape sequences.

---

### Question 12
What happens with this code?

```java
String text = """Line 1
    Line 2
    """;
```

A) Compiles successfully  
B) Compilation error - no line terminator after opening delimiter  
C) Runtime exception  
D) Creates an empty string  

**Answer:** B

**Explanation:**
Text blocks require a line terminator (newline) immediately after the opening `"""` delimiter. Having "Line 1" on the same line causes a compilation error.

---

### Question 13
What is the output?

```java
String text = """
    """;
System.out.println(text.length());
```

A) 0  
B) 1  
C) 3  
D) Compilation error  

**Answer:** B

**Explanation:**
An empty text block (with just a newline between delimiters) results in a string containing a single newline character, so the length is 1.

---

### Question 14
Which of the following is the correct way to create a text block for JSON?

A) `String json = """{"name":"Alice"}""";`  
B) `String json = """`  
`{"name":"Alice"}`  
`""";`  
C) `String json = """  
`{"name":"Alice"}  
`""";`  
D) B and C are both correct  

**Answer:** D

**Explanation:**
Both B and C are valid text block syntax. The opening delimiter must be followed by a line terminator, and the content can be on subsequent lines. Both formats achieve this.

---

### Question 15
What is the result?

```java
String html = """
    <html>
      <body>
      </body>
    </html>
""";
System.out.println(html.startsWith("<html>"));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
The closing delimiter is at column 0, so all incidental indentation is removed. The resulting string starts with "<html>", so `startsWith("<html>")` returns true.

---

### Question 16
What does the `stripIndent()` method do?

A) Removes all whitespace  
B) Removes incidental indentation  
C) Removes trailing whitespace  
D) Removes escape sequences  

**Answer:** B

**Explanation:**
The `stripIndent()` method removes incidental (common leading) whitespace from each line of a text block, similar to the automatic processing that text blocks perform.

---

### Question 17
What is the output?

```java
String text = """
    Hello\tWorld
    """;
System.out.println(text.contains("\t"));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Escape sequences like `\t` work in text blocks just as they do in regular strings. The tab character is included in the string, so `contains("\t")` returns true.

---

### Question 18
Which scenario is text blocks LEAST suitable for?

A) Multi-line SQL queries  
B) HTML templates  
C) Short single-line messages  
D) JSON strings  

**Answer:** C

**Explanation:**
Text blocks are designed for multi-line strings and provide the most benefit there. For short single-line strings, traditional string literals are simpler and more appropriate.

---

### Question 19
What is the output?

```java
String code = """
    public void method() {
        int x = 10;
    }
    """;
System.out.println(code.lines().count());
```

A) 1  
B) 3  
C) 4  
D) 5  

**Answer:** C

**Explanation:**
The `lines()` method returns a stream of lines. The text block contains 4 lines (including the final newline creates an empty 4th line): "public void method() {", "    int x = 10;", "}", and a final empty line.

---

### Question 20
Can text blocks be used with the `+` concatenation operator?

A) No, compilation error  
B) Yes, they work like regular strings  
C) Only with other text blocks  
D) Only if they're on separate lines  

**Answer:** B

**Explanation:**
Text blocks are String objects and can be used with the `+` operator just like regular strings. For example: `String s = """Hello""" + " " + """World""";` is valid.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered text blocks.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Missing line terminator** after opening delimiter
2. **Putting content** on same line as opening delimiter
3. **Forgetting** that text blocks are just Strings
4. **Not understanding** incidental whitespace removal
5. **Assuming** trailing whitespace is preserved (it's not, unless using \s)
6. **Overusing** text blocks for simple single-line strings
7. **Not using** formatted() for string interpolation

---

## ✅ Module 2 Complete!

Congratulations! You've completed Module 2 covering:
- ✅ String class and its methods
- ✅ StringBuilder for efficient string manipulation
- ✅ StringBuffer vs StringBuilder
- ✅ Text blocks (Java 15+)
- ✅ String pool and immutability
- ✅ String interpolation with formatted()

**Next Module:** [Module 3: Date-Time API](../module-03/05-datetime-api.md)

---

**Good luck!** ☕
