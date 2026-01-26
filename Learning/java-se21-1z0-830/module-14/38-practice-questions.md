# Module 14: Practice Questions - Logging and Annotations

## Questions (20)

---

### Question 1
```java
Logger logger = Logger.getLogger("MyLogger");
logger.setLevel(Level.WARNING);
logger.info("Info message");
```
Is the message logged?

**A)** Yes  
**B)** No - INFO below WARNING  
**C)** Depends on handler  
**D)** Compilation error

**Answer: B)**

**Explanation:** Logger level is **WARNING**. **INFO** is below WARNING → **not logged**.

---

### Question 2
What are the log levels from highest to lowest severity?

**A)** SEVERE, ERROR, WARNING, INFO  
**B)** SEVERE, WARNING, INFO, FINE  
**C)** ERROR, WARNING, INFO, DEBUG  
**D)** CRITICAL, ERROR, WARNING, INFO

**Answer: B)**

**Explanation:** Levels: **SEVERE** (highest) → WARNING → INFO → CONFIG → FINE → FINER → FINEST (lowest).

---

### Question 3
```java
Logger logger = Logger.getLogger("MyLogger");
logger.severe("Error occurred");
```
What does `severe()` do?

**A)** Logs at INFO level  
**B)** Logs at SEVERE level  
**C)** Throws exception  
**D)** Logs at WARNING level

**Answer: B)**

**Explanation:** `severe()` logs at **SEVERE** level (highest severity).

---

### Question 4
```java
ConsoleHandler handler = new ConsoleHandler();
handler.setLevel(Level.ALL);
```
What does this do?

**A)** Disables console logging  
**B)** Logs all levels to console  
**C)** Sets logger level  
**D)** Creates log file

**Answer: B)**

**Explanation:** Sets handler to accept **all log levels** for console output.

---

### Question 5
```java
FileHandler fileHandler = new FileHandler("app.log");
```
What does FileHandler do?

**A)** Reads log file  
**B)** Writes log records to file  
**C)** Deletes log file  
**D)** Compresses log file

**Answer: B)**

**Explanation:** **FileHandler** publishes log records to a **file**.

---

### Question 6
```java
@Override
public String tostring() {  // typo: tostring instead of toString
    return "Example";
}
```
What happens?

**A)** Works fine  
**B)** Compilation error  
**C)** Runtime error  
**D)** Warning only

**Answer: B)**

**Explanation:** `@Override` ensures method **overrides** parent. Typo → **compilation error**.

---

### Question 7
```java
@Deprecated
public void oldMethod() {
}
```
What does @Deprecated do?

**A)** Removes method  
**B)** Marks method as deprecated  
**C)** Prevents compilation  
**D)** Throws exception

**Answer: B)**

**Explanation:** `@Deprecated` **marks** method as deprecated. Usage generates **compiler warning**.

---

### Question 8
```java
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
    int subtract(int a, int b);
}
```
What happens?

**A)** Works fine  
**B)** Compilation error  
**C)** Runtime error  
**D)** Warning only

**Answer: B)**

**Explanation:** `@FunctionalInterface` requires **exactly one** abstract method. Two methods → **compilation error**.

---

### Question 9
```java
@SuppressWarnings("unchecked")
public void method() {
    List list = new ArrayList();
}
```
What does @SuppressWarnings do?

**A)** Fixes warnings  
**B)** Suppresses compiler warnings  
**C)** Generates warnings  
**D)** Throws exception

**Answer: B)**

**Explanation:** `@SuppressWarnings` **suppresses** specified compiler warnings.

---

### Question 10
```java
@Retention(RetentionPolicy.RUNTIME)
@interface MyAnnotation {}
```
What does @Retention(RUNTIME) mean?

**A)** Discarded by compiler  
**B)** Available at runtime via reflection  
**C)** Only in source code  
**D)** Only in .class file

**Answer: B)**

**Explanation:** `RetentionPolicy.RUNTIME` makes annotation **available at runtime** for reflection.

---

### Question 11
```java
@Target(ElementType.METHOD)
@interface MethodAnnotation {}
```
What does @Target(METHOD) mean?

**A)** Annotation for classes only  
**B)** Annotation for methods only  
**C)** Annotation for fields only  
**D)** Annotation for all elements

**Answer: B)**

**Explanation:** `@Target(METHOD)` restricts annotation to **methods only**.

---

### Question 12
```java
Logger logger = Logger.getLogger("MyLogger");
logger.log(Level.INFO, "User {0} logged in", "Alice");
```
What is printed?

**A)** User {0} logged in  
**B)** User Alice logged in  
**C)** User 0 logged in  
**D)** Compilation error

**Answer: B)**

**Explanation:** `{0}` is replaced with parameter "Alice": **"User Alice logged in"**.

---

### Question 13
What's the default log level?

**A)** ALL  
**B)** INFO  
**C)** WARNING  
**D)** SEVERE

**Answer: B)**

**Explanation:** Default log level is **INFO** (logs INFO, WARNING, SEVERE).

---

### Question 14
```java
@interface Author {
    String name();
    String date();
    int version() default 1;
}
```
What's the default version?

**A)** 0  
**B)** 1  
**C)** null  
**D)** No default

**Answer: B)**

**Explanation:** `default 1` sets default value to **1**.

---

### Question 15
```java
ConsoleHandler handler = new ConsoleHandler();
handler.setFormatter(new XMLFormatter());
```
What does XMLFormatter do?

**A)** Formats logs as XML  
**B)** Parses XML  
**C)** Creates XML files  
**D)** Validates XML

**Answer: A)**

**Explanation:** **XMLFormatter** formats log records as **XML**.

---

### Question 16
```java
Logger logger = Logger.getLogger("MyLogger");
Handler[] handlers = logger.getHandlers();
```
What does getHandlers() return?

**A)** All logger names  
**B)** All handlers for this logger  
**C)** All log levels  
**D)** All log messages

**Answer: B)**

**Explanation:** `getHandlers()` returns **array of handlers** attached to logger.

---

### Question 17
```java
@SafeVarargs
public static <T> void method(T... elements) {}
```
What does @SafeVarargs do?

**A)** Validates varargs  
**B)** Suppresses varargs warnings  
**C)** Converts varargs to array  
**D)** Removes varargs

**Answer: B)**

**Explanation:** `@SafeVarargs` **suppresses** varargs-related warnings.

---

### Question 18
```java
@Documented
@interface MyAnnotation {}
```
What does @Documented do?

**A)** Creates documentation  
**B)** Includes annotation in Javadoc  
**C)** Removes documentation  
**D)** Nothing

**Answer: B)**

**Explanation:** `@Documented` includes annotation in **generated Javadoc**.

---

### Question 19
```java
@Inherited
@interface ParentAnnotation {}

@ParentAnnotation
class Parent {}

class Child extends Parent {}
```
Does Child have @ParentAnnotation?

**A)** No  
**B)** Yes - inherited from Parent  
**C)** Only if explicitly added  
**D)** Compilation error

**Answer: B)**

**Explanation:** `@Inherited` makes annotation **inherited** by subclasses.

---

### Question 20
```java
FileHandler fh = new FileHandler("app%g.log", 1024 * 1024, 5);
```
What does this create?

**A)** Single log file  
**B)** Rotating log files (5 files, 1MB each)  
**C)** Compressed log file  
**D)** Temporary log file

**Answer: B)**

**Explanation:** Creates **rotating logs**: max 1MB per file, up to **5 files** (app0.log, app1.log, ...).

---

## Score Interpretation

- **18-20 correct**: Excellent! You master logging and annotations.
- **15-17 correct**: Good understanding. Review log levels and meta-annotations.
- **12-14 correct**: Fair grasp. Study handlers, formatters, and annotation elements.
- **Below 12**: Need more practice. Review all logging and annotation concepts.

---

**🎉 Module 14 Complete! 🎉**

**🎓 Java SE 21 Certification Study Guide Complete! 🎓**

You've completed all 14 modules covering:
- Java Fundamentals (Primitives, Strings, Date/Time)
- Object-Oriented Programming (Classes, Inheritance, Interfaces, Enums, Records)
- Exception Handling
- Collections Framework
- Lambda Expressions and Stream API
- Concurrency and Multithreading
- I/O and NIO.2
- Serialization
- Module System
- Localization
- Logging and Annotations

**Total: 78 files created!**

**Previous:** [Theory - Logging and Annotations](38-logging.md)  
**Congratulations on completing your Java SE 21 certification preparation!**
