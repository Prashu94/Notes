# Chapter 2: Installation and Setup

## Table of Contents
- [System Requirements](#system-requirements)
- [Installing on macOS](#installing-on-macos)
- [Installing on Linux](#installing-on-linux)
- [Installing on Windows](#installing-on-windows)
- [Installing with Docker](#installing-with-docker)
- [MongoDB Shell (mongosh)](#mongodb-shell-mongosh)
- [MongoDB Compass](#mongodb-compass)
- [MongoDB Atlas Setup](#mongodb-atlas-setup)
- [Verifying Installation](#verifying-installation)
- [Summary](#summary)

---

## System Requirements

### Minimum Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 64-bit x86_64 | Multi-core processor |
| RAM | 4 GB | 8 GB or more |
| Disk Space | 10 GB | SSD recommended |
| Network | 1 Gbps | Low latency network |

### Supported Operating Systems

| Platform | Versions |
|----------|----------|
| **Windows** | Windows 10, Server 2016, 2019, 2022 |
| **macOS** | macOS 11+ (Big Sur and later) |
| **Ubuntu** | 20.04, 22.04, 24.04 LTS |
| **Debian** | 11, 12 |
| **RHEL/CentOS** | 7, 8, 9 |
| **Amazon Linux** | 2, 2023 |

### File System Recommendations

- **Preferred**: XFS, ext4
- **macOS**: APFS
- **Windows**: NTFS
- **Avoid**: NFS (for data files)

---

## Installing on macOS

### Method 1: Using Homebrew (Recommended)

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add MongoDB tap
brew tap mongodb/brew

# Update Homebrew
brew update

# Install MongoDB Community Edition
brew install mongodb-community@7.0

# Install the MongoDB Shell (mongosh)
brew install mongosh
```

### Starting MongoDB as a Service

```bash
# Start MongoDB as a background service
brew services start mongodb-community@7.0

# Check status
brew services list

# Stop MongoDB
brew services stop mongodb-community@7.0

# Restart MongoDB
brew services restart mongodb-community@7.0
```

### Running MongoDB Manually

```bash
# Run MongoDB in the foreground
mongod --config /opt/homebrew/etc/mongod.conf

# Default configuration file location (Apple Silicon)
/opt/homebrew/etc/mongod.conf

# Default configuration file location (Intel)
/usr/local/etc/mongod.conf
```

### Default Directories (macOS)

| Item | Location |
|------|----------|
| Configuration | `/opt/homebrew/etc/mongod.conf` |
| Data Directory | `/opt/homebrew/var/mongodb` |
| Log File | `/opt/homebrew/var/log/mongodb/mongo.log` |
| Binaries | `/opt/homebrew/opt/mongodb-community@7.0/bin/` |

---

## Installing on Linux

### Ubuntu/Debian Installation

```bash
# Import MongoDB public GPG key
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

# Create list file for MongoDB (Ubuntu 22.04)
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update package list
sudo apt-get update

# Install MongoDB Community Edition
sudo apt-get install -y mongodb-org

# Pin packages to prevent unintended upgrades
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-database hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-mongosh hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
```

### RHEL/CentOS Installation

```bash
# Create repo file
sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo << 'EOF'
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/$releasever/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-7.0.asc
EOF

# Install MongoDB
sudo yum install -y mongodb-org

# For RHEL 9 / CentOS Stream 9, use dnf
sudo dnf install -y mongodb-org
```

### Managing MongoDB Service (systemd)

```bash
# Start MongoDB
sudo systemctl start mongod

# Enable auto-start on boot
sudo systemctl enable mongod

# Check status
sudo systemctl status mongod

# Stop MongoDB
sudo systemctl stop mongod

# Restart MongoDB
sudo systemctl restart mongod

# View logs
sudo journalctl -u mongod -f
```

### Default Directories (Linux)

| Item | Location |
|------|----------|
| Configuration | `/etc/mongod.conf` |
| Data Directory | `/var/lib/mongodb` |
| Log File | `/var/log/mongodb/mongod.log` |
| Binaries | `/usr/bin/` |
| PID File | `/var/run/mongodb/mongod.pid` |

---

## Installing on Windows

### Method 1: MSI Installer (Recommended)

1. **Download** the MSI installer from [MongoDB Download Center](https://www.mongodb.com/try/download/community)

2. **Run the installer** and follow the wizard:
   - Choose "Complete" installation
   - Check "Install MongoDB as a Service"
   - Check "Install MongoDB Compass" (optional)

3. **Configure service** (optional):
   - Service Name: MongoDB
   - Data Directory: `C:\Program Files\MongoDB\Server\7.0\data`
   - Log Directory: `C:\Program Files\MongoDB\Server\7.0\log`

### Method 2: Manual Installation

```powershell
# Download MongoDB ZIP
# Extract to C:\mongodb

# Create data and log directories
mkdir C:\data\db
mkdir C:\data\log

# Start MongoDB
mongod --dbpath C:\data\db --logpath C:\data\log\mongod.log
```

### Installing as a Windows Service

```powershell
# Create configuration file C:\mongodb\mongod.cfg
@"
systemLog:
    destination: file
    path: C:\data\log\mongod.log
storage:
    dbPath: C:\data\db
net:
    port: 27017
    bindIp: 127.0.0.1
"@ | Out-File -FilePath C:\mongodb\mongod.cfg -Encoding UTF8

# Install as service
mongod --config "C:\mongodb\mongod.cfg" --install

# Start service
net start MongoDB

# Stop service
net stop MongoDB
```

### Default Directories (Windows)

| Item | Location |
|------|----------|
| Installation | `C:\Program Files\MongoDB\Server\7.0\` |
| Data Directory | `C:\Program Files\MongoDB\Server\7.0\data\` |
| Log File | `C:\Program Files\MongoDB\Server\7.0\log\mongod.log` |
| Configuration | `C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg` |

---

## Installing with Docker

### Basic Docker Setup

```bash
# Pull the official MongoDB image
docker pull mongo:7.0

# Run MongoDB container
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:7.0

# Run with persistent volume
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password123 \
  mongo:7.0

# Access MongoDB shell in container
docker exec -it mongodb mongosh -u admin -p password123
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password123
      MONGO_INITDB_DATABASE: myapp
    volumes:
      - mongodb_data:/data/db
      - mongodb_config:/data/configdb
      - ./init-scripts:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  mongo-express:
    image: mongo-express:latest
    container_name: mongo-express
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: admin
      ME_CONFIG_MONGODB_ADMINPASSWORD: password123
      ME_CONFIG_MONGODB_SERVER: mongodb
      ME_CONFIG_BASICAUTH_USERNAME: admin
      ME_CONFIG_BASICAUTH_PASSWORD: admin123
    depends_on:
      mongodb:
        condition: service_healthy

volumes:
  mongodb_data:
  mongodb_config:
```

### Initialization Script

```javascript
// init-scripts/01-init.js
// This runs automatically on first container start

// Switch to your application database
db = db.getSiblingDB('myapp');

// Create collections
db.createCollection('users');
db.createCollection('products');

// Create indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.products.createIndex({ sku: 1 }, { unique: true });
db.products.createIndex({ name: "text", description: "text" });

// Insert sample data
db.users.insertMany([
    {
        email: "admin@example.com",
        name: "Admin User",
        role: "admin",
        createdAt: new Date()
    },
    {
        email: "user@example.com",
        name: "Regular User",
        role: "user",
        createdAt: new Date()
    }
]);

print('Database initialized successfully!');
```

### Docker Commands Reference

```bash
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f mongodb

# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Connect to MongoDB shell
docker exec -it mongodb mongosh -u admin -p password123

# Backup database
docker exec mongodb mongodump -u admin -p password123 --archive=/data/db/backup.archive

# Copy backup to host
docker cp mongodb:/data/db/backup.archive ./backup.archive
```

---

## MongoDB Shell (mongosh)

### Installing mongosh

```bash
# macOS (Homebrew)
brew install mongosh

# Ubuntu/Debian
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
sudo apt-get install -y mongodb-mongosh

# Windows (Already included with MSI installer)
# Or download separately from MongoDB Download Center

# npm (any platform)
npm install -g mongosh
```

### Connecting to MongoDB

```bash
# Connect to local MongoDB
mongosh

# Connect with host and port
mongosh "mongodb://localhost:27017"

# Connect with authentication
mongosh "mongodb://username:password@localhost:27017/dbname"

# Connect to replica set
mongosh "mongodb://host1:27017,host2:27017,host3:27017/dbname?replicaSet=myReplicaSet"

# Connect to MongoDB Atlas
mongosh "mongodb+srv://username:password@cluster.mongodb.net/dbname"
```

### Basic Shell Commands

```javascript
// Show all databases
show dbs

// Switch to database (creates if doesn't exist)
use myDatabase

// Show current database
db

// Show collections
show collections

// Get help
help

// Exit shell
exit
// or
quit()
// or Ctrl+C twice
```

### Shell Configuration

```javascript
// Create ~/.mongoshrc.js for custom config
// Custom prompt
prompt = () => {
    return `[${db.getName()}]> `;
};

// Enable pretty printing
config.set("displayBatchSize", 30);

// Custom colors
config.set("inspectDepth", 10);
```

---

## MongoDB Compass

### Features Overview

MongoDB Compass is the official GUI for MongoDB:

- **Visual Data Exploration**: Browse documents visually
- **Query Building**: Build queries with visual query builder
- **Aggregation Pipeline Builder**: Create pipelines visually
- **Index Management**: Create and analyze indexes
- **Schema Analysis**: Visualize document structure
- **Performance Insights**: Real-time server stats
- **Validation Rules**: Create and test schema validation

### Installing Compass

1. **Download** from [MongoDB Compass](https://www.mongodb.com/try/download/compass)
2. **Install** using the installer for your platform
3. **Launch** and connect to your MongoDB instance

### Connecting with Compass

```
# Local connection
mongodb://localhost:27017

# With authentication
mongodb://username:password@localhost:27017/admin?authSource=admin

# MongoDB Atlas
mongodb+srv://username:password@cluster.mongodb.net/
```

### Compass Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  MongoDB Compass                                    [─] [□] [X] │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐  ┌───────────────────────────────────────────┐ │
│ │ Databases   │  │ Documents | Schema | Explain | Indexes    │ │
│ │             │  ├───────────────────────────────────────────┤ │
│ │ ► admin     │  │                                           │ │
│ │ ► config    │  │  {                                        │ │
│ │ ▼ myapp     │  │    "_id": ObjectId("..."),               │ │
│ │   ► users   │  │    "name": "John",                       │ │
│ │   ► orders  │  │    "email": "john@example.com"           │ │
│ │   ► products│  │  }                                        │ │
│ │ ► local     │  │                                           │ │
│ └─────────────┘  └───────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Filter: { status: "active" }                    [Find] [Reset] │
└─────────────────────────────────────────────────────────────────┘
```

---

## MongoDB Atlas Setup

### Creating an Atlas Account

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click "Try Free" or "Get Started Free"
3. Sign up with email or OAuth (Google, GitHub)
4. Verify email address

### Creating a Free Cluster

1. **Choose deployment type**: Shared (Free tier)
2. **Select cloud provider**: AWS, GCP, or Azure
3. **Select region**: Choose closest to your location
4. **Cluster tier**: M0 Sandbox (Free Forever)
5. **Cluster name**: myFirstCluster
6. Click "Create Cluster"

### Configuring Security

#### Database User

```
1. Go to Database Access
2. Click "Add New Database User"
3. Authentication Method: Password
4. Username: myUser
5. Password: <strong password>
6. Database User Privileges: 
   - Atlas admin (for learning)
   - Or custom roles for production
7. Click "Add User"
```

#### Network Access

```
1. Go to Network Access
2. Click "Add IP Address"
3. Options:
   - "Add Current IP Address" (your computer)
   - "Allow Access from Anywhere" (0.0.0.0/0) - for development only
   - Specific CIDR block for production
4. Click "Confirm"
```

### Getting Connection String

```bash
# Click "Connect" on your cluster
# Choose "Connect your application"
# Select driver and version
# Copy connection string

# Example connection string
mongodb+srv://myUser:<password>@mycluster.xxxxx.mongodb.net/?retryWrites=true&w=majority

# Replace <password> with your actual password
```

### Connecting to Atlas

```bash
# Using mongosh
mongosh "mongodb+srv://myUser:myPassword@mycluster.xxxxx.mongodb.net/myDatabase"

# Using Compass
# Paste the connection string in "New Connection"
```

### Atlas Interface Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  MongoDB Atlas                           [⚙️ Settings] [User] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Organizations > My Project > myFirstCluster                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Cluster Overview                                         │   │
│  │                                                         │   │
│  │  Cluster: myFirstCluster (M0)     Status: Active        │   │
│  │  Provider: AWS                    Region: us-east-1     │   │
│  │                                                         │   │
│  │  [Connect] [Collections] [Metrics] [Search] [Triggers]  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐  │
│  │ Databases  │ │ Collections│ │ Network    │ │ Database   │  │
│  │ Access     │ │ Browse     │ │ Access     │ │ Access     │  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Verifying Installation

### Test Local Installation

```javascript
// Connect to MongoDB
mongosh

// Check version
db.version()

// Check server status
db.serverStatus()

// Create a test database
use testdb

// Insert a document
db.test.insertOne({ message: "Hello MongoDB!", timestamp: new Date() })

// Find the document
db.test.find()

// Output:
// { _id: ObjectId("..."), message: "Hello MongoDB!", timestamp: ISODate("...") }

// Clean up
db.test.drop()

// Exit
exit
```

### Verify Server Status

```javascript
// Server information
db.serverStatus()

// Simpler status check
db.runCommand({ ping: 1 })
// Output: { ok: 1 }

// Host info
db.hostInfo()

// Current operations
db.currentOp()

// Server build info
db.version()
// Output: "7.0.x"

db.serverBuildInfo()
```

### Check Server Logs

```bash
# macOS (Homebrew)
tail -f /opt/homebrew/var/log/mongodb/mongo.log

# Linux
tail -f /var/log/mongodb/mongod.log

# Docker
docker logs -f mongodb

# Windows
type "C:\Program Files\MongoDB\Server\7.0\log\mongod.log"
```

### Diagnostic Commands

```javascript
// Database statistics
db.stats()

// Collection statistics
db.collection.stats()

// Index statistics
db.collection.aggregate([{ $indexStats: {} }])

// Connection information
db.runCommand({ connectionStatus: 1 })

// Server configuration
db.adminCommand({ getCmdLineOpts: 1 })
```

---

## Configuration File Reference

### Sample Configuration (mongod.conf)

```yaml
# mongod.conf - MongoDB Configuration File

# Where to store data
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  # Use WiredTiger storage engine
  engine: wiredTiger
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2

# Where to write logs
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: reopen

# Network interfaces
net:
  port: 27017
  bindIp: 127.0.0.1
  # Enable IPv6
  ipv6: false

# Process management
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
  # Fork server process (daemon mode)
  # fork: true
  # pidFilePath: /var/run/mongodb/mongod.pid

# Security settings
security:
  # Enable authentication
  # authorization: enabled
  # keyFile: /path/to/keyfile

# Operation profiling
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

# Replication settings
# replication:
#   replSetName: myReplicaSet

# Sharding settings
# sharding:
#   clusterRole: shardsvr
```

### Key Configuration Options

| Section | Option | Description |
|---------|--------|-------------|
| storage | dbPath | Data file location |
| storage | engine | Storage engine (wiredTiger) |
| systemLog | path | Log file location |
| net | port | Network port (default: 27017) |
| net | bindIp | IP addresses to bind |
| security | authorization | Enable auth (enabled/disabled) |
| replication | replSetName | Replica set name |

---

## Summary

### Key Takeaways

1. **Multiple installation methods** available for each platform
2. **Docker** provides the easiest setup for development
3. **mongosh** is the modern shell for MongoDB interaction
4. **MongoDB Compass** offers visual database management
5. **MongoDB Atlas** provides free cloud hosting for learning
6. **Configuration files** control MongoDB behavior
7. **Always verify installation** with basic commands

### Quick Start Checklist

- [ ] Install MongoDB server
- [ ] Install mongosh (MongoDB Shell)
- [ ] Start MongoDB service
- [ ] Verify with `mongosh` connection
- [ ] Test with basic CRUD operations
- [ ] Install MongoDB Compass (optional)
- [ ] Create MongoDB Atlas account (optional)

### What's Next?

In the next chapter, we'll explore MongoDB's architecture in detail, understanding how data is stored and managed internally.

---

## Practice Exercises

### Exercise 1: Local Installation

1. Install MongoDB Community Edition on your system
2. Start the MongoDB service
3. Connect using mongosh
4. Create a database called "practice"
5. Insert a test document
6. Verify the document was created

### Exercise 2: Docker Setup

1. Create a docker-compose.yml file for MongoDB
2. Add an initialization script
3. Start the containers
4. Connect to MongoDB in the container
5. Verify the initialization script ran successfully

### Exercise 3: MongoDB Atlas

1. Create a MongoDB Atlas account
2. Create a free M0 cluster
3. Configure database user and network access
4. Connect using mongosh with the connection string
5. Create a collection and insert data

---

[← Previous: Introduction to MongoDB](01-introduction-to-mongodb.md) | [Next: MongoDB Architecture →](03-mongodb-architecture.md)
