# Chapter 24: Multi-Database and Fabric

## Learning Objectives
By the end of this chapter, you will:
- Create and manage multiple databases
- Understand database-level isolation
- Use Neo4j Fabric for federated queries
- Implement sharding strategies
- Design multi-database architectures

---

## 24.1 Multi-Database Overview

### Why Multiple Databases?

- **Isolation**: Separate data for different applications
- **Security**: Different access controls per database
- **Performance**: Reduce index/query scope
- **Multi-tenancy**: Separate customer data
- **Lifecycle**: Independent backup/maintenance

### System vs User Databases

```cypher
// System database - manages other databases
:use system

// User databases - store application data
:use neo4j
:use customers
```

---

## 24.2 Database Management

### Creating Databases

```cypher
// Switch to system database
:use system

// Create database
CREATE DATABASE customers

// Create if not exists
CREATE DATABASE orders IF NOT EXISTS

// Create with options (Enterprise)
CREATE DATABASE analytics
OPTIONS {
    existingData: 'use',  // or 'empty'
    existingDataSeedInstance: 'server1'
}

// Show all databases
SHOW DATABASES
```

### Database States

```cypher
// Show database status
SHOW DATABASES
YIELD name, currentStatus, requestedStatus, error
RETURN *

// Possible states:
// - online: Available for queries
// - offline: Stopped
// - starting: Coming online
// - stopping: Going offline
// - initial: Just created

// Start database
START DATABASE customers

// Stop database
STOP DATABASE customers
```

### Dropping Databases

```cypher
// Drop database
DROP DATABASE customers

// Drop if exists
DROP DATABASE customers IF EXISTS

// Drop with data destruction confirmation
DROP DATABASE customers IF EXISTS DESTROY DATA

// Dump before drop (for backup)
DROP DATABASE customers IF EXISTS DUMP DATA
```

### Database Aliases

```cypher
// Create alias
CREATE ALIAS reporting FOR DATABASE analytics

// Use alias
:use reporting

// Show aliases
SHOW ALIASES FOR DATABASES

// Drop alias
DROP ALIAS reporting FOR DATABASE
```

---

## 24.3 Working with Multiple Databases

### Switching Databases

```cypher
// In Neo4j Browser
:use neo4j
:use customers
:use system

// In Cypher (within query)
USE neo4j
MATCH (n) RETURN count(n)
```

### Python Multi-Database Access

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

driver = GraphDatabase.driver(URI, auth=AUTH)

# Specify database in session
with driver.session(database="customers") as session:
    result = session.run("MATCH (c:Customer) RETURN count(c) AS count")
    print(f"Customers: {result.single()['count']}")

with driver.session(database="orders") as session:
    result = session.run("MATCH (o:Order) RETURN count(o) AS count")
    print(f"Orders: {result.single()['count']}")

# System database operations
with driver.session(database="system") as session:
    result = session.run("SHOW DATABASES YIELD name, currentStatus RETURN *")
    for record in result:
        print(f"{record['name']}: {record['currentStatus']}")

driver.close()
```

### Home Database

```cypher
// Set default database for user
ALTER USER alice SET HOME DATABASE customers

// Show current user's home database
SHOW CURRENT USER
YIELD user, homeDatabase
RETURN user, homeDatabase
```

---

## 24.4 Neo4j Fabric (Enterprise)

### What is Fabric?

Fabric enables federated queries across multiple databases, even across different Neo4j clusters.

### Fabric Configuration

```properties
# neo4j.conf

# Enable Fabric
fabric.database.name=fabric

# Define graph aliases
fabric.graph.0.name=customers
fabric.graph.0.uri=neo4j://localhost:7687
fabric.graph.0.database=customers

fabric.graph.1.name=orders
fabric.graph.1.uri=neo4j://localhost:7687
fabric.graph.1.database=orders

fabric.graph.2.name=remote_analytics
fabric.graph.2.uri=neo4j://analytics-server:7687
fabric.graph.2.database=analytics
```

### Basic Fabric Queries

```cypher
// Use fabric database
USE fabric

// Query single graph
USE fabric.customers
MATCH (c:Customer)
RETURN c.name

// Query multiple graphs
USE fabric
CALL {
    USE fabric.customers
    MATCH (c:Customer)
    RETURN c.id AS customerId, c.name AS customerName
}
CALL {
    USE fabric.orders
    WITH customerId
    MATCH (o:Order {customerId: customerId})
    RETURN count(o) AS orderCount
}
RETURN customerName, orderCount
```

### Federated Queries

```cypher
// Aggregate data from multiple databases
USE fabric
UNWIND ['customers', 'orders', 'products'] AS graphName
CALL {
    USE fabric.graph(graphName)
    MATCH (n)
    RETURN count(n) AS nodeCount
}
RETURN graphName, nodeCount

// Join data across databases
USE fabric
CALL {
    USE fabric.customers
    MATCH (c:Customer)-[:LIVES_IN]->(city:City)
    RETURN c.id AS customerId, city.name AS cityName
}
CALL {
    USE fabric.orders
    WITH customerId
    MATCH (o:Order {customerId: customerId})
    RETURN sum(o.total) AS totalSpent
}
RETURN cityName, sum(totalSpent) AS cityRevenue
ORDER BY cityRevenue DESC
```

---

## 24.5 Sharding Strategies

### Sharding by Tenant

```
Database: tenant_acme     - All data for Acme Corp
Database: tenant_globex   - All data for Globex Inc
Database: tenant_initech  - All data for Initech
```

```python
class TenantManager:
    def __init__(self, driver):
        self.driver = driver
    
    def get_tenant_session(self, tenant_id: str):
        """Get session for specific tenant database."""
        database_name = f"tenant_{tenant_id}"
        return self.driver.session(database=database_name)
    
    def create_tenant(self, tenant_id: str):
        """Create database for new tenant."""
        with self.driver.session(database="system") as session:
            session.run(f"CREATE DATABASE tenant_{tenant_id} IF NOT EXISTS")
    
    def query_tenant(self, tenant_id: str, query: str, params: dict = None):
        """Execute query in tenant database."""
        with self.get_tenant_session(tenant_id) as session:
            return session.run(query, params or {})
```

### Sharding by Data Type

```
Database: customers   - Customer nodes and relationships
Database: products    - Product catalog
Database: orders      - Order transactions
Database: analytics   - Aggregated data for reporting
```

### Sharding by Region

```
Database: region_us   - US customers and orders
Database: region_eu   - EU customers and orders
Database: region_apac - APAC customers and orders
```

```cypher
// Query with Fabric across regions
USE fabric
CALL {
    USE fabric.region_us
    MATCH (c:Customer)
    RETURN c.email, 'US' AS region
    UNION
    USE fabric.region_eu
    MATCH (c:Customer)
    RETURN c.email, 'EU' AS region
    UNION
    USE fabric.region_apac
    MATCH (c:Customer)
    RETURN c.email, 'APAC' AS region
}
RETURN email, region
```

### Sharding by Time

```
Database: orders_2024   - Orders from 2024
Database: orders_2025   - Orders from 2025
Database: orders_2026   - Orders from 2026 (current)
```

```python
from datetime import datetime

class TimeShardedOrderManager:
    def __init__(self, driver):
        self.driver = driver
    
    def get_database_for_date(self, date: datetime) -> str:
        return f"orders_{date.year}"
    
    def create_order(self, order_data: dict):
        order_date = order_data.get('orderDate', datetime.now())
        database = self.get_database_for_date(order_date)
        
        with self.driver.session(database=database) as session:
            return session.run("""
                CREATE (o:Order $props)
                RETURN o
            """, props=order_data)
    
    def query_orders_range(self, start_date: datetime, end_date: datetime):
        """Query orders across multiple year databases."""
        results = []
        
        for year in range(start_date.year, end_date.year + 1):
            database = f"orders_{year}"
            
            with self.driver.session(database=database) as session:
                result = session.run("""
                    MATCH (o:Order)
                    WHERE o.orderDate >= $start AND o.orderDate <= $end
                    RETURN o
                """, start=start_date.isoformat(), end=end_date.isoformat())
                
                results.extend([r['o'] for r in result])
        
        return results
```

---

## 24.6 Multi-Database Architecture Patterns

### Pattern 1: Microservices with Dedicated Databases

```
Service: CustomerService  → Database: customers
Service: OrderService     → Database: orders
Service: ProductService   → Database: products
Service: AnalyticsService → Database: analytics (read replicas)
```

```python
class ServiceDatabaseRouter:
    DATABASE_MAPPING = {
        'customer': 'customers',
        'order': 'orders',
        'product': 'products',
        'analytics': 'analytics'
    }
    
    def __init__(self, driver):
        self.driver = driver
    
    def get_session(self, service_name: str):
        database = self.DATABASE_MAPPING.get(service_name, 'neo4j')
        return self.driver.session(database=database)
```

### Pattern 2: Read/Write Separation

```
Database: primary     - Write operations
Database: replica_1   - Read operations (analytics)
Database: replica_2   - Read operations (API)
```

### Pattern 3: Operational + Analytical

```
Database: operational  - Real-time OLTP workloads
Database: analytical   - Batch OLAP workloads, aggregated data
```

```cypher
// Sync from operational to analytical (periodic job)
USE fabric
CALL {
    USE fabric.operational
    MATCH (c:Customer)-[:PURCHASED]->(o:Order)
    WITH c.segment AS segment, sum(o.total) AS revenue, count(o) AS orders
    RETURN segment, revenue, orders
}
CALL {
    USE fabric.analytical
    WITH segment, revenue, orders
    MERGE (s:SegmentStats {segment: segment})
    SET s.revenue = revenue, s.orders = orders, s.updatedAt = datetime()
}
RETURN segment, revenue, orders
```

---

## 24.7 Cross-Database Operations

### Copying Data Between Databases

```cypher
// Export from source
USE source_db
CALL apoc.export.cypher.query(
    'MATCH (c:Customer) RETURN c',
    '/tmp/customers.cypher',
    {}
)

// Import to target
USE target_db
CALL apoc.cypher.runFile('/tmp/customers.cypher')
```

### Using APOC for Cross-Database

```cypher
// Query remote database
CALL apoc.bolt.load(
    'bolt://other-server:7687',
    'MATCH (c:Customer) RETURN c.name AS name',
    {},
    {credentials: {user: 'neo4j', password: 'pass'}}
) YIELD row
CREATE (:CustomerCopy {name: row.name})
```

### Synchronization Pattern

```python
class DatabaseSynchronizer:
    def __init__(self, driver):
        self.driver = driver
    
    def sync_customers(self, source_db: str, target_db: str):
        """Sync customers from source to target database."""
        # Read from source
        with self.driver.session(database=source_db) as session:
            result = session.run("""
                MATCH (c:Customer)
                WHERE c.updatedAt > datetime() - duration('PT1H')
                RETURN c.id AS id, c.name AS name, c.email AS email
            """)
            customers = [dict(r) for r in result]
        
        # Write to target
        with self.driver.session(database=target_db) as session:
            session.run("""
                UNWIND $customers AS cust
                MERGE (c:Customer {id: cust.id})
                SET c.name = cust.name, c.email = cust.email, c.syncedAt = datetime()
            """, customers=customers)
        
        return len(customers)
```

---

## 24.8 Best Practices

### Database Design Guidelines

```
1. Start with a single database unless you have clear reasons to split
2. Split when:
   - Security isolation is required
   - Performance requires smaller scopes
   - Multi-tenancy is needed
   - Different lifecycle requirements

3. Keep related data together:
   - Data frequently joined should be in same database
   - Cross-database joins (via Fabric) are slower

4. Consider operational complexity:
   - Each database needs backup strategy
   - Each database needs monitoring
   - Each database needs index management
```

### Naming Conventions

```
# Tenant databases
tenant_{tenant_id}
tenant_acme
tenant_globex

# Domain databases
{domain}_db
customers_db
orders_db

# Time-partitioned
{domain}_{year}
orders_2024
orders_2025

# Environment-qualified
{env}_{domain}
prod_customers
staging_customers
```

### Monitoring Multiple Databases

```python
class MultiDatabaseMonitor:
    def __init__(self, driver):
        self.driver = driver
    
    def get_all_database_stats(self):
        """Get statistics for all databases."""
        stats = {}
        
        # Get list of databases
        with self.driver.session(database="system") as session:
            result = session.run("""
                SHOW DATABASES
                YIELD name, currentStatus
                WHERE currentStatus = 'online' AND name <> 'system'
                RETURN name
            """)
            databases = [r['name'] for r in result]
        
        # Get stats for each
        for db in databases:
            with self.driver.session(database=db) as session:
                result = session.run("""
                    MATCH (n) WITH count(n) AS nodes
                    MATCH ()-[r]->() WITH nodes, count(r) AS rels
                    RETURN nodes, rels
                """)
                record = result.single()
                stats[db] = {
                    'nodes': record['nodes'],
                    'relationships': record['rels']
                }
        
        return stats
    
    def check_database_health(self):
        """Check health of all databases."""
        with self.driver.session(database="system") as session:
            result = session.run("""
                SHOW DATABASES
                YIELD name, currentStatus, requestedStatus, error
                RETURN name, currentStatus, requestedStatus, error
            """)
            
            health = []
            for r in result:
                status = 'healthy' if r['currentStatus'] == 'online' and not r['error'] else 'unhealthy'
                health.append({
                    'database': r['name'],
                    'status': status,
                    'currentStatus': r['currentStatus'],
                    'error': r['error']
                })
            
            return health
```

---

## Summary

### Key Concepts

| Feature | Description |
|---------|-------------|
| **Multi-Database** | Multiple isolated databases in one Neo4j instance |
| **Fabric** | Federated queries across databases |
| **Database Alias** | Alternative names for databases |
| **Home Database** | Default database for user |

### Key Commands

```cypher
-- Database Management
CREATE DATABASE name
DROP DATABASE name IF EXISTS
START DATABASE name
STOP DATABASE name
SHOW DATABASES

-- Fabric Queries
USE fabric.graphName
CALL { USE fabric.graph1 ... }
CALL { USE fabric.graph2 ... }

-- User Settings
ALTER USER username SET HOME DATABASE dbname
```

---

## Exercises

### Exercise 24.1: Multi-Tenant Setup
1. Create databases for 3 different tenants
2. Populate each with sample data
3. Write a Python class to route queries by tenant

### Exercise 24.2: Fabric Queries
1. Configure Fabric with multiple databases
2. Write queries that aggregate across databases
3. Implement a reporting query that joins data

### Exercise 24.3: Sharding Strategy
1. Design a time-based sharding strategy
2. Implement write routing by date
3. Implement query routing across shards

---

**Next Chapter: [Chapter 25: Graph Data Science Library](25-graph-data-science.md)**
