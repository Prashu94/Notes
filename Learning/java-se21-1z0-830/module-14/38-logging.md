# Module 14: Logging and Annotations

## Table of Contents
1. [Introduction to Logging](#introduction-to-logging)
2. [java.util.logging Package](#javautillogging-package)
3. [Logger Class](#logger-class)
4. [Log Levels](#log-levels)
5. [Handlers](#handlers)
6. [Formatters](#formatters)
7. [Logging Configuration](#logging-configuration)
8. [Annotations Overview](#annotations-overview)
9. [Built-in Annotations](#built-in-annotations)
10. [Meta-Annotations](#meta-annotations)
11. [Custom Annotations](#custom-annotations)
12. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to Logging

**Logging** records application events for debugging, monitoring, and auditing.

### Why Logging?

```
Benefits:
- Track application behavior
- Debug production issues
- Monitor performance
- Audit trail
- Better than System.out.println()
```

---

## java.util.logging Package

**java.util.logging** is Java's built-in logging framework.

### Key Components

```
Logger: Creates log records
Handler: Publishes log records (console, file, etc.)
Formatter: Formats log records
Level: Severity of log message
```

---

## Logger Class

**Logger** is the main logging class.

### Creating Logger

```java
import java.util.logging.*;

public class LoggingExample {
    // Get logger for class
    private static final Logger logger = Logger.getLogger(LoggingExample.class.getName());
    
    public static void main(String[] args) {
        logger.info("Application started");
        logger.warning("This is a warning");
        logger.severe("This is an error");
    }
}
```

### Logger Hierarchy

```java
// Root logger
Logger rootLogger = Logger.getLogger("");

// Package logger
Logger pkgLogger = Logger.getLogger("com.example");

// Class logger
Logger classLogger = Logger.getLogger("com.example.MyClass");

// Hierarchy: root → com → com.example → com.example.MyClass
```

### Logging Methods

```java
Logger logger = Logger.getLogger("MyLogger");

// Log at specific levels
logger.severe("Severe message");     // SEVERE
logger.warning("Warning message");   // WARNING
logger.info("Info message");         // INFO
logger.config("Config message");     // CONFIG
logger.fine("Fine message");         // FINE
logger.finer("Finer message");       // FINER
logger.finest("Finest message");     // FINEST

// Generic log method
logger.log(Level.INFO, "Info message");

// Log with exception
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    logger.log(Level.SEVERE, "Division error", e);
}

// Log with parameters
logger.log(Level.INFO, "User {0} logged in from {1}", 
    new Object[]{"Alice", "192.168.1.1"});
```

---

## Log Levels

**Levels** indicate severity of log messages.

### Level Hierarchy

```
SEVERE   (highest)  - Serious failures
WARNING            - Potential problems
INFO               - Informational messages
CONFIG             - Configuration messages
FINE               - Tracing information
FINER              - Detailed tracing
FINEST   (lowest)  - Very detailed tracing
```

### Setting Log Level

```java
Logger logger = Logger.getLogger("MyLogger");

// Set level
logger.setLevel(Level.WARNING);  // Only WARNING and SEVERE logged

// Logging
logger.finest("Not logged");  // Below WARNING
logger.fine("Not logged");    // Below WARNING
logger.info("Not logged");    // Below WARNING
logger.warning("Logged");     // WARNING level
logger.severe("Logged");      // SEVERE level

// Disable logging
logger.setLevel(Level.OFF);

// Enable all logging
logger.setLevel(Level.ALL);
```

### Level Comparison

```java
Level level1 = Level.INFO;
Level level2 = Level.WARNING;

// Compare levels
if (level1.intValue() < level2.intValue()) {
    System.out.println("INFO is less severe than WARNING");
}
```

---

## Handlers

**Handlers** publish log records to destinations.

### ConsoleHandler

```java
import java.util.logging.*;

Logger logger = Logger.getLogger("MyLogger");

// Create console handler
ConsoleHandler consoleHandler = new ConsoleHandler();
consoleHandler.setLevel(Level.ALL);

// Add handler to logger
logger.addHandler(consoleHandler);
logger.setLevel(Level.ALL);

// Log messages
logger.finest("Finest message");  // Now visible
logger.info("Info message");
```

### FileHandler

```java
try {
    Logger logger = Logger.getLogger("MyLogger");
    
    // Create file handler (appends to file)
    FileHandler fileHandler = new FileHandler("app.log", true);
    fileHandler.setLevel(Level.ALL);
    
    // Add handler
    logger.addHandler(fileHandler);
    logger.setLevel(Level.ALL);
    
    // Log to file
    logger.info("This goes to file");
    logger.warning("This also goes to file");
    
} catch (IOException e) {
    e.printStackTrace();
}
```

### FileHandler Patterns

```java
// Pattern options:
// %h - user home directory
// %t - system temp directory
// %g - generation number
// %u - unique number to avoid conflicts

// Single file
FileHandler fh1 = new FileHandler("app.log");

// User home directory
FileHandler fh2 = new FileHandler("%h/app.log");

// Rotating files (1MB limit, 5 files)
FileHandler fh3 = new FileHandler("app%g.log", 1024 * 1024, 5);

// Temp directory with unique number
FileHandler fh4 = new FileHandler("%t/app%u.log");
```

### Multiple Handlers

```java
Logger logger = Logger.getLogger("MyLogger");

// Console handler (INFO and above)
ConsoleHandler consoleHandler = new ConsoleHandler();
consoleHandler.setLevel(Level.INFO);

// File handler (ALL levels)
FileHandler fileHandler = new FileHandler("app.log");
fileHandler.setLevel(Level.ALL);

// Add both handlers
logger.addHandler(consoleHandler);
logger.addHandler(fileHandler);
logger.setLevel(Level.ALL);

// Message goes to both console and file
logger.info("Info message");

// Message goes only to file (below INFO)
logger.fine("Fine message");
```

### Removing Handlers

```java
Logger logger = Logger.getLogger("MyLogger");

// Get all handlers
Handler[] handlers = logger.getHandlers();

// Remove all handlers
for (Handler handler : handlers) {
    logger.removeHandler(handler);
}
```

---

## Formatters

**Formatters** format log records for output.

### SimpleFormatter

```java
ConsoleHandler handler = new ConsoleHandler();
handler.setFormatter(new SimpleFormatter());

Logger logger = Logger.getLogger("MyLogger");
logger.addHandler(handler);

logger.info("Test message");

// Output:
// Jan 15, 2024 2:30:45 PM MyClass main
// INFO: Test message
```

### XMLFormatter

```java
try {
    FileHandler fileHandler = new FileHandler("app.xml");
    fileHandler.setFormatter(new XMLFormatter());
    
    Logger logger = Logger.getLogger("MyLogger");
    logger.addHandler(fileHandler);
    
    logger.info("Test message");
    
    // Creates XML-formatted log file
} catch (IOException e) {
    e.printStackTrace();
}

// app.xml content:
// <?xml version="1.0" encoding="UTF-8" standalone="no"?>
// <log>
//   <record>
//     <date>2024-01-15T14:30:45</date>
//     <millis>1705328445000</millis>
//     <sequence>0</sequence>
//     <logger>MyLogger</logger>
//     <level>INFO</level>
//     <message>Test message</message>
//   </record>
// </log>
```

### Custom Formatter

```java
import java.util.logging.Formatter;
import java.util.logging.LogRecord;

class CustomFormatter extends Formatter {
    @Override
    public String format(LogRecord record) {
        return String.format("[%s] %s: %s%n",
            record.getLevel(),
            record.getLoggerName(),
            record.getMessage());
    }
}

// Usage
ConsoleHandler handler = new ConsoleHandler();
handler.setFormatter(new CustomFormatter());

Logger logger = Logger.getLogger("MyLogger");
logger.addHandler(handler);

logger.info("Test message");
// Output: [INFO] MyLogger: Test message
```

---

## Logging Configuration

### Configuration File

```properties
# logging.properties

# Root logger level
.level=INFO

# Console handler
handlers=java.util.logging.ConsoleHandler
java.util.logging.ConsoleHandler.level=ALL
java.util.logging.ConsoleHandler.formatter=java.util.logging.SimpleFormatter

# File handler
handlers=java.util.logging.FileHandler
java.util.logging.FileHandler.pattern=app.log
java.util.logging.FileHandler.level=ALL
java.util.logging.FileHandler.formatter=java.util.logging.XMLFormatter

# Specific logger
com.example.MyClass.level=FINE
```

### Loading Configuration

```java
try {
    // Load configuration file
    InputStream configFile = new FileInputStream("logging.properties");
    LogManager.getLogManager().readConfiguration(configFile);
    
    Logger logger = Logger.getLogger("MyLogger");
    logger.info("Logging configured");
    
} catch (IOException e) {
    e.printStackTrace();
}
```

### Programmatic Configuration

```java
Logger logger = Logger.getLogger("MyLogger");

// Disable parent handlers
logger.setUseParentHandlers(false);

// Create and configure handler
ConsoleHandler handler = new ConsoleHandler();
handler.setLevel(Level.ALL);
handler.setFormatter(new SimpleFormatter());

// Add handler and set level
logger.addHandler(handler);
logger.setLevel(Level.ALL);
```

---

## Annotations Overview

**Annotations** provide metadata about program elements.

### What are Annotations?

```java
@Override  // Annotation
public String toString() {
    return "Example";
}
```

### Uses of Annotations

```
- Compiler instructions (@Override, @Deprecated)
- Build-time processing (code generation)
- Runtime processing (reflection)
- Documentation (@param, @return in Javadoc)
```

---

## Built-in Annotations

### @Override

```java
class Parent {
    public void show() {
        System.out.println("Parent");
    }
}

class Child extends Parent {
    @Override  // Ensures method overrides parent method
    public void show() {
        System.out.println("Child");
    }
    
    @Override
    // public void shwo() {  // Compilation error - method doesn't override
    //     System.out.println("Typo");
    // }
}
```

### @Deprecated

```java
class OldAPI {
    @Deprecated  // Marks method as deprecated
    public void oldMethod() {
        System.out.println("Old method");
    }
    
    @Deprecated(since = "2.0", forRemoval = true)
    public void veryOldMethod() {
        System.out.println("Will be removed");
    }
}

// Usage
OldAPI api = new OldAPI();
api.oldMethod();  // Compiler warning: method is deprecated
```

### @SuppressWarnings

```java
class WarningExample {
    @SuppressWarnings("unchecked")  // Suppress unchecked warning
    public void method() {
        List list = new ArrayList();
        list.add("String");
    }
    
    @SuppressWarnings({"unchecked", "deprecation"})  // Multiple warnings
    public void multipleWarnings() {
        List list = new ArrayList();
        Date date = new Date(2024, 1, 15);  // Deprecated constructor
    }
}
```

### @SafeVarargs

```java
class VarargsExample {
    @SafeVarargs  // Suppresses varargs warnings
    public static <T> void printAll(T... elements) {
        for (T element : elements) {
            System.out.println(element);
        }
    }
    
    public static void main(String[] args) {
        printAll("A", "B", "C");
    }
}
```

### @FunctionalInterface

```java
@FunctionalInterface  // Ensures interface has exactly one abstract method
interface Calculator {
    int calculate(int a, int b);
    
    // int subtract(int a, int b);  // Compilation error - multiple abstract methods
}

// Usage
Calculator add = (a, b) -> a + b;
System.out.println(add.calculate(5, 3));  // 8
```

---

## Meta-Annotations

**Meta-annotations** annotate other annotations.

### @Retention

```java
import java.lang.annotation.*;

@Retention(RetentionPolicy.SOURCE)   // Discarded by compiler
@interface SourceAnnotation {}

@Retention(RetentionPolicy.CLASS)    // In .class file, not at runtime (default)
@interface ClassAnnotation {}

@Retention(RetentionPolicy.RUNTIME)  // Available at runtime via reflection
@interface RuntimeAnnotation {}
```

### @Target

```java
@Target(ElementType.TYPE)           // Class, interface, enum
@interface TypeAnnotation {}

@Target(ElementType.METHOD)         // Method
@interface MethodAnnotation {}

@Target(ElementType.FIELD)          // Field
@interface FieldAnnotation {}

@Target({ElementType.METHOD, ElementType.FIELD})  // Multiple targets
@interface MultiTargetAnnotation {}
```

### @Documented

```java
@Documented  // Include in Javadoc
@interface DocumentedAnnotation {
    String value();
}
```

### @Inherited

```java
@Inherited  // Subclasses inherit this annotation
@interface InheritedAnnotation {}

@InheritedAnnotation
class Parent {}

class Child extends Parent {}  // Child also has @InheritedAnnotation
```

---

## Custom Annotations

### Simple Annotation

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Test {
}

// Usage
class TestClass {
    @Test
    public void testMethod() {
        System.out.println("Test");
    }
}
```

### Annotation with Elements

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Author {
    String name();
    String date();
    int version() default 1;  // Default value
}

// Usage
class Example {
    @Author(name = "Alice", date = "2024-01-15")
    public void method1() {}
    
    @Author(name = "Bob", date = "2024-01-16", version = 2)
    public void method2() {}
}
```

### Processing Annotations at Runtime

```java
import java.lang.reflect.Method;

class AnnotationProcessor {
    public static void main(String[] args) throws Exception {
        Class<?> clazz = Example.class;
        
        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(Author.class)) {
                Author author = method.getAnnotation(Author.class);
                System.out.println("Method: " + method.getName());
                System.out.println("Author: " + author.name());
                System.out.println("Date: " + author.date());
                System.out.println("Version: " + author.version());
            }
        }
    }
}
```

---

## Summary and Exam Tips

### Logging Hierarchy

```
SEVERE    - 1000
WARNING   - 900
INFO      - 800
CONFIG    - 700
FINE      - 500
FINER     - 400
FINEST    - 300
```

### Handler Types

- **ConsoleHandler**: Logs to console
- **FileHandler**: Logs to file
- **StreamHandler**: Logs to OutputStream

### Formatter Types

- **SimpleFormatter**: Human-readable text
- **XMLFormatter**: XML format

### Built-in Annotations

- `@Override`: Method overrides parent
- `@Deprecated`: Marks as deprecated
- `@SuppressWarnings`: Suppresses compiler warnings
- `@SafeVarargs`: Suppresses varargs warnings
- `@FunctionalInterface`: Marks functional interface

### Meta-Annotations

- `@Retention`: When annotation is available (SOURCE, CLASS, RUNTIME)
- `@Target`: Where annotation can be applied
- `@Documented`: Include in Javadoc
- `@Inherited`: Subclasses inherit annotation

### Exam Tips

- Default log level: **INFO**
- Logger hierarchy: parent → child
- Handlers publish log records
- Formatters format log records
- Multiple handlers allowed per logger
- `@Override` prevents typos in method names
- `@FunctionalInterface` ensures exactly **one** abstract method
- `@Retention(RUNTIME)` required for reflection
- Annotation elements can have **default values**
- Custom annotation declared with `@interface`

---

**Previous:** [Practice Questions - Localization](37-practice-questions.md)  
**Next:** [Practice Questions - Logging and Annotations](38-practice-questions.md)
