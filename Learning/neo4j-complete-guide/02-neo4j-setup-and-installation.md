# Chapter 2: Neo4j Setup and Installation

## Learning Objectives
By the end of this chapter, you will:
- Install Neo4j using your preferred method
- Understand Neo4j's architecture and components
- Navigate Neo4j Browser confidently
- Run your first Cypher queries
- Set up a development environment

---

## 2.1 Neo4j Deployment Options

### Overview of Options

| Option | Best For | Pros | Cons |
|--------|----------|------|------|
| **AuraDB Free** | Beginners, learning | No setup, free tier | Limited size, cloud only |
| **AuraDB Pro** | Production cloud | Managed, scalable | Cost |
| **Neo4j Desktop** | Development | Full control, multiple DBs | Local resources |
| **Docker** | DevOps, CI/CD | Reproducible, scriptable | Requires Docker |
| **Server Installation** | Production on-prem | Full control | Manual management |

---

## 2.2 Option 1: Neo4j AuraDB (Recommended for Beginners)

### Step 1: Create an Account

1. Go to [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/)
2. Click "Start Free"
3. Sign up with email or Google/GitHub account
4. Verify your email

### Step 2: Create a Free Instance

1. Click "New Instance"
2. Select "AuraDB Free"
3. Choose a region closest to you
4. Name your instance (e.g., "learning-neo4j")
5. Click "Create"

### Step 3: Save Your Credentials

**⚠️ IMPORTANT: Save these immediately!**

```
┌─────────────────────────────────────────────────────────┐
│  Connection URI: neo4j+s://xxxxxxxx.databases.neo4j.io │
│  Username: neo4j                                       │
│  Password: xxxxxxxxxxxxxxxx                            │
│                                                        │
│  SAVE THESE! Password is shown only once.              │
└─────────────────────────────────────────────────────────┘
```

### Step 4: Connect

1. Wait for instance to be "Running" (takes 1-2 minutes)
2. Click "Open" to launch Neo4j Browser
3. Or click "Connect" to get connection details

### AuraDB Free Tier Limits

| Resource | Limit |
|----------|-------|
| Nodes | 200,000 |
| Relationships | 400,000 |
| Storage | 1 GB |
| Databases | 1 |
| Idle timeout | 3 days (auto-pause) |

---

## 2.3 Option 2: Neo4j Desktop (Recommended for Development)

### Step 1: Download

1. Go to [https://neo4j.com/download/](https://neo4j.com/download/)
2. Fill in the form (or skip with guest download)
3. Download for your OS (Windows, macOS, Linux)
4. Copy the activation key shown

### Step 2: Install

**macOS:**
```bash
# Open the downloaded .dmg file
# Drag Neo4j Desktop to Applications
# Open from Applications folder
```

**Windows:**
```bash
# Run the downloaded .exe installer
# Follow the installation wizard
# Launch from Start Menu
```

**Linux:**
```bash
# Extract the downloaded AppImage
chmod +x neo4j-desktop-*.AppImage
./neo4j-desktop-*.AppImage
```

### Step 3: Activate

1. Launch Neo4j Desktop
2. Enter the activation key from the download page
3. Or select "Use Free" for limited features

### Step 4: Create Your First Database

1. Click "New" → "Create project"
2. Name it "Learning Neo4j"
3. Click "Add" → "Local DBMS"
4. Set a password (remember it!)
5. Choose Neo4j version (latest is fine)
6. Click "Create"

### Step 5: Start the Database

1. Click "Start" on your database
2. Wait for status to show "Running"
3. Click "Open" to launch Neo4j Browser

### Neo4j Desktop File Locations

```
macOS:
~/Library/Application Support/Neo4j Desktop/

Windows:
%APPDATA%\Neo4j Desktop\

Linux:
~/.config/Neo4j Desktop/
```

---

## 2.4 Option 3: Docker Installation

### Prerequisites
- Docker installed ([https://docker.com](https://docker.com))
- Basic command line knowledge

### Basic Docker Setup

```bash
# Pull the latest Neo4j image
docker pull neo4j:latest

# Run Neo4j container
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mypassword123 \
  neo4j:latest
```

### Docker with Data Persistence

```bash
# Create directories for data persistence
mkdir -p ~/neo4j/data ~/neo4j/logs ~/neo4j/import ~/neo4j/plugins

# Run with volume mounts
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -v ~/neo4j/data:/data \
  -v ~/neo4j/logs:/logs \
  -v ~/neo4j/import:/var/lib/neo4j/import \
  -v ~/neo4j/plugins:/plugins \
  -e NEO4J_AUTH=neo4j/mypassword123 \
  neo4j:latest
```

### Docker with Graph Data Science Library

```bash
docker run -d \
  --name neo4j-gds \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mypassword123 \
  -e NEO4J_PLUGINS='["graph-data-science"]' \
  -e NEO4J_dbms_security_procedures_unrestricted=gds.* \
  neo4j:latest
```

### Docker Compose Setup

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:latest
    container_name: neo4j
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/mypassword123
      - NEO4J_PLUGINS=["graph-data-science", "apoc"]
      - NEO4J_dbms_security_procedures_unrestricted=gds.*,apoc.*
      - NEO4J_dbms_memory_heap_initial__size=512m
      - NEO4J_dbms_memory_heap_max__size=1G
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_import:/var/lib/neo4j/import
      - neo4j_plugins:/plugins
    restart: unless-stopped

volumes:
  neo4j_data:
  neo4j_logs:
  neo4j_import:
  neo4j_plugins:
```

Run with:
```bash
docker-compose up -d
```

### Docker Commands Reference

```bash
# View logs
docker logs neo4j

# Stop container
docker stop neo4j

# Start container
docker start neo4j

# Remove container
docker rm -f neo4j

# Enter container shell
docker exec -it neo4j bash

# Run cypher-shell inside container
docker exec -it neo4j cypher-shell -u neo4j -p mypassword123
```

---

## 2.5 Neo4j Architecture Overview

### Core Components

```
┌──────────────────────────────────────────────────────────────┐
│                    NEO4J ARCHITECTURE                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐      ┌─────────────────┐               │
│  │   Neo4j Browser │      │  cypher-shell   │               │
│  │   (Port 7474)   │      │                 │               │
│  └────────┬────────┘      └────────┬────────┘               │
│           │                        │                         │
│           │         HTTP           │         Bolt            │
│           └──────────┬─────────────┘                         │
│                      │                                       │
│           ┌──────────▼──────────┐                            │
│           │    Bolt Protocol    │◄────── Port 7687           │
│           │   (Binary, Fast)    │                            │
│           └──────────┬──────────┘                            │
│                      │                                       │
│           ┌──────────▼──────────┐                            │
│           │    Cypher Engine    │                            │
│           │ (Query Processing)  │                            │
│           └──────────┬──────────┘                            │
│                      │                                       │
│           ┌──────────▼──────────┐                            │
│           │   Graph Storage     │                            │
│           │  (Native Format)    │                            │
│           └─────────────────────┘                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Key Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 7474 | HTTP | Neo4j Browser, REST API |
| 7473 | HTTPS | Secure Browser, REST API |
| 7687 | Bolt | Binary protocol for drivers |

### Database Files

```
data/
├── databases/
│   └── neo4j/              # Default database
│       ├── neostore.*      # Node and relationship stores
│       └── schema/         # Index files
├── transactions/
│   └── neo4j/              # Transaction logs
└── dbms/
    └── auth               # Authentication data
```

---

## 2.6 Neo4j Browser Interface

### Accessing Neo4j Browser

- **AuraDB**: Click "Open" in console
- **Desktop**: Click "Open" on running database
- **Docker**: Navigate to http://localhost:7474

### Browser Interface Tour

```
┌──────────────────────────────────────────────────────────────┐
│  Neo4j Browser                                    [≡] [?] [x]│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ neo4j$ MATCH (n) RETURN n LIMIT 25                     │  │
│  └────────────────────────────────────────────────────────┘  │
│  [▶ Run]                                                     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                                                        │  │
│  │              ○ ─────── ○                               │  │
│  │             /│\       /│\                              │  │
│  │            ○ ○ ○     ○ ○ ○                             │  │
│  │                                                        │  │
│  │  [Graph] [Table] [Text] [Code]                         │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  SAVED SCRIPTS    HISTORY    FAVORITES                      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Browser Features

| Feature | Description | Shortcut |
|---------|-------------|----------|
| **Editor** | Write and run Cypher queries | - |
| **Results** | View as graph, table, or text | - |
| **Favorites** | Save frequently used queries | - |
| **History** | Access previous queries | - |
| **Guides** | Interactive tutorials | `:play` |
| **Help** | Command reference | `:help` |

### Essential Browser Commands

```
:help                    # Show help
:clear                   # Clear results
:history                 # Show query history
:queries                 # Show running queries

:play start              # Getting started guide
:play cypher             # Cypher tutorial
:play movies             # Movies dataset tutorial

:dbs                     # List databases
:use <database>          # Switch database

:param name => 'Alice'   # Set parameter
:params                  # Show parameters
:params {}               # Clear parameters

:config                  # Show configuration
:style                   # Graph visualization style
```

---

## 2.7 Your First Cypher Queries

### Verify Connection

```cypher
// Simple test query
RETURN "Hello, Neo4j!" AS greeting
```

Expected output:
```
╒═══════════════╕
│greeting       │
╞═══════════════╡
│"Hello, Neo4j!"│
└───────────────┘
```

### Check Database Status

```cypher
// Show database information
CALL dbms.components() YIELD name, versions, edition
RETURN name, versions, edition
```

### Create Your First Nodes

```cypher
// Create a person node
CREATE (p:Person {name: 'Alice', age: 30})
RETURN p
```

```cypher
// Create multiple nodes
CREATE (bob:Person {name: 'Bob', age: 28})
CREATE (charlie:Person {name: 'Charlie', age: 35})
RETURN bob, charlie
```

### Create Relationships

```cypher
// Create a relationship between existing nodes
MATCH (alice:Person {name: 'Alice'})
MATCH (bob:Person {name: 'Bob'})
CREATE (alice)-[:KNOWS {since: 2020}]->(bob)
RETURN alice, bob
```

### Query Your Graph

```cypher
// Find all Person nodes
MATCH (p:Person)
RETURN p

// Find all nodes and relationships
MATCH (n)-[r]->(m)
RETURN n, r, m

// Find who Alice knows
MATCH (alice:Person {name: 'Alice'})-[:KNOWS]->(friend)
RETURN alice, friend
```

### Update Data

```cypher
// Update a property
MATCH (p:Person {name: 'Alice'})
SET p.city = 'New York'
RETURN p
```

### Delete Data

```cypher
// Delete a relationship
MATCH (alice:Person {name: 'Alice'})-[r:KNOWS]->(bob:Person {name: 'Bob'})
DELETE r

// Delete a node (must have no relationships)
MATCH (p:Person {name: 'Charlie'})
DELETE p

// Delete node and all its relationships
MATCH (p:Person {name: 'Charlie'})
DETACH DELETE p
```

### Clean Up (Delete Everything)

```cypher
// ⚠️ WARNING: Deletes all data!
MATCH (n)
DETACH DELETE n
```

---

## 2.8 Loading Sample Data

### The Movies Dataset

Neo4j comes with a built-in movies dataset. Load it using:

```cypher
// In Neo4j Browser, run:
:play movies

// Then follow the guide, or run directly:
```

Or create it manually:

```cypher
// Create Movie nodes
CREATE (TheMatrix:Movie {title:'The Matrix', released:1999, tagline:'Welcome to the Real World'})
CREATE (TheMatrixReloaded:Movie {title:'The Matrix Reloaded', released:2003, tagline:'Free your mind'})
CREATE (TheMatrixRevolutions:Movie {title:'The Matrix Revolutions', released:2003, tagline:'Everything that has a beginning has an end'})

// Create Person nodes
CREATE (Keanu:Person {name:'Keanu Reeves', born:1964})
CREATE (Carrie:Person {name:'Carrie-Anne Moss', born:1967})
CREATE (Laurence:Person {name:'Laurence Fishburne', born:1961})
CREATE (Hugo:Person {name:'Hugo Weaving', born:1960})
CREATE (LillyW:Person {name:'Lilly Wachowski', born:1967})
CREATE (LanaW:Person {name:'Lana Wachowski', born:1965})
CREATE (JoelS:Person {name:'Joel Silver', born:1952})

// Create ACTED_IN relationships
CREATE (Keanu)-[:ACTED_IN {roles:['Neo']}]->(TheMatrix)
CREATE (Keanu)-[:ACTED_IN {roles:['Neo']}]->(TheMatrixReloaded)
CREATE (Keanu)-[:ACTED_IN {roles:['Neo']}]->(TheMatrixRevolutions)
CREATE (Carrie)-[:ACTED_IN {roles:['Trinity']}]->(TheMatrix)
CREATE (Carrie)-[:ACTED_IN {roles:['Trinity']}]->(TheMatrixReloaded)
CREATE (Carrie)-[:ACTED_IN {roles:['Trinity']}]->(TheMatrixRevolutions)
CREATE (Laurence)-[:ACTED_IN {roles:['Morpheus']}]->(TheMatrix)
CREATE (Laurence)-[:ACTED_IN {roles:['Morpheus']}]->(TheMatrixReloaded)
CREATE (Laurence)-[:ACTED_IN {roles:['Morpheus']}]->(TheMatrixRevolutions)
CREATE (Hugo)-[:ACTED_IN {roles:['Agent Smith']}]->(TheMatrix)
CREATE (Hugo)-[:ACTED_IN {roles:['Agent Smith']}]->(TheMatrixReloaded)
CREATE (Hugo)-[:ACTED_IN {roles:['Agent Smith']}]->(TheMatrixRevolutions)

// Create DIRECTED relationships
CREATE (LillyW)-[:DIRECTED]->(TheMatrix)
CREATE (LanaW)-[:DIRECTED]->(TheMatrix)
CREATE (LillyW)-[:DIRECTED]->(TheMatrixReloaded)
CREATE (LanaW)-[:DIRECTED]->(TheMatrixReloaded)
CREATE (LillyW)-[:DIRECTED]->(TheMatrixRevolutions)
CREATE (LanaW)-[:DIRECTED]->(TheMatrixRevolutions)

// Create PRODUCED relationships
CREATE (JoelS)-[:PRODUCED]->(TheMatrix)
CREATE (JoelS)-[:PRODUCED]->(TheMatrixReloaded)
CREATE (JoelS)-[:PRODUCED]->(TheMatrixRevolutions)
```

### Query the Movies Data

```cypher
// Find all movies
MATCH (m:Movie)
RETURN m.title, m.released

// Find actors in The Matrix
MATCH (p:Person)-[:ACTED_IN]->(m:Movie {title: 'The Matrix'})
RETURN p.name, m.title

// Find all of Keanu's movies
MATCH (keanu:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(movie)
RETURN movie.title

// Find co-actors
MATCH (keanu:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(movie)<-[:ACTED_IN]-(coactor)
RETURN DISTINCT coactor.name
```

---

## 2.9 cypher-shell (Command Line Tool)

### Accessing cypher-shell

**Desktop:**
- Click "Open Terminal" in Neo4j Desktop
- Or find it in the installation directory

**Docker:**
```bash
docker exec -it neo4j cypher-shell -u neo4j -p mypassword123
```

**Direct Installation:**
```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p mypassword123
```

### cypher-shell Commands

```
:help           # Show help
:exit           # Exit shell
:quit           # Exit shell
:history        # Show history
:param          # Set parameter
:params         # Show parameters
:source file    # Execute file
:begin          # Begin transaction
:commit         # Commit transaction
:rollback       # Rollback transaction
```

### Running Scripts

```bash
# Execute a Cypher file
cypher-shell -u neo4j -p password -f queries.cypher

# Pipe commands
echo "MATCH (n) RETURN count(n)" | cypher-shell -u neo4j -p password

# Output to file
cypher-shell -u neo4j -p password -f query.cypher > results.txt
```

---

## 2.10 Setting Up Python Environment

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Neo4j Driver

```bash
# Create a virtual environment (recommended)
python -m venv neo4j-env
source neo4j-env/bin/activate  # On Windows: neo4j-env\Scripts\activate

# Install Neo4j driver
pip install neo4j
```

### Test Connection

Create a file `test_connection.py`:

```python
from neo4j import GraphDatabase

# Connection details
URI = "bolt://localhost:7687"  # For Docker/Desktop
# URI = "neo4j+s://xxxxxxxx.databases.neo4j.io"  # For AuraDB
USERNAME = "neo4j"
PASSWORD = "your_password"

def test_connection():
    driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
    
    try:
        driver.verify_connectivity()
        print("✅ Connection successful!")
        
        # Run a simple query
        with driver.session() as session:
            result = session.run("RETURN 'Hello from Python!' AS message")
            record = result.single()
            print(f"Message: {record['message']}")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    test_connection()
```

Run it:
```bash
python test_connection.py
```

### Environment Variables (Recommended)

Create a `.env` file:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

Use with python-dotenv:
```python
from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)
```

---

## 2.11 Troubleshooting Common Issues

### Connection Issues

| Problem | Solution |
|---------|----------|
| Connection refused | Check if Neo4j is running |
| Authentication failed | Verify username/password |
| Timeout | Check firewall, network settings |
| SSL errors | Use correct protocol (bolt:// vs neo4j+s://) |

### AuraDB Connection

```python
# AuraDB requires neo4j+s:// (SSL)
URI = "neo4j+s://xxxxxxxx.databases.neo4j.io"

# Not bolt:// or neo4j://
```

### Docker Issues

```bash
# Check if container is running
docker ps

# View logs
docker logs neo4j

# Restart container
docker restart neo4j
```

### Memory Issues

Add to docker-compose or command:
```yaml
environment:
  - NEO4J_dbms_memory_heap_initial__size=512m
  - NEO4J_dbms_memory_heap_max__size=1G
  - NEO4J_dbms_memory_pagecache_size=512m
```

---

## Summary

### Key Takeaways

1. **Multiple deployment options**: AuraDB (cloud), Desktop (local), Docker (containerized)
2. **Key ports**: 7474 (HTTP/Browser), 7687 (Bolt protocol)
3. **Neo4j Browser**: Primary interface for learning and development
4. **cypher-shell**: Command-line interface for scripting
5. **Python driver**: Official driver for application development

### Checklist

✅ Installed Neo4j (AuraDB, Desktop, or Docker)  
✅ Connected to Neo4j Browser  
✅ Ran first Cypher queries  
✅ Loaded sample data  
✅ Set up Python environment  

---

## Exercises

### Exercise 2.1: Multi-Method Installation
Try installing Neo4j using at least two different methods (e.g., AuraDB and Docker). Compare the experience.

### Exercise 2.2: Browser Exploration
Complete the `:play movies` tutorial in Neo4j Browser. Note down any queries you find particularly useful.

### Exercise 2.3: Python Connection
Write a Python script that:
1. Connects to your Neo4j instance
2. Creates a few nodes
3. Queries them back
4. Prints the results

### Exercise 2.4: Docker Configuration
Create a Docker Compose file that sets up Neo4j with:
- Persistent data volumes
- APOC and GDS plugins
- Custom memory settings

---

**Next Chapter: [Chapter 3: Graph Database Concepts](03-graph-database-concepts.md)**
