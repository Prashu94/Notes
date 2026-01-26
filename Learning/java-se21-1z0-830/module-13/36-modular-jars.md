# Module 13: Modular JARs and Migration

## Table of Contents
1. [Creating Modular JARs](#creating-modular-jars)
2. [JAR Command Options](#jar-command-options)
3. [Module Versioning](#module-versioning)
4. [jdeps Tool](#jdeps-tool)
5. [jlink Tool](#jlink-tool)
6. [Migration Strategies](#migration-strategies)
7. [Bottom-Up Migration](#bottom-up-migration)
8. [Top-Down Migration](#top-down-migration)
9. [Common Migration Issues](#common-migration-issues)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Creating Modular JARs

### Modular JAR Structure

```
mymodule.jar
    module-info.class       # Module descriptor
    com/
        example/
            MyClass.class
```

### Compilation and Packaging

```bash
# Project structure
mymodule/
    module-info.java
    com/
        example/
            MyClass.java

# Compile
javac -d out \
    mymodule/module-info.java \
    mymodule/com/example/MyClass.java

# Create JAR
jar --create --file mymodule.jar \
    -C out .
```

### JAR with Main Class

```bash
# Create JAR with main class
jar --create --file mymodule.jar \
    --main-class com.example.Main \
    -C out .

# Run
java -jar mymodule.jar
```

### Multi-Module JAR Creation

```bash
# Module structure
project/
    com.example.util/
        module-info.java
        com/example/util/
    com.example.app/
        module-info.java
        com/example/app/

# Compile util module
javac -d out/com.example.util \
    com.example.util/module-info.java \
    com.example.util/com/example/util/*.java

# Package util module
jar --create --file mods/com.example.util.jar \
    -C out/com.example.util .

# Compile app module
javac --module-path mods -d out/com.example.app \
    com.example.app/module-info.java \
    com.example.app/com/example/app/*.java

# Package app module
jar --create --file mods/com.example.app.jar \
    --main-class com.example.app.Main \
    -C out/com.example.app .

# Run
java --module-path mods -m com.example.app
```

---

## JAR Command Options

### Common JAR Options

```bash
# Create JAR
jar --create --file mymodule.jar -C out .
jar -cf mymodule.jar -C out .  # Short form

# Create with verbose output
jar --create --file mymodule.jar --verbose -C out .
jar -cvf mymodule.jar -C out .

# Extract JAR
jar --extract --file mymodule.jar
jar -xf mymodule.jar

# List contents
jar --list --file mymodule.jar
jar -tf mymodule.jar

# Update JAR
jar --update --file mymodule.jar -C out com/example/NewClass.class
jar -uf mymodule.jar -C out com/example/NewClass.class

# Create with main class
jar --create --file app.jar --main-class com.example.Main -C out .
jar -cfe app.jar com.example.Main -C out .

# Describe module
jar --describe-module --file mymodule.jar
jar -d --file mymodule.jar
```

### Module-Specific JAR Options

```bash
# Print module descriptor
jar --describe-module --file mymodule.jar

# Output:
# com.example.mymodule
# requires java.base
# exports com.example.api

# Create multi-release JAR
jar --create --file app.jar \
    --release 11 -C classes-11 . \
    --release 17 -C classes-17 . \
    -C classes .
```

---

## Module Versioning

### Module Version in Descriptor

```java
// module-info.java (compile-time declaration only)
module com.example.mymodule {
    // No version in module-info.java
    exports com.example.api;
}
```

### JAR Manifest Version

```bash
# Create JAR with version in manifest
jar --create --file mymodule.jar \
    --module-version 1.0.0 \
    -C out .

# Describe module shows version
jar --describe-module --file mymodule.jar
# com.example.mymodule@1.0.0
```

### Runtime Version Check

```java
ModuleDescriptor descriptor = MyClass.class.getModule().getDescriptor();
Optional<Version> version = descriptor.version();
version.ifPresent(v -> System.out.println("Version: " + v));
```

---

## jdeps Tool

**jdeps** analyzes class dependencies and helps migration to modules.

### Basic Usage

```bash
# Analyze JAR dependencies
jdeps myapp.jar

# Output shows:
# myapp.jar -> java.base
# myapp.jar -> java.sql
#   com.example.Main -> java.lang
#   com.example.DataAccess -> java.sql
```

### Module Analysis

```bash
# Generate module-info.java suggestion
jdeps --generate-module-info . myapp.jar

# Creates: ./myapp/module-info.java with suggested directives

# Check module dependencies
jdeps --module-path mods -m com.example.app

# Analyze with detailed output
jdeps --verbose myapp.jar

# Check internal API usage
jdeps --jdk-internals myapp.jar
# Warning: using internal sun.misc.Unsafe
```

### Migration Analysis

```bash
# List required modules
jdeps --list-deps myapp.jar
# java.base
# java.sql
# java.logging

# Check dependencies for automatic modules
jdeps --module-path mods mylegacy.jar

# Analyze multi-module application
jdeps --module-path mods --module com.example.app
```

---

## jlink Tool

**jlink** creates custom runtime images with only required modules.

### Creating Custom Runtime

```bash
# Basic custom runtime
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --output myruntime

# Directory structure:
# myruntime/
#   bin/
#     java      # Custom JVM
#   lib/
#   conf/
```

### Running Custom Runtime

```bash
# Run application with custom runtime
myruntime/bin/java -m com.example.app

# Launcher script
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --launcher myapp=com.example.app/com.example.app.Main \
      --output myruntime

# Run with launcher
myruntime/bin/myapp
```

### Optimizations

```bash
# Compress runtime
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --compress 2 \
      --output myruntime

# Strip debug info
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --strip-debug \
      --output myruntime

# Optimize for size
jlink --module-path $JAVA_HOME/jmods:mods \
      --add-modules com.example.app \
      --compress 2 \
      --strip-debug \
      --no-header-files \
      --no-man-pages \
      --output myruntime
```

### Size Comparison

```
Full JDK: ~300 MB
Custom runtime (basic app): ~40 MB
Custom runtime (optimized): ~30 MB
```

---

## Migration Strategies

### Assessment

```bash
# 1. Analyze existing application
jdeps --jdk-internals myapp.jar

# 2. List dependencies
jdeps --list-deps myapp.jar

# 3. Generate module-info suggestion
jdeps --generate-module-info . myapp.jar
```

### Migration Approaches

1. **Bottom-up**: Migrate lowest-level dependencies first
2. **Top-down**: Migrate application code, use automatic modules for dependencies

---

## Bottom-Up Migration

### Step 1: Identify Dependencies

```
Application
    ↓ depends on
Utility Library (no dependencies)
```

### Step 2: Migrate Utility Library

```java
// util/module-info.java
module com.example.util {
    exports com.example.util;
}
```

### Step 3: Package as Modular JAR

```bash
javac -d out util/module-info.java util/com/example/util/*.java
jar --create --file mods/com.example.util.jar -C out .
```

### Step 4: Migrate Application

```java
// app/module-info.java
module com.example.app {
    requires com.example.util;
}
```

### Step 5: Compile and Run

```bash
javac --module-path mods -d out \
    app/module-info.java \
    app/com/example/app/*.java

jar --create --file mods/com.example.app.jar \
    --main-class com.example.app.Main \
    -C out .

java --module-path mods -m com.example.app
```

---

## Top-Down Migration

### Step 1: Place Dependencies on Module Path

```bash
# Dependencies (no module-info.java) become automatic modules
mods/
    commons-lang3-3.12.0.jar  # Automatic module: commons.lang3
    gson-2.8.9.jar            # Automatic module: gson
```

### Step 2: Create Application Module

```java
// app/module-info.java
module com.example.app {
    requires commons.lang3;  // Automatic module
    requires gson;           // Automatic module
}
```

### Step 3: Compile and Run

```bash
javac --module-path mods -d out \
    app/module-info.java \
    app/com/example/app/*.java

java --module-path mods:out -m com.example.app
```

### Step 4: Migrate Dependencies (Later)

When dependencies add `module-info.java`, update requires statements if needed.

---

## Common Migration Issues

### Issue 1: Split Packages

```
Problem: Same package in multiple JARs

Solution:
- Merge packages into single module
- Rename packages in one module
- Keep on classpath (compatibility mode)
```

### Issue 2: Reflection

```java
// Before modules: Reflection works on all classes

// With modules: Need opens directive
module com.example.app {
    opens com.example.model to com.fasterxml.jackson.databind;
}
```

### Issue 3: Internal API Usage

```bash
# Detect internal API usage
jdeps --jdk-internals myapp.jar

# Warning: using sun.misc.Unsafe

# Solution:
# - Use standard API alternatives
# - Use --add-exports (temporary workaround)
# - Use --illegal-access=permit (deprecated)
```

### Issue 4: Service Loading

```java
// Legacy: META-INF/services
// Modules: provides...with in module-info.java

module provider {
    provides com.example.Service with com.example.impl.ServiceImpl;
}
```

### Workarounds

```bash
# Add exports at runtime (temporary)
java --add-exports java.base/sun.misc=ALL-UNNAMED -m myapp

# Add opens for reflection
java --add-opens java.base/java.lang=ALL-UNNAMED -m myapp

# Add reads (unnamed module reads named module)
java --add-reads mymodule=ALL-UNNAMED -m myapp
```

---

## Summary and Exam Tips

### JAR Commands

```bash
# Create
jar -cf mymodule.jar -C out .

# Extract
jar -xf mymodule.jar

# List
jar -tf mymodule.jar

# Describe module
jar -d --file mymodule.jar

# With main class
jar -cfe app.jar com.example.Main -C out .
```

### Migration Tools

| Tool | Purpose |
|------|---------|
| jdeps | Analyze dependencies |
| jlink | Create custom runtime |
| jar | Package modules |

### Exam Tips

- Modular JAR contains `module-info.class`
- `jar --describe-module` shows module descriptor
- `jdeps` analyzes dependencies and suggests module-info.java
- `jlink` requires module path, not classpath
- Automatic module name from JAR filename (remove version, replace special chars with dot)
- Bottom-up: migrate dependencies first
- Top-down: use automatic modules for dependencies
- Custom runtime includes only required modules
- `--compress 2` for smallest runtime
- `--launcher` creates executable script

---

**Previous:** [Practice Questions - Modules](35-practice-questions.md)  
**Next:** [Practice Questions - Modular JARs](36-practice-questions.md)
