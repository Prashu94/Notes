# Chapter 11: Cypher - Functions

## Learning Objectives
By the end of this chapter, you will:
- Use string manipulation functions effectively
- Apply mathematical and numeric functions
- Work with temporal functions for dates and times
- Utilize type conversion functions
- Apply predicate and scalar functions

---

## 11.1 String Functions

### Basic String Operations

```cypher
// String length
RETURN size('Hello World') AS length  // 11

// Case conversion
RETURN 
    toUpper('hello') AS upper,        // HELLO
    toLower('HELLO') AS lower,        // hello
    toUpperCase('hello') AS upper2,   // HELLO (alias)
    toLowerCase('HELLO') AS lower2    // hello (alias)

// Trimming whitespace
RETURN 
    trim('  hello  ') AS trimmed,           // 'hello'
    ltrim('  hello  ') AS leftTrimmed,      // 'hello  '
    rtrim('  hello  ') AS rightTrimmed,     // '  hello'
    btrim('xxhelloxx', 'x') AS customTrim   // 'hello'

// Reverse string
RETURN reverse('hello') AS reversed  // 'olleh'
```

### Substring and Character Operations

```cypher
// Substring extraction
RETURN 
    substring('Hello World', 0, 5) AS sub1,   // 'Hello'
    substring('Hello World', 6) AS sub2,       // 'World'
    left('Hello World', 5) AS leftPart,        // 'Hello'
    right('Hello World', 5) AS rightPart       // 'World'

// Character at position
RETURN 
    substring('Hello', 1, 1) AS char2  // 'e' (0-indexed)

// Split string
RETURN split('a,b,c,d', ',') AS parts  // ['a', 'b', 'c', 'd']

// Join list to string
RETURN 
    'Hello' + ' ' + 'World' AS concat1,           // 'Hello World'
    apoc.text.join(['a', 'b', 'c'], '-') AS joined // 'a-b-c' (APOC)
```

### String Search and Matching

```cypher
// Contains, starts with, ends with (in WHERE)
MATCH (p:Person)
WHERE p.name STARTS WITH 'A'
  AND p.email ENDS WITH '.com'
  AND p.bio CONTAINS 'developer'
RETURN p.name

// Find position of substring
RETURN 
    apoc.text.indexOf('Hello World', 'World') AS pos  // 6 (APOC)

// Replace substring
RETURN replace('Hello World', 'World', 'Neo4j') AS replaced
// 'Hello Neo4j'

// Regular expression match
RETURN 'test@email.com' =~ '.*@.*\\.com' AS isEmail  // true
```

### String Formatting

```cypher
// Padding
RETURN 
    apoc.text.lpad('42', 5, '0') AS leftPad,   // '00042'
    apoc.text.rpad('Hi', 5, '.') AS rightPad   // 'Hi...'

// Format numbers as strings
RETURN 
    toString(3.14159) AS numStr,
    apoc.number.format(1234567.89, '#,##0.00') AS formatted
    // '1,234,567.89'

// String interpolation (using concatenation)
WITH 'Alice' AS name, 30 AS age
RETURN 'Name: ' + name + ', Age: ' + toString(age) AS message
```

---

## 11.2 Mathematical Functions

### Basic Math

```cypher
// Absolute value
RETURN abs(-42) AS absolute  // 42

// Sign
RETURN sign(-5) AS s1, sign(0) AS s2, sign(5) AS s3
// -1, 0, 1

// Rounding
RETURN 
    round(3.7) AS rounded,      // 4
    round(3.14159, 2) AS r2,    // 3.14
    floor(3.7) AS floored,      // 3
    ceil(3.2) AS ceiling        // 4

// Truncate (toward zero)
RETURN 
    toInteger(3.7) AS trunc1,   // 3
    toInteger(-3.7) AS trunc2   // -3
```

### Power and Roots

```cypher
// Power
RETURN 
    2 ^ 10 AS power1,           // 1024
    pow(2, 10) AS power2        // 1024.0 (same as ^)

// Square root
RETURN sqrt(16) AS sqRoot  // 4.0

// Exponential and logarithm
RETURN 
    exp(1) AS e,               // 2.718281828...
    log(e()) AS ln,            // 1.0
    log10(100) AS log10        // 2.0
```

### Trigonometric Functions

```cypher
// Basic trig
RETURN 
    sin(pi() / 2) AS sine,      // 1.0
    cos(0) AS cosine,           // 1.0
    tan(pi() / 4) AS tangent    // ~1.0

// Inverse trig
RETURN 
    asin(1) AS arcSin,          // pi/2
    acos(0) AS arcCos,          // pi/2
    atan(1) AS arcTan           // pi/4

// Degrees and radians
RETURN 
    degrees(pi()) AS deg,       // 180.0
    radians(180) AS rad         // pi
```

### Random Numbers

```cypher
// Random float between 0 and 1
RETURN rand() AS random

// Random integer in range
RETURN toInteger(rand() * 100) AS randomInt  // 0-99

// Random selection from list
WITH ['a', 'b', 'c', 'd'] AS items
RETURN items[toInteger(rand() * size(items))] AS randomItem

// Generate multiple random values
UNWIND range(1, 5) AS i
RETURN i, rand() AS randomValue
```

---

## 11.3 Temporal Functions

### Getting Current Date/Time

```cypher
// Current timestamps
RETURN 
    date() AS today,                    // 2026-01-25
    time() AS currentTime,              // 14:30:45.123456789
    datetime() AS now,                  // 2026-01-25T14:30:45.123Z
    localdatetime() AS localNow,        // 2026-01-25T14:30:45.123
    localtime() AS localTimeNow         // 14:30:45.123456789

// With timezone
RETURN 
    datetime({timezone: 'America/New_York'}) AS nyTime,
    datetime({timezone: 'Europe/London'}) AS londonTime
```

### Creating Temporal Values

```cypher
// Create date
RETURN 
    date('2026-01-25') AS fromString,
    date({year: 2026, month: 1, day: 25}) AS fromMap

// Create time
RETURN 
    time('14:30:00') AS fromString,
    time({hour: 14, minute: 30, second: 0}) AS fromMap

// Create datetime
RETURN 
    datetime('2026-01-25T14:30:00Z') AS fromISO,
    datetime({year: 2026, month: 1, day: 25, hour: 14}) AS fromMap

// From epoch (milliseconds)
RETURN datetime({epochMillis: 1737817200000}) AS fromEpoch
```

### Extracting Components

```cypher
// Date components
WITH date('2026-01-25') AS d
RETURN 
    d.year AS year,           // 2026
    d.month AS month,         // 1
    d.day AS day,             // 25
    d.dayOfWeek AS dow,       // 7 (Sunday)
    d.dayOfYear AS doy,       // 25
    d.week AS week,           // 4
    d.quarter AS quarter      // 1

// Time components
WITH time('14:30:45.123') AS t
RETURN 
    t.hour AS hour,           // 14
    t.minute AS minute,       // 30
    t.second AS second,       // 45
    t.millisecond AS ms       // 123
```

### Duration Operations

```cypher
// Create duration
RETURN 
    duration('P1Y2M3D') AS yearMonthDay,      // 1 year, 2 months, 3 days
    duration('PT2H30M') AS hourMinute,         // 2 hours, 30 minutes
    duration({days: 5, hours: 3}) AS fromMap

// Add duration to date
RETURN 
    date() + duration('P7D') AS nextWeek,
    datetime() + duration('PT2H') AS twoHoursLater,
    date() - duration('P1M') AS lastMonth

// Duration between dates
WITH date('2026-01-01') AS start, date('2026-12-31') AS end
RETURN duration.between(start, end) AS diff
// P11M30D (11 months, 30 days)

// Duration in specific units
WITH date('2026-01-01') AS start, date('2026-12-31') AS end
RETURN 
    duration.inDays(start, end).days AS totalDays,
    duration.inMonths(start, end).months AS totalMonths
```

### Truncating Temporal Values

```cypher
// Truncate to specific unit
RETURN 
    date.truncate('month', date()) AS monthStart,     // 2026-01-01
    date.truncate('year', date()) AS yearStart,       // 2026-01-01
    date.truncate('week', date()) AS weekStart,       // Monday of week
    datetime.truncate('hour', datetime()) AS hourStart
```

---

## 11.4 Type Conversion Functions

### Converting to String

```cypher
RETURN 
    toString(42) AS intStr,           // '42'
    toString(3.14) AS floatStr,       // '3.14'
    toString(true) AS boolStr,        // 'true'
    toString(date()) AS dateStr,      // '2026-01-25'
    toString([1, 2, 3]) AS listStr    // '[1, 2, 3]'
```

### Converting to Numbers

```cypher
// To integer
RETURN 
    toInteger('42') AS fromStr,       // 42
    toInteger(3.7) AS fromFloat,      // 3 (truncates)
    toInteger('3.14') AS fromDecStr,  // 3
    toIntegerOrNull('abc') AS invalid // null

// To float
RETURN 
    toFloat('3.14') AS fromStr,       // 3.14
    toFloat(42) AS fromInt,           // 42.0
    toFloatOrNull('abc') AS invalid   // null
```

### Converting to Boolean

```cypher
RETURN 
    toBoolean('true') AS t1,          // true
    toBoolean('false') AS f1,         // false
    toBoolean('TRUE') AS t2,          // true
    toBooleanOrNull('yes') AS invalid // null
```

### List Conversions

```cypher
// String to list of characters
WITH 'hello' AS str
RETURN [c IN split(str, '') | c] AS chars
// ['h', 'e', 'l', 'l', 'o']

// Convert list elements
WITH ['1', '2', '3'] AS strList
RETURN [s IN strList | toInteger(s)] AS intList
// [1, 2, 3]
```

---

## 11.5 Predicate Functions

### Type Checking

```cypher
// Check value types
WITH [1, 'hello', null, true, [1,2], {a:1}] AS values
UNWIND values AS v
RETURN 
    v,
    valueType(v) AS type

// Results:
// 1        -> 'INTEGER'
// 'hello'  -> 'STRING'
// null     -> 'NULL'
// true     -> 'BOOLEAN'
// [1,2]    -> 'LIST<INTEGER>'
// {a:1}    -> 'MAP'
```

### NULL Checking

```cypher
// Check for NULL
MATCH (p:Person)
RETURN 
    p.name,
    p.middleName IS NULL AS hasNoMiddle,
    p.middleName IS NOT NULL AS hasMiddle,
    coalesce(p.middleName, 'N/A') AS displayMiddle
```

### List Predicates

```cypher
// ANY - at least one element satisfies
WITH [1, 2, 3, 4, 5] AS numbers
RETURN any(n IN numbers WHERE n > 3)  // true

// ALL - every element satisfies
WITH [2, 4, 6, 8] AS numbers
RETURN all(n IN numbers WHERE n % 2 = 0)  // true

// NONE - no element satisfies
WITH [1, 3, 5, 7] AS numbers
RETURN none(n IN numbers WHERE n % 2 = 0)  // true

// SINGLE - exactly one element satisfies
WITH [1, 2, 3, 4, 5] AS numbers
RETURN single(n IN numbers WHERE n = 3)  // true
```

---

## 11.6 Scalar Functions

### COALESCE

```cypher
// Return first non-null value
RETURN coalesce(null, null, 'default') AS value  // 'default'

// Practical usage
MATCH (p:Person)
RETURN 
    p.name,
    coalesce(p.nickname, p.firstName, 'Unknown') AS displayName
```

### CASE Expressions

```cypher
// Simple CASE
MATCH (p:Person)
RETURN p.name,
    CASE p.status
        WHEN 'A' THEN 'Active'
        WHEN 'I' THEN 'Inactive'
        WHEN 'P' THEN 'Pending'
        ELSE 'Unknown'
    END AS statusLabel

// Searched CASE
MATCH (p:Person)
RETURN p.name, p.age,
    CASE 
        WHEN p.age < 18 THEN 'Minor'
        WHEN p.age < 65 THEN 'Adult'
        ELSE 'Senior'
    END AS ageGroup

// CASE with NULL handling
MATCH (p:Person)
RETURN p.name,
    CASE 
        WHEN p.email IS NULL THEN 'No email'
        WHEN p.email CONTAINS '@company.com' THEN 'Internal'
        ELSE 'External'
    END AS emailType
```

### HEAD and LAST

```cypher
// First and last elements of list
WITH [1, 2, 3, 4, 5] AS numbers
RETURN 
    head(numbers) AS first,  // 1
    last(numbers) AS last    // 5

// Practical usage
MATCH (p:Person)-[:VISITED]->(place:Place)
WITH p, collect(place) AS visitedPlaces
ORDER BY p.lastVisitDate
RETURN p.name, 
       head(visitedPlaces).name AS firstVisit,
       last(visitedPlaces).name AS recentVisit
```

### NULLIF and IIF

```cypher
// NULLIF - returns null if values equal
RETURN nullif(5, 5) AS result1  // null
RETURN nullif(5, 3) AS result2  // 5

// Avoid division by zero
WITH 100 AS numerator, 0 AS denominator
RETURN numerator / nullif(denominator, 0) AS safeDiv  // null instead of error
```

---

## 11.7 Graph Functions

### Node and Relationship Info

```cypher
// Get ID
MATCH (p:Person {name: 'Alice'})
RETURN 
    id(p) AS internalId,        // Deprecated
    elementId(p) AS elementId   // Recommended

// Get labels and types
MATCH (n)-[r]->(m)
RETURN 
    labels(n) AS nodeLabels,    // ['Person', 'Employee']
    type(r) AS relType          // 'KNOWS'

// Get properties
MATCH (p:Person {name: 'Alice'})
RETURN 
    properties(p) AS allProps,
    keys(p) AS propertyKeys
```

### Path Functions

```cypher
// Path analysis
MATCH path = (a:Person)-[:KNOWS*1..3]->(b:Person)
WHERE a.name = 'Alice'
RETURN 
    nodes(path) AS allNodes,
    relationships(path) AS allRels,
    length(path) AS pathLength,
    [n IN nodes(path) | n.name] AS names
```

### startNode and endNode

```cypher
// Get relationship endpoints
MATCH ()-[r:KNOWS]->()
WITH r LIMIT 1
RETURN 
    startNode(r).name AS from,
    endNode(r).name AS to
```

---

## 11.8 APOC Functions (Extended Library)

### Text Functions

```cypher
// Levenshtein distance (string similarity)
RETURN apoc.text.levenshteinDistance('hello', 'hallo') AS distance  // 1

// Soundex (phonetic matching)
RETURN apoc.text.soundex('Robert') AS soundex  // R163

// Fuzzy match
RETURN apoc.text.fuzzyMatch('hello world', 'helo wrld') AS similarity

// Capitalize
RETURN apoc.text.capitalize('hello world') AS cap  // 'Hello world'
RETURN apoc.text.capitalizeAll('hello world') AS capAll  // 'Hello World'

// Slug generation
RETURN apoc.text.slug('Hello World!') AS slug  // 'hello-world'
```

### Collection Functions

```cypher
// Flatten nested lists
RETURN apoc.coll.flatten([[1,2], [3,4], [5]]) AS flat
// [1, 2, 3, 4, 5]

// Zip lists
RETURN apoc.coll.zip(['a','b','c'], [1,2,3]) AS zipped
// [['a',1], ['b',2], ['c',3]]

// Partition list
RETURN apoc.coll.partition([1,2,3,4,5], 2) AS partitioned
// [[1,2], [3,4], [5]]

// Set operations
RETURN 
    apoc.coll.union([1,2,3], [3,4,5]) AS union,          // [1,2,3,4,5]
    apoc.coll.intersection([1,2,3], [2,3,4]) AS inter,  // [2,3]
    apoc.coll.subtract([1,2,3], [2]) AS diff            // [1,3]
```

### JSON Functions

```cypher
// Parse JSON
WITH '{"name": "Alice", "age": 30}' AS jsonStr
RETURN apoc.convert.fromJsonMap(jsonStr) AS data

// Convert to JSON
MATCH (p:Person {name: 'Alice'})
RETURN apoc.convert.toJson(properties(p)) AS json

// Access JSON path
WITH '{"user": {"name": "Alice", "address": {"city": "NYC"}}}' AS json
RETURN apoc.json.path(json, '$.user.address.city') AS city  // 'NYC'
```

---

## 11.9 Python Examples

### Using Functions in Queries

```python
from neo4j import GraphDatabase
from datetime import date, timedelta

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def string_function_examples(driver):
    with driver.session() as session:
        # Search with string functions
        result = session.run("""
            MATCH (p:Person)
            WHERE toLower(p.name) CONTAINS toLower($search)
               OR p.email ENDS WITH $domain
            RETURN p.name, 
                   toUpper(substring(p.name, 0, 1)) + 
                   toLower(substring(p.name, 1)) AS formatted
        """, search="alice", domain="@company.com")
        
        for record in result:
            print(f"{record['name']} -> {record['formatted']}")

def date_function_examples(driver):
    with driver.session() as session:
        # Date calculations
        result = session.run("""
            MATCH (o:Order)
            WHERE o.orderDate >= date() - duration('P30D')
            RETURN 
                o.id,
                o.orderDate,
                duration.inDays(o.orderDate, date()).days AS daysAgo,
                o.orderDate.dayOfWeek AS dayOfWeek
            ORDER BY o.orderDate DESC
        """)
        
        print("\nRecent Orders:")
        for record in result:
            print(f"  Order {record['id']}: {record['daysAgo']} days ago")

def aggregation_with_functions(driver):
    with driver.session() as session:
        # Complex aggregation with type conversions
        result = session.run("""
            MATCH (p:Product)
            RETURN 
                p.category,
                count(p) AS count,
                round(avg(p.price), 2) AS avgPrice,
                toString(min(p.price)) + ' - ' + toString(max(p.price)) AS priceRange
        """)
        
        print("\nProduct Statistics:")
        for record in result:
            print(f"  {record['category']}: {record['count']} items, "
                  f"avg ${record['avgPrice']}, range: ${record['priceRange']}")

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    string_function_examples(driver)
    date_function_examples(driver)
    aggregation_with_functions(driver)
```

---

## Summary

### Key Function Categories

| Category | Key Functions |
|----------|---------------|
| **String** | `size`, `toUpper`, `toLower`, `trim`, `substring`, `split`, `replace` |
| **Math** | `abs`, `round`, `floor`, `ceil`, `sqrt`, `pow`, `rand` |
| **Temporal** | `date`, `time`, `datetime`, `duration`, `duration.between` |
| **Conversion** | `toString`, `toInteger`, `toFloat`, `toBoolean` |
| **Predicate** | `any`, `all`, `none`, `single`, `coalesce` |
| **Graph** | `labels`, `type`, `properties`, `keys`, `nodes`, `relationships` |

### Quick Reference

```cypher
-- String
size(str), toUpper(str), substring(str, start, len), split(str, delim)

-- Math
round(n, precision), abs(n), rand(), sqrt(n)

-- Temporal
date(), datetime(), duration('P1D'), date.truncate('month', d)

-- Conversion
toString(val), toInteger(str), toFloat(str)

-- Predicate
coalesce(v1, v2, ...), CASE WHEN ... THEN ... END

-- Graph
labels(node), type(rel), properties(n), nodes(path)
```

---

## Exercises

### Exercise 11.1: String Functions
1. Extract domain from email addresses using string functions
2. Create a full name from firstName and lastName, handling NULLs
3. Search for names matching a pattern (case-insensitive)

### Exercise 11.2: Date/Time Functions
1. Find orders placed in the last 7 days
2. Calculate age from birthDate
3. Group orders by month and day of week

### Exercise 11.3: Type Conversions
1. Parse a CSV-like string into a list of integers
2. Format prices as currency strings
3. Convert various data types and handle invalid inputs safely

### Exercise 11.4: Combined Functions
1. Calculate discounted prices rounded to 2 decimal places
2. Generate a formatted report string with date and numbers
3. Create a search function that matches partial names and emails

---

**Next Chapter: [Chapter 12: Data Types](12-data-types.md)**
