# Module 12: I/O Streams - Reading and Writing Data

## Table of Contents
1. [Introduction to I/O](#introduction-to-io)
2. [Byte Streams](#byte-streams)
3. [Character Streams](#character-streams)
4. [Buffered Streams](#buffered-streams)
5. [Data Streams](#data-streams)
6. [Object Streams](#object-streams)
7. [Console I/O](#console-io)
8. [File Operations](#file-operations)
9. [Try-with-Resources](#try-with-resources)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to I/O

**I/O (Input/Output)** handles reading from and writing to external sources (files, network, console).

### Stream Hierarchy

```
Byte Streams (binary data):
- InputStream/OutputStream (abstract base classes)
  - FileInputStream/FileOutputStream
  - BufferedInputStream/BufferedOutputStream
  - DataInputStream/DataOutputStream
  - ObjectInputStream/ObjectOutputStream

Character Streams (text data):
- Reader/Writer (abstract base classes)
  - FileReader/FileWriter
  - BufferedReader/BufferedWriter
  - InputStreamReader/OutputStreamWriter
  - PrintWriter
```

### Key Differences

| Byte Streams | Character Streams |
|--------------|-------------------|
| Binary data (images, audio) | Text data |
| 8-bit bytes | 16-bit Unicode characters |
| InputStream/OutputStream | Reader/Writer |
| read() returns int (0-255 or -1) | read() returns int (0-65535 or -1) |

---

## Byte Streams

### FileInputStream and FileOutputStream

Reading and writing binary data.

```java
import java.io.*;

// Writing bytes to file
try (FileOutputStream fos = new FileOutputStream("data.bin")) {
    fos.write(65);  // Write single byte
    fos.write(new byte[]{66, 67, 68});  // Write byte array
} catch (IOException e) {
    e.printStackTrace();
}

// Reading bytes from file
try (FileInputStream fis = new FileInputStream("data.bin")) {
    int data;
    while ((data = fis.read()) != -1) {  // -1 indicates end of stream
        System.out.print((char) data);  // A B C D
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

### Reading Byte Arrays

```java
try (FileInputStream fis = new FileInputStream("data.bin")) {
    byte[] buffer = new byte[1024];
    int bytesRead;
    
    while ((bytesRead = fis.read(buffer)) != -1) {
        // Process bytesRead bytes from buffer
        for (int i = 0; i < bytesRead; i++) {
            System.out.print((char) buffer[i]);
        }
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

### Copying Files

```java
void copyFile(String source, String dest) throws IOException {
    try (FileInputStream fis = new FileInputStream(source);
         FileOutputStream fos = new FileOutputStream(dest)) {
        
        byte[] buffer = new byte[8192];  // 8 KB buffer
        int bytesRead;
        
        while ((bytesRead = fis.read(buffer)) != -1) {
            fos.write(buffer, 0, bytesRead);
        }
    }
}
```

---

## Character Streams

### FileReader and FileWriter

Reading and writing text data.

```java
// Writing text to file
try (FileWriter fw = new FileWriter("text.txt")) {
    fw.write("Hello World\n");
    fw.write("Java I/O");
} catch (IOException e) {
    e.printStackTrace();
}

// Reading text from file
try (FileReader fr = new FileReader("text.txt")) {
    int data;
    while ((data = fr.read()) != -1) {
        System.out.print((char) data);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

### InputStreamReader and OutputStreamWriter

Bridge between byte and character streams.

```java
// Reading with specific encoding
try (FileInputStream fis = new FileInputStream("text.txt");
     InputStreamReader isr = new InputStreamReader(fis, "UTF-8")) {
    
    int data;
    while ((data = isr.read()) != -1) {
        System.out.print((char) data);
    }
} catch (IOException e) {
    e.printStackTrace();
}

// Writing with specific encoding
try (FileOutputStream fos = new FileOutputStream("text.txt");
     OutputStreamWriter osw = new OutputStreamWriter(fos, "UTF-8")) {
    
    osw.write("UTF-8 encoded text");
} catch (IOException e) {
    e.printStackTrace();
}
```

---

## Buffered Streams

**Buffered streams** improve performance by reducing system calls.

### BufferedInputStream and BufferedOutputStream

```java
// Buffered byte output
try (FileOutputStream fos = new FileOutputStream("data.bin");
     BufferedOutputStream bos = new BufferedOutputStream(fos)) {
    
    for (int i = 0; i < 10000; i++) {
        bos.write(i);  // Writes to buffer, not file (faster)
    }
    // Buffer flushed automatically when stream closed
} catch (IOException e) {
    e.printStackTrace();
}

// Buffered byte input
try (FileInputStream fis = new FileInputStream("data.bin");
     BufferedInputStream bis = new BufferedInputStream(fis)) {
    
    int data;
    while ((data = bis.read()) != -1) {
        System.out.println(data);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

### BufferedReader and BufferedWriter

```java
// Writing with BufferedWriter
try (FileWriter fw = new FileWriter("text.txt");
     BufferedWriter bw = new BufferedWriter(fw)) {
    
    bw.write("Line 1");
    bw.newLine();  // Platform-independent line separator
    bw.write("Line 2");
    bw.newLine();
    bw.write("Line 3");
} catch (IOException e) {
    e.printStackTrace();
}

// Reading with BufferedReader
try (FileReader fr = new FileReader("text.txt");
     BufferedReader br = new BufferedReader(fr)) {
    
    String line;
    while ((line = br.readLine()) != null) {  // Read entire line
        System.out.println(line);
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

### Performance Comparison

```java
// ❌ Slow - no buffering
long start = System.currentTimeMillis();
try (FileOutputStream fos = new FileOutputStream("data.bin")) {
    for (int i = 0; i < 1000000; i++) {
        fos.write(i);  // 1 million system calls!
    }
}
long slow = System.currentTimeMillis() - start;

// ✅ Fast - with buffering
start = System.currentTimeMillis();
try (FileOutputStream fos = new FileOutputStream("data.bin");
     BufferedOutputStream bos = new BufferedOutputStream(fos)) {
    for (int i = 0; i < 1000000; i++) {
        bos.write(i);  // Buffered, far fewer system calls
    }
}
long fast = System.currentTimeMillis() - start;

System.out.println("Without buffer: " + slow + "ms");
System.out.println("With buffer: " + fast + "ms");
// With buffer is typically 100x faster
```

---

## Data Streams

### DataInputStream and DataOutputStream

Read/write primitive data types.

```java
// Writing primitive data
try (FileOutputStream fos = new FileOutputStream("data.dat");
     DataOutputStream dos = new DataOutputStream(fos)) {
    
    dos.writeInt(123);
    dos.writeDouble(45.67);
    dos.writeBoolean(true);
    dos.writeUTF("Hello");  // UTF-8 encoded string
    dos.writeLong(9876543210L);
} catch (IOException e) {
    e.printStackTrace();
}

// Reading primitive data (must read in same order)
try (FileInputStream fis = new FileInputStream("data.dat");
     DataInputStream dis = new DataInputStream(fis)) {
    
    int intValue = dis.readInt();           // 123
    double doubleValue = dis.readDouble();   // 45.67
    boolean boolValue = dis.readBoolean();   // true
    String strValue = dis.readUTF();         // "Hello"
    long longValue = dis.readLong();         // 9876543210
    
    System.out.println(intValue);
    System.out.println(doubleValue);
    System.out.println(boolValue);
    System.out.println(strValue);
    System.out.println(longValue);
} catch (IOException e) {
    e.printStackTrace();
}
```

### Complete Example

```java
class Product {
    int id;
    String name;
    double price;
    
    Product(int id, String name, double price) {
        this.id = id;
        this.name = name;
        this.price = price;
    }
    
    void saveToStream(DataOutputStream dos) throws IOException {
        dos.writeInt(id);
        dos.writeUTF(name);
        dos.writeDouble(price);
    }
    
    static Product loadFromStream(DataInputStream dis) throws IOException {
        int id = dis.readInt();
        String name = dis.readUTF();
        double price = dis.readDouble();
        return new Product(id, name, price);
    }
}

// Save products
List<Product> products = Arrays.asList(
    new Product(1, "Laptop", 999.99),
    new Product(2, "Mouse", 29.99)
);

try (FileOutputStream fos = new FileOutputStream("products.dat");
     DataOutputStream dos = new DataOutputStream(fos)) {
    
    dos.writeInt(products.size());  // Write count first
    for (Product p : products) {
        p.saveToStream(dos);
    }
} catch (IOException e) {
    e.printStackTrace();
}

// Load products
List<Product> loadedProducts = new ArrayList<>();
try (FileInputStream fis = new FileInputStream("products.dat");
     DataInputStream dis = new DataInputStream(fis)) {
    
    int count = dis.readInt();
    for (int i = 0; i < count; i++) {
        loadedProducts.add(Product.loadFromStream(dis));
    }
} catch (IOException e) {
    e.printStackTrace();
}
```

---

## Object Streams

### Serialization with ObjectOutputStream and ObjectInputStream

Save and load entire objects.

```java
import java.io.Serializable;

// Class must implement Serializable
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    
    String name;
    int age;
    
    Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public String toString() {
        return name + " (" + age + ")";
    }
}

// Serialize (write object)
Person person = new Person("Alice", 30);

try (FileOutputStream fos = new FileOutputStream("person.ser");
     ObjectOutputStream oos = new ObjectOutputStream(fos)) {
    
    oos.writeObject(person);
} catch (IOException e) {
    e.printStackTrace();
}

// Deserialize (read object)
try (FileInputStream fis = new FileInputStream("person.ser");
     ObjectInputStream ois = new ObjectInputStream(fis)) {
    
    Person loaded = (Person) ois.readObject();
    System.out.println(loaded);  // Alice (30)
} catch (IOException | ClassNotFoundException e) {
    e.printStackTrace();
}
```

### Transient Fields

`transient` fields are NOT serialized.

```java
class BankAccount implements Serializable {
    private static final long serialVersionUID = 1L;
    
    String accountNumber;
    double balance;
    transient String password;  // NOT serialized
    
    BankAccount(String accountNumber, double balance, String password) {
        this.accountNumber = accountNumber;
        this.balance = balance;
        this.password = password;
    }
}

// Serialize
BankAccount account = new BankAccount("123456", 1000.0, "secret");

try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("account.ser"))) {
    oos.writeObject(account);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(
        new FileInputStream("account.ser"))) {
    BankAccount loaded = (BankAccount) ois.readObject();
    System.out.println(loaded.accountNumber);  // 123456
    System.out.println(loaded.balance);        // 1000.0
    System.out.println(loaded.password);       // null (not serialized!)
}
```

### Serial Version UID

```java
// ✅ GOOD: Explicit serialVersionUID
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
    
    String name;
    int age;
}

// If you modify class and deserialize old data:
// - Same serialVersionUID: Deserialization attempts (may fail if incompatible)
// - Different/missing serialVersionUID: InvalidClassException
```

---

## Console I/O

### Reading from Console

```java
import java.io.Console;

// Using Console (not available in all environments)
Console console = System.console();
if (console != null) {
    String name = console.readLine("Enter name: ");
    char[] password = console.readPassword("Enter password: ");
    
    System.out.println("Name: " + name);
    // password is char[], not String (for security)
    Arrays.fill(password, ' ');  // Clear password from memory
}

// Using BufferedReader
try (BufferedReader br = new BufferedReader(
        new InputStreamReader(System.in))) {
    
    System.out.print("Enter text: ");
    String line = br.readLine();
    System.out.println("You entered: " + line);
} catch (IOException e) {
    e.printStackTrace();
}

// Using Scanner (simplest)
import java.util.Scanner;

Scanner scanner = new Scanner(System.in);
System.out.print("Enter number: ");
int num = scanner.nextInt();
scanner.nextLine();  // Consume newline
System.out.print("Enter text: ");
String text = scanner.nextLine();
scanner.close();
```

### PrintWriter

```java
// Writing to console
PrintWriter out = new PrintWriter(System.out, true);  // auto-flush
out.println("Hello");
out.printf("Number: %d%n", 42);
out.close();

// Writing to file
try (PrintWriter pw = new PrintWriter("output.txt")) {
    pw.println("Line 1");
    pw.println("Line 2");
    pw.printf("Formatted: %s = %d%n", "value", 100);
} catch (FileNotFoundException e) {
    e.printStackTrace();
}
```

---

## File Operations

### Creating and Deleting Files

```java
import java.io.File;

File file = new File("test.txt");

// Create new file
try {
    boolean created = file.createNewFile();
    if (created) {
        System.out.println("File created");
    } else {
        System.out.println("File already exists");
    }
} catch (IOException e) {
    e.printStackTrace();
}

// Delete file
boolean deleted = file.delete();
if (deleted) {
    System.out.println("File deleted");
}

// Delete on exit
file.deleteOnExit();
```

### File Information

```java
File file = new File("test.txt");

// Existence
boolean exists = file.exists();

// Is file or directory?
boolean isFile = file.isFile();
boolean isDir = file.isDirectory();

// Readable/writable?
boolean canRead = file.canRead();
boolean canWrite = file.canWrite();
boolean canExecute = file.canExecute();

// Size
long bytes = file.length();

// Last modified
long lastModified = file.lastModified();
Date date = new Date(lastModified);

// Absolute path
String absolutePath = file.getAbsolutePath();

// Name
String name = file.getName();
```

### Directory Operations

```java
File dir = new File("mydir");

// Create directory
boolean created = dir.mkdir();  // Create single directory
boolean createdAll = dir.mkdirs();  // Create with parents

// List files
String[] files = dir.list();  // File names
File[] fileObjects = dir.listFiles();  // File objects

// List with filter
File[] txtFiles = dir.listFiles((dir, name) -> name.endsWith(".txt"));

// Iterate directory
for (File file : fileObjects) {
    if (file.isFile()) {
        System.out.println("File: " + file.getName());
    } else if (file.isDirectory()) {
        System.out.println("Directory: " + file.getName());
    }
}
```

---

## Try-with-Resources

**Try-with-resources** automatically closes resources.

### Basic Syntax

```java
// ✅ GOOD: Auto-closes
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line = br.readLine();
} catch (IOException e) {
    e.printStackTrace();
}
// br.close() called automatically

// ❌ BAD: Manual closing
BufferedReader br = null;
try {
    br = new BufferedReader(new FileReader("file.txt"));
    String line = br.readLine();
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (br != null) {
        try {
            br.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

### Multiple Resources

```java
// Multiple resources (closed in reverse order)
try (FileInputStream fis = new FileInputStream("input.txt");
     FileOutputStream fos = new FileOutputStream("output.txt");
     BufferedInputStream bis = new BufferedInputStream(fis);
     BufferedOutputStream bos = new BufferedOutputStream(fos)) {
    
    int data;
    while ((data = bis.read()) != -1) {
        bos.write(data);
    }
}
// Closed in order: bos, bis, fos, fis
```

### Custom AutoCloseable

```java
class MyResource implements AutoCloseable {
    MyResource() {
        System.out.println("Resource opened");
    }
    
    void doWork() {
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

---

## Summary and Exam Tips

### Stream Selection Guide

```java
// Binary data → Byte streams
FileInputStream / FileOutputStream

// Text data → Character streams
FileReader / FileWriter

// Need buffering → Buffered streams
BufferedReader / BufferedWriter
BufferedInputStream / BufferedOutputStream

// Primitive data → Data streams
DataInputStream / DataOutputStream

// Objects → Object streams
ObjectInputStream / ObjectOutputStream

// Formatted output → PrintWriter
PrintWriter
```

### Key Points

- **Byte streams**: InputStream/OutputStream (binary)
- **Character streams**: Reader/Writer (text)
- **Buffered streams**: Improve performance
- **Data streams**: Read/write primitives
- **Object streams**: Serialization
- **try-with-resources**: Auto-close
- **-1**: Indicates end of stream
- **Serializable**: Required for serialization
- **transient**: Field not serialized

### Exam Tips

- `read()` returns **-1** at end of stream
- `readLine()` returns **null** at end
- Buffered streams **significantly improve** performance
- `Serializable` is a **marker interface** (no methods)
- `transient` and `static` fields are NOT serialized
- Try-with-resources closes in **reverse order**
- Data streams must read in **same order** as written
- `FileReader`/`FileWriter` use **default encoding**
- Use `InputStreamReader`/`OutputStreamWriter` for specific encoding
- `PrintWriter` has `checkError()` method (doesn't throw exceptions)

---

**Next:** [Practice Questions - I/O Streams](32-practice-questions.md)
