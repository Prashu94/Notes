# Module 14: Practice Questions - Localization and Resource Bundles

## Questions (20)

---

### Question 1
```java
Locale locale = new Locale("en", "US");
```
What does this create?

**A)** English  
**B)** English (United States)  
**C)** United States  
**D)** Compilation error

**Answer: B)**

**Explanation:** Creates Locale for **English (United States)**: language "en", country "US".

---

### Question 2
```java
Locale locale = Locale.FRANCE;
String language = locale.getLanguage();
```
What is `language`?

**A)** "France"  
**B)** "French"  
**C)** "fr"  
**D)** "FR"

**Answer: C)**

**Explanation:** `getLanguage()` returns **language code**: "fr" (not display name).

---

### Question 3
```java
ResourceBundle bundle = ResourceBundle.getBundle("messages", Locale.FRANCE);
```
What's the search order?

**A)** messages.properties only  
**B)** messages_fr_FR, messages_fr, messages  
**C)** messages_fr, messages_fr_FR, messages  
**D)** messages_FR, messages

**Answer: B)**

**Explanation:** Search order: **messages_fr_FR** → **messages_fr** → **messages** (fallback).

---

### Question 4
```
Files exist:
- messages.properties
- messages_fr.properties
- Messages_fr.class (ListResourceBundle)
```
Which is loaded for Locale.FRANCE?

**A)** messages.properties  
**B)** messages_fr.properties  
**C)** Messages_fr.class  
**D)** Error

**Answer: C)**

**Explanation:** **ListResourceBundle** (class) takes **precedence** over PropertyResourceBundle (.properties).

---

### Question 5
```properties
# messages.properties
greeting=Hello, {0}!
```
```java
ResourceBundle bundle = ResourceBundle.getBundle("messages");
String pattern = bundle.getString("greeting");
String message = MessageFormat.format(pattern, "Alice");
```
What is `message`?

**A)** "Hello, {0}!"  
**B)** "Hello, Alice!"  
**C)** "Hello, 0!"  
**D)** Compilation error

**Answer: B)**

**Explanation:** `MessageFormat.format()` replaces **{0}** with "Alice": **"Hello, Alice!"**.

---

### Question 6
```java
double price = 1234.56;
NumberFormat cf = NumberFormat.getCurrencyInstance(Locale.US);
System.out.println(cf.format(price));
```
What is printed?

**A)** 1234.56  
**B)** $1,234.56  
**C)** 1,234.56 USD  
**D)** $1234.56

**Answer: B)**

**Explanation:** US currency format: **$1,234.56** (symbol, comma separator, 2 decimals).

---

### Question 7
```java
double percent = 0.75;
NumberFormat pf = NumberFormat.getPercentInstance(Locale.US);
System.out.println(pf.format(percent));
```
What is printed?

**A)** 0.75  
**B)** 75  
**C)** 75%  
**D)** 0.75%

**Answer: C)**

**Explanation:** Percent format converts 0.75 to **75%**.

---

### Question 8
```java
LocalDate date = LocalDate.of(2024, 1, 15);
DateTimeFormatter formatter = DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
    .withLocale(Locale.US);
System.out.println(formatter.format(date));
```
What is printed?

**A)** 2024-01-15  
**B)** 1/15/24  
**C)** 01/15/2024  
**D)** January 15, 2024

**Answer: B)**

**Explanation:** SHORT format in US locale: **1/15/24**.

---

### Question 9
```java
Locale locale = Locale.getDefault();
Locale.setDefault(Locale.FRANCE);
System.out.println(Locale.getDefault().getLanguage());
```
What is printed?

**A)** en  
**B)** fr  
**C)** France  
**D)** Depends on system

**Answer: B)**

**Explanation:** After `setDefault(Locale.FRANCE)`, default locale is France with language **"fr"**.

---

### Question 10
```java
public class Messages extends ListResourceBundle {
    protected Object[][] getContents() {
        return new Object[][] {
            {"greeting", "Hello"}
        };
    }
}
```
What can values be?

**A)** Strings only  
**B)** Any Object  
**C)** Numbers only  
**D)** Dates only

**Answer: B)**

**Explanation:** ListResourceBundle values can be **any Object** type.

---

### Question 11
```properties
# messages.properties
greeting=Hello
```
What type are PropertyResourceBundle values?

**A)** String only  
**B)** Object  
**C)** CharSequence  
**D)** Any type

**Answer: A)**

**Explanation:** PropertyResourceBundle (.properties files) values are **Strings only**.

---

### Question 12
```java
Locale locale = Locale.forLanguageTag("en-US");
```
What is this?

**A)** Invalid syntax  
**B)** BCP 47 language tag  
**C)** Compilation error  
**D)** Deprecated

**Answer: B)**

**Explanation:** `forLanguageTag()` uses **BCP 47** language tags: "en-US".

---

### Question 13
```java
ResourceBundle bundle = ResourceBundle.getBundle("messages", 
    new Locale("de", "DE"));
```
Files exist: messages.properties, messages_fr.properties

Which is used?

**A)** messages_fr.properties  
**B)** messages.properties  
**C)** MissingResourceException  
**D)** messages_de.properties created

**Answer: B)**

**Explanation:** No German bundle → falls back to **messages.properties** (default).

---

### Question 14
```java
double number = 1234.89;
NumberFormat nf = NumberFormat.getInstance(Locale.FRANCE);
System.out.println(nf.format(number));
```
What is printed?

**A)** 1,234.89  
**B)** 1.234,89  
**C)** 1 234,89  
**D)** 1234.89

**Answer: C)**

**Explanation:** French number format uses **space** as thousands separator, **comma** as decimal: **1 234,89**.

---

### Question 15
```java
String pattern = "Price: {0,number,currency}";
String message = MessageFormat.format(pattern, 1234.56);
```
What does `{0,number,currency}` do?

**A)** Formats as number  
**B)** Formats as currency  
**C)** Formats as percent  
**D)** Compilation error

**Answer: B)**

**Explanation:** `{0,number,currency}` formats parameter as **currency**: $1,234.56.

---

### Question 16
```java
Locale locale = new Locale("en", "US");
String displayName = locale.getDisplayName(Locale.FRANCE);
```
What is `displayName`?

**A)** "English (United States)"  
**B)** "anglais (États-Unis)"  
**C)** "en_US"  
**D)** "United States"

**Answer: B)**

**Explanation:** `getDisplayName(Locale.FRANCE)` returns display name **in French**: "anglais (États-Unis)".

---

### Question 17
```java
ResourceBundle bundle = ResourceBundle.getBundle("messages");
String value = bundle.getString("unknown.key");
```
What if key doesn't exist?

**A)** Returns null  
**B)** Returns empty string  
**C)** MissingResourceException  
**D)** Returns "unknown.key"

**Answer: C)**

**Explanation:** `getString()` throws **MissingResourceException** if key not found.

---

### Question 18
```java
Locale locale = new Locale.Builder()
    .setLanguage("en")
    .setRegion("US")
    .build();
```
What is this?

**A)** Invalid syntax  
**B)** Locale.Builder pattern (Java 7+)  
**C)** Deprecated  
**D)** Compilation error

**Answer: B)**

**Explanation:** **Locale.Builder** is a fluent API for creating Locales (Java 7+).

---

### Question 19
```java
Locale locale = new Locale("tr", "TR");  // Turkish
String text = "istanbul";
System.out.println(text.toUpperCase(locale));
```
What is printed?

**A)** ISTANBUL  
**B)** İSTANBUL  
**C)** istanbul  
**D)** Istanbul

**Answer: B)**

**Explanation:** Turkish locale: lowercase 'i' → uppercase **'İ'** (dotted capital I): **İSTANBUL**.

---

### Question 20
```java
Locale.setDefault(Locale.Category.DISPLAY, Locale.JAPAN);
Locale.setDefault(Locale.Category.FORMAT, Locale.US);
```
What are categories for?

**A)** Different defaults for UI and formatting  
**B)** Display only  
**C)** Format only  
**D)** No effect

**Answer: A)**

**Explanation:** Categories allow **different defaults**: **DISPLAY** for UI (ja_JP), **FORMAT** for numbers/dates (en_US).

---

## Score Interpretation

- **18-20 correct**: Excellent! You master localization.
- **15-17 correct**: Good understanding. Review ResourceBundle and formatting.
- **12-14 correct**: Fair grasp. Study Locale and MessageFormat.
- **Below 12**: Need more practice. Review all localization topics.

---

**Previous:** [Theory - Localization and Resource Bundles](37-localization.md)  
**Next:** [Theory - Logging and Annotations](38-logging.md)
