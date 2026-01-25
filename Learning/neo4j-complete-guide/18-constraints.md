# Chapter 18: Constraints

## Learning Objectives
By the end of this chapter, you will:
- Understand all constraint types in Neo4j
- Implement data integrity with constraints
- Use constraints for schema enforcement
- Combine constraints with indexes
- Handle constraint violations gracefully

---

## 18.1 Understanding Constraints

### What Constraints Do

Constraints enforce data integrity rules at the database level:

1. **Uniqueness**: Prevent duplicate values
2. **Existence**: Require properties to be present
3. **Type**: Ensure property values are correct types
4. **Key**: Combine uniqueness and existence

### Constraint Benefits

- Data integrity guaranteed by the database
- Automatic index creation for unique constraints
- Clear schema documentation
- Early error detection

---

## 18.2 Node Property Uniqueness Constraints

### Creating Uniqueness Constraints

```cypher
// Single property uniqueness
CREATE CONSTRAINT customer_email_unique
FOR (c:Customer) REQUIRE c.email IS UNIQUE

// With IF NOT EXISTS
CREATE CONSTRAINT product_sku_unique IF NOT EXISTS
FOR (p:Product) REQUIRE p.sku IS UNIQUE

// Multiple unique constraints on same label
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE
CREATE CONSTRAINT user_username_unique FOR (u:User) REQUIRE u.username IS UNIQUE
```

### Composite Uniqueness

```cypher
// Composite unique constraint (combination must be unique)
CREATE CONSTRAINT employee_company_number 
FOR (e:Employee) REQUIRE (e.companyId, e.employeeNumber) IS UNIQUE

// Example: Each company has unique employee numbers
// Valid:
//   (companyId: 'C001', employeeNumber: 'E001')
//   (companyId: 'C002', employeeNumber: 'E001')  // Same number, different company
// Invalid:
//   (companyId: 'C001', employeeNumber: 'E001')  // Duplicate
```

### Uniqueness with NULL

```cypher
// NULL values are NOT considered equal
// Multiple nodes can have NULL for a unique property

CREATE CONSTRAINT person_ssn_unique FOR (p:Person) REQUIRE p.ssn IS UNIQUE

// These are all valid:
CREATE (:Person {name: 'Alice', ssn: '123-45-6789'})
CREATE (:Person {name: 'Bob', ssn: null})  // OK
CREATE (:Person {name: 'Charlie'})          // OK (no ssn property = null)
CREATE (:Person {name: 'Diana', ssn: null}) // OK (null != null)
```

---

## 18.3 Node Property Existence Constraints

### Creating Existence Constraints

```cypher
// Require property to exist
CREATE CONSTRAINT order_id_exists
FOR (o:Order) REQUIRE o.id IS NOT NULL

// Multiple existence constraints
CREATE CONSTRAINT person_name_exists FOR (p:Person) REQUIRE p.name IS NOT NULL
CREATE CONSTRAINT person_email_exists FOR (p:Person) REQUIRE p.email IS NOT NULL
```

### Existence vs Uniqueness

```cypher
// Existence only: Must have value, can be duplicate
CREATE CONSTRAINT product_name_exists FOR (p:Product) REQUIRE p.name IS NOT NULL

// Uniqueness only: Must be unique if present, can be null
CREATE CONSTRAINT product_sku_unique FOR (p:Product) REQUIRE p.sku IS UNIQUE

// Both: Must exist AND be unique (use NODE KEY)
CREATE CONSTRAINT product_sku_key FOR (p:Product) REQUIRE p.sku IS NODE KEY
```

---

## 18.4 Node Key Constraints

### Creating Node Keys

Node keys combine uniqueness AND existence:

```cypher
// Single property node key
CREATE CONSTRAINT customer_id_key
FOR (c:Customer) REQUIRE c.id IS NODE KEY

// Composite node key
CREATE CONSTRAINT order_item_key
FOR (oi:OrderItem) REQUIRE (oi.orderId, oi.productId) IS NODE KEY
```

### Node Key vs Unique + Exists

```cypher
// These are equivalent:
// Option 1: Node Key (preferred)
CREATE CONSTRAINT user_email_key FOR (u:User) REQUIRE u.email IS NODE KEY

// Option 2: Separate constraints
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE
CREATE CONSTRAINT user_email_exists FOR (u:User) REQUIRE u.email IS NOT NULL
```

---

## 18.5 Property Type Constraints

### Creating Type Constraints

```cypher
// Ensure property is specific type
CREATE CONSTRAINT person_age_type
FOR (p:Person) REQUIRE p.age IS :: INTEGER

// String type
CREATE CONSTRAINT person_name_type
FOR (p:Person) REQUIRE p.name IS :: STRING

// Boolean type
CREATE CONSTRAINT product_active_type
FOR (p:Product) REQUIRE p.active IS :: BOOLEAN

// Date type
CREATE CONSTRAINT order_date_type
FOR (o:Order) REQUIRE o.orderDate IS :: DATE

// List type
CREATE CONSTRAINT person_tags_type
FOR (p:Person) REQUIRE p.tags IS :: LIST<STRING>
```

### Available Types

```cypher
// Primitive types
IS :: BOOLEAN
IS :: STRING
IS :: INTEGER
IS :: FLOAT

// Temporal types
IS :: DATE
IS :: TIME
IS :: DATETIME
IS :: LOCALDATETIME
IS :: LOCALTIME
IS :: DURATION

// Spatial type
IS :: POINT

// Collection types
IS :: LIST<STRING>
IS :: LIST<INTEGER>
IS :: LIST<FLOAT>
IS :: LIST<BOOLEAN>
```

### Combining Type with Other Constraints

```cypher
// Type + Existence
CREATE CONSTRAINT person_age_typed_required
FOR (p:Person) REQUIRE p.age IS :: INTEGER
CREATE CONSTRAINT person_age_exists
FOR (p:Person) REQUIRE p.age IS NOT NULL

// Or use Node Key for unique + existence, plus type
CREATE CONSTRAINT product_sku_key FOR (p:Product) REQUIRE p.sku IS NODE KEY
CREATE CONSTRAINT product_sku_type FOR (p:Product) REQUIRE p.sku IS :: STRING
```

---

## 18.6 Relationship Constraints

### Relationship Property Uniqueness

```cypher
// Unique property on relationships
CREATE CONSTRAINT transaction_id_unique
FOR ()-[t:TRANSACTION]-() REQUIRE t.transactionId IS UNIQUE
```

### Relationship Property Existence

```cypher
// Required property on relationships
CREATE CONSTRAINT review_rating_exists
FOR ()-[r:REVIEWED]-() REQUIRE r.rating IS NOT NULL

// Multiple required properties
CREATE CONSTRAINT employment_dates
FOR ()-[e:EMPLOYED_BY]-() REQUIRE e.startDate IS NOT NULL
```

### Relationship Property Type

```cypher
// Type constraints on relationships
CREATE CONSTRAINT review_rating_type
FOR ()-[r:REVIEWED]-() REQUIRE r.rating IS :: INTEGER

CREATE CONSTRAINT knows_since_type
FOR ()-[k:KNOWS]-() REQUIRE k.since IS :: DATE
```

### Relationship Key (Neo4j 5.7+)

```cypher
// Relationship key constraint
CREATE CONSTRAINT transaction_key
FOR ()-[t:TRANSACTION]-() REQUIRE t.id IS RELATIONSHIP KEY
```

---

## 18.7 Managing Constraints

### Listing Constraints

```cypher
// Show all constraints
SHOW CONSTRAINTS

// With details
SHOW CONSTRAINTS YIELD name, type, entityType, labelsOrTypes, properties, ownedIndex

// Filter by type
SHOW CONSTRAINTS WHERE type = 'UNIQUENESS'
SHOW CONSTRAINTS WHERE type = 'NODE_KEY'
SHOW CONSTRAINTS WHERE entityType = 'RELATIONSHIP'
```

### Dropping Constraints

```cypher
// Drop by name
DROP CONSTRAINT customer_email_unique

// Drop if exists
DROP CONSTRAINT customer_email_unique IF EXISTS
```

### Constraint Naming

```cypher
// Good naming convention: <label>_<property>_<type>
CREATE CONSTRAINT customer_email_unique FOR (c:Customer) REQUIRE c.email IS UNIQUE
CREATE CONSTRAINT customer_id_key FOR (c:Customer) REQUIRE c.id IS NODE KEY
CREATE CONSTRAINT customer_name_exists FOR (c:Customer) REQUIRE c.name IS NOT NULL
CREATE CONSTRAINT order_total_type FOR (o:Order) REQUIRE o.total IS :: FLOAT
```

---

## 18.8 Handling Constraint Violations

### Violation Errors

```cypher
// Uniqueness violation
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE

CREATE (:User {email: 'alice@example.com'})
CREATE (:User {email: 'alice@example.com'})  // Error!
// Neo.ClientError.Schema.ConstraintValidationFailed

// Existence violation
CREATE CONSTRAINT order_id_exists FOR (o:Order) REQUIRE o.id IS NOT NULL

CREATE (:Order {total: 99.99})  // Error! Missing id
```

### Using MERGE to Avoid Duplicates

```cypher
// Instead of CREATE, use MERGE
MERGE (u:User {email: 'alice@example.com'})
ON CREATE SET u.createdAt = datetime()
ON MATCH SET u.lastSeen = datetime()
RETURN u

// MERGE uses the unique constraint's index for efficient lookup
```

### Handling Violations in Application Code

```python
from neo4j import GraphDatabase
from neo4j.exceptions import ConstraintError

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

def create_user(driver, email: str, name: str):
    with driver.session() as session:
        try:
            result = session.run("""
                CREATE (u:User {email: $email, name: $name, createdAt: datetime()})
                RETURN u
            """, email=email, name=name)
            return result.single()['u']
        except ConstraintError as e:
            if 'already exists' in str(e):
                print(f"User with email {email} already exists")
                # Option 1: Return existing user
                result = session.run(
                    "MATCH (u:User {email: $email}) RETURN u",
                    email=email
                )
                return result.single()['u']
            raise

def create_or_update_user(driver, email: str, name: str):
    """Use MERGE to handle duplicates gracefully."""
    with driver.session() as session:
        result = session.run("""
            MERGE (u:User {email: $email})
            ON CREATE SET u.name = $name, u.createdAt = datetime()
            ON MATCH SET u.name = $name, u.updatedAt = datetime()
            RETURN u, 
                   CASE WHEN u.createdAt = u.updatedAt OR u.updatedAt IS NULL 
                        THEN 'created' ELSE 'updated' END AS action
        """, email=email, name=name)
        record = result.single()
        return record['u'], record['action']

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    user, action = create_or_update_user(driver, "alice@example.com", "Alice")
    print(f"User {action}: {user['name']}")
```

---

## 18.9 Schema Design with Constraints

### Recommended Schema Pattern

```cypher
// 1. Create node key constraints for primary identifiers
CREATE CONSTRAINT customer_id_key FOR (c:Customer) REQUIRE c.id IS NODE KEY;
CREATE CONSTRAINT product_sku_key FOR (p:Product) REQUIRE p.sku IS NODE KEY;
CREATE CONSTRAINT order_id_key FOR (o:Order) REQUIRE o.id IS NODE KEY;

// 2. Create uniqueness for alternate keys
CREATE CONSTRAINT customer_email_unique FOR (c:Customer) REQUIRE c.email IS UNIQUE;

// 3. Create existence for required fields
CREATE CONSTRAINT customer_name_exists FOR (c:Customer) REQUIRE c.name IS NOT NULL;
CREATE CONSTRAINT product_name_exists FOR (p:Product) REQUIRE p.name IS NOT NULL;
CREATE CONSTRAINT order_date_exists FOR (o:Order) REQUIRE o.orderDate IS NOT NULL;

// 4. Create type constraints for data integrity
CREATE CONSTRAINT product_price_type FOR (p:Product) REQUIRE p.price IS :: FLOAT;
CREATE CONSTRAINT order_total_type FOR (o:Order) REQUIRE o.total IS :: FLOAT;
CREATE CONSTRAINT customer_active_type FOR (c:Customer) REQUIRE c.active IS :: BOOLEAN;

// 5. Relationship constraints
CREATE CONSTRAINT review_rating_exists FOR ()-[r:REVIEWED]-() REQUIRE r.rating IS NOT NULL;
CREATE CONSTRAINT review_rating_type FOR ()-[r:REVIEWED]-() REQUIRE r.rating IS :: INTEGER;
```

### Migration Strategy

```cypher
// Step 1: Check for violations before adding constraint
MATCH (c:Customer)
WHERE c.email IS NULL
RETURN count(c) AS customersWithoutEmail

// Step 2: Fix violations
MATCH (c:Customer)
WHERE c.email IS NULL
SET c.email = 'unknown_' + c.id + '@placeholder.com'

// Step 3: Create constraint
CREATE CONSTRAINT customer_email_exists FOR (c:Customer) REQUIRE c.email IS NOT NULL

// Step 4: Check for uniqueness violations
MATCH (c:Customer)
WITH c.email AS email, collect(c) AS customers
WHERE size(customers) > 1
RETURN email, size(customers) AS duplicateCount

// Step 5: Resolve duplicates, then add uniqueness
CREATE CONSTRAINT customer_email_unique FOR (c:Customer) REQUIRE c.email IS UNIQUE
```

---

## 18.10 Constraints and Indexes

### Automatic Index Creation

```cypher
// Unique constraints automatically create a backing index
CREATE CONSTRAINT person_email_unique FOR (p:Person) REQUIRE p.email IS UNIQUE

SHOW INDEXES
// Shows: person_email_unique index created

// This index is used for:
// - Enforcing uniqueness
// - Fast lookups on the constrained property
MATCH (p:Person {email: 'alice@example.com'})  // Uses index
RETURN p
```

### When to Add Additional Indexes

```cypher
// Constraint provides index for equality lookups
// But you might want additional indexes for:

// 1. Range queries on non-unique properties
CREATE INDEX product_price FOR (p:Product) ON (p.price)

// 2. Text operations
CREATE TEXT INDEX product_name_text FOR (p:Product) ON (p.name)

// 3. Composite queries not covered by constraint
CREATE INDEX customer_city_status FOR (c:Customer) ON (c.city, c.status)
```

---

## Summary

### Constraint Types

| Constraint | Syntax | Purpose |
|------------|--------|---------|
| Unique | `REQUIRE p.prop IS UNIQUE` | Prevent duplicates |
| Exists | `REQUIRE p.prop IS NOT NULL` | Require property |
| Node Key | `REQUIRE p.prop IS NODE KEY` | Unique + Exists |
| Type | `REQUIRE p.prop IS :: TYPE` | Enforce data type |
| Rel Unique | `REQUIRE r.prop IS UNIQUE` | Unique on relationship |
| Rel Exists | `REQUIRE r.prop IS NOT NULL` | Required on relationship |

### Key Commands

```cypher
-- Create constraints
CREATE CONSTRAINT name FOR (n:Label) REQUIRE n.prop IS UNIQUE
CREATE CONSTRAINT name FOR (n:Label) REQUIRE n.prop IS NOT NULL
CREATE CONSTRAINT name FOR (n:Label) REQUIRE n.prop IS NODE KEY
CREATE CONSTRAINT name FOR (n:Label) REQUIRE n.prop IS :: TYPE

-- Manage constraints
SHOW CONSTRAINTS
DROP CONSTRAINT name IF EXISTS

-- Handle duplicates
MERGE (n:Label {uniqueProp: value})
ON CREATE SET n.other = value
ON MATCH SET n.updated = datetime()
```

---

## Exercises

### Exercise 18.1: Basic Constraints
1. Create a node key constraint for User.email
2. Create existence constraints for User.name and User.createdAt
3. Test violations and handle them with MERGE

### Exercise 18.2: Type Constraints
1. Add type constraints for an Order node (total, quantity, date)
2. Attempt to insert invalid data and observe errors
3. Write a migration script to fix existing invalid data

### Exercise 18.3: Composite Constraints
1. Create a composite unique constraint (e.g., year + studentId for enrollment)
2. Create a composite node key
3. Test various duplicate scenarios

### Exercise 18.4: Schema Design
1. Design a complete schema for a library system
2. Include all appropriate constraints
3. Write migration scripts to add constraints to existing data

---

**Next Chapter: [Chapter 19: Query Optimization](19-query-optimization.md)**
