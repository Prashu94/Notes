# Module 7: Records - Practice Questions

## Practice Questions (20)

### Question 1
What is automatically generated for a record?
```java
record Point(int x, int y) { }
```
A) Only constructor  
B) Constructor, getX(), getY()  
C) Constructor, x(), y(), equals(), hashCode(), toString()  
D) Only equals() and hashCode()

**Answer: C) Constructor, x(), y(), equals(), hashCode(), toString()**

**Explanation**: Records automatically generate: a canonical constructor, accessor methods named after components (not getters!), equals(), hashCode(), and toString(). The accessor methods are `x()` and `y()`, not `getX()` and `getY()`.

---

### Question 2
What is the output?
```java
record Person(String name, int age) { }

public class Test {
    public static void main(String[] args) {
        Person p = new Person("Alice", 30);
        System.out.println(p.name());
    }
}
```
A) Alice  
B) name  
C) Compilation error  
D) null

**Answer: A) Alice**

**Explanation**: Record accessor methods are named after the components. The `name()` method returns the value of the name component, which is "Alice". Records don't use get prefixes like traditional JavaBeans.

---

### Question 3
Which statement about records is TRUE?
A) Records can extend other classes  
B) Record fields can be modified after construction  
C) Records are implicitly final  
D) Records can be abstract

**Answer: C) Records are implicitly final**

**Explanation**: Records are implicitly final and cannot be extended. They implicitly extend `java.lang.Record`, cannot extend other classes (A is false), have final fields that cannot be modified (B is false), and cannot be abstract (D is false).

---

### Question 4
What is the result?
```java
record Range(int min, int max) {
    public Range {
        if (min > max) {
            throw new IllegalArgumentException("Invalid range");
        }
    }
}

public class Test {
    public static void main(String[] args) {
        Range r = new Range(10, 5);
    }
}
```
A) Compiles and runs successfully  
B) Compilation error  
C) IllegalArgumentException  
D) NullPointerException

**Answer: C) IllegalArgumentException**

**Explanation**: This demonstrates a compact constructor. The validation code `if (min > max)` throws an IllegalArgumentException because 10 > 5. Compact constructors are a concise way to add validation or normalization logic before the fields are assigned.

---

### Question 5
Which record declaration is INVALID?
A) `record Point(int x, int y) { }`  
B) `record Person(String name) extends Object { }`  
C) `record Circle(double radius) implements Comparable<Circle> { }`  
D) `record Box<T>(T item) { }`

**Answer: B) `record Person(String name) extends Object { }`**

**Explanation**: Records cannot explicitly extend any class because they implicitly extend `java.lang.Record`. Option A is valid (simple record), Option C is valid (records can implement interfaces), and Option D is valid (records can be generic).

---

### Question 6
What is the output?
```java
record Color(int red, int green, int blue) { }

public class Test {
    public static void main(String[] args) {
        Color c1 = new Color(255, 0, 0);
        Color c2 = new Color(255, 0, 0);
        System.out.println(c1.equals(c2));
    }
}
```
A) true  
B) false  
C) Compilation error  
D) Runtime error

**Answer: A) true**

**Explanation**: Records automatically generate an `equals()` method that compares all components. Since both Color instances have the same values for red, green, and blue (255, 0, 0), they are considered equal.

---

### Question 7
What happens when you compile this code?
```java
record Employee(int id, String name) {
    private int salary;  // Line X
}
```
A) Compiles successfully  
B) Compilation error at Line X  
C) salary is automatically initialized  
D) salary becomes a record component

**Answer: B) Compilation error at Line X**

**Explanation**: Records cannot have instance fields beyond those declared in the record header (components). All instance fields must be final and declared as components. You can only add static fields. Line X attempts to add a non-component instance field, causing a compilation error.

---

### Question 8
What is the output?
```java
record Point(int x, int y) {
    public Point() {
        this(0, 0);
    }
}

public class Test {
    public static void main(String[] args) {
        Point p = new Point();
        System.out.println(p);
    }
}
```
A) Point[x=0, y=0]  
B) Compilation error  
C) null  
D) Point[]

**Answer: A) Point[x=0, y=0]**

**Explanation**: Records can have additional constructors, but they must delegate to the canonical constructor using `this()`. The no-arg constructor calls `this(0, 0)`, which invokes the canonical constructor. The automatically generated toString() outputs "Point[x=0, y=0]".

---

### Question 9
Which is TRUE about record accessor methods?
```java
record Book(String title, int year) { }
```
A) Accessor methods are title() and year()  
B) Accessor methods are getTitle() and getYear()  
C) Accessor methods must be manually defined  
D) Records don't have accessor methods

**Answer: A) Accessor methods are title() and year()**

**Explanation**: Record accessor methods are named exactly after the components, not following the JavaBean getX() convention. For a record with components `title` and `year`, the accessor methods are `title()` and `year()`.

---

### Question 10
What is the result?
```java
abstract record Shape(String name) {  // Line X
    abstract double area();
}
```
A) Compiles successfully  
B) Compilation error at Line X  
C) Runtime error  
D) Shape can be instantiated

**Answer: B) Compilation error at Line X**

**Explanation**: Records cannot be declared abstract. They are implicitly final classes designed to be instantiated directly. Abstract classes are meant to be extended, which contradicts the purpose and design of records.

---

### Question 11
What is the output?
```java
record Person(String name, int age) {
    public int age() {
        return age + 1;  // Modified accessor
    }
}

public class Test {
    public static void main(String[] args) {
        Person p = new Person("Alice", 30);
        System.out.println(p.age());
    }
}
```
A) 30  
B) 31  
C) Compilation error  
D) Runtime error

**Answer: B) 31**

**Explanation**: You can override the automatically generated accessor methods. Here, the `age()` accessor is overridden to return `age + 1` instead of the actual age value. So for age 30, it returns 31. While possible, modifying accessors is generally discouraged as it breaks the transparency of records.

---

### Question 12
What happens with this code?
```java
record Point(int x, int y) {
    public Point(int x, int y) {
        this.x = x * 2;
        this.y = y * 2;
    }
}

public class Test {
    public static void main(String[] args) {
        Point p = new Point(5, 10);
        System.out.println(p);
    }
}
```
A) Point[x=5, y=10]  
B) Point[x=10, y=20]  
C) Compilation error  
D) Runtime error

**Answer: B) Point[x=10, y=20]**

**Explanation**: This shows an explicit canonical constructor override. Instead of using a compact constructor, this provides a full constructor that modifies the values before assignment. The x and y values are doubled, so Point(5, 10) becomes Point[x=10, y=20].

---

### Question 13
Which is a valid use of a record? (Java 21)
```java
record Point(int x, int y) { }

public class Test {
    public static void main(String[] args) {
        Object obj = new Point(10, 20);
        
        if (obj instanceof Point(int x, int y)) {  // Line X
            System.out.println(x + y);
        }
    }
}
```
A) Line X is invalid  
B) Prints 30  
C) Compilation error  
D) Prints Point[x=10, y=20]

**Answer: B) Prints 30**

**Explanation**: Java 21 supports record patterns that allow deconstructing records in instanceof checks. The pattern `Point(int x, int y)` extracts the x and y components from the Point record. The code prints 10 + 20 = 30.

---

### Question 14
What is TRUE about this record?
```java
record Config(String url, int timeout) {
    public Config {
        timeout = Math.max(timeout, 1000);
    }
}
```
A) Compact constructor cannot modify parameters  
B) Compact constructor normalizes timeout to minimum 1000  
C) This will not compile  
D) timeout must be assigned using this.timeout

**Answer: B) Compact constructor normalizes timeout to minimum 1000**

**Explanation**: Compact constructors can modify the parameter values before they're assigned to fields. This code ensures timeout is at least 1000. The assignment to fields happens automatically after the compact constructor body. You don't use `this.` in compact constructors.

---

### Question 15
What is the output?
```java
record Box<T>(T item) {
    public static <T> Box<T> empty() {
        return new Box<>(null);
    }
}

public class Test {
    public static void main(String[] args) {
        Box<String> box = Box.empty();
        System.out.println(box.item());
    }
}
```
A) null  
B) Empty box  
C) Compilation error  
D) NullPointerException

**Answer: A) null**

**Explanation**: Records can be generic and have static methods. The `empty()` static method creates a Box with null as the item. The `item()` accessor returns null, which is printed.

---

### Question 16
Which statement about record components is FALSE?
A) Components create private final fields  
B) Components must be declared in the record header  
C) Components can be modified after construction  
D) Components generate accessor methods

**Answer: C) Components can be modified after construction**

**Explanation**: Record components create private final fields that cannot be modified after construction. Records are designed for immutability. All other statements are true: components create private final fields (A), must be in the header (B), and generate accessors (D).

---

### Question 17
What is the result?
```java
record Person(String name) {
    static int count = 0;
    
    public Person {
        count++;
    }
}

public class Test {
    public static void main(String[] args) {
        new Person("Alice");
        new Person("Bob");
        System.out.println(Person.count);
    }
}
```
A) 0  
B) 1  
C) 2  
D) Compilation error

**Answer: C) 2**

**Explanation**: Records can have static fields and modify them in constructors. Each time a Person is created, the compact constructor increments the static count. After creating two Person instances, count is 2.

---

### Question 18
What happens with this code?
```java
record Circle(double radius) {
    public double radius() {
        return 0.0;  // Different value
    }
}

public class Test {
    public static void main(String[] args) {
        Circle c = new Circle(5.0);
        System.out.println(c.radius());
    }
}
```
A) 5.0  
B) 0.0  
C) Compilation error  
D) Runtime error

**Answer: B) 0.0**

**Explanation**: While you can override accessor methods in records, doing so breaks the transparency principle. Here, the `radius()` accessor is overridden to always return 0.0 instead of the actual radius value. This compiles and runs but is poor practice.

---

### Question 19
Which record declaration is VALID?
A) `record Point(int x, int y) implements Cloneable { }`  
B) `record Point(int x, int y) extends Shape { }`  
C) `record Point(final int x, int y) { }`  
D) `public record Point(int x, int y) { }`

**Answer: A and D are valid**

**Explanation**: Records can implement interfaces (A is valid), and can have access modifiers like public (D is valid). Records cannot extend classes (B is invalid). Components don't use modifiers like final explicitly (C is invalid - redundant since they're implicitly final).

---

### Question 20
What is the output?
```java
record Point(int x, int y) { }

public class Test {
    public static void main(String[] args) {
        Point p1 = new Point(10, 20);
        Point p2 = new Point(10, 20);
        System.out.println(p1.hashCode() == p2.hashCode());
    }
}
```
A) true  
B) false  
C) Compilation error  
D) Depends on JVM

**Answer: A) true**

**Explanation**: Records automatically generate a `hashCode()` method based on all components. Since p1 and p2 have identical values for all components (x=10, y=20), they produce the same hash code. This allows records to work correctly in hash-based collections.

---

## Answer Summary
1. C  2. A  3. C  4. C  5. B  
6. A  7. B  8. A  9. A  10. B  
11. B  12. B  13. B  14. B  15. A  
16. C  17. C  18. B  19. A,D  20. A
