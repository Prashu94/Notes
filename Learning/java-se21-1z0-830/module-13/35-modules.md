# Module 13: Java Module System

## Table of Contents
1. [Introduction to Modules](#introduction-to-modules)
2. [Module Benefits](#module-benefits)
3. [Module Declaration](#module-declaration)
4. [Module Directives](#module-directives)
5. [Module Types](#module-types)
6. [Creating Modular Applications](#creating-modular-applications)
7. [Module Path vs Classpath](#module-path-vs-classpath)
8. [Module Resolution](#module-resolution)
9. [Services and Service Providers](#services-and-service-providers)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to Modules

**Java Platform Module System (JPMS)** introduced in Java 9 organizes code into modules for better encapsulation and maintainability.

### What is a Module?

A **module** is a named, self-describing collection of:
- Packages
- Resources
- Module descriptor (`module-info.java`)

### Pre-Modules Issues

```
Problems before modules:
- JAR hell (dependency conflicts)
- Weak encapsulation (public = accessible everywhere)
- Large JRE (entire platform bundled)
- No explicit dependencies
```

---

## Module Benefits

### 1. Strong Encapsulation

```java
// Without modules: public class accessible everywhere
public class InternalClass {  // Anyone can access
    // ...
}

// With modules: public class only accessible if exported
module mymodule {
    // InternalClass NOT exported → not accessible outside module
}
```

### 2. Explicit Dependencies

```java
// Module explicitly declares what it needs
module mymodule {
    requires java.sql;      // Explicit dependency
    requires java.logging;
}
```

### 3. Smaller Runtime

```
jlink tool creates custom runtime with only required modules
Full JRE: ~200 MB
Custom runtime: ~30-50 MB
```

### 4. Reliable Configuration

```
Module system detects:
- Missing dependencies
- Circular dependencies
- Duplicate packages
at startup, not runtime
```

---

## Module Declaration

### module-info.java

**module-info.java** is the module descriptor placed in the **root** of the module source directory.

```
mymodule/
    module-info.java
    com/
        example/
            MyClass.java
```

### Basic Module

```java
// module-info.java
module com.example.mymodule {
    // Module directives
}
```

### Module Naming

```java
// Convention: reverse domain name
module com.company.project.feature {
}

// Valid names
module mymodule {
}

module my.module {
}

// Invalid names
module my-module {  // ✗ Hyphens not allowed
}

module 123module {  // ✗ Cannot start with digit
}
```

---

## Module Directives

### 1. requires

**requires** declares a dependency on another module.

```java
module com.example.app {
    requires java.sql;        // Needs java.sql module
    requires java.logging;    // Needs java.logging module
}
```

### 2. requires transitive

**requires transitive** makes dependency available to modules that require this module.

```java
// Module A
module com.example.moduleA {
    requires transitive java.sql;  // Transitive dependency
}

// Module B
module com.example.moduleB {
    requires com.example.moduleA;  // Also gets java.sql automatically
    // No need: requires java.sql;
}
```

### 3. exports

**exports** makes a package accessible to other modules.

```java
module com.example.mymodule {
    exports com.example.api;         // Public API
    // com.example.internal NOT exported → encapsulated
}
```

### 4. exports...to

**exports...to** restricts package access to specific modules.

```java
module com.example.mymodule {
    exports com.example.api to com.example.client1, com.example.client2;
    // Only client1 and client2 can access com.example.api
}
```

### 5. opens

**opens** allows reflective access to a package at runtime.

```java
module com.example.mymodule {
    opens com.example.model;  // Allows reflection (e.g., for frameworks)
}
```

### 6. opens...to

**opens...to** allows reflective access to specific modules only.

```java
module com.example.mymodule {
    opens com.example.model to com.fasterxml.jackson.databind;
    // Only Jackson can reflect on com.example.model
}
```

### 7. uses

**uses** declares that this module uses a service.

```java
module com.example.consumer {
    uses com.example.service.MyService;  // Service consumer
}
```

### 8. provides...with

**provides...with** declares that this module provides a service implementation.

```java
module com.example.provider {
    provides com.example.service.MyService 
        with com.example.service.impl.MyServiceImpl;
}
```

---

## Module Types

### 1. Named Modules

Explicit modules with `module-info.java`.

```java
// module-info.java
module com.example.named {
    exports com.example.api;
}
```

### 2. Unnamed Module

Code on **classpath** (not module path) belongs to the unnamed module.

```
Features:
- Reads all other modules
- Exports all packages
- Cannot be required by named modules
- Compatibility bridge for legacy code
```

### 3. Automatic Modules

JARs on **module path** without `module-info.java` become automatic modules.

```
Features:
- Name derived from JAR filename
- Exports all packages
- Reads all other modules
- Can be required by named modules
```

### Automatic Module Naming

```
commons-lang3-3.12.0.jar → commons.lang3
junit-4.13.jar → junit
mysql-connector-java-8.0.26.jar → mysql.connector.java
```

**Rules:**
1. Remove `.jar` extension
2. Remove version number
3. Replace non-alphanumeric with `.`
4. Remove consecutive dots

---

## Creating Modular Applications

### Project Structure

```
project/
    com.example.util/
        module-info.java
        com/
            example/
                util/
                    StringUtils.java
    com.example.app/
        module-info.java
        com/
            example/
                app/
                    Main.java
```

### Module: com.example.util

```java
// com.example.util/module-info.java
module com.example.util {
    exports com.example.util;  // Export public API
}
```

```java
// com.example.util/com/example/util/StringUtils.java
package com.example.util;

public class StringUtils {
    public static boolean isEmpty(String str) {
        return str == null || str.isEmpty();
    }
}
```

### Module: com.example.app

```java
// com.example.app/module-info.java
module com.example.app {
    requires com.example.util;  // Depends on util module
}
```

```java
// com.example.app/com/example/app/Main.java
package com.example.app;

import com.example.util.StringUtils;

public class Main {
    public static void main(String[] args) {
        System.out.println(StringUtils.isEmpty(""));  // true
    }
}
```

### Compilation

```bash
# Compile util module
javac -d out/com.example.util \
    com.example.util/module-info.java \
    com.example.util/com/example/util/StringUtils.java

# Compile app module
javac --module-path out -d out/com.example.app \
    com.example.app/module-info.java \
    com.example.app/com/example/app/Main.java

# Run
java --module-path out -m com.example.app/com.example.app.Main
```

---

## Module Path vs Classpath

### Classpath (Legacy)

```bash
java -cp lib/a.jar:lib/b.jar:classes Main
```

**Issues:**
- No encapsulation
- JAR hell (version conflicts)
- No explicit dependencies
- Runtime errors

### Module Path

```bash
java --module-path mods -m com.example.app/com.example.app.Main
```

**Benefits:**
- Strong encapsulation
- Explicit dependencies
- Compile-time checks
- Reliable configuration

### Comparison

| Feature | Classpath | Module Path |
|---------|-----------|-------------|
| Encapsulation | Weak | Strong |
| Dependencies | Implicit | Explicit |
| Errors | Runtime | Compile-time |
| JARs | Regular JARs | Modular JARs / Automatic modules |
| Access | All public classes | Only exported packages |

---

## Module Resolution

### Module Graph

```java
// Module A
module com.example.a {
    requires com.example.b;
}

// Module B
module com.example.b {
    requires com.example.c;
}

// Module C
module com.example.c {
}
```

**Module graph:** A → B → C

### Circular Dependencies

```java
// Module A
module com.example.a {
    requires com.example.b;
}

// Module B
module com.example.b {
    requires com.example.a;  // ✗ Circular dependency
}

// Compilation error!
```

### Split Packages

```java
// Module A
module com.example.a {
    exports com.example.util;
}

// Module B
module com.example.b {
    exports com.example.util;  // ✗ Same package in different modules
}

// Error: Split package not allowed
```

---

## Services and Service Providers

### Service Interface

```java
// com.example.service/module-info.java
module com.example.service {
    exports com.example.service;
}
```

```java
// com.example.service/com/example/service/MessageService.java
package com.example.service;

public interface MessageService {
    String getMessage();
}
```

### Service Provider

```java
// com.example.provider/module-info.java
module com.example.provider {
    requires com.example.service;
    provides com.example.service.MessageService 
        with com.example.provider.EnglishMessageService;
}
```

```java
// com.example.provider/com/example/provider/EnglishMessageService.java
package com.example.provider;

import com.example.service.MessageService;

public class EnglishMessageService implements MessageService {
    @Override
    public String getMessage() {
        return "Hello";
    }
}
```

### Service Consumer

```java
// com.example.consumer/module-info.java
module com.example.consumer {
    requires com.example.service;
    uses com.example.service.MessageService;
}
```

```java
// com.example.consumer/com/example/consumer/Main.java
package com.example.consumer;

import com.example.service.MessageService;
import java.util.ServiceLoader;

public class Main {
    public static void main(String[] args) {
        ServiceLoader<MessageService> loader = 
            ServiceLoader.load(MessageService.class);
        
        for (MessageService service : loader) {
            System.out.println(service.getMessage());
        }
    }
}
```

---

## Summary and Exam Tips

### Key Directives

```java
module com.example.mymodule {
    requires java.sql;                    // Dependency
    requires transitive java.logging;     // Transitive dependency
    
    exports com.example.api;              // Export package
    exports com.example.internal to com.example.client;  // Qualified export
    
    opens com.example.model;              // Open for reflection
    opens com.example.entity to hibernate;  // Qualified open
    
    uses com.example.service.Service;     // Service consumer
    provides com.example.service.Service with com.example.impl.ServiceImpl;  // Service provider
}
```

### Module Types

- **Named module**: Has `module-info.java`
- **Unnamed module**: On classpath
- **Automatic module**: JAR on module path without `module-info.java`

### Exam Tips

- `module-info.java` must be in **root** of module source
- Module names use **dots**, not hyphens
- **exports** makes package accessible (compile-time)
- **opens** allows reflection (runtime)
- **requires transitive** passes dependency to dependent modules
- Unnamed module **cannot be required**
- Automatic modules **export all packages**
- **Circular dependencies** not allowed
- **Split packages** not allowed (same package in multiple modules)
- Service provider class must have **public no-arg constructor**

---

**Previous:** [Module 12 - Practice Questions](../module-12/34-practice-questions.md)  
**Next:** [Practice Questions - Modules](35-practice-questions.md)
