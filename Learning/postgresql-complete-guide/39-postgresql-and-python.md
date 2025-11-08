# PostgreSQL and Python

## Overview

Python is one of the most popular languages for working with PostgreSQL. This comprehensive guide covers database connectivity, ORMs (SQLAlchemy), connection pooling, async operations, migrations, and best practices for Python-PostgreSQL integration.

## Table of Contents

- [Python Database Drivers](#python-database-drivers)
- [psycopg2 Basics](#psycopg2-basics)
- [SQLAlchemy ORM](#sqlalchemy-orm)
- [Connection Pooling](#connection-pooling)
- [Async PostgreSQL](#async-postgresql)
- [Database Migrations](#database-migrations)
- [Query Builders](#query-builders)
- [Performance Optimization](#performance-optimization)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Python Database Drivers

### Available Drivers

```python
# PostgreSQL drivers for Python:

# 1. psycopg2 (most popular)
# - C-based, fast
# - Full PostgreSQL feature support
# - DB-API 2.0 compliant
import psycopg2

# 2. psycopg3 (modern, async support)
# - Pure Python and C implementations
# - Async/await support
# - Better typing
import psycopg

# 3. asyncpg (fastest async driver)
# - Async-only
# - Very high performance
# - Not DB-API compliant
import asyncpg

# 4. pg8000 (pure Python)
# - No C dependencies
# - Slower than psycopg2
# - Good for deployments without compilers
import pg8000

# Installing drivers:
# $ pip install psycopg2-binary  # Easiest
# $ pip install psycopg2  # From source (requires pg_config)
# $ pip install psycopg[binary]  # psycopg3
# $ pip install asyncpg
# $ pip install pg8000
```

## psycopg2 Basics

### Connecting to Database

```python
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

# Basic connection
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydb",
    user="postgres",
    password="password"
)

# Connection with connection string
conn = psycopg2.connect("postgresql://user:password@localhost:5432/mydb")

# Connection with parameters
conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="password",
    connect_timeout=3,
    application_name="my_python_app",
    options="-c statement_timeout=30000"  # 30 second timeout
)

# Using context manager (recommended)
with psycopg2.connect("postgresql://user:password@localhost/mydb") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        print(cur.fetchone())
# Connection automatically closed

# Connection parameters from environment
import os
conn = psycopg2.connect(
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", 5432)),
    database=os.getenv("PGDATABASE", "mydb"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD")
)
```

### Executing Queries

```python
import psycopg2

conn = psycopg2.connect("postgresql://user:password@localhost/mydb")
cur = conn.cursor()

# Simple query
cur.execute("SELECT * FROM users WHERE id = 1")
result = cur.fetchone()
print(result)  # Tuple: (1, 'Alice', 'alice@example.com')

# Fetch all results
cur.execute("SELECT * FROM users")
results = cur.fetchall()
for row in results:
    print(row)

# Fetch results as dictionaries
from psycopg2.extras import RealDictCursor
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT * FROM users WHERE id = 1")
result = cur.fetchone()
print(result)  # Dict: {'id': 1, 'username': 'Alice', 'email': 'alice@example.com'}
print(result['username'])  # Access by column name

# Parameterized queries (ALWAYS use this to prevent SQL injection)
user_id = 1
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# Named parameters
cur.execute(
    "SELECT * FROM users WHERE username = %(username)s AND email = %(email)s",
    {'username': 'alice', 'email': 'alice@example.com'}
)

# Insert data
cur.execute(
    "INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id",
    ('bob', 'bob@example.com')
)
new_id = cur.fetchone()[0]
conn.commit()  # Don't forget to commit!

# Update data
cur.execute(
    "UPDATE users SET email = %s WHERE id = %s",
    ('newemail@example.com', 1)
)
conn.commit()
print(f"Updated {cur.rowcount} rows")

# Delete data
cur.execute("DELETE FROM users WHERE id = %s", (1,))
conn.commit()

# Close cursor and connection
cur.close()
conn.close()
```

### Transactions

```python
import psycopg2

conn = psycopg2.connect("postgresql://user:password@localhost/mydb")

try:
    cur = conn.cursor()
    
    # Begin transaction (implicit with first query)
    cur.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", ('Alice', 1000))
    cur.execute("INSERT INTO accounts (name, balance) VALUES (%s, %s)", ('Bob', 1000))
    
    # Transfer money
    cur.execute("UPDATE accounts SET balance = balance - %s WHERE name = %s", (100, 'Alice'))
    cur.execute("UPDATE accounts SET balance = balance + %s WHERE name = %s", (100, 'Bob'))
    
    # Commit transaction
    conn.commit()
    print("Transaction committed successfully")
    
except psycopg2.Error as e:
    # Rollback on error
    conn.rollback()
    print(f"Transaction failed: {e}")
    
finally:
    cur.close()
    conn.close()

# Using context manager (auto commit/rollback)
with psycopg2.connect("postgresql://user:password@localhost/mydb") as conn:
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (username) VALUES (%s)", ('charlie',))
        # Automatically commits if no exception
        # Automatically rolls back on exception

# Savepoints
with conn.cursor() as cur:
    cur.execute("INSERT INTO users (username) VALUES (%s)", ('dave',))
    conn.commit()
    
    # Create savepoint
    cur.execute("SAVEPOINT my_savepoint")
    cur.execute("INSERT INTO users (username) VALUES (%s)", ('eve',))
    
    # Rollback to savepoint
    cur.execute("ROLLBACK TO SAVEPOINT my_savepoint")
    
    # Release savepoint
    cur.execute("RELEASE SAVEPOINT my_savepoint")
    conn.commit()
```

### Bulk Operations

```python
import psycopg2
from psycopg2.extras import execute_batch, execute_values

conn = psycopg2.connect("postgresql://user:password@localhost/mydb")
cur = conn.cursor()

# Bulk insert with execute_batch (batches multiple inserts)
data = [
    ('user1', 'user1@example.com'),
    ('user2', 'user2@example.com'),
    ('user3', 'user3@example.com'),
    # ... thousands more
]

execute_batch(
    cur,
    "INSERT INTO users (username, email) VALUES (%s, %s)",
    data,
    page_size=1000  # Batch size
)
conn.commit()

# Bulk insert with execute_values (single INSERT with multiple VALUES)
# Fastest method for bulk inserts
execute_values(
    cur,
    "INSERT INTO users (username, email) VALUES %s",
    data,
    page_size=1000
)
conn.commit()

# Bulk update with execute_batch
updates = [
    ('newemail1@example.com', 1),
    ('newemail2@example.com', 2),
    ('newemail3@example.com', 3),
]

execute_batch(
    cur,
    "UPDATE users SET email = %s WHERE id = %s",
    updates,
    page_size=1000
)
conn.commit()

# COPY for very large datasets (fastest)
import io
data_stream = io.StringIO()
for i in range(1000000):
    data_stream.write(f"user{i}\tuser{i}@example.com\n")
data_stream.seek(0)

cur.copy_from(data_stream, 'users', columns=('username', 'email'))
conn.commit()

cur.close()
conn.close()
```

## SQLAlchemy ORM

### Setting Up SQLAlchemy

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create engine
engine = create_engine(
    'postgresql://user:password@localhost:5432/mydb',
    echo=True,  # Log SQL queries
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max additional connections
    pool_pre_ping=True,  # Check connections before using
    pool_recycle=3600  # Recycle connections after 1 hour
)

# Create base class
Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    orders = relationship('Order', back_populates='user')
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship('User', back_populates='orders')
    
    def __repr__(self):
        return f"<Order(id={self.id}, total={self.total})>"

# Create tables
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)
session = Session()
```

### CRUD Operations with SQLAlchemy

```python
from sqlalchemy.orm import Session

# Create
new_user = User(username='alice', email='alice@example.com')
session.add(new_user)
session.commit()
print(f"Created user with ID: {new_user.id}")

# Create multiple
users = [
    User(username='bob', email='bob@example.com'),
    User(username='charlie', email='charlie@example.com'),
]
session.add_all(users)
session.commit()

# Read (query)
user = session.query(User).filter_by(username='alice').first()
print(user.email)

# Query with multiple filters
users = session.query(User).filter(
    User.username.like('a%'),
    User.email.contains('@example.com')
).all()

# Query with ordering
users = session.query(User).order_by(User.created_at.desc()).limit(10).all()

# Query with joins
from sqlalchemy import func
results = session.query(
    User.username,
    func.count(Order.id).label('order_count')
).join(Order).group_by(User.id).all()

for username, order_count in results:
    print(f"{username}: {order_count} orders")

# Update
user = session.query(User).filter_by(username='alice').first()
user.email = 'newalice@example.com'
session.commit()

# Bulk update
session.query(User).filter(User.username.like('test%')).update({
    User.email: 'test@example.com'
}, synchronize_session='fetch')
session.commit()

# Delete
user = session.query(User).filter_by(username='alice').first()
session.delete(user)
session.commit()

# Bulk delete
session.query(User).filter(User.username.like('temp%')).delete()
session.commit()

# Close session
session.close()
```

### Relationships and Joins

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://user:password@localhost/mydb')
Session = sessionmaker(bind=engine)
session = Session()

# Create user with orders
user = User(username='alice', email='alice@example.com')
order1 = Order(total=100)
order2 = Order(total=200)
user.orders = [order1, order2]

session.add(user)
session.commit()

# Access relationship
user = session.query(User).filter_by(username='alice').first()
print(f"User {user.username} has {len(user.orders)} orders")
for order in user.orders:
    print(f"  Order {order.id}: ${order.total}")

# Eager loading (prevent N+1 queries)
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.orders)).all()
for user in users:
    print(f"{user.username}: {len(user.orders)} orders")  # No additional queries

# Subquery loading
from sqlalchemy.orm import subqueryload

users = session.query(User).options(subqueryload(User.orders)).all()

# Complex query with relationships
results = session.query(User).join(Order).filter(Order.total > 100).all()

session.close()
```

## Connection Pooling

### psycopg2 Connection Pool

```python
from psycopg2 import pool
import threading

# Create connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # Min connections
    20,  # Max connections
    host="localhost",
    database="mydb",
    user="postgres",
    password="password"
)

# Get connection from pool
conn = connection_pool.getconn()

try:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    results = cur.fetchall()
    cur.close()
finally:
    # Return connection to pool
    connection_pool.putconn(conn)

# Thread-safe connection pool
class DatabasePool:
    def __init__(self, minconn, maxconn, **kwargs):
        self.pool = pool.ThreadedConnectionPool(minconn, maxconn, **kwargs)
        self.lock = threading.Lock()
    
    def get_connection(self):
        return self.pool.getconn()
    
    def return_connection(self, conn):
        self.pool.putconn(conn)
    
    def close_all(self):
        self.pool.closeall()

# Usage
db_pool = DatabasePool(
    1, 20,
    host="localhost",
    database="mydb",
    user="postgres",
    password="password"
)

conn = db_pool.get_connection()
try:
    # Use connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    cur.close()
finally:
    db_pool.return_connection(conn)

# Context manager for pool connections
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    conn = db_pool.get_connection()
    try:
        yield conn
    finally:
        db_pool.return_connection(conn)

# Usage
with get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    results = cur.fetchall()
    cur.close()
```

### SQLAlchemy Connection Pool

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, NullPool

# Default pool (QueuePool)
engine = create_engine(
    'postgresql://user:password@localhost/mydb',
    pool_size=10,  # Keep 10 connections
    max_overflow=20,  # Allow 20 additional connections
    pool_timeout=30,  # Wait 30 seconds for connection
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True  # Verify connections before use
)

# Custom pool
engine = create_engine(
    'postgresql://user:password@localhost/mydb',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0  # No overflow, fixed pool size
)

# No pooling (new connection each time)
engine = create_engine(
    'postgresql://user:password@localhost/mydb',
    poolclass=NullPool
)

# Monitor pool status
engine.pool.size()  # Current pool size
engine.pool.timeout()  # Pool timeout setting

# Dispose all connections
engine.dispose()
```

## Async PostgreSQL

### asyncpg Usage

```python
import asyncpg
import asyncio

async def main():
    # Connect
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='mydb'
    )
    
    # Execute query
    rows = await conn.fetch('SELECT * FROM users')
    for row in rows:
        print(dict(row))
    
    # Execute with parameters
    row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', 1)
    print(f"User: {row['username']}")
    
    # Insert
    await conn.execute(
        'INSERT INTO users (username, email) VALUES ($1, $2)',
        'alice', 'alice@example.com'
    )
    
    # Transaction
    async with conn.transaction():
        await conn.execute('INSERT INTO users (username) VALUES ($1)', 'bob')
        await conn.execute('INSERT INTO users (username) VALUES ($1)', 'charlie')
    
    # Prepared statement (faster for repeated queries)
    stmt = await conn.prepare('SELECT * FROM users WHERE id = $1')
    row = await stmt.fetchrow(1)
    print(row['username'])
    
    # Close connection
    await conn.close()

# Run async function
asyncio.run(main())

# Connection pool
async def with_pool():
    # Create pool
    pool = await asyncpg.create_pool(
        host='localhost',
        port=5432,
        user='postgres',
        password='password',
        database='mydb',
        min_size=10,
        max_size=20
    )
    
    # Acquire connection from pool
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM users')
        print(f"Found {len(rows)} users")
    
    # Close pool
    await pool.close()

asyncio.run(with_pool())

# Batch operations
async def batch_insert():
    conn = await asyncpg.connect('postgresql://user:password@localhost/mydb')
    
    data = [
        ('user1', 'user1@example.com'),
        ('user2', 'user2@example.com'),
        ('user3', 'user3@example.com'),
    ]
    
    await conn.executemany(
        'INSERT INTO users (username, email) VALUES ($1, $2)',
        data
    )
    
    await conn.close()

asyncio.run(batch_insert())
```

### Async SQLAlchemy (SQLAlchemy 2.0)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
import asyncio

# Create async engine
engine = create_async_engine(
    'postgresql+asyncpg://user:password@localhost/mydb',
    echo=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Use async session
async def main():
    async with AsyncSessionLocal() as session:
        # Query
        result = await session.execute(
            select(User).where(User.username == 'alice')
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"Found user: {user.username}")
        
        # Insert
        new_user = User(username='bob', email='bob@example.com')
        session.add(new_user)
        await session.commit()
        
        # Update
        result = await session.execute(
            select(User).where(User.username == 'bob')
        )
        user = result.scalar_one()
        user.email = 'newemail@example.com'
        await session.commit()

asyncio.run(main())
```

## Database Migrations

### Alembic Setup

```python
# Install Alembic
# $ pip install alembic

# Initialize Alembic
# $ alembic init alembic

# Configure alembic.ini
# sqlalchemy.url = postgresql://user:password@localhost/mydb

# Configure alembic/env.py
from myapp.models import Base

target_metadata = Base.metadata

# Create migration
# $ alembic revision --autogenerate -m "create users table"

# Apply migration
# $ alembic upgrade head

# Rollback migration
# $ alembic downgrade -1

# View migration history
# $ alembic history

# Migration file example (alembic/versions/xxx_create_users.py):
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('users')
"""

# Programmatic migrations
from alembic import command
from alembic.config import Config

alembic_cfg = Config("alembic.ini")
command.upgrade(alembic_cfg, "head")
```

## Query Builders

### SQL Composition with psycopg2.sql

```python
from psycopg2 import sql

# Safe dynamic table/column names
table_name = 'users'
column_name = 'username'

query = sql.SQL("SELECT {column} FROM {table} WHERE id = %s").format(
    column=sql.Identifier(column_name),
    table=sql.Identifier(table_name)
)

cur.execute(query, (1,))

# Dynamic INSERT
columns = ['username', 'email']
values = ['alice', 'alice@example.com']

query = sql.SQL("INSERT INTO users ({}) VALUES ({})").format(
    sql.SQL(', ').join(map(sql.Identifier, columns)),
    sql.SQL(', ').join(sql.Placeholder() * len(values))
)

cur.execute(query, values)

# Dynamic WHERE clause
filters = {'username': 'alice', 'email': 'alice@example.com'}

where_clause = sql.SQL(' AND ').join([
    sql.SQL("{} = {}").format(sql.Identifier(k), sql.Placeholder())
    for k in filters.keys()
])

query = sql.SQL("SELECT * FROM users WHERE {}").format(where_clause)
cur.execute(query, list(filters.values()))
```

## Performance Optimization

### Optimization Techniques

```python
import psycopg2
from psycopg2.extras import execute_values

conn = psycopg2.connect("postgresql://user:password@localhost/mydb")
cur = conn.cursor()

# 1. Use connection pooling (shown earlier)

# 2. Batch operations with execute_values
data = [(f'user{i}', f'user{i}@example.com') for i in range(10000)]
execute_values(cur, "INSERT INTO users (username, email) VALUES %s", data)
conn.commit()

# 3. Use COPY for bulk inserts
import io
csv_data = io.StringIO()
for i in range(100000):
    csv_data.write(f"user{i}\tuser{i}@example.com\n")
csv_data.seek(0)
cur.copy_from(csv_data, 'users', columns=('username', 'email'), sep='\t')
conn.commit()

# 4. Prepared statements (server-side)
cur.execute("PREPARE user_select AS SELECT * FROM users WHERE id = $1")
cur.execute("EXECUTE user_select (1)")
cur.execute("DEALLOCATE user_select")

# 5. Fetch in batches (for large result sets)
cur.execute("SELECT * FROM large_table")
while True:
    rows = cur.fetchmany(1000)  # Fetch 1000 rows at a time
    if not rows:
        break
    for row in rows:
        process(row)

# 6. Use server-side cursors for very large results
cur = conn.cursor(name='large_result_cursor')
cur.execute("SELECT * FROM very_large_table")
for row in cur:  # Fetches in batches automatically
    process(row)
cur.close()

# 7. Disable autocommit for bulk operations
conn.autocommit = False
for i in range(10000):
    cur.execute("INSERT INTO users (username) VALUES (%s)", (f'user{i}',))
conn.commit()
conn.autocommit = True

# 8. Use indexes (database side)
cur.execute("CREATE INDEX idx_users_username ON users(username)")
conn.commit()

cur.close()
conn.close()
```

## Error Handling

### Exception Handling

```python
import psycopg2
from psycopg2 import errors

try:
    conn = psycopg2.connect("postgresql://user:password@localhost/mydb")
    cur = conn.cursor()
    
    # Violate unique constraint
    cur.execute("INSERT INTO users (username) VALUES (%s)", ('alice',))
    cur.execute("INSERT INTO users (username) VALUES (%s)", ('alice',))  # Duplicate!
    conn.commit()
    
except psycopg2.IntegrityError as e:
    print(f"Integrity error: {e}")
    conn.rollback()

except psycopg2.OperationalError as e:
    print(f"Connection error: {e}")

except psycopg2.ProgrammingError as e:
    print(f"Programming error (SQL syntax): {e}")

except psycopg2.Error as e:
    print(f"Database error: {e}")
    conn.rollback()

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()

# Specific error codes
try:
    cur.execute("INSERT INTO users (username) VALUES (%s)", ('alice',))
    conn.commit()
except errors.UniqueViolation:
    print("Username already exists")
    conn.rollback()
except errors.ForeignKeyViolation:
    print("Foreign key constraint violated")
    conn.rollback()
except errors.NotNullViolation:
    print("NOT NULL constraint violated")
    conn.rollback()

# Retry logic
import time

def execute_with_retry(cur, query, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            cur.execute(query, params)
            return True
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
    return False
```

## Best Practices

### Best Practices Checklist

```python
# 1. Always use parameterized queries (prevent SQL injection)
# BAD:
# cur.execute(f"SELECT * FROM users WHERE username = '{username}'")

# GOOD:
cur.execute("SELECT * FROM users WHERE username = %s", (username,))

# 2. Use connection pooling for web applications
from psycopg2 import pool
connection_pool = pool.SimpleConnectionPool(5, 20, **db_params)

# 3. Always close connections and cursors
with psycopg2.connect(**db_params) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users")
# Automatically closed

# 4. Use transactions for data consistency
with conn:  # Auto commit/rollback
    with conn.cursor() as cur:
        cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
        cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")

# 5. Handle errors appropriately
try:
    cur.execute(query)
    conn.commit()
except psycopg2.Error as e:
    conn.rollback()
    logger.error(f"Database error: {e}")
    raise

# 6. Use bulk operations for large datasets
from psycopg2.extras import execute_values
execute_values(cur, "INSERT INTO users VALUES %s", data)

# 7. Set statement timeout
cur.execute("SET statement_timeout = '30s'")

# 8. Use connection strings from environment
import os
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)

# 9. Log slow queries (application side)
import time
start = time.time()
cur.execute(query)
duration = time.time() - start
if duration > 1.0:
    logger.warning(f"Slow query ({duration:.2f}s): {query}")

# 10. Use type hints for better code quality
from typing import List, Dict, Any

def get_users() -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM users")
            return cur.fetchall()
```

## Summary

PostgreSQL and Python integration provides:
- **psycopg2**: Industry-standard PostgreSQL driver
- **SQLAlchemy**: Powerful ORM for object-relational mapping
- **asyncpg**: High-performance async driver
- **Connection Pooling**: Efficient connection management
- **Alembic**: Database migrations
- **Performance**: Bulk operations, prepared statements, COPY

Python offers excellent PostgreSQL support for all application types.

## Next Steps

- Study [Query Optimization](./20-query-optimization.md)
- Learn [Monitoring and Logging](./38-monitoring-and-logging.md)
- Explore [Performance Troubleshooting](./40-performance-troubleshooting.md)
- Practice [Advanced SQL](./11-advanced-select.md)
