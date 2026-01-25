# Chapter 32: Python Driver Deep Dive

## Learning Objectives
By the end of this chapter, you will:
- Master Neo4j Python driver configuration
- Implement connection pooling and session management
- Handle transactions correctly
- Build robust error handling
- Optimize driver performance

---

## 32.1 Driver Installation and Setup

### Installation

```bash
# Install the official driver
pip install neo4j

# With async support
pip install neo4j[async]

# Verify installation
python -c "import neo4j; print(neo4j.__version__)"
```

### Basic Connection

```python
from neo4j import GraphDatabase

# Connection URI formats
# Bolt protocol (default)
URI = "bolt://localhost:7687"

# Neo4j protocol (routing enabled)
URI = "neo4j://localhost:7687"

# With encryption
URI = "neo4j+s://your-instance.databases.neo4j.io"
URI = "bolt+s://your-instance.databases.neo4j.io"

# Authentication
AUTH = ("neo4j", "password")

# Create driver
driver = GraphDatabase.driver(URI, auth=AUTH)

# Verify connectivity
driver.verify_connectivity()

# Always close when done
driver.close()
```

### Context Manager Pattern

```python
from neo4j import GraphDatabase

URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "password")

# Recommended: Use context manager
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    # Use driver here
# Driver automatically closed
```

---

## 32.2 Driver Configuration

### Connection Pool Settings

```python
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password"),
    
    # Connection pool
    max_connection_pool_size=50,           # Max connections in pool
    connection_acquisition_timeout=60.0,   # Wait time for connection
    
    # Connection settings
    connection_timeout=30.0,               # TCP connection timeout
    max_transaction_retry_time=30.0,       # Retry transient errors
    
    # Keep-alive
    keep_alive=True,
    
    # Encryption (for bolt://)
    encrypted=False,
    trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
)
```

### SSL/TLS Configuration

```python
from neo4j import GraphDatabase, TrustAll, TrustSystemCAs, TrustCustomCAs

# Trust all certificates (not for production!)
driver = GraphDatabase.driver(
    "bolt+s://localhost:7687",
    auth=("neo4j", "password"),
    trusted_certificates=TrustAll()
)

# Trust system CA certificates
driver = GraphDatabase.driver(
    "neo4j+s://localhost:7687",
    auth=("neo4j", "password"),
    trusted_certificates=TrustSystemCAs()
)

# Trust custom certificates
driver = GraphDatabase.driver(
    "neo4j+s://localhost:7687",
    auth=("neo4j", "password"),
    trusted_certificates=TrustCustomCAs("/path/to/ca.crt")
)
```

### User Agent and Metadata

```python
driver = GraphDatabase.driver(
    "neo4j://localhost:7687",
    auth=("neo4j", "password"),
    user_agent="MyApp/1.0.0"
)
```

---

## 32.3 Sessions

### Creating Sessions

```python
# Basic session
with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n)")
    print(result.single()[0])

# With database selection
with driver.session(database="movies") as session:
    result = session.run("MATCH (m:Movie) RETURN count(m)")

# With bookmarks (for causal consistency)
from neo4j import Bookmarks

bookmarks = Bookmarks()
with driver.session(bookmarks=bookmarks) as session:
    # Write transaction
    session.execute_write(lambda tx: tx.run("CREATE (n:Test)"))
    bookmarks = session.last_bookmarks()

# Use bookmarks in another session
with driver.session(bookmarks=bookmarks) as session:
    # Guaranteed to see previous write
    result = session.run("MATCH (n:Test) RETURN count(n)")
```

### Session Configuration

```python
with driver.session(
    database="neo4j",
    default_access_mode="WRITE",  # or "READ"
    fetch_size=1000,
    bookmarks=None
) as session:
    # Session operations
    pass
```

---

## 32.4 Transactions

### Auto-commit Transactions

```python
# Simple but no automatic retry
with driver.session() as session:
    result = session.run(
        "CREATE (p:Person {name: $name}) RETURN p",
        name="Alice"
    )
    record = result.single()
    print(record["p"])
```

### Managed Transactions (Recommended)

```python
def create_person(tx, name):
    """Transaction function - will be retried on transient errors."""
    result = tx.run(
        "CREATE (p:Person {name: $name}) RETURN p",
        name=name
    )
    return result.single()["p"]

def get_person(tx, name):
    """Read transaction function."""
    result = tx.run(
        "MATCH (p:Person {name: $name}) RETURN p",
        name=name
    )
    record = result.single()
    return record["p"] if record else None

with driver.session() as session:
    # Write transaction
    person = session.execute_write(create_person, "Alice")
    
    # Read transaction
    found = session.execute_read(get_person, "Alice")
```

### Explicit Transactions

```python
with driver.session() as session:
    tx = session.begin_transaction()
    try:
        tx.run("CREATE (a:Account {id: $id, balance: $balance})",
               id=1, balance=1000)
        tx.run("CREATE (a:Account {id: $id, balance: $balance})",
               id=2, balance=500)
        tx.commit()
    except Exception as e:
        tx.rollback()
        raise

# Context manager for explicit transactions
with driver.session() as session:
    with session.begin_transaction() as tx:
        tx.run("CREATE (n:Test)")
        # Commits automatically if no exception
        # Rolls back on exception
```

### Transaction Metadata

```python
def create_with_metadata(tx, name):
    result = tx.run(
        "CREATE (p:Person {name: $name}) RETURN p",
        name=name
    )
    return result.single()

with driver.session() as session:
    session.execute_write(
        create_with_metadata, 
        "Alice",
        timeout=30.0,  # Transaction timeout
        metadata={"app": "myapp", "user": "admin"}
    )
```

---

## 32.5 Working with Results

### Consuming Results

```python
with driver.session() as session:
    result = session.run("MATCH (p:Person) RETURN p.name AS name, p.age AS age")
    
    # Iterate over records
    for record in result:
        print(f"{record['name']}: {record['age']}")
    
    # Get all as list (loads into memory)
    result = session.run("MATCH (p:Person) RETURN p.name")
    all_records = list(result)
    
    # Get single record
    result = session.run("MATCH (p:Person {name: $name}) RETURN p", name="Alice")
    single = result.single()  # Returns None or Record, raises if multiple
    
    # Get first record
    result = session.run("MATCH (p:Person) RETURN p LIMIT 10")
    first = result.peek()  # Doesn't consume
    
    # Get values directly
    result = session.run("MATCH (p:Person) RETURN p.name")
    names = [record.value() for record in result]
    
    # Convert to list of dicts
    result = session.run("MATCH (p:Person) RETURN p.name AS name, p.age AS age")
    data = [dict(record) for record in result]
```

### Result Summary

```python
with driver.session() as session:
    result = session.run(
        "CREATE (p:Person {name: $name}) RETURN p",
        name="Alice"
    )
    # Consume result first
    list(result)
    
    # Get summary
    summary = result.consume()
    
    print(f"Query: {summary.query}")
    print(f"Parameters: {summary.parameters}")
    print(f"Query type: {summary.query_type}")
    print(f"Counters: {summary.counters}")
    print(f"  Nodes created: {summary.counters.nodes_created}")
    print(f"  Relationships created: {summary.counters.relationships_created}")
    print(f"  Properties set: {summary.counters.properties_set}")
    print(f"Database: {summary.database}")
    print(f"Server: {summary.server.address}")
    
    # Timing information
    print(f"Available after: {summary.result_available_after}ms")
    print(f"Consumed after: {summary.result_consumed_after}ms")
    
    # Plan information (if EXPLAIN/PROFILE used)
    if summary.plan:
        print(f"Plan: {summary.plan}")
    if summary.profile:
        print(f"Profile: {summary.profile}")
```

### Data Types Mapping

```python
from neo4j.time import DateTime, Date, Time, Duration
from neo4j.spatial import Point

# Python to Neo4j type mapping
with driver.session() as session:
    session.run("""
        CREATE (n:TypeTest {
            string: $string,
            integer: $integer,
            float: $float,
            boolean: $boolean,
            list: $list,
            map: $map,
            null: $null,
            date: $date,
            datetime: $datetime,
            duration: $duration,
            point: $point
        })
    """,
        string="hello",
        integer=42,
        float=3.14,
        boolean=True,
        list=[1, 2, 3],
        map={"key": "value"},
        null=None,
        date=Date(2024, 12, 25),
        datetime=DateTime(2024, 12, 25, 10, 30, 0),
        duration=Duration(days=5, hours=3),
        point=Point((12.34, 56.78))  # 2D point
    )

# Neo4j to Python type mapping
with driver.session() as session:
    result = session.run("MATCH (n:TypeTest) RETURN n")
    node = result.single()["n"]
    
    # Node properties are Python types
    print(type(node["date"]))      # neo4j.time.Date
    print(type(node["datetime"]))  # neo4j.time.DateTime
    print(type(node["point"]))     # neo4j.spatial.Point
```

### Working with Nodes and Relationships

```python
with driver.session() as session:
    result = session.run("""
        MATCH (p:Person)-[r:KNOWS]->(friend:Person)
        RETURN p, r, friend
    """)
    
    for record in result:
        person = record["p"]
        relationship = record["r"]
        friend = record["friend"]
        
        # Node properties
        print(f"Person ID: {person.element_id}")
        print(f"Labels: {person.labels}")
        print(f"Properties: {dict(person)}")
        
        # Relationship properties
        print(f"Relationship ID: {relationship.element_id}")
        print(f"Type: {relationship.type}")
        print(f"Start node ID: {relationship.start_node.element_id}")
        print(f"End node ID: {relationship.end_node.element_id}")
        print(f"Properties: {dict(relationship)}")
```

---

## 32.6 Error Handling

### Exception Hierarchy

```python
from neo4j.exceptions import (
    Neo4jError,
    ServiceUnavailable,
    SessionExpired,
    TransientError,
    DatabaseError,
    ClientError,
    ConstraintError,
    AuthError,
    ForbiddenError
)

with driver.session() as session:
    try:
        session.run("CREATE (n:Node)")
    
    except ServiceUnavailable as e:
        # Server not available - retry or fail
        print(f"Server unavailable: {e}")
    
    except SessionExpired as e:
        # Session expired - create new session
        print(f"Session expired: {e}")
    
    except TransientError as e:
        # Transient error - can retry
        print(f"Transient error: {e}")
    
    except ConstraintError as e:
        # Constraint violation
        print(f"Constraint violation: {e.code}: {e.message}")
    
    except AuthError as e:
        # Authentication failed
        print(f"Auth error: {e}")
    
    except ClientError as e:
        # Client-side error (syntax, etc.)
        print(f"Client error: {e.code}: {e.message}")
    
    except Neo4jError as e:
        # Generic Neo4j error
        print(f"Neo4j error: {e.code}: {e.message}")
```

### Retry Logic

```python
import time
from neo4j.exceptions import TransientError, ServiceUnavailable

def execute_with_retry(session, query, params=None, max_retries=3):
    """Execute query with retry logic."""
    for attempt in range(max_retries):
        try:
            result = session.run(query, params or {})
            return list(result)
        
        except (TransientError, ServiceUnavailable) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1} after {wait_time}s: {e}")
                time.sleep(wait_time)
            else:
                raise

# Managed transactions have built-in retry
def create_person(tx, name):
    result = tx.run("CREATE (p:Person {name: $name}) RETURN p", name=name)
    return result.single()

# This automatically retries transient errors
with driver.session() as session:
    person = session.execute_write(create_person, "Alice")
```

---

## 32.7 Async Driver

### Async Basics

```python
import asyncio
from neo4j import AsyncGraphDatabase

async def main():
    URI = "neo4j://localhost:7687"
    AUTH = ("neo4j", "password")
    
    async with AsyncGraphDatabase.driver(URI, auth=AUTH) as driver:
        await driver.verify_connectivity()
        
        async with driver.session() as session:
            result = await session.run("MATCH (n) RETURN count(n) AS count")
            record = await result.single()
            print(f"Node count: {record['count']}")

asyncio.run(main())
```

### Async Transactions

```python
import asyncio
from neo4j import AsyncGraphDatabase

async def create_person(tx, name):
    result = await tx.run(
        "CREATE (p:Person {name: $name}) RETURN p",
        name=name
    )
    record = await result.single()
    return record["p"]

async def get_all_people(tx):
    result = await tx.run("MATCH (p:Person) RETURN p.name AS name")
    return [record["name"] async for record in result]

async def main():
    async with AsyncGraphDatabase.driver(URI, auth=AUTH) as driver:
        async with driver.session() as session:
            # Write
            person = await session.execute_write(create_person, "Alice")
            
            # Read
            names = await session.execute_read(get_all_people)
            print(names)

asyncio.run(main())
```

### Parallel Async Operations

```python
import asyncio
from neo4j import AsyncGraphDatabase

async def get_person_by_name(session, name):
    result = await session.run(
        "MATCH (p:Person {name: $name}) RETURN p",
        name=name
    )
    record = await result.single()
    return record["p"] if record else None

async def main():
    async with AsyncGraphDatabase.driver(URI, auth=AUTH) as driver:
        names = ["Alice", "Bob", "Charlie", "David"]
        
        # Parallel queries
        async with driver.session() as session:
            tasks = [get_person_by_name(session, name) for name in names]
            results = await asyncio.gather(*tasks)
            
            for name, person in zip(names, results):
                print(f"{name}: {person}")

asyncio.run(main())
```

---

## 32.8 Best Practices

### Driver Lifecycle

```python
# BAD: Creating driver for each query
def bad_query():
    driver = GraphDatabase.driver(URI, auth=AUTH)
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n")
    driver.close()

# GOOD: Reuse driver instance
class DatabaseService:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def query(self, cypher, params=None):
        with self.driver.session() as session:
            return list(session.run(cypher, params or {}))
```

### Session Management

```python
# BAD: Long-lived session
session = driver.session()
# ... many operations over long time
session.close()

# GOOD: Short-lived sessions
def get_data():
    with driver.session() as session:
        return list(session.run("MATCH (n) RETURN n"))

def save_data(data):
    with driver.session() as session:
        session.execute_write(lambda tx: tx.run("CREATE (n:Data $props)", props=data))
```

### Parameter Usage

```python
# BAD: String concatenation (SQL injection risk!)
name = "Alice"
session.run(f"MATCH (p:Person {{name: '{name}'}}) RETURN p")

# GOOD: Use parameters
session.run("MATCH (p:Person {name: $name}) RETURN p", name="Alice")

# GOOD: Multiple parameters
session.run(
    "CREATE (p:Person {name: $name, age: $age})",
    name="Alice",
    age=30
)

# GOOD: Dictionary of parameters
params = {"name": "Alice", "age": 30}
session.run("CREATE (p:Person {name: $name, age: $age})", **params)
```

### Result Consumption

```python
# BAD: Not consuming results
with driver.session() as session:
    session.run("CREATE (n:Test)")  # Result not consumed!

# GOOD: Consume results
with driver.session() as session:
    result = session.run("CREATE (n:Test)")
    result.consume()  # Explicitly consume

# GOOD: Use managed transactions
with driver.session() as session:
    session.execute_write(lambda tx: tx.run("CREATE (n:Test)").consume())
```

---

## 32.9 Complete Application Example

```python
from neo4j import GraphDatabase
from typing import List, Dict, Optional
from contextlib import contextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jRepository:
    """Repository pattern for Neo4j operations."""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()
        logger.info("Connected to Neo4j")
    
    def close(self):
        self.driver.close()
        logger.info("Disconnected from Neo4j")
    
    @contextmanager
    def _session(self, database: str = None):
        session = self.driver.session(database=database)
        try:
            yield session
        finally:
            session.close()
    
    # Person operations
    def create_person(self, name: str, age: int = None) -> Dict:
        def _create(tx, name, age):
            result = tx.run("""
                CREATE (p:Person {name: $name, age: $age, created: datetime()})
                RETURN p {.*, id: elementId(p)} AS person
            """, name=name, age=age)
            return result.single()["person"]
        
        with self._session() as session:
            return session.execute_write(_create, name, age)
    
    def get_person(self, name: str) -> Optional[Dict]:
        def _get(tx, name):
            result = tx.run("""
                MATCH (p:Person {name: $name})
                RETURN p {.*, id: elementId(p)} AS person
            """, name=name)
            record = result.single()
            return record["person"] if record else None
        
        with self._session() as session:
            return session.execute_read(_get, name)
    
    def get_all_people(self, limit: int = 100) -> List[Dict]:
        def _get_all(tx, limit):
            result = tx.run("""
                MATCH (p:Person)
                RETURN p {.*, id: elementId(p)} AS person
                ORDER BY p.name
                LIMIT $limit
            """, limit=limit)
            return [record["person"] for record in result]
        
        with self._session() as session:
            return session.execute_read(_get_all, limit)
    
    def update_person(self, name: str, properties: Dict) -> Optional[Dict]:
        def _update(tx, name, properties):
            result = tx.run("""
                MATCH (p:Person {name: $name})
                SET p += $properties, p.updated = datetime()
                RETURN p {.*, id: elementId(p)} AS person
            """, name=name, properties=properties)
            record = result.single()
            return record["person"] if record else None
        
        with self._session() as session:
            return session.execute_write(_update, name, properties)
    
    def delete_person(self, name: str) -> bool:
        def _delete(tx, name):
            result = tx.run("""
                MATCH (p:Person {name: $name})
                DETACH DELETE p
                RETURN count(p) AS deleted
            """, name=name)
            return result.single()["deleted"] > 0
        
        with self._session() as session:
            return session.execute_write(_delete, name)
    
    # Relationship operations
    def create_friendship(self, person1: str, person2: str, 
                          since: str = None) -> Dict:
        def _create_friendship(tx, person1, person2, since):
            result = tx.run("""
                MATCH (p1:Person {name: $person1})
                MATCH (p2:Person {name: $person2})
                MERGE (p1)-[r:KNOWS]->(p2)
                SET r.since = $since
                RETURN p1.name AS person1, p2.name AS person2, r.since AS since
            """, person1=person1, person2=person2, since=since)
            return dict(result.single())
        
        with self._session() as session:
            return session.execute_write(
                _create_friendship, person1, person2, since
            )
    
    def get_friends(self, name: str) -> List[Dict]:
        def _get_friends(tx, name):
            result = tx.run("""
                MATCH (p:Person {name: $name})-[:KNOWS]-(friend:Person)
                RETURN friend {.*, id: elementId(friend)} AS friend
            """, name=name)
            return [record["friend"] for record in result]
        
        with self._session() as session:
            return session.execute_read(_get_friends, name)
    
    def get_friends_of_friends(self, name: str, depth: int = 2) -> List[Dict]:
        def _get_fof(tx, name, depth):
            result = tx.run("""
                MATCH (p:Person {name: $name})-[:KNOWS*2..$depth]-(fof:Person)
                WHERE p <> fof AND NOT (p)-[:KNOWS]-(fof)
                RETURN DISTINCT fof {.*, id: elementId(fof)} AS person,
                       min(length((p)-[:KNOWS*]-(fof))) AS distance
                ORDER BY distance
            """, name=name, depth=depth)
            return [dict(record) for record in result]
        
        with self._session() as session:
            return session.execute_read(_get_fof, name, depth)
    
    # Batch operations
    def bulk_create_people(self, people: List[Dict]) -> int:
        def _bulk_create(tx, people):
            result = tx.run("""
                UNWIND $people AS person
                CREATE (p:Person)
                SET p = person, p.created = datetime()
                RETURN count(p) AS created
            """, people=people)
            return result.single()["created"]
        
        with self._session() as session:
            return session.execute_write(_bulk_create, people)
    
    # Analytics
    def get_statistics(self) -> Dict:
        def _get_stats(tx):
            result = tx.run("""
                MATCH (p:Person)
                WITH count(p) AS personCount
                MATCH ()-[r:KNOWS]->()
                RETURN personCount, count(r) AS friendshipCount
            """)
            return dict(result.single())
        
        with self._session() as session:
            return session.execute_read(_get_stats)

# Usage
if __name__ == "__main__":
    repo = Neo4jRepository(
        "neo4j://localhost:7687",
        "neo4j",
        "password"
    )
    
    try:
        # Create people
        alice = repo.create_person("Alice", 30)
        bob = repo.create_person("Bob", 25)
        charlie = repo.create_person("Charlie", 35)
        
        print(f"Created: {alice['name']}, {bob['name']}, {charlie['name']}")
        
        # Create friendships
        repo.create_friendship("Alice", "Bob", "2020-01-01")
        repo.create_friendship("Bob", "Charlie", "2021-06-15")
        
        # Query
        friends = repo.get_friends("Alice")
        print(f"Alice's friends: {[f['name'] for f in friends]}")
        
        fof = repo.get_friends_of_friends("Alice")
        print(f"Friends of friends: {fof}")
        
        # Statistics
        stats = repo.get_statistics()
        print(f"Statistics: {stats}")
        
    finally:
        repo.close()
```

---

## Summary

### Key Concepts

| Concept | Best Practice |
|---------|---------------|
| Driver | Create once, reuse |
| Session | Short-lived, use context manager |
| Transaction | Use managed transactions |
| Results | Always consume |
| Parameters | Always use, never concatenate |
| Errors | Handle with retry for transient |

### Configuration Checklist

- ✅ Connection pool size for expected load
- ✅ Timeouts configured appropriately
- ✅ SSL/TLS for production
- ✅ Retry logic for transient errors
- ✅ Proper error handling
- ✅ Logging enabled

---

## Exercises

### Exercise 32.1: Connection Management
1. Implement a connection pool wrapper
2. Add health checks
3. Implement graceful shutdown

### Exercise 32.2: Repository Pattern
1. Create a generic repository class
2. Implement CRUD operations
3. Add transaction support

### Exercise 32.3: Async Operations
1. Convert sync code to async
2. Implement parallel queries
3. Measure performance difference

---

**Next Chapter: [Chapter 33: Building Applications](33-building-applications.md)**
