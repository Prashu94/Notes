# Constraints and Keys

## Overview

Constraints enforce rules on data in tables to ensure data integrity, accuracy, and reliability. PostgreSQL provides several types of constraints to maintain database consistency.

## Primary Keys

### Definition

A **primary key** uniquely identifies each row in a table. It combines:
- UNIQUE constraint
- NOT NULL constraint

### Creating Primary Keys

```sql
-- During table creation
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

-- Named primary key
CREATE TABLE products (
    product_id INTEGER,
    CONSTRAINT pk_products PRIMARY KEY (product_id)
);

-- Composite primary key (multiple columns)
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);

-- Adding primary key to existing table
ALTER TABLE customers 
ADD PRIMARY KEY (customer_id);

-- Named constraint
ALTER TABLE customers 
ADD CONSTRAINT pk_customers PRIMARY KEY (customer_id);
```

### Primary Key Characteristics

```sql
-- Only one primary key per table
CREATE TABLE example (
    id1 SERIAL PRIMARY KEY,
    id2 SERIAL PRIMARY KEY  -- ERROR: multiple primary keys
);

-- NULL values not allowed
INSERT INTO users (user_id, username) 
VALUES (NULL, 'john');  -- ERROR: null value in column violates not-null

-- Duplicate values not allowed
INSERT INTO users (user_id, username) VALUES (1, 'alice');
INSERT INTO users (user_id, username) VALUES (1, 'bob');  -- ERROR: duplicate key

-- Viewing primary key
\d users
-- Or
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'users' AND constraint_type = 'PRIMARY KEY';
```

## Foreign Keys

### Definition

A **foreign key** creates a link between two tables, ensuring referential integrity.

### Creating Foreign Keys

```sql
-- Basic foreign key
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    total DECIMAL(10, 2)
);

-- Named foreign key with table-level constraint
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    CONSTRAINT fk_order FOREIGN KEY (order_id) 
        REFERENCES orders(order_id),
    CONSTRAINT fk_product FOREIGN KEY (product_id) 
        REFERENCES products(product_id)
);

-- Multiple column foreign key
CREATE TABLE inventory (
    warehouse_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (warehouse_id, product_id) 
        REFERENCES warehouse_products(warehouse_id, product_id)
);

-- Adding foreign key to existing table
ALTER TABLE orders 
ADD CONSTRAINT fk_user 
    FOREIGN KEY (user_id) 
    REFERENCES users(user_id);
```

### Referential Actions

```sql
-- ON DELETE CASCADE: Delete child rows when parent is deleted
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    content TEXT
);

-- ON DELETE SET NULL: Set foreign key to NULL
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    total DECIMAL(10, 2)
);

-- ON DELETE SET DEFAULT: Set to default value
CREATE TABLE assignments (
    assignment_id SERIAL PRIMARY KEY,
    user_id INTEGER DEFAULT 1 REFERENCES users(user_id) ON DELETE SET DEFAULT
);

-- ON DELETE RESTRICT (default): Prevent deletion if referenced
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    dept_id INTEGER REFERENCES departments(dept_id) ON DELETE RESTRICT
);

-- ON UPDATE CASCADE: Update child rows when parent is updated
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    total DECIMAL(10, 2)
);

-- NO ACTION: Similar to RESTRICT but can be deferred
CREATE TABLE items (
    item_id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id) 
        ON DELETE NO ACTION
        DEFERRABLE INITIALLY DEFERRED
);
```

### Foreign Key Examples

```sql
-- Example: Blog system
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES authors(author_id) ON DELETE CASCADE,
    title TEXT,
    content TEXT
);

CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    content TEXT
);

-- Insert data
INSERT INTO authors (name) VALUES ('John Doe');
INSERT INTO posts (author_id, title, content) 
VALUES (1, 'First Post', 'Content here');

-- This fails without the author
INSERT INTO posts (author_id, title, content) 
VALUES (999, 'Invalid', 'No such author');  -- ERROR: foreign key violation

-- Delete cascade in action
DELETE FROM authors WHERE author_id = 1;  -- Also deletes related posts and comments
```

## Unique Constraints

### Creating Unique Constraints

```sql
-- Column-level unique
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE
);

-- Table-level unique
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50),
    name VARCHAR(100),
    UNIQUE (sku)
);

-- Named unique constraint
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    phone VARCHAR(20),
    CONSTRAINT unique_email UNIQUE (email),
    CONSTRAINT unique_phone UNIQUE (phone)
);

-- Composite unique constraint
CREATE TABLE employee_projects (
    employee_id INTEGER,
    project_id INTEGER,
    role VARCHAR(50),
    UNIQUE (employee_id, project_id)  -- Each employee once per project
);

-- Adding to existing table
ALTER TABLE products 
ADD CONSTRAINT unique_sku UNIQUE (sku);
```

### Unique with NULL

```sql
-- UNIQUE allows multiple NULL values
CREATE TABLE contacts (
    contact_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20) UNIQUE
);

INSERT INTO contacts (email, phone) VALUES ('a@b.com', '123');
INSERT INTO contacts (email, phone) VALUES (NULL, '456');      -- OK
INSERT INTO contacts (email, phone) VALUES (NULL, NULL);       -- OK
INSERT INTO contacts (email, phone) VALUES (NULL, NULL);       -- OK
INSERT INTO contacts (email, phone) VALUES ('a@b.com', '789'); -- ERROR: duplicate email

-- To disallow NULL, combine with NOT NULL
CREATE TABLE strict_contacts (
    contact_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);
```

### Partial Unique Indexes

```sql
-- Unique only where condition is true
CREATE UNIQUE INDEX unique_active_email 
ON users (email) 
WHERE is_active = TRUE;

-- Now you can have duplicate emails for inactive users
INSERT INTO users (email, is_active) VALUES ('test@example.com', TRUE);
INSERT INTO users (email, is_active) VALUES ('test@example.com', FALSE);  -- OK
INSERT INTO users (email, is_active) VALUES ('test@example.com', TRUE);   -- ERROR
```

## Check Constraints

### Creating Check Constraints

```sql
-- Column-level check
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10, 2) CHECK (price > 0),
    stock_quantity INTEGER CHECK (stock_quantity >= 0)
);

-- Table-level check
CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    salary NUMERIC(10, 2),
    bonus NUMERIC(10, 2),
    CHECK (salary > 0),
    CHECK (bonus >= 0),
    CHECK (bonus <= salary * 0.5)  -- Bonus max 50% of salary
);

-- Named check constraint
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    order_date DATE,
    ship_date DATE,
    status VARCHAR(20),
    CONSTRAINT check_dates CHECK (ship_date >= order_date),
    CONSTRAINT check_status CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled'))
);

-- Adding to existing table
ALTER TABLE products 
ADD CONSTRAINT check_price_positive CHECK (price > 0);

-- Complex check
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    event_type VARCHAR(20),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    max_attendees INTEGER,
    CONSTRAINT check_time CHECK (end_time > start_time),
    CONSTRAINT check_duration CHECK (
        event_type = 'short' AND end_time - start_time <= INTERVAL '2 hours'
        OR event_type = 'long'
    ),
    CONSTRAINT check_attendees CHECK (
        max_attendees > 0 AND max_attendees <= 1000
    )
);
```

### Check Constraint Examples

```sql
-- Email validation
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}$'),
    age INTEGER CHECK (age >= 18 AND age <= 120)
);

-- Discount validation
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2),
    discount_percent NUMERIC(5, 2),
    CONSTRAINT check_discount CHECK (
        discount_percent >= 0 AND 
        discount_percent <= 100 AND
        (price * (1 - discount_percent / 100)) >= 0.01
    )
);

-- Date range validation
CREATE TABLE promotions (
    promo_id SERIAL PRIMARY KEY,
    start_date DATE,
    end_date DATE,
    CONSTRAINT check_promo_dates CHECK (
        end_date > start_date AND
        end_date - start_date <= 90  -- Max 90 days
    )
);
```

### Limitations of Check Constraints

```sql
-- Cannot reference other rows or tables
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    total NUMERIC(10, 2),
    CHECK (total <= (SELECT credit_limit FROM users WHERE user_id = orders.user_id))
    -- ERROR: cannot use subquery in check constraint
);

-- Use triggers instead for cross-row/table checks
```

## Not Null Constraints

```sql
-- Column-level NOT NULL
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20)  -- NULL allowed
);

-- Adding NOT NULL to existing column
ALTER TABLE users 
ALTER COLUMN email SET NOT NULL;

-- Removing NOT NULL
ALTER TABLE users 
ALTER COLUMN phone DROP NOT NULL;

-- Multiple NOT NULL columns
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT  -- Optional
);
```

## Default Constraints

```sql
-- Column default values
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'pending',
    login_count INTEGER DEFAULT 0
);

-- Adding default to existing column
ALTER TABLE users 
ALTER COLUMN status SET DEFAULT 'active';

-- Removing default
ALTER TABLE users 
ALTER COLUMN status DROP DEFAULT;

-- Using expressions as defaults
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    log_date DATE DEFAULT CURRENT_DATE,
    log_time TIME DEFAULT CURRENT_TIME,
    log_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT DEFAULT gen_random_uuid()::TEXT
);

-- Inserting with defaults
INSERT INTO users (username) VALUES ('john');  -- Uses all defaults
INSERT INTO users (username, is_active) VALUES ('jane', FALSE);  -- Overrides default
INSERT INTO users (username, created_at) VALUES ('bob', DEFAULT);  -- Explicit default
```

## Exclusion Constraints

### Overview

Exclusion constraints ensure that no two rows satisfy a given condition. Commonly used with ranges to prevent overlaps.

```sql
-- Requires btree_gist extension
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Prevent overlapping room reservations
CREATE TABLE room_bookings (
    booking_id SERIAL PRIMARY KEY,
    room_number INTEGER,
    during TSTZRANGE,
    EXCLUDE USING GIST (
        room_number WITH =,
        during WITH &&
    )
);

-- Try to insert overlapping bookings
INSERT INTO room_bookings VALUES 
    (1, 101, '[2024-12-20 14:00, 2024-12-20 16:00)');

INSERT INTO room_bookings VALUES 
    (2, 101, '[2024-12-20 15:00, 2024-12-20 17:00)');  
-- ERROR: conflicting key value violates exclusion constraint

-- Non-overlapping booking works
INSERT INTO room_bookings VALUES 
    (2, 101, '[2024-12-20 16:00, 2024-12-20 18:00)');  -- OK

-- Different room works
INSERT INTO room_bookings VALUES 
    (3, 102, '[2024-12-20 15:00, 2024-12-20 17:00)');  -- OK
```

### More Exclusion Examples

```sql
-- Employee can't work two shifts simultaneously
CREATE TABLE shifts (
    shift_id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    shift_time TSTZRANGE,
    EXCLUDE USING GIST (
        employee_id WITH =,
        shift_time WITH &&
    )
);

-- Only one active discount per product
CREATE TABLE discounts (
    discount_id SERIAL PRIMARY KEY,
    product_id INTEGER,
    valid_period DATERANGE,
    is_active BOOLEAN,
    EXCLUDE USING GIST (
        product_id WITH =,
        valid_period WITH &&
    ) WHERE (is_active)
);

-- Geographic constraint: prevent overlapping zones
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE zones (
    zone_id SERIAL PRIMARY KEY,
    area GEOMETRY,
    EXCLUDE USING GIST (area WITH &&)
);
```

## Managing Constraints

### Listing Constraints

```sql
-- View all constraints for a table
\d+ table_name

-- Query information schema
SELECT 
    constraint_name,
    constraint_type,
    table_name
FROM information_schema.table_constraints
WHERE table_name = 'users';

-- Detailed constraint info
SELECT
    tc.constraint_name,
    tc.constraint_type,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'orders';

-- Check constraint definitions
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'products'::regclass;
```

### Dropping Constraints

```sql
-- Drop primary key
ALTER TABLE users DROP CONSTRAINT users_pkey;

-- Drop foreign key
ALTER TABLE orders DROP CONSTRAINT fk_user;

-- Drop unique constraint
ALTER TABLE products DROP CONSTRAINT unique_sku;

-- Drop check constraint
ALTER TABLE products DROP CONSTRAINT check_price_positive;

-- Drop if exists
ALTER TABLE products DROP CONSTRAINT IF EXISTS check_old_constraint;
```

### Disabling/Enabling Constraints

```sql
-- You cannot disable constraints directly in PostgreSQL
-- But you can use NOT VALID for new rows only

-- Add constraint without validating existing data
ALTER TABLE products 
ADD CONSTRAINT check_price CHECK (price > 0) NOT VALID;

-- Validate later (locks table)
ALTER TABLE products VALIDATE CONSTRAINT check_price;

-- For foreign keys during data load
ALTER TABLE orders DROP CONSTRAINT fk_user;
-- ... bulk load data ...
ALTER TABLE orders ADD CONSTRAINT fk_user 
    FOREIGN KEY (user_id) REFERENCES users(user_id);
```

## Deferrable Constraints

### Overview

Deferrable constraints are checked at the end of a transaction instead of immediately.

```sql
-- Create deferrable foreign key
CREATE TABLE departments (
    dept_id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    dept_id INTEGER,
    CONSTRAINT fk_dept FOREIGN KEY (dept_id) 
        REFERENCES departments(dept_id)
        DEFERRABLE INITIALLY DEFERRED
);

-- This works with DEFERRABLE
BEGIN;
INSERT INTO employees VALUES (1, 'John', 10);
INSERT INTO departments VALUES (10, 'IT');
COMMIT;

-- Without DEFERRABLE, the first INSERT would fail

-- Set for session
SET CONSTRAINTS ALL DEFERRED;
SET CONSTRAINTS ALL IMMEDIATE;

-- Set for specific constraint
SET CONSTRAINTS fk_dept DEFERRED;
```

### Circular References

```sql
-- Deferrable allows circular references
CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    latest_book_id INTEGER,
    CONSTRAINT fk_latest_book FOREIGN KEY (latest_book_id)
        REFERENCES books(book_id)
        DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    author_id INTEGER,
    CONSTRAINT fk_author FOREIGN KEY (author_id)
        REFERENCES authors(author_id)
        DEFERRABLE INITIALLY DEFERRED
);

-- Insert with circular reference
BEGIN;
INSERT INTO authors VALUES (1, 'John Doe', 100);
INSERT INTO books VALUES (100, 'Great Book', 1);
COMMIT;
```

## Best Practices

### 1. Primary Keys

```sql
-- DO: Use SERIAL or BIGSERIAL for auto-increment
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,  -- Better than SERIAL for large tables
    username VARCHAR(50)
);

-- DO: Consider UUID for distributed systems
CREATE TABLE distributed_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data TEXT
);

-- DON'T: Use business data as primary key
CREATE TABLE bad_example (
    email VARCHAR(255) PRIMARY KEY  -- What if user changes email?
);
```

### 2. Foreign Keys

```sql
-- DO: Always index foreign keys
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id)
);
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- DO: Choose appropriate referential action
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL  -- Keep logs
);

CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE  -- Delete items
);
```

### 3. Check Constraints

```sql
-- DO: Validate data at database level
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    price NUMERIC(10, 2) CHECK (price > 0),
    discount NUMERIC(5, 2) CHECK (discount BETWEEN 0 AND 100)
);

-- DON'T: Rely only on application validation
-- Database constraints are last line of defense
```

### 4. Naming Conventions

```sql
-- Primary keys: pk_tablename
-- Foreign keys: fk_tablename_column
-- Unique: unique_column or uq_tablename_column
-- Check: check_condition or ck_tablename_condition

CREATE TABLE orders (
    order_id SERIAL,
    user_id INTEGER,
    total DECIMAL(10, 2),
    status VARCHAR(20),
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(user_id),
    CONSTRAINT ck_orders_total CHECK (total >= 0),
    CONSTRAINT ck_orders_status CHECK (status IN ('pending', 'completed', 'cancelled'))
);
```

## Summary

**Key Constraint Types**:
- **PRIMARY KEY**: Unique identifier, not null
- **FOREIGN KEY**: Referential integrity between tables
- **UNIQUE**: No duplicate values (allows NULL)
- **CHECK**: Custom validation rules
- **NOT NULL**: Requires a value
- **DEFAULT**: Automatic value assignment
- **EXCLUSION**: Prevent overlapping ranges

**Best Practices**:
- Always define primary keys
- Use foreign keys for referential integrity
- Index foreign key columns
- Choose appropriate referential actions
- Use CHECK constraints for data validation
- Name constraints consistently

**Next Topics**:
- [Indexes](09-indexes.md)
- [Transactions and ACID](16-transactions-and-acid.md)
- [Database Design Principles](06-database-design-principles.md)
