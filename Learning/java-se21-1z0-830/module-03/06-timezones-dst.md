# Module 3.2: Time Zones and Daylight Saving Time

## 📚 Table of Contents
1. [Introduction](#introduction)
2. [ZonedDateTime](#zoneddatetime)
3. [ZoneId and ZoneOffset](#zoneid-and-zoneoffset)
4. [Instant](#instant)
5. [Daylight Saving Time](#daylight-saving-time)
6. [Converting Between Time Zones](#converting-between-time-zones)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)

---

## Introduction

While LocalDate, LocalTime, and LocalDateTime represent dates and times without timezone information, real-world applications often need to work with specific time zones. Java's Date-Time API provides classes like ZonedDateTime, ZoneId, and Instant to handle timezone-aware operations.

### Why Time Zones Matter

- Global applications need to display times in user's local timezone
- Scheduling across time zones requires careful handling
- Daylight Saving Time changes must be accounted for
- Database timestamps often use UTC

---

## ZonedDateTime

ZonedDateTime combines a date, time, and timezone. It's the most complete representation of a point in time.

### Creating ZonedDateTime

```java
// Current date-time in system default timezone
ZonedDateTime now = ZonedDateTime.now();

// Specific timezone
ZonedDateTime tokyo = ZonedDateTime.now(ZoneId.of("Asia/Tokyo"));

// From LocalDateTime
LocalDateTime ldt = LocalDateTime.of(2024, 1, 15, 14, 30);
ZonedDateTime zdt = ldt.atZone(ZoneId.of("America/New_York"));

// Direct construction
ZonedDateTime zdt2 = ZonedDateTime.of(2024, 1, 15, 14, 30, 0, 0,
                                       ZoneId.of("Europe/London"));
```

### ZonedDateTime Components

```java
ZonedDateTime zdt = ZonedDateTime.now(ZoneId.of("America/New_York"));

// Date components
int year = zdt.getYear();          // 2024
int month = zdt.getMonthValue();   // 1
int day = zdt.getDayOfMonth();     // 15

// Time components
int hour = zdt.getHour();          // 14
int minute = zdt.getMinute();      // 30

// Timezone components
ZoneId zone = zdt.getZone();       // America/New_York
ZoneOffset offset = zdt.getOffset(); // -05:00 (or -04:00 in DST)
```

### Manipulating ZonedDateTime

```java
ZonedDateTime zdt = ZonedDateTime.now();

// Add/subtract (immutable - returns new object)
ZonedDateTime tomorrow = zdt.plusDays(1);
ZonedDateTime nextWeek = zdt.plusWeeks(1);
ZonedDateTime yesterday = zdt.minusDays(1);

// With methods (replace components)
ZonedDateTime newTime = zdt.withHour(10).withMinute(0);
```

---

## ZoneId and ZoneOffset

### ZoneId

ZoneId represents a time zone, like "America/New_York" or "Europe/Paris".

```java
// Get system default timezone
ZoneId defaultZone = ZoneId.systemDefault();

// Specific timezone
ZoneId newYork = ZoneId.of("America/New_York");
ZoneId tokyo = ZoneId.of("Asia/Tokyo");
ZoneId utc = ZoneId.of("UTC");

// Get all available zone IDs
Set<String> allZones = ZoneId.getAvailableZoneIds();
// Returns 600+ zone IDs like "America/New_York", "Europe/London", etc.

// From offset
ZoneId fromOffset = ZoneId.of("+05:30"); // India Standard Time
```

### ZoneOffset

ZoneOffset represents a fixed offset from UTC (like +05:30 or -08:00).

```java
// Create offset
ZoneOffset offset = ZoneOffset.of("+05:30"); // India
ZoneOffset utc = ZoneOffset.UTC;             // +00:00
ZoneOffset offset2 = ZoneOffset.ofHours(-5); // -05:00

// Get offset for a specific zone and time
ZonedDateTime zdt = ZonedDateTime.now(ZoneId.of("America/New_York"));
ZoneOffset currentOffset = zdt.getOffset();  // -05:00 or -04:00 (DST)
```

### ZoneId vs ZoneOffset

| Feature | ZoneId | ZoneOffset |
|---------|--------|------------|
| **Type** | Time zone (e.g., America/New_York) | Fixed offset (e.g., +05:30) |
| **DST** | Handles DST automatically | No DST handling |
| **Examples** | "Europe/London", "Asia/Tokyo" | "+01:00", "-08:00" |
| **Use Case** | Business logic with time zones | UTC offsets, database timestamps |

---

## Instant

Instant represents a point in time on the timeline in UTC (similar to Unix timestamp). It's timezone-independent.

### Creating Instant

```java
// Current instant (UTC)
Instant now = Instant.now();

// From epoch seconds
Instant epoch = Instant.ofEpochSecond(1704459600); // 2024-01-05 15:00:00 UTC
Instant millis = Instant.ofEpochMilli(1704459600000L);

// From ZonedDateTime
ZonedDateTime zdt = ZonedDateTime.now();
Instant instant = zdt.toInstant();
```

### Using Instant

```java
Instant instant = Instant.now();

// Get epoch values
long epochSeconds = instant.getEpochSecond();
long epochMillis = instant.toEpochMilli();

// Manipulate (immutable)
Instant later = instant.plusSeconds(3600);    // 1 hour later
Instant earlier = instant.minusSeconds(60);   // 1 minute earlier

// Compare
Instant i1 = Instant.now();
Instant i2 = i1.plusSeconds(10);
boolean isBefore = i1.isBefore(i2);  // true
boolean isAfter = i1.isAfter(i2);    // false

// Calculate duration
Duration duration = Duration.between(i1, i2);  // 10 seconds
```

### Converting Between Instant and ZonedDateTime

```java
// Instant to ZonedDateTime (add timezone)
Instant instant = Instant.now();
ZonedDateTime nyTime = instant.atZone(ZoneId.of("America/New_York"));
ZonedDateTime tokyoTime = instant.atZone(ZoneId.of("Asia/Tokyo"));

// ZonedDateTime to Instant (remove timezone, convert to UTC)
ZonedDateTime zdt = ZonedDateTime.now();
Instant instant2 = zdt.toInstant();
```

---

## Daylight Saving Time

Daylight Saving Time (DST) is when clocks are moved forward by 1 hour in spring and back by 1 hour in fall.

### How Java Handles DST

Java's ZonedDateTime automatically handles DST transitions:

```java
// Spring forward - 2:00 AM becomes 3:00 AM (1 hour gap)
ZonedDateTime beforeSpring = ZonedDateTime.of(
    2024, 3, 10, 1, 30, 0, 0,
    ZoneId.of("America/New_York")
);

ZonedDateTime afterSpring = beforeSpring.plusHours(1);
// Jumps from 01:30 to 03:30 (skips 02:30)

// Fall back - 2:00 AM becomes 1:00 AM (1 hour overlap)
ZonedDateTime beforeFall = ZonedDateTime.of(
    2024, 11, 3, 1, 30, 0, 0,
    ZoneId.of("America/New_York")
);

ZonedDateTime afterFall = beforeFall.plusHours(2);
// Results in 02:30, but occurs twice (1st time: DST, 2nd time: Standard)
```

### DST Gap (Spring Forward)

During spring forward, times between 2:00 AM and 3:00 AM don't exist:

```java
// Attempting to create a time in the gap
ZonedDateTime gap = ZonedDateTime.of(
    2024, 3, 10, 2, 30, 0, 0,  // 2:30 AM doesn't exist
    ZoneId.of("America/New_York")
);
// Java adjusts to 03:30 (after the gap)

System.out.println(gap);  // 2024-03-10T03:30-04:00[America/New_York]
```

### DST Overlap (Fall Back)

During fall back, times between 1:00 AM and 2:00 AM occur twice:

```java
// Creating time during overlap - defaults to earlier occurrence
ZonedDateTime overlap = ZonedDateTime.of(
    2024, 11, 3, 1, 30, 0, 0,
    ZoneId.of("America/New_York")
);

// First occurrence (DST offset -04:00)
System.out.println(overlap);  // 2024-11-03T01:30-04:00

// Explicitly specify later occurrence
ZonedDateTime later = overlap.withLaterOffsetAtOverlap();
System.out.println(later);    // 2024-11-03T01:30-05:00
```

### Checking DST Status

```java
ZonedDateTime summer = ZonedDateTime.of(
    2024, 7, 1, 12, 0, 0, 0,
    ZoneId.of("America/New_York")
);

ZonedDateTime winter = ZonedDateTime.of(
    2024, 12, 1, 12, 0, 0, 0,
    ZoneId.of("America/New_York")
);

ZoneOffset summerOffset = summer.getOffset();  // -04:00 (DST)
ZoneOffset winterOffset = winter.getOffset();  // -05:00 (Standard)

// Check if DST rules exist for a zone
ZoneId zone = ZoneId.of("America/New_York");
// ZoneRules rules = zone.getRules();
// boolean hasDST = !rules.getTransitions().isEmpty();
```

---

## Converting Between Time Zones

### Same Instant, Different Time Zones

```java
// Create time in New York
ZonedDateTime nyTime = ZonedDateTime.of(
    2024, 1, 15, 14, 30, 0, 0,
    ZoneId.of("America/New_York")
);

// Convert to Tokyo (same instant, different local time)
ZonedDateTime tokyoTime = nyTime.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));

System.out.println(nyTime);     // 2024-01-15T14:30-05:00[America/New_York]
System.out.println(tokyoTime);  // 2024-01-16T04:30+09:00[Asia/Tokyo]
// 14 hours ahead (5 + 9 = 14 hour difference)
```

### Same Local Time, Different Time Zones

```java
// Keep same local time, just change timezone
ZonedDateTime nyTime = ZonedDateTime.of(
    2024, 1, 15, 14, 30, 0, 0,
    ZoneId.of("America/New_York")
);

// Keep 14:30 but interpret as London time (different instant!)
ZonedDateTime londonTime = nyTime.withZoneSameLocal(ZoneId.of("Europe/London"));

System.out.println(nyTime);      // 2024-01-15T14:30-05:00[America/New_York]
System.out.println(londonTime);  // 2024-01-15T14:30+00:00[Europe/London]
// Same wall-clock time, different actual instant
```

### Multi-Step Conversion

```java
// New York -> UTC -> Tokyo
ZonedDateTime nyTime = ZonedDateTime.now(ZoneId.of("America/New_York"));

// Step 1: Convert to Instant (UTC)
Instant instant = nyTime.toInstant();

// Step 2: Apply Tokyo timezone
ZonedDateTime tokyoTime = instant.atZone(ZoneId.of("Asia/Tokyo"));
```

---

## Best Practices

### 1. Store Timestamps in UTC

```java
// Good: Store as Instant (UTC)
Instant timestamp = Instant.now();
// Store in database as TIMESTAMP or BIGINT (epoch millis)

// Display in user's timezone
ZonedDateTime userTime = timestamp.atZone(ZoneId.of("America/Los_Angeles"));
```

### 2. Use ZoneId, Not Offset

```java
// Bad: Offset doesn't handle DST
ZonedDateTime bad = ZonedDateTime.now(ZoneOffset.of("-05:00"));

// Good: ZoneId handles DST automatically
ZonedDateTime good = ZonedDateTime.now(ZoneId.of("America/New_York"));
```

### 3. Always Specify Time Zone

```java
// Avoid: Uses system default timezone
ZonedDateTime ambiguous = ZonedDateTime.now();

// Better: Explicit timezone
ZonedDateTime explicit = ZonedDateTime.now(ZoneId.of("America/New_York"));

// Best: UTC for server-side operations
Instant utc = Instant.now();
```

### 4. Test DST Transitions

```java
// Test business logic around DST transitions
LocalDate springForward = LocalDate.of(2024, 3, 10);  // US DST starts
LocalDate fallBack = LocalDate.of(2024, 11, 3);       // US DST ends

// Ensure scheduling, billing, etc. work correctly
```

---

## Common Pitfalls

### 1. Confusing withZoneSameInstant vs withZoneSameLocal

```java
ZonedDateTime ny = ZonedDateTime.of(2024, 1, 15, 14, 30, 0, 0,
                                     ZoneId.of("America/New_York"));

// Same instant in time
ZonedDateTime tokyo1 = ny.withZoneSameInstant(ZoneId.of("Asia/Tokyo"));
// 2024-01-16T04:30+09:00 (next day in Tokyo!)

// Same wall-clock time (different instant!)
ZonedDateTime tokyo2 = ny.withZoneSameLocal(ZoneId.of("Asia/Tokyo"));
// 2024-01-15T14:30+09:00 (same day, same time, but different moment)
```

### 2. Assuming Fixed Offsets

```java
// Wrong: Offset changes with DST
ZonedDateTime summer = ZonedDateTime.of(2024, 7, 1, 12, 0, 0, 0,
                                         ZoneId.of("America/New_York"));
ZoneOffset summerOffset = summer.getOffset();  // -04:00

ZonedDateTime winter = ZonedDateTime.of(2024, 12, 1, 12, 0, 0, 0,
                                         ZoneId.of("America/New_York"));
ZoneOffset winterOffset = winter.getOffset();  // -05:00

// Offsets are different!
```

### 3. Not Handling DST Gaps

```java
// This time doesn't exist (2:30 AM during spring forward)
LocalDateTime ldt = LocalDateTime.of(2024, 3, 10, 2, 30);
ZonedDateTime zdt = ldt.atZone(ZoneId.of("America/New_York"));

// Java adjusts to 03:30 automatically
System.out.println(zdt);  // 2024-03-10T03:30-04:00
```

### 4. Using LocalDateTime for Scheduling

```java
// Bad: LocalDateTime has no timezone
LocalDateTime meeting = LocalDateTime.of(2024, 6, 15, 14, 0);
// Is this 2 PM in New York or Tokyo?

// Good: Use ZonedDateTime
ZonedDateTime meeting2 = ZonedDateTime.of(2024, 6, 15, 14, 0, 0, 0,
                                           ZoneId.of("America/New_York"));
```

---

## Summary

| Class | Purpose | Timezone | DST |
|-------|---------|----------|-----|
| **LocalDate** | Date only | No | N/A |
| **LocalTime** | Time only | No | N/A |
| **LocalDateTime** | Date + Time | No | N/A |
| **ZonedDateTime** | Date + Time + Zone | Yes | Yes |
| **Instant** | UTC timestamp | UTC only | N/A |
| **ZoneId** | Timezone (e.g., America/New_York) | - | Handles DST |
| **ZoneOffset** | Fixed offset (e.g., +05:30) | - | No DST |

### Key Takeaways

1. **ZonedDateTime** = LocalDateTime + ZoneId
2. **Instant** = point in time in UTC
3. **DST** is automatically handled by ZoneId
4. Use **withZoneSameInstant** to convert time zones (same moment)
5. Use **withZoneSameLocal** to keep same clock time (different moment)
6. Store timestamps as **Instant** or **epoch millis**
7. Display in user's timezone using **ZonedDateTime**

---

## Practice Questions

Ready to test your knowledge? Proceed to [Time Zones Practice Questions](06-practice-questions.md) to solidify your understanding!

---

**Next:** [Practice Questions - Time Zones and DST](06-practice-questions.md)  
**Previous:** [Date-Time API Practice Questions](05-practice-questions.md)

---

**Good luck!** ☕
