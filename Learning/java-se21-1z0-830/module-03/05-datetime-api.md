# Module 3.1: Date-Time API - LocalDate, LocalTime, LocalDateTime

## 📚 Table of Contents
1. [Overview](#overview)
2. [The Old Date/Time Problems](#the-old-datetime-problems)
3. [LocalDate](#localdate)
4. [LocalTime](#localtime)
5. [LocalDateTime](#localdatetime)
6. [Period and Duration](#period-and-duration)
7. [Formatting and Parsing](#formatting-and-parsing)
8. [Best Practices](#best-practices)

---

## Overview

The **Java Date-Time API** (java.time package) was introduced in Java 8 to replace the problematic old `java.util.Date` and `java.util.Calendar` classes. It provides immutable, thread-safe classes for date and time manipulation.

**Key Classes:**
- `LocalDate` - Date without time or timezone
- `LocalTime` - Time without date or timezone  
- `LocalDateTime` - Date and time without timezone
- `ZonedDateTime` - Date and time with timezone
- `Instant` - Timestamp (epoch seconds)
- `Period` - Date-based amount (years, months, days)
- `Duration` - Time-based amount (hours, minutes, seconds)

---

## The Old Date/Time Problems

```java
// ❌ OLD API (Deprecated, don't use)
Date date = new Date();  // Mutable, not thread-safe
date.setYear(121);       // Year is 1900-based!
date.setMonth(0);        // Months are 0-indexed (January = 0)

Calendar cal = Calendar.getInstance();
cal.set(2024, 0, 15);    // Still 0-indexed months!

// ✅ NEW API (Use this!)
LocalDate today = LocalDate.now();
LocalDate date = LocalDate.of(2024, 1, 15);  // 1-indexed months
LocalDate date2 = LocalDate.of(2024, Month.JANUARY, 15);
```

---

## LocalDate

**Represents a date without time-zone** (e.g., 2024-01-15).

### Creating LocalDate

```java
// Current date
LocalDate today = LocalDate.now();  // 2024-01-15

// Specific date
LocalDate date1 = LocalDate.of(2024, 1, 15);  // 2024-01-15
LocalDate date2 = LocalDate.of(2024, Month.JANUARY, 15);  // Using Month enum

// From string (ISO format: yyyy-MM-dd)
LocalDate date3 = LocalDate.parse("2024-01-15");

// Epoch day (days since 1970-01-01)
LocalDate date4 = LocalDate.ofEpochDay(0);  // 1970-01-01
LocalDate date5 = LocalDate.ofEpochDay(19737);  // 2024-01-15

// Year and day of year
LocalDate date6 = LocalDate.ofYearDay(2024, 15);  // 15th day of 2024
```

### Getting Components

```java
LocalDate date = LocalDate.of(2024, 1, 15);

int year = date.getYear();           // 2024
int month = date.getMonthValue();    // 1 (January)
Month monthEnum = date.getMonth();   // JANUARY
int day = date.getDayOfMonth();      // 15
int dayOfYear = date.getDayOfYear(); // 15
DayOfWeek dayOfWeek = date.getDayOfWeek();  // MONDAY

// Checking properties
boolean isLeap = date.isLeapYear();  // true (2024 is leap year)
```

### Manipulating Dates (Returns new instance - immutable!)

```java
LocalDate date = LocalDate.of(2024, 1, 15);

// Adding
LocalDate plusDays = date.plusDays(10);      // 2024-01-25
LocalDate plusWeeks = date.plusWeeks(2);     // 2024-01-29
LocalDate plusMonths = date.plusMonths(3);   // 2024-04-15
LocalDate plusYears = date.plusYears(1);     // 2025-01-15

// Subtracting
LocalDate minusDays = date.minusDays(10);    // 2024-01-05
LocalDate minusWeeks = date.minusWeeks(1);   // 2024-01-08
LocalDate minusMonths = date.minusMonths(1); // 2023-12-15
LocalDate minusYears = date.minusYears(1);   // 2023-01-15

// With (replacing components)
LocalDate withYear = date.withYear(2025);    // 2025-01-15
LocalDate withMonth = date.withMonth(6);     // 2024-06-15
LocalDate withDay = date.withDayOfMonth(1);  // 2024-01-01
LocalDate withDayOfYear = date.withDayOfYear(100);  // 100th day of 2024
```

### Comparing Dates

```java
LocalDate date1 = LocalDate.of(2024, 1, 15);
LocalDate date2 = LocalDate.of(2024, 6, 15);

// Comparison
boolean isBefore = date1.isBefore(date2);  // true
boolean isAfter = date1.isAfter(date2);    // false
boolean isEqual = date1.isEqual(date1);    // true

// compareTo
int comparison = date1.compareTo(date2);   // negative (date1 < date2)
```

### Other Useful Methods

```java
LocalDate date = LocalDate.of(2024, 2, 15);

// Length of month/year
int lengthOfMonth = date.lengthOfMonth();  // 29 (February 2024 - leap year)
int lengthOfYear = date.lengthOfYear();    // 366

// Min/Max
LocalDate min = LocalDate.MIN;  // -999999999-01-01
LocalDate max = LocalDate.MAX;  // +999999999-12-31

// Until
long daysBetween = date.until(LocalDate.of(2024, 3, 15), ChronoUnit.DAYS);  // 29
```

---

## LocalTime

**Represents a time without date or time-zone** (e.g., 14:30:15).

### Creating LocalTime

```java
// Current time
LocalTime now = LocalTime.now();  // 14:30:15.123456789

// Specific time
LocalTime time1 = LocalTime.of(14, 30);          // 14:30:00
LocalTime time2 = LocalTime.of(14, 30, 15);      // 14:30:15
LocalTime time3 = LocalTime.of(14, 30, 15, 123); // 14:30:15.000000123

// From string (ISO format: HH:mm:ss)
LocalTime time4 = LocalTime.parse("14:30:15");

// Special times
LocalTime midnight = LocalTime.MIDNIGHT;  // 00:00:00
LocalTime noon = LocalTime.NOON;          // 12:00:00
LocalTime min = LocalTime.MIN;            // 00:00:00
LocalTime max = LocalTime.MAX;            // 23:59:59.999999999

// From seconds/nanos of day
LocalTime time5 = LocalTime.ofSecondOfDay(3661);  // 01:01:01
LocalTime time6 = LocalTime.ofNanoOfDay(1000000000L);  // 00:00:01
```

### Getting Components

```java
LocalTime time = LocalTime.of(14, 30, 15, 123456789);

int hour = time.getHour();        // 14
int minute = time.getMinute();    // 30
int second = time.getSecond();    // 15
int nano = time.getNano();        // 123456789

long secondOfDay = time.toSecondOfDay();  // 52215
long nanoOfDay = time.toNanoOfDay();      // 52215123456789
```

### Manipulating Time

```java
LocalTime time = LocalTime.of(14, 30, 15);

// Adding
LocalTime plusHours = time.plusHours(2);     // 16:30:15
LocalTime plusMinutes = time.plusMinutes(45); // 15:15:15
LocalTime plusSeconds = time.plusSeconds(30); // 14:30:45
LocalTime plusNanos = time.plusNanos(1000);  // 14:30:15.000001

// Subtracting
LocalTime minusHours = time.minusHours(2);   // 12:30:15
LocalTime minusMinutes = time.minusMinutes(45); // 13:45:15

// With
LocalTime withHour = time.withHour(10);      // 10:30:15
LocalTime withMinute = time.withMinute(0);   // 14:00:15
LocalTime withSecond = time.withSecond(0);   // 14:30:00
LocalTime withNano = time.withNano(0);       // 14:30:15

// Wraps around midnight
LocalTime wrapped = time.plusHours(15);      // 05:30:15 (next day)
```

### Comparing Times

```java
LocalTime time1 = LocalTime.of(10, 30);
LocalTime time2 = LocalTime.of(14, 30);

boolean isBefore = time1.isBefore(time2);  // true
boolean isAfter = time1.isAfter(time2);    // false
int comparison = time1.compareTo(time2);   // negative
```

---

## LocalDateTime

**Combines LocalDate and LocalTime** (e.g., 2024-01-15T14:30:15).

### Creating LocalDateTime

```java
// Current date-time
LocalDateTime now = LocalDateTime.now();  // 2024-01-15T14:30:15.123456789

// From date and time components
LocalDateTime dt1 = LocalDateTime.of(2024, 1, 15, 14, 30);  // 2024-01-15T14:30:00
LocalDateTime dt2 = LocalDateTime.of(2024, 1, 15, 14, 30, 15);  // With seconds
LocalDateTime dt3 = LocalDateTime.of(2024, 1, 15, 14, 30, 15, 123);  // With nanos

// From LocalDate and LocalTime
LocalDate date = LocalDate.of(2024, 1, 15);
LocalTime time = LocalTime.of(14, 30, 15);
LocalDateTime dt4 = LocalDateTime.of(date, time);  // 2024-01-15T14:30:15

// From string (ISO format: yyyy-MM-ddTHH:mm:ss)
LocalDateTime dt5 = LocalDateTime.parse("2024-01-15T14:30:15");

// From LocalDate
LocalDateTime dt6 = date.atTime(14, 30);  // Combines with time
LocalDateTime dt7 = date.atStartOfDay();  // 2024-01-15T00:00:00

// From LocalTime
LocalDateTime dt8 = time.atDate(date);  // Combines with date
```

### Getting Components

```java
LocalDateTime dt = LocalDateTime.of(2024, 1, 15, 14, 30, 15);

// Date components
int year = dt.getYear();           // 2024
int month = dt.getMonthValue();    // 1
int day = dt.getDayOfMonth();      // 15
LocalDate datepart = dt.toLocalDate();  // 2024-01-15

// Time components
int hour = dt.getHour();           // 14
int minute = dt.getMinute();       // 30
int second = dt.getSecond();       // 15
LocalTime timepart = dt.toLocalTime();  // 14:30:15
```

### Manipulating LocalDateTime

```java
LocalDateTime dt = LocalDateTime.of(2024, 1, 15, 14, 30, 15);

// Date operations
LocalDateTime plusDays = dt.plusDays(10);      // 2024-01-25T14:30:15
LocalDateTime plusMonths = dt.plusMonths(3);   // 2024-04-15T14:30:15

// Time operations
LocalDateTime plusHours = dt.plusHours(5);     // 2024-01-15T19:30:15
LocalDateTime plusMinutes = dt.plusMinutes(45); // 2024-01-15T15:15:15

// Combined
LocalDateTime later = dt.plusDays(1).plusHours(2);  // 2024-01-16T16:30:15

// With operations
LocalDateTime modified = dt.withYear(2025)
                           .withMonth(6)
                           .withHour(10)
                           .withMinute(0);  // 2025-06-15T10:00:15
```

---

## Period and Duration

### Period - Date-based amount

```java
// Creating periods
Period period1 = Period.ofDays(10);        // 10 days
Period period2 = Period.ofWeeks(2);        // 14 days
Period period3 = Period.ofMonths(3);       // 3 months
Period period4 = Period.ofYears(1);        // 1 year
Period period5 = Period.of(1, 6, 15);      // 1 year, 6 months, 15 days

// Between dates
LocalDate start = LocalDate.of(2024, 1, 15);
LocalDate end = LocalDate.of(2024, 6, 20);
Period between = Period.between(start, end);  // 5 months, 5 days

// Getting components
int years = period5.getYears();      // 1
int months = period5.getMonths();    // 6
int days = period5.getDays();        // 15

// Using with dates
LocalDate date = LocalDate.of(2024, 1, 15);
LocalDate newDate = date.plus(period5);  // 2025-07-30
LocalDate earlier = date.minus(Period.ofMonths(3));  // 2023-10-15
```

### Duration - Time-based amount

```java
// Creating durations
Duration duration1 = Duration.ofDays(1);      // 24 hours
Duration duration2 = Duration.ofHours(2);     // 2 hours
Duration duration3 = Duration.ofMinutes(30);  // 30 minutes
Duration duration4 = Duration.ofSeconds(45);  // 45 seconds
Duration duration5 = Duration.ofMillis(1000); // 1 second
Duration duration6 = Duration.ofNanos(1000000); // 1 millisecond

// Between times/datetimes
LocalTime start = LocalTime.of(10, 0);
LocalTime end = LocalTime.of(14, 30);
Duration between = Duration.between(start, end);  // 4 hours 30 minutes

// Getting components
long seconds = duration2.getSeconds();  // 7200
int nanos = duration2.getNano();        // 0
long days = duration1.toDays();         // 1
long hours = duration1.toHours();       // 24
long minutes = duration1.toMinutes();   // 1440

// Using with time
LocalTime time = LocalTime.of(10, 0);
LocalTime newTime = time.plus(duration2);  // 12:00:00
```

---

## Formatting and Parsing

### Predefined Formatters

```java
LocalDate date = LocalDate.of(2024, 1, 15);
LocalTime time = LocalTime.of(14, 30, 15);
LocalDateTime dt = LocalDateTime.of(date, time);

// ISO formats
String isoDate = date.format(DateTimeFormatter.ISO_DATE);  // "2024-01-15"
String isoTime = time.format(DateTimeFormatter.ISO_TIME);  // "14:30:15"
String isoDateTime = dt.format(DateTimeFormatter.ISO_DATE_TIME);  // "2024-01-15T14:30:15"

// Basic ISO
String basic = date.format(DateTimeFormatter.BASIC_ISO_DATE);  // "20240115"
```

### Custom Formatters

```java
LocalDateTime dt = LocalDateTime.of(2024, 1, 15, 14, 30);

// Custom pattern
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm");
String formatted = dt.format(formatter);  // "15/01/2024 14:30"

// Common patterns
DateTimeFormatter f1 = DateTimeFormatter.ofPattern("yyyy-MM-dd");
DateTimeFormatter f2 = DateTimeFormatter.ofPattern("dd-MMM-yyyy");  // "15-Jan-2024"
DateTimeFormatter f3 = DateTimeFormatter.ofPattern("EEEE, MMMM dd, yyyy");  // "Monday, January 15, 2024"

// Pattern symbols:
// yyyy - year (2024)
// MM - month as number (01-12)
// MMM - month short name (Jan)
// MMMM - month full name (January)
// dd - day of month (01-31)
// EEE - day of week short (Mon)
// EEEE - day of week full (Monday)
// HH - hour (00-23)
// mm - minute (00-59)
// ss - second (00-59)
```

### Parsing

```java
// Using predefined formatters
LocalDate date1 = LocalDate.parse("2024-01-15");  // ISO format
LocalTime time1 = LocalTime.parse("14:30:15");

// Using custom formatters
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy");
LocalDate date2 = LocalDate.parse("15/01/2024", formatter);

DateTimeFormatter dtFormatter = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm");
LocalDateTime dt = LocalDateTime.parse("15-01-2024 14:30", dtFormatter);

// Invalid formats throw DateTimeParseException
// LocalDate invalid = LocalDate.parse("2024/01/15");  // Exception!
```

---

## Best Practices

### ✅ DO:

1. **Use the new Date-Time API** (java.time)
   ```java
   LocalDate date = LocalDate.now();
   ```

2. **Remember immutability** - methods return new instances
   ```java
   LocalDate date = LocalDate.now();
   date.plusDays(5);  // Does nothing!
   date = date.plusDays(5);  // Correct
   ```

3. **Use appropriate types**
   - `LocalDate` for date only
   - `LocalTime` for time only
   - `LocalDateTime` for date and time
   - `ZonedDateTime` for date, time, and timezone

4. **Use Period for dates, Duration for time**
   ```java
   Period p = Period.ofMonths(3);
   Duration d = Duration.ofHours(2);
   ```

### ❌ DON'T:

1. **Don't use old Date/Calendar classes**
   ```java
   // Bad
   Date date = new Date();
   
   // Good
   LocalDate date = LocalDate.now();
   ```

2. **Don't forget results are immutable**
   ```java
   // Bad - doesn't change date
   LocalDate date = LocalDate.now();
   date.plusDays(5);
   
   // Good
   date = date.plusDays(5);
   ```

---

## Summary

- **LocalDate** - Date without time or timezone
- **LocalTime** - Time without date or timezone
- **LocalDateTime** - Date and time without timezone
- All classes are **immutable** and **thread-safe**
- **Period** - Date-based durations (years, months, days)
- **Duration** - Time-based durations (hours, minutes, seconds)
- Use **DateTimeFormatter** for formatting and parsing
- Months are **1-indexed** (January = 1, not 0)

---

## Next Steps

Proceed to [Practice Questions](05-practice-questions.md) to test your understanding!
