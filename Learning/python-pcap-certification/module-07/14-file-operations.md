# Module 7: File Operations and I/O

## Introduction to File Handling

Files allow programs to store and retrieve data persistently. Python provides built-in functions for file operations.

### Why File Operations?
- **Persistence**: Store data beyond program execution
- **Data Exchange**: Share data between programs
- **Logging**: Record program activity
- **Configuration**: Store application settings

---

## Opening Files

### The `open()` Function

```python
file = open('filename.txt', 'mode')
# ... work with file ...
file.close()
```

### File Modes

| Mode | Description | Creates if Missing | Overwrites |
|------|-------------|-------------------|------------|
| `'r'` | Read (default) | ❌ No | N/A |
| `'w'` | Write | ✅ Yes | ✅ Yes |
| `'a'` | Append | ✅ Yes | ❌ No |
| `'r+'` | Read + Write | ❌ No | ❌ No |
| `'w+'` | Write + Read | ✅ Yes | ✅ Yes |
| `'a+'` | Append + Read | ✅ Yes | ❌ No |
| `'rb'` | Read binary | ❌ No | N/A |
| `'wb'` | Write binary | ✅ Yes | ✅ Yes |
| `'ab'` | Append binary | ✅ Yes | ❌ No |

### Examples

**Read Mode:**
```python
# Open file for reading (must exist)
file = open('data.txt', 'r')
content = file.read()
file.close()
```

**Write Mode:**
```python
# Open file for writing (creates/overwrites)
file = open('output.txt', 'w')
file.write('Hello, World!')
file.close()
```

**Append Mode:**
```python
# Open file for appending (creates if missing)
file = open('log.txt', 'a')
file.write('New log entry\n')
file.close()
```

---

## Reading Files

### Method 1: `read()` - Read Entire File
```python
file = open('document.txt', 'r')
content = file.read()  # Returns entire file as string
print(content)
file.close()
```

### Method 2: `read(size)` - Read Specified Bytes
```python
file = open('document.txt', 'r')
chunk = file.read(10)  # Read first 10 characters
print(chunk)
file.close()
```

### Method 3: `readline()` - Read Single Line
```python
file = open('document.txt', 'r')
line1 = file.readline()  # Read first line
line2 = file.readline()  # Read second line
print(line1, line2)
file.close()
```

### Method 4: `readlines()` - Read All Lines as List
```python
file = open('document.txt', 'r')
lines = file.readlines()  # Returns list of lines
for line in lines:
    print(line.strip())  # strip() removes \n
file.close()
```

### Method 5: Iterate Over File Object
```python
file = open('document.txt', 'r')
for line in file:  # Most memory-efficient
    print(line.strip())
file.close()
```

---

## Writing to Files

### Method 1: `write()` - Write String
```python
file = open('output.txt', 'w')
file.write('First line\n')
file.write('Second line\n')
file.close()
```

### Method 2: `writelines()` - Write List of Strings
```python
lines = ['Line 1\n', 'Line 2\n', 'Line 3\n']
file = open('output.txt', 'w')
file.writelines(lines)
file.close()
```

### Method 3: Print to File
```python
file = open('output.txt', 'w')
print('Hello', 'World', file=file)
print('Another line', file=file)
file.close()
```

---

## Context Managers (`with` Statement)

### The Problem: Forgetting to Close Files
```python
# Bad: File might not close if error occurs
file = open('data.txt', 'r')
content = file.read()
# If error occurs here, file.close() won't execute
file.close()
```

### The Solution: `with` Statement
```python
# Good: File automatically closes
with open('data.txt', 'r') as file:
    content = file.read()
    # File automatically closes after this block
# File is closed here, even if error occurred
```

### Benefits of `with`
✅ **Automatic cleanup**: File always closes  
✅ **Exception safe**: Closes even if error occurs  
✅ **Cleaner code**: No need for explicit close()

### Examples

**Reading with Context Manager:**
```python
with open('input.txt', 'r') as file:
    for line in file:
        print(line.strip())
```

**Writing with Context Manager:**
```python
with open('output.txt', 'w') as file:
    file.write('Hello, World!\n')
    file.write('This is easy!\n')
```

**Multiple Files:**
```python
with open('source.txt', 'r') as infile, open('dest.txt', 'w') as outfile:
    for line in infile:
        outfile.write(line.upper())
```

---

## File Methods and Attributes

### Common File Methods

```python
file = open('data.txt', 'r')

# Read operations
file.read()       # Read entire file
file.read(10)     # Read 10 characters
file.readline()   # Read one line
file.readlines()  # Read all lines as list

# Write operations
file.write(string)      # Write string
file.writelines(list)   # Write list of strings

# File position
file.tell()       # Current position in file
file.seek(0)      # Move to beginning
file.seek(10)     # Move to position 10

# Other methods
file.close()      # Close file
file.flush()      # Flush buffer to disk
file.fileno()     # Get file descriptor

file.close()
```

### File Attributes

```python
file = open('data.txt', 'r')

print(file.name)     # 'data.txt'
print(file.mode)     # 'r'
print(file.closed)   # False
print(file.readable()) # True
print(file.writable()) # False

file.close()
print(file.closed)   # True
```

---

## Working with File Positions

### `tell()` - Get Current Position
```python
with open('data.txt', 'r') as file:
    print(file.tell())      # 0 (beginning)
    file.read(5)            # Read 5 characters
    print(file.tell())      # 5
```

### `seek()` - Change Position
```python
with open('data.txt', 'r') as file:
    file.seek(0)      # Go to beginning
    file.seek(10)     # Go to position 10
    file.seek(0, 2)   # Go to end (whence=2)
```

**seek() Parameters:**
- `seek(offset, whence=0)`
- `whence=0`: From beginning (default)
- `whence=1`: From current position
- `whence=2`: From end

---

## Binary Files

### Reading Binary Files
```python
with open('image.png', 'rb') as file:
    data = file.read()
    print(type(data))  # <class 'bytes'>
```

### Writing Binary Files
```python
data = b'\x00\x01\x02\x03'
with open('binary.dat', 'wb') as file:
    file.write(data)
```

### Copying Binary Files
```python
with open('source.png', 'rb') as src, open('dest.png', 'wb') as dst:
    dst.write(src.read())
```

---

## File Exceptions and Error Handling

### Common File Exceptions

```python
try:
    with open('missing.txt', 'r') as file:
        content = file.read()
except FileNotFoundError:
    print("File not found!")
except PermissionError:
    print("Permission denied!")
except IOError as e:
    print(f"IO Error: {e}")
```

### Checking File Existence
```python
import os

if os.path.exists('file.txt'):
    with open('file.txt', 'r') as file:
        content = file.read()
else:
    print("File doesn't exist")
```

---

## Working with File Paths

### Using `os.path` Module

```python
import os

# Join paths (OS-independent)
path = os.path.join('folder', 'subfolder', 'file.txt')
# Windows: folder\subfolder\file.txt
# Linux/Mac: folder/subfolder/file.txt

# Check if path exists
exists = os.path.exists(path)

# Check if it's a file
is_file = os.path.isfile(path)

# Check if it's a directory
is_dir = os.path.isdir(path)

# Get absolute path
abs_path = os.path.abspath('file.txt')

# Get directory name
dirname = os.path.dirname('/path/to/file.txt')  # '/path/to'

# Get file name
basename = os.path.basename('/path/to/file.txt')  # 'file.txt'

# Split extension
name, ext = os.path.splitext('document.txt')  # ('document', '.txt')
```

### Using `pathlib` Module (Python 3.4+)

```python
from pathlib import Path

# Create path object
path = Path('folder') / 'subfolder' / 'file.txt'

# Check existence
if path.exists():
    print("Exists")

# Read file
content = path.read_text()

# Write file
path.write_text('Hello, World!')

# Get parts
print(path.name)       # 'file.txt'
print(path.stem)       # 'file'
print(path.suffix)     # '.txt'
print(path.parent)     # 'folder/subfolder'
```

---

## Practical Examples

### Example 1: Count Lines in File
```python
with open('document.txt', 'r') as file:
    line_count = sum(1 for line in file)
    print(f"Lines: {line_count}")
```

### Example 2: Word Counter
```python
with open('document.txt', 'r') as file:
    content = file.read()
    words = content.split()
    print(f"Word count: {len(words)}")
```

### Example 3: File Copy Function
```python
def copy_file(source, destination):
    with open(source, 'r') as src, open(destination, 'w') as dst:
        dst.write(src.read())
```

### Example 4: Append to Log File
```python
import datetime

def log_message(message):
    timestamp = datetime.datetime.now()
    with open('app.log', 'a') as log:
        log.write(f"{timestamp}: {message}\n")

log_message("Application started")
log_message("Processing data")
```

### Example 5: Read CSV-like Data
```python
data = []
with open('data.csv', 'r') as file:
    for line in file:
        fields = line.strip().split(',')
        data.append(fields)

for row in data:
    print(row)
```

### Example 6: Filter File Contents
```python
# Keep only non-empty lines
with open('input.txt', 'r') as infile, open('output.txt', 'w') as outfile:
    for line in infile:
        if line.strip():  # If line is not empty
            outfile.write(line)
```

---

## File Buffering

### How Buffering Works
- Python buffers file I/O for performance
- Writes are stored in memory before writing to disk
- Use `flush()` to force write to disk

```python
with open('output.txt', 'w') as file:
    file.write('Line 1\n')
    file.flush()  # Force write to disk now
    file.write('Line 2\n')
    # Automatically flushed when file closes
```

### Controlling Buffering
```python
# Unbuffered (writes immediately)
file = open('output.txt', 'w', buffering=0)  # Binary only

# Line buffered (flush after newline)
file = open('output.txt', 'w', buffering=1)

# Custom buffer size
file = open('output.txt', 'w', buffering=4096)
```

---

## Best Practices

### 1. Always Use Context Managers
```python
# Good
with open('file.txt', 'r') as file:
    content = file.read()

# Avoid
file = open('file.txt', 'r')
content = file.read()
file.close()  # Might not execute if error
```

### 2. Handle Exceptions
```python
try:
    with open('data.txt', 'r') as file:
        content = file.read()
except FileNotFoundError:
    print("File not found")
except PermissionError:
    print("Permission denied")
```

### 3. Use Appropriate Modes
```python
# Reading: use 'r'
# Writing (overwrite): use 'w'
# Appending: use 'a'
# Binary: add 'b' ('rb', 'wb', 'ab')
```

### 4. Read Large Files Efficiently
```python
# Good: Read line by line
with open('huge_file.txt', 'r') as file:
    for line in file:
        process(line)

# Avoid: Read entire file
with open('huge_file.txt', 'r') as file:
    content = file.read()  # May consume too much memory
```

### 5. Close Files Properly
```python
# Context manager closes automatically
with open('file.txt', 'r') as file:
    pass  # File closes here

# Manual close
file = open('file.txt', 'r')
try:
    content = file.read()
finally:
    file.close()  # Always executes
```

---

## Summary

✅ **open()** function opens files with various modes  
✅ **read()** reads file content  
✅ **write()** writes to file  
✅ **Context managers** (`with`) ensure proper cleanup  
✅ **File methods**: readline(), readlines(), tell(), seek()  
✅ **Binary mode** for non-text files  
✅ **Error handling** for file operations  
✅ **pathlib** for modern path handling  

---

## Next Steps
Continue to **Module 7: Practice Questions - File Operations**
