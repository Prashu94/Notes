# Triggers

## Overview

Triggers are database objects that automatically execute specified functions in response to certain events on a table or view. They are essential for enforcing business rules, maintaining data integrity, auditing changes, and automating complex workflows.

## Table of Contents
- [Trigger Basics](#trigger-basics)
- [Trigger Types](#trigger-types)
- [Creating Triggers](#creating-triggers)
- [Trigger Functions](#trigger-functions)
- [Trigger Variables](#trigger-variables)
- [Event Triggers](#event-triggers)
- [Common Use Cases](#common-use-cases)
- [Performance Considerations](#performance-considerations)

## Trigger Basics

### Trigger Components

A trigger consists of two parts:
1. **Trigger Function**: The PL/pgSQL function that executes
2. **Trigger Definition**: Specifies when the function fires

```sql
-- Step 1: Create the trigger function
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO employee_audit (
        employee_id,
        action,
        old_salary,
        new_salary,
        changed_at,
        changed_by
    ) VALUES (
        NEW.employee_id,
        TG_OP,
        OLD.salary,
        NEW.salary,
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 2: Create the trigger
CREATE TRIGGER employee_audit_trigger
    AFTER UPDATE ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_employee_changes();
```

### Trigger Timing

- **BEFORE**: Execute before the operation (can prevent or modify)
- **AFTER**: Execute after the operation (for auditing, cascading)
- **INSTEAD OF**: Execute instead of the operation (for views)

### Trigger Events

- **INSERT**: New rows added
- **UPDATE**: Existing rows modified
- **DELETE**: Rows removed
- **TRUNCATE**: Table truncated (statement-level only)

### Trigger Level

- **FOR EACH ROW**: Fires once per affected row
- **FOR EACH STATEMENT**: Fires once per SQL statement

## Trigger Types

### Row-Level Triggers

```sql
-- BEFORE INSERT trigger
CREATE OR REPLACE FUNCTION set_created_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.created_at := CURRENT_TIMESTAMP;
    NEW.created_by := current_user;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamps
    BEFORE INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION set_created_timestamp();

-- BEFORE UPDATE trigger
CREATE OR REPLACE FUNCTION set_updated_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    NEW.updated_by := current_user;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_update_timestamp
    BEFORE UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_timestamp();

-- AFTER DELETE trigger
CREATE OR REPLACE FUNCTION archive_deleted_order()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO deleted_orders
    SELECT OLD.*, CURRENT_TIMESTAMP, current_user;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_order_trigger
    AFTER DELETE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION archive_deleted_order();
```

### Statement-Level Triggers

```sql
-- Log all bulk operations
CREATE OR REPLACE FUNCTION log_bulk_operation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO operation_log (
        table_name,
        operation,
        timestamp,
        username
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        CURRENT_TIMESTAMP,
        current_user
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_operations
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH STATEMENT
    EXECUTE FUNCTION log_bulk_operation();

-- Prevent truncate
CREATE OR REPLACE FUNCTION prevent_truncate()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'TRUNCATE is not allowed on this table';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_truncate
    BEFORE TRUNCATE ON important_data
    FOR EACH STATEMENT
    EXECUTE FUNCTION prevent_truncate();
```

### Multiple Event Triggers

```sql
-- Single trigger for multiple events
CREATE OR REPLACE FUNCTION track_all_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO change_log (action, new_data, changed_at)
        VALUES ('INSERT', row_to_json(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO change_log (action, old_data, new_data, changed_at)
        VALUES ('UPDATE', row_to_json(OLD), row_to_json(NEW), CURRENT_TIMESTAMP);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO change_log (action, old_data, changed_at)
        VALUES ('DELETE', row_to_json(OLD), CURRENT_TIMESTAMP);
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER track_changes
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION track_all_changes();
```

## Creating Triggers

### Basic Syntax

```sql
CREATE [ CONSTRAINT ] TRIGGER name
    { BEFORE | AFTER | INSTEAD OF } { event [ OR ... ] }
    ON table_name
    [ FROM referenced_table_name ]
    [ NOT DEFERRABLE | DEFERRABLE [ INITIALLY IMMEDIATE | INITIALLY DEFERRED ] ]
    [ FOR [ EACH ] { ROW | STATEMENT } ]
    [ WHEN ( condition ) ]
    EXECUTE FUNCTION function_name ( arguments )
```

### Conditional Triggers

```sql
-- Trigger only when specific columns change
CREATE TRIGGER salary_change_audit
    AFTER UPDATE OF salary, bonus ON employees
    FOR EACH ROW
    EXECUTE FUNCTION audit_salary_changes();

-- Trigger with WHEN condition
CREATE OR REPLACE FUNCTION notify_large_order()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('large_orders', 
        json_build_object(
            'order_id', NEW.order_id,
            'amount', NEW.total_amount
        )::text
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER large_order_notification
    AFTER INSERT ON orders
    FOR EACH ROW
    WHEN (NEW.total_amount > 10000)
    EXECUTE FUNCTION notify_large_order();

-- Only trigger when values actually change
CREATE TRIGGER update_only_if_changed
    AFTER UPDATE ON products
    FOR EACH ROW
    WHEN (OLD.* IS DISTINCT FROM NEW.*)
    EXECUTE FUNCTION log_product_change();
```

### INSTEAD OF Triggers (Views)

```sql
-- Create a view
CREATE VIEW employee_summary AS
SELECT 
    e.employee_id,
    e.employee_name,
    e.salary,
    d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- Make view updatable with trigger
CREATE OR REPLACE FUNCTION update_employee_summary()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE employees
    SET 
        employee_name = NEW.employee_name,
        salary = NEW.salary
    WHERE employee_id = NEW.employee_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_employee_view
    INSTEAD OF UPDATE ON employee_summary
    FOR EACH ROW
    EXECUTE FUNCTION update_employee_summary();

-- INSERT on view
CREATE OR REPLACE FUNCTION insert_employee_summary()
RETURNS TRIGGER AS $$
DECLARE
    v_dept_id INTEGER;
BEGIN
    -- Get department_id from name
    SELECT department_id INTO v_dept_id
    FROM departments
    WHERE department_name = NEW.department_name;
    
    IF v_dept_id IS NULL THEN
        RAISE EXCEPTION 'Department % not found', NEW.department_name;
    END IF;
    
    INSERT INTO employees (employee_name, salary, department_id)
    VALUES (NEW.employee_name, NEW.salary, v_dept_id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER insert_employee_view
    INSTEAD OF INSERT ON employee_summary
    FOR EACH ROW
    EXECUTE FUNCTION insert_employee_summary();
```

### Constraint Triggers

```sql
-- Deferrable constraint trigger
CREATE CONSTRAINT TRIGGER check_credit_limit
    AFTER INSERT OR UPDATE ON orders
    DEFERRABLE INITIALLY DEFERRED
    FOR EACH ROW
    EXECUTE FUNCTION validate_credit_limit();

-- Example: Can defer checking until transaction end
BEGIN;
    INSERT INTO orders (customer_id, total_amount) VALUES (1, 5000);
    -- Credit limit check deferred
    UPDATE customers SET credit_limit = credit_limit + 5000 WHERE customer_id = 1;
    -- Now check passes
COMMIT;
```

## Trigger Functions

### Special Return Values

```sql
-- BEFORE trigger: Can modify or skip operation
CREATE OR REPLACE FUNCTION validate_and_modify()
RETURNS TRIGGER AS $$
BEGIN
    -- Validate
    IF NEW.price < 0 THEN
        RAISE EXCEPTION 'Price cannot be negative';
    END IF;
    
    -- Modify before insert
    NEW.price := ROUND(NEW.price, 2);
    NEW.slug := LOWER(REGEXP_REPLACE(NEW.name, '\s+', '-', 'g'));
    
    RETURN NEW;  -- Continue with modified row
    -- RETURN NULL would skip the operation
END;
$$ LANGUAGE plpgsql;

-- Prevent deletion
CREATE OR REPLACE FUNCTION prevent_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_protected THEN
        RAISE EXCEPTION 'Cannot delete protected record';
    END IF;
    RETURN OLD;  -- Allow deletion
    -- RETURN NULL would skip deletion
END;
$$ LANGUAGE plpgsql;

-- AFTER trigger: Return value ignored
CREATE OR REPLACE FUNCTION after_trigger_example()
RETURNS TRIGGER AS $$
BEGIN
    -- Do some action
    INSERT INTO audit_log VALUES (NEW.id, TG_OP, CURRENT_TIMESTAMP);
    
    RETURN NULL;  -- Return value doesn't matter for AFTER triggers
END;
$$ LANGUAGE plpgsql;
```

### Modifying Related Tables

```sql
-- Cascade update to related table
CREATE OR REPLACE FUNCTION update_order_total()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE orders
    SET total_amount = (
        SELECT SUM(quantity * unit_price)
        FROM order_items
        WHERE order_id = NEW.order_id
    )
    WHERE order_id = NEW.order_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER recalculate_order_total
    AFTER INSERT OR UPDATE OR DELETE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_order_total();

-- Update inventory on order
CREATE OR REPLACE FUNCTION update_inventory()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE products
        SET stock_quantity = stock_quantity - NEW.quantity
        WHERE product_id = NEW.product_id;
        
        IF NOT FOUND OR (SELECT stock_quantity FROM products WHERE product_id = NEW.product_id) < 0 THEN
            RAISE EXCEPTION 'Insufficient inventory for product %', NEW.product_id;
        END IF;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE products
        SET stock_quantity = stock_quantity + OLD.quantity - NEW.quantity
        WHERE product_id = NEW.product_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE products
        SET stock_quantity = stock_quantity + OLD.quantity
        WHERE product_id = OLD.product_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER manage_inventory
    AFTER INSERT OR UPDATE OR DELETE ON order_items
    FOR EACH ROW
    EXECUTE FUNCTION update_inventory();
```

## Trigger Variables

### Available Special Variables

```sql
CREATE OR REPLACE FUNCTION demonstrate_trigger_variables()
RETURNS TRIGGER AS $$
BEGIN
    RAISE NOTICE 'Trigger: %', TG_NAME;                    -- Trigger name
    RAISE NOTICE 'Operation: %', TG_OP;                    -- INSERT/UPDATE/DELETE/TRUNCATE
    RAISE NOTICE 'Level: %', TG_LEVEL;                     -- ROW or STATEMENT
    RAISE NOTICE 'When: %', TG_WHEN;                       -- BEFORE, AFTER, INSTEAD OF
    RAISE NOTICE 'Table: %.%', TG_TABLE_SCHEMA, TG_TABLE_NAME;
    RAISE NOTICE 'Relation OID: %', TG_RELID;
    
    IF TG_OP != 'INSERT' THEN
        RAISE NOTICE 'Old row: %', OLD;
    END IF;
    
    IF TG_OP != 'DELETE' THEN
        RAISE NOTICE 'New row: %', NEW;
    END IF;
    
    -- TG_ARGV: arguments passed to trigger function
    IF TG_NARGS > 0 THEN
        RAISE NOTICE 'Argument 1: %', TG_ARGV[0];
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Accessing OLD and NEW

```sql
-- Compare old and new values
CREATE OR REPLACE FUNCTION track_specific_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO status_history (
            record_id,
            old_status,
            new_status,
            changed_at
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    IF OLD.price != NEW.price THEN
        INSERT INTO price_history (
            product_id,
            old_price,
            new_price,
            changed_at
        ) VALUES (
            NEW.id,
            OLD.price,
            NEW.price,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### Passing Arguments to Triggers

```sql
-- Generic audit function with arguments
CREATE OR REPLACE FUNCTION generic_audit()
RETURNS TRIGGER AS $$
DECLARE
    audit_table TEXT := TG_ARGV[0];
    key_column TEXT := TG_ARGV[1];
BEGIN
    EXECUTE format(
        'INSERT INTO %I (operation, key_value, old_data, new_data, changed_at)
         VALUES ($1, $2, $3, $4, $5)',
        audit_table
    ) USING TG_OP, 
            CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
            row_to_json(OLD),
            row_to_json(NEW),
            CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger with arguments
CREATE TRIGGER audit_products
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW
    EXECUTE FUNCTION generic_audit('product_audit', 'product_id');

CREATE TRIGGER audit_customers
    AFTER INSERT OR UPDATE OR DELETE ON customers
    FOR EACH ROW
    EXECUTE FUNCTION generic_audit('customer_audit', 'customer_id');
```

## Event Triggers

Event triggers fire on DDL events (CREATE, ALTER, DROP):

```sql
-- Log all DDL commands
CREATE OR REPLACE FUNCTION log_ddl_commands()
RETURNS event_trigger AS $$
BEGIN
    INSERT INTO ddl_log (
        command_tag,
        object_type,
        schema_name,
        object_name,
        executed_at,
        executed_by
    ) VALUES (
        TG_TAG,
        TG_EVENT,
        current_schema(),
        NULL,
        CURRENT_TIMESTAMP,
        current_user
    );
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER log_ddl
    ON ddl_command_end
    EXECUTE FUNCTION log_ddl_commands();

-- Prevent dropping tables
CREATE OR REPLACE FUNCTION prevent_table_drop()
RETURNS event_trigger AS $$
BEGIN
    IF TG_TAG = 'DROP TABLE' THEN
        RAISE EXCEPTION 'Dropping tables is not allowed!';
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER no_drop_table
    ON sql_drop
    EXECUTE FUNCTION prevent_table_drop();

-- Get detailed information about dropped objects
CREATE OR REPLACE FUNCTION log_dropped_objects()
RETURNS event_trigger AS $$
DECLARE
    obj RECORD;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
    LOOP
        INSERT INTO dropped_objects_log (
            object_type,
            schema_name,
            object_name,
            dropped_at,
            dropped_by
        ) VALUES (
            obj.object_type,
            obj.schema_name,
            obj.object_name,
            CURRENT_TIMESTAMP,
            current_user
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER track_drops
    ON sql_drop
    EXECUTE FUNCTION log_dropped_objects();
```

## Common Use Cases

### 1. Audit Trails

```sql
-- Complete audit solution
CREATE TABLE audit_log (
    audit_id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL,
    record_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT DEFAULT current_user
);

CREATE OR REPLACE FUNCTION create_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    record_id INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        old_data := row_to_json(OLD)::JSONB;
        record_id := OLD.id;
    ELSIF TG_OP = 'INSERT' THEN
        new_data := row_to_json(NEW)::JSONB;
        record_id := NEW.id;
    ELSIF TG_OP = 'UPDATE' THEN
        old_data := row_to_json(OLD)::JSONB;
        new_data := row_to_json(NEW)::JSONB;
        record_id := NEW.id;
    END IF;
    
    INSERT INTO audit_log (
        table_name,
        operation,
        record_id,
        old_values,
        new_values
    ) VALUES (
        TG_TABLE_NAME,
        TG_OP,
        record_id,
        old_data,
        new_data
    );
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply to multiple tables
CREATE TRIGGER audit_employees
    AFTER INSERT OR UPDATE OR DELETE ON employees
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();

CREATE TRIGGER audit_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW EXECUTE FUNCTION create_audit_trail();
```

### 2. Data Validation

```sql
-- Complex validation trigger
CREATE OR REPLACE FUNCTION validate_order()
RETURNS TRIGGER AS $$
BEGIN
    -- Check customer exists and is active
    IF NOT EXISTS (
        SELECT 1 FROM customers 
        WHERE customer_id = NEW.customer_id 
        AND status = 'active'
    ) THEN
        RAISE EXCEPTION 'Customer % is not active', NEW.customer_id;
    END IF;
    
    -- Check credit limit
    IF (
        SELECT SUM(total_amount) 
        FROM orders 
        WHERE customer_id = NEW.customer_id 
        AND status = 'pending'
    ) + NEW.total_amount > (
        SELECT credit_limit 
        FROM customers 
        WHERE customer_id = NEW.customer_id
    ) THEN
        RAISE EXCEPTION 'Order exceeds customer credit limit';
    END IF;
    
    -- Validate order date
    IF NEW.order_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Order date cannot be in the future';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_order_trigger
    BEFORE INSERT OR UPDATE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION validate_order();
```

### 3. Maintaining Derived Data

```sql
-- Keep summary table updated
CREATE OR REPLACE FUNCTION update_customer_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
        INSERT INTO customer_statistics (
            customer_id,
            total_orders,
            total_spent,
            last_order_date
        )
        SELECT 
            customer_id,
            COUNT(*),
            SUM(total_amount),
            MAX(order_date)
        FROM orders
        WHERE customer_id = NEW.customer_id
        GROUP BY customer_id
        ON CONFLICT (customer_id) DO UPDATE SET
            total_orders = EXCLUDED.total_orders,
            total_spent = EXCLUDED.total_spent,
            last_order_date = EXCLUDED.last_order_date;
    ELSIF TG_OP = 'DELETE' THEN
        -- Recalculate for deleted order's customer
        INSERT INTO customer_statistics (
            customer_id,
            total_orders,
            total_spent,
            last_order_date
        )
        SELECT 
            customer_id,
            COUNT(*),
            SUM(total_amount),
            MAX(order_date)
        FROM orders
        WHERE customer_id = OLD.customer_id
        GROUP BY customer_id
        ON CONFLICT (customer_id) DO UPDATE SET
            total_orders = EXCLUDED.total_orders,
            total_spent = EXCLUDED.total_spent,
            last_order_date = EXCLUDED.last_order_date;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER maintain_customer_stats
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_stats();
```

### 4. Notifications

```sql
-- Send notifications via LISTEN/NOTIFY
CREATE OR REPLACE FUNCTION notify_order_changes()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    payload := json_build_object(
        'operation', TG_OP,
        'order_id', COALESCE(NEW.order_id, OLD.order_id),
        'customer_id', COALESCE(NEW.customer_id, OLD.customer_id),
        'timestamp', CURRENT_TIMESTAMP
    );
    
    PERFORM pg_notify('order_changes', payload::text);
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notify_orders
    AFTER INSERT OR UPDATE OR DELETE ON orders
    FOR EACH ROW
    EXECUTE FUNCTION notify_order_changes();

-- Applications can listen:
-- LISTEN order_changes;
```

### 5. Enforcing Business Rules

```sql
-- Prevent modification of closed orders
CREATE OR REPLACE FUNCTION prevent_closed_order_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status = 'closed' THEN
        RAISE EXCEPTION 'Cannot modify closed orders';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_change_closed_orders
    BEFORE UPDATE OR DELETE ON orders
    FOR EACH ROW
    WHEN (OLD.status = 'closed')
    EXECUTE FUNCTION prevent_closed_order_changes();
```

## Performance Considerations

### 1. Minimize Trigger Work

```sql
-- BAD: Expensive operation in trigger
CREATE OR REPLACE FUNCTION slow_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- Complex calculation on every insert
    UPDATE statistics SET value = (
        SELECT COUNT(*) FROM huge_table WHERE condition
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- GOOD: Queue work for batch processing
CREATE OR REPLACE FUNCTION queue_for_processing()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO work_queue (table_name, record_id, operation)
    VALUES (TG_TABLE_NAME, NEW.id, TG_OP);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 2. Use Statement-Level When Possible

```sql
-- Row-level: Fires N times for N rows
CREATE TRIGGER row_trigger
    AFTER INSERT ON orders
    FOR EACH ROW
    EXECUTE FUNCTION row_level_function();

-- Statement-level: Fires once per statement
CREATE TRIGGER statement_trigger
    AFTER INSERT ON orders
    FOR EACH STATEMENT
    EXECUTE FUNCTION statement_level_function();
```

### 3. Avoid Trigger Cascades

```sql
-- Can cause performance issues
-- Trigger A modifies Table B
-- Trigger B modifies Table C
-- Trigger C modifies Table A (circular!)

-- Better: Use a single trigger with all logic
-- Or use explicit transaction control in procedures
```

### 4. Consider Trigger Ordering

```sql
-- Control execution order with trigger names (alphabetical)
CREATE TRIGGER a_first_trigger ...;
CREATE TRIGGER b_second_trigger ...;
CREATE TRIGGER c_third_trigger ...;

-- Or use explicit ordering (PostgreSQL 11+)
CREATE TRIGGER my_trigger
    AFTER UPDATE ON my_table
    FOR EACH ROW
    EXECUTE FUNCTION my_function();

-- Manage trigger order
ALTER TRIGGER my_trigger ON my_table
    DEPENDS ON EXTENSION my_extension;
```

## Managing Triggers

```sql
-- List all triggers
SELECT 
    t.tgname AS trigger_name,
    c.relname AS table_name,
    p.proname AS function_name,
    pg_get_triggerdef(t.oid) AS trigger_definition
FROM pg_trigger t
JOIN pg_class c ON t.tgrelid = c.oid
JOIN pg_proc p ON t.tgfoid = p.oid
WHERE NOT t.tgisinternal
ORDER BY c.relname, t.tgname;

-- Disable trigger
ALTER TABLE orders DISABLE TRIGGER audit_orders;

-- Enable trigger
ALTER TABLE orders ENABLE TRIGGER audit_orders;

-- Disable all triggers on table
ALTER TABLE orders DISABLE TRIGGER ALL;

-- Enable all triggers
ALTER TABLE orders ENABLE TRIGGER ALL;

-- Drop trigger
DROP TRIGGER IF EXISTS audit_orders ON orders;

-- Drop trigger function
DROP FUNCTION IF EXISTS create_audit_trail() CASCADE;
```

## Best Practices

1. **Keep triggers simple**: Complex logic belongs in functions called from application
2. **Avoid recursive triggers**: Can cause infinite loops
3. **Document trigger behavior**: Comment what and why
4. **Test thoroughly**: Including edge cases and bulk operations
5. **Monitor performance**: Triggers can slow down DML operations
6. **Use WHEN conditions**: Filter at trigger level, not in function
7. **Handle all cases**: Consider INSERT, UPDATE, DELETE scenarios
8. **Return appropriate values**: NEW for BEFORE, NULL for AFTER
9. **Log errors appropriately**: Use RAISE with proper severity

## Common Pitfalls

1. **Forgetting RETURN**: BEFORE triggers must return NEW/OLD/NULL
2. **Modifying OLD**: OLD is read-only, only NEW can be modified
3. **Trigger mutations**: Modifying the same table can cause issues
4. **Not handling NULL**: Check for NULL values in OLD/NEW
5. **Inefficient queries**: Triggers execute for every affected row
6. **Cascading triggers**: One trigger firing another can be hard to debug

## Summary

PostgreSQL triggers provide:
- **Automatic execution**: Code runs in response to data changes
- **Flexibility**: BEFORE, AFTER, INSTEAD OF at row or statement level
- **Data integrity**: Enforce complex business rules
- **Audit trails**: Track all changes automatically
- **Event triggers**: Monitor DDL operations

Use triggers wisely for automation, but prefer application logic for complex business rules.

## Next Steps

- Learn about [Stored Procedures and Functions](./17-stored-procedures-and-functions.md)
- Explore [Constraints](./08-constraints-and-keys.md) for declarative rules
- Study [Performance Optimization](./20-query-optimization.md)
- Practice [Transaction Management](./16-transactions-and-acid.md)
