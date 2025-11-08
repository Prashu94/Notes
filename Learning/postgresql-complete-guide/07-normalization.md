# Normalization

## Overview

Database normalization is the process of organizing data to:
- Reduce redundancy
- Improve data integrity
- Simplify data maintenance
- Optimize query performance

## Normal Forms

### First Normal Form (1NF)

**Rules**:
1. Each column contains atomic (indivisible) values
2. Each column contains values of a single type
3. Each column has a unique name
4. Order doesn't matter

**Before 1NF** (Violates atomicity):
```sql
CREATE TABLE bad_customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    phones VARCHAR(255)  -- '555-1234, 555-5678, 555-9012'
);
```

**After 1NF**:
```sql
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE customer_phones (
    phone_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    phone_number VARCHAR(20)
);
```

**Another 1NF Example**:
```sql
-- Violates 1NF: Repeating groups
CREATE TABLE bad_orders (
    order_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100),
    product1 VARCHAR(100),
    quantity1 INTEGER,
    product2 VARCHAR(100),
    quantity2 INTEGER,
    product3 VARCHAR(100),
    quantity3 INTEGER
);

-- Conforms to 1NF
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER
);
```

### Second Normal Form (2NF)

**Rules**:
1. Must be in 1NF
2. No partial dependencies (non-key attributes must depend on entire primary key)

**Applies to**: Tables with composite primary keys

**Before 2NF** (Partial dependency):
```sql
CREATE TABLE bad_order_items (
    order_id INTEGER,
    product_id INTEGER,
    product_name VARCHAR(100),      -- Depends only on product_id
    product_price DECIMAL(10, 2),   -- Depends only on product_id
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);
```

**After 2NF**:
```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    product_price DECIMAL(10, 2)
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);
```

**Another Example**:
```sql
-- Violates 2NF
CREATE TABLE bad_student_courses (
    student_id INTEGER,
    course_id INTEGER,
    student_name VARCHAR(100),      -- Depends only on student_id
    student_email VARCHAR(255),     -- Depends only on student_id
    course_name VARCHAR(100),       -- Depends only on course_id
    instructor VARCHAR(100),        -- Depends only on course_id
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id)
);

-- Conforms to 2NF
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    student_name VARCHAR(100),
    student_email VARCHAR(255)
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100),
    instructor VARCHAR(100)
);

CREATE TABLE enrollments (
    student_id INTEGER REFERENCES students(student_id),
    course_id INTEGER REFERENCES courses(course_id),
    grade VARCHAR(2),
    PRIMARY KEY (student_id, course_id)
);
```

### Third Normal Form (3NF)

**Rules**:
1. Must be in 2NF
2. No transitive dependencies (non-key attributes must not depend on other non-key attributes)

**Before 3NF** (Transitive dependency):
```sql
CREATE TABLE bad_employees (
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(100),
    department_id INTEGER,
    department_name VARCHAR(100),      -- Depends on department_id (transitive)
    department_location VARCHAR(100)   -- Depends on department_id (transitive)
);
```

**After 3NF**:
```sql
CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(100),
    department_location VARCHAR(100)
);

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(100),
    department_id INTEGER REFERENCES departments(department_id)
);
```

**Another Example**:
```sql
-- Violates 3NF
CREATE TABLE bad_books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    author_id INTEGER,
    author_name VARCHAR(100),         -- Transitive dependency
    author_country VARCHAR(50),       -- Transitive dependency
    publisher_id INTEGER,
    publisher_name VARCHAR(100),      -- Transitive dependency
    publisher_city VARCHAR(100)       -- Transitive dependency
);

-- Conforms to 3NF
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    author_name VARCHAR(100),
    author_country VARCHAR(50)
);

CREATE TABLE publishers (
    publisher_id SERIAL PRIMARY KEY,
    publisher_name VARCHAR(100),
    publisher_city VARCHAR(100)
);

CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    author_id INTEGER REFERENCES authors(author_id),
    publisher_id INTEGER REFERENCES publishers(publisher_id)
);
```

### Boyce-Codd Normal Form (BCNF)

**Rules**:
1. Must be in 3NF
2. Every determinant must be a candidate key

**BCNF is stricter than 3NF** - handles special cases where 3NF isn't enough.

**Example**:
```sql
-- Violates BCNF (but is in 3NF)
CREATE TABLE class_schedule (
    student_id INTEGER,
    course_id INTEGER,
    instructor VARCHAR(100),
    -- Functional dependencies:
    -- (student_id, course_id) → instructor (composite key determines instructor)
    -- instructor → course_id (instructor determines course - violation!)
    PRIMARY KEY (student_id, course_id)
);

-- Conforms to BCNF
CREATE TABLE instructor_courses (
    instructor VARCHAR(100) PRIMARY KEY,
    course_id INTEGER REFERENCES courses(course_id)
);

CREATE TABLE student_enrollments (
    student_id INTEGER,
    instructor VARCHAR(100) REFERENCES instructor_courses(instructor),
    PRIMARY KEY (student_id, instructor)
);
```

### Fourth Normal Form (4NF)

**Rules**:
1. Must be in BCNF
2. No multi-valued dependencies

**Before 4NF** (Multi-valued dependency):
```sql
-- Violates 4NF: Skills and languages are independent
CREATE TABLE bad_employee_skills (
    employee_id INTEGER,
    skill VARCHAR(100),
    language VARCHAR(50),
    PRIMARY KEY (employee_id, skill, language)
);

-- This creates unnecessary combinations:
-- If employee knows Java AND Spanish, French
-- We'd need: (emp, Java, Spanish), (emp, Java, French)
```

**After 4NF**:
```sql
CREATE TABLE employee_skills (
    employee_id INTEGER,
    skill VARCHAR(100),
    PRIMARY KEY (employee_id, skill)
);

CREATE TABLE employee_languages (
    employee_id INTEGER,
    language VARCHAR(50),
    PRIMARY KEY (employee_id, language)
);
```

### Fifth Normal Form (5NF)

**Rules**:
1. Must be in 4NF
2. No join dependencies that aren't implied by candidate keys

**Rarely needed in practice.**

**Example**:
```sql
-- A complex scenario where a table can be decomposed
-- into smaller tables that can be joined to recreate original

-- Violates 5NF
CREATE TABLE agent_company_product (
    agent_id INTEGER,
    company_id INTEGER,
    product_id INTEGER,
    PRIMARY KEY (agent_id, company_id, product_id)
);

-- After 5NF (if business rules allow)
CREATE TABLE agent_company (
    agent_id INTEGER,
    company_id INTEGER,
    PRIMARY KEY (agent_id, company_id)
);

CREATE TABLE company_product (
    company_id INTEGER,
    product_id INTEGER,
    PRIMARY KEY (company_id, product_id)
);

CREATE TABLE agent_product (
    agent_id INTEGER,
    product_id INTEGER,
    PRIMARY KEY (agent_id, product_id)
);
```

## Practical Normalization Example

### Denormalized Table (Before)

```sql
CREATE TABLE bad_orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE,
    
    -- Customer info (repeated for each order)
    customer_id INTEGER,
    customer_name VARCHAR(100),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_address TEXT,
    customer_city VARCHAR(100),
    customer_country VARCHAR(50),
    
    -- Product 1
    product1_id INTEGER,
    product1_name VARCHAR(100),
    product1_price DECIMAL(10, 2),
    product1_quantity INTEGER,
    
    -- Product 2
    product2_id INTEGER,
    product2_name VARCHAR(100),
    product2_price DECIMAL(10, 2),
    product2_quantity INTEGER,
    
    -- Product 3
    product3_id INTEGER,
    product3_name VARCHAR(100),
    product3_price DECIMAL(10, 2),
    product3_quantity INTEGER,
    
    -- Order totals
    subtotal DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    total DECIMAL(10, 2)
);
```

**Problems**:
- Data redundancy (customer info repeated)
- Update anomalies (changing customer email requires updating all orders)
- Insertion anomalies (can't add customer without an order)
- Deletion anomalies (deleting last order deletes customer)
- Limited to 3 products per order
- Wastes space for orders with fewer products

### Normalized Tables (After - 3NF)

```sql
-- Customers table
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Addresses table (one-to-many relationship)
CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    address_line TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE
);

-- Products table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0
);

-- Orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address_id INTEGER REFERENCES addresses(address_id),
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) GENERATED ALWAYS AS (subtotal + tax) STORED
);

-- Order items table (many-to-many resolution)
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    line_total DECIMAL(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Create indexes for performance
CREATE INDEX idx_addresses_customer ON addresses(customer_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

**Benefits**:
- ✅ No redundancy (customer info stored once)
- ✅ No update anomalies (change customer email in one place)
- ✅ No insertion anomalies (can add customers independently)
- ✅ No deletion anomalies (deleting order doesn't delete customer)
- ✅ Unlimited products per order
- ✅ Efficient storage (no wasted columns)
- ✅ Data integrity enforced by foreign keys

## When to Denormalize

### Reasons for Denormalization

**1. Read Performance**
```sql
-- Normalized (requires join)
SELECT 
    o.order_id,
    c.name,
    c.email,
    o.total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- Denormalized (faster for reads)
CREATE TABLE orders_denorm (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    customer_name VARCHAR(100),      -- Denormalized
    customer_email VARCHAR(255),     -- Denormalized
    total DECIMAL(10, 2)
);
```

**2. Reporting/Analytics**
```sql
-- Create materialized view for reporting
CREATE MATERIALIZED VIEW customer_order_stats AS
SELECT 
    c.customer_id,
    c.name,
    c.email,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(o.total), 0) AS lifetime_value,
    MAX(o.order_date) AS last_order_date,
    AVG(o.total) AS average_order_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email;

CREATE INDEX idx_customer_stats_id ON customer_order_stats(customer_id);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY customer_order_stats;
```

**3. Historical Data**
```sql
-- Store price at time of purchase
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    product_name VARCHAR(100),           -- Denormalized for history
    unit_price DECIMAL(10, 2),           -- Price at purchase time
    quantity INTEGER
);
```

### Controlled Denormalization

```sql
-- Keep normalized tables as source of truth
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    total_orders INTEGER DEFAULT 0,      -- Denormalized counter
    lifetime_value DECIMAL(10, 2) DEFAULT 0  -- Denormalized sum
);

-- Use triggers to keep denormalized data in sync
CREATE OR REPLACE FUNCTION update_customer_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE customers
        SET total_orders = total_orders + 1,
            lifetime_value = lifetime_value + NEW.total
        WHERE customer_id = NEW.customer_id;
    ELSIF (TG_OP = 'UPDATE') THEN
        UPDATE customers
        SET lifetime_value = lifetime_value - OLD.total + NEW.total
        WHERE customer_id = NEW.customer_id;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE customers
        SET total_orders = total_orders - 1,
            lifetime_value = lifetime_value - OLD.total
        WHERE customer_id = OLD.customer_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_customer_stats
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION update_customer_stats();
```

## Common Scenarios

### Scenario 1: Blog System

```sql
-- Normalized design (3NF)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    bio TEXT
);

CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    author_id INTEGER REFERENCES users(user_id),
    title VARCHAR(200) NOT NULL,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tags (
    tag_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE likes (
    post_id INTEGER REFERENCES posts(post_id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (post_id, user_id)
);
```

### Scenario 2: Inventory Management

```sql
-- Normalized design
CREATE TABLE warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location TEXT
);

CREATE TABLE suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(category_id)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id),
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    unit_cost DECIMAL(10, 2) NOT NULL
);

CREATE TABLE warehouse_inventory (
    warehouse_id INTEGER REFERENCES warehouses(warehouse_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL DEFAULT 0,
    reorder_level INTEGER NOT NULL,
    PRIMARY KEY (warehouse_id, product_id)
);

CREATE TABLE purchase_orders (
    po_id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(supplier_id),
    order_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE purchase_order_items (
    po_item_id SERIAL PRIMARY KEY,
    po_id INTEGER REFERENCES purchase_orders(po_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL
);
```

## Best Practices

### 1. Start with Normalization

Always start with a normalized design (typically 3NF), then selectively denormalize based on:
- Measured performance issues
- Specific query patterns
- Read-to-write ratio

### 2. Document Denormalization

```sql
-- Add comments explaining denormalization
COMMENT ON COLUMN orders.customer_name IS 
'Denormalized from customers.name for query performance. Updated via trigger.';

COMMENT ON TABLE customer_order_stats IS 
'Materialized view for reporting. Refresh daily at 2 AM.';
```

### 3. Use Views for Abstraction

```sql
-- Normalized storage
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category_id INTEGER REFERENCES categories(category_id)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- View hides complexity
CREATE VIEW products_with_category AS
SELECT 
    p.product_id,
    p.name AS product_name,
    c.name AS category_name
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id;

-- Applications query the view
SELECT * FROM products_with_category;
```

### 4. Monitor and Measure

```sql
-- Track query performance
CREATE EXTENSION pg_stat_statements;

-- Identify slow queries
SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Summary

**Normal Forms**:
- **1NF**: Atomic values, no repeating groups
- **2NF**: 1NF + no partial dependencies
- **3NF**: 2NF + no transitive dependencies
- **BCNF**: 3NF + every determinant is a candidate key
- **4NF**: BCNF + no multi-valued dependencies
- **5NF**: 4NF + no join dependencies

**Benefits of Normalization**:
- ✅ Reduced redundancy
- ✅ Improved data integrity
- ✅ Easier maintenance
- ✅ Logical data organization

**When to Denormalize**:
- Read-heavy workloads
- Complex reporting queries
- Historical data preservation
- After measuring performance

**Best Practices**:
- Start normalized (3NF typical target)
- Denormalize selectively based on metrics
- Use views and materialized views
- Document denormalization decisions
- Maintain data integrity with triggers

**Next Topics**:
- [Database Design Principles](06-database-design-principles.md)
- [Constraints and Keys](08-constraints-and-keys.md)
- [Query Optimization](20-query-optimization.md)
