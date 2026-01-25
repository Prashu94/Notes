# Chapter 12: Cypher - Data Types

## Learning Objectives
By the end of this chapter, you will:
- Understand all Neo4j data types
- Work with temporal types effectively
- Use spatial types for geolocation
- Handle NULL values properly
- Convert between types safely

---

## 12.1 Overview of Data Types

### Primitive Types

| Type | Description | Example |
|------|-------------|---------|
| `INTEGER` | 64-bit signed integer | `42`, `-17` |
| `FLOAT` | 64-bit floating point | `3.14`, `-0.001` |
| `STRING` | Unicode text | `'Hello'`, `"World"` |
| `BOOLEAN` | True or false | `true`, `false` |
| `NULL` | Absence of value | `null` |

### Composite Types

| Type | Description | Example |
|------|-------------|---------|
| `LIST` | Ordered collection | `[1, 2, 3]`, `['a', 'b']` |
| `MAP` | Key-value pairs | `{name: 'Alice', age: 30}` |

### Temporal Types

| Type | Description | Example |
|------|-------------|---------|
| `DATE` | Calendar date | `date('2026-01-25')` |
| `TIME` | Time with timezone | `time('14:30:00+05:30')` |
| `LOCALTIME` | Time without timezone | `localtime('14:30:00')` |
| `DATETIME` | Date and time with timezone | `datetime('2026-01-25T14:30:00Z')` |
| `LOCALDATETIME` | Date and time without timezone | `localdatetime('2026-01-25T14:30:00')` |
| `DURATION` | Time span | `duration('P1Y2M3D')` |

### Spatial Types

| Type | Description | Example |
|------|-------------|---------|
| `POINT` | Geographic or Cartesian point | `point({latitude: 40.7, longitude: -74.0})` |

---

## 12.2 Working with Numbers

### Integers

```cypher
// Integer literals
RETURN 42, -17, 0

// Large integers
RETURN 9223372036854775807 AS maxLong  // Max 64-bit signed

// Integer operations
RETURN 
    17 / 5 AS intDiv,      // 3 (integer division)
    17 % 5 AS modulo,      // 2 (remainder)
    17.0 / 5 AS floatDiv   // 3.4 (float division)

// Bitwise operations (APOC)
RETURN 
    apoc.bitwise.op(5, 'AND', 3) AS andOp,  // 1
    apoc.bitwise.op(5, 'OR', 3) AS orOp,    // 7
    apoc.bitwise.op(5, 'XOR', 3) AS xorOp   // 6
```

### Floating Point Numbers

```cypher
// Float literals
RETURN 3.14, -0.001, 1.0e10

// Special values
RETURN 
    1.0 / 0.0 AS infinity,      // Infinity
    -1.0 / 0.0 AS negInfinity,  // -Infinity
    0.0 / 0.0 AS notANumber     // NaN

// Precision considerations
RETURN 0.1 + 0.2 = 0.3 AS equal  // false (floating point precision)
RETURN abs(0.1 + 0.2 - 0.3) < 0.0001 AS almostEqual  // true

// Formatting
RETURN 
    round(3.14159, 2) AS rounded,  // 3.14
    apoc.number.format(1234.567, '#,##0.00') AS formatted  // '1,234.57'
```

### Number Ranges

```cypher
// Generate number sequences
RETURN range(1, 10) AS oneToTen        // [1,2,3,4,5,6,7,8,9,10]
RETURN range(0, 10, 2) AS evens        // [0,2,4,6,8,10]
RETURN range(10, 1, -1) AS countdown   // [10,9,8,7,6,5,4,3,2,1]
```

---

## 12.3 Working with Strings

### String Literals

```cypher
// Single or double quotes
RETURN 'Hello' AS s1, "World" AS s2

// Escape sequences
RETURN 
    'Line1\nLine2' AS newline,
    'Tab\there' AS tab,
    'Quote: \'single\' and \"double\"' AS quotes,
    'Backslash: \\' AS backslash

// Unicode
RETURN 'Emoji: \u2764' AS heart  // ❤
```

### String Properties

```cypher
// Length and emptiness
WITH 'Hello World' AS str
RETURN 
    size(str) AS length,           // 11
    size(str) = 0 AS isEmpty,      // false
    str = '' AS isEmptyAlt         // false

// Character access (via substring)
WITH 'Hello' AS str
RETURN 
    substring(str, 0, 1) AS first,  // 'H'
    substring(str, 4, 1) AS last    // 'o'
```

### String Comparisons

```cypher
// Lexicographic comparison
RETURN 
    'apple' < 'banana' AS less,     // true
    'Apple' < 'apple' AS caseSens,  // true (uppercase < lowercase)
    toLower('Apple') = toLower('APPLE') AS caseInsens  // true

// Pattern matching
RETURN 
    'test@email.com' =~ '.*@.*' AS matches,           // true
    'test@email.com' =~ '(?i)TEST@.*' AS caseInsens   // true
```

---

## 12.4 Working with Booleans

### Boolean Values

```cypher
// Literals
RETURN true, false

// From comparisons
RETURN 
    5 > 3 AS greater,           // true
    'a' = 'b' AS equal,         // false
    null = null AS nullEquals   // null (not true!)
```

### Boolean Operators

```cypher
// AND, OR, NOT, XOR
RETURN 
    true AND false AS andOp,    // false
    true OR false AS orOp,      // true
    NOT true AS notOp,          // false
    true XOR true AS xorOp      // false

// Short-circuit evaluation
RETURN true OR (1/0 > 0) AS shortCircuit  // true (no division error)
```

### Three-Valued Logic (with NULL)

```cypher
// NULL in boolean operations
RETURN 
    true AND null AS tAndN,     // null
    false AND null AS fAndN,    // false
    true OR null AS tOrN,       // true
    false OR null AS fOrN,      // null
    NOT null AS notN            // null

// Safe boolean checks
MATCH (p:Person)
WHERE p.active = true           // Only returns explicit true
RETURN p.name

MATCH (p:Person)
WHERE p.active IS NOT NULL AND p.active
RETURN p.name                   // Explicit NULL check
```

---

## 12.5 Temporal Types Deep Dive

### DATE Type

```cypher
// Creating dates
RETURN 
    date() AS today,
    date('2026-01-25') AS fromString,
    date({year: 2026, month: 1, day: 25}) AS fromComponents,
    date({year: 2026, week: 4, dayOfWeek: 7}) AS fromWeek,
    date({year: 2026, ordinalDay: 25}) AS fromOrdinal

// Date components
WITH date('2026-01-25') AS d
RETURN 
    d.year, d.month, d.day,
    d.quarter,                  // 1
    d.week,                     // 4
    d.dayOfWeek,               // 7 (Sunday)
    d.dayOfYear                // 25
```

### TIME and LOCALTIME

```cypher
// Time with timezone
RETURN 
    time() AS now,
    time('14:30:00') AS fromStr,
    time('14:30:00+05:30') AS withOffset,
    time({hour: 14, minute: 30, second: 0, timezone: '+05:30'}) AS fromMap

// Local time (no timezone)
RETURN 
    localtime() AS now,
    localtime('14:30:00') AS fromStr

// Components
WITH time('14:30:45.123456789+05:30') AS t
RETURN 
    t.hour, t.minute, t.second,
    t.millisecond, t.microsecond, t.nanosecond,
    t.timezone, t.offset
```

### DATETIME and LOCALDATETIME

```cypher
// Datetime with timezone
RETURN 
    datetime() AS now,
    datetime('2026-01-25T14:30:00Z') AS utc,
    datetime('2026-01-25T14:30:00+05:30') AS withOffset,
    datetime({timezone: 'America/New_York'}) AS nyTime

// Local datetime
RETURN 
    localdatetime() AS now,
    localdatetime('2026-01-25T14:30:00') AS fromStr

// Combining date and time
WITH date('2026-01-25') AS d, time('14:30:00') AS t
RETURN datetime({date: d, time: t}) AS combined

// Converting between types
WITH datetime('2026-01-25T14:30:00Z') AS dt
RETURN 
    date(dt) AS dateOnly,
    time(dt) AS timeOnly
```

### DURATION Type

```cypher
// Duration formats (ISO 8601)
RETURN 
    duration('P1Y') AS oneYear,
    duration('P2M') AS twoMonths,
    duration('P3D') AS threeDays,
    duration('PT4H') AS fourHours,
    duration('PT5M') AS fiveMinutes,
    duration('PT6S') AS sixSeconds,
    duration('P1Y2M3DT4H5M6S') AS complex

// From components
RETURN duration({
    years: 1, months: 2, days: 3,
    hours: 4, minutes: 5, seconds: 6
}) AS fromMap

// Duration components
WITH duration('P1Y2M3DT4H5M6.789S') AS d
RETURN 
    d.years, d.months, d.days,
    d.hours, d.minutes, d.seconds,
    d.milliseconds, d.microseconds, d.nanoseconds

// Arithmetic with durations
RETURN 
    date() + duration('P7D') AS nextWeek,
    datetime() - duration('PT2H') AS twoHoursAgo,
    duration('P1D') + duration('P1D') AS twoDays,
    duration('P10D') / 2 AS fiveDays
```

### Duration Between

```cypher
// Calculate difference
WITH date('2026-01-01') AS start, date('2026-12-31') AS end
RETURN 
    duration.between(start, end) AS diff,
    duration.inDays(start, end).days AS totalDays,
    duration.inMonths(start, end).months AS totalMonths,
    duration.inSeconds(start, end).seconds AS totalSeconds
```

---

## 12.6 Spatial Types

### Creating Points

```cypher
// Geographic point (WGS 84)
RETURN point({latitude: 40.7128, longitude: -74.0060}) AS nyc
// SRID 4326

// 3D geographic point
RETURN point({latitude: 40.7128, longitude: -74.0060, height: 10}) AS nyc3d
// SRID 4979

// Cartesian point (2D)
RETURN point({x: 100, y: 200}) AS cart2d
// SRID 7203

// Cartesian point (3D)
RETURN point({x: 100, y: 200, z: 50}) AS cart3d
// SRID 9157
```

### Point Properties

```cypher
// Access coordinates
WITH point({latitude: 40.7128, longitude: -74.0060}) AS p
RETURN 
    p.latitude AS lat,
    p.longitude AS lon,
    p.x AS x,              // Same as longitude
    p.y AS y,              // Same as latitude
    p.srid AS srid         // 4326

// Cartesian point
WITH point({x: 100, y: 200}) AS p
RETURN p.x, p.y, p.srid    // 7203
```

### Distance Calculations

```cypher
// Geographic distance (meters)
WITH 
    point({latitude: 40.7128, longitude: -74.0060}) AS nyc,
    point({latitude: 34.0522, longitude: -118.2437}) AS la
RETURN point.distance(nyc, la) / 1000 AS distanceKm
// ~3940 km

// Find nearby locations
MATCH (place:Place)
WITH place, point({latitude: $lat, longitude: $lon}) AS userLocation
WHERE point.distance(place.location, userLocation) < 5000  // 5km
RETURN place.name, point.distance(place.location, userLocation) AS meters
ORDER BY meters
```

### Spatial Indexes

```cypher
// Create point index
CREATE POINT INDEX place_location FOR (p:Place) ON (p.location)

// Query with index
MATCH (p:Place)
WHERE point.distance(p.location, point({latitude: 40.7, longitude: -74.0})) < 1000
RETURN p.name
```

---

## 12.7 Lists

### Creating Lists

```cypher
// Literal lists
RETURN [1, 2, 3] AS numbers
RETURN ['a', 'b', 'c'] AS strings
RETURN [1, 'two', 3.0, true] AS mixed  // Allowed but not recommended

// Range
RETURN range(1, 5) AS oneToFive  // [1, 2, 3, 4, 5]

// From query results
MATCH (p:Person)
RETURN collect(p.name) AS names
```

### List Operations

```cypher
// Access elements (0-indexed)
WITH [10, 20, 30, 40, 50] AS list
RETURN 
    list[0] AS first,       // 10
    list[-1] AS last,       // 50
    list[1..3] AS slice,    // [20, 30]
    list[2..] AS fromIndex, // [30, 40, 50]
    list[..3] AS toIndex    // [10, 20, 30]

// Length
RETURN size([1, 2, 3]) AS len  // 3

// Concatenation
RETURN [1, 2] + [3, 4] AS combined  // [1, 2, 3, 4]

// Membership
RETURN 
    3 IN [1, 2, 3] AS contains,     // true
    4 IN [1, 2, 3] AS notContains   // false
```

### List Comprehensions

```cypher
// Transform elements
WITH [1, 2, 3, 4, 5] AS numbers
RETURN [n IN numbers | n * 2] AS doubled
// [2, 4, 6, 8, 10]

// Filter elements
WITH [1, 2, 3, 4, 5] AS numbers
RETURN [n IN numbers WHERE n % 2 = 0] AS evens
// [2, 4]

// Filter and transform
WITH [1, 2, 3, 4, 5] AS numbers
RETURN [n IN numbers WHERE n % 2 = 0 | n * 10] AS result
// [20, 40]
```

### List Functions

```cypher
// Common functions
WITH [3, 1, 4, 1, 5, 9, 2, 6] AS nums
RETURN 
    head(nums) AS first,           // 3
    last(nums) AS last,            // 6
    tail(nums) AS rest,            // [1, 4, 1, 5, 9, 2, 6]
    reverse(nums) AS reversed,     // [6, 2, 9, 5, 1, 4, 1, 3]
    size(nums) AS length           // 8

// Reduce
WITH [1, 2, 3, 4, 5] AS nums
RETURN reduce(sum = 0, n IN nums | sum + n) AS total  // 15

// UNWIND (list to rows)
UNWIND [1, 2, 3] AS num
RETURN num
// Returns 3 rows: 1, 2, 3
```

---

## 12.8 Maps

### Creating Maps

```cypher
// Literal maps
RETURN {name: 'Alice', age: 30} AS person

// From node properties
MATCH (p:Person {name: 'Alice'})
RETURN properties(p) AS personMap

// Dynamic keys (APOC)
RETURN apoc.map.fromPairs([['name', 'Alice'], ['age', 30]]) AS person
```

### Map Operations

```cypher
// Access values
WITH {name: 'Alice', age: 30, city: 'NYC'} AS person
RETURN 
    person.name AS name,        // 'Alice'
    person['age'] AS age,       // 30
    person.unknown AS missing   // null

// Get keys
WITH {a: 1, b: 2, c: 3} AS m
RETURN keys(m) AS allKeys  // ['a', 'b', 'c']

// Merge maps (APOC)
WITH {a: 1, b: 2} AS m1, {b: 3, c: 4} AS m2
RETURN apoc.map.merge(m1, m2) AS merged
// {a: 1, b: 3, c: 4}
```

### Map Projections

```cypher
// Select specific properties
MATCH (p:Person {name: 'Alice'})
RETURN p {.name, .age} AS subset

// Add computed properties
MATCH (p:Person {name: 'Alice'})
RETURN p {.name, .age, status: 'active'} AS enhanced

// Include all properties plus extras
MATCH (p:Person {name: 'Alice'})
RETURN p {.*, fullName: p.firstName + ' ' + p.lastName} AS full
```

---

## 12.9 NULL Handling

### Understanding NULL

```cypher
// NULL means "unknown" or "missing"
RETURN 
    null = null AS nullEquals,     // null (not true!)
    null <> null AS nullNotEquals, // null
    null IS NULL AS isNull,        // true
    null IS NOT NULL AS isNotNull  // false

// NULL in operations
RETURN 
    null + 1 AS arithmetic,        // null
    'hello' + null AS concat,      // null
    [1, null, 3] AS inList         // [1, null, 3]
```

### NULL-safe Operations

```cypher
// COALESCE for defaults
RETURN coalesce(null, null, 'default') AS value  // 'default'

// Conditional NULL handling
MATCH (p:Person)
RETURN 
    p.name,
    CASE 
        WHEN p.email IS NULL THEN 'No email'
        ELSE p.email
    END AS email

// Safe navigation with OPTIONAL MATCH
MATCH (p:Person {name: 'Alice'})
OPTIONAL MATCH (p)-[:WORKS_FOR]->(c:Company)
RETURN p.name, coalesce(c.name, 'Unemployed') AS company
```

### NULL in Collections

```cypher
// NULL filtering
WITH [1, null, 2, null, 3] AS mixed
RETURN [x IN mixed WHERE x IS NOT NULL] AS filtered
// [1, 2, 3]

// NULL in aggregations (ignored)
UNWIND [1, 2, null, 4] AS n
RETURN sum(n) AS total, avg(n) AS average
// 7, 2.333... (null ignored)
```

---

## 12.10 Type Checking and Conversion

### Type Checking Functions

```cypher
// Check type
WITH [42, 'hello', true, null, [1,2], {a:1}] AS values
UNWIND values AS v
RETURN v, valueType(v) AS type

// Results:
// 42       -> 'INTEGER'
// 'hello'  -> 'STRING'  
// true     -> 'BOOLEAN'
// null     -> 'NULL'
// [1,2]    -> 'LIST<INTEGER>'
// {a:1}    -> 'MAP'
```

### Safe Conversions

```cypher
// Use OrNull variants for safe conversion
RETURN 
    toIntegerOrNull('42') AS valid,     // 42
    toIntegerOrNull('abc') AS invalid,  // null
    toFloatOrNull('3.14') AS float,     // 3.14
    toBooleanOrNull('yes') AS bool      // null (only 'true'/'false' work)

// Type coercion in comparisons
RETURN 
    1 = 1.0 AS intEqualsFloat,  // true
    '1' = 1 AS strEqualsInt     // false (no auto-coercion)
```

---

## Summary

### Type Hierarchy

```
Any
├── Primitive
│   ├── NUMBER (INTEGER, FLOAT)
│   ├── STRING
│   ├── BOOLEAN
│   └── NULL
├── Composite
│   ├── LIST<T>
│   └── MAP
├── Temporal
│   ├── DATE
│   ├── TIME / LOCALTIME
│   ├── DATETIME / LOCALDATETIME
│   └── DURATION
└── Spatial
    └── POINT
```

### Quick Reference

```cypher
-- Numbers
42, 3.14, round(n, 2), toInteger(s), toFloat(s)

-- Strings
'text', size(s), substring(s, 0, 5), split(s, ',')

-- Booleans
true, false, AND, OR, NOT, XOR

-- Temporal
date(), datetime(), duration('P1D'), d.year, d.month

-- Spatial
point({latitude: 40.7, longitude: -74.0}), point.distance(p1, p2)

-- Lists
[1, 2, 3], list[0], size(list), [x IN list WHERE ...]

-- Maps
{key: value}, map.key, keys(map), properties(node)

-- NULL
IS NULL, IS NOT NULL, coalesce(v1, v2), toIntegerOrNull(s)
```

---

## Exercises

### Exercise 12.1: Numeric Operations
1. Calculate percentage of total for each product category
2. Generate a sequence of dates for the next 30 days
3. Round prices to nearest 0.05

### Exercise 12.2: Temporal Operations
1. Find all events occurring this week
2. Calculate the age of each person from their birthDate
3. Group orders by quarter and calculate quarterly totals

### Exercise 12.3: Spatial Queries
1. Store locations for all stores and find nearest to a user
2. Find all locations within 10km of a central point
3. Calculate total distance of a delivery route

### Exercise 12.4: Complex Types
1. Create a nested structure representing a product with variants
2. Parse a JSON-like string into usable data
3. Transform a list of maps into a summary report

---

**Next Chapter: [Chapter 13: List Operations](13-list-operations.md)**
