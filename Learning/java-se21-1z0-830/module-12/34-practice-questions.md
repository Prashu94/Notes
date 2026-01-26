# Module 12: Practice Questions - Serialization

## Questions (20)

---

### Question 1
```java
class Person {
    private String name;
}

Person person = new Person("Alice");
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("person.ser"))) {
    oos.writeObject(person);
}
```
What happens?

**A)** Works fine  
**B)** NotSerializableException  
**C)** Compilation error  
**D)** IOException

**Answer: B)**

**Explanation:** `Person` doesn't implement `Serializable`. Throws **NotSerializableException**.

---

### Question 2
```java
class User implements Serializable {
    private String username;
    private transient String password;
}

User user = new User("alice", "secret");
// Serialize and deserialize
```
After deserialization, what is `password`?

**A)** "secret"  
**B)** null  
**C)** ""  
**D)** Compilation error

**Answer: B)**

**Explanation:** `transient` fields are NOT serialized. Object reference defaults to **null**.

---

### Question 3
```java
class Counter implements Serializable {
    private static int count = 100;
}
```
After serialization and deserialization, what is `count`?

**A)** 100  
**B)** 0  
**C)** Current value in JVM  
**D)** null

**Answer: C)**

**Explanation:** `static` fields are NOT serialized. They retain **current value** in JVM.

---

### Question 4
```java
class Data implements Serializable {
    private transient int value = 50;
}
```
After deserialization, what is `value`?

**A)** 50  
**B)** 0  
**C)** null  
**D)** Undefined

**Answer: B)**

**Explanation:** `transient` fields not serialized. `int` defaults to **0** (not field initializer value).

---

### Question 5
```java
class Person implements Serializable {
    // No serialVersionUID declared
}
```
What happens if you add a field and deserialize old data?

**A)** Works fine  
**B)** InvalidClassException  
**C)** New field gets default value  
**D)** Compilation error

**Answer: B)**

**Explanation:** Without explicit `serialVersionUID`, JVM generates one. Class change → different UID → **InvalidClassException**.

---

### Question 6
```java
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("data.ser"))) {
    oos.writeInt(100);
    oos.writeObject("Hello");
}

try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("data.ser"))) {
    String text = (String) ois.readObject();
    int number = ois.readInt();
}
```
What happens?

**A)** Works correctly  
**B)** ClassCastException  
**C)** IOException  
**D)** Reads wrong values

**Answer: B)**

**Explanation:** Must read in **same order** as written. Reading String first when int was written causes **ClassCastException**.

---

### Question 7
```java
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.writeUTF(name);
    }
}
```
What's wrong?

**A)** Nothing  
**B)** Should call defaultWriteObject()  
**C)** writeObject should be public  
**D)** Compilation error

**Answer: B)**

**Explanation:** Should call `defaultWriteObject()` first to serialize non-transient fields.

```java
private void writeObject(ObjectOutputStream oos) throws IOException {
    oos.defaultWriteObject();  // First!
    // Then custom serialization
}
```

---

### Question 8
```java
class Person implements Externalizable {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
}
```
What happens during deserialization?

**A)** Works fine  
**B)** InvalidClassException  
**C)** NullPointerException  
**D)** Compilation error

**Answer: B)**

**Explanation:** `Externalizable` requires **public no-arg constructor**. Missing constructor causes **InvalidClassException**.

---

### Question 9
```java
class Product implements Serializable {
    private String name;
    private double price;
}

List<Product> products = Arrays.asList(
    new Product("A", 10.0),
    new Product("B", 20.0)
);

try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("products.ser"))) {
    oos.writeObject(products);
}
```
Can you serialize a List?

**A)** Yes  
**B)** No - List not Serializable  
**C)** Only with custom serialization  
**D)** Depends on implementation

**Answer: A)**

**Explanation:** List implementations (ArrayList, LinkedList) are **Serializable** if elements are Serializable.

---

### Question 10
```java
class Person implements Serializable {
    private String name;
    private Person friend;
}

Person p1 = new Person("Alice");
Person p2 = new Person("Bob");
p1.friend = p2;
p2.friend = p1;  // Circular reference

// Serialize p1
```
What happens?

**A)** StackOverflowError  
**B)** Works fine - serializes both objects  
**C)** Infinite loop  
**D)** NotSerializableException

**Answer: B)**

**Explanation:** Serialization handles circular references. Each object serialized **once**.

---

### Question 11
```java
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
}
```
What is `serialVersionUID`?

**A)** Unique employee ID  
**B)** Version control for class compatibility  
**C)** Object ID  
**D)** Random number

**Answer: B)**

**Explanation:** `serialVersionUID` ensures **class compatibility** during deserialization.

---

### Question 12
```java
class Parent {
    private String parentField = "parent";
}

class Child extends Parent implements Serializable {
    private String childField = "child";
}
```
What is serialized?

**A)** Both parentField and childField  
**B)** Only childField  
**C)** Only parentField  
**D)** Neither

**Answer: B)**

**Explanation:** Parent doesn't implement Serializable. Only **childField** is serialized.

---

### Question 13
```java
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("obj.ser"))) {
    oos.writeObject("Hello");
    oos.writeObject(42);
}
```
Can you serialize primitive values with writeObject()?

**A)** No - use writeInt()  
**B)** Yes - auto-boxed  
**C)** Compilation error  
**D)** Only with Externalizable

**Answer: B)**

**Explanation:** Primitives are **auto-boxed** to wrapper classes (Integer, etc.) which are Serializable.

---

### Question 14
```java
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    
    private void readObject(ObjectInputStream ois) 
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
        if (name == null) {
            throw new InvalidObjectException("Name is null");
        }
    }
}
```
What is the purpose of this readObject()?

**A)** Custom deserialization  
**B)** Validation after deserialization  
**C)** Performance optimization  
**D)** Encryption

**Answer: B)**

**Explanation:** `readObject()` **validates** deserialized state to ensure object integrity.

---

### Question 15
```java
class Data implements Serializable {
    private transient Thread thread;
}
```
Why is `thread` transient?

**A)** For performance  
**B)** Thread is not Serializable  
**C)** To save memory  
**D)** Thread is deprecated

**Answer: B)**

**Explanation:** `Thread` is **not Serializable**. Must mark transient to avoid NotSerializableException.

---

### Question 16
```java
class Person implements Serializable {
    private String name;
    
    private void writeObject(ObjectOutputStream oos) throws IOException {
        oos.defaultWriteObject();
    }
    
    private void readObject(ObjectInputStream ois) 
            throws IOException, ClassNotFoundException {
        ois.defaultReadObject();
    }
}
```
What access modifier must writeObject/readObject have?

**A)** public  
**B)** protected  
**C)** private  
**D)** default (package-private)

**Answer: C)**

**Explanation:** `writeObject()` and `readObject()` must be **private**.

---

### Question 17
```java
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("obj.ser"))) {
    Object obj = ois.readObject();
}
```
What exception can `readObject()` throw (besides IOException)?

**A)** InstantiationException  
**B)** ClassNotFoundException  
**C)** NoSuchMethodException  
**D)** IllegalAccessException

**Answer: B)**

**Explanation:** `readObject()` throws **ClassNotFoundException** if class not found.

---

### Question 18
```java
class Employee implements Externalizable {
    private String name;
    
    public Employee() {}
    
    @Override
    public void writeExternal(ObjectOutput out) throws IOException {
        out.writeUTF(name);
    }
    
    @Override
    public void readExternal(ObjectInput in) 
            throws IOException, ClassNotFoundException {
        name = in.readUTF();
    }
}
```
What's the advantage of Externalizable over Serializable?

**A)** Easier to use  
**B)** Complete control and better performance  
**C)** No constructor needed  
**D)** Automatic serialization

**Answer: B)**

**Explanation:** `Externalizable` provides **complete control** over serialization for better performance.

---

### Question 19
```java
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private int age;
}

// Version 1 serialized

class Person implements Serializable {
    private static final long serialVersionUID = 1L;  // Same UID
    private String name;
    private int age;
    private String email = "unknown@example.com";  // New field
}

// Deserialize Version 1 data
```
What happens to `email`?

**A)** null  
**B)** "unknown@example.com"  
**C)** Exception  
**D)** Compilation error

**Answer: B)**

**Explanation:** New field with default value. Deserialization assigns **default value**: "unknown@example.com".

---

### Question 20
```java
class Data implements Serializable {
    private int value;
    
    // No-arg constructor
    public Data() {
        value = 100;
    }
    
    public Data(int value) {
        this.value = value;
    }
}

Data data = new Data(50);
// Serialize and deserialize
```
After deserialization, what is `value`?

**A)** 100 (no-arg constructor called)  
**B)** 50 (serialized value)  
**C)** 0 (default value)  
**D)** Undefined

**Answer: B)**

**Explanation:** **Serializable** does NOT call constructor. Deserializes **field values**: 50.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master serialization.
- **15-17 correct**: Good understanding. Review transient and serialVersionUID.
- **12-14 correct**: Fair grasp. Study Serializable vs Externalizable.
- **Below 12**: Need more practice. Review all serialization concepts.

---

**Module 12 Complete!**

**Previous:** [Theory - Serialization](34-serialization.md)  
**Next:** [Module 13 - Modules and Packaging](../module-13/35-modules.md)
