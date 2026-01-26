# Module 7: Enums - Practice Questions

## Practice Questions (20)

### Question 1
What is the output?
```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY
}

public class Test {
    public static void main(String[] args) {
        Day day = Day.MONDAY;
        System.out.println(day.ordinal());
    }
}
```
A) 1  
B) 0  
C) MONDAY  
D) Compilation error

**Answer: B) 0**

**Explanation**: The `ordinal()` method returns the position of the enum constant in the enum declaration, starting from 0. MONDAY is the first constant, so its ordinal is 0. TUESDAY would be 1, WEDNESDAY would be 2, etc.

---

### Question 2
Which statement about enum constructors is TRUE?
```java
enum Size {
    SMALL("S"), MEDIUM("M"), LARGE("L");
    
    private String code;
    
    Size(String code) {  // Line X
        this.code = code;
    }
}
```
A) Line X must be declared public  
B) Line X must be declared protected  
C) Line X is implicitly private  
D) Line X will cause a compilation error

**Answer: C) Line X is implicitly private**

**Explanation**: Enum constructors are implicitly private and cannot be public or protected. This prevents external code from creating new enum instances. The constructor can only be called internally when the enum constants are initialized.

---

### Question 3
What is the result?
```java
enum Color {
    RED, GREEN, BLUE
}

public class Test {
    public static void main(String[] args) {
        Color color = Color.valueOf("red");
        System.out.println(color);
    }
}
```
A) RED  
B) red  
C) IllegalArgumentException  
D) Compilation error

**Answer: C) IllegalArgumentException**

**Explanation**: The `valueOf()` method is case-sensitive and must match the exact enum constant name. "red" doesn't match "RED", so `valueOf()` throws an `IllegalArgumentException`. The correct call would be `Color.valueOf("RED")`.

---

### Question 4
What is the output?
```java
enum Level {
    LOW, MEDIUM, HIGH
}

public class Test {
    public static void main(String[] args) {
        Level[] levels = Level.values();
        System.out.println(levels.length);
    }
}
```
A) 0  
B) 2  
C) 3  
D) Compilation error

**Answer: C) 3**

**Explanation**: The `values()` method returns an array containing all enum constants in the order they're declared. Level has three constants (LOW, MEDIUM, HIGH), so the array length is 3.

---

### Question 5
Which enum declaration is INVALID?
A)
```java
enum A {
    X, Y, Z
}
```
B)
```java
enum B {
    X, Y, Z;
    private int value;
}
```
C)
```java
public enum C {
    X(1), Y(2), Z(3);
    private int value;
    public C(int value) {
        this.value = value;
    }
}
```
D)
```java
enum D {
    X, Y, Z;
    public void method() { }
}
```

**Answer: C)**

**Explanation**: Enum constructors cannot be public or protected; they must be private or package-private. Option C attempts to declare a public constructor, which causes a compilation error. All other options are valid.

---

### Question 6
What is the output?
```java
enum Status {
    PENDING, APPROVED, REJECTED
}

public class Test {
    public static void main(String[] args) {
        Status s1 = Status.APPROVED;
        Status s2 = Status.APPROVED;
        System.out.println(s1 == s2);
    }
}
```
A) true  
B) false  
C) Compilation error  
D) Runtime error

**Answer: A) true**

**Explanation**: Enum constants are singleton instances. There's only one instance of each enum constant in the JVM. Both `s1` and `s2` reference the same APPROVED instance, so `==` comparison returns true. This is why `==` is preferred over `equals()` for enums.

---

### Question 7
What is the result?
```java
enum Operation {
    PLUS {
        public int apply(int x, int y) { return x + y; }
    },
    MINUS {
        public int apply(int x, int y) { return x - y; }
    };
    
    public abstract int apply(int x, int y);
}

public class Test {
    public static void main(String[] args) {
        System.out.println(Operation.PLUS.apply(5, 3));
    }
}
```
A) 8  
B) 2  
C) 15  
D) Compilation error

**Answer: A) 8**

**Explanation**: This demonstrates constant-specific method implementation in enums. Each enum constant (PLUS, MINUS) provides its own implementation of the abstract `apply()` method. PLUS.apply(5, 3) returns 5 + 3 = 8.

---

### Question 8
Which is TRUE about this code?
```java
enum Day {
    MONDAY, TUESDAY, WEDNESDAY
}

public class Test {
    public static void main(String[] args) {
        Day day = new Day();  // Line X
    }
}
```
A) Compiles successfully  
B) Line X causes compilation error  
C) Runtime error at Line X  
D) day will be null

**Answer: B) Line X causes compilation error**

**Explanation**: Enums cannot be instantiated using the `new` keyword. Enum instances can only be the predefined constants. You can only reference existing enum constants like `Day.MONDAY`, not create new instances.

---

### Question 9
What is the output?
```java
enum Size {
    SMALL, MEDIUM, LARGE;
    
    public static void main(String[] args) {
        System.out.println("Testing enum");
    }
}

public class Test {
    public static void main(String[] args) {
        Size.main(args);
    }
}
```
A) Testing enum  
B) Compilation error  
C) Runtime error  
D) No output

**Answer: A) Testing enum**

**Explanation**: Enums can have a main() method just like regular classes. When called explicitly via `Size.main(args)`, it executes and prints "Testing enum". This is valid but uncommon in practice.

---

### Question 10
What happens when you compile this code?
```java
enum Priority {
    LOW(1), MEDIUM(2), HIGH(3);
    
    private int level;
    
    Priority(int level) {
        this.level = level;
    }
}

class Urgent extends Priority {  // Line X
}
```
A) Compiles successfully  
B) Compilation error at Line X  
C) Runtime error  
D) Urgent enum is created

**Answer: B) Compilation error at Line X**

**Explanation**: Enums are implicitly final and cannot be extended. All enum types implicitly extend `java.lang.Enum`, and Java doesn't support multiple inheritance. Line X attempts to extend an enum, which is illegal.

---

### Question 11
What is the output?
```java
enum Month {
    JAN, FEB, MAR
}

public class Test {
    public static void main(String[] args) {
        Month month = Month.FEB;
        
        switch (month) {
            case JAN:
                System.out.print("January");
                break;
            case Month.FEB:  // Line X
                System.out.print("February");
                break;
            case MAR:
                System.out.print("March");
                break;
        }
    }
}
```
A) February  
B) Compilation error at Line X  
C) Runtime error  
D) No output

**Answer: B) Compilation error at Line X**

**Explanation**: In switch statements with enums, case labels must use unqualified enum constant names. You cannot use `Month.FEB`; it must be just `FEB`. The enum type is already known from the switch expression.

---

### Question 12
What is TRUE about this enum?
```java
enum Animal {
    DOG, CAT, BIRD;
    
    private String sound;
    
    public void setSound(String sound) {
        this.sound = sound;
    }
}
```
A) Each enum constant can have different sounds  
B) All enum constants share the same sound value  
C) sound must be final  
D) setSound() is not allowed in enums

**Answer: A) Each enum constant can have different sounds**

**Explanation**: Each enum constant is a separate instance with its own set of instance variables. DOG, CAT, and BIRD are different objects, so each can have its own `sound` value. Instance variables in enums don't have to be final (though they often are for immutability).

---

### Question 13
What is the output?
```java
enum Status {
    ACTIVE, INACTIVE;
    
    public static Status getDefault() {
        return ACTIVE;
    }
}

public class Test {
    public static void main(String[] args) {
        Status status = Status.getDefault();
        System.out.println(status.name());
    }
}
```
A) ACTIVE  
B) active  
C) getDefault  
D) Compilation error

**Answer: A) ACTIVE**

**Explanation**: The `name()` method returns the name of the enum constant exactly as declared. The static method `getDefault()` returns the ACTIVE constant, and `name()` returns the string "ACTIVE".

---

### Question 14
Which statement about EnumSet is TRUE?
```java
import java.util.EnumSet;

enum Day {
    MON, TUE, WED, THU, FRI, SAT, SUN
}
```
A) EnumSet can contain elements from multiple enum types  
B) EnumSet.of(Day.MON, Day.FRI) creates a set with MON and FRI  
C) EnumSet is slower than HashSet for enums  
D) EnumSet allows null elements

**Answer: B) EnumSet.of(Day.MON, Day.FRI) creates a set with MON and FRI**

**Explanation**: `EnumSet.of()` creates an EnumSet containing the specified enum constants. EnumSet can only contain elements from a single enum type (A is false), is more efficient than HashSet for enums (C is false), and doesn't allow null elements (D is false).

---

### Question 15
What is the result?
```java
enum Color {
    RED, GREEN, BLUE
}

public class Test {
    public static void main(String[] args) {
        Color color = null;
        System.out.println(color.name());
    }
}
```
A) null  
B) RED  
C) NullPointerException  
D) Compilation error

**Answer: C) NullPointerException**

**Explanation**: Calling any method (including `name()`) on a null reference throws a `NullPointerException`. The variable `color` is null, so attempting to invoke `name()` on it fails at runtime.

---

### Question 16
What is the output?
```java
enum Level {
    LOW, MEDIUM, HIGH
}

public class Test {
    public static void main(String[] args) {
        Level level = Level.MEDIUM;
        System.out.println(level.ordinal() + " " + level.name());
    }
}
```
A) 0 MEDIUM  
B) 1 MEDIUM  
C) 2 MEDIUM  
D) MEDIUM 1

**Answer: B) 1 MEDIUM**

**Explanation**: `ordinal()` returns the position (0-based index) in the enum declaration. MEDIUM is at index 1 (LOW=0, MEDIUM=1, HIGH=2). `name()` returns the constant name as a string. Output: "1 MEDIUM".

---

### Question 17
Which enum implementation is VALID?
A)
```java
enum A implements Serializable {
    X, Y
}
```
B)
```java
enum B extends Object {
    X, Y
}
```
C)
```java
enum C extends Enum {
    X, Y
}
```
D)
```java
class D extends Enum {
    X, Y
}
```

**Answer: A)**

**Explanation**: Enums can implement interfaces (like Serializable). However, enums cannot explicitly extend any class because they implicitly extend `java.lang.Enum`. Options B, C, and D all attempt to extend a class, which is illegal for enums.

---

### Question 18
What is the output?
```java
enum Size {
    SMALL, MEDIUM, LARGE
}

public class Test {
    public static void main(String[] args) {
        System.out.println(Size.valueOf("MEDIUM") == Size.MEDIUM);
    }
}
```
A) true  
B) false  
C) Compilation error  
D) IllegalArgumentException

**Answer: A) true**

**Explanation**: `valueOf("MEDIUM")` returns the MEDIUM enum constant. Since enum constants are singletons, `valueOf()` returns the exact same instance as the constant reference. Therefore, `==` comparison returns true.

---

### Question 19
What happens with this code?
```java
enum Operation {
    PLUS, MINUS;
    
    public int calculate(int a, int b) {
        return a + b;
    }
}

public class Test {
    public static void main(String[] args) {
        System.out.println(Operation.MINUS.calculate(10, 5));
    }
}
```
A) 15  
B) 5  
C) -5  
D) Compilation error

**Answer: A) 15**

**Explanation**: The `calculate()` method is defined once for the enum and shared by all constants. Both PLUS and MINUS will use the same implementation (a + b). This returns 10 + 5 = 15, regardless of which constant calls it. To have different behavior per constant, you'd need constant-specific implementations.

---

### Question 20
What is TRUE about enum comparison?
```java
enum Priority {
    LOW, HIGH
}
```
A) Must use equals() for comparison  
B) Can use == for comparison  
C) == and equals() give different results  
D) Enums cannot be compared

**Answer: B) Can use == for comparison**

**Explanation**: Enum constants are singletons, so `==` is safe and actually preferred for enum comparison. It's null-safe and more efficient than `equals()`. Both `==` and `equals()` give the same result for enums, but `==` is recommended because it handles null gracefully.

---

## Answer Summary
1. B  2. C  3. C  4. C  5. C  
6. A  7. A  8. B  9. A  10. B  
11. B  12. A  13. A  14. B  15. C  
16. B  17. A  18. A  19. A  20. B
