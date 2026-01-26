# Module 3.1: Date-Time API - Practice Questions

## 📝 Practice Exam (20 Questions)

**Time Limit:** 30 minutes  
**Passing Score:** 16/20 (80%)

---

### Question 1
What is the output of the following code?

```java
LocalDate date = LocalDate.of(2024, 1, 15);
date.plusDays(5);
System.out.println(date);
```

A) 2024-01-15  
B) 2024-01-20  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
LocalDate is immutable. The `plusDays()` method returns a new LocalDate object but doesn't modify the original. Since the return value is not assigned, `date` remains unchanged (2024-01-15).

---

### Question 2
Which of the following creates a LocalDate for February 29, 2024?

A) `LocalDate.of(2024, 2, 29);`  
B) `LocalDate.of(2024, Month.FEBRUARY, 29);`  
C) Both A and B  
D) Neither - throws DateTimeException  

**Answer:** C

**Explanation:**
2024 is a leap year, so February has 29 days. Both syntaxes are valid for creating LocalDate. Option A uses the month number (1-12), and option B uses the Month enum.

---

### Question 3
What does the following code print?

```java
LocalTime time = LocalTime.of(23, 30);
time = time.plusHours(2);
System.out.println(time);
```

A) 25:30  
B) 01:30  
C) 23:30  
D) Runtime exception  

**Answer:** B

**Explanation:**
LocalTime wraps around at midnight. Adding 2 hours to 23:30 gives 01:30 (1:30 AM the next day). Note that the time wraps but doesn't carry a date.

---

### Question 4
Which statement about the Date-Time API is FALSE?

A) LocalDate, LocalTime, and LocalDateTime are immutable  
B) Months are 1-indexed (January = 1)  
C) LocalDate can store timezone information  
D) Period is used for date-based durations  

**Answer:** C

**Explanation:**
LocalDate does NOT store timezone information. It represents only a date (year, month, day) without time or timezone. For timezone information, use ZonedDateTime.

---

### Question 5
What is the output?

```java
LocalDate date = LocalDate.of(2024, 1, 31);
date = date.plusMonths(1);
System.out.println(date);
```

A) 2024-02-31  
B) 2024-02-29  
C) 2024-03-02  
D) DateTimeException  

**Answer:** B

**Explanation:**
When adding months results in an invalid date, the date is adjusted to the last valid day of the month. February 2024 has 29 days (leap year), so January 31 + 1 month = February 29.

---

### Question 6
What does `LocalDateTime.now().toLocalDate()` return?

A) A LocalDateTime object  
B) A LocalDate object  
C) A String  
D) Compilation error  

**Answer:** B

**Explanation:**
The `toLocalDate()` method extracts the date portion from a LocalDateTime and returns it as a LocalDate object.

---

### Question 7
What is the result?

```java
Period period = Period.ofDays(30);
System.out.println(period.getMonths());
```

A) 1  
B) 0  
C) 30  
D) Compilation error  

**Answer:** B

**Explanation:**
`Period.ofDays(30)` creates a Period of 30 days only. The `getMonths()` method returns the months component, which is 0. Period doesn't automatically convert days to months - it stores days, months, and years separately.

---

### Question 8
Which of the following is true about Duration?

A) It's used for date-based amounts  
B) It can be used with LocalDate  
C) It's measured in seconds and nanoseconds  
D) It can represent years and months  

**Answer:** C

**Explanation:**
Duration represents time-based amounts and is internally stored as seconds and nanoseconds. It's used with LocalTime and LocalDateTime, not LocalDate. For date-based amounts, use Period.

---

### Question 9
What is the output?

```java
LocalDate date1 = LocalDate.of(2024, 1, 15);
LocalDate date2 = LocalDate.of(2024, 6, 15);
Period period = Period.between(date1, date2);
System.out.println(period.getDays());
```

A) 152  
B) 5  
C) 0  
D) Depends on leap year  

**Answer:** C

**Explanation:**
`Period.between()` calculates the period as 5 months and 0 days (from January 15 to June 15). The `getDays()` method returns only the days component (0), not the total number of days.

---

### Question 10
What does the following code print?

```java
LocalTime time = LocalTime.of(10, 30, 45);
System.out.println(time.getHour());
```

A) 10  
B) 10:30  
C) 10:30:45  
D) Compilation error  

**Answer:** A

**Explanation:**
The `getHour()` method returns only the hour component as an int. The value is 10.

---

### Question 11
Which method creates a LocalDateTime?

A) `LocalDate.atTime(LocalTime)`  
B) `LocalTime.atDate(LocalDate)`  
C) `LocalDateTime.of(LocalDate, LocalTime)`  
D) All of the above  

**Answer:** D

**Explanation:**
All three methods are valid ways to create a LocalDateTime:
- `LocalDate.atTime(time)` - adds time to a date
- `LocalTime.atDate(date)` - adds date to a time  
- `LocalDateTime.of(date, time)` - combines date and time

---

### Question 12
What is the output?

```java
LocalDate date = LocalDate.parse("2024-01-15");
System.out.println(date.getMonthValue());
```

A) 0  
B) 1  
C) JANUARY  
D) Compilation error  

**Answer:** B

**Explanation:**
`getMonthValue()` returns the month as an int from 1-12. January is 1 (unlike the old Calendar API where January was 0).

---

### Question 13
What happens with this code?

```java
LocalDate date = LocalDate.of(2024, 2, 30);
```

A) Creates 2024-02-30  
B) Creates 2024-02-29  
C) Creates 2024-03-01  
D) Throws DateTimeException  

**Answer:** D

**Explanation:**
February never has 30 days. This throws a DateTimeException because the date is invalid. Unlike plusMonths(), the of() method doesn't adjust invalid dates.

---

### Question 14
What is the result?

```java
LocalTime time1 = LocalTime.of(10, 0);
LocalTime time2 = LocalTime.of(14, 30);
Duration duration = Duration.between(time1, time2);
System.out.println(duration.toHours());
```

A) 4  
B) 4.5  
C) 270  
D) 16200  

**Answer:** A

**Explanation:**
`Duration.between()` calculates the duration as 4 hours and 30 minutes. The `toHours()` method returns only the whole hours component, which is 4.

---

### Question 15
Which format string pattern represents "15-Jan-2024"?

A) `"dd-MM-yyyy"`  
B) `"dd-MMM-yyyy"`  
C) `"DD-MM-YYYY"`  
D) `"dd-mm-yyyy"`  

**Answer:** B

**Explanation:**
- `dd` - day of month (01-31)
- `MMM` - month short name (Jan)
- `yyyy` - year (2024)

Pattern `"dd-MMM-yyyy"` produces "15-Jan-2024".

---

### Question 16
What does the following code print?

```java
LocalDateTime dt = LocalDateTime.of(2024, 1, 15, 14, 30);
dt.plusDays(5).plusHours(2);
System.out.println(dt);
```

A) 2024-01-15T14:30  
B) 2024-01-20T16:30  
C) 2024-01-20T14:30  
D) Compilation error  

**Answer:** A

**Explanation:**
LocalDateTime is immutable. The chain of `plusDays().plusHours()` returns a new object, but it's not assigned back to `dt`. Therefore, `dt` remains unchanged.

---

### Question 17
What is the correct way to get the current date?

A) `new LocalDate()`  
B) `LocalDate.now()`  
C) `LocalDate.current()`  
D) `LocalDate.today()`  

**Answer:** B

**Explanation:**
The `now()` static method is used to get the current date. LocalDate doesn't have a public constructor, and `current()` or `today()` methods don't exist.

---

### Question 18
What is the output?

```java
LocalDate date = LocalDate.of(2024, 1, 15);
System.out.println(date.isLeapYear());
```

A) true  
B) false  
C) Compilation error  
D) Runtime exception  

**Answer:** A

**Explanation:**
2024 is a leap year (divisible by 4, and if divisible by 100, also divisible by 400). The `isLeapYear()` method returns true.

---

### Question 19
Which of the following is NOT a valid LocalTime?

A) `LocalTime.of(0, 0)`  
B) `LocalTime.of(12, 30)`  
C) `LocalTime.of(23, 59)`  
D) `LocalTime.of(24, 0)`  

**Answer:** D

**Explanation:**
Hours in LocalTime range from 0-23. Hour 24 is invalid and throws DateTimeException. Midnight is represented as 00:00 (hour 0).

---

### Question 20
What does the following code print?

```java
LocalDate date = LocalDate.of(2024, 1, 15);
Period period = Period.of(1, 2, 10);
LocalDate newDate = date.plus(period);
System.out.println(newDate);
```

A) 2025-03-25  
B) 2025-02-15  
C) 2024-03-25  
D) Compilation error  

**Answer:** A

**Explanation:**
`Period.of(1, 2, 10)` creates a period of 1 year, 2 months, and 10 days. Adding this to 2024-01-15:
- Add 1 year: 2025-01-15
- Add 2 months: 2025-03-15
- Add 10 days: 2025-03-25

---

## 📊 Scoring Guide

**Score Interpretation:**
- **18-20 (90-100%)**: Excellent! You have mastered the Date-Time API.
- **16-17 (80-89%)**: Good! Review the questions you missed.
- **14-15 (70-79%)**: Fair. Revisit the theory and practice more.
- **Below 14 (< 70%)**: Need more study. Review the theory document carefully.

---

## 🎯 Common Mistakes to Avoid

1. **Forgetting immutability** - must assign return values
2. **Confusing Period and Duration** - Period for dates, Duration for time
3. **Invalid dates** - February 30 throws exception
4. **Time wrapping** - 23:00 + 2 hours = 01:00
5. **Month indexing** - Months are 1-12, not 0-11
6. **getDays() vs total days** - Period.getDays() returns only days component
7. **Date adjustment** - plusMonths() adjusts to last valid day

---

## Next Steps

✅ **Scored 16+?** Move to [Time Zones and Daylight Saving](06-timezones-dst.md)

⚠️ **Scored below 16?** Review [Date-Time API Theory](05-datetime-api.md) and retake this quiz.

---

**Good luck!** ☕
