# Installation and Setup

## System Requirements

### Minimum Requirements
- **CPU**: 1 GHz processor
- **RAM**: 1 GB (2 GB recommended)
- **Disk**: 100 MB for software + space for data
- **OS**: Linux, macOS, Windows, BSD

### Recommended for Production
- **CPU**: Multi-core processor
- **RAM**: 4+ GB
- **Disk**: SSD storage
- **OS**: Linux (Ubuntu, CentOS, Debian)

## Installation Methods

### 1. macOS Installation

#### Using Homebrew (Recommended)

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@16

# Start PostgreSQL service
brew services start postgresql@16

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
echo 'export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Using Postgres.app

1. Download from [postgresapp.com](https://postgresapp.com/)
2. Drag to Applications folder
3. Launch the app
4. Click "Initialize" to create a new server
5. Configure PATH in your shell profile

```bash
# Add to ~/.zshrc
export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/latest/bin
```

#### Using Official Installer

1. Download from [postgresql.org/download/macosx](https://www.postgresql.org/download/macosx/)
2. Run the .dmg installer
3. Follow installation wizard
4. Set password for postgres user

### 2. Linux Installation

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Check service status
sudo systemctl status postgresql

# Enable auto-start on boot
sudo systemctl enable postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

#### CentOS/RHEL/Fedora

```bash
# Install PostgreSQL repository
sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Disable built-in PostgreSQL module (RHEL 8+)
sudo dnf -qy module disable postgresql

# Install PostgreSQL 16
sudo dnf install -y postgresql16-server

# Initialize database
sudo /usr/pgsql-16/bin/postgresql-16-setup initdb

# Enable and start service
sudo systemctl enable postgresql-16
sudo systemctl start postgresql-16
```

#### Arch Linux

```bash
# Install PostgreSQL
sudo pacman -S postgresql

# Initialize database cluster
sudo -iu postgres initdb -D /var/lib/postgres/data

# Start and enable service
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 3. Windows Installation

#### Using Official Installer

1. Download from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run the installer (.exe file)
3. Follow installation wizard:
   - Choose installation directory
   - Select components (Server, pgAdmin 4, Command Line Tools)
   - Set data directory
   - Set password for postgres superuser
   - Set port (default: 5432)
   - Set locale
4. Complete installation
5. PostgreSQL installed as Windows service

#### Using Chocolatey

```powershell
# Install Chocolatey (if not installed)
# Run in PowerShell as Administrator

# Install PostgreSQL
choco install postgresql

# Service is automatically started
```

### 4. Docker Installation

```bash
# Pull PostgreSQL image
docker pull postgres:16

# Run PostgreSQL container
docker run --name postgres-dev \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=mydb \
  -p 5432:5432 \
  -v postgres-data:/var/lib/postgresql/data \
  -d postgres:16

# Connect to PostgreSQL
docker exec -it postgres-dev psql -U postgres

# Stop container
docker stop postgres-dev

# Start container
docker start postgres-dev

# Remove container
docker rm postgres-dev
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:16
    container_name: postgres-dev
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
      POSTGRES_DB: testdb
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres-data:
```

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f postgres
```

## Initial Configuration

### 1. Accessing PostgreSQL

#### Switch to postgres User (Linux/macOS)

```bash
# Switch to postgres user
sudo -i -u postgres

# Access PostgreSQL prompt
psql

# Or in one command
sudo -u postgres psql
```

#### Direct Access (if configured)

```bash
# Connect as postgres user
psql -U postgres

# Connect to specific database
psql -U postgres -d mydb

# Connect to remote server
psql -h localhost -p 5432 -U postgres -d mydb
```

### 2. Setting Up Password

```sql
-- Set password for postgres user
ALTER USER postgres PASSWORD 'your_secure_password';

-- Create new superuser
CREATE USER admin WITH SUPERUSER PASSWORD 'admin_password';

-- Create regular user
CREATE USER myuser WITH PASSWORD 'user_password';
```

### 3. Creating Your First Database

```sql
-- Create database
CREATE DATABASE myapp;

-- Create database with owner
CREATE DATABASE myapp OWNER myuser;

-- List all databases
\l

-- Connect to database
\c myapp

-- Show current database
SELECT current_database();
```

### 4. Configuration Files

#### Key Configuration Files

1. **postgresql.conf**: Main configuration file
2. **pg_hba.conf**: Client authentication configuration
3. **pg_ident.conf**: User name mapping

#### Finding Configuration Files

```sql
-- Show config file locations
SHOW config_file;
SHOW hba_file;
SHOW data_directory;
```

#### Common Locations

**Linux**:
- `/etc/postgresql/16/main/postgresql.conf`
- `/var/lib/postgresql/16/main/`

**macOS (Homebrew)**:
- `/opt/homebrew/var/postgresql@16/`

**Windows**:
- `C:\Program Files\PostgreSQL\16\data\`

### 5. Basic Configuration Settings

#### Edit postgresql.conf

```bash
# Find and edit configuration
sudo nano /etc/postgresql/16/main/postgresql.conf
```

**Important Settings**:

```conf
# Connection Settings
listen_addresses = 'localhost'  # Change to '*' for all interfaces
port = 5432
max_connections = 100

# Memory Settings
shared_buffers = 256MB          # 25% of RAM
effective_cache_size = 1GB      # 50-75% of RAM
work_mem = 4MB
maintenance_work_mem = 64MB

# Write-Ahead Log
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB

# Query Planning
random_page_cost = 1.1          # For SSD
effective_io_concurrency = 200  # For SSD

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'           # For development only
log_min_duration_statement = 1000  # Log slow queries (ms)
```

#### Edit pg_hba.conf (Authentication)

```bash
# Edit authentication file
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

**Common Configurations**:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 local connections
host    all             all             127.0.0.1/32            md5

# IPv6 local connections
host    all             all             ::1/128                 md5

# Allow remote connections (use with caution)
host    all             all             0.0.0.0/0               md5
```

**Authentication Methods**:
- `trust`: Allow connection without password (not secure)
- `md5`: Password authentication with MD5 hashing
- `scram-sha-256`: More secure password authentication
- `peer`: Use OS username (local connections only)
- `ident`: Use ident server

### 6. Reload Configuration

```bash
# Reload configuration without restart
sudo systemctl reload postgresql

# Or using SQL
SELECT pg_reload_conf();

# Restart PostgreSQL (for major changes)
sudo systemctl restart postgresql
```

## Verifying Installation

### 1. Check Version

```bash
# Check PostgreSQL version
psql --version
postgres --version

# In psql
SELECT version();
```

### 2. Check Service Status

```bash
# Linux
sudo systemctl status postgresql

# macOS (Homebrew)
brew services list

# Check if listening on port
sudo lsof -i :5432
# Or
sudo netstat -tlnp | grep 5432
```

### 3. Test Connection

```bash
# Test local connection
psql -U postgres -c "SELECT 1;"

# Test with specific database
psql -U postgres -d postgres -c "SELECT current_database();"
```

## Installing pgAdmin (GUI Tool)

### macOS

```bash
# Using Homebrew
brew install --cask pgadmin4
```

### Linux

```bash
# Ubuntu/Debian
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

sudo apt update
sudo apt install pgadmin4-desktop
```

### Windows

Download from [pgadmin.org](https://www.pgadmin.org/download/)

### Access pgAdmin

1. Launch pgAdmin
2. Set master password
3. Add new server:
   - Name: Local PostgreSQL
   - Host: localhost
   - Port: 5432
   - Username: postgres
   - Password: your_password

## Setting Up Development Environment

### 1. Install Client Libraries

#### Python

```bash
pip install psycopg2-binary
# Or for production
pip install psycopg2
```

#### Node.js

```bash
npm install pg
```

#### Java

```xml
<!-- Maven -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.0</version>
</dependency>
```

#### Go

```bash
go get github.com/lib/pq
```

### 2. Environment Variables

```bash
# Add to ~/.zshrc or ~/.bashrc
export PGHOST=localhost
export PGPORT=5432
export PGUSER=postgres
export PGPASSWORD=your_password
export PGDATABASE=postgres

# For security, use .pgpass file instead
# Create ~/.pgpass file
echo "localhost:5432:*:postgres:your_password" > ~/.pgpass
chmod 600 ~/.pgpass
```

### 3. Create Development Database

```sql
-- Create development database
CREATE DATABASE dev_db;

-- Create test database
CREATE DATABASE test_db;

-- Create user for development
CREATE USER dev_user WITH PASSWORD 'dev_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dev_db TO dev_user;
GRANT ALL PRIVILEGES ON DATABASE test_db TO dev_user;

-- Connect and grant schema privileges
\c dev_db
GRANT ALL ON SCHEMA public TO dev_user;
```

## Common Installation Issues

### Issue 1: Port Already in Use

```bash
# Find process using port 5432
sudo lsof -i :5432

# Kill the process
sudo kill -9 <PID>

# Or change PostgreSQL port in postgresql.conf
port = 5433
```

### Issue 2: Permission Denied

```bash
# Fix data directory permissions (Linux)
sudo chown -R postgres:postgres /var/lib/postgresql/16/main
sudo chmod 750 /var/lib/postgresql/16/main
```

### Issue 3: Cannot Connect to Server

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# Verify pg_hba.conf settings
sudo cat /etc/postgresql/16/main/pg_hba.conf
```

### Issue 4: Password Authentication Failed

```sql
-- Reset password
sudo -u postgres psql
ALTER USER postgres PASSWORD 'new_password';
```

## Uninstallation

### macOS (Homebrew)

```bash
brew services stop postgresql@16
brew uninstall postgresql@16
rm -rf /opt/homebrew/var/postgresql@16
```

### Linux (Ubuntu/Debian)

```bash
sudo systemctl stop postgresql
sudo apt-get --purge remove postgresql postgresql-*
sudo rm -rf /var/lib/postgresql
sudo rm -rf /etc/postgresql
sudo userdel -r postgres
```

### Windows

1. Use "Add or Remove Programs"
2. Uninstall PostgreSQL
3. Manually delete data directory if needed

## Next Steps

- [PostgreSQL Architecture](03-postgresql-architecture.md)
- [Data Types](04-data-types.md)
- [Basic SQL Operations](05-basic-sql-operations.md)

## Summary

You've learned how to:
- Install PostgreSQL on different operating systems
- Configure basic settings
- Set up authentication
- Create databases and users
- Install GUI tools
- Troubleshoot common issues

Your PostgreSQL installation is now ready for development!
