# Chapter 23: Security

## Learning Objectives
By the end of this chapter, you will:
- Configure authentication and authorization
- Manage users and roles
- Implement fine-grained access control
- Secure data with encryption
- Follow security best practices

---

## 23.1 Authentication

### Built-in Authentication

```properties
# neo4j.conf
# Enable authentication (default: true)
dbms.security.auth_enabled=true

# Minimum password length
dbms.security.auth_minimum_password_length=8
```

### Default User

```cypher
// Initial login with default credentials
// Username: neo4j
// Password: neo4j (must change on first login)

// Change password
ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'newSecurePassword123!'
```

### Native Authentication Provider

```properties
# Use native Neo4j authentication
dbms.security.authentication_providers=native
dbms.security.authorization_providers=native
```

### LDAP Authentication (Enterprise)

```properties
# Enable LDAP
dbms.security.authentication_providers=ldap
dbms.security.authorization_providers=ldap

# LDAP server configuration
dbms.security.ldap.host=ldap://ldap.example.com:389
dbms.security.ldap.authentication.user_dn_template=cn={0},ou=users,dc=example,dc=com
dbms.security.ldap.authentication.cache_enabled=true

# Group to role mapping
dbms.security.ldap.authorization.group_to_role_mapping=\
    cn=admins,ou=groups,dc=example,dc=com=admin;\
    cn=readers,ou=groups,dc=example,dc=com=reader
```

---

## 23.2 User Management

### Creating Users

```cypher
// Create user
CREATE USER alice SET PASSWORD 'SecurePass123!' CHANGE REQUIRED

// Create user without password change requirement
CREATE USER bob SET PASSWORD 'SecurePass456!' CHANGE NOT REQUIRED

// Create user with home database
CREATE USER carol SET PASSWORD 'SecurePass789!' SET HOME DATABASE customers

// Create user if not exists
CREATE USER david IF NOT EXISTS SET PASSWORD 'SecurePass000!'
```

### Managing Users

```cypher
// List all users
SHOW USERS

// Show current user
SHOW CURRENT USER

// Alter user password
ALTER USER alice SET PASSWORD 'NewSecurePass123!'

// Suspend user
ALTER USER alice SET STATUS SUSPENDED

// Activate user
ALTER USER alice SET STATUS ACTIVE

// Set home database
ALTER USER alice SET HOME DATABASE neo4j

// Drop user
DROP USER alice

// Drop if exists
DROP USER alice IF EXISTS
```

### Password Policies

```properties
# neo4j.conf
# Require password change on first login
dbms.security.auth_lock_time=5s

# Account lockout
dbms.security.auth_max_failed_attempts=3
```

---

## 23.3 Role-Based Access Control (RBAC)

### Built-in Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full database and system access |
| `architect` | Full database access, no system admin |
| `publisher` | Read/write on all databases |
| `editor` | Read/write except schema changes |
| `reader` | Read-only access |
| `PUBLIC` | Default role for all users |

### Creating Custom Roles

```cypher
// Create role
CREATE ROLE data_analyst

// Create if not exists
CREATE ROLE data_scientist IF NOT EXISTS

// Show roles
SHOW ROLES

// Show role privileges
SHOW ROLE data_analyst PRIVILEGES

// Drop role
DROP ROLE data_analyst

// Drop if exists
DROP ROLE data_analyst IF EXISTS
```

### Assigning Roles

```cypher
// Grant role to user
GRANT ROLE reader TO alice

// Grant multiple roles
GRANT ROLE reader, editor TO bob

// Revoke role
REVOKE ROLE editor FROM bob

// Show user roles
SHOW USER alice PRIVILEGES
```

---

## 23.4 Privileges

### Database Privileges

```cypher
// Grant access to database
GRANT ACCESS ON DATABASE customers TO data_analyst

// Grant read privilege
GRANT MATCH {*} ON GRAPH customers TO data_analyst

// Grant write privileges
GRANT CREATE ON GRAPH customers TO data_analyst
GRANT SET PROPERTY {*} ON GRAPH customers TO data_analyst
GRANT DELETE ON GRAPH customers TO data_analyst

// Grant all privileges on database
GRANT ALL ON DATABASE customers TO data_analyst

// Deny access
DENY ACCESS ON DATABASE production TO data_analyst
```

### Graph Element Privileges

```cypher
// Grant read on specific labels
GRANT MATCH {*} ON GRAPH customers NODES Customer TO data_analyst
GRANT MATCH {*} ON GRAPH customers RELATIONSHIPS PURCHASED TO data_analyst

// Grant read on specific properties
GRANT MATCH {name, email} ON GRAPH customers NODES Customer TO data_analyst

// Grant write on specific labels
GRANT CREATE ON GRAPH customers NODES Customer TO data_analyst
GRANT SET PROPERTY {status} ON GRAPH customers NODES Customer TO data_analyst
GRANT DELETE ON GRAPH customers NODES TempData TO data_analyst
```

### Property-Level Security

```cypher
// Hide sensitive properties
DENY READ {ssn, creditCard} ON GRAPH customers NODES Customer TO data_analyst

// Allow setting specific properties only
GRANT SET PROPERTY {name, email} ON GRAPH customers NODES Customer TO data_analyst
DENY SET PROPERTY {*} ON GRAPH customers NODES Customer TO data_analyst
```

### Procedure Privileges

```cypher
// Grant execute on procedures
GRANT EXECUTE PROCEDURE db.labels TO data_analyst
GRANT EXECUTE PROCEDURE apoc.* TO data_analyst

// Grant execute on functions
GRANT EXECUTE FUNCTION apoc.* TO data_analyst

// Deny admin procedures
DENY EXECUTE PROCEDURE dbms.* TO data_analyst
```

### Showing and Revoking Privileges

```cypher
// Show all privileges
SHOW PRIVILEGES

// Show privileges for role
SHOW ROLE data_analyst PRIVILEGES

// Show privileges for user
SHOW USER alice PRIVILEGES

// Revoke privilege
REVOKE MATCH {*} ON GRAPH customers FROM data_analyst

// Revoke all
REVOKE ALL ON DATABASE customers FROM data_analyst
```

---

## 23.5 Fine-Grained Access Control (Enterprise)

### Row-Level Security

```cypher
// Create role for regional access
CREATE ROLE us_sales_team

// Grant access only to US data
GRANT MATCH {*} ON GRAPH sales 
    NODES Customer 
    WHERE Customer.region = 'US' 
    TO us_sales_team

// Grant access to relationships connected to accessible nodes
GRANT TRAVERSE ON GRAPH sales TO us_sales_team
```

### Subgraph Access

```cypher
// Create segmented access
CREATE ROLE marketing_team

// Access only marketing-related data
GRANT MATCH {*} ON GRAPH main NODES Campaign, Lead, MarketingContact TO marketing_team
GRANT MATCH {*} ON GRAPH main RELATIONSHIPS TARGETED, RESPONDED TO marketing_team
```

---

## 23.6 Encryption

### SSL/TLS Configuration

```properties
# neo4j.conf

# Enable TLS for Bolt
dbms.ssl.policy.bolt.enabled=true
dbms.ssl.policy.bolt.base_directory=certificates/bolt
dbms.ssl.policy.bolt.private_key=private.key
dbms.ssl.policy.bolt.public_certificate=public.crt
dbms.ssl.policy.bolt.client_auth=NONE  # or REQUIRE, OPTIONAL

# Enable TLS for HTTPS
dbms.ssl.policy.https.enabled=true
dbms.ssl.policy.https.base_directory=certificates/https
dbms.ssl.policy.https.private_key=private.key
dbms.ssl.policy.https.public_certificate=public.crt
```

### Generating Certificates

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 \
    -keyout private.key \
    -out public.crt \
    -days 365 \
    -nodes \
    -subj "/CN=neo4j.example.com"

# Place in Neo4j certificates directory
mkdir -p /var/lib/neo4j/certificates/bolt
cp private.key public.crt /var/lib/neo4j/certificates/bolt/
```

### Connecting with TLS (Python)

```python
from neo4j import GraphDatabase

# With self-signed certificate
driver = GraphDatabase.driver(
    "neo4j+s://localhost:7687",  # neo4j+s for encrypted
    auth=("neo4j", "password"),
    encrypted=True,
    trust=TRUST_CUSTOM_CA_SIGNED_CERTIFICATES,
    trusted_certificates=TrustCustomCAs("/path/to/ca.crt")
)

# With system CA
driver = GraphDatabase.driver(
    "neo4j+s://localhost:7687",
    auth=("neo4j", "password")
)

# Ignore certificate (development only!)
driver = GraphDatabase.driver(
    "neo4j+ssc://localhost:7687",  # ssc = self-signed certificate
    auth=("neo4j", "password")
)
```

---

## 23.7 Audit Logging

### Enable Security Logging

```properties
# neo4j.conf
# Enable security log
dbms.security.log_successful_authentication=true
dbms.logs.security.level=INFO
dbms.logs.security.rotation.size=10M
dbms.logs.security.rotation.keep_number=7
```

### Security Log Format

```
2026-01-25 10:30:15.123+0000 INFO  [johnsmith]: logged in
2026-01-25 10:30:20.456+0000 INFO  [johnsmith]: CREATE USER alice ...
2026-01-25 10:30:25.789+0000 WARN  [unknown]: failed to log in: invalid principal or credentials
2026-01-25 10:30:30.012+0000 INFO  [johnsmith]: GRANT ROLE reader TO alice
```

### Query Audit Logging

```properties
# Log all queries
db.logs.query.enabled=true
db.logs.query.threshold=0  # Log all queries
db.logs.query.parameter_logging_enabled=true  # Include parameters

# Rotation
db.logs.query.rotation.size=50M
db.logs.query.rotation.keep_number=10
```

---

## 23.8 Security Best Practices

### Authentication Best Practices

```cypher
// 1. Change default password immediately
ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'ComplexP@ssw0rd!'

// 2. Create named admin user
CREATE USER admin SET PASSWORD 'SecureAdminPass!' CHANGE NOT REQUIRED
GRANT ROLE admin TO admin

// 3. Disable or rename neo4j user
DROP USER neo4j
// Or rename by creating new and migrating

// 4. Set appropriate password policy
// In neo4j.conf: dbms.security.auth_minimum_password_length=12
```

### Authorization Best Practices

```cypher
// 1. Follow least privilege principle
// Create specific roles instead of using admin
CREATE ROLE app_backend
GRANT ACCESS ON DATABASE neo4j TO app_backend
GRANT MATCH {*} ON GRAPH neo4j TO app_backend
GRANT CREATE ON GRAPH neo4j NODES Customer, Order TO app_backend
// Don't grant DELETE unless necessary

// 2. Separate read and write roles
CREATE ROLE app_reader
GRANT ACCESS ON DATABASE neo4j TO app_reader
GRANT MATCH {*} ON GRAPH neo4j TO app_reader

CREATE ROLE app_writer
GRANT ROLE app_reader TO app_writer
GRANT CREATE, SET PROPERTY, DELETE ON GRAPH neo4j TO app_writer

// 3. Use deny to restrict sensitive data
CREATE ROLE analyst
GRANT MATCH {*} ON GRAPH neo4j TO analyst
DENY READ {ssn, password, creditCard} ON GRAPH neo4j NODES * TO analyst
```

### Network Security

```properties
# neo4j.conf

# Bind to specific interfaces
server.default_listen_address=10.0.0.5  # Internal IP only

# Or localhost only
server.default_listen_address=127.0.0.1

# Disable HTTP (use HTTPS only)
server.http.enabled=false
server.https.enabled=true
```

### Connection Security

```python
# Always use encrypted connections in production
from neo4j import GraphDatabase

# Production connection
driver = GraphDatabase.driver(
    "neo4j+s://neo4j.production.example.com:7687",
    auth=("app_user", "secure_password"),
    max_connection_lifetime=3600,
    max_connection_pool_size=50,
    connection_acquisition_timeout=60
)
```

---

## 23.9 Python Security Examples

```python
from neo4j import GraphDatabase
from typing import List, Dict
import hashlib
import secrets

URI = "neo4j+s://localhost:7687"
AUTH = ("admin", "admin_password")

class SecurityManager:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)
    
    def close(self):
        self.driver.close()
    
    def create_user(self, username: str, password: str, roles: List[str] = None):
        """Create a new user with specified roles."""
        with self.driver.session(database="system") as session:
            # Create user
            session.run("""
                CREATE USER $username 
                SET PASSWORD $password 
                CHANGE NOT REQUIRED
            """, username=username, password=password)
            
            # Assign roles
            if roles:
                for role in roles:
                    session.run(
                        "GRANT ROLE $role TO $username",
                        role=role, username=username
                    )
            
            return True
    
    def create_custom_role(self, role_name: str, privileges: Dict):
        """Create a custom role with specified privileges."""
        with self.driver.session(database="system") as session:
            # Create role
            session.run("CREATE ROLE $role IF NOT EXISTS", role=role_name)
            
            # Grant database access
            if 'databases' in privileges:
                for db in privileges['databases']:
                    session.run(f"""
                        GRANT ACCESS ON DATABASE {db} TO $role
                    """, role=role_name)
            
            # Grant read privileges
            if 'read_labels' in privileges:
                for label in privileges['read_labels']:
                    session.run(f"""
                        GRANT MATCH {{*}} ON GRAPH neo4j NODES {label} TO $role
                    """, role=role_name)
            
            # Grant write privileges
            if 'write_labels' in privileges:
                for label in privileges['write_labels']:
                    session.run(f"""
                        GRANT CREATE ON GRAPH neo4j NODES {label} TO $role
                    """, role=role_name)
                    session.run(f"""
                        GRANT SET PROPERTY {{*}} ON GRAPH neo4j NODES {label} TO $role
                    """, role=role_name)
    
    def list_users(self) -> List[Dict]:
        """List all users with their roles."""
        with self.driver.session(database="system") as session:
            result = session.run("""
                SHOW USERS
                YIELD user, roles, suspended
                RETURN user, roles, suspended
            """)
            return [dict(r) for r in result]
    
    def audit_privileges(self, role: str) -> List[Dict]:
        """Get all privileges for a role."""
        with self.driver.session(database="system") as session:
            result = session.run("""
                SHOW ROLE $role PRIVILEGES
                YIELD access, action, resource, graph, segment
                RETURN access, action, resource, graph, segment
            """, role=role)
            return [dict(r) for r in result]
    
    def check_access(self, username: str, database: str, operation: str) -> bool:
        """Check if user has specific access (simplified check)."""
        with self.driver.session(database="system") as session:
            result = session.run("""
                SHOW USER $username PRIVILEGES
                YIELD access, action, graph
                WHERE graph = $database OR graph = '*'
                RETURN access, action
            """, username=username, database=database)
            
            privileges = [dict(r) for r in result]
            
            for priv in privileges:
                if priv['access'] == 'GRANTED' and priv['action'] == operation:
                    return True
                if priv['access'] == 'DENIED' and priv['action'] == operation:
                    return False
            
            return False
    
    def suspend_user(self, username: str):
        """Suspend a user account."""
        with self.driver.session(database="system") as session:
            session.run("ALTER USER $username SET STATUS SUSPENDED", username=username)
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password."""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def rotate_password(self, username: str) -> str:
        """Rotate user password and return new password."""
        new_password = self.generate_secure_password()
        
        with self.driver.session(database="system") as session:
            session.run(
                "ALTER USER $username SET PASSWORD $password",
                username=username, password=new_password
            )
        
        return new_password

# Usage
security = SecurityManager(URI, AUTH)
try:
    # Create custom role
    security.create_custom_role('app_backend', {
        'databases': ['neo4j'],
        'read_labels': ['Customer', 'Product', 'Order'],
        'write_labels': ['Customer', 'Order']
    })
    
    # Create user with role
    security.create_user('app_service', 'ServicePass123!', ['app_backend'])
    
    # List all users
    users = security.list_users()
    for user in users:
        print(f"{user['user']}: roles={user['roles']}, suspended={user['suspended']}")
    
    # Audit role privileges
    privileges = security.audit_privileges('app_backend')
    for priv in privileges:
        print(f"{priv['access']} {priv['action']} on {priv['graph']}")
        
finally:
    security.close()
```

---

## Summary

### Security Layers

| Layer | Implementation |
|-------|---------------|
| **Authentication** | Native, LDAP, OIDC |
| **Authorization** | RBAC with fine-grained privileges |
| **Encryption** | TLS for connections |
| **Auditing** | Security and query logs |

### Key Commands

```cypher
-- User Management
CREATE USER username SET PASSWORD 'pass' CHANGE REQUIRED
ALTER USER username SET STATUS SUSPENDED/ACTIVE
DROP USER username

-- Role Management  
CREATE ROLE rolename
GRANT ROLE rolename TO username
REVOKE ROLE rolename FROM username

-- Privileges
GRANT ACCESS ON DATABASE dbname TO role
GRANT MATCH {*} ON GRAPH dbname TO role
DENY READ {property} ON GRAPH dbname NODES Label TO role
```

---

## Exercises

### Exercise 23.1: User Setup
1. Create admin, developer, and analyst users
2. Create appropriate roles
3. Assign roles based on least privilege

### Exercise 23.2: Fine-Grained Access
1. Create role that can only read specific labels
2. Create role that can write but not delete
3. Test access with different users

### Exercise 23.3: Audit Setup
1. Enable security and query logging
2. Monitor login attempts
3. Track privilege changes

---

**Next Chapter: [Chapter 24: Multi-Database and Fabric](24-multi-database-fabric.md)**
