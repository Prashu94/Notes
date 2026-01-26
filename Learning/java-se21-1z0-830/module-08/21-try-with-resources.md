# Module 8: Exception Handling - try-with-resources and Custom Exceptions

## Table of Contents
1. [try-with-resources Introduction](#try-with-resources-introduction)
2. [AutoCloseable Interface](#autocloseable-interface)
3. [Resource Management](#resource-management)
4. [Multiple Resources](#multiple-resources)
5. [Suppressed Exceptions](#suppressed-exceptions)
6. [Custom Exceptions](#custom-exceptions)
7. [Exception Chaining](#exception-chaining)
8. [Best Practices](#best-practices)

## try-with-resources Introduction

**try-with-resources** (introduced in Java 7) automatically closes resources that implement `AutoCloseable` or `Closeable`, eliminating the need for explicit `finally` blocks.

### Old Way (Before Java 7)

```java
// Manual resource management - verbose and error-prone
BufferedReader reader = null;
try {
    reader = new BufferedReader(new FileReader("file.txt"));
    String line = reader.readLine();
    System.out.println(line);
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (reader != null) {
        try {
            reader.close();  // Must close manually
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### New Way (Java 7+)

```java
// Automatic resource management - clean and safe
try (BufferedReader reader = new BufferedReader(new FileReader("file.txt"))) {
    String line = reader.readLine();
    System.out.println(line);
} catch (IOException e) {
    e.printStackTrace();
}
// reader.close() is called automatically
```

### Benefits

1. **Automatic cleanup**: Resources closed automatically
2. **Guaranteed cleanup**: Close happens even if exception thrown
3. **Cleaner code**: No verbose finally blocks
4. **Exception suppression**: Handles multiple exceptions properly
5. **Compiler enforcement**: Ensures resources are closed

## AutoCloseable Interface

Any resource used in try-with-resources must implement `AutoCloseable` or `Closeable`:

### AutoCloseable Interface

```java
public interface AutoCloseable {
    void close() throws Exception;
}
```

### Closeable Interface

```java
public interface Closeable extends AutoCloseable {
    void close() throws IOException;
}
```

**Difference:**
- `AutoCloseable.close()` can throw any `Exception`
- `Closeable.close()` can only throw `IOException` (more restrictive)

### Built-in AutoCloseable Classes

Many Java classes implement AutoCloseable:

```java
// I/O classes
FileInputStream, FileOutputStream
BufferedReader, BufferedWriter
Scanner, PrintWriter

// Database classes
Connection, Statement, ResultSet

// Network classes
Socket, ServerSocket

// NIO classes
FileChannel, ByteChannel
```

### Creating Custom AutoCloseable Resource

```java
public class MyResource implements AutoCloseable {
    public MyResource() {
        System.out.println("Resource opened");
    }
    
    public void doWork() {
        System.out.println("Working...");
    }
    
    @Override
    public void close() {
        System.out.println("Resource closed");
    }
}

// Usage
try (MyResource resource = new MyResource()) {
    resource.doWork();
}
// Output:
// Resource opened
// Working...
// Resource closed
```

## Resource Management

### Basic Syntax

```java
try (ResourceType resource = new ResourceType()) {
    // Use resource
} catch (ExceptionType e) {
    // Handle exception
}
// resource.close() called automatically
```

### Complete Example

```java
import java.io.*;

public class ReadFile {
    public static void main(String[] args) {
        try (FileReader fr = new FileReader("data.txt");
             BufferedReader br = new BufferedReader(fr)) {
            
            String line;
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }
        } catch (IOException e) {
            System.out.println("Error reading file: " + e.getMessage());
        }
        // Both fr and br are closed automatically (in reverse order)
    }
}
```

### Resource Initialization

Resources must be initialized in the try declaration:

```java
// VALID
try (Scanner sc = new Scanner(System.in)) {
    String input = sc.nextLine();
}

// INVALID - won't compile
Scanner sc;
try (sc = new Scanner(System.in)) {  // Compile error
    String input = sc.nextLine();
}
```

### Scope of Resources

Resources declared in try-with-resources are implicitly final and scoped to the try block:

```java
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    // br is available here
    String line = br.readLine();
    // br = new BufferedReader(new FileReader("other.txt"));  // Compile error - final
} catch (IOException e) {
    // br not available here
    // System.out.println(br);  // Compile error - out of scope
}
```

## Multiple Resources

You can manage multiple resources in one try-with-resources statement:

### Semicolon-Separated Resources

```java
try (FileInputStream fis = new FileInputStream("input.txt");
     FileOutputStream fos = new FileOutputStream("output.txt")) {
    
    int data;
    while ((data = fis.read()) != -1) {
        fos.write(data);
    }
} catch (IOException e) {
    e.printStackTrace();
}
// Both fis and fos are closed automatically in reverse order (fos then fis)
```

### Closing Order

Resources are closed in **reverse order** of declaration:

```java
class Resource implements AutoCloseable {
    private String name;
    
    public Resource(String name) {
        this.name = name;
        System.out.println(name + " opened");
    }
    
    @Override
    public void close() {
        System.out.println(name + " closed");
    }
}

// Usage
try (Resource r1 = new Resource("First");
     Resource r2 = new Resource("Second");
     Resource r3 = new Resource("Third")) {
    System.out.println("Using resources");
}

// Output:
// First opened
// Second opened
// Third opened
// Using resources
// Third closed    <- Reverse order
// Second closed
// First closed
```

### Java 9+ Enhancement: Effectively Final Variables

Java 9+ allows using effectively final variables:

```java
// Java 9+
BufferedReader br = new BufferedReader(new FileReader("file.txt"));
try (br) {  // Can use existing variable if effectively final
    String line = br.readLine();
}

// Multiple resources
Scanner sc1 = new Scanner(System.in);
Scanner sc2 = new Scanner("Hello");
try (sc1; sc2) {
    // Use scanners
}
```

## Suppressed Exceptions

When both the try block and close() method throw exceptions, the close() exception is **suppressed**:

### Suppressed Exception Example

```java
class ProblematicResource implements AutoCloseable {
    public void use() throws Exception {
        throw new Exception("Exception in use()");
    }
    
    @Override
    public void close() throws Exception {
        throw new Exception("Exception in close()");
    }
}

public class Test {
    public static void main(String[] args) {
        try (ProblematicResource res = new ProblematicResource()) {
            res.use();
        } catch (Exception e) {
            System.out.println("Main exception: " + e.getMessage());
            
            // Get suppressed exceptions
            Throwable[] suppressed = e.getSuppressed();
            for (Throwable t : suppressed) {
                System.out.println("Suppressed: " + t.getMessage());
            }
        }
    }
}

// Output:
// Main exception: Exception in use()
// Suppressed: Exception in close()
```

### Why Suppression Matters

```java
// Without try-with-resources (old way)
Resource res = null;
try {
    res = new Resource();
    res.use();  // Throws exception
} finally {
    if (res != null) {
        res.close();  // Also throws exception - MASKS the first exception!
    }
}
// The exception from use() is lost!

// With try-with-resources
try (Resource res = new Resource()) {
    res.use();  // Primary exception
}  // close() exception is suppressed, not lost
```

### Accessing Suppressed Exceptions

```java
Throwable[] getSuppressed()  // Returns array of suppressed exceptions
void addSuppressed(Throwable exception)  // Adds suppressed exception
```

## Custom Exceptions

Creating custom exceptions allows you to represent application-specific error conditions:

### Basic Custom Exception

```java
public class InvalidAgeException extends Exception {
    public InvalidAgeException() {
        super();
    }
    
    public InvalidAgeException(String message) {
        super(message);
    }
    
    public InvalidAgeException(String message, Throwable cause) {
        super(message, cause);
    }
    
    public InvalidAgeException(Throwable cause) {
        super(cause);
    }
}
```

### Custom Runtime Exception

```java
public class InsufficientFundsException extends RuntimeException {
    private double deficit;
    
    public InsufficientFundsException(double deficit) {
        super("Insufficient funds. Deficit: $" + deficit);
        this.deficit = deficit;
    }
    
    public double getDeficit() {
        return deficit;
    }
}
```

### Using Custom Exceptions

```java
public class BankAccount {
    private double balance;
    
    public BankAccount(double balance) {
        this.balance = balance;
    }
    
    public void withdraw(double amount) {
        if (amount > balance) {
            throw new InsufficientFundsException(amount - balance);
        }
        balance -= amount;
    }
}

// Usage
try {
    BankAccount account = new BankAccount(100);
    account.withdraw(150);
} catch (InsufficientFundsException e) {
    System.out.println(e.getMessage());
    System.out.println("Deficit: $" + e.getDeficit());
}
```

### Checked vs Unchecked Custom Exceptions

```java
// Checked - extends Exception
public class DatabaseException extends Exception {
    public DatabaseException(String message) {
        super(message);
    }
}

// Must be declared or caught
public void saveData() throws DatabaseException {
    // If error occurs
    throw new DatabaseException("Failed to save");
}

// Unchecked - extends RuntimeException
public class ValidationException extends RuntimeException {
    public ValidationException(String message) {
        super(message);
    }
}

// No need to declare
public void validateInput(String input) {
    if (input == null) {
        throw new ValidationException("Input cannot be null");
    }
}
```

## Exception Chaining

Exception chaining links a new exception to an original cause:

### Basic Chaining

```java
public class DataProcessor {
    public void processFile(String path) throws DataProcessingException {
        try {
            FileReader reader = new FileReader(path);
            // Process file
        } catch (FileNotFoundException e) {
            // Wrap the original exception
            throw new DataProcessingException("Cannot process file: " + path, e);
        }
    }
}

// Custom exception with chaining support
public class DataProcessingException extends Exception {
    public DataProcessingException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### Accessing the Cause

```java
try {
    processor.processFile("data.txt");
} catch (DataProcessingException e) {
    System.out.println("Error: " + e.getMessage());
    
    // Get original cause
    Throwable cause = e.getCause();
    if (cause != null) {
        System.out.println("Caused by: " + cause.getMessage());
    }
    
    // Print full stack trace (shows cause chain)
    e.printStackTrace();
}
```

### initCause Method

```java
public class CustomException extends Exception {
    public CustomException(String message) {
        super(message);
    }
}

// Setting cause after construction
try {
    // Some operation
} catch (IOException e) {
    CustomException ce = new CustomException("Operation failed");
    ce.initCause(e);  // Set the cause
    throw ce;
}
```

### Multi-Level Chaining

```java
public class ServiceLayer {
    public void businessOperation() throws ServiceException {
        try {
            dataLayer.databaseOperation();
        } catch (DataException e) {
            throw new ServiceException("Business operation failed", e);
        }
    }
}

public class DataLayer {
    public void databaseOperation() throws DataException {
        try {
            Connection conn = getConnection();
        } catch (SQLException e) {
            throw new DataException("Database operation failed", e);
        }
    }
}

// Stack trace shows the full chain:
// ServiceException: Business operation failed
//     Caused by: DataException: Database operation failed
//         Caused by: SQLException: Connection refused
```

## Best Practices

### 1. Always Use try-with-resources for AutoCloseable

```java
// BAD - manual closing
BufferedReader br = null;
try {
    br = new BufferedReader(new FileReader("file.txt"));
} finally {
    if (br != null) br.close();
}

// GOOD - automatic closing
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    // Use br
}
```

### 2. Close Resources in Reverse Order

```java
// try-with-resources handles this automatically
try (FileInputStream fis = new FileInputStream("input.txt");
     BufferedInputStream bis = new BufferedInputStream(fis)) {
    // bis is closed first, then fis
}
```

### 3. Create Specific Custom Exceptions

```java
// BAD - generic exception
throw new Exception("Invalid age");

// GOOD - specific exception
throw new InvalidAgeException("Age must be between 0 and 150");
```

### 4. Include Context in Exception Messages

```java
// BAD
throw new IllegalArgumentException("Invalid input");

// GOOD
throw new IllegalArgumentException(
    "Invalid input: expected positive number, got " + value
);
```

### 5. Use Checked Exceptions for Recoverable Conditions

```java
// User can retry or handle differently
public void connectToDatabase() throws ConnectionException {
    // Checked - caller must handle
}
```

### 6. Use Unchecked Exceptions for Programming Errors

```java
// Programming error - should be fixed in code
public void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("Age cannot be negative");
    }
}
```

### 7. Don't Suppress Exceptions Without Logging

```java
// BAD
try (Resource r = new Resource()) {
} catch (Exception e) {
    // Silent suppression
}

// GOOD
try (Resource r = new Resource()) {
} catch (Exception e) {
    logger.error("Failed to use resource", e);
}
```

## Summary

- **try-with-resources** automatically closes AutoCloseable resources
- Resources must implement `AutoCloseable` or `Closeable` interfaces
- Resources are closed in **reverse order** of declaration
- Java 9+ allows using effectively final variables in try-with-resources
- **Suppressed exceptions** occur when both try block and close() throw exceptions
- Use `getSuppressed()` to access suppressed exceptions
- **Custom exceptions** represent application-specific error conditions
- Extend `Exception` for checked, `RuntimeException` for unchecked exceptions
- **Exception chaining** links new exceptions to original causes using constructors or `initCause()`
- Use `getCause()` to access the original exception
- Best practices: use try-with-resources, create specific exceptions, include context in messages

## Key Takeaways

1. try-with-resources eliminates manual resource cleanup
2. AutoCloseable.close() is called automatically, even with exceptions
3. Multiple resources are closed in reverse order
4. Suppressed exceptions preserve exception information
5. Custom exceptions improve error handling clarity
6. Checked exceptions force handling, unchecked indicate programming errors
7. Exception chaining preserves root cause information
8. Always include meaningful exception messages
9. Java 9+ allows effectively final variables in try-with-resources
10. Never silently suppress exceptions without logging
