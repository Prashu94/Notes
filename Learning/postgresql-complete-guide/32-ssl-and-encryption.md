# SSL and Encryption

## Overview

PostgreSQL supports SSL/TLS encryption for secure client-server communication and provides various encryption capabilities for protecting data at rest and in transit. This guide covers SSL configuration, certificate management, data encryption, and security best practices.

## Table of Contents
- [SSL/TLS Basics](#ssltls-basics)
- [Configuring SSL Server](#configuring-ssl-server)
- [Client SSL Configuration](#client-ssl-configuration)
- [Certificate Management](#certificate-management)
- [SSL Modes](#ssl-modes)
- [Data Encryption](#data-encryption)
- [Column-Level Encryption](#column-level-encryption)
- [Transparent Data Encryption](#transparent-data-encryption)
- [Security Best Practices](#security-best-practices)

## SSL/TLS Basics

### Why Use SSL/TLS?

```sql
-- Without SSL:
-- - Data transmitted in plain text
-- - Passwords visible on network
-- - Vulnerable to man-in-the-middle attacks
-- - No server identity verification

-- With SSL:
-- - Encrypted communication
-- - Protected credentials
-- - Mutual authentication possible
-- - Data integrity verification

-- Check if connection is using SSL
SELECT * FROM pg_stat_ssl WHERE pid = pg_backend_pid();
-- Shows: ssl (true/false), version, cipher, bits

-- View all SSL connections
SELECT 
    pid,
    usename,
    client_addr,
    ssl,
    version,
    cipher
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
WHERE ssl = true;
```

### SSL Terminology

```sql
-- CA (Certificate Authority): Issues and signs certificates
-- Server Certificate: Proves server identity
-- Client Certificate: Proves client identity (optional)
-- Private Key: Secret key for decryption
-- Public Key: Distributed for encryption
-- Certificate Chain: CA -> Intermediate CA -> Server Cert

-- File types:
-- .key - Private key file
-- .crt/.cer/.pem - Certificate file
-- .csr - Certificate signing request
```

## Configuring SSL Server

### Basic SSL Setup

```sql
-- 1. Generate server certificate and key
-- (On server machine, not in SQL)

-- Generate private key
-- $ openssl genrsa -out server.key 2048

-- Generate certificate signing request
-- $ openssl req -new -key server.key -out server.csr

-- Generate self-signed certificate (for testing)
-- $ openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

-- Set proper permissions
-- $ chmod 600 server.key
-- $ chown postgres:postgres server.key server.crt

-- 2. Configure postgresql.conf
-- ssl = on
-- ssl_cert_file = 'server.crt'
-- ssl_key_file = 'server.key'
-- ssl_ca_file = 'root.crt'  -- Optional: for client cert verification

-- 3. Restart PostgreSQL
-- $ pg_ctl restart

-- 4. Verify SSL is enabled
SHOW ssl;  -- Should show 'on'
```

### SSL Configuration Parameters

```sql
-- In postgresql.conf:

-- Enable SSL
-- ssl = on

-- Certificate files (relative to data directory)
-- ssl_cert_file = 'server.crt'
-- ssl_key_file = 'server.key'
-- ssl_ca_file = 'root.crt'
-- ssl_crl_file = 'root.crl'  -- Certificate revocation list

-- SSL cipher configuration
-- ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
-- ssl_prefer_server_ciphers = on

-- SSL protocol versions
-- ssl_min_protocol_version = 'TLSv1.2'
-- ssl_max_protocol_version = ''  -- Empty = no max

-- DH parameters (for DHE ciphers)
-- ssl_dh_params_file = 'dh2048.pem'

-- ECDH curve
-- ssl_ecdh_curve = 'prime256v1'

-- Check current SSL configuration
SELECT name, setting, category 
FROM pg_settings 
WHERE name LIKE 'ssl%'
ORDER BY name;
```

### Requiring SSL in pg_hba.conf

```sql
-- pg_hba.conf entries:

-- Require SSL for all connections
-- hostssl  all  all  0.0.0.0/0  scram-sha-256

-- Require SSL with client certificate
-- hostssl  all  all  0.0.0.0/0  cert

-- Require SSL for specific database
-- hostssl  production  all  0.0.0.0/0  scram-sha-256

-- Require SSL for specific user
-- hostssl  all  admin  0.0.0.0/0  scram-sha-256

-- Allow non-SSL for local connections
-- host  all  all  127.0.0.1/32  scram-sha-256

-- Reject non-SSL remote connections
-- hostnossl  all  all  0.0.0.0/0  reject

-- After changes, reload configuration
SELECT pg_reload_conf();
```

## Client SSL Configuration

### Connection String SSL Parameters

```sql
-- Using connection string:

-- Require SSL
-- psql "postgresql://user@host/db?sslmode=require"

-- Verify server certificate
-- psql "postgresql://user@host/db?sslmode=verify-ca&sslrootcert=/path/to/ca.crt"

-- Verify hostname matches certificate
-- psql "postgresql://user@host/db?sslmode=verify-full&sslrootcert=/path/to/ca.crt"

-- With client certificate
-- psql "postgresql://user@host/db?sslmode=require&sslcert=/path/to/client.crt&sslkey=/path/to/client.key"

-- Environment variables:
-- export PGSSLMODE=require
-- export PGSSLROOTCERT=/path/to/ca.crt
-- export PGSSLCERT=/path/to/client.crt
-- export PGSSLKEY=/path/to/client.key
```

### Client Certificate Authentication

```sql
-- 1. Generate client certificate
-- $ openssl genrsa -out client.key 2048
-- $ openssl req -new -key client.key -out client.csr
-- $ openssl x509 -req -days 365 -in client.csr -CA root.crt -CAkey root.key -out client.crt

-- 2. Configure pg_hba.conf
-- hostssl  all  all  0.0.0.0/0  cert clientcert=verify-full

-- 3. Map certificate CN to PostgreSQL username
-- In pg_ident.conf:
-- cert_map  /^(.*)@example\.com$  \1

-- In pg_hba.conf:
-- hostssl  all  all  0.0.0.0/0  cert map=cert_map

-- 4. Connect with client certificate
-- psql "postgresql://user@host/db?sslmode=require&sslcert=client.crt&sslkey=client.key"

-- Verify client certificate info
SELECT 
    pid,
    usename,
    ssl_client_dn,
    ssl_client_serial
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
WHERE ssl = true AND ssl_client_dn IS NOT NULL;
```

## Certificate Management

### Creating Certificates

```sql
-- Production setup with proper CA:

-- 1. Create CA private key
-- $ openssl genrsa -aes256 -out ca.key 4096

-- 2. Create CA certificate
-- $ openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

-- 3. Create server private key
-- $ openssl genrsa -out server.key 2048

-- 4. Create server CSR
-- $ openssl req -new -key server.key -out server.csr
-- Important: CN must match hostname

-- 5. Sign server certificate with CA
-- $ openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt

-- 6. Verify certificate
-- $ openssl verify -CAfile ca.crt server.crt

-- 7. View certificate details
-- $ openssl x509 -in server.crt -text -noout
```

### Certificate Expiration

```sql
-- Check certificate expiration (on server)
-- $ openssl x509 -in server.crt -noout -enddate

-- Monitor certificate expiration
CREATE OR REPLACE FUNCTION check_ssl_cert_expiry()
RETURNS TABLE(days_until_expiry INTEGER) AS $$
DECLARE
    cert_end_date TEXT;
    expiry_days INTEGER;
BEGIN
    -- This would require extension or external script
    -- For demonstration purposes
    RAISE NOTICE 'Check SSL certificate expiration manually';
    RETURN QUERY SELECT NULL::INTEGER;
END;
$$ LANGUAGE plpgsql;

-- Set up monitoring alert for certificates expiring soon
-- Use external tools like:
-- - Nagios/Icinga
-- - Prometheus + Alertmanager
-- - Custom scripts checking openssl output
```

### Certificate Renewal

```sql
-- Renewal process:

-- 1. Generate new CSR (or reuse if CN unchanged)
-- $ openssl req -new -key server.key -out server-new.csr

-- 2. Sign new certificate
-- $ openssl x509 -req -days 365 -in server-new.csr -CA ca.crt -CAkey ca.key -out server-new.crt

-- 3. Test new certificate
-- $ openssl verify -CAfile ca.crt server-new.crt

-- 4. Backup old certificate
-- $ cp server.crt server.crt.old

-- 5. Replace certificate
-- $ cp server-new.crt server.crt

-- 6. Reload PostgreSQL (no downtime)
SELECT pg_reload_conf();

-- Or restart for certain configurations
-- $ pg_ctl restart
```

## SSL Modes

### Client SSL Modes

```sql
-- disable: No SSL, even if server supports it
-- psql "postgresql://user@host/db?sslmode=disable"
-- Use only for trusted networks

-- allow: Try non-SSL first, then SSL
-- psql "postgresql://user@host/db?sslmode=allow"
-- Not recommended (can be downgraded)

-- prefer: Try SSL first, then non-SSL (default)
-- psql "postgresql://user@host/db?sslmode=prefer"
-- Encrypted if server supports, but no verification

-- require: Require SSL, but don't verify certificate
-- psql "postgresql://user@host/db?sslmode=require"
-- Encrypted, but vulnerable to MITM with forged cert

-- verify-ca: Require SSL and verify server certificate is signed by trusted CA
-- psql "postgresql://user@host/db?sslmode=verify-ca&sslrootcert=ca.crt"
-- Encrypted and CA-verified

-- verify-full: Like verify-ca, plus verify hostname matches certificate
-- psql "postgresql://user@host/db?sslmode=verify-full&sslrootcert=ca.crt"
-- Most secure: encrypted, CA-verified, hostname-verified

-- Recommended for production: verify-full
```

### Testing SSL Modes

```sql
-- Test connection with different modes
-- psql "postgresql://user@localhost/db?sslmode=disable"
-- psql "postgresql://user@localhost/db?sslmode=require"
-- psql "postgresql://user@localhost/db?sslmode=verify-full"

-- Check current connection SSL status
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    ssl,
    version as ssl_version,
    cipher as ssl_cipher,
    bits as ssl_bits
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid)
WHERE pid = pg_backend_pid();

-- Verify SSL is enforced
-- Try connecting without SSL (should fail if required)
-- psql "postgresql://user@host/db?sslmode=disable"
```

## Data Encryption

### Password Encryption

```sql
-- Install pgcrypto extension
CREATE EXTENSION pgcrypto;

-- Hash password with crypt (bcrypt)
SELECT crypt('my_password', gen_salt('bf'));
-- Result: $2a$06$...hash...

-- Store hashed password
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

INSERT INTO users (username, password_hash)
VALUES ('john', crypt('secret123', gen_salt('bf')));

-- Verify password
SELECT * FROM users
WHERE username = 'john'
  AND password_hash = crypt('secret123', password_hash);

-- Different hash algorithms
SELECT crypt('password', gen_salt('des'));   -- DES (weak)
SELECT crypt('password', gen_salt('md5'));   -- MD5 (weak)
SELECT crypt('password', gen_salt('bf'));    -- Blowfish (good)
SELECT crypt('password', gen_salt('bf', 12)); -- Higher cost factor
```

### Symmetric Encryption

```sql
-- PGP symmetric encryption
SELECT pgp_sym_encrypt('sensitive data', 'encryption_key');
-- Result: bytea encrypted data

-- Decrypt
SELECT pgp_sym_decrypt(
    pgp_sym_encrypt('sensitive data', 'encryption_key'),
    'encryption_key'
);
-- Result: sensitive data

-- Store encrypted data
CREATE TABLE secure_data (
    id SERIAL PRIMARY KEY,
    encrypted_value BYTEA
);

INSERT INTO secure_data (encrypted_value)
VALUES (pgp_sym_encrypt('credit card: 1234-5678-9012-3456', 'secret_key'));

-- Query decrypted data
SELECT 
    id,
    pgp_sym_decrypt(encrypted_value, 'secret_key') as decrypted
FROM secure_data;
```

### Asymmetric Encryption

```sql
-- Generate key pair (outside PostgreSQL)
-- $ openssl genrsa -out private.key 2048
-- $ openssl rsa -in private.key -pubout -out public.key

-- Load public key
-- Read key into variable in application

-- Encrypt with public key
SELECT pgp_pub_encrypt('sensitive data', 
    dearmor('-----BEGIN PUBLIC KEY-----
    ...key content...
    -----END PUBLIC KEY-----')
);

-- Decrypt with private key
SELECT pgp_pub_decrypt(encrypted_data,
    dearmor('-----BEGIN PRIVATE KEY-----
    ...key content...
    -----END PRIVATE KEY-----')
);

-- Use for secure data exchange
-- Client encrypts with server's public key
-- Only server can decrypt with private key
```

## Column-Level Encryption

### Encrypting Specific Columns

```sql
-- Create table with encrypted columns
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    ssn_encrypted BYTEA,  -- Encrypted SSN
    credit_card_encrypted BYTEA,  -- Encrypted CC
    created_at TIMESTAMP DEFAULT now()
);

-- Insert with encryption
INSERT INTO customers (name, email, ssn_encrypted, credit_card_encrypted)
VALUES (
    'John Doe',
    'john@example.com',
    pgp_sym_encrypt('123-45-6789', 'encryption_key'),
    pgp_sym_encrypt('1234-5678-9012-3456', 'encryption_key')
);

-- Query with decryption
SELECT 
    id,
    name,
    email,
    pgp_sym_decrypt(ssn_encrypted, 'encryption_key') as ssn,
    '****-****-****-' || right(pgp_sym_decrypt(credit_card_encrypted, 'encryption_key')::TEXT, 4) as cc_masked
FROM customers;

-- Create view for encrypted columns
CREATE VIEW customers_decrypted AS
SELECT 
    id,
    name,
    email,
    pgp_sym_decrypt(ssn_encrypted, current_setting('app.encryption_key')) as ssn,
    pgp_sym_decrypt(credit_card_encrypted, current_setting('app.encryption_key')) as credit_card
FROM customers;

-- Set encryption key per session
SET app.encryption_key = 'secret_key';
SELECT * FROM customers_decrypted;
```

### Searchable Encryption

```sql
-- Problem: Can't search encrypted data
-- Solution: Store hash for searching

CREATE TABLE secure_users (
    id SERIAL PRIMARY KEY,
    email_encrypted BYTEA,
    email_hash TEXT,  -- For searching
    UNIQUE (email_hash)
);

-- Insert with encryption and hash
INSERT INTO secure_users (email_encrypted, email_hash)
VALUES (
    pgp_sym_encrypt('user@example.com', 'key'),
    encode(digest('user@example.com', 'sha256'), 'hex')
);

-- Search by hash
SELECT 
    id,
    pgp_sym_decrypt(email_encrypted, 'key') as email
FROM secure_users
WHERE email_hash = encode(digest('user@example.com', 'sha256'), 'hex');

-- Note: Hash reveals if same email exists (deterministic)
-- For privacy, use keyed hash (HMAC)
```

### Encryption Functions

```sql
-- PGP symmetric encryption
SELECT pgp_sym_encrypt(data, key);
SELECT pgp_sym_decrypt(encrypted, key);

-- PGP asymmetric encryption
SELECT pgp_pub_encrypt(data, public_key);
SELECT pgp_pub_decrypt(encrypted, private_key);

-- Raw encryption (not recommended)
SELECT encrypt(data, key, 'aes');
SELECT decrypt(encrypted, key, 'aes');

-- Hashing
SELECT digest(data, 'sha256');
SELECT digest(data, 'sha512');

-- HMAC (keyed hash)
SELECT hmac(data, key, 'sha256');

-- Armor/Dearmor (ASCII encoding)
SELECT armor(bytea_data);
SELECT dearmor(armored_text);

-- Generate random
SELECT gen_random_bytes(16);
SELECT gen_random_uuid();
```

## Transparent Data Encryption

### Filesystem-Level Encryption

```sql
-- PostgreSQL doesn't provide built-in TDE
-- Use OS-level encryption instead:

-- 1. LUKS (Linux Unified Key Setup)
-- Encrypt entire data partition
-- $ cryptsetup luksFormat /dev/sdb
-- $ cryptsetup open /dev/sdb pgdata
-- $ mkfs.ext4 /dev/mapper/pgdata

-- 2. dm-crypt
-- Similar to LUKS, Linux encryption

-- 3. ZFS encryption
-- $ zfs create -o encryption=aes-256-gcm pool/pgdata

-- 4. BitLocker (Windows)
-- Encrypt drive containing PostgreSQL data

-- 5. FileVault (macOS)
-- Encrypt volume with PostgreSQL data

-- Advantages:
-- - Transparent to PostgreSQL
-- - Protects backups
-- - No query performance impact (hardware acceleration)
-- - Protects against physical theft

-- Check if filesystem is encrypted (varies by OS)
-- Linux: lsblk -f
-- Show encrypted volumes
```

### Tablespace Encryption

```sql
-- Create encrypted tablespace (requires encrypted filesystem)

-- 1. Create encrypted filesystem mount
-- (Outside PostgreSQL)

-- 2. Create tablespace on encrypted mount
CREATE TABLESPACE encrypted_ts
LOCATION '/encrypted_mount/pgdata';

-- 3. Create tables in encrypted tablespace
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    data TEXT
) TABLESPACE encrypted_ts;

-- 4. Move existing table to encrypted tablespace
ALTER TABLE existing_table SET TABLESPACE encrypted_ts;

-- Query tablespace usage
SELECT 
    tablespace_name,
    location
FROM pg_tablespaces
WHERE tablespace_name = 'encrypted_ts';
```

## Security Best Practices

### 1. Always Use SSL in Production

```sql
-- postgresql.conf
-- ssl = on
-- ssl_min_protocol_version = 'TLSv1.2'
-- ssl_prefer_server_ciphers = on
-- ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'

-- pg_hba.conf
-- hostssl  all  all  0.0.0.0/0  scram-sha-256
-- hostnossl  all  all  0.0.0.0/0  reject  # Reject non-SSL

-- Client connection
-- sslmode=verify-full (most secure)
```

### 2. Secure Key Management

```sql
-- Never hardcode encryption keys
-- Bad:
-- SELECT pgp_sym_decrypt(data, 'hardcoded_key');

-- Good: Use environment variables or key management service
-- SET app.encryption_key = get_key_from_vault();
-- SELECT pgp_sym_decrypt(data, current_setting('app.encryption_key'));

-- Use separate keys for different data types
-- SET app.ssn_key = ...
-- SET app.cc_key = ...

-- Rotate keys periodically
-- Re-encrypt with new key, keep old key for decryption temporarily
```

### 3. Certificate Best Practices

```sql
-- Use strong key sizes (2048+ bits RSA, 256+ bits ECDSA)
-- Set appropriate certificate expiration (1 year recommended)
-- Monitor expiration dates
-- Use proper CA-signed certificates in production
-- Store private keys securely (chmod 600, encrypted filesystem)
-- Use certificate pinning for critical connections
-- Implement certificate revocation (CRL or OCSP)
```

### 4. Encrypt Sensitive Data

```sql
-- Identify sensitive columns
-- - Personally Identifiable Information (PII)
-- - Financial data (credit cards, bank accounts)
-- - Health records (HIPAA)
-- - Authentication credentials

-- Encrypt at rest (column-level or filesystem)
-- Encrypt in transit (SSL/TLS)
-- Encrypt backups
-- Secure key management
-- Audit access to encrypted data

-- Example: PCI DSS compliant credit card storage
CREATE TABLE payment_methods (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    cc_encrypted BYTEA,  -- Encrypted PAN
    cc_last4 TEXT,       -- Last 4 digits (unencrypted)
    cc_hash TEXT,        -- For duplicate detection
    created_at TIMESTAMP
);
```

### 5. Audit and Monitor

```sql
-- Log SSL connections
-- log_connections = on
-- log_line_prefix = '%m [%p] %u@%d %r '

-- Monitor SSL status
SELECT 
    count(*) FILTER (WHERE ssl) as ssl_connections,
    count(*) FILTER (WHERE NOT ssl) as non_ssl_connections
FROM pg_stat_ssl
JOIN pg_stat_activity USING (pid);

-- Alert on non-SSL connections (if required)
SELECT 
    usename,
    client_addr,
    application_name
FROM pg_stat_activity
WHERE ssl = false
  AND client_addr IS NOT NULL;

-- Log data access to encrypted columns
CREATE TRIGGER audit_sensitive_access
AFTER SELECT ON sensitive_table
FOR EACH STATEMENT
EXECUTE FUNCTION log_sensitive_access();
```

### 6. Regular Security Audits

```sql
-- Check SSL configuration
SELECT name, setting FROM pg_settings WHERE name LIKE 'ssl%';

-- Verify certificates valid
-- $ openssl x509 -in server.crt -noout -checkend 2592000  # 30 days

-- Review pg_hba.conf
-- Ensure SSL required where appropriate

-- Check for unencrypted sensitive data
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE column_name LIKE '%password%'
  AND data_type NOT IN ('bytea');  -- Should be encrypted

-- Review encryption key rotation schedule
-- Document last rotation date
-- Plan next rotation
```

## Summary

PostgreSQL SSL and encryption provides:
- **SSL/TLS**: Encrypted client-server communication
- **Certificate Authentication**: Mutual authentication with client certs
- **Data Encryption**: pgcrypto extension for column-level encryption
- **Transparent Encryption**: Filesystem-level encryption for data at rest
- **SSL Modes**: Various levels of security (disable to verify-full)
- **Best Practices**: Proper key management, certificate handling, monitoring

Encryption is essential for protecting sensitive data in transit and at rest.

## Next Steps

- Learn about [Authentication and Authorization](./30-authentication-authorization.md)
- Explore [Database Security](./33-database-security.md)
- Study [Backup and Recovery](./35-backup-and-recovery.md)
- Practice [Monitoring and Logging](./38-monitoring-and-logging.md)
