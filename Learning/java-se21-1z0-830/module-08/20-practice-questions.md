# Module 8: Exception Basics - Practice Questions

## Practice Questions (20)

### Question 1
Which statement is TRUE about exception handling in Java?
A) Checked exceptions extend RuntimeException  
B) Errors should always be caught and handled  
C) Unchecked exceptions must be declared with throws  
D) finally block always executes unless JVM exits

**Answer: D) finally block always executes unless JVM exits**

**Explanation**: The finally block executes regardless of whether an exception is thrown or caught, unless the JVM exits (System.exit()) or the thread is killed. Checked exceptions extend Exception (not RuntimeException), Errors should NOT be caught, and unchecked exceptions don't need throws declarations.

---

### Question 2
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try {
            System.out.print("A");
            int x = 10 / 0;
            System.out.print("B");
        } catch (ArithmeticException e) {
            System.out.print("C");
        } finally {
            System.out.print("D");
        }
    }
}
```
A) AB  
B) ACD  
C) ABCD  
D) AD

**Answer: B) ACD**

**Explanation**: "A" is printed, then ArithmeticException is thrown (dividing by zero), "B" is skipped, the catch block prints "C", and finally block prints "D". Output: ACD.

---

### Question 3
Which exception type is checked?
A) NullPointerException  
B) IOException  
C) ArithmeticException  
D) ClassCastException

**Answer: B) IOException**

**Explanation**: IOException is a checked exception that must be declared or caught. The other options (NullPointerException, ArithmeticException, ClassCastException) are unchecked exceptions (RuntimeException subclasses).

---

### Question 4
What is the result?
```java
public class Test {
    public static void main(String[] args) {
        try {
            return;
        } finally {
            System.out.println("Finally");
        }
    }
}
```
A) No output  
B) Finally  
C) Compilation error  
D) Runtime exception

**Answer: B) Finally**

**Explanation**: Even though there's a return statement in the try block, the finally block executes before the method returns. Output: "Finally".

---

### Question 5
Which is the correct order for catch blocks?
```java
try {
    // code
} // insert catch blocks here
```
A)
```java
catch (Exception e) { }
catch (IOException e) { }
```
B)
```java
catch (IOException e) { }
catch (Exception e) { }
```
C) Both A and B are valid  
D) Neither A nor B is valid

**Answer: B)**

**Explanation**: catch blocks must be ordered from most specific to most general. IOException is more specific than Exception, so it must come first. Option A won't compile because the IOException catch is unreachable (Exception catches everything).

---

### Question 6
What happens when this code runs?
```java
public class Test {
    public static void main(String[] args) {
        try {
            System.out.print("A");
            throw new RuntimeException();
        } catch (RuntimeException e) {
            System.out.print("B");
            return;
        } finally {
            System.out.print("C");
        }
        System.out.print("D");
    }
}
```
A) ABC  
B) ABCD  
C) AB  
D) ACD

**Answer: A) ABC**

**Explanation**: "A" is printed, exception is thrown and caught (prints "B"), return is encountered but finally executes first (prints "C"), then the method returns. "D" is never reached due to the return statement. Output: ABC.

---

### Question 7
Which statement about multi-catch is TRUE?
```java
catch (IOException | SQLException e) {
    // code
}
```
A) e can be reassigned to different exception  
B) IOException and SQLException must be related  
C) e is implicitly final  
D) Multi-catch requires Java 5+

**Answer: C) e is implicitly final**

**Explanation**: In multi-catch blocks, the exception variable is implicitly final and cannot be reassigned. The exception types must NOT be related (no parent-child relationship). Multi-catch was introduced in Java 7, not Java 5.

---

### Question 8
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        System.out.println(test());
    }
    
    public static int test() {
        try {
            return 10;
        } finally {
            return 20;
        }
    }
}
```
A) 10  
B) 20  
C) Compilation error  
D) 30

**Answer: B) 20**

**Explanation**: When finally contains a return statement, it overrides the return value from the try block. The method returns 20. (Note: Returning from finally is poor practice and generates a compiler warning.)

---

### Question 9
Which is an unchecked exception?
A) IOException  
B) SQLException  
C) IllegalArgumentException  
D) InterruptedException

**Answer: C) IllegalArgumentException**

**Explanation**: IllegalArgumentException extends RuntimeException, making it unchecked. IOException, SQLException, and InterruptedException are checked exceptions that must be declared or caught.

---

### Question 10
What happens when you compile this code?
```java
public void method() {
    FileReader fr = new FileReader("file.txt");
}
```
A) Compiles successfully  
B) Compilation error - FileReader not found  
C) Compilation error - IOException must be caught or declared  
D) Runtime exception

**Answer: C) Compilation error - IOException must be caught or declared**

**Explanation**: The FileReader constructor throws a checked exception (IOException) that must be either caught with try-catch or declared with throws. The code won't compile without handling this exception.

---

### Question 11
What is the result?
```java
public class Test {
    public static void main(String[] args) {
        try {
            int[] arr = new int[-5];
        } catch (NegativeArraySizeException e) {
            System.out.print("A");
        } catch (RuntimeException e) {
            System.out.print("B");
        }
    }
}
```
A) A  
B) B  
C) AB  
D) No output

**Answer: A) A**

**Explanation**: Creating an array with negative size throws NegativeArraySizeException. The first catch block matches (more specific), so "A" is printed. The second catch is not executed.

---

### Question 12
Which statement is TRUE about the finally block?
A) finally is optional  
B) finally must come before catch  
C) Only one finally block is allowed  
D) Both A and C

**Answer: D) Both A and C**

**Explanation**: The finally block is optional, but if present, only one is allowed and it must come after all catch blocks. You can have try-catch without finally, or try-finally without catch.

---

### Question 13
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try {
            method();
        } catch (Exception e) {
            System.out.print("Caught");
        }
    }
    
    public static void method() {
        throw new RuntimeException("Error");
    }
}
```
A) Error  
B) Caught  
C) Compilation error  
D) No output

**Answer: B) Caught**

**Explanation**: The method() throws RuntimeException which propagates to main() where it's caught by the catch block. "Caught" is printed.

---

### Question 14
Which exception is thrown by this code?
```java
String s = null;
int len = s.length();
```
A) NullPointerException  
B) IllegalArgumentException  
C) ArrayIndexOutOfBoundsException  
D) ClassCastException

**Answer: A) NullPointerException**

**Explanation**: Attempting to call a method on a null reference throws NullPointerException. This is one of the most common runtime exceptions.

---

### Question 15
What happens when you compile this code?
```java
try {
    // code
} catch (IOException | FileNotFoundException e) {
}
```
A) Compiles successfully  
B) Compilation error - FileNotFoundException is subclass of IOException  
C) Compilation error - missing finally  
D) Runtime exception

**Answer: B) Compilation error - FileNotFoundException is subclass of IOException**

**Explanation**: In multi-catch, exception types cannot have a parent-child relationship. FileNotFoundException extends IOException, so this code won't compile. You should only catch IOException.

---

### Question 16
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try {
            System.out.print("1");
            int x = Integer.parseInt("abc");
            System.out.print("2");
        } catch (NumberFormatException e) {
            System.out.print("3");
        } catch (Exception e) {
            System.out.print("4");
        }
    }
}
```
A) 12  
B) 13  
C) 14  
D) 1234

**Answer: B) 13**

**Explanation**: "1" is printed, then parseInt throws NumberFormatException (cannot parse "abc"), "2" is skipped, the first catch matches and prints "3". The second catch is not executed. Output: 13.

---

### Question 17
Which can follow a try block? (Choose all that apply)
A) catch only  
B) finally only  
C) catch and finally  
D) Neither catch nor finally

**Answer: A, B, and C**

**Explanation**: A try block can be followed by: catch only (try-catch), finally only (try-finally), or both catch and finally (try-catch-finally). Option D is invalid - a try must be followed by at least catch or finally.

---

### Question 18
What is the result?
```java
public class Test {
    public static void main(String[] args) {
        try {
            throw new Exception("Error");
        } catch (Exception e) {
            System.out.print(e.getMessage());
        }
    }
}
```
A) Exception  
B) Error  
C) java.lang.Exception: Error  
D) Compilation error

**Answer: B) Error**

**Explanation**: The getMessage() method returns the detail message string ("Error") that was passed to the Exception constructor. Output: "Error".

---

### Question 19
Which statement about exception propagation is TRUE?
A) Exceptions always propagate to main()  
B) Checked exceptions don't propagate  
C) Uncaught exceptions propagate up the call stack  
D) finally blocks prevent propagation

**Answer: C) Uncaught exceptions propagate up the call stack**

**Explanation**: If an exception is not caught in a method, it propagates to the caller. This continues up the call stack until caught or reaching main(). If uncaught in main(), the program terminates. Both checked and unchecked exceptions propagate, and finally blocks don't prevent propagation.

---

### Question 20
What is the output?
```java
public class Test {
    public static void main(String[] args) {
        try {
            System.out.print("A");
            throw new RuntimeException();
        } catch (NullPointerException e) {
            System.out.print("B");
        } catch (RuntimeException e) {
            System.out.print("C");
        } finally {
            System.out.print("D");
        }
    }
}
```
A) AB  
B) ACD  
C) ABCD  
D) AD

**Answer: B) ACD**

**Explanation**: "A" is printed, RuntimeException is thrown, first catch doesn't match (NullPointerException), second catch matches and prints "C", finally prints "D". Output: ACD.

---

## Answer Summary
1. D  2. B  3. B  4. B  5. B  
6. A  7. C  8. B  9. C  10. C  
11. A  12. D  13. B  14. A  15. B  
16. B  17. A,B,C  18. B  19. C  20. B
