# JSON and JSONB

## Overview

PostgreSQL provides powerful JSON and JSONB data types, enabling document-oriented storage alongside traditional relational data. These features allow PostgreSQL to function as both a relational and NoSQL database.

## Table of Contents
- [JSON vs JSONB](#json-vs-jsonb)
- [Creating and Storing JSON](#creating-and-storing-json)
- [Querying JSON Data](#querying-json-data)
- [JSON Operators](#json-operators)
- [JSON Functions](#json-functions)
- [Indexing JSON](#indexing-json)
- [JSON Aggregation](#json-aggregation)
- [Modifying JSON](#modifying-json)
- [JSON Validation](#json-validation)
- [Best Practices](#best-practices)

## JSON vs JSONB

### Differences

```sql
-- JSON: Text storage, preserves exact input
CREATE TABLE json_test (
    id SERIAL PRIMARY KEY,
    data JSON
);

-- JSONB: Binary storage, more efficient
CREATE TABLE jsonb_test (
    id SERIAL PRIMARY KEY,
    data JSONB
);

-- JSON preserves whitespace and key order
INSERT INTO json_test (data) VALUES 
('{"name":  "John",   "age": 30}');

SELECT data FROM json_test;
-- Returns: {"name":  "John",   "age": 30}  (exact input)

-- JSONB removes whitespace, may reorder keys
INSERT INTO jsonb_test (data) VALUES 
('{"name":  "John",   "age": 30}');

SELECT data FROM jsonb_test;
-- Returns: {"age": 30, "name": "John"}  (normalized)

-- Comparison:
-- JSON:
--   + Faster input (no processing)
--   + Preserves exact format
--   - Slower processing
--   - No indexing support
--   - Larger storage

-- JSONB:
--   + Much faster processing
--   + Supports indexing (GIN, GiST)
--   + Smaller storage
--   + Supports more operators
--   - Slower input (parsing)
--   - Normalizes format

-- Recommendation: Use JSONB unless you need exact format preservation
```

### Storage Size

```sql
-- Check storage size
CREATE TABLE storage_test (
    id SERIAL PRIMARY KEY,
    json_data JSON,
    jsonb_data JSONB
);

INSERT INTO storage_test (json_data, jsonb_data) VALUES 
('{"name": "John", "age": 30, "email": "john@example.com"}',
 '{"name": "John", "age": 30, "email": "john@example.com"}');

SELECT 
    pg_column_size(json_data) as json_size,
    pg_column_size(jsonb_data) as jsonb_size
FROM storage_test;
-- JSONB is typically 10-20% larger due to binary overhead
-- But faster processing compensates
```

## Creating and Storing JSON

### Basic JSON Storage

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    profile JSONB,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT now()
);

-- Insert JSON data
INSERT INTO users (username, profile) VALUES 
('john_doe', '{"name": "John Doe", "age": 30, "email": "john@example.com"}');

-- Insert with jsonb_build_object
INSERT INTO users (username, profile) VALUES 
('jane_doe', jsonb_build_object(
    'name', 'Jane Doe',
    'age', 28,
    'email', 'jane@example.com',
    'address', jsonb_build_object(
        'city', 'New York',
        'country', 'USA'
    )
));

-- Insert array
INSERT INTO users (username, profile) VALUES 
('bob', '{"name": "Bob", "hobbies": ["reading", "gaming", "cooking"]}');

-- Insert nested structures
INSERT INTO users (username, profile) VALUES 
('alice', '{
    "name": "Alice",
    "age": 25,
    "contacts": {
        "email": "alice@example.com",
        "phone": "+1234567890"
    },
    "tags": ["developer", "designer"]
}');
```

### JSON Construction Functions

```sql
-- jsonb_build_object: Create object from key-value pairs
SELECT jsonb_build_object(
    'name', 'John',
    'age', 30,
    'active', true
);
-- Result: {"age": 30, "name": "John", "active": true}

-- jsonb_build_array: Create array
SELECT jsonb_build_array(1, 2, 3, 'four', true);
-- Result: [1, 2, 3, "four", true]

-- json_object: Create object from arrays
SELECT json_object(
    ARRAY['name', 'age', 'city'],
    ARRAY['John', '30', 'NYC']
);
-- Result: {"name": "John", "age": "30", "city": "NYC"}

-- to_jsonb: Convert row to JSON
SELECT to_jsonb(users.*) FROM users LIMIT 1;

-- row_to_json: Convert row with nested objects
SELECT row_to_json(u) 
FROM (
    SELECT id, username, profile 
    FROM users 
    WHERE id = 1
) u;
```

## Querying JSON Data

### Accessing JSON Fields

```sql
-- -> operator: Get JSON object field (returns JSON)
SELECT profile -> 'name' as name FROM users;
-- Returns: "John Doe" (with quotes)

-- ->> operator: Get JSON object field as text
SELECT profile ->> 'name' as name FROM users;
-- Returns: John Doe (without quotes)

-- Access nested fields
SELECT profile -> 'contacts' -> 'email' as email FROM users;

-- Chain operators
SELECT profile -> 'address' ->> 'city' as city FROM users;

-- Array access (0-indexed)
SELECT profile -> 'hobbies' -> 0 as first_hobby FROM users;

-- Get array element as text
SELECT profile -> 'hobbies' ->> 1 as second_hobby FROM users;

-- Path access
SELECT profile #> '{contacts, email}' as email FROM users;
SELECT profile #>> '{contacts, phone}' as phone FROM users;
-- #>  returns JSON
-- #>> returns text
```

### Filtering by JSON Content

```sql
-- WHERE with JSON fields
SELECT username, profile ->> 'name' as name
FROM users
WHERE profile ->> 'age' = '30';

-- Cast to proper type
SELECT username, profile ->> 'age' as age
FROM users
WHERE (profile ->> 'age')::int > 25;

-- Check for key existence
SELECT username
FROM users
WHERE profile ? 'email';  -- Has 'email' key?

-- Check for any of multiple keys
SELECT username
FROM users
WHERE profile ?| ARRAY['email', 'phone'];  -- Has 'email' OR 'phone'?

-- Check for all keys
SELECT username
FROM users
WHERE profile ?& ARRAY['name', 'age'];  -- Has 'name' AND 'age'?

-- JSON containment (@>)
SELECT username
FROM users
WHERE profile @> '{"age": 30}';  -- Contains this JSON

-- Contained by (<@)
SELECT username
FROM users
WHERE '{"name": "John Doe"}' <@ profile;  -- Is contained in profile
```

### Array Operations

```sql
-- Array contains specific value
SELECT username
FROM users
WHERE profile -> 'hobbies' @> '"reading"';

-- Get array length
SELECT 
    username,
    jsonb_array_length(profile -> 'hobbies') as hobby_count
FROM users;

-- Expand array to rows
SELECT 
    username,
    jsonb_array_elements_text(profile -> 'hobbies') as hobby
FROM users;

-- Filter by array element
SELECT username
FROM users
WHERE profile -> 'tags' @> '["developer"]';
```

## JSON Operators

### Comparison Operators

```sql
-- Equality
SELECT * FROM users WHERE profile = '{"name": "John"}';

-- Containment (@>)
SELECT * FROM users 
WHERE profile @> '{"age": 30, "name": "John"}';
-- True if left JSON contains right JSON

-- Contained by (<@)
SELECT * FROM users 
WHERE '{"age": 30}' <@ profile;
-- True if left JSON is contained in right JSON

-- Key existence (?)
SELECT * FROM users WHERE profile ? 'email';

-- Any key exists (?|)
SELECT * FROM users 
WHERE profile ?| ARRAY['email', 'phone'];

-- All keys exist (?&)
SELECT * FROM users 
WHERE profile ?& ARRAY['name', 'age', 'email'];
```

### Path Operators

```sql
-- JSON path (#>, #>>)
SELECT profile #> '{contacts, email}' FROM users;  -- Returns JSON
SELECT profile #>> '{contacts, email}' FROM users; -- Returns text

-- Deep path access
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    data JSONB
);

INSERT INTO orders (data) VALUES ('{
    "customer": {
        "name": "John",
        "address": {
            "city": "NYC",
            "zip": "10001"
        }
    },
    "items": [
        {"name": "Widget", "price": 19.99},
        {"name": "Gadget", "price": 29.99}
    ]
}');

-- Access nested city
SELECT data #>> '{customer, address, city}' as city FROM orders;

-- Access array element property
SELECT data #>> '{items, 0, name}' as first_item FROM orders;
```

## JSON Functions

### Extraction Functions

```sql
-- jsonb_extract_path: Extract nested value
SELECT jsonb_extract_path(profile, 'contacts', 'email') FROM users;

-- jsonb_extract_path_text: Extract as text
SELECT jsonb_extract_path_text(profile, 'contacts', 'email') FROM users;

-- jsonb_typeof: Get JSON type
SELECT 
    username,
    jsonb_typeof(profile -> 'age') as age_type,
    jsonb_typeof(profile -> 'hobbies') as hobbies_type
FROM users;
-- Returns: number, array, object, string, boolean, null

-- jsonb_object_keys: Get object keys
SELECT jsonb_object_keys(profile) as key FROM users LIMIT 1;

-- jsonb_each: Expand object to key-value pairs
SELECT * FROM jsonb_each((SELECT profile FROM users LIMIT 1));

-- jsonb_each_text: Expand to key-text pairs
SELECT * FROM jsonb_each_text((SELECT profile FROM users LIMIT 1));
```

### Array Functions

```sql
-- jsonb_array_elements: Expand array to rows (as JSONB)
SELECT jsonb_array_elements(profile -> 'hobbies') as hobby
FROM users
WHERE profile ? 'hobbies';

-- jsonb_array_elements_text: Expand to text rows
SELECT 
    username,
    jsonb_array_elements_text(profile -> 'hobbies') as hobby
FROM users
WHERE profile ? 'hobbies';

-- jsonb_array_length: Array size
SELECT 
    username,
    jsonb_array_length(profile -> 'tags') as tag_count
FROM users
WHERE profile ? 'tags';

-- jsonb_to_recordset: Array of objects to table
SELECT * FROM jsonb_to_recordset('[
    {"name": "John", "age": 30},
    {"name": "Jane", "age": 25}
]') AS x(name TEXT, age INT);
```

### Conversion Functions

```sql
-- to_jsonb: Convert value to JSONB
SELECT to_jsonb('hello'::text);
SELECT to_jsonb(123);
SELECT to_jsonb(true);

-- array_to_json: Convert array
SELECT array_to_json(ARRAY[1, 2, 3, 4]);

-- row_to_json: Convert row
SELECT row_to_json(u)
FROM (SELECT id, username FROM users LIMIT 1) u;

-- jsonb_populate_record: JSON to record
CREATE TYPE user_type AS (name TEXT, age INT);

SELECT * FROM jsonb_populate_record(
    null::user_type,
    '{"name": "John", "age": 30}'
);

-- jsonb_to_record: JSON to anonymous record
SELECT * FROM jsonb_to_record('{"name": "John", "age": 30}') 
AS x(name TEXT, age INT);
```

## Indexing JSON

### GIN Indexes

Most efficient for JSONB:

```sql
-- Default GIN index (supports @>, ?, ?&, ?| operators)
CREATE INDEX idx_users_profile ON users USING GIN(profile);

-- Query uses index automatically
EXPLAIN SELECT * FROM users WHERE profile @> '{"age": 30}';
-- Shows: Bitmap Index Scan using idx_users_profile

-- Index specific path
CREATE INDEX idx_users_email ON users USING GIN((profile -> 'contacts'));

-- Index for key existence
CREATE INDEX idx_users_keys ON users USING GIN(profile jsonb_ops);

-- Index for path operations
CREATE INDEX idx_users_path ON users USING GIN(profile jsonb_path_ops);
-- Smaller, faster, but only supports @> and @? operators
```

### Expression Indexes

```sql
-- Index specific field
CREATE INDEX idx_users_age ON users ((profile ->> 'age'));

-- Index with cast
CREATE INDEX idx_users_age_int ON users (((profile ->> 'age')::int));

-- Use in query
SELECT * FROM users 
WHERE (profile ->> 'age')::int > 25;
-- Uses idx_users_age_int

-- Index nested field
CREATE INDEX idx_users_city ON users ((profile #>> '{address, city}'));

-- Partial index
CREATE INDEX idx_active_users ON users USING GIN(profile)
WHERE (profile ->> 'active')::boolean = true;
```

### B-tree Indexes for Sorting

```sql
-- B-tree for sorting by JSON field
CREATE INDEX idx_users_name ON users ((profile ->> 'name'));

SELECT username, profile ->> 'name' as name
FROM users
ORDER BY profile ->> 'name';
-- Uses idx_users_name for sorting
```

## JSON Aggregation

### Building JSON from Rows

```sql
-- json_agg: Aggregate rows to JSON array
SELECT json_agg(username) FROM users;
-- Result: ["john_doe", "jane_doe", "bob", "alice"]

-- Aggregate objects
SELECT json_agg(json_build_object(
    'id', id,
    'username', username,
    'name', profile ->> 'name'
)) FROM users;

-- jsonb_object_agg: Build object from key-value pairs
SELECT jsonb_object_agg(username, profile -> 'name')
FROM users;
-- Result: {"john_doe": "John Doe", "jane_doe": "Jane Doe", ...}

-- Nested aggregation
SELECT 
    u.username,
    jsonb_build_object(
        'user', u.username,
        'orders', (
            SELECT json_agg(json_build_object('id', o.id, 'total', o.total))
            FROM orders o
            WHERE o.user_id = u.id
        )
    ) as user_data
FROM users u;
```

### Grouping with JSON

```sql
-- Group and aggregate to JSON
SELECT 
    profile ->> 'city' as city,
    json_agg(username) as users
FROM users
GROUP BY profile ->> 'city';

-- Complex aggregation
SELECT 
    profile ->> 'country' as country,
    count(*) as user_count,
    json_agg(json_build_object(
        'username', username,
        'name', profile ->> 'name',
        'age', (profile ->> 'age')::int
    ) ORDER BY (profile ->> 'age')::int) as users
FROM users
GROUP BY profile ->> 'country';
```

## Modifying JSON

### Concatenation

```sql
-- Concatenate objects (||)
UPDATE users 
SET profile = profile || '{"last_login": "2024-01-15"}'
WHERE username = 'john_doe';

-- Concatenate arrays
UPDATE users
SET profile = jsonb_set(
    profile,
    '{hobbies}',
    (profile -> 'hobbies') || '["swimming"]'
)
WHERE username = 'bob';
```

### Setting Values

```sql
-- jsonb_set: Set value at path
UPDATE users
SET profile = jsonb_set(profile, '{age}', '31')
WHERE username = 'john_doe';

-- Set nested value
UPDATE users
SET profile = jsonb_set(profile, '{contacts, phone}', '"+1234567890"')
WHERE username = 'john_doe';

-- Create missing path
UPDATE users
SET profile = jsonb_set(
    profile, 
    '{address, city}', 
    '"New York"',
    true  -- create_missing = true
)
WHERE username = 'john_doe';

-- Set array element
UPDATE users
SET profile = jsonb_set(profile, '{hobbies, 0}', '"music"')
WHERE username = 'bob';
```

### Inserting Values

```sql
-- jsonb_insert: Insert value
UPDATE users
SET profile = jsonb_insert(
    profile,
    '{hobbies, 0}',  -- Path
    '"hiking"',       -- Value
    true              -- insert_after = true
)
WHERE username = 'bob';

-- Insert at beginning (insert_after = false)
UPDATE users
SET profile = jsonb_insert(
    profile,
    '{hobbies, 0}',
    '"painting"',
    false
)
WHERE username = 'bob';
```

### Deleting Keys

```sql
-- Remove key (-)
UPDATE users
SET profile = profile - 'last_login'
WHERE username = 'john_doe';

-- Remove multiple keys
UPDATE users
SET profile = profile - ARRAY['temp_field1', 'temp_field2'];

-- Remove nested key
UPDATE users
SET profile = profile #- '{contacts, phone}'
WHERE username = 'john_doe';

-- Remove array element by index
UPDATE users
SET profile = profile #- '{hobbies, 1}'
WHERE username = 'bob';
```

### Replacing Values

```sql
-- jsonb_set with replacement
UPDATE users
SET profile = jsonb_set(
    profile,
    '{name}',
    to_jsonb(upper(profile ->> 'name'))
)
WHERE username = 'john_doe';

-- Conditional update
UPDATE users
SET profile = CASE 
    WHEN (profile ->> 'age')::int >= 18 
    THEN profile || '{"status": "adult"}'
    ELSE profile || '{"status": "minor"}'
END;
```

## JSON Validation

### Schema Validation

```sql
-- Install check constraint
ALTER TABLE users ADD CONSTRAINT profile_has_name
CHECK (profile ? 'name');

ALTER TABLE users ADD CONSTRAINT profile_age_valid
CHECK ((profile ->> 'age')::int BETWEEN 0 AND 150);

-- Complex validation
ALTER TABLE users ADD CONSTRAINT profile_valid
CHECK (
    profile ? 'name' AND
    profile ? 'email' AND
    (profile ->> 'age')::int >= 0
);

-- Custom validation function
CREATE FUNCTION validate_user_profile(profile JSONB) 
RETURNS BOOLEAN AS $$
BEGIN
    -- Check required fields
    IF NOT (profile ? 'name' AND profile ? 'email') THEN
        RETURN FALSE;
    END IF;
    
    -- Validate age
    IF profile ? 'age' THEN
        IF (profile ->> 'age')::int < 0 OR (profile ->> 'age')::int > 150 THEN
            RETURN FALSE;
        END IF;
    END IF;
    
    -- Validate email format
    IF NOT (profile ->> 'email' ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

ALTER TABLE users ADD CONSTRAINT profile_schema_valid
CHECK (validate_user_profile(profile));
```

### JSON Schema (Extension)

```sql
-- Use jsonschema extension (if available)
-- CREATE EXTENSION jsonschema;

-- Define schema
CREATE TABLE user_schema (
    schema JSONB
);

INSERT INTO user_schema VALUES ('{
    "type": "object",
    "required": ["name", "email"],
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "age": {"type": "integer", "minimum": 0, "maximum": 150}
    }
}');

-- Validate against schema
-- SELECT jsonschema_is_valid(
--     (SELECT schema FROM user_schema),
--     '{"name": "John", "email": "john@example.com", "age": 30}'
-- );
```

## Best Practices

### 1. Choose JSONB Over JSON

```sql
-- Always prefer JSONB unless you need exact format
CREATE TABLE good_design (
    id SERIAL PRIMARY KEY,
    data JSONB  -- Good: indexable, efficient
);

CREATE TABLE bad_design (
    id SERIAL PRIMARY KEY,
    data JSON   -- Bad: slower, no indexing
);
```

### 2. Index Appropriately

```sql
-- For containment queries
CREATE INDEX idx_data_gin ON table_name USING GIN(data);

-- For specific fields (frequent queries)
CREATE INDEX idx_data_email ON table_name ((data ->> 'email'));

-- For sorting
CREATE INDEX idx_data_created ON table_name ((data ->> 'created_at'));
```

### 3. Normalize When Needed

```sql
-- Don't over-use JSON - normalize frequently queried data
CREATE TABLE users_normalized (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,  -- Normalized for queries
    age INT,              -- Normalized for filtering
    profile JSONB         -- Additional flexible data
);

CREATE INDEX ON users_normalized (email);
CREATE INDEX ON users_normalized (age);
```

### 4. Use Constraints

```sql
-- Ensure data quality
ALTER TABLE users ADD CONSTRAINT email_required
CHECK (profile ? 'email');

ALTER TABLE users ADD CONSTRAINT valid_age
CHECK ((profile ->> 'age')::int >= 0);
```

### 5. Monitor Performance

```sql
-- Check JSON query performance
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM users 
WHERE profile @> '{"age": 30}';

-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
WHERE tablename = 'users';
```

## Summary

PostgreSQL JSON features include:
- **Data types**: JSON (text) vs JSONB (binary, preferred)
- **Operators**: ->, ->>, @>, ?, ?|, ?& for querying
- **Functions**: Extract, aggregate, modify JSON data
- **Indexing**: GIN indexes for fast containment queries
- **Flexibility**: Combine relational and document models
- **Performance**: Efficient storage and querying with JSONB

PostgreSQL's JSON support enables flexible schema design while maintaining ACID guarantees.

## Next Steps

- Learn about [Arrays and Composite Types](./27-arrays-and-composite-types.md)
- Explore [Full-Text Search](./25-full-text-search.md)
- Study [Index Optimization](./22-index-optimization.md)
- Practice [Query Optimization](./20-query-optimization.md)
