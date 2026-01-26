# Module 12: NIO.2 - Path and Files API

## Table of Contents
1. [Introduction to NIO.2](#introduction-to-nio2)
2. [Path Interface](#path-interface)
3. [Paths and Path Factory Methods](#paths-and-path-factory-methods)
4. [Path Operations](#path-operations)
5. [Files Class - File Operations](#files-class-file-operations)
6. [Reading and Writing Files](#reading-and-writing-files)
7. [Directory Operations](#directory-operations)
8. [File Attributes](#file-attributes)
9. [Walking File Trees](#walking-file-trees)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to NIO.2

**NIO.2** (New I/O 2) introduced in Java 7 provides modern file system access with better performance and features.

### NIO.2 vs Legacy I/O

| Legacy (java.io.File) | NIO.2 (java.nio.file) |
|----------------------|----------------------|
| Limited error reporting | Detailed exceptions |
| No symbolic link support | Full symbolic link support |
| Poor performance | Better performance |
| Limited file attributes | Rich metadata access |
| File class | Path interface + Files class |

### Key Classes

```java
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
```

---

## Path Interface

**Path** represents a file or directory path in the file system.

### Creating Path Objects

```java
import java.nio.file.Path;
import java.nio.file.Paths;

// Using Paths factory method (Java 7-10)
Path path1 = Paths.get("file.txt");
Path path2 = Paths.get("/home/user/documents/file.txt");
Path path3 = Paths.get("dir", "subdir", "file.txt");  // Joins with separator

// Using Path.of() factory method (Java 11+)
Path path4 = Path.of("file.txt");
Path path5 = Path.of("/home/user/documents/file.txt");
Path path6 = Path.of("dir", "subdir", "file.txt");

// From URI
Path path7 = Paths.get(URI.create("file:///home/user/file.txt"));

// From File
File file = new File("file.txt");
Path path8 = file.toPath();

// Convert Path to File
File file2 = path1.toFile();
```

### Path Information

```java
Path path = Paths.get("/home/user/documents/report.pdf");

// Get file name
Path fileName = path.getFileName();  // report.pdf

// Get parent
Path parent = path.getParent();  // /home/user/documents

// Get root
Path root = path.getRoot();  // /

// Get name count
int count = path.getNameCount();  // 4 (home, user, documents, report.pdf)

// Get specific name element
Path name = path.getName(0);  // home
Path name2 = path.getName(1);  // user

// Is absolute?
boolean absolute = path.isAbsolute();  // true

// Get absolute path
Path absolutePath = path.toAbsolutePath();

// String representation
String pathString = path.toString();
```

---

## Paths and Path Factory Methods

### Relative and Absolute Paths

```java
// Relative path
Path relative = Paths.get("data/file.txt");
System.out.println(relative.isAbsolute());  // false

// Absolute path
Path absolute = Paths.get("/home/user/file.txt");
System.out.println(absolute.isAbsolute());  // true

// Convert relative to absolute
Path absolutePath = relative.toAbsolutePath();
System.out.println(absolutePath);  // /current/directory/data/file.txt
```

### Path Manipulation

```java
Path base = Paths.get("/home/user");

// Resolve - join paths
Path resolved = base.resolve("documents/file.txt");
System.out.println(resolved);  // /home/user/documents/file.txt

// Resolve with absolute path (returns absolute)
Path resolved2 = base.resolve("/etc/config");
System.out.println(resolved2);  // /etc/config

// Resolve sibling
Path path = Paths.get("/home/user/documents/file.txt");
Path sibling = path.resolveSibling("other.txt");
System.out.println(sibling);  // /home/user/documents/other.txt

// Relativize - create relative path
Path path1 = Paths.get("/home/user/documents");
Path path2 = Paths.get("/home/user/documents/reports/2024");
Path relative = path1.relativize(path2);
System.out.println(relative);  // reports/2024

// Normalize - remove redundant elements
Path path3 = Paths.get("/home/user/../user/./documents");
Path normalized = path3.normalize();
System.out.println(normalized);  // /home/user/documents
```

### Path Comparison

```java
Path path1 = Paths.get("/home/user/file.txt");
Path path2 = Paths.get("/home/user/file.txt");
Path path3 = Paths.get("file.txt");

// Equality
boolean equal = path1.equals(path2);  // true
boolean equal2 = path1.equals(path3);  // false (different paths)

// Starts with / ends with
boolean starts = path1.startsWith("/home");  // true
boolean ends = path1.endsWith("file.txt");  // true

// Compare
int comparison = path1.compareTo(path2);  // 0 (equal)
```

---

## Path Operations

### Subpaths

```java
Path path = Paths.get("/home/user/documents/report.pdf");

// Subpath (start inclusive, end exclusive)
Path sub1 = path.subpath(0, 2);  // home/user
Path sub2 = path.subpath(1, 3);  // user/documents
Path sub3 = path.subpath(2, 4);  // documents/report.pdf
```

### Iterating Path Elements

```java
Path path = Paths.get("/home/user/documents/file.txt");

// Iterate over elements
for (Path element : path) {
    System.out.println(element);
}
// Output:
// home
// user
// documents
// file.txt

// Using iterator
Iterator<Path> iterator = path.iterator();
while (iterator.hasNext()) {
    System.out.println(iterator.next());
}
```

---

## Files Class - File Operations

### Checking File Existence

```java
import java.nio.file.Files;

Path path = Paths.get("file.txt");

// Check existence
boolean exists = Files.exists(path);
boolean notExists = Files.notExists(path);

// Check if regular file
boolean isFile = Files.isRegularFile(path);

// Check if directory
boolean isDir = Files.isDirectory(path);

// Check if symbolic link
boolean isSymLink = Files.isSymbolicLink(path);

// Check accessibility
boolean readable = Files.isReadable(path);
boolean writable = Files.isWritable(path);
boolean executable = Files.isExecutable(path);

// Check if hidden
boolean hidden = Files.isHidden(path);

// Check if same file
Path path2 = Paths.get("file.txt");
boolean same = Files.isSameFile(path, path2);
```

### Creating Files and Directories

```java
// Create file
Path file = Paths.get("newfile.txt");
try {
    Files.createFile(file);
} catch (FileAlreadyExistsException e) {
    System.out.println("File already exists");
} catch (IOException e) {
    e.printStackTrace();
}

// Create directory
Path dir = Paths.get("newdir");
Files.createDirectory(dir);

// Create directories (with parents)
Path dirs = Paths.get("parent/child/grandchild");
Files.createDirectories(dirs);

// Create temp file
Path tempFile = Files.createTempFile("prefix", ".txt");
System.out.println(tempFile);  // /tmp/prefix12345.txt

// Create temp directory
Path tempDir = Files.createTempDirectory("tempdir");
System.out.println(tempDir);  // /tmp/tempdir67890
```

### Deleting Files

```java
Path path = Paths.get("file.txt");

// Delete file (throws exception if doesn't exist)
try {
    Files.delete(path);
} catch (NoSuchFileException e) {
    System.out.println("File doesn't exist");
} catch (DirectoryNotEmptyException e) {
    System.out.println("Directory not empty");
} catch (IOException e) {
    e.printStackTrace();
}

// Delete if exists (returns boolean)
boolean deleted = Files.deleteIfExists(path);
```

### Copying and Moving Files

```java
Path source = Paths.get("source.txt");
Path target = Paths.get("target.txt");

// Copy file
Files.copy(source, target);

// Copy with options
import java.nio.file.StandardCopyOption;

Files.copy(source, target, 
    StandardCopyOption.REPLACE_EXISTING,
    StandardCopyOption.COPY_ATTRIBUTES);

// Move/rename file
Files.move(source, target);

// Move with options
Files.move(source, target,
    StandardCopyOption.REPLACE_EXISTING,
    StandardCopyOption.ATOMIC_MOVE);

// Copy from InputStream
try (InputStream in = new FileInputStream("input.txt")) {
    Files.copy(in, target, StandardCopyOption.REPLACE_EXISTING);
}

// Copy to OutputStream
try (OutputStream out = new FileOutputStream("output.txt")) {
    Files.copy(source, out);
}
```

---

## Reading and Writing Files

### Reading Files

```java
Path path = Paths.get("file.txt");

// Read all bytes
byte[] bytes = Files.readAllBytes(path);
String content = new String(bytes);

// Read all lines
List<String> lines = Files.readAllLines(path);
for (String line : lines) {
    System.out.println(line);
}

// Read with specific encoding
List<String> linesUtf8 = Files.readAllLines(path, StandardCharsets.UTF_8);

// Read as String (Java 11+)
String contentStr = Files.readString(path);

// Read lines as Stream
try (Stream<String> stream = Files.lines(path)) {
    stream.forEach(System.out::println);
}

// Buffered reader
try (BufferedReader reader = Files.newBufferedReader(path)) {
    String line;
    while ((line = reader.readLine()) != null) {
        System.out.println(line);
    }
}
```

### Writing Files

```java
Path path = Paths.get("output.txt");

// Write bytes
byte[] bytes = "Hello World".getBytes();
Files.write(path, bytes);

// Write lines
List<String> lines = Arrays.asList("Line 1", "Line 2", "Line 3");
Files.write(path, lines);

// Write with options
import java.nio.file.StandardOpenOption;

Files.write(path, lines,
    StandardOpenOption.CREATE,
    StandardOpenOption.APPEND);

// Write string (Java 11+)
Files.writeString(path, "Hello World");

// Buffered writer
try (BufferedWriter writer = Files.newBufferedWriter(path)) {
    writer.write("Line 1");
    writer.newLine();
    writer.write("Line 2");
}

// Output stream
try (OutputStream out = Files.newOutputStream(path)) {
    out.write("Hello".getBytes());
}
```

---

## Directory Operations

### Listing Directory Contents

```java
Path dir = Paths.get("mydir");

// List directory (returns Stream)
try (Stream<Path> stream = Files.list(dir)) {
    stream.forEach(System.out::println);
}

// Filter entries
try (Stream<Path> stream = Files.list(dir)) {
    stream.filter(path -> path.toString().endsWith(".txt"))
          .forEach(System.out::println);
}

// Get DirectoryStream
try (DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
    for (Path entry : stream) {
        System.out.println(entry);
    }
}

// DirectoryStream with filter
try (DirectoryStream<Path> stream = 
        Files.newDirectoryStream(dir, "*.txt")) {
    for (Path entry : stream) {
        System.out.println(entry);
    }
}
```

### Walking Directory Trees

```java
// Walk tree (depth-first)
try (Stream<Path> stream = Files.walk(Paths.get("."))) {
    stream.forEach(System.out::println);
}

// Walk with max depth
try (Stream<Path> stream = Files.walk(Paths.get("."), 2)) {
    stream.forEach(System.out::println);
}

// Find files
try (Stream<Path> stream = Files.find(Paths.get("."),
        Integer.MAX_VALUE,
        (path, attrs) -> path.toString().endsWith(".txt"))) {
    stream.forEach(System.out::println);
}

// Find with BiPredicate
try (Stream<Path> stream = Files.find(Paths.get("."), 3,
        (path, attrs) -> attrs.isRegularFile() && attrs.size() > 1024)) {
    stream.forEach(System.out::println);
}
```

---

## File Attributes

### Basic File Attributes

```java
import java.nio.file.attribute.*;

Path path = Paths.get("file.txt");

// File size
long size = Files.size(path);

// Last modified time
FileTime lastModified = Files.getLastModifiedTime(path);
System.out.println(lastModified);

// Set last modified time
FileTime newTime = FileTime.fromMillis(System.currentTimeMillis());
Files.setLastModifiedTime(path, newTime);

// Get BasicFileAttributes
BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes.class);

System.out.println("Size: " + attrs.size());
System.out.println("Created: " + attrs.creationTime());
System.out.println("Modified: " + attrs.lastModifiedTime());
System.out.println("Accessed: " + attrs.lastAccessTime());
System.out.println("Is directory: " + attrs.isDirectory());
System.out.println("Is regular file: " + attrs.isRegularFile());
System.out.println("Is symbolic link: " + attrs.isSymbolicLink());
```

### Platform-Specific Attributes

```java
// DOS attributes (Windows)
DosFileAttributes dosAttrs = Files.readAttributes(path, DosFileAttributes.class);
boolean hidden = dosAttrs.isHidden();
boolean readOnly = dosAttrs.isReadOnly();
boolean system = dosAttrs.isSystem();
boolean archive = dosAttrs.isArchive();

// POSIX attributes (Unix/Linux)
PosixFileAttributes posixAttrs = Files.readAttributes(path, PosixFileAttributes.class);
UserPrincipal owner = posixAttrs.owner();
GroupPrincipal group = posixAttrs.group();
Set<PosixFilePermission> permissions = posixAttrs.permissions();

// Print permissions
for (PosixFilePermission perm : permissions) {
    System.out.println(perm);
}
```

---

## Walking File Trees

### FileVisitor Interface

```java
import java.nio.file.*;
import java.nio.file.attribute.BasicFileAttributes;

class PrintFileVisitor extends SimpleFileVisitor<Path> {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) {
        System.out.println("File: " + file);
        return FileVisitResult.CONTINUE;
    }
    
    @Override
    public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) {
        System.out.println("Directory: " + dir);
        return FileVisitResult.CONTINUE;
    }
    
    @Override
    public FileVisitResult visitFileFailed(Path file, IOException exc) {
        System.err.println("Failed to visit: " + file);
        return FileVisitResult.CONTINUE;
    }
    
    @Override
    public FileVisitResult postVisitDirectory(Path dir, IOException exc) {
        System.out.println("Finished directory: " + dir);
        return FileVisitResult.CONTINUE;
    }
}

// Usage
Files.walkFileTree(Paths.get("."), new PrintFileVisitor());
```

### Practical Examples

```java
// Delete directory tree
class DeleteFileVisitor extends SimpleFileVisitor<Path> {
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) 
            throws IOException {
        Files.delete(file);
        return FileVisitResult.CONTINUE;
    }
    
    @Override
    public FileVisitResult postVisitDirectory(Path dir, IOException exc) 
            throws IOException {
        Files.delete(dir);
        return FileVisitResult.CONTINUE;
    }
}

// Copy directory tree
class CopyFileVisitor extends SimpleFileVisitor<Path> {
    private Path source;
    private Path target;
    
    CopyFileVisitor(Path source, Path target) {
        this.source = source;
        this.target = target;
    }
    
    @Override
    public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs) 
            throws IOException {
        Path newDir = target.resolve(source.relativize(dir));
        Files.createDirectories(newDir);
        return FileVisitResult.CONTINUE;
    }
    
    @Override
    public FileVisitResult visitFile(Path file, BasicFileAttributes attrs) 
            throws IOException {
        Path newFile = target.resolve(source.relativize(file));
        Files.copy(file, newFile, StandardCopyOption.REPLACE_EXISTING);
        return FileVisitResult.CONTINUE;
    }
}
```

---

## Summary and Exam Tips

### Path vs File

```java
// Legacy
File file = new File("file.txt");
file.exists();
file.delete();

// NIO.2
Path path = Paths.get("file.txt");
Files.exists(path);
Files.delete(path);
```

### Key Differences

| Operation | java.io.File | java.nio.file |
|-----------|--------------|---------------|
| Create path | `new File()` | `Paths.get()` or `Path.of()` |
| Check exists | `file.exists()` | `Files.exists(path)` |
| Delete | `file.delete()` | `Files.delete(path)` |
| Copy | Manual | `Files.copy()` |
| Move | `file.renameTo()` | `Files.move()` |
| Read all lines | Manual | `Files.readAllLines()` |

### Exam Tips

- **Path** is an **interface**, not a class
- `Paths.get()` and `Path.of()` create Path instances
- `Files` class contains **static utility methods**
- `resolve()` joins paths, **absolute path parameter** returns that path
- `relativize()` creates relative path between two paths
- `normalize()` removes `.` and `..` from path
- `Files.walk()` returns **Stream** (must close)
- `Files.list()` returns **Stream** (must close)
- `FileVisitResult.SKIP_SUBTREE` skips directory contents
- `FileVisitResult.TERMINATE` stops walking
- Try-with-resources should be used for Streams from `Files.walk()`, `Files.list()`, `Files.lines()`

---

**Previous:** [Practice Questions - I/O Streams](32-practice-questions.md)  
**Next:** [Practice Questions - NIO.2](33-practice-questions.md)
