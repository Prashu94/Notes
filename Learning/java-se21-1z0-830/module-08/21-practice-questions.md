# Module 8: try-with-resources and Custom Exceptions - Practice Questions

## Practice Questions (20)

### Question 1
Which interface must a resource implement to be used in try-with-resources?
A) Closeable only  
B) AutoCloseable or Closeable  
C) Serializable  
D) Cloneable

**Answer: B) AutoCloseable or Closeable**

**Explanation**: Resources in try-with-resources must implement AutoCloseable or its sub-interface Closeable. Closeable extends AutoCloseable and is more specific (throws only IOException). Serializable and Cloneable are unrelated to resource management.

---

### Question 2
What is the output?
```java
class MyResource implements AutoCloseable {
    public MyResource() {
        System.out.print("Open ");
    }
    
    public void close() {
        System.out.print("Close ");
    }
}

public class Test {
    public static void main(String[] args) {
        try (MyResource r = new MyResource()) {
            System.out.print("Use ");
        }
    }
}
```
A) Open Use Close  
B) Open Close Use  
C) Use Open Close  
D) Open Use

**Answer: A) Open Use Close**

**Explanation**: Constructor runs first (prints "Open "), try block executes (prints "Use "), then close() is called automatically (prints "Close "). Output: "Open Use Close ".

---

### Question 3
What happens when this code runs?
```java
try (Scanner sc = new Scanner(System.in)) {
    sc = new Scanner("Hello");
}
```
A) Compiles and runs successfully  
B) Compilation error - sc is final  
C) Runtime exception  
D) No output

**Answer: B) Compilation error - sc is final**

**Explanation**: Resources declared in try-with-resources are implicitly final and cannot be reassigned. Attempting to reassign `sc` causes a compilation error.

---

### Question 4
Which statement about resource closing order is TRUE?
```java
try (Resource r1 = new Resource();
     Resource r2 = new Resource();
     Resource r3 = new Resource()) {
    // code
}
```
A) Resources close in declaration order: r1, r2, r3  
B) Resources close in reverse order: r3, r2, r1  
C) Resources close in random order  
D) Only r3 is closed

**Answer: B) Resources close in reverse order: r3, r2, r1**

**Explanation**: Resources in try-with-resources are always closed in reverse order of their declaration. This ensures that dependent resources are closed before their dependencies.

---

### Question 5
What is the result?
```java
class ProblematicResource implements AutoCloseable {
    public void use() throws Exception {
        throw new Exception("Use failed");
    }
    
    public void close() throws Exception {
        throw new Exception("Close failed");
    }
}

public class Test {
    public static void main(String[] args) {
        try (ProblematicResource r = new ProblematicResource()) {
            r.use();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.out.println(e.getSuppressed().length);
        }
    }
}
```
A) Use failed, 0  
B) Close failed, 0  
C) Use failed, 1  
D) Close failed, 1

**Answer: C) Use failed, 1**

**Explanation**: The exception from use() is the main exception. The exception from close() is suppressed. getSuppressed() returns an array with 1 element (the close exception). Output: "Use failed" and "1".

---

### Question 6
Which is the correct way to create a checked custom exception?
A) `public class MyException extends RuntimeException`  
B) `public class MyException extends Exception`  
C) `public class MyException extends Error`  
D) `public class MyException extends Throwable`

**Answer: B) `public class MyException extends Exception`**

**Explanation**: Custom checked exceptions should extend Exception (not RuntimeException, Error, or Throwable directly). Extending RuntimeException creates unchecked exceptions. Errors represent serious JVM problems and should not be extended.

---

### Question 7
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try (MyResource r1 = new MyResource("A");
             MyResource r2 = new MyResource("B")) {
            System.out.print("Use ");
        }
    }
}

class MyResource implements AutoCloseable {
    private String name;
    
    public MyResource(String name) {
        this.name = name;
        System.out.print(name + "Open ");
    }
    
    public void close() {
        System.out.print(name + "Close ");
    }
}
```
A) AOpen BOpen Use AClose BClose  
B) AOpen BOpen Use BClose AClose  
C) BOpen AOpen Use AClose BClose  
D) BOpen AOpen Use BClose AClose

**Answer: B) AOpen BOpen Use BClose AClose**

**Explanation**: Resources are created in order (A then B), try block executes, then resources close in reverse order (B then A). Output: "AOpen BOpen Use BClose AClose ".

---

### Question 8
Which is TRUE about exception chaining?
```java
throw new ServiceException("Failed", originalException);
```
A) originalException is discarded  
B) originalException can be retrieved with getCause()  
C) originalException becomes the main exception  
D) Chaining is only for checked exceptions

**Answer: B) originalException can be retrieved with getCause()**

**Explanation**: Exception chaining wraps one exception inside another. The wrapped exception can be retrieved using getCause(). This preserves the original cause while adding context. Chaining works for both checked and unchecked exceptions.

---

### Question 9
What happens when you compile this code?
```java
BufferedReader br = new BufferedReader(new FileReader("file.txt"));
br = new BufferedReader(new FileReader("other.txt"));
try (br) {
    String line = br.readLine();
}
```
A) Compiles successfully (Java 9+)  
B) Compilation error - br is reassigned  
C) Compilation error - br not initialized in try  
D) Runtime exception

**Answer: B) Compilation error - br is reassigned**

**Explanation**: Even in Java 9+, the variable used in try-with-resources must be effectively final. Reassigning `br` makes it not effectively final, causing a compilation error.

---

### Question 10
Which method is part of the Throwable class for exception chaining?
A) getCause()  
B) getOrigin()  
C) getParent()  
D) getRoot()

**Answer: A) getCause()**

**Explanation**: The getCause() method returns the cause of the exception (the exception that caused this exception to be thrown). This is part of the exception chaining mechanism. The other methods don't exist in Throwable.

---

### Question 11
What is the result?
```java
public class InvalidInputException extends RuntimeException {
    public InvalidInputException(String message) {
        super(message);
    }
}

public class Test {
    public static void main(String[] args) throws InvalidInputException {
        throw new InvalidInputException("Bad input");
    }
}
```
A) Compilation error - must catch exception  
B) Compilation error - throws not needed  
C) Compiles and throws exception at runtime  
D) No output

**Answer: C) Compiles and throws exception at runtime**

**Explanation**: InvalidInputException extends RuntimeException (unchecked), so it doesn't need to be declared with throws (though it's allowed). The code compiles and throws the exception at runtime.

---

### Question 12
Which is TRUE about AutoCloseable vs Closeable?
A) AutoCloseable extends Closeable  
B) Closeable extends AutoCloseable  
C) They are unrelated interfaces  
D) They are the same interface

**Answer: B) Closeable extends AutoCloseable**

**Explanation**: Closeable extends AutoCloseable and is more specific. AutoCloseable.close() throws Exception, while Closeable.close() throws only IOException. Any Closeable is also an AutoCloseable.

---

### Question 13
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try {
            method1();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            System.out.println(e.getCause().getMessage());
        }
    }
    
    public static void method1() throws Exception {
        try {
            throw new IOException("IO Error");
        } catch (IOException e) {
            throw new Exception("Wrapper", e);
        }
    }
}
```
A) Wrapper, null  
B) IO Error, null  
C) Wrapper, IO Error  
D) Compilation error

**Answer: C) Wrapper, IO Error**

**Explanation**: The Exception constructor with two parameters sets the message to "Wrapper" and the cause to the IOException. getMessage() returns "Wrapper", getCause().getMessage() returns "IO Error".

---

### Question 14
What happens when this code compiles?
```java
try {
    // code
}
```
A) Compiles successfully  
B) Compilation error - missing catch or finally  
C) Compilation error - missing resource  
D) Runtime exception

**Answer: B) Compilation error - missing catch or finally**

**Explanation**: A try block must be followed by either catch, finally, or both (or be a try-with-resources). A standalone try block without catch/finally causes a compilation error.

---

### Question 15
Which custom exception type should be used for a programming error?
A) Extending Exception  
B) Extending RuntimeException  
C) Extending Error  
D) Extending Throwable

**Answer: B) Extending RuntimeException**

**Explanation**: Programming errors (like invalid arguments) should use unchecked exceptions by extending RuntimeException. Checked exceptions (Exception) are for recoverable conditions. Errors are for serious JVM issues and shouldn't be extended.

---

### Question 16
What is the result?
```java
try (Scanner sc = new Scanner("Hello World")) {
    System.out.println(sc.next());
}
System.out.println(sc.next());
```
A) Hello, World  
B) Hello, then compilation error  
C) Compilation error - sc out of scope  
D) Runtime exception

**Answer: C) Compilation error - sc out of scope**

**Explanation**: Resources declared in try-with-resources are scoped to the try block only. The variable `sc` is not accessible outside the try block, causing a compilation error.

---

### Question 17
Which is TRUE about suppressed exceptions?
A) They are completely discarded  
B) They can be accessed with getSuppressed()  
C) They become the main exception  
D) They only occur with checked exceptions

**Answer: B) They can be accessed with getSuppressed()**

**Explanation**: Suppressed exceptions (like close() exceptions in try-with-resources) are not discarded but are attached to the main exception and can be retrieved using getSuppressed(). This preserves all exception information.

---

### Question 18
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try (Resource r = new Resource()) {
            throw new Exception("Error");
        } catch (Exception e) {
            System.out.print("Caught ");
        }
    }
}

class Resource implements AutoCloseable {
    public void close() {
        System.out.print("Closed ");
    }
}
```
A) Caught Closed  
B) Closed Caught  
C) Caught  
D) Closed

**Answer: B) Closed Caught**

**Explanation**: When an exception is thrown in try-with-resources, close() is called first, then the catch block executes. Output: "Closed Caught ".

---

### Question 19
Which statement is TRUE about exception constructors?
```java
public MyException(String message, Throwable cause) {
    super(message, cause);
}
```
A) This creates exception chaining  
B) This creates suppressed exceptions  
C) This is invalid syntax  
D) cause parameter is ignored

**Answer: A) This creates exception chaining**

**Explanation**: Passing a Throwable to the exception constructor creates exception chaining. The cause can be retrieved with getCause(). This is different from suppressed exceptions which occur in try-with-resources.

---

### Question 20
What happens when this code runs?
```java
class MyResource implements AutoCloseable {
    public void close() throws InterruptedException {
        Thread.sleep(100);
    }
}

public class Test {
    public static void main(String[] args) {
        try (MyResource r = new MyResource()) {
            System.out.println("Using");
        }
    }
}
```
A) Compiles and runs successfully  
B) Compilation error - InterruptedException must be caught  
C) Runtime exception  
D) Infinite loop

**Answer: B) Compilation error - InterruptedException must be caught**

**Explanation**: close() throws a checked exception (InterruptedException) which must be caught or declared. The main method doesn't handle this exception, causing a compilation error.

---

## Answer Summary
1. B  2. A  3. B  4. B  5. C  
6. B  7. B  8. B  9. B  10. A  
11. C  12. B  13. C  14. B  15. B  
16. C  17. B  18. B  19. A  20. B
