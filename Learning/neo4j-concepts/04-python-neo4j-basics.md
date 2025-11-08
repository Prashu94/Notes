# Neo4j with Python - Complete Implementation Guide

## Table of Contents
1. [Setup and Installation](#setup-and-installation)
2. [Connection Management](#connection-management)
3. [CRUD Operations](#crud-operations)
4. [Transactions](#transactions)
5. [Working with Results](#working-with-results)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [Practical Examples](#practical-examples)

---

## Setup and Installation

### Install Neo4j Python Driver

```bash
# Install neo4j driver
pip install neo4j

# Install additional helpful packages
pip install python-dotenv  # For environment variables
pip install pandas        # For data manipulation
```

### Get Neo4j Instance

**Option 1: Neo4j Desktop**
- Download from https://neo4j.com/download/
- Create a local database
- Start the database
- Note the URI (bolt://localhost:7687) and credentials

**Option 2: Neo4j AuraDB (Cloud)**
- Create free account at https://neo4j.com/cloud/aura/
- Create a database instance
- Download credentials
- Note the URI and password

**Option 3: Docker**
```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    neo4j:latest
```

---

## Connection Management

### Basic Connection

```python
from neo4j import GraphDatabase

# Connection configuration
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "your_password")

# Create driver instance
driver = GraphDatabase.driver(URI, auth=AUTH)

# Verify connection
driver.verify_connectivity()
print("Connection established!")

# Always close when done
driver.close()
```

### Connection with Context Manager

```python
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def verify_connectivity(self):
        self.driver.verify_connectivity()
        
# Usage with context manager
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    # Use driver here
# Automatically closes connection
```

### Production-Ready Connection Class

```python
from neo4j import GraphDatabase
from typing import Optional, Dict, Any, List
import logging

class Neo4jDatabase:
    """Neo4j database connection manager"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "neo4j"):
        """
        Initialize Neo4j connection
        
        Args:
            uri: Neo4j URI (e.g., bolt://localhost:7687)
            user: Username
            password: Password
            database: Database name (default: neo4j)
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
        self._connect()
        
    def _connect(self):
        """Establish database connection"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            logging.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logging.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logging.info("Neo4j connection closed")
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Execute a Cypher query
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Execute a write query in a transaction"""
        def _transaction_function(tx, query, parameters):
            result = tx.run(query, parameters)
            return [record.data() for record in result]
        
        with self.driver.session(database=self.database) as session:
            return session.execute_write(_transaction_function, query, parameters or {})
    
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Execute a read query"""
        def _transaction_function(tx, query, parameters):
            result = tx.run(query, parameters)
            return [record.data() for record in result]
        
        with self.driver.session(database=self.database) as session:
            return session.execute_read(_transaction_function, query, parameters or {})

# Usage
db = Neo4jDatabase(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="your_password"
)

try:
    # Use database
    results = db.execute_query("MATCH (n:Person) RETURN n LIMIT 5")
    print(results)
finally:
    db.close()
```

### Environment Variables

```python
# .env file
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# Python code
import os
from dotenv import load_dotenv

load_dotenv()

db = Neo4jDatabase(
    uri=os.getenv("NEO4J_URI"),
    user=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD"),
    database=os.getenv("NEO4J_DATABASE", "neo4j")
)
```

---

## CRUD Operations

### Create Operations

#### Create Nodes

```python
def create_person(driver, name: str, age: int, email: str):
    """Create a person node"""
    query = """
    CREATE (p:Person {
        name: $name,
        age: $age,
        email: $email,
        createdAt: datetime()
    })
    RETURN p
    """
    
    with driver.session() as session:
        result = session.run(query, name=name, age=age, email=email)
        record = result.single()
        return record["p"]

# Usage
person = create_person(driver, "Alice Johnson", 30, "alice@example.com")
print(f"Created: {person['name']}")
```

#### Create with MERGE (avoid duplicates)

```python
def get_or_create_person(driver, email: str, name: str, age: int):
    """Get existing person or create new one"""
    query = """
    MERGE (p:Person {email: $email})
    ON CREATE SET 
        p.name = $name,
        p.age = $age,
        p.createdAt = datetime()
    ON MATCH SET 
        p.lastSeen = datetime()
    RETURN p, 
           CASE WHEN p.createdAt = datetime() THEN 'created' ELSE 'existed' END AS status
    """
    
    with driver.session() as session:
        result = session.run(query, email=email, name=name, age=age)
        record = result.single()
        return record["p"], record["status"]

# Usage
person, status = get_or_create_person(driver, "alice@example.com", "Alice", 30)
print(f"Person {status}: {person['name']}")
```

#### Create Relationships

```python
def create_friendship(driver, person1_email: str, person2_email: str, since_date: str):
    """Create friendship relationship between two people"""
    query = """
    MATCH (p1:Person {email: $email1})
    MATCH (p2:Person {email: $email2})
    MERGE (p1)-[r:FRIENDS_WITH {since: date($since)}]->(p2)
    RETURN p1.name AS person1, p2.name AS person2, r.since AS since
    """
    
    with driver.session() as session:
        result = session.run(
            query, 
            email1=person1_email, 
            email2=person2_email, 
            since=since_date
        )
        record = result.single()
        return record

# Usage
friendship = create_friendship(driver, "alice@example.com", "bob@example.com", "2020-01-15")
print(f"{friendship['person1']} and {friendship['person2']} friends since {friendship['since']}")
```

#### Batch Create

```python
def batch_create_people(driver, people_list: List[Dict]):
    """Create multiple people efficiently"""
    query = """
    UNWIND $people AS person
    CREATE (p:Person {
        name: person.name,
        age: person.age,
        email: person.email,
        city: person.city
    })
    RETURN count(p) AS created
    """
    
    with driver.session() as session:
        result = session.run(query, people=people_list)
        record = result.single()
        return record["created"]

# Usage
people = [
    {"name": "Alice", "age": 30, "email": "alice@example.com", "city": "SF"},
    {"name": "Bob", "age": 35, "email": "bob@example.com", "city": "NY"},
    {"name": "Charlie", "age": 28, "email": "charlie@example.com", "city": "SF"}
]
count = batch_create_people(driver, people)
print(f"Created {count} people")
```

### Read Operations

#### Find Single Node

```python
def find_person_by_email(driver, email: str) -> Optional[Dict]:
    """Find person by email"""
    query = """
    MATCH (p:Person {email: $email})
    RETURN p
    """
    
    with driver.session() as session:
        result = session.run(query, email=email)
        record = result.single()
        return dict(record["p"]) if record else None

# Usage
person = find_person_by_email(driver, "alice@example.com")
if person:
    print(f"Found: {person['name']}, age {person['age']}")
else:
    print("Person not found")
```

#### Find Multiple Nodes

```python
def find_people_by_city(driver, city: str) -> List[Dict]:
    """Find all people in a city"""
    query = """
    MATCH (p:Person {city: $city})
    RETURN p.name AS name, p.age AS age, p.email AS email
    ORDER BY p.age DESC
    """
    
    with driver.session() as session:
        result = session.run(query, city=city)
        return [dict(record) for record in result]

# Usage
people = find_people_by_city(driver, "San Francisco")
for person in people:
    print(f"{person['name']}, {person['age']}")
```

#### Find with Relationships

```python
def get_friends(driver, person_email: str) -> List[Dict]:
    """Get all friends of a person"""
    query = """
    MATCH (p:Person {email: $email})-[r:FRIENDS_WITH]->(friend:Person)
    RETURN friend.name AS name, 
           friend.email AS email, 
           r.since AS friendsSince
    ORDER BY r.since
    """
    
    with driver.session() as session:
        result = session.run(query, email=person_email)
        return [dict(record) for record in result]

# Usage
friends = get_friends(driver, "alice@example.com")
for friend in friends:
    print(f"{friend['name']} (friends since {friend['friendsSince']})")
```

#### Complex Pattern Matching

```python
def find_friends_of_friends(driver, person_email: str) -> List[Dict]:
    """Find friends of friends (2nd degree connections)"""
    query = """
    MATCH (p:Person {email: $email})-[:FRIENDS_WITH*2]-(fof:Person)
    WHERE p <> fof
    AND NOT (p)-[:FRIENDS_WITH]-(fof)
    RETURN DISTINCT fof.name AS name, 
           fof.email AS email,
           fof.city AS city
    LIMIT 10
    """
    
    with driver.session() as session:
        result = session.run(query, email=person_email)
        return [dict(record) for record in result]
```

#### Aggregation Queries

```python
def get_statistics(driver) -> Dict:
    """Get database statistics"""
    query = """
    MATCH (p:Person)
    RETURN count(p) AS totalPeople,
           avg(p.age) AS avgAge,
           min(p.age) AS minAge,
           max(p.age) AS maxAge,
           count(DISTINCT p.city) AS uniqueCities
    """
    
    with driver.session() as session:
        result = session.run(query)
        return dict(result.single())

# Usage
stats = get_statistics(driver)
print(f"Total people: {stats['totalPeople']}")
print(f"Average age: {stats['avgAge']:.1f}")
```

### Update Operations

#### Update Node Properties

```python
def update_person_age(driver, email: str, new_age: int):
    """Update person's age"""
    query = """
    MATCH (p:Person {email: $email})
    SET p.age = $age, p.updatedAt = datetime()
    RETURN p
    """
    
    with driver.session() as session:
        result = session.run(query, email=email, age=new_age)
        record = result.single()
        return dict(record["p"]) if record else None
```

#### Update Multiple Properties

```python
def update_person(driver, email: str, updates: Dict):
    """Update multiple person properties"""
    # Build SET clause dynamically
    set_clauses = ", ".join([f"p.{key} = ${key}" for key in updates.keys()])
    query = f"""
    MATCH (p:Person {{email: $email}})
    SET {set_clauses}, p.updatedAt = datetime()
    RETURN p
    """
    
    params = {"email": email, **updates}
    
    with driver.session() as session:
        result = session.run(query, **params)
        record = result.single()
        return dict(record["p"]) if record else None

# Usage
updated = update_person(driver, "alice@example.com", {
    "age": 31,
    "city": "New York",
    "phone": "555-1234"
})
```

#### Add Labels

```python
def add_employee_label(driver, email: str, company: str):
    """Add Employee label to person"""
    query = """
    MATCH (p:Person {email: $email})
    SET p:Employee, p.company = $company
    RETURN p
    """
    
    with driver.session() as session:
        result = session.run(query, email=email, company=company)
        record = result.single()
        return dict(record["p"]) if record else None
```

### Delete Operations

#### Delete Node

```python
def delete_person(driver, email: str) -> bool:
    """Delete person and all relationships"""
    query = """
    MATCH (p:Person {email: $email})
    DETACH DELETE p
    RETURN count(p) AS deleted
    """
    
    with driver.session() as session:
        result = session.run(query, email=email)
        record = result.single()
        return record["deleted"] > 0

# Usage
deleted = delete_person(driver, "temp@example.com")
print(f"Person deleted: {deleted}")
```

#### Delete Relationship

```python
def remove_friendship(driver, email1: str, email2: str):
    """Remove friendship between two people"""
    query = """
    MATCH (p1:Person {email: $email1})-[r:FRIENDS_WITH]-(p2:Person {email: $email2})
    DELETE r
    RETURN count(r) AS deleted
    """
    
    with driver.session() as session:
        result = session.run(query, email1=email1, email2=email2)
        record = result.single()
        return record["deleted"]
```

#### Conditional Delete

```python
def delete_inactive_users(driver, days_inactive: int):
    """Delete users who haven't been seen in X days"""
    query = """
    MATCH (p:Person)
    WHERE p.lastSeen < datetime() - duration({days: $days})
    DETACH DELETE p
    RETURN count(p) AS deleted
    """
    
    with driver.session() as session:
        result = session.run(query, days=days_inactive)
        record = result.single()
        return record["deleted"]
```

---

## Transactions

### Explicit Transactions

```python
def transfer_friendship(driver, from_email: str, to_email: str, friend_email: str):
    """
    Transfer a friendship from one person to another atomically
    Either both operations succeed or both fail
    """
    def _transaction_function(tx):
        # Remove old friendship
        tx.run("""
            MATCH (p1:Person {email: $from_email})-[r:FRIENDS_WITH]-(friend:Person {email: $friend_email})
            DELETE r
        """, from_email=from_email, friend_email=friend_email)
        
        # Create new friendship
        result = tx.run("""
            MATCH (p2:Person {email: $to_email})
            MATCH (friend:Person {email: $friend_email})
            CREATE (p2)-[r:FRIENDS_WITH]->(friend)
            RETURN r
        """, to_email=to_email, friend_email=friend_email)
        
        return result.single()
    
    with driver.session() as session:
        return session.execute_write(_transaction_function)
```

### Transaction with Retry Logic

```python
from neo4j.exceptions import ServiceUnavailable, TransientError
import time

def execute_with_retry(driver, transaction_function, max_retries=3):
    """Execute transaction with automatic retry on transient errors"""
    for attempt in range(max_retries):
        try:
            with driver.session() as session:
                return session.execute_write(transaction_function)
        except (ServiceUnavailable, TransientError) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Transaction failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

### Read and Write Transactions

```python
def get_and_update_counter(driver, counter_name: str):
    """
    Safely increment a counter using read and write transactions
    """
    # Read transaction
    def _read_counter(tx):
        result = tx.run("""
            MATCH (c:Counter {name: $name})
            RETURN c.value AS value
        """, name=counter_name)
        record = result.single()
        return record["value"] if record else 0
    
    # Write transaction
    def _increment_counter(tx, new_value):
        result = tx.run("""
            MERGE (c:Counter {name: $name})
            SET c.value = $value
            RETURN c.value AS value
        """, name=counter_name, value=new_value)
        return result.single()["value"]
    
    with driver.session() as session:
        # Read current value
        current = session.execute_read(_read_counter)
        # Increment
        new_value = current + 1
        # Write new value
        return session.execute_write(_increment_counter, new_value)
```

---

## Working with Results

### Accessing Result Records

```python
def demonstrate_results(driver):
    """Show different ways to work with results"""
    
    with driver.session() as session:
        # Get single record
        result = session.run("MATCH (p:Person {email: $email}) RETURN p", 
                            email="alice@example.com")
        record = result.single()
        if record:
            person = record["p"]
            print(f"Name: {person['name']}")
        
        # Iterate over multiple records
        result = session.run("MATCH (p:Person) RETURN p.name AS name, p.age AS age")
        for record in result:
            print(f"{record['name']}: {record['age']}")
        
        # Convert to list
        result = session.run("MATCH (p:Person) RETURN p")
        people = [dict(record["p"]) for record in result]
        
        # Get all data at once
        result = session.run("MATCH (p:Person) RETURN p.name AS name")
        records = result.data()  # List of dicts
        print(records)
```

### Converting to DataFrames

```python
import pandas as pd

def query_to_dataframe(driver, query: str, parameters: dict = None) -> pd.DataFrame:
    """Execute query and return results as pandas DataFrame"""
    with driver.session() as session:
        result = session.run(query, parameters or {})
        return pd.DataFrame([record.data() for record in result])

# Usage
df = query_to_dataframe(driver, """
    MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
    RETURN p.name AS employee, c.name AS company, p.age AS age
    ORDER BY age DESC
""")
print(df.head())
print(df.describe())
```

### Working with Complex Objects

```python
def get_person_with_relationships(driver, email: str) -> Dict:
    """Get person with all their relationships"""
    query = """
    MATCH (p:Person {email: $email})
    OPTIONAL MATCH (p)-[r:FRIENDS_WITH]->(friend:Person)
    OPTIONAL MATCH (p)-[:WORKS_FOR]->(company:Company)
    RETURN p, 
           collect(DISTINCT friend.name) AS friends,
           company.name AS company
    """
    
    with driver.session() as session:
        result = session.run(query, email=email)
        record = result.single()
        
        if not record:
            return None
        
        return {
            "person": dict(record["p"]),
            "friends": record["friends"],
            "company": record["company"]
        }

# Usage
data = get_person_with_relationships(driver, "alice@example.com")
print(f"Person: {data['person']['name']}")
print(f"Friends: {', '.join(data['friends'])}")
print(f"Company: {data['company']}")
```

---

## Error Handling

### Comprehensive Error Handling

```python
from neo4j.exceptions import (
    ServiceUnavailable,
    AuthError,
    CypherSyntaxError,
    ConstraintError,
    TransientError
)

def safe_execute_query(driver, query: str, parameters: dict = None):
    """Execute query with comprehensive error handling"""
    try:
        with driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
            
    except AuthError:
        print("Authentication failed - check credentials")
        raise
        
    except ServiceUnavailable:
        print("Database unavailable - check connection")
        raise
        
    except CypherSyntaxError as e:
        print(f"Cypher syntax error: {e}")
        raise
        
    except ConstraintError as e:
        print(f"Constraint violation: {e}")
        # Handle duplicate or constraint errors
        return None
        
    except TransientError as e:
        print(f"Transient error - retry may succeed: {e}")
        raise
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
```

### Validation Before Query

```python
def create_person_safe(driver, email: str, name: str, age: int):
    """Create person with validation"""
    # Validate input
    if not email or "@" not in email:
        raise ValueError("Invalid email address")
    
    if age < 0 or age > 150:
        raise ValueError("Age must be between 0 and 150")
    
    # Check if person already exists
    existing = find_person_by_email(driver, email)
    if existing:
        raise ValueError(f"Person with email {email} already exists")
    
    # Create person
    return create_person(driver, name, age, email)
```

---

## Best Practices

### 1. Use Parameterized Queries (Always!)

```python
# ❌ BAD - SQL injection-style vulnerability
def bad_query(driver, name):
    query = f"MATCH (p:Person {{name: '{name}'}}) RETURN p"
    # Dangerous if name contains malicious code
    
# ✅ GOOD - Parameterized
def good_query(driver, name):
    query = "MATCH (p:Person {name: $name}) RETURN p"
    with driver.session() as session:
        return session.run(query, name=name)
```

### 2. Use Connection Pooling

```python
# Driver automatically pools connections
driver = GraphDatabase.driver(
    uri,
    auth=(user, password),
    max_connection_pool_size=50,
    connection_acquisition_timeout=60
)
```

### 3. Close Resources Properly

```python
# ✅ Use context managers
with driver.session() as session:
    result = session.run(query)
    data = [record.data() for record in result]
# Session automatically closed

# Or ensure driver is closed
try:
    driver = GraphDatabase.driver(uri, auth=auth)
    # use driver
finally:
    driver.close()
```

### 4. Batch Operations

```python
def batch_create_with_relationships(driver, batch_size=1000):
    """Create nodes and relationships in batches"""
    query = """
    UNWIND $batch AS item
    MERGE (p:Person {email: item.email})
    SET p.name = item.name, p.age = item.age
    WITH p, item
    UNWIND item.friends AS friendEmail
    MATCH (friend:Person {email: friendEmail})
    MERGE (p)-[:FRIENDS_WITH]->(friend)
    """
    
    # Process data in chunks
    all_data = get_large_dataset()  # Your data source
    
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i:i + batch_size]
        with driver.session() as session:
            session.run(query, batch=batch)
        print(f"Processed {i + len(batch)} records")
```

### 5. Type Hints and Documentation

```python
from typing import List, Dict, Optional

def find_people(
    driver: GraphDatabase.driver,
    city: Optional[str] = None,
    min_age: int = 0,
    max_age: int = 150,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Find people matching criteria
    
    Args:
        driver: Neo4j driver instance
        city: Filter by city (optional)
        min_age: Minimum age (default: 0)
        max_age: Maximum age (default: 150)
        limit: Maximum results (default: 100)
        
    Returns:
        List of person dictionaries
        
    Raises:
        ValueError: If age range is invalid
    """
    if min_age > max_age:
        raise ValueError("min_age must be <= max_age")
    
    query = """
    MATCH (p:Person)
    WHERE p.age >= $min_age AND p.age <= $max_age
    AND ($city IS NULL OR p.city = $city)
    RETURN p
    LIMIT $limit
    """
    
    with driver.session() as session:
        result = session.run(
            query, 
            city=city, 
            min_age=min_age, 
            max_age=max_age, 
            limit=limit
        )
        return [dict(record["p"]) for record in result]
```

---

## Practical Examples

### Complete Example: User Management System

See the next file: `05-sample-application.md` for a complete working application.

### Quick Example: Simple Blog System

```python
class BlogSystem:
    def __init__(self, driver):
        self.driver = driver
    
    def create_user(self, username: str, email: str):
        query = """
        CREATE (u:User {
            username: $username,
            email: $email,
            createdAt: datetime()
        })
        RETURN u
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, email=email)
            return dict(result.single()["u"])
    
    def create_post(self, username: str, title: str, content: str):
        query = """
        MATCH (u:User {username: $username})
        CREATE (p:Post {
            title: $title,
            content: $content,
            createdAt: datetime()
        })
        CREATE (u)-[:AUTHORED]->(p)
        RETURN p
        """
        with self.driver.session() as session:
            result = session.run(
                query, 
                username=username, 
                title=title, 
                content=content
            )
            return dict(result.single()["p"])
    
    def add_comment(self, username: str, post_id: str, text: str):
        query = """
        MATCH (u:User {username: $username})
        MATCH (p:Post)
        WHERE id(p) = $post_id
        CREATE (c:Comment {
            text: $text,
            createdAt: datetime()
        })
        CREATE (u)-[:COMMENTED]->(c)
        CREATE (c)-[:ON_POST]->(p)
        RETURN c
        """
        with self.driver.session() as session:
            result = session.run(
                query, 
                username=username, 
                post_id=post_id, 
                text=text
            )
            return dict(result.single()["c"])
    
    def get_user_feed(self, username: str, limit: int = 20):
        query = """
        MATCH (u:User {username: $username})-[:FOLLOWS]->(author:User)
        MATCH (author)-[:AUTHORED]->(post:Post)
        RETURN post.title AS title,
               post.content AS content,
               author.username AS author,
               post.createdAt AS createdAt
        ORDER BY post.createdAt DESC
        LIMIT $limit
        """
        with self.driver.session() as session:
            result = session.run(query, username=username, limit=limit)
            return [dict(record) for record in result]

# Usage
driver = GraphDatabase.driver(URI, auth=AUTH)
blog = BlogSystem(driver)

# Create users
blog.create_user("alice", "alice@example.com")
blog.create_user("bob", "bob@example.com")

# Create post
post = blog.create_post("alice", "My First Post", "Hello, Neo4j!")

# Get feed
feed = blog.get_user_feed("bob")
```

---

**Next:** Proceed to [05-sample-application.md](05-sample-application.md) for a complete social network application implementation.
