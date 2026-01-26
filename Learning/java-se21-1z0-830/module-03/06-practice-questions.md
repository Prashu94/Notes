# Module 3.2: Time Zones and DST - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output?

```java
Instant instant = Instant.ofEpochSecond(0);
ZonedDateTime zdt = instant.atZone(ZoneId.of("UTC"));
System.out.println(zdt.getYear());
```

A) 1969  
B) 1970  
C) 2024  
D) DateTimeException  

**Answer:** B

**Explanation:**
Epoch second 0 represents January 1, 1970, 00:00:00 UTC (Unix epoch). The year is 1970.

---

### Question 2
Which method converts a ZonedDateTime to a different timezone while keeping the same instant in time?

A) `withZone()`  
B) `withZoneSameLocal()`  
C) `withZoneSameInstant()`  
D) `toZone()`  

**Answer:** C

**Explanation:**
`withZoneSameInstant()` converts to a different timezone while representing the same point in time. The wall-clock time will change, but the instant remains the same.

---

### Question 3
What happens during daylight saving time "spring forward"?

A) Clocks move back 1 hour  
B) Clocks move forward 1 hour  
C) Clocks move forward 2 hours  
D) Nothing changes  

**Answer:** B

**Explanation:**
During spring forward (start of DST), clocks move forward 1 hour, typically from 2:00 AM to 3:00 AM. There's a 1-hour gap where times don't exist.

---

### Question 4
What is the difference between ZoneId and ZoneOffset?

A) ZoneId is for time, ZoneOffset is for date  
B) ZoneId handles DST, ZoneOffset is a fixed offset  
C) They are the same  
D) ZoneOffset is deprecated  

**Answer:** B

**Explanation:**
ZoneId represents a timezone (like "America/New_York") that handles DST automatically. ZoneOffset is a fixed offset from UTC (like "+05:30") that doesn't account for DST.

---

### Question 5
What is the output?

```java
ZonedDateTime ny = ZonedDateTime.of(2024, 1, 15, 14, 30, 0, 0,
                                     ZoneId.of("America/New_York"));
ZonedDateTime tokyo = ny.withZoneSameLocal(ZoneId.of("Asia/Tokyo"));
System.out.println(ny.toInstant().equals(tokyo.toInstant()));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
`withZoneSameLocal()` keeps the same wall-clock time (14:30) but changes the timezone. This represents a DIFFERENT instant in time. The instants are not equal.

---

### Question 6
What class represents a point in time on the UTC timeline?

A) LocalDateTime  
B) ZonedDateTime  
C) Instant  
D) Duration  

**Answer:** C

**Explanation:**
Instant represents a point in time in UTC, similar to a Unix timestamp. It doesn't have timezone or local date/time information.

---

### Question 7
What is the result?

```java
ZonedDateTime zdt = ZonedDateTime.of(2024, 3, 10, 2, 30, 0, 0,
                                      ZoneId.of("America/New_York"));
System.out.println(zdt.getHour());
```

A) 2  
B) 3  
C) 1  
D) DateTimeException  

**Answer:** B

**Explanation:**
March 10, 2024, 2:30 AM doesn't exist in America/New_York due to DST spring forward. Java automatically adjusts to 3:30 AM (after the gap). The hour is 3.

---

### Question 8
How do you get all available time zone IDs?

A) `ZoneId.getAll()`  
B) `ZoneId.list()`  
C) `ZoneId.getAvailableZoneIds()`  
D) `ZoneId.values()`  

**Answer:** C

**Explanation:**
`ZoneId.getAvailableZoneIds()` returns a Set of all available zone IDs (600+ zones like "America/New_York", "Europe/London", etc.).

---

### Question 9
What is the output?

```java
Instant i1 = Instant.now();
Instant i2 = i1.plusSeconds(60);
Duration d = Duration.between(i1, i2);
System.out.println(d.getSeconds());
```

A) 1  
B) 60  
C) 3600  
D) Compilation error  

**Answer:** B

**Explanation:**
`Duration.between()` calculates the duration as 60 seconds. The `getSeconds()` method returns 60.

---

### Question 10
Which of the following is true about Instant?

A) It stores timezone information  
B) It's mutable  
C) It represents a point in time in UTC  
D) It can be used with LocalDate  

**Answer:** C

**Explanation:**
Instant represents a point in time on the UTC timeline. It's immutable and doesn't store timezone information (always UTC). You need to convert to ZonedDateTime to work with timezones.

---

### Question 11
What happens with this code?

```java
LocalDateTime ldt = LocalDateTime.of(2024, 1, 15, 14, 30);
ZonedDateTime zdt = ldt.atZone(ZoneId.of("America/New_York"));
```

A) Compilation error  
B) Runtime exception  
C) Creates a ZonedDateTime  
D) Returns null  

**Answer:** C

**Explanation:**
The `atZone()` method adds timezone information to a LocalDateTime, creating a ZonedDateTime. This is a valid operation.

---

### Question 12
What is the output?

```java
ZoneOffset offset = ZoneOffset.of("+05:30");
System.out.println(offset.getTotalSeconds());
```

A) 330  
B) 5.5  
C) 19800  
D) 5:30  

**Answer:** C

**Explanation:**
+05:30 means 5 hours and 30 minutes = (5 × 3600) + (30 × 60) = 18000 + 1800 = 19800 seconds.

---

### Question 13
During DST "fall back", what happens to times between 1:00 AM and 2:00 AM?

A) They don't exist (gap)  
B) They occur twice (overlap)  
C) They are shifted by 2 hours  
D) Nothing special  

**Answer:** B

**Explanation:**
During fall back, clocks move back 1 hour (e.g., 2:00 AM becomes 1:00 AM). Times between 1:00 AM and 2:00 AM occur twice - once in DST and once in standard time.

---

### Question 14
What is the recommended way to store timestamps in a database?

A) LocalDateTime  
B) String  
C) Instant (UTC)  
D) ZonedDateTime  

**Answer:** C

**Explanation:**
Best practice is to store timestamps as Instant (UTC) or epoch milliseconds. This avoids timezone ambiguity. Convert to user's timezone only for display.

---

### Question 15
What is the output?

```java
Instant instant = Instant.now();
long epochSeconds = instant.getEpochSecond();
Instant instant2 = Instant.ofEpochSecond(epochSeconds);
System.out.println(instant.equals(instant2));
```

A) true  
B) false  
C) Compilation error  
D) Depends on nanoseconds  

**Answer:** D

**Explanation:**
It depends on the nanoseconds component. `getEpochSecond()` only gets seconds, losing nanoseconds precision. If the original instant has non-zero nanoseconds, the reconstructed instant won't be equal. If nanoseconds are 0, they'll be equal.

---

### Question 16
What does `ZoneId.systemDefault()` return?

A) UTC  
B) The system's default timezone  
C) America/New_York  
D) null  

**Answer:** B

**Explanation:**
`ZoneId.systemDefault()` returns the system's default timezone as configured in the operating system. This can vary by machine and user settings.

---

### Question 17
What is the output?

```java
ZonedDateTime zdt = ZonedDateTime.now(ZoneId.of("UTC"));
Instant instant = zdt.toInstant();
System.out.println(zdt.getHour() == instant.atZone(ZoneId.of("UTC")).getHour());
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
Both represent the same instant in UTC. Converting the instant back to UTC gives the same hour. The comparison is true.

---

### Question 18
Which method keeps the same wall-clock time but changes the timezone?

A) `withZoneSameInstant()`  
B) `withZoneSameLocal()`  
C) `toZone()`  
D) `convertZone()`  

**Answer:** B

**Explanation:**
`withZoneSameLocal()` keeps the same local time (e.g., 14:30) but interprets it in a different timezone. This represents a different instant in time.

---

### Question 19
What is the correct way to create a ZoneOffset for UTC?

A) `ZoneOffset.of("0")`  
B) `ZoneOffset.UTC`  
C) `ZoneOffset.ofHours(0)`  
D) All of the above  

**Answer:** D

**Explanation:**
All three are valid ways to create a UTC offset:
- `ZoneOffset.of("0")` or `ZoneOffset.of("+00:00")`
- `ZoneOffset.UTC` (constant)
- `ZoneOffset.ofHours(0)`

---

### Question 20
What is the output?

```java
ZonedDateTime summer = ZonedDateTime.of(2024, 7, 1, 12, 0, 0, 0,
                                         ZoneId.of("America/New_York"));
ZonedDateTime winter = ZonedDateTime.of(2024, 12, 1, 12, 0, 0, 0,
                                         ZoneId.of("America/New_York"));
System.out.println(summer.getOffset().equals(winter.getOffset()));
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** B

**Explanation:**
Summer (July) is during DST with offset -04:00. Winter (December) is standard time with offset -05:00. The offsets are different, so equals() returns false.

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered time zones and DST.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Confusing withZoneSameInstant vs withZoneSameLocal**
   - SameInstant: same moment, different wall-clock time
   - SameLocal: same wall-clock time, different moment

2. **Assuming fixed offsets** - offsets change with DST

3. **Not handling DST gaps** - spring forward skips hours

4. **Not handling DST overlaps** - fall back repeats hours

5. **Using LocalDateTime for scheduling** - no timezone info

6. **Storing timezones as offsets** - won't handle DST changes

7. **Forgetting to convert to UTC** for database storage

---

## Module 3 Complete! 🎉

You've completed the Date-Time API module covering:
- ✅ LocalDate, LocalTime, LocalDateTime
- ✅ Period and Duration
- ✅ ZonedDateTime and time zones
- ✅ Instant and UTC timestamps
- ✅ Daylight Saving Time handling

**Total Practice Questions:** 40/40 ✓

---

## Next Steps

✅ **Scored 16+ on both quizzes?** Move to [Module 4: Control Flow](../module-04/07-control-flow-basics.md)

⚠️ **Scored below 16?** Review the theory documents and retake the quizzes.

---

**Good luck!** ☕
