# Chapter 21: APOC Data Operations

## Learning Objectives
By the end of this chapter, you will:
- Use APOC for advanced data loading
- Perform batch operations efficiently
- Work with external data sources
- Transform and manipulate data
- Schedule periodic operations

---

## 21.1 Introduction to APOC

### What is APOC?

APOC (Awesome Procedures on Cypher) is Neo4j's standard library of procedures and functions extending Cypher capabilities.

### Installing APOC

```cypher
// Check if APOC is installed
RETURN apoc.version()

// List all APOC procedures
CALL apoc.help('apoc')

// Search for specific procedures
CALL apoc.help('load')
```

### Configuration

In `neo4j.conf`:
```properties
# Enable APOC procedures
dbms.security.procedures.unrestricted=apoc.*
dbms.security.procedures.allowlist=apoc.*

# Enable file import/export
apoc.import.file.enabled=true
apoc.export.file.enabled=true
```

---

## 21.2 Loading JSON Data

### Load from File

```cypher
// Simple JSON array
// [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
CALL apoc.load.json('file:///people.json') YIELD value
CREATE (:Person {name: value.name, age: value.age})

// Nested JSON
CALL apoc.load.json('file:///company.json') YIELD value
CREATE (c:Company {name: value.company})
WITH c, value.employees AS employees
UNWIND employees AS emp
CREATE (e:Employee {name: emp.name})
CREATE (e)-[:WORKS_FOR]->(c)
```

### Load from URL

```cypher
// REST API
CALL apoc.load.json('https://api.example.com/users') YIELD value
UNWIND value.data AS user
CREATE (:User {id: user.id, name: user.name, email: user.email})

// With headers
CALL apoc.load.json('https://api.example.com/users', 
    {}, 
    {headers: {Authorization: 'Bearer token123'}}) 
YIELD value
RETURN value
```

### JSON Path Extraction

```cypher
// Extract specific paths
CALL apoc.load.json('https://api.example.com/complex', '$.data[*].users')
YIELD value
RETURN value

// Multiple paths
CALL apoc.load.json('file:///data.json') YIELD value
WITH apoc.convert.getJsonProperty(value, '$.store.book[?(@.price<10)]') AS cheapBooks
UNWIND cheapBooks AS book
RETURN book.title, book.price
```

---

## 21.3 Loading CSV with APOC

### Enhanced CSV Loading

```cypher
// Basic CSV load
CALL apoc.load.csv('file:///products.csv') YIELD map
CREATE (:Product {
    sku: map.sku,
    name: map.name,
    price: toFloat(map.price)
})

// With configuration
CALL apoc.load.csv('file:///data.csv', {
    header: true,
    sep: ';',
    ignore: ['notes'],
    mapping: {
        age: {type: 'int'},
        salary: {type: 'float'},
        active: {type: 'boolean'},
        hireDate: {type: 'date', format: 'yyyy-MM-dd'}
    }
}) YIELD map
CREATE (:Employee {
    name: map.name,
    age: map.age,
    salary: map.salary,
    active: map.active,
    hireDate: map.hireDate
})
```

### Parallel Loading

```cypher
// Load large CSV in parallel
CALL apoc.periodic.iterate(
    "CALL apoc.load.csv('file:///large_file.csv') YIELD map RETURN map",
    "CREATE (:Product {sku: map.sku, name: map.name})",
    {batchSize: 10000, parallel: true}
)
```

---

## 21.4 JDBC Database Connectivity

### Loading from Relational Databases

```cypher
// Load from PostgreSQL
CALL apoc.load.jdbc(
    'jdbc:postgresql://localhost:5432/mydb?user=neo4j&password=pass',
    'SELECT id, name, email FROM users'
) YIELD row
CREATE (:User {id: row.id, name: row.name, email: row.email})

// Using connection alias (configured in apoc.conf)
CALL apoc.load.jdbc('postgres', 'SELECT * FROM products') YIELD row
CREATE (:Product {id: row.id, name: row.name})

// With parameters
CALL apoc.load.jdbc('mysql', 
    'SELECT * FROM orders WHERE customer_id = ?', 
    [$customerId]
) YIELD row
RETURN row
```

### Configuration for JDBC

In `apoc.conf`:
```properties
apoc.jdbc.postgres.url=jdbc:postgresql://localhost:5432/mydb?user=neo4j&password=pass
apoc.jdbc.mysql.url=jdbc:mysql://localhost:3306/mydb?user=neo4j&password=pass
```

### Importing Relationships from SQL

```cypher
// Import users first
CALL apoc.load.jdbc('postgres', 'SELECT * FROM users') YIELD row
CREATE (:User {id: row.id, name: row.name})

// Then import relationships
CALL apoc.load.jdbc('postgres', 
    'SELECT user_id, product_id, quantity FROM orders'
) YIELD row
MATCH (u:User {id: row.user_id})
MATCH (p:Product {id: row.product_id})
CREATE (u)-[:PURCHASED {quantity: row.quantity}]->(p)
```

---

## 21.5 Periodic Iterate (Batch Processing)

### Basic Usage

```cypher
// Update all nodes in batches
CALL apoc.periodic.iterate(
    "MATCH (p:Product) RETURN p",
    "SET p.updatedAt = datetime()",
    {batchSize: 1000, parallel: false}
)
YIELD batches, total, timeTaken, committedOperations
RETURN batches, total, timeTaken

// Create relationships in batches
CALL apoc.periodic.iterate(
    "MATCH (c:Customer), (p:Product) 
     WHERE c.preferredCategory = p.category 
     RETURN c, p",
    "CREATE (c)-[:INTERESTED_IN]->(p)",
    {batchSize: 5000, parallel: true, concurrency: 4}
)
```

### Configuration Options

```cypher
CALL apoc.periodic.iterate(
    "outer statement returning values",
    "inner statement using $value",
    {
        batchSize: 1000,      // Rows per transaction
        parallel: true,       // Run batches in parallel
        concurrency: 4,       // Number of parallel threads
        retries: 3,           // Retry failed batches
        iterateList: false,   // Process rows individually vs as list
        params: {key: value}  // Additional parameters
    }
)
```

### Error Handling

```cypher
// Continue on errors
CALL apoc.periodic.iterate(
    "MATCH (p:Product) RETURN p",
    "SET p.price = toFloat(p.priceString)",  // May fail on invalid data
    {batchSize: 1000, batchMode: 'BATCH_SINGLE', failedParams: 100}
)
YIELD failedBatches, failedOperations, errorMessages
RETURN failedBatches, failedOperations, errorMessages
```

---

## 21.6 Periodic Commit and Scheduled Jobs

### Periodic Commit

```cypher
// Commit every N operations
CALL apoc.periodic.commit(
    "MATCH (p:Product) 
     WHERE p.processed IS NULL 
     WITH p LIMIT $limit 
     SET p.processed = true 
     RETURN count(*)",
    {limit: 10000}
)
YIELD updates, executions, runtime
RETURN updates, executions, runtime
```

### Scheduled Background Jobs

```cypher
// Schedule recurring job (Neo4j 5+)
CALL apoc.periodic.schedule(
    'cleanup-job',
    'MATCH (n:TempNode) WHERE n.createdAt < datetime() - duration("P7D") DELETE n',
    60  // Run every 60 seconds
)

// List scheduled jobs
CALL apoc.periodic.list()

// Cancel a job
CALL apoc.periodic.cancel('cleanup-job')
```

---

## 21.7 Data Transformation

### Merging and Refactoring Nodes

```cypher
// Merge duplicate nodes
MATCH (p:Person)
WITH p.email AS email, collect(p) AS persons
WHERE size(persons) > 1
CALL apoc.refactor.mergeNodes(persons, {
    properties: 'combine',
    mergeRels: true
})
YIELD node
RETURN node

// Clone nodes
MATCH (p:Product {sku: 'TEMPLATE'})
CALL apoc.refactor.cloneNodes([p], true, ['sku'])
YIELD input, output
SET output.sku = 'NEW-' + randomUUID()
RETURN output

// Clone subgraph
MATCH path = (c:Customer)-[:PURCHASED]->(o:Order)-[:CONTAINS]->(p:Product)
WHERE c.id = 'C001'
CALL apoc.refactor.cloneSubgraph(
    nodes(path),
    relationships(path),
    {skipProperties: ['id']}
)
YIELD input, output
RETURN input, output
```

### Changing Node Labels

```cypher
// Add label
MATCH (p:Person) WHERE p.role = 'Employee'
CALL apoc.create.addLabels(p, ['Employee'])
YIELD node
RETURN count(node)

// Remove label
MATCH (p:Person:TempLabel)
CALL apoc.create.removeLabels(p, ['TempLabel'])
YIELD node
RETURN count(node)

// Rename label
CALL apoc.refactor.rename.label('OldLabel', 'NewLabel')
```

### Changing Relationship Types

```cypher
// Change relationship type
MATCH (a:Person)-[r:KNOWS]->(b:Person)
WHERE r.closeness > 0.8
CALL apoc.refactor.setType(r, 'CLOSE_FRIEND')
YIELD input, output
RETURN count(*)

// Rename relationship type globally
CALL apoc.refactor.rename.type('WORKS_AT', 'EMPLOYED_BY')
```

---

## 21.8 Export Data

### Export to CSV

```cypher
// Export query results to CSV
CALL apoc.export.csv.query(
    'MATCH (p:Product) RETURN p.sku AS sku, p.name AS name, p.price AS price',
    'products.csv',
    {}
)

// Export entire database
CALL apoc.export.csv.all('full_export.csv', {})

// Export specific nodes
MATCH (c:Customer)-[:PURCHASED]->(o:Order)
WITH collect(DISTINCT c) + collect(DISTINCT o) AS nodes
CALL apoc.export.csv.data(nodes, [], 'customers_orders.csv', {})
YIELD nodes AS exportedNodes
RETURN exportedNodes
```

### Export to JSON

```cypher
// Export to JSON
CALL apoc.export.json.query(
    'MATCH (p:Product) RETURN p',
    'products.json',
    {jsonFormat: 'JSON_LINES'}
)

// Stream JSON (for API response)
CALL apoc.export.json.query(
    'MATCH (u:User {id: $userId})-[:PURCHASED]->(o:Order) RETURN u, collect(o) AS orders',
    null,
    {params: {userId: 'U001'}, stream: true}
)
YIELD data
RETURN data
```

### Export to Cypher Scripts

```cypher
// Generate Cypher CREATE statements
CALL apoc.export.cypher.all('backup.cypher', {
    format: 'cypher-shell',
    useOptimizations: {type: 'NONE', unwindBatchSize: 20}
})

// Export specific data
MATCH (p:Product) WHERE p.category = 'Electronics'
WITH collect(p) AS products
CALL apoc.export.cypher.data(products, [], 'electronics.cypher', {})
YIELD nodes
RETURN nodes
```

---

## 21.9 XML Processing

### Load XML

```cypher
// Load XML file
CALL apoc.load.xml('file:///data.xml') YIELD value
UNWIND value._children AS child
WHERE child._type = 'product'
CREATE (:Product {
    id: child.id,
    name: child.name._text
})

// With XPath
CALL apoc.load.xml('file:///catalog.xml', '/catalog/product') YIELD value
CREATE (:Product {
    sku: value.sku,
    name: value.name._text,
    price: toFloat(value.price._text)
})
```

### XML to Map

```cypher
// Convert XML to nested map structure
CALL apoc.load.xml('file:///config.xml') YIELD value
CALL apoc.convert.toMap(value) YIELD value AS config
RETURN config
```

---

## 21.10 Python Integration Examples

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

class APOCOperations:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def batch_import_json(self, json_url: str, label: str, batch_size: int = 1000):
        """Import JSON data in batches using APOC."""
        with self.driver.session() as session:
            result = session.run("""
                CALL apoc.periodic.iterate(
                    "CALL apoc.load.json($url) YIELD value RETURN value",
                    "CREATE (n:" + $label + ") SET n = value",
                    {batchSize: $batchSize, parallel: false, params: {url: $url}}
                )
                YIELD batches, total, timeTaken, committedOperations, failedOperations
                RETURN batches, total, timeTaken, committedOperations, failedOperations
            """, url=json_url, label=label, batchSize=batch_size)
            
            return result.single()
    
    def merge_duplicate_nodes(self, label: str, unique_property: str):
        """Merge nodes with duplicate property values."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n:$label)
                WITH n[$prop] AS propValue, collect(n) AS nodes
                WHERE size(nodes) > 1
                CALL apoc.refactor.mergeNodes(nodes, {
                    properties: 'combine',
                    mergeRels: true
                })
                YIELD node
                RETURN count(node) AS mergedCount
            """.replace('$label', label).replace('$prop', unique_property))
            
            return result.single()['mergedCount']
    
    def export_to_json(self, query: str, params: dict = None):
        """Export query results to JSON string."""
        with self.driver.session() as session:
            result = session.run("""
                CALL apoc.export.json.query($query, null, {stream: true, params: $params})
                YIELD data
                RETURN data
            """, query=query, params=params or {})
            
            return result.single()['data']
    
    def import_from_postgres(self, jdbc_url: str, sql_query: str, 
                             label: str, batch_size: int = 1000):
        """Import data from PostgreSQL."""
        with self.driver.session() as session:
            result = session.run("""
                CALL apoc.periodic.iterate(
                    "CALL apoc.load.jdbc($jdbc, $sql) YIELD row RETURN row",
                    "CREATE (n:$label) SET n = row",
                    {batchSize: $batch, parallel: false, 
                     params: {jdbc: $jdbc, sql: $sql}}
                )
                YIELD batches, total, timeTaken
                RETURN batches, total, timeTaken
            """.replace('$label', label),
                jdbc=jdbc_url, sql=sql_query, batch=batch_size)
            
            return result.single()
    
    def run_periodic_commit(self, update_query: str, batch_limit: int = 10000):
        """Run update in batches with periodic commit."""
        with self.driver.session() as session:
            result = session.run("""
                CALL apoc.periodic.commit($query, {limit: $limit})
                YIELD updates, executions, runtime
                RETURN updates, executions, runtime
            """, query=update_query, limit=batch_limit)
            
            return result.single()
    
    def transform_data(self, source_label: str, target_label: str, 
                       property_mappings: dict):
        """Transform nodes from one label to another with property mapping."""
        props_cypher = ', '.join([f"target.{v} = source.{k}" 
                                   for k, v in property_mappings.items()])
        
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (source:{source_label})
                CREATE (target:{target_label})
                SET {props_cypher}
                WITH source, target
                CALL apoc.create.addLabels(target, labels(source))
                YIELD node
                DETACH DELETE source
                RETURN count(node) AS transformed
            """)
            
            return result.single()['transformed']

# Usage
apoc_ops = APOCOperations(URI, AUTH)
try:
    # Import JSON from URL
    stats = apoc_ops.batch_import_json(
        'https://api.example.com/products',
        'Product',
        batch_size=5000
    )
    print(f"Imported {stats['total']} products in {stats['batches']} batches")
    
    # Export data
    json_data = apoc_ops.export_to_json(
        "MATCH (p:Product) WHERE p.price > 100 RETURN p LIMIT 10"
    )
    print(json_data)
    
finally:
    apoc_ops.close()
```

---

## Summary

### Key APOC Procedures

| Category | Procedure | Use Case |
|----------|-----------|----------|
| **Load** | `apoc.load.json` | Load JSON data |
| **Load** | `apoc.load.csv` | Enhanced CSV loading |
| **Load** | `apoc.load.jdbc` | Connect to SQL databases |
| **Batch** | `apoc.periodic.iterate` | Batch processing |
| **Batch** | `apoc.periodic.commit` | Periodic commits |
| **Export** | `apoc.export.csv.*` | Export to CSV |
| **Export** | `apoc.export.json.*` | Export to JSON |
| **Refactor** | `apoc.refactor.mergeNodes` | Merge duplicates |
| **Refactor** | `apoc.refactor.cloneNodes` | Clone nodes |
| **Create** | `apoc.create.addLabels` | Dynamic labels |

---

## Exercises

### Exercise 21.1: JSON Import
1. Create a JSON file with nested company/employee structure
2. Import using APOC with proper relationships
3. Handle missing/null values gracefully

### Exercise 21.2: Batch Processing
1. Create 100,000 test nodes
2. Use `apoc.periodic.iterate` to update all nodes
3. Compare performance with different batch sizes

### Exercise 21.3: Database Migration
1. Create a sample PostgreSQL table
2. Use APOC JDBC to import into Neo4j
3. Create appropriate relationships

### Exercise 21.4: Data Export
1. Export a subgraph to JSON
2. Export to Cypher script for backup
3. Verify export by importing into fresh database

---

**Next Chapter: [Chapter 22: Database Administration](22-database-administration.md)**
