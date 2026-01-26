# Module 12: Practice Questions - I/O Streams

## Questions (20)

---

### Question 1
```java
try (FileInputStream fis = new FileInputStream("file.txt")) {
    int data = fis.read();
}
```
What type is `data`?

**A)** `byte`  
**B)** `int`  
**C)** `char`  
**D)** `String`

**Answer: B)**

**Explanation:** `read()` returns **int** (0-255 for data, -1 for end of stream).

---

### Question 2
```java
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line = br.readLine();
}
```
What does `readLine()` return at end of file?

**A)** ""  
**B)** -1  
**C)** null  
**D)** EOFException

**Answer: C)**

**Explanation:** `readLine()` returns **null** when end of file reached.

---

### Question 3
```java
class Person implements Serializable {
    String name;
    transient int age;
}
```
After serialization and deserialization, what is `age`?

**A)** Original value  
**B)** 0  
**C)** null  
**D)** Compilation error

**Answer: B)**

**Explanation:** `transient` fields are NOT serialized. `int` defaults to **0** after deserialization.

---

### Question 4
```java
try (FileWriter fw = new FileWriter("file.txt")) {
    fw.write(65);
}
```
What is written to the file?

**A)** 65  
**B)** A  
**C)** a  
**D)** Binary 01000001

**Answer: B)**

**Explanation:** `FileWriter` writes characters. 65 is ASCII for **'A'**.

---

### Question 5
```java
try (DataOutputStream dos = new DataOutputStream(
        new FileOutputStream("data.dat"))) {
    dos.writeInt(100);
    dos.writeDouble(3.14);
}
```
How many bytes are written?

**A)** 4  
**B)** 8  
**C)** 12  
**D)** 16

**Answer: C)**

**Explanation:** `int` = 4 bytes, `double` = 8 bytes. Total: **12 bytes**.

---

### Question 6
```java
try (FileOutputStream fos = new FileOutputStream("file.txt");
     BufferedOutputStream bos = new BufferedOutputStream(fos)) {
    bos.write(65);
}
```
When is data written to disk?

**A)** Immediately on write()  
**B)** When buffer is full  
**C)** When stream closes  
**D)** B or C

**Answer: D)**

**Explanation:** Buffered streams write to disk when buffer is **full** or stream **closes** (auto-flush).

---

### Question 7
```java
class Product {
    String name;
}
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("obj.ser"))) {
    oos.writeObject(new Product());
}
```
What happens?

**A)** Works fine  
**B)** NotSerializableException  
**C)** Compilation error  
**D)** IOException

**Answer: B)**

**Explanation:** `Product` doesn't implement `Serializable`. Throws **NotSerializableException**.

---

### Question 8
```java
try (FileInputStream fis = new FileInputStream("file.txt")) {
    int data;
    while ((data = fis.read()) != -1) {
        System.out.print(data);
    }
}
```
What is printed for file containing "AB"?

**A)** AB  
**B)** 6566  
**C)** A B  
**D)** Compilation error

**Answer: B)**

**Explanation:** `read()` returns **int** values. 'A' = 65, 'B' = 66. Prints **6566**.

---

### Question 9
```java
BufferedReader br = new BufferedReader(new FileReader("file.txt"));
String line = br.readLine();
br.close();
```
What's wrong?

**A)** Nothing  
**B)** Should use try-with-resources  
**C)** readLine() throws exception  
**D)** BufferedReader needs BufferedWriter

**Answer: B)**

**Explanation:** Should use **try-with-resources** to ensure stream closes even if exception occurs.

```java
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line = br.readLine();
}
```

---

### Question 10
```java
class Data implements Serializable {
    static int count = 0;
    int value = 10;
}
```
After serialization and deserialization, what happens to `count`?

**A)** Serialized and restored  
**B)** Not serialized, keeps current value  
**C)** Reset to 0  
**D)** Compilation error

**Answer: B)**

**Explanation:** `static` fields are NOT serialized. They belong to class, not instance.

---

### Question 11
```java
try (PrintWriter pw = new PrintWriter("file.txt")) {
    pw.println("Hello");
    pw.printf("%d", 42);
}
```
Does `PrintWriter` throw IOException?

**A)** Yes  
**B)** No - use checkError()  
**C)** Only for file not found  
**D)** Depends on file

**Answer: B)**

**Explanation:** `PrintWriter` **doesn't throw** IOException. Use `checkError()` to check for errors.

---

### Question 12
```java
try (FileReader fr = new FileReader("file.txt");
     BufferedReader br = new BufferedReader(fr)) {
    // Read file
}
```
In what order are streams closed?

**A)** fr, then br  
**B)** br, then fr  
**C)** Simultaneously  
**D)** Random order

**Answer: B)**

**Explanation:** Try-with-resources closes in **reverse order** of declaration. **br** first, then **fr**.

---

### Question 13
```java
try (DataInputStream dis = new DataInputStream(
        new FileInputStream("data.dat"))) {
    int value = dis.readInt();
    double d = dis.readDouble();
}
```
Data was written as: `dos.writeDouble(3.14); dos.writeInt(100);`

What happens?

**A)** Works correctly  
**B)** Reads wrong values  
**C)** IOException  
**D)** EOFException

**Answer: B)**

**Explanation:** Must read in **same order** as written. Reading int first when double was written gives wrong values.

---

### Question 14
```java
File file = new File("test.txt");
boolean created = file.createNewFile();
```
What does `createNewFile()` return?

**A)** Always true  
**B)** true if created, false if already exists  
**C)** false if created  
**D)** Throws exception if exists

**Answer: B)**

**Explanation:** Returns **true** if file created, **false** if file already exists.

---

### Question 15
```java
try (FileOutputStream fos = new FileOutputStream("data.bin")) {
    fos.write(new byte[]{65, 66, 67});
}

try (FileInputStream fis = new FileInputStream("data.bin")) {
    byte[] buffer = new byte[2];
    int bytesRead = fis.read(buffer);
    System.out.println(bytesRead);
}
```
What is printed?

**A)** 1  
**B)** 2  
**C)** 3  
**D)** -1

**Answer: B)**

**Explanation:** Buffer size is 2. `read(buffer)` reads up to 2 bytes, returns **2**.

---

### Question 16
```java
class Employee implements Serializable {
    private static final long serialVersionUID = 1L;
}
```
What is `serialVersionUID` used for?

**A)** Unique employee ID  
**B)** Version control for serialization  
**C)** Serial number  
**D)** Nothing

**Answer: B)**

**Explanation:** `serialVersionUID` ensures **version compatibility** during deserialization.

---

### Question 17
```java
try (BufferedWriter bw = new BufferedWriter(new FileWriter("file.txt"))) {
    bw.write("Line 1");
    bw.newLine();
    bw.write("Line 2");
}
```
What does `newLine()` do?

**A)** Writes \n  
**B)** Writes platform-specific line separator  
**C)** Creates new file  
**D)** Compilation error

**Answer: B)**

**Explanation:** `newLine()` writes **platform-specific** line separator (\n on Unix, \r\n on Windows).

---

### Question 18
```java
File dir = new File("mydir");
boolean created = dir.mkdir();
```
What if parent directory doesn't exist?

**A)** Creates parent automatically  
**B)** Returns false  
**C)** Throws IOException  
**D)** Creates with warning

**Answer: B)**

**Explanation:** `mkdir()` fails if parent doesn't exist. Returns **false**. Use `mkdirs()` to create parents.

---

### Question 19
```java
try (InputStreamReader isr = new InputStreamReader(
        new FileInputStream("file.txt"), "UTF-8")) {
    int data = isr.read();
}
```
What is `InputStreamReader`?

**A)** Byte stream  
**B)** Character stream  
**C)** Bridge from bytes to characters  
**D)** Object stream

**Answer: C)**

**Explanation:** `InputStreamReader` is a **bridge** from byte stream to character stream with specified encoding.

---

### Question 20
```java
try (ObjectOutputStream oos = new ObjectOutputStream(
        new FileOutputStream("obj.ser"))) {
    oos.writeObject("Hello");
    oos.writeObject(42);
}
```
Can you serialize primitive values?

**A)** Yes, directly  
**B)** No - must use wrapper classes  
**C)** Yes, auto-boxed  
**D)** Only with DataOutputStream

**Answer: C)**

**Explanation:** Primitives are **auto-boxed** to wrapper classes (Integer, etc.) which are Serializable.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master I/O streams.
- **15-17 correct**: Good understanding. Review serialization and buffering.
- **12-14 correct**: Fair grasp. Study stream types and try-with-resources.
- **Below 12**: Need more practice. Review all I/O concepts.

---

**Previous:** [Theory - I/O Streams](32-io-streams.md)  
**Next:** [Theory - NIO.2 Path and Files](33-nio2-paths.md)
