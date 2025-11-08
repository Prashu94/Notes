# PostgreSQL Data Types

## Overview

PostgreSQL supports a rich set of native data types, and allows users to create custom types. Choosing the right data type is crucial for:
- Data integrity
- Storage efficiency
- Query performance
- Application correctness

## Numeric Types

### 1. Integer Types

| Type | Storage | Range | Use Case |
|------|---------|-------|----------|
| `SMALLINT` | 2 bytes | -32,768 to 32,767 | Small numbers |
| `INTEGER` (INT) | 4 bytes | -2,147,483,648 to 2,147,483,647 | Common integers |
| `BIGINT` | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 | Large numbers |

```sql
-- Examples
CREATE TABLE numeric_examples (
    small_num SMALLINT,
    medium_num INTEGER,
    large_num BIGINT
);

INSERT INTO numeric_examples VALUES (100, 1000000, 9999999999999);

-- Auto-increment (SERIAL types)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,          -- INTEGER with auto-increment
    user_id BIGSERIAL,              -- BIGINT with auto-increment
    code SMALLSERIAL                -- SMALLINT with auto-increment
);
```

### 2. Arbitrary Precision

| Type | Storage | Range | Use Case |
|------|---------|-------|----------|
| `DECIMAL(p, s)` | Variable | Up to 131072 digits | Exact calculations |
| `NUMERIC(p, s)` | Variable | Up to 131072 digits | Financial data |

- `p` = precision (total digits)
- `s` = scale (digits after decimal)

```sql
-- Examples
CREATE TABLE financial_data (
    product_price DECIMAL(10, 2),      -- 99999999.99
    tax_rate NUMERIC(5, 4),            -- 0.0825
    total DECIMAL,                      -- No limit specified
    amount NUMERIC(12, 3)               -- 999999999.999
);

INSERT INTO financial_data VALUES (199.99, 0.0825, 1234567890.12, 999999.999);

-- Calculations maintain precision
SELECT 
    product_price * (1 + tax_rate) AS total_with_tax
FROM financial_data;
```

### 3. Floating-Point Types

| Type | Storage | Range | Precision |
|------|---------|-------|-----------|
| `REAL` | 4 bytes | 6 decimal digits | Variable |
| `DOUBLE PRECISION` | 8 bytes | 15 decimal digits | Variable |

```sql
-- Examples
CREATE TABLE scientific_data (
    measurement REAL,
    precise_value DOUBLE PRECISION
);

-- Warning: Floating-point arithmetic can be imprecise
SELECT 0.1 + 0.2;  -- Result: 0.30000000000000004

-- Use NUMERIC for exact calculations
SELECT 0.1::NUMERIC + 0.2::NUMERIC;  -- Result: 0.3
```

### 4. Serial Types (Auto-increment)

```sql
-- SERIAL is shorthand for:
-- 1. Create sequence
-- 2. Create integer column
-- 3. Set default to nextval(sequence)

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- Equivalent to:
CREATE SEQUENCE products_id_seq;
CREATE TABLE products (
    id INTEGER PRIMARY KEY DEFAULT nextval('products_id_seq'),
    name VARCHAR(100)
);

-- Insert without specifying ID
INSERT INTO products (name) VALUES ('Product A');

-- Get last inserted ID
SELECT lastval();
SELECT currval('products_id_seq');
```

## Character Types

### String Types

| Type | Description | Storage |
|------|-------------|---------|
| `CHAR(n)` | Fixed-length, blank-padded | n bytes |
| `VARCHAR(n)` | Variable-length with limit | Actual length + 1 byte |
| `TEXT` | Variable unlimited length | Actual length + 1 byte |

```sql
CREATE TABLE text_examples (
    code CHAR(5),               -- Always 5 characters (padded)
    name VARCHAR(100),          -- Up to 100 characters
    description TEXT            -- Unlimited length
);

INSERT INTO text_examples VALUES 
    ('A1', 'Short', 'This is a very long description that can be as long as needed without any limit');

-- CHAR is padded with spaces
SELECT 
    code,
    length(code) AS char_length,      -- 5
    char_length(code) AS actual_chars -- 2
FROM text_examples
WHERE code = 'A1';

-- VARCHAR and TEXT are similar
-- TEXT is generally preferred (no overhead difference)
```

### Best Practices

```sql
-- DON'T: Use arbitrary limits
CREATE TABLE bad_example (
    email VARCHAR(255)  -- Why 255?
);

-- DO: Use TEXT unless there's a business rule
CREATE TABLE good_example (
    email TEXT CHECK (char_length(email) <= 320),  -- RFC 5321 limit
    username TEXT CHECK (char_length(username) BETWEEN 3 AND 30)
);

-- DON'T: Use CHAR unless fixed length is required
CREATE TABLE bad_codes (
    country_code CHAR(50)  -- Wastes space
);

-- DO: Use CHAR for truly fixed-length data
CREATE TABLE good_codes (
    country_code CHAR(2),    -- ISO 3166-1 alpha-2
    currency_code CHAR(3)    -- ISO 4217
);
```

## Date/Time Types

| Type | Storage | Range | Resolution |
|------|---------|-------|------------|
| `DATE` | 4 bytes | 4713 BC to 5874897 AD | 1 day |
| `TIME` | 8 bytes | 00:00:00 to 24:00:00 | 1 microsecond |
| `TIME WITH TIME ZONE` | 12 bytes | Same as TIME | 1 microsecond |
| `TIMESTAMP` | 8 bytes | 4713 BC to 294276 AD | 1 microsecond |
| `TIMESTAMP WITH TIME ZONE` | 8 bytes | Same as TIMESTAMP | 1 microsecond |
| `INTERVAL` | 16 bytes | -178000000 years to 178000000 years | 1 microsecond |

```sql
CREATE TABLE event_schedule (
    event_date DATE,
    event_time TIME,
    event_datetime TIMESTAMP,
    event_datetime_tz TIMESTAMPTZ,  -- Recommended for timestamps
    duration INTERVAL
);

-- Insert examples
INSERT INTO event_schedule VALUES (
    '2024-12-25',                           -- DATE
    '14:30:00',                             -- TIME
    '2024-12-25 14:30:00',                  -- TIMESTAMP
    '2024-12-25 14:30:00+00',               -- TIMESTAMPTZ
    '2 hours 30 minutes'                    -- INTERVAL
);

-- Current date/time functions
SELECT 
    CURRENT_DATE,                    -- 2024-12-25
    CURRENT_TIME,                    -- 14:30:00.123456+00
    CURRENT_TIMESTAMP,               -- 2024-12-25 14:30:00.123456+00
    NOW(),                           -- Same as CURRENT_TIMESTAMP
    LOCALTIMESTAMP,                  -- Without timezone
    CLOCK_TIMESTAMP();               -- Changes during statement execution

-- Date arithmetic
SELECT 
    CURRENT_DATE + INTERVAL '1 day',          -- Tomorrow
    CURRENT_DATE - INTERVAL '1 week',         -- Last week
    CURRENT_TIMESTAMP + INTERVAL '3 hours',   -- 3 hours from now
    AGE(TIMESTAMP '2024-01-01', TIMESTAMP '2023-01-01');  -- 1 year

-- Extract parts
SELECT 
    EXTRACT(YEAR FROM CURRENT_DATE),
    EXTRACT(MONTH FROM CURRENT_DATE),
    EXTRACT(DAY FROM CURRENT_DATE),
    EXTRACT(HOUR FROM CURRENT_TIMESTAMP),
    DATE_PART('quarter', CURRENT_DATE);

-- Formatting
SELECT 
    TO_CHAR(CURRENT_DATE, 'YYYY-MM-DD'),
    TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'),
    TO_CHAR(CURRENT_DATE, 'Day, DD Month YYYY');
```

### Timezone Best Practices

```sql
-- ALWAYS use TIMESTAMPTZ for timestamps
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),     -- Good
    scheduled_at TIMESTAMP                     -- Bad (no timezone)
);

-- Set timezone for session
SET timezone = 'America/New_York';
SELECT NOW();

SET timezone = 'UTC';
SELECT NOW();

-- Convert between timezones
SELECT 
    NOW() AT TIME ZONE 'America/New_York',
    NOW() AT TIME ZONE 'Asia/Tokyo',
    NOW() AT TIME ZONE 'Europe/London';
```

## Boolean Type

```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    feature_enabled BOOLEAN,
    is_active BOOLEAN DEFAULT TRUE
);

-- Boolean values
INSERT INTO settings (feature_enabled) VALUES 
    (TRUE),
    (FALSE),
    ('yes'),     -- Converted to TRUE
    ('no'),      -- Converted to FALSE
    ('1'),       -- Converted to TRUE
    ('0'),       -- Converted to FALSE
    ('t'),       -- Converted to TRUE
    ('f');       -- Converted to FALSE

-- Boolean operations
SELECT * FROM settings WHERE feature_enabled;              -- TRUE rows
SELECT * FROM settings WHERE NOT feature_enabled;          -- FALSE rows
SELECT * FROM settings WHERE feature_enabled IS NULL;      -- NULL rows
SELECT * FROM settings WHERE feature_enabled IS NOT TRUE;  -- FALSE and NULL rows
```

## Binary Data Type

```sql
-- BYTEA: Binary string
CREATE TABLE file_storage (
    id SERIAL PRIMARY KEY,
    filename TEXT,
    content BYTEA,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert binary data
INSERT INTO file_storage (filename, content) VALUES 
    ('test.txt', '\x48656c6c6f'),                    -- Hex format
    ('data.bin', '\000\001\002\003'::bytea);         -- Escape format

-- Retrieve size
SELECT 
    filename,
    octet_length(content) AS size_bytes,
    pg_size_pretty(octet_length(content)::bigint) AS size_human
FROM file_storage;
```

## UUID Type

```sql
-- Universally Unique Identifier
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE distributed_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT NOT NULL
);

-- Insert with auto-generated UUID
INSERT INTO distributed_users (username) VALUES ('alice');

-- Insert with explicit UUID
INSERT INTO distributed_users VALUES 
    ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'bob');

-- Generate UUIDs
SELECT 
    uuid_generate_v1(),    -- Time-based
    uuid_generate_v4(),    -- Random
    gen_random_uuid();     -- Random (built-in, no extension needed)
```

## JSON Types

### JSON vs JSONB

| Feature | JSON | JSONB |
|---------|------|-------|
| Storage | Text format | Decomposed binary |
| Input Speed | Faster | Slower (processing) |
| Query Speed | Slower | Much faster |
| Indexing | Limited | Full support |
| Whitespace | Preserved | Not preserved |
| Key Order | Preserved | Not preserved |
| Duplicate Keys | Allowed | Last value wins |
| **Recommendation** | **Rarely use** | **Use this** |

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    attributes JSONB,         -- Use JSONB
    metadata JSON             -- Rarely needed
);

-- Insert JSON data
INSERT INTO products (name, attributes) VALUES 
    ('Laptop', '{"brand": "Dell", "ram": "16GB", "storage": {"type": "SSD", "size": "512GB"}}'),
    ('Phone', '{"brand": "Apple", "model": "iPhone 14", "colors": ["black", "white", "blue"]}');

-- Query JSON data
SELECT 
    name,
    attributes->>'brand' AS brand,                    -- Text extraction
    attributes->'storage'->>'size' AS storage_size,   -- Nested extraction
    attributes->'colors'->0 AS first_color            -- Array access
FROM products;

-- JSON operators
SELECT 
    attributes ? 'brand',                             -- Has key?
    attributes ?& ARRAY['brand', 'model'],            -- Has all keys?
    attributes ?| ARRAY['brand', 'price'],            -- Has any key?
    attributes @> '{"brand": "Dell"}'                 -- Contains?
FROM products;

-- Indexing JSONB
CREATE INDEX idx_attributes ON products USING GIN (attributes);

-- Query with index
SELECT * FROM products WHERE attributes @> '{"brand": "Dell"}';

-- JSON functions
SELECT 
    jsonb_array_length(attributes->'colors') AS color_count,
    jsonb_object_keys(attributes) AS keys,
    jsonb_pretty(attributes) AS formatted
FROM products;
```

## Array Types

```sql
-- Any data type can be an array
CREATE TABLE array_examples (
    id SERIAL PRIMARY KEY,
    tags TEXT[],                          -- Text array
    scores INTEGER[],                     -- Integer array
    matrix INTEGER[][],                   -- Multi-dimensional array
    fixed_array INTEGER[3]                -- Fixed size (not enforced!)
);

-- Insert arrays
INSERT INTO array_examples (tags, scores, matrix) VALUES 
    (
        ARRAY['postgresql', 'database', 'sql'],
        ARRAY[95, 87, 92],
        ARRAY[[1,2,3], [4,5,6]]
    ),
    (
        '{"python", "programming"}',      -- Alternative syntax
        '{85, 90, 88}',
        '{{7,8,9}, {10,11,12}}'
    );

-- Array operations
SELECT 
    tags,
    tags[1],                              -- First element (1-indexed!)
    tags[1:2],                            -- Slice
    array_length(tags, 1),                -- Length
    cardinality(tags),                    -- Total elements
    array_append(tags, 'new'),            -- Append
    array_prepend('first', tags),         -- Prepend
    array_cat(tags, ARRAY['more']),       -- Concatenate
    'postgresql' = ANY(tags),             -- Contains?
    tags @> ARRAY['sql']                  -- Contains array?
FROM array_examples;

-- Array aggregation
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    product_id INTEGER
);

INSERT INTO orders (product_id) VALUES (1), (2), (1), (3), (2), (1);

SELECT array_agg(product_id) AS all_products,
       array_agg(DISTINCT product_id) AS unique_products
FROM orders;

-- Unnest array (array to rows)
SELECT unnest(ARRAY['a', 'b', 'c']) AS element;

-- Create array from rows
SELECT array_agg(order_id) FROM orders WHERE product_id = 1;
```

## Range Types

```sql
-- Built-in range types
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    room_number INTEGER,
    during TSTZRANGE,                     -- Timestamp range with timezone
    price_range NUMRANGE                  -- Numeric range
);

-- Insert ranges
INSERT INTO reservations VALUES 
    (1, 101, '[2024-12-20 14:00, 2024-12-22 11:00)', numrange(100, 200)),
    (2, 102, '[2024-12-21 15:00, 2024-12-23 12:00)', numrange(150, 250));

-- Range operators
SELECT 
    during,
    lower(during) AS check_in,            -- Lower bound
    upper(during) AS check_out,           -- Upper bound
    isempty(during) AS is_empty,          -- Empty range?
    lower_inc(during) AS includes_lower,  -- Includes lower bound?
    upper_inc(during) AS includes_upper   -- Includes upper bound?
FROM reservations;

-- Range operations
SELECT 
    during @> TIMESTAMPTZ '2024-12-21 10:00+00',  -- Contains element?
    during && tstzrange(
        '2024-12-21 00:00+00', 
        '2024-12-22 00:00+00'
    ) AS overlaps,                                  -- Overlaps?
    during * tstzrange(
        '2024-12-21 00:00+00', 
        '2024-12-23 00:00+00'
    ) AS intersection                               -- Intersection
FROM reservations;

-- Prevent overlapping bookings
CREATE TABLE room_bookings (
    id SERIAL PRIMARY KEY,
    room_number INTEGER,
    during TSTZRANGE,
    EXCLUDE USING GIST (
        room_number WITH =,
        during WITH &&
    )
);

-- This will fail if overlapping
INSERT INTO room_bookings VALUES 
    (1, 101, '[2024-12-20, 2024-12-22)'),
    (2, 101, '[2024-12-21, 2024-12-23)');  -- ERROR: conflicts with existing key
```

## Composite Types

```sql
-- Define custom type
CREATE TYPE address AS (
    street TEXT,
    city TEXT,
    state CHAR(2),
    zip_code VARCHAR(10)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    home_address address,
    work_address address
);

-- Insert composite values
INSERT INTO customers VALUES (
    1,
    'John Doe',
    ROW('123 Main St', 'New York', 'NY', '10001')::address,
    ROW('456 Work Ave', 'New York', 'NY', '10002')::address
);

-- Access composite fields
SELECT 
    name,
    (home_address).street,
    (home_address).city,
    (home_address).state
FROM customers;

-- Update composite field
UPDATE customers 
SET home_address.city = 'Brooklyn'
WHERE id = 1;
```

## Enumerated Types

```sql
-- Create enum type
CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name TEXT,
    current_mood mood
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    status order_status DEFAULT 'pending'
);

-- Insert enum values
INSERT INTO person VALUES (1, 'Alice', 'happy');
INSERT INTO orders (status) VALUES ('processing');

-- Enum ordering
SELECT * FROM person WHERE current_mood > 'sad';  -- 'ok' and 'happy'

-- List enum values
SELECT unnest(enum_range(NULL::mood));

-- Add enum value
ALTER TYPE mood ADD VALUE 'excited';
ALTER TYPE mood ADD VALUE 'anxious' BEFORE 'ok';
ALTER TYPE mood ADD VALUE 'ecstatic' AFTER 'happy';
```

## Geometric Types

```sql
CREATE TABLE geometric_examples (
    location POINT,                  -- (x, y)
    area BOX,                        -- ((x1,y1), (x2,y2))
    path PATH,                       -- ((x1,y1), ...)
    polygon POLYGON,                 -- ((x1,y1), ...)
    circle CIRCLE,                   -- <(x,y), r>
    line LINE,                       -- {A, B, C}
    line_segment LSEG               -- ((x1,y1), (x2,y2))
);

-- Insert geometric data
INSERT INTO geometric_examples (location, area, circle) VALUES 
    (POINT(1, 2), BOX(POINT(0,0), POINT(10,10)), CIRCLE(POINT(5,5), 3));

-- Geometric operations
SELECT 
    location,
    location <-> POINT(0, 0) AS distance_from_origin,  -- Distance
    area @> POINT(5, 5) AS contains_point,             -- Contains?
    circle && BOX(POINT(0,0), POINT(10,10)) AS overlaps -- Overlap?
FROM geometric_examples;
```

## Network Address Types

```sql
CREATE TABLE network_logs (
    id SERIAL PRIMARY KEY,
    client_ip INET,              -- IPv4 or IPv6 address
    network CIDR,                -- IPv4 or IPv6 network
    mac_address MACADDR          -- MAC address
);

-- Insert network data
INSERT INTO network_logs VALUES 
    (1, '192.168.1.100', '192.168.1.0/24', '08:00:2b:01:02:03'),
    (2, '2001:db8::1', '2001:db8::/32', '08-00-2b-01-02-03');

-- Network operations
SELECT 
    client_ip,
    host(client_ip) AS ip_address,
    masklen(network) AS subnet_mask,
    broadcast(network) AS broadcast_addr,
    client_ip << network AS is_in_network
FROM network_logs;
```

## Full-Text Search Types

```sql
-- TSVector: Processed document for searching
-- TSQuery: Search query

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    body TEXT,
    search_vector TSVECTOR
);

-- Populate with data
INSERT INTO documents (title, body) VALUES 
    ('PostgreSQL Tutorial', 'Learn PostgreSQL database management'),
    ('Advanced SQL', 'Master complex SQL queries');

-- Create tsvector
UPDATE documents 
SET search_vector = to_tsvector('english', title || ' ' || body);

-- Search
SELECT * FROM documents 
WHERE search_vector @@ to_tsquery('english', 'postgresql & database');

-- Create GIN index for fast searching
CREATE INDEX idx_search ON documents USING GIN (search_vector);
```

## Type Conversion

```sql
-- Explicit casting
SELECT 
    '123'::INTEGER,                      -- String to integer
    123::TEXT,                           -- Integer to string
    '2024-01-01'::DATE,                  -- String to date
    CAST('123.45' AS NUMERIC(10,2)),     -- CAST function
    '{"key": "value"}'::JSONB;           -- String to JSONB

-- Implicit conversion (when safe)
SELECT 123 + 456;                        -- Both integers
SELECT 123 + 456.78;                     -- Integer promoted to numeric

-- Date/time conversion
SELECT 
    TO_DATE('20240101', 'YYYYMMDD'),
    TO_TIMESTAMP('2024-01-01 12:30:00', 'YYYY-MM-DD HH24:MI:SS'),
    TO_CHAR(NOW(), 'YYYY-MM-DD');
```

## Summary Table

| Category | Types | Use Case |
|----------|-------|----------|
| **Numeric** | SMALLINT, INTEGER, BIGINT, DECIMAL, NUMERIC, REAL, DOUBLE PRECISION | Numbers, calculations |
| **Character** | CHAR, VARCHAR, TEXT | Strings, text data |
| **Date/Time** | DATE, TIME, TIMESTAMP, TIMESTAMPTZ, INTERVAL | Dates, times, durations |
| **Boolean** | BOOLEAN | True/false values |
| **Binary** | BYTEA | Binary data, files |
| **UUID** | UUID | Unique identifiers |
| **JSON** | JSON, JSONB | Semi-structured data |
| **Array** | Any type[] | Lists, collections |
| **Range** | INT4RANGE, TSRANGE, TSTZRANGE, etc. | Value ranges |
| **Composite** | Custom types | Structured data |
| **Enum** | Custom enums | Fixed set of values |
| **Geometric** | POINT, LINE, POLYGON, etc. | Spatial data |
| **Network** | INET, CIDR, MACADDR | IP addresses, networks |
| **Text Search** | TSVECTOR, TSQUERY | Full-text search |

## Next Steps

- [Basic SQL Operations](05-basic-sql-operations.md)
- [Constraints and Keys](08-constraints-and-keys.md)
- [JSON and JSONB](26-json-and-jsonb.md)
