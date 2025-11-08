# Arrays and Composite Types

## Overview

PostgreSQL supports array data types for storing multiple values in a single column, and composite types for creating custom structured data types. These features enable efficient storage and querying of complex data structures.

## Table of Contents
- [Array Types](#array-types)
- [Creating and Storing Arrays](#creating-and-storing-arrays)
- [Querying Arrays](#querying-arrays)
- [Array Functions and Operators](#array-functions-and-operators)
- [Array Indexing](#array-indexing)
- [Composite Types](#composite-types)
- [Using Composite Types](#using-composite-types)
- [Nested Structures](#nested-structures)
- [Best Practices](#best-practices)

## Array Types

### Declaring Array Columns

```sql
-- Array of integers
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    tags INTEGER[]
);

-- Array of text
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[],
    authors TEXT[]
);

-- Multi-dimensional arrays
CREATE TABLE matrices (
    id SERIAL PRIMARY KEY,
    data INTEGER[][]
);

-- Array with size limit (advisory, not enforced)
CREATE TABLE limited_array (
    id SERIAL PRIMARY KEY,
    values INTEGER[10]  -- Suggests max 10 elements, not enforced
);

-- Array of any data type
CREATE TABLE flexible (
    id SERIAL PRIMARY KEY,
    numbers INTEGER[],
    decimals NUMERIC[],
    timestamps TIMESTAMP[],
    json_docs JSONB[]
);
```

## Creating and Storing Arrays

### Inserting Array Data

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[],
    scores INTEGER[]
);

-- Array literal syntax
INSERT INTO posts (title, tags, scores) VALUES
    ('First Post', '{"postgresql", "database", "sql"}', '{5, 4, 5}');

-- ARRAY constructor
INSERT INTO posts (title, tags, scores) VALUES
    ('Second Post', ARRAY['python', 'programming'], ARRAY[4, 5, 3, 4]);

-- Empty array
INSERT INTO posts (title, tags, scores) VALUES
    ('Third Post', '{}', ARRAY[]::INTEGER[]);

-- NULL vs empty array
INSERT INTO posts (title, tags, scores) VALUES
    ('Fourth Post', NULL, '{}');  -- tags is NULL, scores is empty

-- Multi-dimensional array
INSERT INTO matrices (data) VALUES
    ('{{1, 2, 3}, {4, 5, 6}}');

-- Array from subquery
INSERT INTO posts (title, tags)
SELECT 'Generated Post', array_agg(tag_name)
FROM (VALUES ('tag1'), ('tag2'), ('tag3')) AS t(tag_name);
```

### Array Construction Functions

```sql
-- array_agg: Create array from rows
SELECT array_agg(name) FROM products;

-- array_agg with ordering
SELECT array_agg(name ORDER BY created_at DESC) as recent_products
FROM products;

-- array_agg with DISTINCT
SELECT array_agg(DISTINCT category) as categories
FROM products;

-- ARRAY constructor from values
SELECT ARRAY[1, 2, 3, 4, 5];

-- ARRAY from SELECT
SELECT ARRAY(SELECT id FROM products WHERE price > 100);

-- Generate series as array
SELECT ARRAY(SELECT generate_series(1, 10));

-- String to array
SELECT string_to_array('one,two,three', ',');
-- Result: {one,two,three}

SELECT string_to_array('one:two:three', ':');
-- Result: {one,two,three}
```

## Querying Arrays

### Accessing Array Elements

```sql
-- Access by index (1-based)
SELECT 
    title,
    tags[1] as first_tag,
    tags[2] as second_tag
FROM posts;

-- Access last element
SELECT 
    title,
    tags[array_length(tags, 1)] as last_tag
FROM posts;

-- Slice array [start:end]
SELECT 
    title,
    tags[1:2] as first_two_tags,
    tags[2:3] as middle_tags
FROM posts;

-- Slice from start
SELECT tags[:3] as first_three FROM posts;

-- Slice to end
SELECT tags[2:] as from_second FROM posts;
```

### Filtering by Array Content

```sql
-- Array contains value
SELECT * FROM posts
WHERE 'postgresql' = ANY(tags);

-- Array contains all values
SELECT * FROM posts
WHERE tags @> ARRAY['postgresql', 'database'];

-- Array is contained by
SELECT * FROM posts
WHERE ARRAY['postgresql'] <@ tags;

-- Array overlaps (has any common elements)
SELECT * FROM posts
WHERE tags && ARRAY['postgresql', 'python'];

-- Array equality
SELECT * FROM posts
WHERE tags = ARRAY['postgresql', 'database'];

-- Check if array is empty
SELECT * FROM posts
WHERE array_length(tags, 1) IS NULL OR array_length(tags, 1) = 0;

-- Check if NOT empty
SELECT * FROM posts
WHERE array_length(tags, 1) > 0;
```

### Searching Arrays

```sql
-- Find position of element
SELECT 
    title,
    array_position(tags, 'postgresql') as position
FROM posts;

-- Find all positions
SELECT 
    title,
    array_positions(tags, 'database') as positions
FROM posts;

-- Case-insensitive search (using unnest)
SELECT title
FROM posts
WHERE EXISTS (
    SELECT 1 FROM unnest(tags) tag 
    WHERE lower(tag) = lower('PostgreSQL')
);

-- Pattern matching in array elements
SELECT title
FROM posts
WHERE EXISTS (
    SELECT 1 FROM unnest(tags) tag 
    WHERE tag LIKE '%sql%'
);
```

## Array Functions and Operators

### Array Operators

```sql
-- Concatenation (||)
SELECT ARRAY[1, 2] || ARRAY[3, 4];
-- Result: {1,2,3,4}

SELECT ARRAY[1, 2] || 3;
-- Result: {1,2,3}

SELECT 1 || ARRAY[2, 3];
-- Result: {1,2,3}

-- Containment (@>, <@)
SELECT ARRAY[1,2,3] @> ARRAY[2,3];  -- true
SELECT ARRAY[2,3] <@ ARRAY[1,2,3];  -- true

-- Overlap (&&)
SELECT ARRAY[1,2,3] && ARRAY[3,4,5];  -- true (3 is common)
SELECT ARRAY[1,2] && ARRAY[3,4];      -- false

-- Comparison (=, <>, <, >, <=, >=)
SELECT ARRAY[1,2,3] = ARRAY[1,2,3];   -- true
SELECT ARRAY[1,2] < ARRAY[1,3];       -- true (lexicographic)

-- ANY and ALL
SELECT * FROM posts WHERE 'python' = ANY(tags);
SELECT * FROM posts WHERE 5 > ALL(scores);
```

### Array Manipulation Functions

```sql
-- array_append: Add to end
SELECT array_append(ARRAY[1,2,3], 4);
-- Result: {1,2,3,4}

-- array_prepend: Add to beginning
SELECT array_prepend(0, ARRAY[1,2,3]);
-- Result: {0,1,2,3}

-- array_cat: Concatenate arrays
SELECT array_cat(ARRAY[1,2], ARRAY[3,4]);
-- Result: {1,2,3,4}

-- array_remove: Remove all occurrences
SELECT array_remove(ARRAY[1,2,3,2,1], 2);
-- Result: {1,3,1}

-- array_replace: Replace all occurrences
SELECT array_replace(ARRAY[1,2,3,2,1], 2, 99);
-- Result: {1,99,3,99,1}

-- array_fill: Create array filled with value
SELECT array_fill(0, ARRAY[5]);
-- Result: {0,0,0,0,0}

SELECT array_fill(0, ARRAY[3,3]);
-- Result: {{0,0,0},{0,0,0},{0,0,0}}
```

### Array Aggregation and Analysis

```sql
-- array_length: Get dimension length
SELECT array_length(ARRAY[1,2,3], 1);  -- 3
SELECT array_length(ARRAY[[1,2],[3,4]], 1);  -- 2 (rows)
SELECT array_length(ARRAY[[1,2],[3,4]], 2);  -- 2 (columns)

-- array_dims: Get dimensions as text
SELECT array_dims(ARRAY[1,2,3]);
-- Result: [1:3]
SELECT array_dims(ARRAY[[1,2,3],[4,5,6]]);
-- Result: [1:2][1:3]

-- array_lower/array_upper: Get bounds
SELECT array_lower(ARRAY[1,2,3], 1);  -- 1
SELECT array_upper(ARRAY[1,2,3], 1);  -- 3

-- cardinality: Total number of elements
SELECT cardinality(ARRAY[1,2,3]);  -- 3
SELECT cardinality(ARRAY[[1,2],[3,4]]);  -- 4

-- unnest: Expand array to rows
SELECT unnest(ARRAY[1,2,3]);
-- Result:
-- 1
-- 2
-- 3

-- unnest with WITH ORDINALITY
SELECT * FROM unnest(ARRAY['a','b','c']) WITH ORDINALITY;
-- Result:
-- unnest | ordinality
-- a      | 1
-- b      | 2
-- c      | 3

-- Multiple arrays with unnest
SELECT * FROM unnest(
    ARRAY['a','b','c'],
    ARRAY[1,2,3]
) AS t(letter, number);
```

### Array Transformations

```sql
-- array_to_string: Convert to delimited string
SELECT array_to_string(ARRAY['a', 'b', 'c'], ',');
-- Result: 'a,b,c'

SELECT array_to_string(ARRAY['a', NULL, 'c'], ',', 'NULL');
-- Result: 'a,NULL,c'

-- string_to_array: Parse delimited string
SELECT string_to_array('one,two,three', ',');
-- Result: {one,two,three}

-- array_agg: Aggregate to array
SELECT category, array_agg(product_name)
FROM products
GROUP BY category;

-- Sort and deduplicate array
SELECT ARRAY(
    SELECT DISTINCT unnest(ARRAY[3,1,2,3,1])
    ORDER BY 1
);
-- Result: {1,2,3}
```

## Array Indexing

### GIN Indexes for Arrays

```sql
-- Create GIN index for containment queries
CREATE INDEX idx_posts_tags ON posts USING GIN(tags);

-- Queries that use the index:
-- Array contains (@>)
EXPLAIN SELECT * FROM posts WHERE tags @> ARRAY['postgresql'];
-- Array overlap (&&)
EXPLAIN SELECT * FROM posts WHERE tags && ARRAY['python', 'ruby'];

-- Create GIN index with specific operator class
CREATE INDEX idx_posts_tags_gin ON posts USING GIN(tags array_ops);
```

### B-tree Indexes

```sql
-- Index for equality
CREATE INDEX idx_posts_tags_btree ON posts (tags);

-- Useful for exact matches
SELECT * FROM posts WHERE tags = ARRAY['postgresql', 'database'];
```

### Partial Indexes

```sql
-- Index only non-empty arrays
CREATE INDEX idx_posts_nonempty_tags ON posts USING GIN(tags)
WHERE array_length(tags, 1) > 0;

-- Index specific array lengths
CREATE INDEX idx_posts_few_tags ON posts USING GIN(tags)
WHERE array_length(tags, 1) <= 5;
```

## Composite Types

### Creating Composite Types

```sql
-- Define composite type
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT
);

CREATE TYPE contact_info AS (
    email TEXT,
    phone TEXT,
    address address  -- Nested composite type
);

-- Use in table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    contact contact_info,
    billing_address address,
    shipping_address address
);
```

### Inserting Composite Data

```sql
-- ROW constructor
INSERT INTO customers (name, contact, billing_address) VALUES (
    'John Doe',
    ROW('john@example.com', '123-456-7890', ROW('123 Main St', 'NYC', 'NY', '10001', 'USA')),
    ROW('123 Main St', 'NYC', 'NY', '10001', 'USA')
);

-- Cast from string
INSERT INTO customers (name, billing_address) VALUES (
    'Jane Smith',
    '("456 Oak Ave", "LA", "CA", "90001", "USA")'::address
);

-- Using composite type constructor
INSERT INTO customers (name, billing_address) VALUES (
    'Bob Johnson',
    ROW('789 Pine Rd', 'Chicago', 'IL', '60601', 'USA')::address
);
```

## Using Composite Types

### Accessing Composite Fields

```sql
-- Dot notation (requires parentheses)
SELECT 
    name,
    (billing_address).street,
    (billing_address).city,
    (billing_address).state
FROM customers;

-- Without parentheses (table name ambiguity)
SELECT 
    name,
    (c.billing_address).street,
    (c.billing_address).city
FROM customers c;

-- Access nested composite
SELECT 
    name,
    (contact).email,
    ((contact).address).city
FROM customers;

-- Decompose composite type
SELECT 
    name,
    (billing_address).*
FROM customers;
-- Returns: name, street, city, state, zip_code, country
```

### Querying Composite Fields

```sql
-- Filter by composite field
SELECT * FROM customers
WHERE (billing_address).city = 'NYC';

-- Compare composite values
SELECT * FROM customers
WHERE billing_address = ROW('123 Main St', 'NYC', 'NY', '10001', 'USA')::address;

-- IS NULL checks
SELECT * FROM customers
WHERE (billing_address).city IS NULL;

-- IS DISTINCT FROM (NULL-safe comparison)
SELECT * FROM customers
WHERE (billing_address).city IS DISTINCT FROM 'NYC';
```

### Updating Composite Fields

```sql
-- Update entire composite
UPDATE customers
SET billing_address = ROW('999 New St', 'Boston', 'MA', '02101', 'USA')::address
WHERE name = 'John Doe';

-- Update single field (requires ROW constructor)
UPDATE customers
SET billing_address = ROW(
    (billing_address).street,
    'San Francisco',  -- Change city
    (billing_address).state,
    (billing_address).zip_code,
    (billing_address).country
)::address
WHERE name = 'Jane Smith';

-- PostgreSQL 14+: Update single field directly
UPDATE customers
SET billing_address.city = 'San Francisco'
WHERE name = 'Jane Smith';
```

### Composite Type Functions

```sql
-- ROW constructor
SELECT ROW(1, 'text', true);

-- Composite type to JSON
SELECT row_to_json(billing_address) FROM customers;

-- Create composite from JSON
SELECT * FROM json_populate_record(
    NULL::address,
    '{"street": "123 Main St", "city": "NYC", "state": "NY", "zip_code": "10001", "country": "USA"}'
);

-- Compare composite types
SELECT 
    name,
    billing_address = shipping_address as addresses_match
FROM customers;
```

## Nested Structures

### Arrays of Composite Types

```sql
-- Define types
CREATE TYPE phone_number AS (
    type TEXT,
    number TEXT
);

CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name TEXT,
    phones phone_number[]
);

-- Insert array of composite types
INSERT INTO persons (name, phones) VALUES (
    'Alice',
    ARRAY[
        ROW('home', '555-1234')::phone_number,
        ROW('work', '555-5678')::phone_number,
        ROW('mobile', '555-9012')::phone_number
    ]
);

-- Query array of composites
SELECT 
    name,
    (phones[1]).type as first_phone_type,
    (phones[1]).number as first_phone_number
FROM persons;

-- Unnest array of composites
SELECT 
    name,
    (phone).type,
    (phone).number
FROM persons, unnest(phones) AS phone;

-- Filter by composite field in array
SELECT name
FROM persons
WHERE EXISTS (
    SELECT 1 FROM unnest(phones) p
    WHERE (p).type = 'mobile'
);
```

### Composite Types with Arrays

```sql
-- Composite type containing arrays
CREATE TYPE order_summary AS (
    order_id INTEGER,
    item_ids INTEGER[],
    item_names TEXT[],
    total NUMERIC
);

CREATE TABLE order_history (
    customer_id INTEGER,
    orders order_summary[]
);

-- Insert data
INSERT INTO order_history VALUES (
    1,
    ARRAY[
        ROW(101, ARRAY[1,2,3], ARRAY['Widget','Gadget','Thing'], 99.99)::order_summary,
        ROW(102, ARRAY[4,5], ARRAY['Stuff','Item'], 49.99)::order_summary
    ]
);

-- Query nested structure
SELECT 
    customer_id,
    (orders[1]).order_id,
    (orders[1]).item_names[1] as first_item
FROM order_history;
```

### Table Types

```sql
-- Use existing table as type
CREATE TABLE sample_table (
    id INTEGER,
    name TEXT,
    value NUMERIC
);

-- Use table as composite type
CREATE TABLE container (
    id SERIAL PRIMARY KEY,
    data sample_table
);

-- Insert using table type
INSERT INTO container (data) VALUES (
    ROW(1, 'test', 123.45)::sample_table
);

-- Query
SELECT (data).id, (data).name FROM container;
```

## Best Practices

### 1. Arrays vs Normalized Tables

```sql
-- Use arrays for:
-- - Fixed small sets (tags, categories)
-- - Data rarely queried independently
-- - No referential integrity needed

CREATE TABLE posts_with_arrays (
    id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[]  -- Good: simple tags, no foreign keys
);

-- Use normalized tables for:
-- - Large datasets
-- - Complex queries on related data
-- - Foreign key constraints needed

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);  -- Better for complex relationships
```

### 2. Index Arrays Properly

```sql
-- GIN index for containment queries
CREATE INDEX idx_tags_gin ON posts USING GIN(tags);

-- Expression index for array length
CREATE INDEX idx_tags_length ON posts (array_length(tags, 1));

-- Partial index for non-empty arrays
CREATE INDEX idx_nonempty_tags ON posts USING GIN(tags)
WHERE array_length(tags, 1) > 0;
```

### 3. Composite Types for Related Data

```sql
-- Good: Logically grouped data
CREATE TYPE money_amount AS (
    amount NUMERIC(10,2),
    currency TEXT
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    total money_amount,
    tax money_amount,
    subtotal money_amount
);

-- Alternative: When you need constraints/indexes
CREATE TABLE transactions_normalized (
    id SERIAL PRIMARY KEY,
    total_amount NUMERIC(10,2),
    total_currency TEXT,
    tax_amount NUMERIC(10,2),
    tax_currency TEXT,
    CHECK (total_currency IN ('USD', 'EUR', 'GBP'))
);
```

### 4. Avoid Deep Nesting

```sql
-- Avoid: Too complex
CREATE TYPE level3 AS (data TEXT);
CREATE TYPE level2 AS (items level3[]);
CREATE TYPE level1 AS (groups level2[]);

-- Better: Flatten or use JSONB
CREATE TABLE better_design (
    id SERIAL PRIMARY KEY,
    data JSONB  -- More flexible for nested structures
);
```

### 5. NULL Handling

```sql
-- Check for NULL vs empty array
SELECT 
    title,
    CASE 
        WHEN tags IS NULL THEN 'null'
        WHEN array_length(tags, 1) IS NULL THEN 'empty'
        ELSE 'has values'
    END as tag_status
FROM posts;

-- Use COALESCE for defaults
SELECT 
    title,
    coalesce(array_length(tags, 1), 0) as tag_count
FROM posts;
```

## Summary

PostgreSQL arrays and composite types provide:
- **Arrays**: Store multiple values in single column with efficient querying
- **Composite types**: Create custom structured data types
- **Operators**: @>, <@, && for containment and overlap
- **Functions**: array_agg, unnest, array_append for manipulation
- **Indexing**: GIN indexes for efficient array queries
- **Nesting**: Combine arrays and composites for complex structures

Use arrays for simple collections and composite types for logically grouped data.

## Next Steps

- Learn about [JSON and JSONB](./26-json-and-jsonb.md)
- Explore [Custom Types and Domains](./29-custom-types-and-domains.md)
- Study [Index Optimization](./22-index-optimization.md)
- Practice [Advanced Data Types](./04-data-types.md)
