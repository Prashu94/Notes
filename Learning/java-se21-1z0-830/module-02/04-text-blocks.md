# Module 2.2: Text Blocks (Java 15+)

## 📚 Table of Contents
1. [Overview](#overview)
2. [Basic Syntax](#basic-syntax)
3. [Indentation Management](#indentation-management)
4. [Escape Sequences](#escape-sequences)
5. [String Interpolation](#string-interpolation)
6. [Comparison with Traditional Strings](#comparison-with-traditional-strings)
7. [Best Practices](#best-practices)

---

## Overview

**Text blocks** (introduced in Java 15 as a standard feature, preview in Java 13-14) provide a cleaner way to write multi-line strings. They are particularly useful for:
- HTML, JSON, SQL
- Multi-line text
- Embedded code snippets
- Any text with significant formatting

---

## Basic Syntax

### Traditional Multi-Line Strings (Before Java 15)

```java
// Messy and hard to read
String html = "<html>\n" +
              "  <body>\n" +
              "    <h1>Hello</h1>\n" +
              "  </body>\n" +
              "</html>";

String json = "{\n" +
              "  \"name\": \"Alice\",\n" +
              "  \"age\": 25\n" +
              "}";

String sql = "SELECT id, name, email\n" +
             "FROM users\n" +
             "WHERE status = 'active'\n" +
             "ORDER BY name";
```

### Text Blocks (Java 15+)

```java
// Clean and readable
String html = """
    <html>
      <body>
        <h1>Hello</h1>
      </body>
    </html>
    """;

String json = """
    {
      "name": "Alice",
      "age": 25
    }
    """;

String sql = """
    SELECT id, name, email
    FROM users
    WHERE status = 'active'
    ORDER BY name
    """;
```

### Syntax Rules

1. **Opening delimiter**: Three double quotes `"""`
2. **Line terminator required** after opening delimiter
3. **Content**: Multi-line text
4. **Closing delimiter**: Three double quotes `"""`

```java
// ✅ Correct - line terminator after opening delimiter
String text = """
    Hello World
    """;

// ❌ Wrong - no line terminator
String text = """Hello World""";  // Compilation error

// ❌ Wrong - content on same line as opening delimiter
String text = """Hello
    World
    """;  // Compilation error
```

---

## Indentation Management

Text blocks automatically manage indentation using **incidental whitespace** removal.

### Incidental Whitespace

The **common leading whitespace** is automatically removed:

```java
String text = """
        Line 1
        Line 2
        Line 3
        """;
        
// Result (all lines aligned to leftmost content):
// "Line 1\nLine 2\nLine 3\n"
```

### Determining Incidental Whitespace

The indentation is determined by:
1. The **closing delimiter** position
2. The **leftmost** non-blank line

```java
// Example 1: Closing delimiter determines indentation
String html = """
        <html>
            <body>
            </body>
        </html>
    """;  // Indented 4 spaces from closing delimiter

// Result preserves relative indentation:
// "    <html>\n        <body>\n        </body>\n    </html>\n"

// Example 2: Leftmost line determines indentation
String text = """
    Line 1
        Line 2
    Line 3
    """;

// Result:
// "Line 1\n    Line 2\nLine 3\n"
```

### Controlling Indentation

```java
// Remove all leading whitespace
String text = """
Line 1
Line 2
""";  // Closing delimiter at column 0

// Result: "Line 1\nLine 2\n"

// Preserve specific indentation
String code = """
    public void method() {
        int x = 10;
        System.out.println(x);
    }
    """;

// Result preserves relative indentation
```

### indent() Method

```java
String text = """
    Line 1
    Line 2
    """;

// Add 4 spaces to each line
String indented = text.indent(4);
// "        Line 1\n        Line 2\n"

// Remove 2 spaces from each line
String dedented = text.indent(-2);
// "  Line 1\n  Line 2\n"
```

---

## Escape Sequences

### Automatic Handling

Text blocks recognize escape sequences:

```java
String text = """
    Line 1\tTabbed
    Line 2\nExtra newline
    Quote: \"Hello\"
    """;

// \t becomes tab
// \n becomes newline (additional to inherent newlines)
// \" becomes "
```

### Line Terminator Escape (\)

Use backslash at end of line to continue on next line:

```java
// Without escape - includes newline
String long1 = """
    This is a very
    long line
    """;
// Result: "This is a very\nlong line\n"

// With escape - no newline
String long2 = """
    This is a very \
    long line
    """;
// Result: "This is a very long line\n"
```

### Whitespace Escape (\s)

Preserve trailing whitespace:

```java
// Trailing spaces are normally removed
String text1 = """
    Line 1   
    Line 2   
    """;
// Result: "Line 1\nLine 2\n" (spaces removed)

// Use \s to preserve trailing space
String text2 = """
    Line 1   \s
    Line 2   \s
    """;
// Result: "Line 1    \nLine 2    \n" (spaces preserved)
```

---

## String Interpolation

Text blocks don't have built-in interpolation, but you can use:

### String.format()

```java
String name = "Alice";
int age = 25;

String message = """
    Hello, %s!
    You are %d years old.
    """.formatted(name, age);

// Or using String.format()
String message2 = String.format("""
    Hello, %s!
    You are %d years old.
    """, name, age);
```

### formatted() Method (Java 15+)

```java
String template = """
    {
      "name": "%s",
      "age": %d,
      "active": %b
    }
    """.formatted("Alice", 25, true);

// Result:
// {
//   "name": "Alice",
//   "age": 25,
//   "active": true
// }
```

### Concatenation

```java
String name = "Alice";

String greeting = """
    Hello, """ + name + """
    !
    Welcome to Java 21.
    """;
```

---

## Comparison with Traditional Strings

### HTML Example

```java
// Traditional (hard to read)
String html = "<html>\n" +
              "  <body>\n" +
              "    <p>Hello " + name + "</p>\n" +
              "  </body>\n" +
              "</html>";

// Text Block (clean)
String html = """
    <html>
      <body>
        <p>Hello %s</p>
      </body>
    </html>
    """.formatted(name);
```

### JSON Example

```java
// Traditional
String json = "{\n" +
              "  \"name\": \"" + name + "\",\n" +
              "  \"age\": " + age + ",\n" +
              "  \"email\": \"" + email + "\"\n" +
              "}";

// Text Block
String json = """
    {
      "name": "%s",
      "age": %d,
      "email": "%s"
    }
    """.formatted(name, age, email);
```

### SQL Example

```java
// Traditional
String sql = "SELECT u.id, u.name, u.email\n" +
             "FROM users u\n" +
             "WHERE u.status = '" + status + "'\n" +
             "  AND u.created_date > '" + date + "'\n" +
             "ORDER BY u.name";

// Text Block
String sql = """
    SELECT u.id, u.name, u.email
    FROM users u
    WHERE u.status = '%s'
      AND u.created_date > '%s'
    ORDER BY u.name
    """.formatted(status, date);
```

---

## Best Practices

### ✅ DO:

1. **Use text blocks for multi-line strings**
   ```java
   String html = """
       <!DOCTYPE html>
       <html>
         <body>Hello</body>
       </html>
       """;
   ```

2. **Use formatted() for interpolation**
   ```java
   String json = """
       {
         "name": "%s",
         "value": %d
       }
       """.formatted(name, value);
   ```

3. **Position closing delimiter to control indentation**
   ```java
   // No indentation
   String text = """
   Line 1
   Line 2
   """;
   
   // With indentation
   String text = """
       Line 1
       Line 2
       """;
   ```

4. **Use line continuation for long lines**
   ```java
   String text = """
       This is a very long line that \
       continues here
       """;
   ```

### ❌ DON'T:

1. **Don't put content on opening delimiter line**
   ```java
   // Wrong
   String text = """Content
       More content
       """;
   ```

2. **Don't forget the line terminator**
   ```java
   // Wrong
   String text = """Hello World""";
   ```

3. **Don't use for short strings**
   ```java
   // Overkill
   String simple = """
       Hello
       """;
   
   // Better
   String simple = "Hello";
   ```

---

## Common Use Cases

### 1. HTML Templates

```java
String page = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>%s</title>
    </head>
    <body>
        <h1>%s</h1>
        <p>%s</p>
    </body>
    </html>
    """.formatted(title, heading, content);
```

### 2. JSON Generation

```java
String userJson = """
    {
      "id": %d,
      "username": "%s",
      "email": "%s",
      "roles": ["user", "admin"],
      "active": %b
    }
    """.formatted(id, username, email, active);
```

### 3. SQL Queries

```java
String query = """
    SELECT 
        u.id,
        u.name,
        u.email,
        COUNT(o.id) as order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.status = 'active'
    GROUP BY u.id, u.name, u.email
    HAVING COUNT(o.id) > %d
    ORDER BY order_count DESC
    """.formatted(minOrders);
```

### 4. Regular Expressions

```java
String emailPattern = """
    ^[a-zA-Z0-9._%+-]+\
    @[a-zA-Z0-9.-]+\
    \\.[a-zA-Z]{2,}$\
    """;
```

### 5. Error Messages

```java
String errorMsg = """
    ============================================
    ERROR: Failed to process request
    ============================================
    
    Time: %s
    User: %s
    Action: %s
    
    Details:
    %s
    
    Please contact support if this persists.
    ============================================
    """.formatted(timestamp, username, action, details);
```

---

## Advanced Features

### stripIndent() Method

```java
String text = """
        Line 1
            Line 2
        Line 3
        """.stripIndent();

// Removes incidental indentation
// "Line 1\n    Line 2\nLine 3\n"
```

### translateEscapes() Method

```java
String text = """
    Line 1\\tTabbed
    Line 2\\nNewline
    """.translateEscapes();

// Converts escape sequences
// "Line 1\tTabbed\nLine 2\nNewline\n"
```

---

## Summary

- **Text blocks** (`"""..."""`) provide cleaner multi-line string syntax
- Introduced as standard in **Java 15** (preview in 13-14)
- **Automatic indentation** management based on content alignment
- **Escape sequences** work as in regular strings
- **Line continuation** with `\` at end of line
- **Trailing whitespace** preserved with `\s`
- Use **formatted()** for string interpolation
- Best for HTML, JSON, SQL, and formatted text
- **More readable** than traditional string concatenation

---

## Next Steps

Proceed to [Practice Questions](04-practice-questions.md) to test your understanding of text blocks!
