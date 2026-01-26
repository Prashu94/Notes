# Module 13: Practice Questions - Java Module System

## Questions (20)

---

### Question 1
```java
// module-info.java
module com.example.mymodule {
    exports com.example.api;
}
```
Where must `module-info.java` be located?

**A)** In any package  
**B)** In the root of module source  
**C)** In META-INF  
**D)** In com.example

**Answer: B)**

**Explanation:** `module-info.java` must be in the **root** of the module source directory.

---

### Question 2
```java
module com.example.app {
    requires java.sql;
}
```
What does `requires` do?

**A)** Exports a package  
**B)** Declares a dependency  
**C)** Opens for reflection  
**D)** Provides a service

**Answer: B)**

**Explanation:** `requires` declares that this module **depends on** another module.

---

### Question 3
```java
module com.example.a {
    requires transitive com.example.b;
}

module com.example.c {
    requires com.example.a;
}
```
Can module C access com.example.b?

**A)** No  
**B)** Yes, because of requires transitive  
**C)** Only if C also requires B  
**D)** Compilation error

**Answer: B)**

**Explanation:** `requires transitive` makes **B** available to modules requiring **A**.

---

### Question 4
```java
module com.example.mymodule {
    exports com.example.api;
}
```
Can classes in `com.example.internal` be accessed from other modules?

**A)** Yes  
**B)** No - not exported  
**C)** Only if public  
**D)** With reflection

**Answer: B)**

**Explanation:** Only **exported** packages are accessible. `com.example.internal` is **encapsulated**.

---

### Question 5
```java
module com.example.mymodule {
    exports com.example.api to com.example.client;
}
```
Which modules can access `com.example.api`?

**A)** All modules  
**B)** Only com.example.client  
**C)** No modules  
**D)** Only unnamed module

**Answer: B)**

**Explanation:** `exports...to` restricts access to **specific modules**: `com.example.client`.

---

### Question 6
```java
module com.example.a {
    requires com.example.b;
}

module com.example.b {
    requires com.example.a;
}
```
What happens?

**A)** Works fine  
**B)** Compilation error - circular dependency  
**C)** Runtime error  
**D)** Warning only

**Answer: B)**

**Explanation:** **Circular dependencies** between modules are **not allowed**.

---

### Question 7
```java
module com.example.mymodule {
    opens com.example.model;
}
```
What does `opens` do?

**A)** Exports package  
**B)** Allows reflective access  
**C)** Declares dependency  
**D)** Provides service

**Answer: B)**

**Explanation:** `opens` allows **reflective access** to the package at runtime.

---

### Question 8
What is the unnamed module?

**A)** Module without name  
**B)** Code on classpath  
**C)** Automatic module  
**D)** System module

**Answer: B)**

**Explanation:** Code on **classpath** (not module path) belongs to the **unnamed module**.

---

### Question 9
```java
// commons-lang3-3.12.0.jar on module path (no module-info.java)
```
What is this?

**A)** Named module  
**B)** Unnamed module  
**C)** Automatic module  
**D)** System module

**Answer: C)**

**Explanation:** JAR on module path without `module-info.java` becomes **automatic module**.

---

### Question 10
```
commons-lang3-3.12.0.jar
```
What is the automatic module name?

**A)** commons-lang3-3.12.0  
**B)** commons.lang3  
**C)** commons.lang3.3.12.0  
**D)** commons-lang3

**Answer: B)**

**Explanation:** Version and hyphens removed, replaced with dots: **commons.lang3**.

---

### Question 11
Can a named module require the unnamed module?

**A)** Yes  
**B)** No  
**C)** Only with requires transitive  
**D)** Only with opens

**Answer: B)**

**Explanation:** Named modules **cannot require** the unnamed module.

---

### Question 12
```java
// Module A exports com.example.util
// Module B exports com.example.util
```
What's the problem?

**A)** Nothing  
**B)** Split package - not allowed  
**C)** Circular dependency  
**D)** Missing requires

**Answer: B)**

**Explanation:** Same package in multiple modules is a **split package** - **not allowed**.

---

### Question 13
```java
module com.example.app {
    uses com.example.service.MessageService;
}
```
What does `uses` do?

**A)** Exports service  
**B)** Declares service consumer  
**C)** Provides implementation  
**D)** Opens for reflection

**Answer: B)**

**Explanation:** `uses` declares this module **consumes** a service.

---

### Question 14
```java
module com.example.provider {
    provides com.example.service.MessageService 
        with com.example.impl.MessageServiceImpl;
}
```
What does `provides...with` do?

**A)** Declares service consumer  
**B)** Declares service provider  
**C)** Exports service  
**D)** Opens service

**Answer: B)**

**Explanation:** `provides...with` declares this module **provides** a service implementation.

---

### Question 15
```java
module my-module {
    exports com.example;
}
```
Is this valid?

**A)** Yes  
**B)** No - hyphens not allowed in module names  
**C)** Yes but deprecated  
**D)** Only for automatic modules

**Answer: B)**

**Explanation:** Module names use **dots**, not **hyphens**. Should be `my.module`.

---

### Question 16
```bash
java --module-path mods -m com.example.app/com.example.app.Main
```
What is `-m`?

**A)** Module path  
**B)** Module to run (module/class)  
**C)** Module classpath  
**D)** Module export

**Answer: B)**

**Explanation:** `-m` or `--module` specifies **module/class** to run.

---

### Question 17
What's exported by an automatic module?

**A)** Nothing  
**B)** Only public classes  
**C)** All packages  
**D)** Only specified packages

**Answer: C)**

**Explanation:** Automatic modules **export all packages**.

---

### Question 18
```java
module com.example.app {
    requires java.sql;
}

// Use Connection class
```
Can you access `java.sql.Connection`?

**A)** Yes  
**B)** No - must export  
**C)** Only with opens  
**D)** Only with transitive

**Answer: A)**

**Explanation:** `requires java.sql` gives access to **exported** packages in java.sql module.

---

### Question 19
```java
public class MessageServiceImpl implements MessageService {
    private MessageServiceImpl() {}  // private constructor
}

module provider {
    provides MessageService with MessageServiceImpl;
}
```
What's wrong?

**A)** Nothing  
**B)** Provider must have public no-arg constructor  
**C)** Missing uses  
**D)** Missing exports

**Answer: B)**

**Explanation:** Service provider class must have **public no-arg constructor**.

---

### Question 20
```java
module com.example.app {
    opens com.example.model to com.fasterxml.jackson.databind;
}
```
What does this qualified `opens` do?

**A)** Opens to all modules  
**B)** Opens only to jackson.databind  
**C)** Exports to jackson.databind  
**D)** Requires jackson.databind

**Answer: B)**

**Explanation:** Qualified `opens...to` allows reflective access **only to specified modules**.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master the module system.
- **15-17 correct**: Good understanding. Review module directives.
- **12-14 correct**: Fair grasp. Study exports, requires, opens.
- **Below 12**: Need more practice. Review module fundamentals.

---

**Previous:** [Theory - Java Module System](35-modules.md)  
**Next:** [Theory - Modular JARs and Migration](36-modular-jars.md)
