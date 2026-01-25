# Chapter 20: Importing Data

## Learning Objectives
By the end of this chapter, you will:
- Import data from CSV files
- Handle large-scale data imports
- Transform data during import
- Create relationships from imported data
- Use batch processing for performance

---

## 20.1 LOAD CSV Basics

### Simple CSV Import

```cypher
// products.csv
// sku,name,price,category
// P001,Laptop,999.99,Electronics
// P002,Headphones,149.99,Electronics

LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
CREATE (:Product {
    sku: row.sku,
    name: row.name,
    price: toFloat(row.price),
    category: row.category
})
```

### CSV Location Options

```cypher
// From Neo4j import directory (default)
LOAD CSV FROM 'file:///data.csv' AS row

// From HTTP URL
LOAD CSV FROM 'https://example.com/data.csv' AS row

// From HTTPS
LOAD CSV FROM 'https://raw.githubusercontent.com/user/repo/main/data.csv' AS row
```

### CSV Options

```cypher
// With headers (access by column name)
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
RETURN row.columnName

// Without headers (access by index)
LOAD CSV FROM 'file:///data.csv' AS row
RETURN row[0], row[1], row[2]

// Custom field delimiter
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
FIELDTERMINATOR ';'
CREATE (:Node {prop: row.column})

// Handle quoted fields with different quote character
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
FIELDTERMINATOR ',' QUOTESEPARATOR "'"
RETURN row
```

---

## 20.2 Data Type Conversion

### Type Conversion Functions

```cypher
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
CREATE (:Product {
    // String (default)
    name: row.name,
    
    // Integer
    quantity: toInteger(row.quantity),
    
    // Float
    price: toFloat(row.price),
    
    // Boolean
    active: toBoolean(row.active),  // 'true'/'false' strings
    
    // Date
    createdDate: date(row.createdDate),  // 'YYYY-MM-DD' format
    
    // DateTime
    timestamp: datetime(row.timestamp),  // ISO 8601 format
    
    // List from delimited string
    tags: split(row.tags, '|')
})
```

### Handling NULL Values

```cypher
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CREATE (:Product {
    sku: row.sku,
    name: row.name,
    // Handle empty strings as null
    description: CASE WHEN row.description = '' THEN null ELSE row.description END,
    // Or use coalesce for default value
    category: coalesce(nullif(row.category, ''), 'Uncategorized')
})
```

### Date Parsing

```cypher
// Various date formats
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CREATE (:Event {
    // Standard format: YYYY-MM-DD
    date1: date(row.isoDate),
    
    // Custom format parsing
    date2: date(apoc.date.parse(row.usDate, 'ms', 'MM/dd/yyyy')),
    
    // Datetime with timezone
    timestamp: datetime(row.timestamp)
})
```

---

## 20.3 Creating Relationships During Import

### Method 1: Two-Pass Import

```cypher
// Pass 1: Create nodes
LOAD CSV WITH HEADERS FROM 'file:///customers.csv' AS row
CREATE (:Customer {
    id: row.customerId,
    name: row.name,
    email: row.email
})

// Create index for relationship creation
CREATE INDEX customer_id FOR (c:Customer) ON (c.id)

// Pass 2: Create relationships from orders
LOAD CSV WITH HEADERS FROM 'file:///orders.csv' AS row
MATCH (c:Customer {id: row.customerId})
CREATE (c)-[:PLACED]->(:Order {
    id: row.orderId,
    total: toFloat(row.total),
    orderDate: date(row.orderDate)
})
```

### Method 2: MERGE for Safety

```cypher
// Safely create nodes and relationships
LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row
MERGE (a:Person {id: row.personId})
ON CREATE SET a.name = row.personName
MERGE (b:Company {id: row.companyId})
ON CREATE SET b.name = row.companyName
MERGE (a)-[:WORKS_FOR]->(b)
```

### Method 3: Relationship Properties

```cypher
// orders_products.csv
// orderId,productId,quantity,unitPrice
LOAD CSV WITH HEADERS FROM 'file:///order_items.csv' AS row
MATCH (o:Order {id: row.orderId})
MATCH (p:Product {id: row.productId})
CREATE (o)-[:CONTAINS {
    quantity: toInteger(row.quantity),
    unitPrice: toFloat(row.unitPrice)
}]->(p)
```

---

## 20.4 Large-Scale Imports

### Using CALL IN TRANSACTIONS

```cypher
// Import in batches of 1000 rows
LOAD CSV WITH HEADERS FROM 'file:///large_file.csv' AS row
CALL {
    WITH row
    CREATE (:Product {
        sku: row.sku,
        name: row.name,
        price: toFloat(row.price)
    })
} IN TRANSACTIONS OF 1000 ROWS
```

### Progress Monitoring

```cypher
// With reporting
LOAD CSV WITH HEADERS FROM 'file:///large_file.csv' AS row
CALL {
    WITH row
    CREATE (:Product {
        sku: row.sku,
        name: row.name
    })
} IN TRANSACTIONS OF 10000 ROWS
ON ERROR CONTINUE
REPORT STATUS AFTER 10000 ROWS
```

### Periodic Commit (Legacy)

```cypher
// Older approach (use CALL IN TRANSACTIONS instead)
:auto USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CREATE (:Node {prop: row.prop})
```

---

## 20.5 Conditional Import Logic

### CASE Statements

```cypher
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
CREATE (p:Product {
    sku: row.sku,
    name: row.name,
    priceCategory: CASE 
        WHEN toFloat(row.price) < 50 THEN 'Budget'
        WHEN toFloat(row.price) < 200 THEN 'Mid-Range'
        ELSE 'Premium'
    END
})
```

### Multiple Labels Based on Data

```cypher
LOAD CSV WITH HEADERS FROM 'file:///users.csv' AS row
CALL {
    WITH row
    WITH row, 
         CASE row.role 
             WHEN 'admin' THEN ['User', 'Admin']
             WHEN 'moderator' THEN ['User', 'Moderator']
             ELSE ['User']
         END AS labels
    CALL apoc.create.node(labels, {
        id: row.id,
        name: row.name,
        email: row.email
    }) YIELD node
    RETURN node
}
RETURN count(*)
```

### Filter Rows During Import

```cypher
// Only import active products
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
WITH row WHERE row.status = 'active'
CREATE (:Product {
    sku: row.sku,
    name: row.name
})

// Skip rows with missing data
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
WITH row WHERE row.sku IS NOT NULL AND row.name IS NOT NULL
CREATE (:Product {
    sku: row.sku,
    name: row.name
})
```

---

## 20.6 Import from Multiple Files

### Sequential Import

```cypher
// Step 1: Import customers
LOAD CSV WITH HEADERS FROM 'file:///customers.csv' AS row
CALL {
    WITH row
    CREATE (:Customer {id: row.id, name: row.name, email: row.email})
} IN TRANSACTIONS OF 1000 ROWS;

// Step 2: Create index
CREATE INDEX customer_id FOR (c:Customer) ON (c.id);

// Step 3: Import products  
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
CALL {
    WITH row
    CREATE (:Product {sku: row.sku, name: row.name, price: toFloat(row.price)})
} IN TRANSACTIONS OF 1000 ROWS;

// Step 4: Create index
CREATE INDEX product_sku FOR (p:Product) ON (p.sku);

// Step 5: Import orders and relationships
LOAD CSV WITH HEADERS FROM 'file:///orders.csv' AS row
CALL {
    WITH row
    MATCH (c:Customer {id: row.customerId})
    CREATE (c)-[:PLACED]->(:Order {id: row.id, total: toFloat(row.total)})
} IN TRANSACTIONS OF 1000 ROWS;
```

### Dynamic File Names with APOC

```cypher
// Import from multiple files matching pattern
CALL apoc.periodic.iterate(
    "CALL apoc.load.directory('*.csv') YIELD value RETURN value AS file",
    "CALL apoc.load.csv(file) YIELD map
     CREATE (:Data {props: map})",
    {batchSize: 1000}
)
```

---

## 20.7 Handling Errors

### Error Handling Strategies

```cypher
// Continue on error
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL {
    WITH row
    CREATE (:Product {
        sku: row.sku,
        price: toFloat(row.price)  // May fail on invalid data
    })
} IN TRANSACTIONS OF 1000 ROWS
ON ERROR CONTINUE

// Fail on first error (default)
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL {
    WITH row
    CREATE (:Product {sku: row.sku})
} IN TRANSACTIONS OF 1000 ROWS
ON ERROR FAIL

// Break on error but keep previous batches
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL {
    WITH row
    CREATE (:Product {sku: row.sku})
} IN TRANSACTIONS OF 1000 ROWS
ON ERROR BREAK
```

### Validation Before Import

```cypher
// Check for issues first
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
WITH row WHERE row.price IS NULL OR NOT toFloat(row.price) >= 0
RETURN row.sku AS invalidSku, row.price AS invalidPrice
LIMIT 100

// Then import if no issues
LOAD CSV WITH HEADERS FROM 'file:///products.csv' AS row
WITH row WHERE toFloat(row.price) >= 0
CREATE (:Product {sku: row.sku, price: toFloat(row.price)})
```

---

## 20.8 JSON Import with APOC

### Load JSON from File

```cypher
// Simple JSON array
// [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
CALL apoc.load.json('file:///people.json') YIELD value
CREATE (:Person {name: value.name, age: value.age})

// Nested JSON
// {"company": "Acme", "employees": [{"name": "Alice"}, {"name": "Bob"}]}
CALL apoc.load.json('file:///company.json') YIELD value
CREATE (c:Company {name: value.company})
WITH c, value
UNWIND value.employees AS emp
CREATE (e:Employee {name: emp.name})
CREATE (e)-[:WORKS_FOR]->(c)
```

### JSON from URL

```cypher
// Load from REST API
CALL apoc.load.json('https://api.example.com/products') YIELD value
CREATE (:Product {
    id: value.id,
    name: value.name,
    price: value.price
})
```

---

## 20.9 Python Import Script

```python
from neo4j import GraphDatabase
import csv
from typing import List, Dict
import os

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class DataImporter:
    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def create_constraints_and_indexes(self):
        """Create constraints and indexes before import."""
        constraints = [
            "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT product_sku IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE",
            "CREATE CONSTRAINT order_id IF NOT EXISTS FOR (o:Order) REQUIRE o.id IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                session.run(constraint)
            print("Constraints and indexes created")
    
    def import_csv_batch(self, file_path: str, label: str, 
                         id_property: str, batch_size: int = 1000):
        """Import CSV file in batches."""
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        total = len(rows)
        imported = 0
        
        with self.driver.session() as session:
            for i in range(0, total, batch_size):
                batch = rows[i:i + batch_size]
                
                # Build dynamic query based on columns
                columns = batch[0].keys()
                props = ', '.join([f"{col}: row.{col}" for col in columns])
                
                session.run(f"""
                    UNWIND $rows AS row
                    CREATE (n:{label} {{{props}}})
                """, rows=batch)
                
                imported += len(batch)
                print(f"Imported {imported}/{total} {label} nodes")
        
        return imported
    
    def import_customers(self, file_path: str, batch_size: int = 1000):
        """Import customers with proper type conversion."""
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        with self.driver.session() as session:
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                
                session.run("""
                    UNWIND $rows AS row
                    CREATE (:Customer {
                        id: row.id,
                        name: row.name,
                        email: row.email,
                        country: row.country,
                        createdAt: datetime()
                    })
                """, rows=batch)
                
                print(f"Imported customers: {min(i + batch_size, len(rows))}/{len(rows)}")
    
    def import_products(self, file_path: str, batch_size: int = 1000):
        """Import products with numeric conversion."""
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = []
            for row in reader:
                rows.append({
                    'sku': row['sku'],
                    'name': row['name'],
                    'price': float(row['price']),
                    'category': row['category'],
                    'inStock': row.get('inStock', 'true').lower() == 'true'
                })
        
        with self.driver.session() as session:
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                
                session.run("""
                    UNWIND $rows AS row
                    CREATE (:Product {
                        sku: row.sku,
                        name: row.name,
                        price: row.price,
                        category: row.category,
                        inStock: row.inStock
                    })
                """, rows=batch)
    
    def import_orders_with_relationships(self, orders_file: str, 
                                          items_file: str, batch_size: int = 500):
        """Import orders and create relationships."""
        # Load orders
        with open(orders_file, 'r') as f:
            orders = list(csv.DictReader(f))
        
        # Load order items
        with open(items_file, 'r') as f:
            items = list(csv.DictReader(f))
        
        # Group items by order
        items_by_order = {}
        for item in items:
            order_id = item['orderId']
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append({
                'productSku': item['productSku'],
                'quantity': int(item['quantity']),
                'unitPrice': float(item['unitPrice'])
            })
        
        with self.driver.session() as session:
            for i in range(0, len(orders), batch_size):
                batch = orders[i:i + batch_size]
                
                for order in batch:
                    order_items = items_by_order.get(order['orderId'], [])
                    
                    session.run("""
                        MATCH (c:Customer {id: $customerId})
                        CREATE (o:Order {
                            id: $orderId,
                            total: $total,
                            orderDate: date($orderDate)
                        })
                        CREATE (c)-[:PLACED]->(o)
                        WITH o
                        UNWIND $items AS item
                        MATCH (p:Product {sku: item.productSku})
                        CREATE (o)-[:CONTAINS {
                            quantity: item.quantity,
                            unitPrice: item.unitPrice
                        }]->(p)
                    """, 
                        customerId=order['customerId'],
                        orderId=order['orderId'],
                        total=float(order['total']),
                        orderDate=order['orderDate'],
                        items=order_items
                    )
                
                print(f"Imported orders: {min(i + batch_size, len(orders))}/{len(orders)}")
    
    def verify_import(self):
        """Verify import results."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Customer) WITH count(c) AS customers
                MATCH (p:Product) WITH customers, count(p) AS products
                MATCH (o:Order) WITH customers, products, count(o) AS orders
                MATCH ()-[r:PLACED]->() WITH customers, products, orders, count(r) AS placed
                MATCH ()-[r:CONTAINS]->() 
                RETURN customers, products, orders, placed, count(r) AS contains
            """)
            
            record = result.single()
            print("\n=== Import Verification ===")
            print(f"Customers: {record['customers']}")
            print(f"Products: {record['products']}")
            print(f"Orders: {record['orders']}")
            print(f"PLACED relationships: {record['placed']}")
            print(f"CONTAINS relationships: {record['contains']}")

# Usage
def main():
    importer = DataImporter(URI, AUTH)
    
    try:
        # Step 1: Create constraints
        importer.create_constraints_and_indexes()
        
        # Step 2: Import nodes
        importer.import_customers('customers.csv')
        importer.import_products('products.csv')
        
        # Step 3: Import orders with relationships
        importer.import_orders_with_relationships('orders.csv', 'order_items.csv')
        
        # Step 4: Verify
        importer.verify_import()
        
    finally:
        importer.close()

if __name__ == '__main__':
    main()
```

---

## 20.10 Import Best Practices

### Pre-Import Checklist

1. **Clean and validate data** before import
2. **Create constraints** for unique properties
3. **Create indexes** for lookup properties
4. **Plan import order**: nodes before relationships
5. **Test with small sample** first

### Performance Tips

```cypher
// 1. Disable constraints during bulk import (if safe)
// Import data, then add constraints

// 2. Use appropriate batch sizes
// - Too small: overhead from transactions
// - Too large: memory issues
// Typical: 1000-10000 rows per transaction

// 3. Import nodes first, relationships second
// 4. Use UNWIND instead of multiple CREATE statements

// ❌ Slow
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CREATE (:Node {prop: row.prop})

// ✅ Faster with explicit batching
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL {
    WITH row
    CREATE (:Node {prop: row.prop})
} IN TRANSACTIONS OF 5000 ROWS
```

---

## Summary

### Key Commands

```cypher
-- Basic CSV import
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CREATE (:Label {prop: row.column})

-- With batching
LOAD CSV WITH HEADERS FROM 'file:///data.csv' AS row
CALL { WITH row CREATE ... } IN TRANSACTIONS OF 1000 ROWS

-- Type conversions
toInteger(), toFloat(), toBoolean(), date(), datetime(), split()

-- APOC JSON
CALL apoc.load.json('file:///data.json') YIELD value
```

### Import Strategy

1. Create constraints and indexes
2. Import nodes (customers, products, etc.)
3. Wait for indexes to populate
4. Import relationships
5. Verify import completeness

---

## Exercises

### Exercise 20.1: Basic Import
1. Create CSV files for products (sku, name, price, category)
2. Import with proper type conversion
3. Create indexes and verify

### Exercise 20.2: Relationships
1. Create CSV for customers and orders
2. Import customers first
3. Import orders with PLACED relationships

### Exercise 20.3: Large Dataset
1. Generate 100,000 row CSV
2. Import using batched transactions
3. Measure and optimize import time

### Exercise 20.4: JSON Import
1. Create nested JSON structure
2. Import with APOC
3. Create appropriate relationships

---

**Next Chapter: [Chapter 21: APOC Data Operations](21-apoc-data-operations.md)**
