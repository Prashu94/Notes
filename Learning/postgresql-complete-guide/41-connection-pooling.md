# Connection Pooling

## Overview

Connection pooling is a critical performance optimization technique that maintains a pool of reusable database connections, significantly reducing the overhead of establishing new connections for each database operation. This comprehensive guide covers pooling concepts, implementations (PgBouncer, Pgpool-II, application-level pooling), configuration tuning, monitoring, and best practices.

## Table of Contents

- [Why Connection Pooling](#why-connection-pooling)
- [Connection Overhead](#connection-overhead)
- [Pooling Architectures](#pooling-architectures)
- [PgBouncer](#pgbouncer)
- [Pgpool-II](#pgpool-ii)
- [Application-Level Pooling](#application-level-pooling)
- [Pool Sizing](#pool-sizing)
- [Monitoring Pooling](#monitoring-pooling)
- [Best Practices](#best-practices)

## Why Connection Pooling

### Performance Benefits

```sql
-- Without pooling: Creating new connection for each request
-- Connection establishment overhead:
-- 1. TCP handshake: ~1-5ms
-- 2. PostgreSQL authentication: ~5-20ms
-- 3. Session initialization: ~2-10ms
-- Total: ~8-35ms per connection

-- For 1000 requests/second:
-- Without pooling: 8000-35000ms wasted time
-- With pooling: ~0ms (reuse existing connections)

-- Measuring connection overhead
SELECT
    COUNT(*) AS total_connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active_connections,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle_connections,
    COUNT(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_transaction
FROM pg_stat_activity
WHERE backend_type = 'client backend';

-- PostgreSQL connection limits
SHOW max_connections; -- Default: 100

-- Connection costs
-- Each connection consumes:
-- - Memory: ~2-10 MB per connection
-- - File descriptors: 1 per connection
-- - Context switching overhead

-- Example: 1000 concurrent connections
-- Memory: 2-10 GB just for connections!
-- With pooling: 20-50 actual connections, much lower memory usage
```

### Resource Management

```sql
-- Check current connection usage
SELECT
    datname,
    COUNT(*) AS connections,
    max_conn,
    ROUND(100.0 * COUNT(*) / max_conn, 2) AS pct_used
FROM pg_stat_activity,
    (SELECT setting::int AS max_conn FROM pg_settings WHERE name = 'max_connections') mc
WHERE datname IS NOT NULL
GROUP BY datname, max_conn
ORDER BY connections DESC;

-- Connection pooling benefits:
-- 1. Reduces connection establishment overhead
-- 2. Limits concurrent connections to prevent resource exhaustion
-- 3. Enables connection reuse across requests
-- 4. Provides connection queuing when pool is exhausted
-- 5. Enables connection health checks
-- 6. Improves application scalability

-- Without pooling problems:
-- - Connection storms during traffic spikes
-- - "FATAL: too many connections" errors
-- - High memory consumption
-- - CPU overhead from connection management
-- - Slow application response times
```

## Connection Overhead

### Connection Lifecycle

```sql
-- Connection establishment phases
-- 1. TCP Connection
--    - Client initiates TCP handshake
--    - SYN, SYN-ACK, ACK packets
--    - Time: ~1-5ms (local), ~50-200ms (remote)

-- 2. PostgreSQL Startup
--    - Send startup packet
--    - Negotiate protocol version
--    - Time: ~1-5ms

-- 3. Authentication
--    - Send authentication request
--    - Client sends credentials
--    - Verify credentials
--    - Time: ~5-20ms (depends on method: md5, scram-sha-256, etc.)

-- 4. Backend Process Initialization
--    - Fork backend process (or use existing from connection pool)
--    - Initialize session variables
--    - Load shared memory
--    - Time: ~2-10ms

-- 5. Ready for Query
--    - Connection established
--    - Total time: ~8-35ms minimum

-- Measuring connection time
SELECT
    NOW() AS connection_time,
    backend_start,
    NOW() - backend_start AS connection_age
FROM pg_stat_activity
WHERE pid = pg_backend_pid();

-- Connection termination overhead
-- 1. Send close message
-- 2. Clean up session state
-- 3. Close backend process
-- 4. Release resources
-- Time: ~2-10ms

-- Connection pooling eliminates this overhead by reusing connections
```

## Pooling Architectures

### Pooling Models

```text
1. Session Pooling (Connection Pooling)
   - Client gets exclusive connection for entire session
   - Connection returned to pool when client disconnects
   - Supports all PostgreSQL features
   - Use case: Long-lived connections, complex transactions

   [Client 1] ----> [Pool] ----> [Connection A] ----> [PostgreSQL]
   [Client 2] ----> [Pool] ----> [Connection B] ----> [PostgreSQL]
   [Client 3] ----> [Pool] ----> [Connection C] ----> [PostgreSQL]

2. Transaction Pooling
   - Connection assigned for duration of transaction
   - Returned to pool after COMMIT or ROLLBACK
   - More efficient than session pooling
   - Does NOT support:
     - Prepared statements across transactions
     - Temporary tables
     - Session-level settings (unless reset)
   - Use case: Web applications with short transactions

   [Client 1] ----> [Pool] <----> [Connection A] <----> [PostgreSQL]
                             \
   [Client 2] ----> [Pool] -----> [Connection B] <----> [PostgreSQL]

3. Statement Pooling
   - Connection returned after each statement
   - Most aggressive pooling mode
   - Does NOT support:
     - Multi-statement transactions
     - Prepared statements
     - Temporary tables
     - Session variables
   - Use case: Read-only queries, stateless applications

   [Client 1 Query 1] ----> [Pool] ----> [Conn A] ----> [PostgreSQL]
   [Client 2 Query 1] ----> [Pool] ----> [Conn A] ----> [PostgreSQL]
   [Client 1 Query 2] ----> [Pool] ----> [Conn B] ----> [PostgreSQL]

Recommendation:
- Use Session Pooling for complex applications
- Use Transaction Pooling for web applications (most common)
- Use Statement Pooling only for simple read-only workloads
```

### Architecture Patterns

```text
1. Client-Side Pooling (Application-Level)
   [App Server 1] ---> [App Pool] ----> [PostgreSQL]
   [App Server 2] ---> [App Pool] ----> [PostgreSQL]
   [App Server 3] ---> [App Pool] ----> [PostgreSQL]
   
   Pros: Simple, language-specific, no additional infrastructure
   Cons: Each app server maintains separate pool, less efficient

2. Server-Side Pooling (PgBouncer/Pgpool)
   [App Server 1] ------\
   [App Server 2] --------> [PgBouncer] ----> [PostgreSQL]
   [App Server 3] ------/
   
   Pros: Centralized, efficient, supports multiple apps
   Cons: Additional infrastructure, single point of failure

3. Hybrid Pooling (Both)
   [App 1] --> [App Pool] --\
   [App 2] --> [App Pool] ----> [PgBouncer] ----> [PostgreSQL]
   [App 3] --> [App Pool] --/
   
   Pros: Best of both worlds
   Cons: More complex, harder to tune
```

## PgBouncer

### Installation and Configuration

```bash
# Install PgBouncer (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install pgbouncer

# Install PgBouncer (macOS with Homebrew)
brew install pgbouncer

# Configuration file: /etc/pgbouncer/pgbouncer.ini
```

```ini
# pgbouncer.ini

[databases]
# Database connection strings
mydb = host=localhost port=5432 dbname=mydb
production_db = host=db.example.com port=5432 dbname=proddb user=appuser password=secret

# Fallback connection
* = host=localhost port=5432

[pgbouncer]
# Listen address and port
listen_addr = 0.0.0.0
listen_port = 6432

# Authentication
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Admin users
admin_users = admin_user

# Pool mode (session, transaction, statement)
pool_mode = transaction

# Connection limits
max_client_conn = 1000        # Max client connections
default_pool_size = 25        # Connections per pool
min_pool_size = 5             # Minimum connections to maintain
reserve_pool_size = 5         # Additional emergency connections
reserve_pool_timeout = 3      # Seconds before using reserve pool

# Server connection settings
server_lifetime = 3600        # Close server connection after 1 hour
server_idle_timeout = 600     # Close idle server connection after 10 min
server_connect_timeout = 15   # Timeout for connecting to PostgreSQL

# Client connection settings
client_idle_timeout = 0       # Never close idle client connections
client_login_timeout = 60     # Timeout for client login

# DNS settings
dns_max_ttl = 15
dns_nxdomain_ttl = 15

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1

# Stats period
stats_period = 60

# Verbose logging (0=off, 1=on, 2=verbose)
verbose = 0

# PID file
pidfile = /var/run/pgbouncer/pgbouncer.pid

# Unix socket
unix_socket_dir = /var/run/postgresql
unix_socket_mode = 0777
unix_socket_group = postgres
```

### User Authentication

```bash
# Create userlist.txt file for authentication
# Format: "username" "password"

# For MD5 authentication, get hashed password from PostgreSQL
psql -U postgres -c "SELECT rolpassword FROM pg_authid WHERE rolname = 'myuser';"

# userlist.txt
cat > /etc/pgbouncer/userlist.txt << EOF
"myuser" "md5..."
"appuser" "md5..."
EOF

# Set permissions
chmod 600 /etc/pgbouncer/userlist.txt
chown pgbouncer:pgbouncer /etc/pgbouncer/userlist.txt

# Start PgBouncer
sudo systemctl start pgbouncer
sudo systemctl enable pgbouncer

# Check status
sudo systemctl status pgbouncer

# View logs
sudo tail -f /var/log/postgresql/pgbouncer.log
```

### PgBouncer Administration

```sql
-- Connect to PgBouncer admin console
psql -h localhost -p 6432 -U admin_user pgbouncer

-- Show pools
SHOW POOLS;
-- Output columns:
-- database | user | cl_active | cl_waiting | sv_active | sv_idle | sv_used | sv_tested | sv_login | maxwait | pool_mode

-- Show statistics
SHOW STATS;
-- Output:
-- database | total_xact_count | total_query_count | total_received | total_sent | total_xact_time | total_query_time | total_wait_time | avg_xact_count | avg_query_count | avg_recv | avg_sent | avg_xact_time | avg_query_time | avg_wait_time

-- Show clients
SHOW CLIENTS;
-- Shows all connected clients

-- Show servers
SHOW SERVERS;
-- Shows all server connections to PostgreSQL

-- Show databases
SHOW DATABASES;

-- Show configuration
SHOW CONFIG;

-- Pause database (drain connections)
PAUSE mydb;

-- Resume database
RESUME mydb;

-- Reload configuration
RELOAD;

-- Shutdown PgBouncer gracefully
SHUTDOWN;

-- Kill a client connection
KILL client_id;

-- Enable/disable a database
DISABLE mydb;
ENABLE mydb;
```

### PgBouncer Monitoring

```bash
# Monitor PgBouncer with psql
watch -n 1 "psql -h localhost -p 6432 -U admin_user pgbouncer -c 'SHOW POOLS' -c 'SHOW STATS'"

# Check for waiting clients
psql -h localhost -p 6432 -U admin_user pgbouncer -c "SELECT database, cl_waiting FROM SHOW POOLS WHERE cl_waiting > 0;"

# Monitor average query time
psql -h localhost -p 6432 -U admin_user pgbouncer -c "SELECT database, avg_query_time FROM SHOW STATS ORDER BY avg_query_time DESC;"
```

## Pgpool-II

### Installation and Configuration

```bash
# Install Pgpool-II (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install pgpool2

# Configuration file: /etc/pgpool2/pgpool.conf
```

```conf
# pgpool.conf

# Connection pooling
listen_addresses = '*'
port = 9999

# Backend connections
backend_hostname0 = 'localhost'
backend_port0 = 5432
backend_weight0 = 1
backend_data_directory0 = '/var/lib/postgresql/14/main'
backend_flag0 = 'ALLOW_TO_FAILOVER'

# For replication, add more backends:
# backend_hostname1 = 'standby-host'
# backend_port1 = 5432
# backend_weight1 = 1
# backend_data_directory1 = '/var/lib/postgresql/14/standby'
# backend_flag1 = 'ALLOW_TO_FAILOVER'

# Connection pooling
num_init_children = 32          # Number of concurrent sessions
max_pool = 4                    # Connection pool size per child
child_life_time = 300           # Child process lifetime (seconds)
child_max_connections = 0       # Max connections per child (0=unlimited)
connection_life_time = 0        # Connection lifetime (0=unlimited)
client_idle_limit = 0           # Disconnect idle clients (0=disabled)

# Load balancing
load_balance_mode = on
black_function_list = 'nextval,setval,lastval'  # Don't load balance these

# Replication
replication_mode = off
replicate_select = off

# Master/Slave mode
master_slave_mode = off
master_slave_sub_mode = 'stream'

# Connection cache
connection_cache = on
reset_query_list = 'ABORT; DISCARD ALL'

# Health check
health_check_period = 10        # Health check interval (seconds)
health_check_timeout = 20       # Health check timeout
health_check_user = 'pgpool'
health_check_password = ''
health_check_database = 'postgres'
health_check_max_retries = 3
health_check_retry_delay = 1

# Failover and failback
failover_command = ''
failback_command = ''
fail_over_on_backend_error = off

# Logging
log_destination = 'stderr'
log_line_prefix = '%t: pid %p: '
log_connections = on
log_hostname = on
log_statement = off
log_per_node_statement = off

# PID file
pid_file_name = '/var/run/pgpool/pgpool.pid'

# Authentication
enable_pool_hba = on
pool_passwd = 'pool_passwd'
```

### Pool HBA Configuration

```conf
# /etc/pgpool2/pool_hba.conf
# Similar to pg_hba.conf

# TYPE  DATABASE    USER        ADDRESS         METHOD
local   all         all                         trust
host    all         all         127.0.0.1/32    md5
host    all         all         ::1/128         md5
host    all         all         0.0.0.0/0       md5
```

### Starting Pgpool-II

```bash
# Start Pgpool-II
sudo systemctl start pgpool2
sudo systemctl enable pgpool2

# Check status
sudo systemctl status pgpool2

# View logs
sudo tail -f /var/log/pgpool2/pgpool.log

# Reload configuration
sudo pgpool reload

# Stop Pgpool-II
sudo pgpool stop

# Show pool status
psql -h localhost -p 9999 -U postgres -c "SHOW POOL_NODES;"
```

## Application-Level Pooling

### Node.js (pg)

```javascript
const { Pool } = require('pg');

// Create connection pool
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'password',
  max: 20,                    // Maximum pool size
  min: 5,                     // Minimum pool size
  idleTimeoutMillis: 30000,   // Close idle connections after 30 seconds
  connectionTimeoutMillis: 2000, // Return error if no connection available
  maxUses: 7500,              // Close connection after 7500 uses
});

// Query using pool (auto-manages connections)
async function queryExample() {
  const res = await pool.query('SELECT * FROM users WHERE id = $1', [1]);
  console.log(res.rows[0]);
}

// Acquire client for transaction
async function transactionExample() {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('INSERT INTO users (username) VALUES ($1)', ['alice']);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release(); // Return to pool
  }
}

// Monitor pool
pool.on('connect', (client) => {
  console.log('New client connected');
});

pool.on('acquire', (client) => {
  console.log('Client acquired from pool');
});

pool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
});

// Graceful shutdown
async function shutdown() {
  await pool.end();
  console.log('Pool closed');
}

process.on('SIGTERM', shutdown);
```

### Python (psycopg2)

```python
import psycopg2
from psycopg2 import pool

# Create connection pool
connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=5,              # Minimum connections
    maxconn=20,             # Maximum connections
    host='localhost',
    port=5432,
    database='mydb',
    user='postgres',
    password='password'
)

# Get connection from pool
def query_example():
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (1,))
        result = cursor.fetchone()
        print(result)
        cursor.close()
    finally:
        connection_pool.putconn(conn)  # Return to pool

# Transaction example
def transaction_example():
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN")
        cursor.execute("INSERT INTO users (username) VALUES (%s)", ('alice',))
        cursor.execute("COMMIT")
        cursor.close()
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e
    finally:
        connection_pool.putconn(conn)

# Close pool
def shutdown():
    connection_pool.closeall()
    print("Pool closed")
```

### Java (HikariCP)

```java
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class DatabasePool {
    private static HikariDataSource dataSource;
    
    static {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/mydb");
        config.setUsername("postgres");
        config.setPassword("password");
        config.setMaximumPoolSize(20);
        config.setMinimumIdle(5);
        config.setIdleTimeout(30000);
        config.setConnectionTimeout(2000);
        config.setMaxLifetime(1800000); // 30 minutes
        config.setLeakDetectionThreshold(60000); // Detect leaks after 60 seconds
        
        dataSource = new HikariDataSource(config);
    }
    
    public static Connection getConnection() throws Exception {
        return dataSource.getConnection();
    }
    
    public static void queryExample() throws Exception {
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?")) {
            stmt.setInt(1, 1);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                System.out.println(rs.getString("username"));
            }
        }
    }
    
    public static void shutdown() {
        if (dataSource != null) {
            dataSource.close();
        }
    }
}
```

## Pool Sizing

### Calculating Pool Size

```sql
-- Formula for pool size:
-- pool_size = connections_needed_per_transaction * average_transactions_per_second * average_transaction_duration

-- Example:
-- - 100 transactions per second
-- - Average transaction duration: 50ms (0.05 seconds)
-- - Connections needed per transaction: 1
-- pool_size = 1 * 100 * 0.05 = 5 connections

-- However, add buffer for spikes:
-- pool_size = 5 * 2 = 10 connections

-- Rule of thumb:
-- pool_size = ((core_count * 2) + effective_spindle_count)
-- For SSD: effective_spindle_count = 1-2
-- For HDD: effective_spindle_count = number of disks

-- Example with 4 cores and SSD:
-- pool_size = (4 * 2) + 1 = 9 connections

-- Check current connection usage
SELECT
    COUNT(*) AS total_connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle
FROM pg_stat_activity
WHERE backend_type = 'client backend';

-- Monitor connection usage over time
CREATE TABLE connection_stats (
    recorded_at TIMESTAMP DEFAULT NOW(),
    total_connections INT,
    active_connections INT,
    idle_connections INT
);

-- Record stats every minute
INSERT INTO connection_stats (total_connections, active_connections, idle_connections)
SELECT
    COUNT(*),
    COUNT(*) FILTER (WHERE state = 'active'),
    COUNT(*) FILTER (WHERE state = 'idle')
FROM pg_stat_activity
WHERE backend_type = 'client backend';

-- Analyze peak usage
SELECT
    DATE_TRUNC('hour', recorded_at) AS hour,
    MAX(total_connections) AS peak_connections,
    AVG(active_connections) AS avg_active
FROM connection_stats
GROUP BY hour
ORDER BY hour DESC;
```

### Pool Configuration Guidelines

```text
Pool Configuration Guidelines:

1. Application-Level Pool Size (per application instance):
   - Small applications: 5-10 connections
   - Medium applications: 10-20 connections
   - Large applications: 20-50 connections
   
   Multiple app instances: pool_size_per_instance * num_instances

2. PgBouncer/Pgpool Pool Size (server-side):
   - default_pool_size: 15-30 connections per database
   - max_client_conn: 1000-5000 (based on expected client connections)
   
   Example:
   - 10 app servers, 20 connections each = 200 total client connections
   - PgBouncer pool size: 20-30 actual PostgreSQL connections
   - Reduction ratio: 200/25 = 8:1

3. PostgreSQL max_connections:
   - Calculate: sum of all pools + admin connections + replication slots
   - Example:
     - PgBouncer pool: 25 connections
     - Admin connections: 5
     - Replication: 2
     - Buffer: 10
     - Total: 42 connections
   
   - Set max_connections = 50 (with buffer)

4. Memory Considerations:
   - Each connection: ~2-10 MB
   - 100 connections = 200-1000 MB just for connections
   - With pooling: 25 connections = 50-250 MB

5. Idle Connection Management:
   - idleTimeoutMillis: 30000 (30 seconds) for application pools
   - server_idle_timeout: 600 (10 minutes) for PgBouncer
   - Prevents stale connections and reduces memory usage

6. Connection Lifetime:
   - maxLifetime: 1800000 (30 minutes) for application pools
   - server_lifetime: 3600 (1 hour) for PgBouncer
   - Prevents connection leaks and forces reconnection

Tuning Process:
1. Start with small pool (5-10 connections)
2. Monitor connection usage and wait times
3. Increase pool size if clients are waiting
4. Decrease if connections are mostly idle
5. Monitor PostgreSQL performance (CPU, memory, disk I/O)
```

## Monitoring Pooling

### PgBouncer Metrics

```sql
-- Connect to PgBouncer admin
psql -h localhost -p 6432 -U admin_user pgbouncer

-- Show pool status
SHOW POOLS;
-- Key metrics:
-- cl_active: Active client connections
-- cl_waiting: Clients waiting for connection
-- sv_active: Active server connections
-- sv_idle: Idle server connections
-- maxwait: Max wait time in seconds

-- Check for bottlenecks
SELECT database, cl_waiting, maxwait
FROM SHOW POOLS
WHERE cl_waiting > 0 OR maxwait > 0;

-- Show statistics
SHOW STATS;
-- Key metrics:
-- total_xact_count: Total transactions
-- total_query_count: Total queries
-- total_wait_time: Total wait time (microseconds)
-- avg_xact_time: Average transaction time
-- avg_query_time: Average query time
-- avg_wait_time: Average wait time

-- Calculate wait time percentage
SELECT
    database,
    avg_query_time,
    avg_wait_time,
    ROUND(100.0 * avg_wait_time / NULLIF(avg_query_time + avg_wait_time, 0), 2) AS pct_wait_time
FROM SHOW STATS
ORDER BY pct_wait_time DESC;

-- Show server connections
SHOW SERVERS;
-- Shows all connections to PostgreSQL

-- Show clients
SHOW CLIENTS;
-- Shows all client connections
```

### Application Pool Monitoring

```javascript
// Node.js (pg) pool monitoring
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  database: 'mydb',
  max: 20,
});

// Log pool metrics
function logPoolMetrics() {
  console.log('Pool Metrics:', {
    totalCount: pool.totalCount,    // Total connections (active + idle)
    idleCount: pool.idleCount,      // Idle connections
    waitingCount: pool.waitingCount // Clients waiting for connection
  });
}

setInterval(logPoolMetrics, 60000); // Log every minute

// Monitor pool events
pool.on('connect', (client) => {
  console.log('New connection established');
});

pool.on('acquire', (client) => {
  console.log('Connection acquired from pool');
});

pool.on('remove', (client) => {
  console.log('Connection removed from pool');
});

pool.on('error', (err, client) => {
  console.error('Pool error:', err);
});
```

## Best Practices

### Best Practices Checklist

```text
Connection Pooling Best Practices:

1. Always Use Connection Pooling
   ✓ Use PgBouncer/Pgpool for server-side pooling
   ✓ Use application-level pools (pg, psycopg2, HikariCP)
   ✓ Never create new connection for each request

2. Choose Correct Pool Mode
   ✓ Session mode: Complex applications with prepared statements
   ✓ Transaction mode: Web applications (most common)
   ✓ Statement mode: Read-only, stateless queries

3. Size Pools Correctly
   ✓ Start small (5-10 connections), increase if needed
   ✓ Monitor wait times and connection usage
   ✓ Application pool: 10-20 connections per instance
   ✓ Server-side pool: 15-30 connections per database

4. Configure Timeouts
   ✓ Connection timeout: 2-5 seconds
   ✓ Idle timeout: 30-300 seconds
   ✓ Connection lifetime: 30-60 minutes
   ✓ Statement timeout: 30-60 seconds

5. Monitor Pool Health
   ✓ Track active vs idle connections
   ✓ Monitor wait times
   ✓ Alert on connection exhaustion
   ✓ Log pool errors

6. Handle Connection Errors
   ✓ Implement retry logic with exponential backoff
   ✓ Health check connections before use
   ✓ Handle "pool exhausted" gracefully
   ✓ Log connection errors for debugging

7. Graceful Shutdown
   ✓ Close pool on application shutdown
   ✓ Wait for active connections to finish
   ✓ Use process signals (SIGTERM, SIGINT)

8. Security
   ✓ Use SSL for connections
   ✓ Store credentials securely (environment variables)
   ✓ Use separate pools for different users/roles
   ✓ Limit max_client_conn to prevent DoS

9. Testing
   ✓ Test pool under load
   ✓ Verify connection reuse
   ✓ Test connection timeout behavior
   ✓ Test graceful degradation when pool exhausted

10. Documentation
    ✓ Document pool configuration
    ✓ Explain pool mode choice
    ✓ Document expected connection usage
    ✓ Provide monitoring dashboards

Common Mistakes to Avoid:
✗ Not using connection pooling
✗ Creating too large pools (wastes memory)
✗ Not setting timeouts (connections leak)
✗ Not monitoring pool metrics
✗ Not handling connection errors
✗ Not closing pools on shutdown
✗ Using session pooling with PgBouncer (use transaction mode)
✗ Not configuring SSL for production
```

## Summary

Connection pooling is essential for PostgreSQL performance and scalability:

- **Why Pooling**: Eliminates connection overhead (8-35ms per connection), reduces memory usage, prevents "too many connections" errors
- **Pooling Modes**: Session (full support), Transaction (web apps), Statement (read-only)
- **PgBouncer**: Lightweight, efficient, transaction-level pooling (most popular)
- **Pgpool-II**: Advanced features (load balancing, replication, failover)
- **Application Pooling**: Language-specific (pg, psycopg2, HikariCP)
- **Pool Sizing**: Formula: (core_count * 2) + effective_spindle_count, start small (5-10), monitor and adjust
- **Monitoring**: Track active/idle connections, wait times, pool exhaustion
- **Best Practices**: Always use pooling, choose correct mode, size appropriately, monitor health, handle errors gracefully

Connection pooling is a critical optimization that should be implemented in every PostgreSQL application.

## Next Steps

- Study [PostgreSQL and Node.js](./40-postgresql-and-nodejs.md)
- Learn [Performance Troubleshooting](./42-performance-troubleshooting.md)
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Practice [High Availability](./37-high-availability.md)
