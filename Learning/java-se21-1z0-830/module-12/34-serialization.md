# Module 12: Serialization

## Table of Contents
1. [Introduction to Serialization](#introduction-to-serialization)
2. [Serializable Interface](#serializable-interface)
3. [ObjectOutputStream and ObjectInputStream](#objectoutputstream-and-objectinputstream)
4. [transient Keyword](#transient-keyword)
5. [serialVersionUID](#serialversionuid)
6. [Custom Serialization](#custom-serialization)
7. [Externalizable Interface](#externalizable-interface)
8. [Serialization Best Practices](#serialization-best-practices)
9. [Common Serialization Issues](#common-serialization-issues)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to Serialization

**Serialization** is the process of converting an object into a byte stream for storage or transmission. **Deserialization** reconstructs the object from the byte stream.

### Use Cases

- **Persistence**: Save object state to disk
- **Network transfer**: Send objects over network
- **Caching**: Store objects in cache
- **Deep cloning**: Create copies of objects
- **Session management**: Store session data

### Serialization Process

```
Object → ObjectOutputStream → Byte Stream → File/Network
Byte Stream → ObjectInputStream → Object
```

---

## Serializable Interface

**Serializable** is a **marker interface** (no methods) indicating a class can be serialized.

### Basic Serialization

```java
import java.io.*;

// Class must implement Serializable
class Person implements Serializable {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}

public class SerializationExample {
    public static void main(String[] args) throws IOException, ClassNotFoundException {
        Person person = new Person("Alice", 30);
        
        // Serialize
        try (ObjectOutputStream oos = new ObjectOutputStream(
                new FileOutputStream("person.ser"))) {
            oos.writeObject(person);
        }
        
        // Deserialize
        try (ObjectInputStream ois = new ObjectInputStream(
                new FileInputStream("person.ser"))) {
            Person deserializedPerson = (Person) ois.readObject();
            System.out.println(deserializedPerson);  // Person{name='Alice', age=30}
        }
    }
}
```

### Serialization Requirements

```java
// ✓ Valid - all fields serializable
class Employee implements Serializable {
    private String name;      // String is Serializable
    private int salary;       // primitives are serializable
    private Address address;  // Address must be Serializable
}

class Address implements Serializable {
    private String city;
    private String country;
}

// ✗ Invalid - non-serializable field
class Manager implements Serializable {
    private String name;
    private Thread thread;  // Thread is NOT Serializable - causes exception
}
```

---

## ObjectOutputStream and ObjectInputStream

### ObjectOutputStream Methods

```java
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("objects.ser"))) {
    
    // Write object
    oos.writeObject(new Person("Bob", 25));
    
    // Write primitives
    oos.writeInt(42);
    oos.writeDouble(3.14);
    oos.writeBoolean(true);
    oos.writeChar('A');
    oos.writeLong(1000L);
    
    // Write String
    oos.writeUTF("Hello");
    
    // Flush
    oos.flush();
}
```

### ObjectInputStream Methods

```java
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("objects.ser"))) {
    
    // Read object (must cast)
    Person person = (Person) ois.readObject();
    
    // Read primitives (must read in same order as written)
    int number = ois.readInt();
    double pi = ois.readDouble();
    boolean flag = ois.readBoolean();
    char letter = ois.readChar();
    long value = ois.readLong();
    
    // Read String
    String text = ois.readUTF();
}
```

### Multiple Objects

```java
// Serialize multiple objects
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("people.ser"))) {
    oos.writeObject(new Person("Alice", 30));
    oos.writeObject(new Person("Bob", 25));
    oos.writeObject(new Person("Charlie", 35));
}

// Deserialize multiple objects
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("people.ser"))) {
    Person p1 = (Person) ois.readObject();
    Person p2 = (Person) ois.readObject();
    Person p3 = (Person) ois.readObject();
    
    System.out.println(p1);
    System.out.println(p2);
    System.out.println(p3);
}
```

### Collection Serialization

```java
import java.util.*;

List<Person> people = Arrays.asList(
    new Person("Alice", 30),
    new Person("Bob", 25)
);

// Serialize collection
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("people.ser"))) {
    oos.writeObject(people);
}

// Deserialize collection
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("people.ser"))) {
    @SuppressWarnings("unchecked")
    List<Person> deserializedPeople = (List<Person>) ois.readObject();
    deserializedPeople.forEach(System.out::println);
}
```

---

## transient Keyword

**transient** marks fields that should **not** be serialized.

### transient Fields

```java
class User implements Serializable {
    private String username;
    private transient String password;  // NOT serialized
    private int age;
    
    public User(String username, String password, int age) {
        this.username = username;
        this.password = password;
        this.age = age;
    }
    
    @Override
    public String toString() {
        return "User{username='" + username + 
               "', password='" + password + 
               "', age=" + age + "}";
    }
}

// Usage
User user = new User("alice", "secret123", 30);
System.out.println(user);  // User{username='alice', password='secret123', age=30}

// Serialize
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("user.ser"))) {
    oos.writeObject(user);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("user.ser"))) {
    User deserializedUser = (User) ois.readObject();
    System.out.println(deserializedUser);  
    // User{username='alice', password='null', age=30}
    // password is null (default value)
}
```

### transient Default Values

```java
class Data implements Serializable {
    private transient int number = 100;      // int defaults to 0
    private transient String text = "Hello"; // Object defaults to null
    private transient boolean flag = true;   // boolean defaults to false
}

// After deserialization:
// number = 0
// text = null
// flag = false
```

### static Fields

```java
class Counter implements Serializable {
    private static int count = 0;  // static fields NOT serialized
    private int id;
    
    public Counter() {
        this.id = ++count;
    }
}

// Static fields belong to CLASS, not instance
// They are NOT serialized
```

---

## serialVersionUID

**serialVersionUID** is a version control field for class compatibility during deserialization.

### Purpose

```java
class Person implements Serializable {
    // Explicit serialVersionUID
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;
}
```

### Version Compatibility

```java
// Version 1
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private int salary;
}

// Serialize object with Version 1
Employee emp = new Employee("Alice", 50000);
// ... serialize ...

// Version 2 - added field (compatible)
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;  // Same UID
    private String name;
    private int salary;
    private String department = "Unknown";  // New field with default
}

// Deserialization works!
// New field gets default value
```

### Incompatible Changes

```java
// Version 1
class Product implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private int price;
}

// Version 2 - removed field (incompatible if UID changed)
class Product implements Serializable {
    private static final long serialVersionUID = 2L;  // Changed UID!
    private String name;
    // price removed
}

// Deserialization throws InvalidClassException!
```

### Auto-Generated UID

```java
// No explicit serialVersionUID
class Person implements Serializable {
    private String name;
    private int age;
}

// JVM generates UID based on class structure
// Any change to class → different UID → InvalidClassException

// Best practice: Always declare explicit serialVersionUID
```

---

## Custom Serialization

### writeObject and readObject

```java
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private transient int salary;  // transient, but we'll serialize manually
    
    public Employee(String name, int salary) {
        this.name = name;
        this.salary = salary;
    }
    
    // Custom serialization
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.defaultWriteObject();  // Serialize non-transient fields
        oos.writeInt(salary * 2);  // Encrypt salary (simple example)
    }
    
    // Custom deserialization
    private void readObject(ObjectInputStream ois) 
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();  // Deserialize non-transient fields
        salary = ois.readInt() / 2;  // Decrypt salary
    }
    
    @Override
    public String toString() {
        return "Employee{name='" + name + "', salary=" + salary + "}";
    }
}

// Usage
Employee emp = new Employee("Alice", 50000);

// Serialize
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("emp.ser"))) {
    oos.writeObject(emp);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("emp.ser"))) {
    Employee deserializedEmp = (Employee) ois.readObject();
    System.out.println(deserializedEmp);  // Employee{name='Alice', salary=50000}
}
```

### Validation During Deserialization

```java
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    private void readObject(ObjectInputStream ois) 
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        
        // Validate after deserialization
        if (age < 0 || age > 150) {
            throw new InvalidObjectException("Invalid age: " + age);
        }
        if (name == null || name.isEmpty()) {
            throw new InvalidObjectException("Name cannot be empty");
        }
    }
}
```

---

## Externalizable Interface

**Externalizable** extends Serializable and provides complete control over serialization.

### Externalizable vs Serializable

```java
import java.io.Externalizable;

class Person implements Externalizable {
    private String name;
    private int age;
    
    // Required: public no-arg constructor
    public Person() {
    }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public void writeExternal(ObjectOutput out) throws IOException {
        out.writeUTF(name);
        out.writeInt(age);
    }
    
    @Override
    public void readExternal(ObjectInput in) throws IOException, ClassNotFoundException {
        name = in.readUTF();
        age = in.readInt();
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
}
```

### Comparison

| Feature | Serializable | Externalizable |
|---------|-------------|----------------|
| Control | Automatic | Complete manual control |
| No-arg constructor | Not required | **Required** |
| Methods | writeObject/readObject (optional) | writeExternal/readExternal (required) |
| Performance | Slower | Faster (you control what's written) |
| Default behavior | Serializes all non-transient fields | You write everything |

---

## Serialization Best Practices

### 1. Always Declare serialVersionUID

```java
class Person implements Serializable {
    private static final long serialVersionUID = 1L;  // Explicit UID
    private String name;
}
```

### 2. Use transient for Sensitive Data

```java
class User implements Serializable {
    private String username;
    private transient String password;  // Don't serialize passwords
}
```

### 3. Validate in readObject

```java
private void readObject(ObjectInputStream ois) 
        throws IOException, ClassNotFoundException {
    ois.defaultReadObject();
    // Validate state
    if (age < 0) throw new InvalidObjectException("Invalid age");
}
```

### 4. Handle Non-Serializable Fields

```java
class MyClass implements Serializable {
    private transient NonSerializableClass field;
    
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.defaultWriteObject();
        oos.writeObject(field.getSomeSerializableData());
    }
    
    private void readObject(ObjectInputStream ois) 
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        Object data = ois.readObject();
        field = new NonSerializableClass(data);
    }
}
```

### 5. Use Serialization Proxy Pattern

```java
class Period implements Serializable {
    private final Date start;
    private final Date end;
    
    public Period(Date start, Date end) {
        this.start = start;
        this.end = end;
    }
    
    // Serialization proxy
    private static class SerializationProxy implements Serializable {
        private final Date start;
        private final Date end;
        
        SerializationProxy(Period period) {
            this.start = period.start;
            this.end = period.end;
        }
        
        private Object readResolve() {
            return new Period(start, end);
        }
    }
    
    private Object writeReplace() {
        return new SerializationProxy(this);
    }
    
    private void readObject(ObjectInputStream ois) 
            throws InvalidObjectException {
        throw new InvalidObjectException("Proxy required");
    }
}
```

---

## Common Serialization Issues

### NotSerializableException

```java
class Employee implements Serializable {
    private String name;
    private Department dept;  // Department is NOT Serializable
}

// Throws NotSerializableException
```

**Solution:**
```java
class Department implements Serializable {
    private String name;
}
```

Or use `transient`:
```java
class Employee implements Serializable {
    private String name;
    private transient Department dept;  // Won't be serialized
}
```

### InvalidClassException

```java
// Serialized with version 1
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
}

// Deserialize with version 2 (different UID)
class Person implements Serializable {
    private static final long serialVersionUID = 2L;  // Changed!
    private String name;
}

// Throws InvalidClassException
```

### Object Graph Serialization

```java
class Person implements Serializable {
    private String name;
    private Person spouse;  // Circular reference
}

Person p1 = new Person("Alice");
Person p2 = new Person("Bob");
p1.spouse = p2;
p2.spouse = p1;  // Circular reference

// Serialization handles this correctly!
// Deserializes both objects and maintains references
```

---

## Summary and Exam Tips

### Key Points

- **Serializable** is a marker interface (no methods)
- Class must implement Serializable to be serialized
- **All fields** must be serializable (or transient)
- `transient` fields are **not** serialized → default values after deserialization
- `static` fields are **not** serialized (belong to class, not instance)
- `serialVersionUID` controls version compatibility
- ObjectOutputStream writes, ObjectInputStream reads
- Must read in **same order** as written
- `readObject()` can throw ClassNotFoundException

### Exam Tips

- `writeObject()` and `readObject()` must be **private**
- Externalizable requires **public no-arg constructor**
- Serializable does **not** require no-arg constructor
- `defaultWriteObject()` and `defaultReadObject()` handle default serialization
- Objects are serialized **once** even with circular references
- Parent class doesn't need to be Serializable (parent fields won't be serialized)
- Use try-with-resources for ObjectOutputStream/ObjectInputStream

---

**Previous:** [Practice Questions - NIO.2](33-practice-questions.md)  
**Next:** [Practice Questions - Serialization](34-practice-questions.md)
