# Stored Procedures and Functions

## Overview

PostgreSQL supports both stored procedures and functions, allowing you to encapsulate business logic, improve performance, and maintain consistency. Functions return values and can be used in SQL expressions, while procedures (introduced in PostgreSQL 11) support transaction control and don't return values directly.

## Table of Contents
- [Functions vs Procedures](#functions-vs-procedures)
- [Creating Functions](#creating-functions)
- [Function Languages](#function-languages)
- [Stored Procedures](#stored-procedures)
- [Parameters and Return Types](#parameters-and-return-types)
- [Control Structures](#control-structures)
- [Error Handling](#error-handling)
- [Performance and Best Practices](#performance-and-best-practices)

## Functions vs Procedures

### Key Differences

| Feature | Functions | Procedures |
|---------|-----------|------------|
| **Returns** | Must return a value | No return value |
| **Usage** | Can be used in SELECT | Called with CALL |
| **Transactions** | Cannot control transactions | Can COMMIT/ROLLBACK |
| **Since** | All PostgreSQL versions | PostgreSQL 11+ |

```sql
-- Function: Returns a value
CREATE FUNCTION get_customer_count() RETURNS INTEGER AS $$
    SELECT COUNT(*) FROM customers;
$$ LANGUAGE SQL;

-- Use in query
SELECT get_customer_count();

-- Procedure: Performs actions
CREATE PROCEDURE archive_old_orders() AS $$
BEGIN
    INSERT INTO archived_orders SELECT * FROM orders WHERE order_date < '2020-01-01';
    DELETE FROM orders WHERE order_date < '2020-01-01';
    COMMIT;  -- Procedures can control transactions
END;
$$ LANGUAGE plpgsql;

-- Call procedure
CALL archive_old_orders();
```

## Creating Functions

### Basic Function Syntax

```sql
-- Simple SQL function
CREATE FUNCTION add_numbers(a INTEGER, b INTEGER) 
RETURNS INTEGER AS $$
    SELECT a + b;
$$ LANGUAGE SQL;

-- Usage
SELECT add_numbers(5, 3);  -- Returns 8

-- Function with default parameters
CREATE FUNCTION calculate_discount(
    amount NUMERIC,
    discount_pct NUMERIC DEFAULT 10
) RETURNS NUMERIC AS $$
    SELECT amount * (1 - discount_pct / 100.0);
$$ LANGUAGE SQL;

SELECT calculate_discount(100);      -- Uses default 10%
SELECT calculate_discount(100, 20);  -- Uses 20%

-- Function with named parameters
CREATE FUNCTION format_name(
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT DEFAULT NULL
) RETURNS TEXT AS $$
    SELECT 
        CASE 
            WHEN middle_name IS NOT NULL 
            THEN first_name || ' ' || middle_name || ' ' || last_name
            ELSE first_name || ' ' || last_name
        END;
$$ LANGUAGE SQL;

SELECT format_name(first_name => 'John', last_name => 'Doe');
SELECT format_name('Jane', 'Smith', 'Marie');
```

### PL/pgSQL Functions

More powerful with procedural features:

```sql
-- Basic PL/pgSQL function
CREATE OR REPLACE FUNCTION calculate_bonus(
    employee_id INTEGER
) RETURNS NUMERIC AS $$
DECLARE
    emp_salary NUMERIC;
    emp_performance NUMERIC;
    bonus NUMERIC;
BEGIN
    -- Get employee data
    SELECT salary, performance_score 
    INTO emp_salary, emp_performance
    FROM employees
    WHERE employees.employee_id = calculate_bonus.employee_id;
    
    -- Calculate bonus based on performance
    IF emp_performance >= 9 THEN
        bonus := emp_salary * 0.15;
    ELSIF emp_performance >= 7 THEN
        bonus := emp_salary * 0.10;
    ELSIF emp_performance >= 5 THEN
        bonus := emp_salary * 0.05;
    ELSE
        bonus := 0;
    END IF;
    
    RETURN bonus;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT 
    employee_name,
    salary,
    calculate_bonus(employee_id) as bonus
FROM employees;
```

### Functions Returning Multiple Columns

```sql
-- Return composite type
CREATE TYPE customer_stats AS (
    total_orders INTEGER,
    total_spent NUMERIC,
    avg_order_value NUMERIC,
    last_order_date DATE
);

CREATE FUNCTION get_customer_stats(cust_id INTEGER)
RETURNS customer_stats AS $$
    SELECT 
        COUNT(*)::INTEGER,
        SUM(total_amount),
        AVG(total_amount),
        MAX(order_date)::DATE
    FROM orders
    WHERE customer_id = cust_id;
$$ LANGUAGE SQL;

-- Usage
SELECT * FROM get_customer_stats(100);
SELECT (get_customer_stats(100)).total_orders;

-- Return TABLE
CREATE FUNCTION get_top_customers(limit_count INTEGER DEFAULT 10)
RETURNS TABLE(
    customer_id INTEGER,
    customer_name TEXT,
    total_spent NUMERIC,
    order_count BIGINT
) AS $$
    SELECT 
        c.customer_id,
        c.customer_name,
        SUM(o.total_amount) as total_spent,
        COUNT(o.order_id) as order_count
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
    ORDER BY total_spent DESC
    LIMIT limit_count;
$$ LANGUAGE SQL;

-- Usage
SELECT * FROM get_top_customers(5);
```

### Functions Returning Sets

```sql
-- RETURNS SETOF
CREATE FUNCTION get_employee_hierarchy(manager_id INTEGER)
RETURNS SETOF employees AS $$
    WITH RECURSIVE subordinates AS (
        SELECT * FROM employees WHERE employees.manager_id = get_employee_hierarchy.manager_id
        UNION ALL
        SELECT e.* FROM employees e
        JOIN subordinates s ON e.manager_id = s.employee_id
    )
    SELECT * FROM subordinates;
$$ LANGUAGE SQL;

-- Returns multiple rows
SELECT * FROM get_employee_hierarchy(1);

-- Generator function
CREATE FUNCTION generate_fibonacci(n INTEGER)
RETURNS SETOF INTEGER AS $$
DECLARE
    a INTEGER := 0;
    b INTEGER := 1;
    temp INTEGER;
    i INTEGER := 0;
BEGIN
    WHILE i < n LOOP
        RETURN NEXT a;
        temp := a + b;
        a := b;
        b := temp;
        i := i + 1;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM generate_fibonacci(10);
```

## Function Languages

### SQL Functions

Simplest, fastest for simple operations:

```sql
CREATE FUNCTION get_full_name(first_name TEXT, last_name TEXT)
RETURNS TEXT AS $$
    SELECT first_name || ' ' || last_name;
$$ LANGUAGE SQL IMMUTABLE;

-- Inline SQL functions
CREATE FUNCTION get_order_total(order_id INTEGER)
RETURNS NUMERIC AS $$
    SELECT SUM(quantity * unit_price)
    FROM order_items
    WHERE order_items.order_id = get_order_total.order_id;
$$ LANGUAGE SQL STABLE;
```

### PL/pgSQL Functions

Full procedural language:

```sql
CREATE OR REPLACE FUNCTION process_order(
    p_customer_id INTEGER,
    p_product_id INTEGER,
    p_quantity INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_order_id INTEGER;
    v_price NUMERIC;
    v_stock INTEGER;
BEGIN
    -- Check stock
    SELECT stock_quantity, price INTO v_stock, v_price
    FROM products
    WHERE product_id = p_product_id;
    
    IF v_stock < p_quantity THEN
        RAISE EXCEPTION 'Insufficient stock. Available: %, Requested: %', v_stock, p_quantity;
    END IF;
    
    -- Create order
    INSERT INTO orders (customer_id, order_date, total_amount)
    VALUES (p_customer_id, CURRENT_DATE, v_price * p_quantity)
    RETURNING order_id INTO v_order_id;
    
    -- Add order item
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES (v_order_id, p_product_id, p_quantity, v_price);
    
    -- Update stock
    UPDATE products
    SET stock_quantity = stock_quantity - p_quantity
    WHERE product_id = p_product_id;
    
    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql;
```

### Python Functions (PL/Python)

```sql
-- Install extension
CREATE EXTENSION plpython3u;

-- Python function
CREATE FUNCTION calculate_statistics(numbers NUMERIC[])
RETURNS TABLE(mean NUMERIC, median NUMERIC, std_dev NUMERIC) AS $$
    import statistics
    nums = [float(n) for n in numbers]
    return [(
        statistics.mean(nums),
        statistics.median(nums),
        statistics.stdev(nums)
    )]
$$ LANGUAGE plpython3u;

-- Usage
SELECT * FROM calculate_statistics(ARRAY[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
```

### JavaScript Functions (PL/V8)

```sql
-- Install extension
CREATE EXTENSION plv8;

-- JavaScript function
CREATE FUNCTION parse_json_data(json_text TEXT)
RETURNS TABLE(key TEXT, value TEXT) AS $$
    var obj = JSON.parse(json_text);
    var result = [];
    for (var k in obj) {
        result.push({key: k, value: String(obj[k])});
    }
    return result;
$$ LANGUAGE plv8;
```

## Stored Procedures

### Basic Procedure Syntax

```sql
-- Simple procedure
CREATE PROCEDURE update_customer_tier() AS $$
BEGIN
    UPDATE customers
    SET customer_tier = CASE
        WHEN total_purchases > 10000 THEN 'VIP'
        WHEN total_purchases > 5000 THEN 'Premium'
        ELSE 'Regular'
    END;
    
    -- Log the update
    INSERT INTO audit_log (action, timestamp)
    VALUES ('Customer tiers updated', CURRENT_TIMESTAMP);
END;
$$ LANGUAGE plpgsql;

-- Call procedure
CALL update_customer_tier();
```

### Procedures with Parameters

```sql
-- Procedure with IN parameters
CREATE PROCEDURE give_raise(
    emp_id INTEGER,
    raise_percentage NUMERIC
) AS $$
BEGIN
    UPDATE employees
    SET salary = salary * (1 + raise_percentage / 100)
    WHERE employee_id = emp_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Employee % not found', emp_id;
    END IF;
    
    -- Log change
    INSERT INTO salary_changes (employee_id, change_date, change_pct)
    VALUES (emp_id, CURRENT_DATE, raise_percentage);
END;
$$ LANGUAGE plpgsql;

CALL give_raise(123, 10);

-- Procedure with INOUT parameters
CREATE PROCEDURE calculate_tax(
    INOUT amount NUMERIC,
    tax_rate NUMERIC DEFAULT 0.10
) AS $$
BEGIN
    amount := amount * (1 + tax_rate);
END;
$$ LANGUAGE plpgsql;

-- Usage with variable
DO $$
DECLARE
    order_total NUMERIC := 100;
BEGIN
    CALL calculate_tax(order_total, 0.15);
    RAISE NOTICE 'Total with tax: %', order_total;
END $$;
```

### Transaction Control in Procedures

```sql
CREATE PROCEDURE batch_process_orders() AS $$
DECLARE
    v_order RECORD;
    v_processed INTEGER := 0;
    v_failed INTEGER := 0;
BEGIN
    FOR v_order IN SELECT * FROM pending_orders LOOP
        BEGIN
            -- Process each order in its own transaction
            INSERT INTO processed_orders SELECT * FROM pending_orders 
            WHERE order_id = v_order.order_id;
            
            DELETE FROM pending_orders WHERE order_id = v_order.order_id;
            
            v_processed := v_processed + 1;
            COMMIT;  -- Commit each successful order
            
        EXCEPTION WHEN OTHERS THEN
            -- If one order fails, rollback and continue
            ROLLBACK;
            v_failed := v_failed + 1;
            
            INSERT INTO error_log (order_id, error_message, error_time)
            VALUES (v_order.order_id, SQLERRM, CURRENT_TIMESTAMP);
            COMMIT;  -- Commit error log
        END;
    END LOOP;
    
    RAISE NOTICE 'Processed: %, Failed: %', v_processed, v_failed;
END;
$$ LANGUAGE plpgsql;
```

## Parameters and Return Types

### Parameter Modes

```sql
-- IN parameters (default)
CREATE FUNCTION calc_discount(IN price NUMERIC, IN discount NUMERIC)
RETURNS NUMERIC AS $$
    SELECT price * (1 - discount / 100);
$$ LANGUAGE SQL;

-- OUT parameters
CREATE FUNCTION get_stats(
    IN dept_id INTEGER,
    OUT emp_count INTEGER,
    OUT avg_salary NUMERIC,
    OUT total_salary NUMERIC
) AS $$
    SELECT 
        COUNT(*)::INTEGER,
        AVG(salary),
        SUM(salary)
    FROM employees
    WHERE department_id = dept_id;
$$ LANGUAGE SQL;

SELECT * FROM get_stats(10);

-- INOUT parameters
CREATE FUNCTION increment(INOUT x INTEGER) AS $$
BEGIN
    x := x + 1;
END;
$$ LANGUAGE plpgsql;

-- Variadic parameters (variable number)
CREATE FUNCTION sum_numbers(VARIADIC numbers NUMERIC[])
RETURNS NUMERIC AS $$
    SELECT SUM(n) FROM UNNEST(numbers) AS n;
$$ LANGUAGE SQL;

SELECT sum_numbers(1, 2, 3, 4, 5);  -- Pass any number of arguments
```

### Complex Return Types

```sql
-- Return JSON
CREATE FUNCTION get_customer_json(cust_id INTEGER)
RETURNS JSON AS $$
    SELECT json_build_object(
        'customer_id', c.customer_id,
        'name', c.customer_name,
        'orders', (
            SELECT json_agg(json_build_object(
                'order_id', o.order_id,
                'date', o.order_date,
                'total', o.total_amount
            ))
            FROM orders o
            WHERE o.customer_id = c.customer_id
        )
    )
    FROM customers c
    WHERE c.customer_id = cust_id;
$$ LANGUAGE SQL;

-- Return array
CREATE FUNCTION get_employee_ids(dept_id INTEGER)
RETURNS INTEGER[] AS $$
    SELECT ARRAY_AGG(employee_id)
    FROM employees
    WHERE department_id = dept_id;
$$ LANGUAGE SQL;

-- Return custom type
CREATE TYPE address_type AS (
    street TEXT,
    city TEXT,
    state TEXT,
    zip TEXT
);

CREATE FUNCTION parse_address(address_text TEXT)
RETURNS address_type AS $$
DECLARE
    result address_type;
BEGIN
    -- Parsing logic here
    result.street := split_part(address_text, ',', 1);
    result.city := split_part(address_text, ',', 2);
    -- ... more parsing
    RETURN result;
END;
$$ LANGUAGE plpgsql;
```

## Control Structures

### IF Statements

```sql
CREATE FUNCTION get_grade(score INTEGER)
RETURNS CHAR(1) AS $$
BEGIN
    IF score >= 90 THEN
        RETURN 'A';
    ELSIF score >= 80 THEN
        RETURN 'B';
    ELSIF score >= 70 THEN
        RETURN 'C';
    ELSIF score >= 60 THEN
        RETURN 'D';
    ELSE
        RETURN 'F';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### CASE Statements

```sql
CREATE FUNCTION categorize_amount(amount NUMERIC)
RETURNS TEXT AS $$
BEGIN
    RETURN CASE
        WHEN amount < 0 THEN 'Negative'
        WHEN amount = 0 THEN 'Zero'
        WHEN amount < 100 THEN 'Small'
        WHEN amount < 1000 THEN 'Medium'
        ELSE 'Large'
    END;
END;
$$ LANGUAGE plpgsql;
```

### Loops

```sql
-- Simple LOOP
CREATE FUNCTION count_to_n(n INTEGER)
RETURNS VOID AS $$
DECLARE
    i INTEGER := 1;
BEGIN
    LOOP
        RAISE NOTICE 'Count: %', i;
        i := i + 1;
        EXIT WHEN i > n;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- WHILE loop
CREATE FUNCTION factorial(n INTEGER)
RETURNS BIGINT AS $$
DECLARE
    result BIGINT := 1;
    i INTEGER := 1;
BEGIN
    WHILE i <= n LOOP
        result := result * i;
        i := i + 1;
    END LOOP;
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- FOR loop (integer range)
CREATE FUNCTION sum_range(start_num INTEGER, end_num INTEGER)
RETURNS BIGINT AS $$
DECLARE
    total BIGINT := 0;
    i INTEGER;
BEGIN
    FOR i IN start_num..end_num LOOP
        total := total + i;
    END LOOP;
    RETURN total;
END;
$$ LANGUAGE plpgsql;

-- FOR loop (query results)
CREATE FUNCTION update_order_totals()
RETURNS INTEGER AS $$
DECLARE
    v_order RECORD;
    v_count INTEGER := 0;
BEGIN
    FOR v_order IN 
        SELECT order_id FROM orders WHERE total_amount IS NULL
    LOOP
        UPDATE orders
        SET total_amount = (
            SELECT SUM(quantity * unit_price)
            FROM order_items
            WHERE order_id = v_order.order_id
        )
        WHERE order_id = v_order.order_id;
        
        v_count := v_count + 1;
    END LOOP;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- FOREACH loop (arrays)
CREATE FUNCTION sum_array(numbers INTEGER[])
RETURNS INTEGER AS $$
DECLARE
    total INTEGER := 0;
    num INTEGER;
BEGIN
    FOREACH num IN ARRAY numbers LOOP
        total := total + num;
    END LOOP;
    RETURN total;
END;
$$ LANGUAGE plpgsql;
```

### CONTINUE and EXIT

```sql
CREATE FUNCTION process_even_numbers(max_num INTEGER)
RETURNS SETOF INTEGER AS $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN 1..max_num LOOP
        -- Skip odd numbers
        CONTINUE WHEN i % 2 = 1;
        
        -- Exit at 100
        EXIT WHEN i > 100;
        
        RETURN NEXT i;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;
```

## Error Handling

### RAISE Statements

```sql
CREATE FUNCTION validate_age(age INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    IF age < 0 THEN
        RAISE EXCEPTION 'Age cannot be negative: %', age;
    ELSIF age < 18 THEN
        RAISE WARNING 'Age % is below 18', age;
    END IF;
    
    RAISE NOTICE 'Age validation passed for age %', age;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Different severity levels
RAISE DEBUG 'Debug message';
RAISE LOG 'Log message';
RAISE INFO 'Info message';
RAISE NOTICE 'Notice message';
RAISE WARNING 'Warning message';
RAISE EXCEPTION 'Error message';
```

### Exception Handling

```sql
CREATE FUNCTION safe_divide(numerator NUMERIC, denominator NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN numerator / denominator;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE WARNING 'Division by zero attempted';
        RETURN NULL;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Unexpected error: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Multiple exception types
CREATE FUNCTION process_payment(amount NUMERIC, account_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    current_balance NUMERIC;
BEGIN
    SELECT balance INTO STRICT current_balance
    FROM accounts WHERE id = account_id;
    
    IF current_balance < amount THEN
        RAISE EXCEPTION 'Insufficient funds' USING ERRCODE = '50001';
    END IF;
    
    UPDATE accounts SET balance = balance - amount
    WHERE id = account_id;
    
    RETURN TRUE;
    
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE EXCEPTION 'Account % not found', account_id;
    WHEN TOO_MANY_ROWS THEN
        RAISE EXCEPTION 'Multiple accounts found with id %', account_id;
    WHEN SQLSTATE '50001' THEN
        RAISE WARNING 'Insufficient funds in account %', account_id;
        RETURN FALSE;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Payment processing failed: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Capture error details
CREATE FUNCTION handle_errors()
RETURNS VOID AS $$
BEGIN
    -- Some risky operation
    PERFORM * FROM non_existent_table;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error Code: %', SQLSTATE;
        RAISE NOTICE 'Error Message: %', SQLERRM;
        RAISE NOTICE 'Error Detail: %', PG_EXCEPTION_DETAIL;
        RAISE NOTICE 'Error Hint: %', PG_EXCEPTION_HINT;
        RAISE NOTICE 'Error Context: %', PG_EXCEPTION_CONTEXT;
END;
$$ LANGUAGE plpgsql;
```

## Performance and Best Practices

### Function Volatility

```sql
-- IMMUTABLE: Always returns same result for same inputs
CREATE FUNCTION add(a INTEGER, b INTEGER)
RETURNS INTEGER AS $$
    SELECT a + b;
$$ LANGUAGE SQL IMMUTABLE;

-- STABLE: Same result within single query
CREATE FUNCTION get_current_user_id()
RETURNS INTEGER AS $$
    SELECT id FROM users WHERE username = current_user;
$$ LANGUAGE SQL STABLE;

-- VOLATILE: Can change (default)
CREATE FUNCTION random_number()
RETURNS DOUBLE PRECISION AS $$
    SELECT random();
$$ LANGUAGE SQL VOLATILE;
```

### Function Cost Hints

```sql
-- Set execution cost (default: 100 for SQL, 100 for PL/pgSQL)
CREATE FUNCTION expensive_calculation(n INTEGER)
RETURNS BIGINT AS $$
    -- Complex calculation
    SELECT SUM(i) FROM generate_series(1, n) i;
$$ LANGUAGE SQL
IMMUTABLE
COST 1000;  -- Hint to planner this is expensive

-- Set estimated rows returned
CREATE FUNCTION get_large_dataset()
RETURNS SETOF customers AS $$
    SELECT * FROM customers;
$$ LANGUAGE SQL
STABLE
ROWS 10000;  -- Hint about result size
```

### Inlining SQL Functions

```sql
-- Simple SQL functions are automatically inlined
CREATE FUNCTION is_active(status TEXT)
RETURNS BOOLEAN AS $$
    SELECT status = 'active';
$$ LANGUAGE SQL IMMUTABLE;

-- This query will inline the function
SELECT * FROM users WHERE is_active(status);
-- Equivalent to: SELECT * FROM users WHERE status = 'active';
```

### Security

```sql
-- SECURITY DEFINER: Execute with creator's privileges
CREATE FUNCTION get_salary_total()
RETURNS NUMERIC AS $$
    SELECT SUM(salary) FROM employees;
$$ LANGUAGE SQL
SECURITY DEFINER;  -- Runs as function owner

-- SECURITY INVOKER: Execute with caller's privileges (default)
CREATE FUNCTION get_my_orders()
RETURNS SETOF orders AS $$
    SELECT * FROM orders WHERE customer_id = get_current_customer_id();
$$ LANGUAGE SQL
SECURITY INVOKER;  -- Runs as caller

-- Set search_path for security
CREATE FUNCTION secure_function()
RETURNS TEXT AS $$
    SELECT 'Secure';
$$ LANGUAGE SQL
SECURITY DEFINER
SET search_path = public, pg_temp;  -- Prevent injection
```

### Best Practices

1. **Use appropriate language**: SQL for simple queries, PL/pgSQL for complex logic
2. **Set volatility correctly**: Enables optimization
3. **Handle exceptions**: Gracefully deal with errors
4. **Use STRICT**: Function returns NULL if any input is NULL
5. **Document functions**: Use COMMENT ON
6. **Version control**: Keep function definitions in migration scripts
7. **Test thoroughly**: Unit test your functions

```sql
-- Example with best practices
CREATE OR REPLACE FUNCTION calculate_order_total(
    order_id INTEGER
)
RETURNS NUMERIC AS $$
    SELECT COALESCE(SUM(quantity * unit_price), 0)
    FROM order_items
    WHERE order_items.order_id = calculate_order_total.order_id;
$$ 
LANGUAGE SQL
STABLE  -- Same result within query
STRICT  -- Returns NULL for NULL input
PARALLEL SAFE  -- Can be parallelized
COST 50;  -- Lower cost than default

COMMENT ON FUNCTION calculate_order_total(INTEGER) IS 
'Calculates the total amount for an order by summing all order items';
```

## Common Pitfalls

1. **Not setting volatility**: Leads to missed optimizations
2. **Forgetting exception handling**: Unhandled errors abort transactions
3. **Using SELECT instead of PERFORM**: In PL/pgSQL, use PERFORM when you don't need results
4. **SQL injection in dynamic SQL**: Always use parameters
5. **Not using STRICT**: Can lead to unexpected NULL handling

```sql
-- BAD: SQL injection risk
CREATE FUNCTION bad_search(table_name TEXT, search_term TEXT)
RETURNS SETOF RECORD AS $$
BEGIN
    RETURN QUERY EXECUTE 'SELECT * FROM ' || table_name || 
        ' WHERE name = ''' || search_term || '''';
END;
$$ LANGUAGE plpgsql;

-- GOOD: Use parameters
CREATE FUNCTION good_search(table_name TEXT, search_term TEXT)
RETURNS SETOF RECORD AS $$
BEGIN
    RETURN QUERY EXECUTE 
        'SELECT * FROM ' || quote_ident(table_name) || 
        ' WHERE name = $1'
    USING search_term;
END;
$$ LANGUAGE plpgsql;
```

## Summary

PostgreSQL stored procedures and functions provide:
- **Functions**: Return values, can be used in SQL expressions
- **Procedures**: Support transaction control, called with CALL
- **Multiple languages**: SQL, PL/pgSQL, Python, JavaScript, and more
- **Rich control structures**: Loops, conditionals, exception handling
- **Performance options**: Volatility, cost hints, inlining

Use them to encapsulate business logic, improve code reuse, and enhance performance.

## Next Steps

- Learn about [Triggers](./18-triggers.md) to automatically execute functions
- Explore [Query Optimization](./20-query-optimization.md) for performance
- Study [Transaction Management](./16-transactions-and-acid.md)
- Practice [Error Handling Patterns](./52-troubleshooting-guide.md)
