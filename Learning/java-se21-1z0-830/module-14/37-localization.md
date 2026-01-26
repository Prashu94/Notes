# Module 14: Localization and Resource Bundles

## Table of Contents
1. [Introduction to Localization](#introduction-to-localization)
2. [Locale Class](#locale-class)
3. [ResourceBundle](#resourcebundle)
4. [PropertyResourceBundle](#propertyresourcebundle)
5. [ListResourceBundle](#listresourcebundle)
6. [NumberFormat](#numberformat)
7. [DateTimeFormatter](#datetimeformatter)
8. [MessageFormat](#messageformat)
9. [Locale-Sensitive Operations](#locale-sensitive-operations)
10. [Summary and Exam Tips](#summary-and-exam-tips)

---

## Introduction to Localization

**Localization** (l10n) adapts applications for different languages and regions.

### Internationalization vs Localization

- **Internationalization (i18n)**: Design application to support multiple locales
- **Localization (l10n)**: Adapt application for specific locale (translations, formats)

### Key Concepts

```
Locale: Language + Region (e.g., en_US, fr_FR, ja_JP)
Resource Bundle: Locale-specific data (messages, labels)
Formatting: Numbers, dates, currencies per locale
```

---

## Locale Class

**Locale** represents a specific geographical, political, or cultural region.

### Creating Locales

```java
import java.util.Locale;

// Using constructors
Locale locale1 = new Locale("en");           // English
Locale locale2 = new Locale("en", "US");     // English (United States)
Locale locale3 = new Locale("fr", "FR");     // French (France)

// Using constants
Locale locale4 = Locale.US;                  // English (United States)
Locale locale5 = Locale.FRANCE;              // French (France)
Locale locale6 = Locale.JAPAN;               // Japanese (Japan)
Locale locale7 = Locale.ENGLISH;             // English (no country)
Locale locale8 = Locale.FRENCH;              // French (no country)

// Using Locale.Builder (Java 7+)
Locale locale9 = new Locale.Builder()
    .setLanguage("en")
    .setRegion("US")
    .build();

// Using Locale.forLanguageTag (BCP 47)
Locale locale10 = Locale.forLanguageTag("en-US");
Locale locale11 = Locale.forLanguageTag("zh-CN");  // Chinese (China)
```

### Locale Information

```java
Locale locale = new Locale("en", "US");

// Get language
String language = locale.getLanguage();        // "en"
String displayLanguage = locale.getDisplayLanguage();  // "English"

// Get country
String country = locale.getCountry();          // "US"
String displayCountry = locale.getDisplayCountry();    // "United States"

// Get display name
String displayName = locale.getDisplayName();  // "English (United States)"

// Language tag
String tag = locale.toLanguageTag();          // "en-US"

// Get in different locale
Locale french = Locale.FRANCE;
String displayInFrench = locale.getDisplayName(french);  
// "anglais (États-Unis)"
```

### Default Locale

```java
// Get default locale
Locale defaultLocale = Locale.getDefault();
System.out.println(defaultLocale);  // System default (e.g., en_US)

// Set default locale
Locale.setDefault(Locale.FRANCE);
System.out.println(Locale.getDefault());  // fr_FR

// Categories (Java 7+)
Locale.setDefault(Locale.Category.DISPLAY, Locale.JAPAN);
Locale.setDefault(Locale.Category.FORMAT, Locale.US);

Locale displayLocale = Locale.getDefault(Locale.Category.DISPLAY);  // ja_JP
Locale formatLocale = Locale.getDefault(Locale.Category.FORMAT);    // en_US
```

---

## ResourceBundle

**ResourceBundle** provides locale-specific data.

### ResourceBundle Hierarchy

```
Bundle_en_US.properties     (English, United States)
Bundle_en.properties        (English)
Bundle.properties           (Default)
```

### Loading ResourceBundle

```java
import java.util.ResourceBundle;

// Load bundle for default locale
ResourceBundle bundle = ResourceBundle.getBundle("messages");

// Load bundle for specific locale
ResourceBundle bundleUS = ResourceBundle.getBundle("messages", Locale.US);
ResourceBundle bundleFR = ResourceBundle.getBundle("messages", Locale.FRANCE);

// Get value
String greeting = bundle.getString("greeting");
```

### ResourceBundle Lookup

```
Requested: messages_fr_FR

Search order:
1. messages_fr_FR.properties
2. messages_fr.properties
3. messages.properties (default)
4. MissingResourceException if not found
```

---

## PropertyResourceBundle

**PropertyResourceBundle** loads from `.properties` files.

### Properties File Format

```properties
# messages.properties (default)
greeting=Hello
farewell=Goodbye
welcome=Welcome, {0}!

# messages_fr.properties (French)
greeting=Bonjour
farewell=Au revoir
welcome=Bienvenue, {0}!

# messages_es.properties (Spanish)
greeting=Hola
farewell=Adiós
welcome=¡Bienvenido, {0}!
```

### Using PropertyResourceBundle

```java
public class LocalizationExample {
    public static void main(String[] args) {
        // English
        ResourceBundle bundle = ResourceBundle.getBundle("messages", Locale.US);
        System.out.println(bundle.getString("greeting"));  // Hello
        
        // French
        ResourceBundle bundleFR = ResourceBundle.getBundle("messages", Locale.FRANCE);
        System.out.println(bundleFR.getString("greeting"));  // Bonjour
        
        // Spanish
        ResourceBundle bundleES = ResourceBundle.getBundle("messages", 
            new Locale("es", "ES"));
        System.out.println(bundleES.getString("greeting"));  // Hola
    }
}
```

### Fallback Mechanism

```java
// Request: messages_de_DE (German, Germany)
// Files:
//   messages_de.properties exists
//   messages.properties exists
//   messages_de_DE.properties does NOT exist

ResourceBundle bundle = ResourceBundle.getBundle("messages", 
    new Locale("de", "DE"));

// Uses: messages_de.properties (closest match)
```

---

## ListResourceBundle

**ListResourceBundle** is a Java class-based resource bundle.

### Creating ListResourceBundle

```java
import java.util.ListResourceBundle;

// Default bundle
public class Messages extends ListResourceBundle {
    @Override
    protected Object[][] getContents() {
        return new Object[][] {
            {"greeting", "Hello"},
            {"farewell", "Goodbye"}
        };
    }
}

// French bundle
public class Messages_fr extends ListResourceBundle {
    @Override
    protected Object[][] getContents() {
        return new Object[][] {
            {"greeting", "Bonjour"},
            {"farewell", "Au revoir"}
        };
    }
}

// Spanish bundle
public class Messages_es extends ListResourceBundle {
    @Override
    protected Object[][] getContents() {
        return new Object[][] {
            {"greeting", "Hola"},
            {"farewell", "Adiós"}
        };
    }
}
```

### Using ListResourceBundle

```java
public class ListBundleExample {
    public static void main(String[] args) {
        // English (default)
        ResourceBundle bundle = ResourceBundle.getBundle("Messages", Locale.US);
        System.out.println(bundle.getString("greeting"));  // Hello
        
        // French
        ResourceBundle bundleFR = ResourceBundle.getBundle("Messages", Locale.FRANCE);
        System.out.println(bundleFR.getString("greeting"));  // Bonjour
    }
}
```

### PropertyResourceBundle vs ListResourceBundle

| Feature | PropertyResourceBundle | ListResourceBundle |
|---------|----------------------|-------------------|
| Format | .properties file | Java class |
| Values | Strings only | Any Object |
| Compilation | Not needed | Required |
| Modification | Edit file (no recompile) | Requires recompilation |
| Priority | Lower | **Higher** (ListResourceBundle takes precedence) |

---

## NumberFormat

**NumberFormat** formats numbers according to locale.

### Number Formatting

```java
import java.text.NumberFormat;

double number = 1234567.89;

// US format
NumberFormat nfUS = NumberFormat.getInstance(Locale.US);
System.out.println(nfUS.format(number));  // 1,234,567.89

// France format
NumberFormat nfFR = NumberFormat.getInstance(Locale.FRANCE);
System.out.println(nfFR.format(number));  // 1 234 567,89

// Germany format
NumberFormat nfDE = NumberFormat.getInstance(Locale.GERMANY);
System.out.println(nfDE.format(number));  // 1.234.567,89
```

### Currency Formatting

```java
double price = 1234.56;

// US currency
NumberFormat cfUS = NumberFormat.getCurrencyInstance(Locale.US);
System.out.println(cfUS.format(price));  // $1,234.56

// France currency
NumberFormat cfFR = NumberFormat.getCurrencyInstance(Locale.FRANCE);
System.out.println(cfFR.format(price));  // 1 234,56 €

// Japan currency
NumberFormat cfJP = NumberFormat.getCurrencyInstance(Locale.JAPAN);
System.out.println(cfJP.format(price));  // ¥1,235
```

### Percent Formatting

```java
double percentage = 0.75;

// US percent
NumberFormat pfUS = NumberFormat.getPercentInstance(Locale.US);
System.out.println(pfUS.format(percentage));  // 75%

// France percent
NumberFormat pfFR = NumberFormat.getPercentInstance(Locale.FRANCE);
System.out.println(pfFR.format(percentage));  // 75 %
```

### Parsing Numbers

```java
try {
    NumberFormat nf = NumberFormat.getInstance(Locale.US);
    Number num = nf.parse("1,234.56");
    System.out.println(num.doubleValue());  // 1234.56
    
    NumberFormat cf = NumberFormat.getCurrencyInstance(Locale.US);
    Number price = cf.parse("$1,234.56");
    System.out.println(price.doubleValue());  // 1234.56
} catch (ParseException e) {
    e.printStackTrace();
}
```

---

## DateTimeFormatter

**DateTimeFormatter** formats dates/times according to locale.

### Formatting Dates

```java
import java.time.*;
import java.time.format.*;

LocalDate date = LocalDate.of(2024, 1, 15);

// Short format
DateTimeFormatter shortUS = DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
    .withLocale(Locale.US);
System.out.println(shortUS.format(date));  // 1/15/24

DateTimeFormatter shortFR = DateTimeFormatter.ofLocalizedDate(FormatStyle.SHORT)
    .withLocale(Locale.FRANCE);
System.out.println(shortFR.format(date));  // 15/01/2024

// Medium format
DateTimeFormatter mediumUS = DateTimeFormatter.ofLocalizedDate(FormatStyle.MEDIUM)
    .withLocale(Locale.US);
System.out.println(mediumUS.format(date));  // Jan 15, 2024

// Long format
DateTimeFormatter longFR = DateTimeFormatter.ofLocalizedDate(FormatStyle.LONG)
    .withLocale(Locale.FRANCE);
System.out.println(longFR.format(date));  // 15 janvier 2024

// Full format
DateTimeFormatter fullDE = DateTimeFormatter.ofLocalizedDate(FormatStyle.FULL)
    .withLocale(Locale.GERMANY);
System.out.println(fullDE.format(date));  // Montag, 15. Januar 2024
```

### Formatting Times

```java
LocalTime time = LocalTime.of(14, 30, 45);

// Short time
DateTimeFormatter timeFormatter = DateTimeFormatter.ofLocalizedTime(FormatStyle.SHORT)
    .withLocale(Locale.US);
System.out.println(timeFormatter.format(time));  // 2:30 PM

DateTimeFormatter timeFormatterFR = DateTimeFormatter.ofLocalizedTime(FormatStyle.SHORT)
    .withLocale(Locale.FRANCE);
System.out.println(timeFormatterFR.format(time));  // 14:30
```

### Custom Patterns

```java
LocalDateTime dateTime = LocalDateTime.of(2024, 1, 15, 14, 30);

// Custom pattern
DateTimeFormatter custom = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");
System.out.println(custom.format(dateTime));  // 15/01/2024 14:30

// Localized custom pattern
DateTimeFormatter customUS = DateTimeFormatter.ofPattern("EEEE, MMMM d, yyyy")
    .withLocale(Locale.US);
System.out.println(customUS.format(dateTime));  // Monday, January 15, 2024

DateTimeFormatter customFR = DateTimeFormatter.ofPattern("EEEE d MMMM yyyy")
    .withLocale(Locale.FRANCE);
System.out.println(customFR.format(dateTime));  // lundi 15 janvier 2024
```

---

## MessageFormat

**MessageFormat** creates parameterized messages.

### Basic MessageFormat

```java
import java.text.MessageFormat;

String pattern = "Hello, {0}! You have {1} messages.";
String message = MessageFormat.format(pattern, "Alice", 5);
System.out.println(message);  // Hello, Alice! You have 5 messages.
```

### With ResourceBundle

```properties
# messages.properties
welcome=Welcome, {0}!
notification=You have {0} new messages and {1} alerts.

# messages_fr.properties
welcome=Bienvenue, {0}!
notification=Vous avez {0} nouveaux messages et {1} alertes.
```

```java
ResourceBundle bundle = ResourceBundle.getBundle("messages", Locale.US);
String pattern = bundle.getString("notification");
String message = MessageFormat.format(pattern, 5, 3);
System.out.println(message);  // You have 5 new messages and 3 alerts.

ResourceBundle bundleFR = ResourceBundle.getBundle("messages", Locale.FRANCE);
String patternFR = bundleFR.getString("notification");
String messageFR = MessageFormat.format(patternFR, 5, 3);
System.out.println(messageFR);  // Vous avez 5 nouveaux messages et 3 alertes.
```

### Advanced Formatting

```java
// Number formatting
String pattern1 = "Price: {0,number,currency}";
String message1 = MessageFormat.format(pattern1, 1234.56);
System.out.println(message1);  // Price: $1,234.56

// Date formatting
String pattern2 = "Date: {0,date,long}";
String message2 = MessageFormat.format(pattern2, new Date());
System.out.println(message2);  // Date: January 15, 2024

// Choice format
String pattern3 = "There {0,choice,0#are no files|1#is one file|1<are {0,number,integer} files}.";
System.out.println(MessageFormat.format(pattern3, 0));  // There are no files.
System.out.println(MessageFormat.format(pattern3, 1));  // There is one file.
System.out.println(MessageFormat.format(pattern3, 5));  // There are 5 files.
```

---

## Locale-Sensitive Operations

### String Comparison

```java
import java.text.Collator;

String s1 = "élève";
String s2 = "école";

// Default comparison (not locale-aware)
System.out.println(s1.compareTo(s2));  // Positive (e acute > e)

// Locale-sensitive comparison
Collator collatorFR = Collator.getInstance(Locale.FRANCE);
System.out.println(collatorFR.compare(s1, s2));  // Negative (école comes first)
```

### Case Conversion

```java
String text = "istanbul";

// Default (English)
System.out.println(text.toUpperCase());  // ISTANBUL

// Turkish locale (i → İ, I → ı)
Locale turkish = new Locale("tr", "TR");
System.out.println(text.toUpperCase(turkish));  // İSTANBUL
```

---

## Summary and Exam Tips

### Locale Creation

```java
new Locale("en", "US")              // Constructor
Locale.US                           // Constant
Locale.forLanguageTag("en-US")      // Language tag
new Locale.Builder()
    .setLanguage("en")
    .setRegion("US")
    .build()                        // Builder
```

### ResourceBundle Loading

```
Search order for messages_fr_FR:
1. messages_fr_FR.properties
2. messages_fr.properties
3. messages.properties

ListResourceBundle has priority over PropertyResourceBundle
```

### Exam Tips

- Locale format: **language_COUNTRY** (e.g., en_US, fr_FR)
- `ResourceBundle.getBundle()` uses fallback mechanism
- **ListResourceBundle** takes precedence over **PropertyResourceBundle**
- PropertyResourceBundle values are **Strings only**
- ListResourceBundle values can be **any Object**
- `NumberFormat.getInstance()` for numbers
- `NumberFormat.getCurrencyInstance()` for currency
- `NumberFormat.getPercentInstance()` for percentages
- `DateTimeFormatter.ofLocalizedDate()` for dates
- `MessageFormat.format()` for parameterized messages
- `{0}`, `{1}` are placeholders in MessageFormat
- Default locale: `Locale.getDefault()`

---

**Previous:** [Module 13 - Practice Questions](../module-13/36-practice-questions.md)  
**Next:** [Practice Questions - Localization](37-practice-questions.md)
