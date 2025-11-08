# Database Design Principles

## Overview

Good database design is crucial for:
- Data integrity and consistency
- Query performance
- Scalability
- Maintainability
- Application reliability

## Core Principles

### 1. Data Integrity

**Goal**: Ensure data is accurate, consistent, and reliable.

**Techniques**:

```sql
-- Use constraints
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}$'),
    age INTEGER CHECK (age BETWEEN 0 AND 120),
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Foreign key relationships
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
);

-- Prevent invalid state combinations
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    paid_at TIMESTAMPTZ,
    CONSTRAINT check_paid_status CHECK (
        (status = 'paid' AND paid_at IS NOT NULL) OR
        (status != 'paid' AND paid_at IS NULL)
    )
);
```

### 2. Minimize Redundancy

**Goal**: Store each piece of data once (or with controlled redundancy).

```sql
-- Bad: Redundant data
CREATE TABLE bad_orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    user_name VARCHAR(100),      -- Redundant
    user_email VARCHAR(255),     -- Redundant
    user_address TEXT,           -- Redundant
    product_id INTEGER,
    product_name VARCHAR(100),   -- Redundant
    product_price DECIMAL(10,2)  -- Redundant
);

-- Good: Normalized design
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    address TEXT
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    price_at_purchase DECIMAL(10,2) NOT NULL  -- OK: Historical data
);
```

### 3. Entity-Relationship Modeling

**Identify Entities**:
```sql
-- Entities are things/concepts in your domain
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TIMESTAMPTZ DEFAULT NOW()
);
```

**Identify Relationships**:

```sql
-- One-to-One: User to Profile
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE
);

CREATE TABLE user_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(user_id),  -- UNIQUE = one-to-one
    bio TEXT,
    avatar_url TEXT
);

-- One-to-Many: Customer to Orders
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),  -- Many orders per customer
    total DECIMAL(10,2)
);

-- Many-to-Many: Students and Courses
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- Junction/Bridge table
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id),
    course_id INTEGER REFERENCES courses(course_id),
    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
    grade VARCHAR(2),
    UNIQUE (student_id, course_id)  -- Prevent duplicate enrollments
);
```

### 4. Choose Appropriate Data Types

```sql
-- Good: Appropriate types
CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,           -- BIGSERIAL for scalability
    sku VARCHAR(50) NOT NULL UNIQUE,            -- Fixed max length
    name TEXT NOT NULL,                         -- TEXT for variable length
    description TEXT,                           -- TEXT for long content
    price NUMERIC(10, 2) NOT NULL,              -- NUMERIC for money
    stock_quantity INTEGER NOT NULL DEFAULT 0,  -- INTEGER for counts
    is_active BOOLEAN DEFAULT TRUE,             -- BOOLEAN for flags
    metadata JSONB,                             -- JSONB for flexible data
    created_at TIMESTAMPTZ DEFAULT NOW(),       -- TIMESTAMPTZ for timestamps
    weight_kg DECIMAL(8, 3)                     -- DECIMAL for measurements
);

-- Bad: Poor type choices
CREATE TABLE bad_products (
    product_id INTEGER PRIMARY KEY,             -- Too small for large scale
    sku TEXT,                                   -- Should have max length
    price FLOAT,                                -- Precision issues with money
    stock_quantity VARCHAR(10),                 -- Should be INTEGER
    is_active VARCHAR(5),                       -- Should be BOOLEAN
    created_at VARCHAR(50)                      -- Should be TIMESTAMPTZ
);
```

### 5. Naming Conventions

```sql
-- Consistent naming conventions
CREATE TABLE customers (                        -- Plural table names
    customer_id SERIAL PRIMARY KEY,             -- table_name_id for PKs
    first_name VARCHAR(50),                     -- snake_case
    last_name VARCHAR(50),
    email_address VARCHAR(255),
    phone_number VARCHAR(20),
    created_at TIMESTAMPTZ,                     -- _at suffix for timestamps
    updated_at TIMESTAMPTZ,
    is_active BOOLEAN,                          -- is_ prefix for booleans
    has_subscription BOOLEAN                    -- has_ prefix for booleans
);

-- Foreign keys
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),  -- FK matches referenced column
    order_date DATE,
    total_amount DECIMAL(10, 2)
);

-- Constraints
ALTER TABLE orders 
ADD CONSTRAINT fk_orders_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

ALTER TABLE orders 
ADD CONSTRAINT check_orders_total 
    CHECK (total_amount >= 0);

ALTER TABLE orders 
ADD CONSTRAINT unique_orders_reference 
    UNIQUE (order_reference);

-- Indexes
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

### 6. Primary Keys

```sql
-- Surrogate keys (recommended for most cases)
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,              -- Auto-increment surrogate key
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL
);

-- Natural keys (use when appropriate)
CREATE TABLE countries (
    country_code CHAR(2) PRIMARY KEY,           -- ISO 3166-1 alpha-2
    country_name VARCHAR(100) NOT NULL
);

-- Composite keys
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- UUID keys (for distributed systems)
CREATE TABLE distributed_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data TEXT
);
```

## Design Patterns

### 1. Audit Trail Pattern

```sql
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by INTEGER REFERENCES users(user_id),
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_by INTEGER REFERENCES users(user_id),
    deleted_at TIMESTAMPTZ,                     -- Soft delete
    deleted_by INTEGER REFERENCES users(user_id)
);

-- Automatic update trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 2. Soft Delete Pattern

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ,
    deleted_by INTEGER REFERENCES users(user_id)
);

-- View for active products only
CREATE VIEW active_products AS
SELECT * FROM products WHERE is_deleted = FALSE;

-- Prevent accidental querying of deleted records
CREATE INDEX idx_products_active ON products(product_id) WHERE is_deleted = FALSE;
```

### 3. Versioning Pattern

```sql
CREATE TABLE documents (
    document_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE document_versions (
    version_id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(document_id),
    version INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    changed_by INTEGER REFERENCES users(user_id),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (document_id, version)
);
```

### 4. Hierarchical Data Pattern

```sql
-- Adjacency List (simple parent reference)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES categories(category_id)
);

-- Materialized Path
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    path TEXT NOT NULL UNIQUE  -- e.g., '/1/3/7/'
);

-- Closure Table (many-to-many self-reference)
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE category_tree (
    ancestor_id INTEGER REFERENCES categories(category_id),
    descendant_id INTEGER REFERENCES categories(category_id),
    depth INTEGER NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id)
);

-- Nested Sets (rarely used in PostgreSQL due to ltree extension)
CREATE EXTENSION ltree;

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    path ltree NOT NULL
);

CREATE INDEX idx_categories_path ON categories USING GIST (path);
```

### 5. Lookup Tables Pattern

```sql
-- Status lookup table
CREATE TABLE order_statuses (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    sort_order INTEGER NOT NULL
);

INSERT INTO order_statuses (status_name, display_name, sort_order) VALUES
    ('pending', 'Pending', 1),
    ('processing', 'Processing', 2),
    ('shipped', 'Shipped', 3),
    ('delivered', 'Delivered', 4),
    ('cancelled', 'Cancelled', 5);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    status_id INTEGER REFERENCES order_statuses(status_id),
    total DECIMAL(10, 2)
);

-- Alternative: ENUM type (simpler but less flexible)
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    status order_status DEFAULT 'pending',
    total DECIMAL(10, 2)
);
```

## Schema Organization

### 1. Use Schemas for Logical Separation

```sql
-- Create schemas
CREATE SCHEMA sales;
CREATE SCHEMA inventory;
CREATE SCHEMA hr;
CREATE SCHEMA audit;

-- Tables in different schemas
CREATE TABLE sales.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    total DECIMAL(10, 2)
);

CREATE TABLE inventory.products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    stock_quantity INTEGER
);

CREATE TABLE hr.employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50)
);

-- Audit tables
CREATE TABLE audit.order_changes (
    change_id SERIAL PRIMARY KEY,
    order_id INTEGER,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by INTEGER,
    old_values JSONB,
    new_values JSONB
);

-- Set default schema
SET search_path TO sales, inventory, public;
```

### 2. Separate Read and Write Concerns

```sql
-- Write tables (normalized)
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE,
    total DECIMAL(10, 2)
);

-- Read views (denormalized for performance)
CREATE MATERIALIZED VIEW customer_order_summary AS
SELECT 
    c.customer_id,
    c.name,
    c.email,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(o.total), 0) AS total_spent,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.email;

CREATE INDEX idx_customer_summary_id ON customer_order_summary(customer_id);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY customer_order_summary;
```

## Anti-Patterns to Avoid

### 1. Entity-Attribute-Value (EAV)

```sql
-- Bad: EAV pattern (flexible but slow)
CREATE TABLE entity_attributes (
    entity_id INTEGER,
    attribute_name VARCHAR(50),
    attribute_value TEXT
);

-- Better: Use JSONB for flexible attributes
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    attributes JSONB
);

CREATE INDEX idx_products_attributes ON products USING GIN (attributes);

-- Query specific attributes
SELECT * FROM products WHERE attributes->>'color' = 'red';
```

### 2. Polymorphic Associations

```sql
-- Bad: Polymorphic foreign key
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    commentable_type VARCHAR(50),  -- 'Post' or 'Product'
    commentable_id INTEGER,        -- References either posts or products
    content TEXT
);

-- Better: Separate tables or shared interface table
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    title TEXT
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE post_comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(post_id),
    content TEXT
);

CREATE TABLE product_comments (
    comment_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    content TEXT
);

-- Or use a shared interface
CREATE TABLE commentable_items (
    item_id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL
);

CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    item_id INTEGER UNIQUE REFERENCES commentable_items(item_id),
    title TEXT
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    item_id INTEGER UNIQUE REFERENCES commentable_items(item_id),
    name TEXT
);

CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES commentable_items(item_id),
    content TEXT
);
```

### 3. Multi-Column Attributes

```sql
-- Bad: Multiple similar columns
CREATE TABLE bad_contacts (
    contact_id SERIAL PRIMARY KEY,
    phone1 VARCHAR(20),
    phone2 VARCHAR(20),
    phone3 VARCHAR(20),
    email1 VARCHAR(255),
    email2 VARCHAR(255),
    email3 VARCHAR(255)
);

-- Good: Separate related table
CREATE TABLE contacts (
    contact_id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE contact_phones (
    phone_id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(contact_id),
    phone_type VARCHAR(20),  -- 'mobile', 'home', 'work'
    phone_number VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE
);

CREATE TABLE contact_emails (
    email_id SERIAL PRIMARY KEY,
    contact_id INTEGER REFERENCES contacts(contact_id),
    email_type VARCHAR(20),  -- 'personal', 'work'
    email_address VARCHAR(255),
    is_primary BOOLEAN DEFAULT FALSE
);
```

### 4. Storing Calculated Values

```sql
-- Bad: Storing calculated values that can become stale
CREATE TABLE bad_orders (
    order_id SERIAL PRIMARY KEY,
    subtotal DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    total DECIMAL(10, 2)  -- Redundant: total = subtotal + tax
);

-- Good: Calculate on the fly or use generated columns
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    subtotal DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) GENERATED ALWAYS AS (subtotal + tax) STORED
);

-- Or calculate in query
SELECT 
    order_id,
    subtotal,
    tax,
    subtotal + tax AS total
FROM orders;

-- Exception: Storing for historical accuracy
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    price_at_purchase DECIMAL(10, 2) NOT NULL,  -- OK: Historical price
    quantity INTEGER NOT NULL
);
```

## Performance Considerations

### 1. Index Strategy

```sql
-- Index foreign keys
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- Index frequently queried columns
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Composite indexes for common query patterns
CREATE INDEX idx_orders_customer_status ON orders(customer_id, status);
CREATE INDEX idx_products_category_active ON products(category_id, is_active);
```

### 2. Partitioning Strategy

```sql
-- Partition large tables by date
CREATE TABLE orders (
    order_id BIGSERIAL,
    customer_id INTEGER,
    order_date DATE NOT NULL,
    total DECIMAL(10, 2)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Partition by list
CREATE TABLE customers (
    customer_id BIGSERIAL,
    country_code CHAR(2) NOT NULL,
    name VARCHAR(100)
) PARTITION BY LIST (country_code);

CREATE TABLE customers_us PARTITION OF customers
    FOR VALUES IN ('US');

CREATE TABLE customers_uk PARTITION OF customers
    FOR VALUES IN ('UK');
```

## Best Practices Checklist

### Design Phase
- [ ] Identify all entities and relationships
- [ ] Choose appropriate primary keys
- [ ] Define all foreign key relationships
- [ ] Apply normalization (usually 3NF)
- [ ] Consider denormalization for read-heavy workloads
- [ ] Choose appropriate data types
- [ ] Define all constraints (NOT NULL, CHECK, UNIQUE)
- [ ] Plan for audit trails if needed
- [ ] Consider soft deletes vs hard deletes

### Implementation Phase
- [ ] Use consistent naming conventions
- [ ] Add comments to tables and columns
- [ ] Create indexes on foreign keys
- [ ] Create indexes on frequently queried columns
- [ ] Set appropriate default values
- [ ] Use transactions for related operations
- [ ] Implement triggers for automation (sparingly)

### Documentation
- [ ] Document schema with ER diagrams
- [ ] Document business rules
- [ ] Document any denormalization decisions
- [ ] Maintain data dictionary

### Testing
- [ ] Test all constraints
- [ ] Test cascading deletes
- [ ] Load test with realistic data volumes
- [ ] Test query performance
- [ ] Test backup and recovery

## Real-World Example: E-Commerce Schema

```sql
-- Core entities
CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE addresses (
    address_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(customer_id) ON DELETE CASCADE,
    address_type VARCHAR(20) CHECK (address_type IN ('billing', 'shipping')),
    street_address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50),
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    parent_id INTEGER REFERENCES categories(category_id),
    slug VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(category_id),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(customer_id),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    subtotal NUMERIC(10, 2) NOT NULL CHECK (subtotal >= 0),
    tax NUMERIC(10, 2) NOT NULL CHECK (tax >= 0),
    shipping NUMERIC(10, 2) NOT NULL CHECK (shipping >= 0),
    total NUMERIC(10, 2) GENERATED ALWAYS AS (subtotal + tax + shipping) STORED,
    billing_address_id BIGINT REFERENCES addresses(address_id),
    shipping_address_id BIGINT REFERENCES addresses(address_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    order_item_id BIGSERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    subtotal NUMERIC(10, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Indexes
CREATE INDEX idx_addresses_customer ON addresses(customer_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
```

## Summary

**Key Principles**:
- Ensure data integrity with constraints
- Minimize redundancy through normalization
- Model entities and relationships clearly
- Choose appropriate data types
- Use consistent naming conventions
- Index strategically for performance

**Common Patterns**:
- Audit trails for tracking changes
- Soft deletes for data retention
- Versioning for historical records
- Hierarchical data structures
- Lookup tables for code values

**Avoid Anti-Patterns**:
- EAV (use JSONB instead)
- Polymorphic associations
- Multi-column attributes
- Storing calculated values (use generated columns)

**Next Topics**:
- [Normalization](07-normalization.md)
- [Constraints and Keys](08-constraints-and-keys.md)
- [Indexes](09-indexes.md)
