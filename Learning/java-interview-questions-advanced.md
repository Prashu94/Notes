# Java Interview Questions - Advanced Concepts

## 1. What is Java Memory Model (JVM Architecture)?

**Answer:**

The JVM divides memory into several areas, each serving a specific purpose.

**JVM Architecture:**

```
┌─────────────────────────────────────────┐
│         Class Loader Subsystem          │
│  ┌────────┬───────────┬──────────────┐  │
│  │ Loading│ Linking   │ Initialization│  │
│  └────────┴───────────┴──────────────┘  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Runtime Data Areas              │
│  ┌────────────────┬──────────────────┐  │
│  │ Method Area    │  Heap            │  │
│  │ (Class data)   │  (Objects)       │  │
│  └────────────────┴──────────────────┘  │
│  ┌────────────────────────────────────┐ │
│  │ Stack  │ PC Register │ Native Stack│ │
│  │ (per thread)                        │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         Execution Engine                │
│  ┌────────┬───────────┬──────────────┐  │
│  │ Inter- │    JIT    │   Garbage    │  │
│  │ preter │ Compiler  │   Collector  │  │
│  └────────┴───────────┴──────────────┘  │
└─────────────────────────────────────────┘
```

**Memory Areas:**

**1. Method Area (Metaspace in Java 8+):**
- Stores class structures: class name, parent class, methods, variables
- Runtime constant pool
- Static variables
- Shared among all threads

**2. Heap:**
- Objects and arrays
- Shared among all threads
- Garbage collection occurs here
- Young Generation (Eden, Survivor S0, S1)
- Old Generation (Tenured)

**3. Stack (per thread):**
- Local variables
- Method call stack (stack frames)
- Partial results
- Method invocation and return
- Each thread has private stack

**4. Program Counter (PC) Register:**
- Address of current executing instruction
- Per thread

**5. Native Method Stack:**
- Native method information
- Per thread

**Memory Allocation Example:**

```java
class Employee {
    static int count = 0;     // Method Area (static)
    int id;                   // Heap (instance variable)
    String name;              // Reference in Heap, object in String Pool
    
    public Employee(int id, String name) {
        this.id = id;
        this.name = name;
        count++;
    }
    
    public void display() {
        int localVar = 10;    // Stack (local variable)
        System.out.println(name);
    }
}

// Main method
Employee emp = new Employee(1, "John");
// emp reference -> Stack
// Employee object -> Heap
// "John" string -> String Pool (Heap)
// count static variable -> Method Area
```

**Memory Configuration:**

```bash
# Heap size
java -Xms512m -Xmx2048m MyApp
# -Xms: Initial heap size
# -Xmx: Maximum heap size

# Stack size
java -Xss1m MyApp
# -Xss: Stack size per thread

# Metaspace
java -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=512m MyApp
```

**Young Generation vs Old Generation:**

| Aspect | Young Generation | Old Generation |
|--------|------------------|----------------|
| **Objects** | New objects | Long-lived objects |
| **GC** | Minor GC (frequent) | Major GC (infrequent) |
| **Speed** | Fast | Slower |
| **Areas** | Eden, S0, S1 | Tenured |

**Object Lifecycle:**

```
1. Object created -> Eden Space
2. Survived Minor GC -> Survivor Space (S0/S1)
3. Survived multiple GCs -> Old Generation
4. No longer referenced -> Garbage Collected
```

---

## 2. What is the difference between heap and stack memory?

**Answer:**

| Feature | Stack | Heap |
|---------|-------|------|
| **Purpose** | Method execution, local variables | Object storage |
| **Scope** | Method level | Application level |
| **Lifecycle** | Exists while method executes | Until garbage collected |
| **Size** | Smaller (typically 1MB) | Larger (configurable) |
| **Access Speed** | Faster | Slower |
| **Memory Management** | Automatic (LIFO) | Garbage Collector |
| **Thread Safety** | Private to thread | Shared among threads |
| **Exception** | StackOverflowError | OutOfMemoryError |
| **Storage** | Primitives, references | Objects, arrays |

**Example:**

```java
class Demo {
    public void method1() {
        int x = 10;              // Stack (primitive)
        String str = "Hello";    // Reference in Stack, object in Heap
        Employee emp = new Employee();  // Reference in Stack, object in Heap
        
        method2(x);  // x passed to stack of method2
    }
    
    public void method2(int y) {
        int z = y * 2;          // Stack (local variable)
    }
}

// Memory layout:
// Stack:
//   method1 frame: x=10, str=reference, emp=reference
//   method2 frame: y=10, z=20
// Heap:
//   "Hello" String object
//   Employee object
```

**Stack Frame:**

```java
public void calculate(int a, int b) {
    int result = a + b;
    System.out.println(result);
}

// Stack Frame for this method:
// ┌─────────────────┐
// │ Local Variables │
// │  a = 5          │
// │  b = 10         │
// │  result = 15    │
// ├─────────────────┤
// │ Operand Stack   │
// ├─────────────────┤
// │ Frame Data      │
// │ (return address)│
// └─────────────────┘
```

**StackOverflowError:**

```java
// Infinite recursion
public void recursiveMethod() {
    recursiveMethod();  // No base case
}
// Throws StackOverflowError when stack memory exhausted
```

**OutOfMemoryError:**

```java
// Creating too many objects
List<byte[]> list = new ArrayList<>();
while (true) {
    list.add(new byte[1024 * 1024]);  // 1MB each
}
// Throws OutOfMemoryError: Java heap space
```

**Pass by Value (Stack):**

```java
public void modifyPrimitive(int x) {
    x = 20;  // Modifies copy on stack
}

public void modifyObject(Employee emp) {
    emp.setName("John");  // Modifies object in heap
    emp = new Employee(); // Only changes local reference
}

int num = 10;
modifyPrimitive(num);
System.out.println(num);  // 10 (unchanged)

Employee employee = new Employee("Alice");
modifyObject(employee);
System.out.println(employee.getName());  // John (modified)
```

---

## 3. What is reflection in Java?

**Answer:**

Reflection is the ability to inspect and manipulate classes, methods, fields, and constructors at runtime.

**Reflection API (java.lang.reflect):**
- Class
- Method
- Field
- Constructor
- Modifier

**Getting Class Object:**

```java
// 1. Using .class
Class<?> clazz1 = String.class;

// 2. Using getClass()
String str = "Hello";
Class<?> clazz2 = str.getClass();

// 3. Using Class.forName()
Class<?> clazz3 = Class.forName("java.lang.String");
```

**Inspecting Class:**

```java
class Employee {
    private int id;
    public String name;
    
    public Employee() {}
    public Employee(int id, String name) {
        this.id = id;
        this.name = name;
    }
    
    public void display() {
        System.out.println(name);
    }
    
    private void secretMethod() {
        System.out.println("Secret");
    }
}

// Get class information
Class<?> clazz = Employee.class;

// Class name
System.out.println(clazz.getName());  // Employee
System.out.println(clazz.getSimpleName());  // Employee

// Package
System.out.println(clazz.getPackage());

// Modifiers
int modifiers = clazz.getModifiers();
System.out.println(Modifier.isPublic(modifiers));

// Parent class
Class<?> superClass = clazz.getSuperclass();

// Interfaces
Class<?>[] interfaces = clazz.getInterfaces();
```

**Working with Fields:**

```java
// Get all public fields
Field[] publicFields = clazz.getFields();

// Get all fields (including private)
Field[] allFields = clazz.getDeclaredFields();

// Get specific field
Field nameField = clazz.getDeclaredField("name");
Field idField = clazz.getDeclaredField("id");

// Access private field
Employee emp = new Employee(1, "John");
idField.setAccessible(true);  // Bypass private access
int id = (int) idField.get(emp);
System.out.println(id);  // 1

// Modify private field
idField.set(emp, 2);
```

**Working with Methods:**

```java
// Get all public methods
Method[] publicMethods = clazz.getMethods();

// Get all methods (including private)
Method[] allMethods = clazz.getDeclaredMethods();

// Get specific method
Method displayMethod = clazz.getMethod("display");

// Invoke method
Employee emp = new Employee(1, "John");
displayMethod.invoke(emp);  // Prints: John

// Invoke private method
Method secretMethod = clazz.getDeclaredMethod("secretMethod");
secretMethod.setAccessible(true);
secretMethod.invoke(emp);  // Prints: Secret

// Method with parameters
Method setNameMethod = clazz.getMethod("setName", String.class);
setNameMethod.invoke(emp, "Alice");
```

**Working with Constructors:**

```java
// Get all constructors
Constructor<?>[] constructors = clazz.getDeclaredConstructors();

// Get specific constructor
Constructor<?> constructor = clazz.getConstructor(int.class, String.class);

// Create instance using reflection
Employee emp = (Employee) constructor.newInstance(1, "John");

// Default constructor
Constructor<?> defaultConstructor = clazz.getConstructor();
Employee emp2 = (Employee) defaultConstructor.newInstance();
```

**Creating Proxy:**

```java
interface Calculator {
    int add(int a, int b);
    int subtract(int a, int b);
}

// Create dynamic proxy
Calculator calculator = (Calculator) Proxy.newProxyInstance(
    Calculator.class.getClassLoader(),
    new Class<?>[] { Calculator.class },
    (proxy, method, args) -> {
        System.out.println("Method called: " + method.getName());
        
        if (method.getName().equals("add")) {
            return (int) args[0] + (int) args[1];
        } else if (method.getName().equals("subtract")) {
            return (int) args[0] - (int) args[1];
        }
        return null;
    }
);

System.out.println(calculator.add(5, 3));       // 8
System.out.println(calculator.subtract(5, 3));  // 2
```

**Use Cases:**
- Dependency Injection (Spring, Guice)
- ORM frameworks (Hibernate)
- Testing frameworks (JUnit, Mockito)
- Serialization/Deserialization
- IDE auto-completion
- Debugging tools

**Disadvantages:**
- Performance overhead
- Security restrictions
- Breaks encapsulation
- Complex code
- Compile-time type checking lost

---

## 4. What is serialization and deserialization?

**Answer:**

**Serialization:** Converting object to byte stream for storage/transmission
**Deserialization:** Converting byte stream back to object

**Serializable Interface:**

```java
import java.io.*;

class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private int id;
    private String name;
    private transient String password;  // Not serialized
    private static int count = 0;       // Not serialized
    
    public Employee(int id, String name, String password) {
        this.id = id;
        this.name = name;
        this.password = password;
    }
}

// Serialization
Employee emp = new Employee(1, "John", "secret123");

try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("employee.ser"))) {
    oos.writeObject(emp);
}

// Deserialization
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("employee.ser"))) {
    Employee emp2 = (Employee) ois.readObject();
    System.out.println(emp2.getName());  // John
    System.out.println(emp2.getPassword());  // null (transient)
}
```

**serialVersionUID:**

```java
// Explicit version ID
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    
    // If class structure changes, increment version
    // to prevent InvalidClassException
}

// Without explicit serialVersionUID, JVM generates one
// Changes to class structure will break deserialization
```

**Transient Keyword:**

```java
class User implements Serializable {
    private String username;
    private transient String password;  // Not serialized
    
    // Password won't be saved during serialization
}
```

**Static Fields:**

```java
class Example implements Serializable {
    private int instanceVar = 10;
    private static int staticVar = 20;
    
    // Only instanceVar is serialized
    // staticVar belongs to class, not object
}
```

**Custom Serialization:**

```java
class Employee implements Serializable {
    private int id;
    private String name;
    private transient String password;
    
    // Custom serialization
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.defaultWriteObject();  // Serialize non-transient fields
        
        // Encrypt password before serialization
        String encrypted = encrypt(password);
        oos.writeObject(encrypted);
    }
    
    // Custom deserialization
    private void readObject(ObjectInputStream ois) 
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();  // Deserialize non-transient fields
        
        // Decrypt password after deserialization
        String encrypted = (String) ois.readObject();
        password = decrypt(encrypted);
    }
}
```

**Externalizable Interface:**

```java
import java.io.*;

class Employee implements Externalizable {
    private int id;
    private String name;
    
    // Must have public no-arg constructor
    public Employee() {}
    
    public Employee(int id, String name) {
        this.id = id;
        this.name = name;
    }
    
    @Override
    public void writeExternal(ObjectOutput out) throws IOException {
        // Complete control over serialization
        out.writeInt(id);
        out.writeUTF(name);
    }
    
    @Override
    public void readExternal(ObjectInput in) 
            throws IOException, ClassNotFoundException {
        // Complete control over deserialization
        id = in.readInt();
        name = in.readUTF();
    }
}
```

**Serializable vs Externalizable:**

| Feature | Serializable | Externalizable |
|---------|--------------|----------------|
| **Control** | Automatic | Manual |
| **Methods** | Optional (writeObject/readObject) | Mandatory (writeExternal/readExternal) |
| **Constructor** | Not required | Public no-arg required |
| **Performance** | Slower | Faster |
| **Ease** | Easy | Complex |

**Inheritance and Serialization:**

```java
// Parent not serializable
class Parent {
    int x = 10;
    
    Parent() {
        System.out.println("Parent constructor");
    }
}

// Child serializable
class Child extends Parent implements Serializable {
    int y = 20;
}

// When deserializing Child:
// - y is restored from stream
// - x is initialized by Parent's no-arg constructor
// - Parent constructor must be accessible
```

**Collections Serialization:**

```java
// ArrayList, HashMap, etc. are Serializable
List<Employee> employees = new ArrayList<>();
employees.add(new Employee(1, "John"));
employees.add(new Employee(2, "Alice"));

// Serialize entire list
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("employees.ser"))) {
    oos.writeObject(employees);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("employees.ser"))) {
    List<Employee> list = (List<Employee>) ois.readObject();
}
```

**Use Cases:**
- Saving object state to file
- Session management in web applications
- Deep cloning objects
- RMI (Remote Method Invocation)
- Caching
- Message passing in distributed systems

**Alternatives:**
- JSON (Jackson, Gson)
- XML (JAXB)
- Protocol Buffers
- Avro

---

## 5. What is the difference between `==`, `.equals()`, and `.hashCode()`?

**Answer:**

**Detailed Explanation:**

**1. `==` Operator:**
- Compares references (memory addresses) for objects
- Compares values for primitives
- Cannot be overridden

```java
String s1 = new String("Hello");
String s2 = new String("Hello");
String s3 = s1;

System.out.println(s1 == s2);  // false (different objects)
System.out.println(s1 == s3);  // true (same reference)

int a = 10, b = 10;
System.out.println(a == b);    // true (value comparison)
```

**2. `.equals()` Method:**
- Compares content/values
- Can be overridden
- Default implementation uses `==`

```java
String s1 = new String("Hello");
String s2 = new String("Hello");

System.out.println(s1.equals(s2));  // true (same content)
```

**3. `.hashCode()` Method:**
- Returns integer hash code
- Used by hash-based collections (HashMap, HashSet)
- Must be consistent with equals()

**Contract Between equals() and hashCode():**

1. If `a.equals(b)` is true, then `a.hashCode() == b.hashCode()` must be true
2. If `a.hashCode() == b.hashCode()`, `a.equals(b)` may or may not be true
3. If `a.equals(b)` is false, hash codes can be same or different

**Proper Implementation:**

```java
class Employee {
    private int id;
    private String name;
    private String department;
    
    public Employee(int id, String name, String department) {
        this.id = id;
        this.name = name;
        this.department = department;
    }
    
    @Override
    public boolean equals(Object obj) {
        // 1. Check if same reference
        if (this == obj) {
            return true;
        }
        
        // 2. Check if null or different class
        if (obj == null || getClass() != obj.getClass()) {
            return false;
        }
        
        // 3. Cast and compare fields
        Employee employee = (Employee) obj;
        return id == employee.id &&
               Objects.equals(name, employee.name) &&
               Objects.equals(department, employee.department);
    }
    
    @Override
    public int hashCode() {
        // Use Objects.hash() for convenience
        return Objects.hash(id, name, department);
    }
}
```

**Why Both Methods Are Important:**

```java
// HashMap internally uses hashCode() and equals()
Map<Employee, String> map = new HashMap<>();

Employee e1 = new Employee(1, "John", "IT");
Employee e2 = new Employee(1, "John", "IT");

map.put(e1, "Manager");

// Without proper hashCode/equals
System.out.println(map.get(e2));  // null

// With proper hashCode/equals
System.out.println(map.get(e2));  // Manager
```

**Bad Implementation Example:**

```java
class BadEmployee {
    private int id;
    
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof BadEmployee)) return false;
        BadEmployee other = (BadEmployee) obj;
        return this.id == other.id;
    }
    
    // WRONG: Not overriding hashCode()
    // Violates contract: equal objects may have different hash codes
}

// Problem in HashMap
Set<BadEmployee> set = new HashSet<>();
BadEmployee e1 = new BadEmployee(1);
BadEmployee e2 = new BadEmployee(1);

set.add(e1);
set.add(e2);  // Added twice! (different hash codes)
System.out.println(set.size());  // 2 (should be 1)
```

**Hash Collision:**

```java
// Good hash function distributes values evenly
class GoodHash {
    private int id;
    private String name;
    
    @Override
    public int hashCode() {
        return Objects.hash(id, name);  // Good distribution
    }
}

// Bad hash function causes many collisions
class BadHash {
    private int id;
    
    @Override
    public int hashCode() {
        return 1;  // All objects have same hash code!
    }
}
```

**String Pool Example:**

```java
// String literals use String Pool
String s1 = "Hello";
String s2 = "Hello";
System.out.println(s1 == s2);        // true (same object in pool)
System.out.println(s1.equals(s2));   // true

// new String() creates new object
String s3 = new String("Hello");
System.out.println(s1 == s3);        // false (different objects)
System.out.println(s1.equals(s3));   // true

// intern() returns pooled string
String s4 = s3.intern();
System.out.println(s1 == s4);        // true (pooled)
```

---

## 6. What is the difference between ClassNotFoundException and NoClassDefFoundError?

**Answer:**

**ClassNotFoundException:**
- Checked exception
- Occurs at runtime when loading class dynamically
- Class not found in classpath
- Thrown by methods like `Class.forName()`, `ClassLoader.loadClass()`

```java
try {
    Class.forName("com.example.NonExistentClass");
} catch (ClassNotFoundException e) {
    System.out.println("Class not found: " + e.getMessage());
}
```

**NoClassDefFoundError:**
- Error (not exception)
- Occurs at runtime when JVM can't find class definition
- Class was available at compile time but not at runtime
- Usually due to class file deletion or classpath issues

```java
// At compile time, MyClass exists
MyClass obj = new MyClass();  // Compiles fine

// At runtime, MyClass.class is missing from classpath
// Throws NoClassDefFoundError
```

**Detailed Comparison:**

| Feature | ClassNotFoundException | NoClassDefFoundError |
|---------|----------------------|---------------------|
| **Type** | Checked Exception | Error |
| **Package** | java.lang | java.lang |
| **Cause** | Class not in classpath | Class present at compile time but missing at runtime |
| **When** | Dynamic class loading | Normal class usage |
| **Methods** | Class.forName(), loadClass() | new keyword, static method call |
| **Recovery** | Catchable, recoverable | Rarely recoverable |

**Scenarios:**

**ClassNotFoundException:**

```java
// 1. JDBC driver loading
try {
    Class.forName("com.mysql.jdbc.Driver");
} catch (ClassNotFoundException e) {
    e.printStackTrace();
}

// 2. Custom class loader
ClassLoader loader = MyClass.class.getClassLoader();
try {
    Class<?> clazz = loader.loadClass("com.example.MyClass");
} catch (ClassNotFoundException e) {
    e.printStackTrace();
}

// 3. Reflection
try {
    Class<?> clazz = Class.forName("java.util.ArrayList");
    Object instance = clazz.newInstance();
} catch (ClassNotFoundException e) {
    e.printStackTrace();
}
```

**NoClassDefFoundError:**

```java
// Scenario 1: Static initializer failure
class Example {
    static {
        // Exception in static block
        throw new RuntimeException("Initialization failed");
    }
}

// First access throws ExceptionInInitializerError
// Subsequent access throws NoClassDefFoundError
Example obj = new Example();

// Scenario 2: Missing dependency
// MyClass depends on HelperClass
// HelperClass.class deleted from classpath
MyClass obj = new MyClass();  // NoClassDefFoundError

// Scenario 3: Version mismatch
// Compiled with Java 11, running on Java 8
// Uses Java 11 specific class
MyClass obj = new MyClass();  // NoClassDefFoundError
```

**How to Resolve:**

**ClassNotFoundException:**
- Add missing JAR to classpath
- Check class name spelling
- Verify package structure
- Ensure class is compiled

```bash
# Add to classpath
java -cp .:mylib.jar com.example.Main
```

**NoClassDefFoundError:**
- Check classpath at runtime
- Verify all dependencies present
- Check static initializers for exceptions
- Verify Java version compatibility
- Check for circular dependencies

```bash
# Print classpath
java -verbose:class com.example.Main

# Check class loading
java -XX:+TraceClassLoading com.example.Main
```

---

## 7. What are design patterns? Explain Singleton, Factory, and Builder patterns.

**Answer:**

Design patterns are reusable solutions to common software design problems.

**Types:**
1. Creational (object creation)
2. Structural (object composition)
3. Behavioral (object interaction)

---

### **1. Singleton Pattern**

Ensures only one instance of a class exists.

**Eager Initialization:**

```java
class Singleton {
    // Instance created at class loading
    private static final Singleton INSTANCE = new Singleton();
    
    private Singleton() {
        // Private constructor
    }
    
    public static Singleton getInstance() {
        return INSTANCE;
    }
}
```

**Lazy Initialization (Thread-safe):**

```java
class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {  // Double-check
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

**Bill Pugh Singleton (Best):**

```java
class Singleton {
    private Singleton() {}
    
    // Inner static class - loaded on first access
    private static class SingletonHelper {
        private static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return SingletonHelper.INSTANCE;
    }
}
```

**Enum Singleton (Thread-safe, Serialization-safe):**

```java
enum Singleton {
    INSTANCE;
    
    public void doSomething() {
        System.out.println("Singleton method");
    }
}

// Usage
Singleton.INSTANCE.doSomething();
```

---

### **2. Factory Pattern**

Creates objects without specifying exact class.

**Simple Factory:**

```java
// Product interface
interface Shape {
    void draw();
}

// Concrete products
class Circle implements Shape {
    @Override
    public void draw() {
        System.out.println("Drawing Circle");
    }
}

class Rectangle implements Shape {
    @Override
    public void draw() {
        System.out.println("Drawing Rectangle");
    }
}

class Triangle implements Shape {
    @Override
    public void draw() {
        System.out.println("Drawing Triangle");
    }
}

// Factory
class ShapeFactory {
    public static Shape getShape(String shapeType) {
        if (shapeType == null) {
            return null;
        }
        
        switch (shapeType.toUpperCase()) {
            case "CIRCLE":
                return new Circle();
            case "RECTANGLE":
                return new Rectangle();
            case "TRIANGLE":
                return new Triangle();
            default:
                throw new IllegalArgumentException("Unknown shape: " + shapeType);
        }
    }
}

// Usage
Shape shape1 = ShapeFactory.getShape("CIRCLE");
shape1.draw();  // Drawing Circle

Shape shape2 = ShapeFactory.getShape("RECTANGLE");
shape2.draw();  // Drawing Rectangle
```

**Factory Method Pattern:**

```java
// Abstract factory
abstract class ShapeFactory {
    abstract Shape createShape();
    
    public void renderShape() {
        Shape shape = createShape();
        shape.draw();
    }
}

// Concrete factories
class CircleFactory extends ShapeFactory {
    @Override
    Shape createShape() {
        return new Circle();
    }
}

class RectangleFactory extends ShapeFactory {
    @Override
    Shape createShape() {
        return new Rectangle();
    }
}

// Usage
ShapeFactory factory = new CircleFactory();
factory.renderShape();  // Drawing Circle
```

**Abstract Factory Pattern:**

```java
// Abstract products
interface Button {
    void paint();
}

interface Checkbox {
    void paint();
}

// Windows products
class WindowsButton implements Button {
    @Override
    public void paint() {
        System.out.println("Windows button");
    }
}

class WindowsCheckbox implements Checkbox {
    @Override
    public void paint() {
        System.out.println("Windows checkbox");
    }
}

// Mac products
class MacButton implements Button {
    @Override
    public void paint() {
        System.out.println("Mac button");
    }
}

class MacCheckbox implements Checkbox {
    @Override
    public void paint() {
        System.out.println("Mac checkbox");
    }
}

// Abstract factory
interface GUIFactory {
    Button createButton();
    Checkbox createCheckbox();
}

// Concrete factories
class WindowsFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new WindowsButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new WindowsCheckbox();
    }
}

class MacFactory implements GUIFactory {
    @Override
    public Button createButton() {
        return new MacButton();
    }
    
    @Override
    public Checkbox createCheckbox() {
        return new MacCheckbox();
    }
}

// Usage
GUIFactory factory = new WindowsFactory();
Button button = factory.createButton();
Checkbox checkbox = factory.createCheckbox();
button.paint();     // Windows button
checkbox.paint();   // Windows checkbox
```

---

### **3. Builder Pattern**

Constructs complex objects step by step.

**Without Builder (Telescoping Constructor):**

```java
class Pizza {
    private String size;
    private boolean cheese;
    private boolean pepperoni;
    private boolean bacon;
    private boolean mushrooms;
    
    // Telescoping constructors - hard to maintain
    public Pizza(String size) {
        this(size, false, false, false, false);
    }
    
    public Pizza(String size, boolean cheese) {
        this(size, cheese, false, false, false);
    }
    
    public Pizza(String size, boolean cheese, boolean pepperoni) {
        this(size, cheese, pepperoni, false, false);
    }
    
    // ... more constructors
}
```

**With Builder:**

```java
class Pizza {
    private final String size;
    private final boolean cheese;
    private final boolean pepperoni;
    private final boolean bacon;
    private final boolean mushrooms;
    
    private Pizza(Builder builder) {
        this.size = builder.size;
        this.cheese = builder.cheese;
        this.pepperoni = builder.pepperoni;
        this.bacon = builder.bacon;
        this.mushrooms = builder.mushrooms;
    }
    
    public static class Builder {
        // Required parameters
        private final String size;
        
        // Optional parameters - default values
        private boolean cheese = false;
        private boolean pepperoni = false;
        private boolean bacon = false;
        private boolean mushrooms = false;
        
        public Builder(String size) {
            this.size = size;
        }
        
        public Builder cheese(boolean value) {
            cheese = value;
            return this;
        }
        
        public Builder pepperoni(boolean value) {
            pepperoni = value;
            return this;
        }
        
        public Builder bacon(boolean value) {
            bacon = value;
            return this;
        }
        
        public Builder mushrooms(boolean value) {
            mushrooms = value;
            return this;
        }
        
        public Pizza build() {
            return new Pizza(this);
        }
    }
    
    @Override
    public String toString() {
        return "Pizza [size=" + size + ", cheese=" + cheese + 
               ", pepperoni=" + pepperoni + ", bacon=" + bacon + 
               ", mushrooms=" + mushrooms + "]";
    }
}

// Usage - Fluent API
Pizza pizza = new Pizza.Builder("Large")
    .cheese(true)
    .pepperoni(true)
    .bacon(true)
    .build();

System.out.println(pizza);
// Pizza [size=Large, cheese=true, pepperoni=true, bacon=true, mushrooms=false]
```

**Real-world Example (StringBuilder):**

```java
// StringBuilder uses Builder pattern
StringBuilder builder = new StringBuilder();
String result = builder
    .append("Hello")
    .append(" ")
    .append("World")
    .toString();
```

**Benefits:**
- **Singleton**: Controlled instance creation, global access
- **Factory**: Decoupling, flexibility, single responsibility
- **Builder**: Readable code, immutable objects, flexible construction

---

## 8. What is the difference between fail-fast and fail-safe iterators?

**Answer:**

**Fail-Fast Iterators:**
- Throw `ConcurrentModificationException` if collection modified during iteration
- Used by: ArrayList, HashMap, HashSet
- Use original collection directly

**Fail-Safe Iterators:**
- Don't throw exception when modified
- Work on clone/copy of collection
- Used by: ConcurrentHashMap, CopyOnWriteArrayList
- May not reflect latest changes

**Examples:**

**Fail-Fast (ArrayList):**

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    System.out.println(element);
    
    // Modification during iteration
    list.add("D");  // Throws ConcurrentModificationException
}
```

**Correct Way (Using Iterator's remove):**

```java
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    if (element.equals("B")) {
        iterator.remove();  // Safe removal
    }
}

System.out.println(list);  // [A, C]
```

**Fail-Safe (ConcurrentHashMap):**

```java
Map<String, Integer> map = new ConcurrentHashMap<>();
map.put("A", 1);
map.put("B", 2);
map.put("C", 3);

Iterator<String> iterator = map.keySet().iterator();
while (iterator.hasNext()) {
    String key = iterator.next();
    System.out.println(key);
    
    // Modification allowed - no exception
    map.put("D", 4);
}

// D may or may not be printed (depending on timing)
```

**Fail-Safe (CopyOnWriteArrayList):**

```java
List<String> list = new CopyOnWriteArrayList<>(Arrays.asList("A", "B", "C"));

Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String element = iterator.next();
    System.out.println(element);
    
    // Modification allowed - works on copy
    list.add("D");
}

// Prints: A, B, C (not D, as iterator works on snapshot)
System.out.println(list);  // [A, B, C, D, D, D]
```

---

## 9. Explain Java 8+ Optional class and its benefits.

**Answer:**

Optional is a container object that may or may not contain a non-null value.

**Creating Optional:**

```java
// Empty Optional
Optional<String> empty = Optional.empty();

// Optional with value
Optional<String> opt1 = Optional.of("Hello");

// Optional that may be null
Optional<String> opt2 = Optional.ofNullable("Hello");
Optional<String> opt3 = Optional.ofNullable(null);  // OK
```

**Before Optional:**

```java
// Null checking hell
public String getCity(User user) {
    if (user != null) {
        Address address = user.getAddress();
        if (address != null) {
            City city = address.getCity();
            if (city != null) {
                return city.getName();
            }
        }
    }
    return "Unknown";
}
```

**With Optional:**

```java
public String getCity(User user) {
    return Optional.ofNullable(user)
        .map(User::getAddress)
        .map(Address::getCity)
        .map(City::getName)
        .orElse("Unknown");
}
```

---

## 10. What is the difference between synchronized and concurrent collections?

**Answer:**

**Synchronized Collections:**
- Created using `Collections.synchronizedXxx()` methods
- Entire collection synchronized (lock on whole object)
- Poor performance in multi-threaded environment

**Concurrent Collections:**
- Designed for high concurrency
- Fine-grained locking or lock-free algorithms
- Better performance
- Available since Java 5 (java.util.concurrent)

```java
// Synchronized
Map<String, Integer> syncMap = Collections.synchronizedMap(new HashMap<>());

// Concurrent
Map<String, Integer> concurrentMap = new ConcurrentHashMap<>();
```
