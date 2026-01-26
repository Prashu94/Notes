# Module 13: Practice Questions - Modular JARs and Migration

## Questions (20)

---

### Question 1
```bash
jar --create --file mymodule.jar -C out .
```
What does this create?

**A)** Regular JAR  
**B)** Modular JAR if module-info.class exists  
**C)** Automatic module  
**D)** Compilation error

**Answer: B)**

**Explanation:** Creates **modular JAR** if `module-info.class` exists in `out` directory.

---

### Question 2
```bash
jar --describe-module --file mymodule.jar
```
What does this do?

**A)** Extracts JAR  
**B)** Shows module descriptor  
**C)** Compiles module  
**D)** Lists files

**Answer: B)**

**Explanation:** `--describe-module` (or `-d`) displays the **module descriptor** from JAR.

---

### Question 3
```bash
jar -tf myapp.jar
```
What does this do?

**A)** Creates JAR  
**B)** Extracts JAR  
**C)** Lists JAR contents  
**D)** Updates JAR

**Answer: C)**

**Explanation:** `-tf` (--list --file) **lists** JAR contents.

---

### Question 4
```bash
jdeps myapp.jar
```
What does jdeps do?

**A)** Creates JAR  
**B)** Analyzes dependencies  
**C)** Runs application  
**D)** Compiles code

**Answer: B)**

**Explanation:** `jdeps` **analyzes** class and module dependencies.

---

### Question 5
```bash
jdeps --generate-module-info . myapp.jar
```
What does this generate?

**A)** JAR file  
**B)** Suggested module-info.java  
**C)** Compiled classes  
**D)** Runtime image

**Answer: B)**

**Explanation:** Generates **suggested module-info.java** based on dependencies.

---

### Question 6
```bash
jlink --module-path mods --add-modules com.example.app --output runtime
```
What does jlink create?

**A)** JAR file  
**B)** Custom runtime image  
**C)** Module descriptor  
**D)** Compiled classes

**Answer: B)**

**Explanation:** `jlink` creates **custom runtime image** with only required modules.

---

### Question 7
What's included in a custom jlink runtime?

**A)** All JDK modules  
**B)** Only specified modules and dependencies  
**C)** Source code  
**D)** Development tools

**Answer: B)**

**Explanation:** Custom runtime includes **only specified modules** and their dependencies.

---

### Question 8
```bash
jlink --compress 2 --module-path mods --add-modules app --output runtime
```
What does `--compress 2` do?

**A)** Compresses source code  
**B)** Compresses runtime image  
**C)** Compiles faster  
**D)** Nothing

**Answer: B)**

**Explanation:** `--compress 2` **compresses** runtime image for smaller size.

---

### Question 9
```
commons-lang3-3.12.0.jar (no module-info.java)
```
What module name on module path?

**A)** commons-lang3-3.12.0  
**B)** commons.lang3  
**C)** commons.lang3.3.12.0  
**D)** commons-lang3

**Answer: B)**

**Explanation:** Automatic module name: remove version and special chars → **commons.lang3**.

---

### Question 10
What's bottom-up migration?

**A)** Migrate application first  
**B)** Migrate lowest-level dependencies first  
**C)** Migrate randomly  
**D)** No migration needed

**Answer: B)**

**Explanation:** Bottom-up migrates **dependencies first**, then application.

---

### Question 11
What's top-down migration?

**A)** Migrate dependencies first  
**B)** Migrate application, use automatic modules for dependencies  
**C)** Migrate randomly  
**D)** No migration

**Answer: B)**

**Explanation:** Top-down migrates **application first**, dependencies as **automatic modules**.

---

### Question 12
```bash
jar --create --file app.jar --main-class com.example.Main -C out .
```
How to run this JAR?

**A)** java -cp app.jar Main  
**B)** java -jar app.jar  
**C)** java -m app.jar  
**D)** java app.jar

**Answer: B)**

**Explanation:** JAR with `--main-class` runs with `java -jar`.

---

### Question 13
```bash
jdeps --jdk-internals myapp.jar
```
What does this check?

**A)** Module dependencies  
**B)** Internal JDK API usage  
**C)** JAR size  
**D)** Performance

**Answer: B)**

**Explanation:** `--jdk-internals` detects usage of **internal JDK APIs** (e.g., sun.misc.Unsafe).

---

### Question 14
What's required in a modular JAR?

**A)** META-INF/MANIFEST.MF  
**B)** module-info.class  
**C)** pom.xml  
**D)** Nothing special

**Answer: B)**

**Explanation:** Modular JAR must contain **module-info.class** in root.

---

### Question 15
```bash
jar -xf myapp.jar
```
What does this do?

**A)** Creates JAR  
**B)** Extracts JAR contents  
**C)** Lists JAR  
**D)** Updates JAR

**Answer: B)**

**Explanation:** `-xf` (--extract --file) **extracts** JAR contents.

---

### Question 16
```bash
jlink --strip-debug --module-path mods --add-modules app --output runtime
```
What does `--strip-debug` do?

**A)** Removes debug symbols  
**B)** Adds debug info  
**C)** Debugs application  
**D)** Nothing

**Answer: A)**

**Explanation:** `--strip-debug` **removes debug symbols** to reduce runtime size.

---

### Question 17
Can jlink create runtime from classpath?

**A)** Yes  
**B)** No - requires module path  
**C)** Only with automatic modules  
**D)** Only with unnamed module

**Answer: B)**

**Explanation:** `jlink` requires **module path**, not classpath.

---

### Question 18
```bash
jar --module-version 1.0.0 --create --file app.jar -C out .
```
Where is version stored?

**A)** module-info.java  
**B)** JAR manifest  
**C)** Separate file  
**D)** Not stored

**Answer: B)**

**Explanation:** `--module-version` stores version in **JAR manifest**.

---

### Question 19
What happens with split packages in modules?

**A)** Works fine  
**B)** Compilation error  
**C)** Runtime warning  
**D)** Performance issue

**Answer: B)**

**Explanation:** **Split packages** (same package in multiple modules) cause **compilation error**.

---

### Question 20
```bash
jlink --launcher myapp=com.example.app/com.example.app.Main \
      --module-path mods --add-modules com.example.app --output runtime
```
What does `--launcher` create?

**A)** JAR file  
**B)** Executable script to run application  
**C)** Module descriptor  
**D)** Manifest

**Answer: B)**

**Explanation:** `--launcher` creates **executable script** in `runtime/bin/` directory.

---

## Score Interpretation

- **18-20 correct**: Excellent! You master modular JARs and migration.
- **15-17 correct**: Good understanding. Review jdeps and jlink.
- **12-14 correct**: Fair grasp. Study JAR commands and migration.
- **Below 12**: Need more practice. Review all topics.

---

**Module 13 Complete!**

**Previous:** [Theory - Modular JARs and Migration](36-modular-jars.md)  
**Next:** [Module 14 - Localization and Logging](../module-14/37-localization.md)
