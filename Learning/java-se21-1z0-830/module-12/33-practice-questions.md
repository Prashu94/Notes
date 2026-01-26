# Module 12: Practice Questions - NIO.2 Path and Files

## Questions (20)

---

### Question 1
```java
Path path = Paths.get("/home/user/file.txt");
Path fileName = path.getFileName();
```
What is `fileName`?

**A)** `/home/user/file.txt`  
**B)** `file.txt`  
**C)** `/file.txt`  
**D)** `user/file.txt`

**Answer: B)**

**Explanation:** `getFileName()` returns only the **file name** without directory: `file.txt`.

---

### Question 2
```java
Path path = Path.of("dir/file.txt");
System.out.println(path.isAbsolute());
```
What is printed?

**A)** `true`  
**B)** `false`  
**C)** Compilation error  
**D)** Exception

**Answer: B)**

**Explanation:** Path is relative (doesn't start with root). Prints **false**.

---

### Question 3
```java
Path path = Paths.get("/home/user/docs");
Path resolved = path.resolve("/etc/config");
```
What is `resolved`?

**A)** `/home/user/docs/etc/config`  
**B)** `/etc/config`  
**C)** `/home/user/etc/config`  
**D)** Compilation error

**Answer: B)**

**Explanation:** When `resolve()` parameter is **absolute**, it returns that absolute path: `/etc/config`.

---

### Question 4
```java
Path path = Paths.get("/home/user/../user/./docs");
Path normalized = path.normalize();
```
What is `normalized`?

**A)** `/home/user/../user/./docs`  
**B)** `/home/docs`  
**C)** `/home/user/docs`  
**D)** `/docs`

**Answer: C)**

**Explanation:** `normalize()` removes `..` and `.`: `/home/user/docs`.

---

### Question 5
```java
Path p1 = Paths.get("/home/user/documents");
Path p2 = Paths.get("/home/user/documents/reports/2024");
Path relative = p1.relativize(p2);
```
What is `relative`?

**A)** `/reports/2024`  
**B)** `reports/2024`  
**C)** `../reports/2024`  
**D)** `2024`

**Answer: B)**

**Explanation:** `relativize()` creates relative path from p1 to p2: `reports/2024`.

---

### Question 6
```java
Path path = Paths.get("/home/user/file.txt");
System.out.println(path.getNameCount());
```
What is printed?

**A)** 2  
**B)** 3  
**C)** 4  
**D)** 5

**Answer: B)**

**Explanation:** Name count excludes root. Count: `home`, `user`, `file.txt` = **3**.

---

### Question 7
```java
Path path = Paths.get("/home/user/documents/file.txt");
Path sub = path.subpath(1, 3);
```
What is `sub`?

**A)** `/user/documents`  
**B)** `user/documents`  
**C)** `home/user/documents`  
**D)** `user/documents/file.txt`

**Answer: B)**

**Explanation:** `subpath(1, 3)` gets elements 1 and 2: `user/documents` (relative path).

---

### Question 8
```java
Path file = Paths.get("file.txt");
Files.delete(file);
```
What if file doesn't exist?

**A)** Returns false  
**B)** Throws NoSuchFileException  
**C)** Does nothing  
**D)** Creates the file

**Answer: B)**

**Explanation:** `delete()` throws **NoSuchFileException** if file doesn't exist.

---

### Question 9
```java
Path source = Paths.get("source.txt");
Path target = Paths.get("target.txt");
Files.copy(source, target);
```
What if target already exists?

**A)** Overwrites target  
**B)** Throws FileAlreadyExistsException  
**C)** Returns false  
**D)** Creates target2.txt

**Answer: B)**

**Explanation:** `copy()` throws **FileAlreadyExistsException** unless `REPLACE_EXISTING` option used.

---

### Question 10
```java
Path path = Paths.get("file.txt");
List<String> lines = Files.readAllLines(path);
```
What if file is large (1 GB)?

**A)** Works fine  
**B)** OutOfMemoryError  
**C)** IOException  
**D)** Stream reads efficiently

**Answer: B)**

**Explanation:** `readAllLines()` loads **entire file** into memory. Large files cause **OutOfMemoryError**.

For large files, use `Files.lines()` which returns Stream:
```java
try (Stream<String> stream = Files.lines(path)) {
    stream.forEach(System.out::println);
}
```

---

### Question 11
```java
Path dir = Paths.get("parent/child/grandchild");
Files.createDirectory(dir);
```
What if parent directories don't exist?

**A)** Creates all parents  
**B)** Throws IOException  
**C)** Returns false  
**D)** Creates only grandchild

**Answer: B)**

**Explanation:** `createDirectory()` requires parent to exist. Throws **IOException**. Use `createDirectories()` for parents.

---

### Question 12
```java
try (Stream<Path> stream = Files.walk(Paths.get("."))) {
    stream.forEach(System.out::println);
}
```
What happens without try-with-resources?

**A)** Works fine  
**B)** Resource leak  
**C)** Compilation error  
**D)** Stream auto-closes

**Answer: B)**

**Explanation:** `Files.walk()` returns Stream that **must be closed** to free resources.

---

### Question 13
```java
Path path = Paths.get("file.txt");
boolean deleted = Files.deleteIfExists(path);
```
What does `deleteIfExists()` return?

**A)** Always true  
**B)** true if deleted, false if didn't exist  
**C)** false if deleted  
**D)** Throws exception

**Answer: B)**

**Explanation:** Returns **true** if file was deleted, **false** if didn't exist.

---

### Question 14
```java
Path path = Paths.get("/home/user/file.txt");
System.out.println(path.getRoot());
```
What is printed?

**A)** `/`  
**B)** `/home`  
**C)** `null`  
**D)** `file.txt`

**Answer: A)**

**Explanation:** `getRoot()` returns root component: `/`.

---

### Question 15
```java
Path path = Paths.get("file.txt");
Path absolute = path.toAbsolutePath();
```
What if current directory is `/home/user`?

**A)** `file.txt`  
**B)** `/file.txt`  
**C)** `/home/user/file.txt`  
**D)** `user/file.txt`

**Answer: C)**

**Explanation:** `toAbsolutePath()` resolves relative path against current directory: `/home/user/file.txt`.

---

### Question 16
```java
try (Stream<Path> stream = Files.list(Paths.get("."))) {
    long count = stream.count();
}
```
Does `Files.list()` list subdirectories recursively?

**A)** Yes  
**B)** No - only immediate children  
**C)** Only files, not directories  
**D)** Depends on parameter

**Answer: B)**

**Explanation:** `Files.list()` lists **only immediate children**, not recursive. Use `Files.walk()` for recursive.

---

### Question 17
```java
Path path = Paths.get("file.txt");
long size = Files.size(path);
```
What if path is a directory?

**A)** Returns total size of contents  
**B)** Returns 0  
**C)** Throws IOException  
**D)** Returns -1

**Answer: C)**

**Explanation:** `Files.size()` works for **files only**. Throws **IOException** for directories.

---

### Question 18
```java
Path base = Paths.get("/home/user/file.txt");
Path sibling = base.resolveSibling("other.txt");
```
What is `sibling`?

**A)** `/home/user/file.txt/other.txt`  
**B)** `/home/user/other.txt`  
**C)** `/other.txt`  
**D)** `other.txt`

**Answer: B)**

**Explanation:** `resolveSibling()` replaces file name: `/home/user/other.txt`.

---

### Question 19
```java
Path source = Paths.get("source.txt");
Path target = Paths.get("target.txt");
Files.move(source, target, StandardCopyOption.ATOMIC_MOVE);
```
What is `ATOMIC_MOVE`?

**A)** Move very fast  
**B)** Move as single indivisible operation  
**C)** Move in small chunks  
**D)** Move with encryption

**Answer: B)**

**Explanation:** `ATOMIC_MOVE` ensures move is **atomic** - either completes fully or not at all.

---

### Question 20
```java
Path path = Paths.get("file.txt");
BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes.class);
System.out.println(attrs.isDirectory());
```
What is `BasicFileAttributes`?

**A)** Class for basic file info  
**B)** Interface for file metadata  
**C)** Enum of attributes  
**D)** Annotation

**Answer: B)**

**Explanation:** `BasicFileAttributes` is an **interface** providing file metadata like size, timestamps, type.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master NIO.2.
- **15-17 correct**: Good understanding. Review Path operations.
- **12-14 correct**: Fair grasp. Study Files class methods.
- **Below 12**: Need more practice. Review Path and Files API.

---

**Previous:** [Theory - NIO.2 Path and Files](33-nio2-paths.md)  
**Next:** [Theory - Serialization](34-serialization.md)
