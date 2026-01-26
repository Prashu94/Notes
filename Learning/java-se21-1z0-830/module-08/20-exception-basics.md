# Module 8: Exception Handling - Exception Basics

## Table of Contents
1. [Introduction to Exceptions](#introduction-to-exceptions)
2. [Exception Hierarchy](#exception-hierarchy)
3. [Types of Exceptions](#types-of-exceptions)
4. [try-catch-finally](#try-catch-finally)
5. [Multiple catch Blocks](#multiple-catch-blocks)
6. [Exception Propagation](#exception-propagation)
7. [Best Practices](#best-practices)

## Introduction to Exceptions

An **exception** is an event that disrupts the normal flow of program execution. Java's exception handling mechanism provides a way to transfer control from one part of a program to another when exceptional conditions occur.

### Why Exception Handling?

```java
// Without exception handling
public int divide(int a, int b) {
    return a / b;  // What if b is 0?
}

// With exception handling
public int divide(int a, int b) {
    try {
        return a / b;
    } catch (ArithmeticException e) {
        System.out.println("Cannot divide by zero");
        return 0;
    }
}
```

### Benefits
- Separates error-handling code from regular code
- Propagates errors up the call stack
- Groups and differentiates error types
- Provides meaningful error information

## Exception Hierarchy

All exceptions in Java inherit from `Throwable`:

```
java.lang.Object
    └── java.lang.Throwable
            ├── java.lang.Error
            │       ├── OutOfMemoryError
            │       ├── StackOverflowError
            │       └── VirtualMachineError
            └── java.lang.Exception
                    ├── IOException
                    ├── SQLException
                    ├── ClassNotFoundException
                    └── java.lang.RuntimeException
                            ├── NullPointerException
                            ├── IndexOutOfBoundsException
                            ├── ArithmeticException
                            ├── IllegalArgumentException
                            └── NumberFormatException
```

### Throwable Class

```java
public class Throwable {
    public String getMessage()        // Returns detail message
    public String getLocalizedMessage()  // Returns localized description
    public Throwable getCause()       // Returns the cause
    public void printStackTrace()     // Prints stack trace
    public StackTraceElement[] getStackTrace()  // Gets stack trace
}
```

### Key Methods Example

```java
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("Message: " + e.getMessage());
    System.out.println("Cause: " + e.getCause());
    e.printStackTrace();
    
    for (StackTraceElement element : e.getStackTrace()) {
        System.out.println(element.getClassName() + "." + 
                         element.getMethodName() + 
                         ":" + element.getLineNumber());
    }
}
```

## Types of Exceptions

### 1. Checked Exceptions

**Checked exceptions** must be declared in the method signature or handled with try-catch. They represent **recoverable conditions** that a well-written application should anticipate.

```java
// Must be declared or caught
public void readFile(String path) throws IOException {
    FileReader reader = new FileReader(path);  // Throws IOException
}

// Or caught
public void readFile(String path) {
    try {
        FileReader reader = new FileReader(path);
    } catch (IOException e) {
        System.out.println("File not found: " + path);
    }
}
```

Common checked exceptions:
- `IOException` - I/O operation failure
- `SQLException` - Database access error
- `ClassNotFoundException` - Class cannot be located
- `InterruptedException` - Thread interrupted
- `FileNotFoundException` - File not found

### 2. Unchecked Exceptions (Runtime Exceptions)

**Runtime exceptions** do NOT need to be declared or caught. They represent **programming errors** that could be prevented.

```java
// No need to declare or catch
public int getElement(int[] array, int index) {
    return array[index];  // May throw ArrayIndexOutOfBoundsException
}

// But you CAN catch them if needed
public int getElement(int[] array, int index) {
    try {
        return array[index];
    } catch (ArrayIndexOutOfBoundsException e) {
        System.out.println("Invalid index");
        return -1;
    }
}
```

Common runtime exceptions:
- `NullPointerException` - Null reference access
- `ArrayIndexOutOfBoundsException` - Array index out of range
- `ClassCastException` - Invalid type cast
- `IllegalArgumentException` - Illegal method argument
- `NumberFormatException` - String to number conversion fails
- `ArithmeticException` - Arithmetic error (e.g., divide by zero)

### 3. Errors

**Errors** represent serious problems that applications should NOT try to catch. They indicate conditions external to the application.

```java
// DON'T catch Errors unless you know what you're doing
public class ErrorExample {
    public static void main(String[] args) {
        try {
            causeStackOverflow();
        } catch (StackOverflowError e) {  // Generally not recommended
            System.out.println("Stack overflow occurred");
        }
    }
    
    public static void causeStackOverflow() {
        causeStackOverflow();  // Infinite recursion
    }
}
```

Common errors:
- `OutOfMemoryError` - JVM runs out of memory
- `StackOverflowError` - Stack overflow (too deep recursion)
- `NoClassDefFoundError` - Class definition not found at runtime

## try-catch-finally

### Basic Syntax

```java
try {
    // Code that may throw an exception
} catch (ExceptionType e) {
    // Handle the exception
} finally {
    // Always executed (optional)
}
```

### try Block

The `try` block contains code that might throw an exception:

```java
try {
    int result = 10 / 0;  // Throws ArithmeticException
    System.out.println("This won't be printed");
}
```

### catch Block

The `catch` block handles the exception:

```java
try {
    int[] array = {1, 2, 3};
    System.out.println(array[5]);
} catch (ArrayIndexOutOfBoundsException e) {
    System.out.println("Index out of bounds: " + e.getMessage());
}
```

### finally Block

The `finally` block **always executes**, whether an exception occurs or not:

```java
FileReader reader = null;
try {
    reader = new FileReader("file.txt");
    // Read file
} catch (IOException e) {
    System.out.println("Error reading file");
} finally {
    // Always executed - cleanup code
    if (reader != null) {
        try {
            reader.close();
        } catch (IOException e) {
            System.out.println("Error closing file");
        }
    }
}
```

### When finally DOES Execute

```java
public class FinallyExample {
    public static void main(String[] args) {
        System.out.println(test());  // Prints: Finally / 1
    }
    
    public static int test() {
        try {
            return 1;
        } finally {
            System.out.println("Finally");
            // return 2;  // This would override the try's return value
        }
    }
}
```

### When finally DOESN'T Execute

```java
// Only these cases prevent finally from executing:
// 1. JVM exits
System.exit(0);

// 2. Thread is killed
Thread.currentThread().stop();

// 3. Infinite loop in try
while(true) { }

// 4. System crash
```

## Multiple catch Blocks

You can have multiple `catch` blocks to handle different exceptions differently:

### Order Matters

```java
try {
    // Code
} catch (FileNotFoundException e) {  // More specific first
    System.out.println("File not found");
} catch (IOException e) {  // Less specific after
    System.out.println("I/O error");
} catch (Exception e) {  // Most general last
    System.out.println("Generic error");
}

// INVALID - won't compile
try {
    // Code
} catch (Exception e) {  // Too general
    System.out.println("Generic error");
} catch (IOException e) {  // Unreachable - compile error
    System.out.println("I/O error");
}
```

### Multi-catch (Java 7+)

Handle multiple exception types in one catch block:

```java
try {
    // Code that may throw different exceptions
    int result = Integer.parseInt(args[0]);
    int[] array = new int[result];
} catch (NumberFormatException | NegativeArraySizeException e) {
    // e is effectively final
    System.out.println("Invalid input: " + e.getMessage());
}
```

**Rules for multi-catch:**
- Exception types must NOT be subclasses of each other
- The caught exception is implicitly `final`
- Cannot assign different exception to the variable

```java
// INVALID - IllegalArgumentException is parent of NumberFormatException
try {
    // Code
} catch (IllegalArgumentException | NumberFormatException e) {  // Compile error
}

// VALID - unrelated exception types
try {
    // Code
} catch (IOException | SQLException e) {
}
```

## Exception Propagation

When a method throws an exception and doesn't catch it, the exception propagates up the call stack:

### Example

```java
public class PropagationExample {
    public static void main(String[] args) {
        try {
            method1();
        } catch (ArithmeticException e) {
            System.out.println("Caught in main: " + e.getMessage());
        }
    }
    
    public static void method1() {
        method2();
    }
    
    public static void method2() {
        method3();
    }
    
    public static void method3() {
        int result = 10 / 0;  // Exception occurs here
        // Exception propagates: method3 -> method2 -> method1 -> main
    }
}
```

### Stack Trace

```
Exception in thread "main" java.lang.ArithmeticException: / by zero
    at PropagationExample.method3(PropagationExample.java:16)
    at PropagationExample.method2(PropagationExample.java:12)
    at PropagationExample.method1(PropagationExample.java:8)
    at PropagationExample.main(PropagationExample.java:4)
```

### throws Keyword

For checked exceptions, methods must declare them with `throws`:

```java
// Declares that method may throw IOException
public void readFile(String path) throws IOException {
    FileReader reader = new FileReader(path);
}

// Caller must handle or declare
public void processFile() {
    try {
        readFile("data.txt");
    } catch (IOException e) {
        System.out.println("Error: " + e.getMessage());
    }
}

// Or propagate further
public void processFile() throws IOException {
    readFile("data.txt");
}
```

### Multiple throws

```java
public void complexOperation() throws IOException, SQLException {
    // Method that may throw multiple checked exceptions
}

// Handling
public void caller() {
    try {
        complexOperation();
    } catch (IOException e) {
        // Handle I/O exception
    } catch (SQLException e) {
        // Handle SQL exception
    }
}
```

## Best Practices

### 1. Catch Specific Exceptions

```java
// BAD
try {
    // Code
} catch (Exception e) {  // Too broad
}

// GOOD
try {
    // Code
} catch (IOException e) {
    // Handle I/O exception specifically
} catch (SQLException e) {
    // Handle SQL exception specifically
}
```

### 2. Don't Swallow Exceptions

```java
// BAD
try {
    // Code
} catch (Exception e) {
    // Silent failure - debugging nightmare
}

// GOOD
try {
    // Code
} catch (Exception e) {
    logger.error("Error occurred", e);
    // Or rethrow, or handle appropriately
}
```

### 3. Use finally for Cleanup

```java
Connection conn = null;
try {
    conn = getConnection();
    // Use connection
} catch (SQLException e) {
    // Handle exception
} finally {
    if (conn != null) {
        try {
            conn.close();
        } catch (SQLException e) {
            logger.error("Failed to close connection", e);
        }
    }
}
```

### 4. Don't Use Exceptions for Control Flow

```java
// BAD
try {
    int i = 0;
    while (true) {
        array[i++] = 0;
    }
} catch (ArrayIndexOutOfBoundsException e) {
    // Using exception to exit loop
}

// GOOD
for (int i = 0; i < array.length; i++) {
    array[i] = 0;
}
```

### 5. Include Meaningful Error Messages

```java
// BAD
throw new IllegalArgumentException();

// GOOD
throw new IllegalArgumentException(
    "Age must be between 0 and 150, got: " + age
);
```

### 6. Document Exceptions

```java
/**
 * Reads user data from file.
 * 
 * @param path the file path
 * @return User object
 * @throws IOException if file cannot be read
 * @throws IllegalArgumentException if path is null
 */
public User readUser(String path) throws IOException {
    if (path == null) {
        throw new IllegalArgumentException("Path cannot be null");
    }
    // Read file
}
```

## Summary

- **Exceptions** disrupt normal program flow and must be handled
- **Checked exceptions** must be declared or caught (e.g., IOException)
- **Unchecked exceptions** (RuntimeException) don't need declaration (e.g., NullPointerException)
- **Errors** represent serious problems and shouldn't be caught (e.g., OutOfMemoryError)
- **try-catch-finally**: try contains risky code, catch handles exceptions, finally always executes
- **Multiple catch blocks** must be ordered from most specific to most general
- **Multi-catch** (Java 7+) handles multiple unrelated exceptions in one block
- **Exception propagation**: uncaught exceptions propagate up the call stack
- **throws** declares checked exceptions in method signatures
- **Best practices**: catch specific exceptions, don't swallow exceptions, use finally for cleanup, include meaningful messages

## Key Takeaways

1. All exceptions inherit from `Throwable`
2. Checked exceptions force compile-time handling
3. Runtime exceptions indicate programming errors
4. finally always executes (except JVM exit, thread kill, etc.)
5. catch blocks must be ordered from specific to general
6. Multi-catch uses | to handle multiple exceptions
7. Uncaught exceptions propagate up the call stack
8. throws declares exceptions in method signatures
9. Never use exceptions for control flow
10. Always include meaningful error messages
