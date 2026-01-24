# Part 9: Special Topics Exercises

## Topics Covered
- PostgreSQL with Python (Chapter 39)
- PostgreSQL with Node.js (Chapter 40)
- Connection Pooling (Chapter 41)
- Concurrency Control (Chapter 42)
- MVCC Deep Dive (Chapter 43)

---

## Exercise 9.1: Python Application Integration 🟡

### Scenario
Build a Python banking operations module that handles transactions, customer management, and reporting for NeoBank's internal tools.

### Requirements
1. Proper connection management with context managers
2. Parameterized queries for security
3. Transaction handling with savepoints
4. Async operations for high throughput

### Solution

```python
# neobank_db.py - Database Operations Module

import asyncio
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

import psycopg2
from psycopg2 import sql, extras
from psycopg2.pool import ThreadedConnectionPool
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration and Connection Management
# =============================================================================

@dataclass
class DatabaseConfig:
    """Database configuration container."""
    host: str = "localhost"
    port: int = 5432
    database: str = "neobank"
    user: str = "neobank_app"
    password: str = "secure_password"
    min_connections: int = 5
    max_connections: int = 20
    
    @property
    def dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseManager:
    """Manages database connections with pooling."""
    
    _instance = None
    _pool = None
    
    def __new__(cls, config: DatabaseConfig = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = config or DatabaseConfig()
            cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self):
        """Initialize the connection pool."""
        self._pool = ThreadedConnectionPool(
            minconn=self._config.min_connections,
            maxconn=self._config.max_connections,
            host=self._config.host,
            port=self._config.port,
            database=self._config.database,
            user=self._config.user,
            password=self._config.password
        )
        logger.info(f"Connection pool initialized with {self._config.min_connections}-{self._config.max_connections} connections")
    
    @contextmanager
    def get_connection(self):
        """Context manager for getting a connection from the pool."""
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit: bool = True, cursor_factory=None):
        """Context manager for getting a cursor with automatic commit/rollback."""
        with self.get_connection() as conn:
            cursor_kwargs = {}
            if cursor_factory:
                cursor_kwargs['cursor_factory'] = cursor_factory
            cursor = conn.cursor(**cursor_kwargs)
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                cursor.close()
    
    def close(self):
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Connection pool closed")


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class Customer:
    customer_id: UUID
    customer_number: str
    first_name: str
    last_name: str
    email: str
    phone_primary: str
    customer_type: str
    customer_status: str
    created_at: datetime


@dataclass
class Account:
    account_id: UUID
    customer_id: UUID
    account_number: str
    account_type: str
    currency_code: str
    current_balance: Decimal
    available_balance: Decimal
    account_status: str


@dataclass
class Transaction:
    transaction_id: UUID
    account_id: UUID
    transaction_type: str
    amount: Decimal
    currency_code: str
    running_balance: Decimal
    description: str
    transaction_date: datetime


# =============================================================================
# Repository Classes (Data Access Layer)
# =============================================================================

class CustomerRepository:
    """Repository for customer operations."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_by_id(self, customer_id: UUID) -> Optional[Customer]:
        """Retrieve a customer by ID."""
        query = """
            SELECT customer_id, customer_number, first_name, last_name, 
                   email, phone_primary, customer_type, customer_status, created_at
            FROM banking.customers
            WHERE customer_id = %s
        """
        with self.db.get_cursor(commit=False, cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, (str(customer_id),))
            row = cur.fetchone()
            if row:
                return Customer(**row)
        return None
    
    def search(self, 
               email: str = None, 
               phone: str = None,
               status: str = None,
               limit: int = 100) -> List[Customer]:
        """Search customers with filters."""
        conditions = []
        params = []
        
        if email:
            conditions.append("email ILIKE %s")
            params.append(f"%{email}%")
        if phone:
            conditions.append("phone_primary LIKE %s")
            params.append(f"%{phone}%")
        if status:
            conditions.append("customer_status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions) if conditions else "TRUE"
        
        query = f"""
            SELECT customer_id, customer_number, first_name, last_name,
                   email, phone_primary, customer_type, customer_status, created_at
            FROM banking.customers
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s
        """
        params.append(limit)
        
        with self.db.get_cursor(commit=False, cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return [Customer(**row) for row in cur.fetchall()]
    
    def create(self, customer_data: Dict[str, Any]) -> UUID:
        """Create a new customer."""
        query = """
            INSERT INTO banking.customers (
                first_name, last_name, email, phone_primary, 
                date_of_birth, customer_type
            ) VALUES (
                %(first_name)s, %(last_name)s, %(email)s, %(phone_primary)s,
                %(date_of_birth)s, %(customer_type)s
            )
            RETURNING customer_id
        """
        with self.db.get_cursor(commit=True) as cur:
            cur.execute(query, customer_data)
            return cur.fetchone()[0]
    
    def update(self, customer_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update customer fields."""
        # Build dynamic UPDATE query safely
        set_clauses = []
        params = []
        
        allowed_fields = {'first_name', 'last_name', 'email', 'phone_primary', 
                         'phone_secondary', 'customer_status'}
        
        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(sql.SQL("{} = %s").format(sql.Identifier(field)))
                params.append(value)
        
        if not set_clauses:
            return False
        
        params.append(str(customer_id))
        
        query = sql.SQL("""
            UPDATE banking.customers
            SET {}, updated_at = NOW()
            WHERE customer_id = %s
        """).format(sql.SQL(", ").join(set_clauses))
        
        with self.db.get_cursor(commit=True) as cur:
            cur.execute(query, params)
            return cur.rowcount > 0


class TransactionRepository:
    """Repository for transaction operations with proper ACID handling."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def execute_transfer(self, 
                        from_account_id: UUID, 
                        to_account_id: UUID,
                        amount: Decimal,
                        description: str = "Transfer") -> Dict[str, Any]:
        """
        Execute a transfer between accounts with full ACID compliance.
        Uses savepoints for complex transaction control.
        """
        with self.db.get_connection() as conn:
            conn.autocommit = False
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            
            try:
                # Start transaction and create savepoint
                cursor.execute("SAVEPOINT transfer_start")
                
                # Step 1: Lock accounts in consistent order to prevent deadlocks
                account_ids = sorted([str(from_account_id), str(to_account_id)])
                cursor.execute("""
                    SELECT account_id, account_number, current_balance, available_balance,
                           account_status, currency_code
                    FROM banking.accounts
                    WHERE account_id IN %s
                    ORDER BY account_id
                    FOR UPDATE
                """, (tuple(account_ids),))
                
                accounts = {str(row['account_id']): row for row in cursor.fetchall()}
                
                from_account = accounts.get(str(from_account_id))
                to_account = accounts.get(str(to_account_id))
                
                # Validate accounts
                if not from_account or not to_account:
                    raise ValueError("One or both accounts not found")
                
                if from_account['account_status'] != 'active' or to_account['account_status'] != 'active':
                    raise ValueError("Account(s) not active")
                
                if from_account['currency_code'] != to_account['currency_code']:
                    raise ValueError("Currency mismatch - cross-currency transfer not implemented")
                
                if from_account['available_balance'] < amount:
                    raise ValueError(f"Insufficient funds: available {from_account['available_balance']}, requested {amount}")
                
                # Step 2: Update balances
                cursor.execute("SAVEPOINT balance_updates")
                
                # Debit source account
                cursor.execute("""
                    UPDATE banking.accounts
                    SET current_balance = current_balance - %s,
                        available_balance = available_balance - %s,
                        updated_at = NOW()
                    WHERE account_id = %s
                    RETURNING current_balance
                """, (amount, amount, str(from_account_id)))
                new_from_balance = cursor.fetchone()['current_balance']
                
                # Credit destination account
                cursor.execute("""
                    UPDATE banking.accounts
                    SET current_balance = current_balance + %s,
                        available_balance = available_balance + %s,
                        updated_at = NOW()
                    WHERE account_id = %s
                    RETURNING current_balance
                """, (amount, amount, str(to_account_id)))
                new_to_balance = cursor.fetchone()['current_balance']
                
                # Step 3: Create transaction records
                cursor.execute("SAVEPOINT transaction_records")
                
                # Debit transaction
                cursor.execute("""
                    INSERT INTO banking.transactions (
                        account_id, transaction_type, amount, currency_code,
                        running_balance, description, reference_number
                    ) VALUES (
                        %s, 'debit', %s, %s, %s, %s, %s
                    ) RETURNING transaction_id
                """, (
                    str(from_account_id), amount, from_account['currency_code'],
                    new_from_balance, f"Transfer to {to_account['account_number']}: {description}",
                    f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                ))
                debit_txn_id = cursor.fetchone()['transaction_id']
                
                # Credit transaction
                cursor.execute("""
                    INSERT INTO banking.transactions (
                        account_id, transaction_type, amount, currency_code,
                        running_balance, description, reference_number
                    ) VALUES (
                        %s, 'credit', %s, %s, %s, %s, %s
                    ) RETURNING transaction_id
                """, (
                    str(to_account_id), amount, to_account['currency_code'],
                    new_to_balance, f"Transfer from {from_account['account_number']}: {description}",
                    f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                ))
                credit_txn_id = cursor.fetchone()['transaction_id']
                
                # Commit all changes
                conn.commit()
                
                return {
                    'success': True,
                    'debit_transaction_id': debit_txn_id,
                    'credit_transaction_id': credit_txn_id,
                    'from_new_balance': new_from_balance,
                    'to_new_balance': new_to_balance
                }
                
            except Exception as e:
                # Rollback to appropriate savepoint or full transaction
                conn.rollback()
                logger.error(f"Transfer failed: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }
            finally:
                cursor.close()
    
    def get_statement(self,
                     account_id: UUID,
                     start_date: date,
                     end_date: date) -> List[Transaction]:
        """Get account statement for a date range."""
        query = """
            SELECT transaction_id, account_id, transaction_type, amount,
                   currency_code, running_balance, description, transaction_date
            FROM banking.transactions
            WHERE account_id = %s
              AND transaction_date >= %s
              AND transaction_date < %s + INTERVAL '1 day'
            ORDER BY transaction_date DESC
        """
        with self.db.get_cursor(commit=False, cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(query, (str(account_id), start_date, end_date))
            return [Transaction(**row) for row in cur.fetchall()]


# =============================================================================
# Async Operations with asyncpg (High Performance)
# =============================================================================

class AsyncDatabaseManager:
    """Async database manager using asyncpg for high-throughput operations."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
    
    async def initialize(self):
        """Initialize async connection pool."""
        self.pool = await asyncpg.create_pool(
            self.config.dsn,
            min_size=self.config.min_connections,
            max_size=self.config.max_connections,
            command_timeout=60
        )
        logger.info("Async connection pool initialized")
    
    async def close(self):
        """Close async connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Async connection pool closed")
    
    async def fetch_many(self, query: str, params: tuple = None) -> List[Dict]:
        """Fetch multiple rows."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *(params or ()))
            return [dict(row) for row in rows]
    
    async def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict]:
        """Fetch single row."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *(params or ()))
            return dict(row) if row else None
    
    async def execute(self, query: str, params: tuple = None) -> str:
        """Execute a command."""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *(params or ()))


class AsyncTransactionProcessor:
    """High-performance async transaction processor."""
    
    def __init__(self, db: AsyncDatabaseManager):
        self.db = db
    
    async def process_batch_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Process a batch of transactions efficiently."""
        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                # Use prepared statements for efficiency
                stmt = await conn.prepare("""
                    INSERT INTO banking.transactions (
                        account_id, transaction_type, amount, currency_code,
                        description, reference_number
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    RETURNING transaction_id
                """)
                
                results = []
                for txn in transactions:
                    txn_id = await stmt.fetchval(
                        txn['account_id'],
                        txn['transaction_type'],
                        txn['amount'],
                        txn['currency_code'],
                        txn.get('description', ''),
                        txn['reference_number']
                    )
                    results.append(txn_id)
                
                return {
                    'processed': len(results),
                    'transaction_ids': results
                }
    
    async def get_daily_summary(self, account_id: UUID, transaction_date: date) -> Dict:
        """Get daily transaction summary."""
        query = """
            SELECT 
                COUNT(*) AS transaction_count,
                SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) AS total_credits,
                SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) AS total_debits,
                MAX(running_balance) AS closing_balance
            FROM banking.transactions
            WHERE account_id = $1
              AND transaction_date::DATE = $2
        """
        return await self.db.fetch_one(query, (account_id, transaction_date))


# =============================================================================
# Usage Example
# =============================================================================

async def main():
    """Example usage of the database modules."""
    
    # Synchronous operations
    print("=== Synchronous Operations ===")
    db = DatabaseManager(DatabaseConfig())
    
    # Customer operations
    customer_repo = CustomerRepository(db)
    customers = customer_repo.search(status='active', limit=5)
    for c in customers:
        print(f"Customer: {c.first_name} {c.last_name} - {c.email}")
    
    # Transaction operations
    txn_repo = TransactionRepository(db)
    # result = txn_repo.execute_transfer(
    #     from_account_id=UUID('...'),
    #     to_account_id=UUID('...'),
    #     amount=Decimal('100.00'),
    #     description='Test transfer'
    # )
    # print(f"Transfer result: {result}")
    
    db.close()
    
    # Async operations
    print("\n=== Async Operations ===")
    async_db = AsyncDatabaseManager(DatabaseConfig())
    await async_db.initialize()
    
    async_processor = AsyncTransactionProcessor(async_db)
    # summary = await async_processor.get_daily_summary(
    #     UUID('...'),
    #     date.today()
    # )
    # print(f"Daily summary: {summary}")
    
    await async_db.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Exercise 9.2: Node.js Application Integration 🟡

### Scenario
Build a Node.js API layer for NeoBank's mobile and web applications using proper connection pooling and query parameterization.

### Solution

```javascript
// neobank-db.js - Node.js Database Module

const { Pool } = require('pg');
const format = require('pg-format');

// =============================================================================
// Configuration
// =============================================================================

const config = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'neobank',
  user: process.env.DB_USER || 'neobank_app',
  password: process.env.DB_PASSWORD || 'secure_password',
  max: 20,                    // Maximum pool size
  min: 5,                     // Minimum pool size
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 2000,
  statement_timeout: 30000,   // Query timeout
};

// =============================================================================
// Database Pool Manager
// =============================================================================

class DatabasePool {
  constructor() {
    this.pool = new Pool(config);
    
    this.pool.on('error', (err, client) => {
      console.error('Unexpected error on idle client', err);
    });
    
    this.pool.on('connect', () => {
      console.log('New client connected to pool');
    });
  }
  
  async query(text, params) {
    const start = Date.now();
    try {
      const result = await this.pool.query(text, params);
      const duration = Date.now() - start;
      console.log('Query executed', { text: text.substring(0, 50), duration, rows: result.rowCount });
      return result;
    } catch (err) {
      console.error('Query error', { text: text.substring(0, 50), error: err.message });
      throw err;
    }
  }
  
  async getClient() {
    const client = await this.pool.connect();
    const query = client.query.bind(client);
    const release = client.release.bind(client);
    
    // Override release to track query time
    client.release = () => {
      client.release = release;
      return release();
    };
    
    return client;
  }
  
  async transaction(callback) {
    const client = await this.getClient();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    } finally {
      client.release();
    }
  }
  
  async close() {
    await this.pool.end();
    console.log('Pool closed');
  }
}

const db = new DatabasePool();

// =============================================================================
// Customer Repository
// =============================================================================

class CustomerRepository {
  
  async findById(customerId) {
    const query = `
      SELECT customer_id, customer_number, first_name, last_name,
             email, phone_primary, customer_type, customer_status,
             kyc_status, created_at
      FROM banking.customers
      WHERE customer_id = $1
    `;
    const result = await db.query(query, [customerId]);
    return result.rows[0] || null;
  }
  
  async findByEmail(email) {
    const query = `
      SELECT customer_id, customer_number, first_name, last_name,
             email, phone_primary, customer_type, customer_status
      FROM banking.customers
      WHERE email = $1
    `;
    const result = await db.query(query, [email.toLowerCase()]);
    return result.rows[0] || null;
  }
  
  async search({ email, phone, status, customerType, limit = 50, offset = 0 }) {
    const conditions = [];
    const params = [];
    let paramIndex = 1;
    
    if (email) {
      conditions.push(`email ILIKE $${paramIndex++}`);
      params.push(`%${email}%`);
    }
    if (phone) {
      conditions.push(`phone_primary LIKE $${paramIndex++}`);
      params.push(`%${phone}%`);
    }
    if (status) {
      conditions.push(`customer_status = $${paramIndex++}`);
      params.push(status);
    }
    if (customerType) {
      conditions.push(`customer_type = $${paramIndex++}`);
      params.push(customerType);
    }
    
    const whereClause = conditions.length > 0 
      ? `WHERE ${conditions.join(' AND ')}` 
      : '';
    
    const query = `
      SELECT customer_id, customer_number, first_name, last_name,
             email, phone_primary, customer_type, customer_status, created_at
      FROM banking.customers
      ${whereClause}
      ORDER BY created_at DESC
      LIMIT $${paramIndex++} OFFSET $${paramIndex}
    `;
    params.push(limit, offset);
    
    const result = await db.query(query, params);
    return result.rows;
  }
  
  async create(customerData) {
    const query = `
      INSERT INTO banking.customers (
        first_name, last_name, email, phone_primary,
        date_of_birth, customer_type
      ) VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING customer_id, customer_number
    `;
    const params = [
      customerData.firstName,
      customerData.lastName,
      customerData.email.toLowerCase(),
      customerData.phone,
      customerData.dateOfBirth,
      customerData.customerType || 'individual'
    ];
    
    const result = await db.query(query, params);
    return result.rows[0];
  }
  
  async update(customerId, updates) {
    const allowedFields = ['first_name', 'last_name', 'email', 'phone_primary', 
                          'phone_secondary', 'customer_status'];
    
    const setClauses = [];
    const params = [];
    let paramIndex = 1;
    
    for (const [key, value] of Object.entries(updates)) {
      // Convert camelCase to snake_case
      const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
      if (allowedFields.includes(snakeKey)) {
        setClauses.push(`${snakeKey} = $${paramIndex++}`);
        params.push(value);
      }
    }
    
    if (setClauses.length === 0) {
      throw new Error('No valid fields to update');
    }
    
    params.push(customerId);
    
    const query = `
      UPDATE banking.customers
      SET ${setClauses.join(', ')}, updated_at = NOW()
      WHERE customer_id = $${paramIndex}
      RETURNING customer_id
    `;
    
    const result = await db.query(query, params);
    return result.rowCount > 0;
  }
}

// =============================================================================
// Transaction Repository
// =============================================================================

class TransactionRepository {
  
  async executeTransfer({ fromAccountId, toAccountId, amount, description = 'Transfer' }) {
    return db.transaction(async (client) => {
      // Lock accounts in consistent order
      const accountIds = [fromAccountId, toAccountId].sort();
      
      const lockResult = await client.query(`
        SELECT account_id, account_number, current_balance, available_balance,
               account_status, currency_code
        FROM banking.accounts
        WHERE account_id = ANY($1)
        ORDER BY account_id
        FOR UPDATE
      `, [accountIds]);
      
      const accounts = new Map(lockResult.rows.map(a => [a.account_id, a]));
      const fromAccount = accounts.get(fromAccountId);
      const toAccount = accounts.get(toAccountId);
      
      // Validations
      if (!fromAccount || !toAccount) {
        throw new Error('Account not found');
      }
      if (fromAccount.account_status !== 'active' || toAccount.account_status !== 'active') {
        throw new Error('Account not active');
      }
      if (parseFloat(fromAccount.available_balance) < parseFloat(amount)) {
        throw new Error('Insufficient funds');
      }
      if (fromAccount.currency_code !== toAccount.currency_code) {
        throw new Error('Currency mismatch');
      }
      
      // Debit source
      const debitResult = await client.query(`
        UPDATE banking.accounts
        SET current_balance = current_balance - $1,
            available_balance = available_balance - $1,
            updated_at = NOW()
        WHERE account_id = $2
        RETURNING current_balance
      `, [amount, fromAccountId]);
      
      // Credit destination
      const creditResult = await client.query(`
        UPDATE banking.accounts
        SET current_balance = current_balance + $1,
            available_balance = available_balance + $1,
            updated_at = NOW()
        WHERE account_id = $2
        RETURNING current_balance
      `, [amount, toAccountId]);
      
      const referenceNumber = `TRF-${Date.now()}`;
      
      // Create transaction records
      const debitTxn = await client.query(`
        INSERT INTO banking.transactions (
          account_id, transaction_type, amount, currency_code,
          running_balance, description, reference_number
        ) VALUES ($1, 'debit', $2, $3, $4, $5, $6)
        RETURNING transaction_id
      `, [
        fromAccountId, amount, fromAccount.currency_code,
        debitResult.rows[0].current_balance,
        `Transfer to ${toAccount.account_number}: ${description}`,
        referenceNumber
      ]);
      
      const creditTxn = await client.query(`
        INSERT INTO banking.transactions (
          account_id, transaction_type, amount, currency_code,
          running_balance, description, reference_number
        ) VALUES ($1, 'credit', $2, $3, $4, $5, $6)
        RETURNING transaction_id
      `, [
        toAccountId, amount, toAccount.currency_code,
        creditResult.rows[0].current_balance,
        `Transfer from ${fromAccount.account_number}: ${description}`,
        referenceNumber
      ]);
      
      return {
        success: true,
        referenceNumber,
        debitTransactionId: debitTxn.rows[0].transaction_id,
        creditTransactionId: creditTxn.rows[0].transaction_id
      };
    });
  }
  
  async getStatement(accountId, startDate, endDate, { limit = 100, offset = 0 } = {}) {
    const query = `
      SELECT transaction_id, transaction_type, amount, currency_code,
             running_balance, description, reference_number, 
             transaction_date, created_at
      FROM banking.transactions
      WHERE account_id = $1
        AND transaction_date >= $2
        AND transaction_date < $3::DATE + INTERVAL '1 day'
      ORDER BY transaction_date DESC
      LIMIT $4 OFFSET $5
    `;
    
    const result = await db.query(query, [accountId, startDate, endDate, limit, offset]);
    return result.rows;
  }
  
  async getDailySummary(accountId, date) {
    const query = `
      SELECT 
        COUNT(*) AS transaction_count,
        SUM(CASE WHEN transaction_type = 'credit' THEN amount ELSE 0 END) AS total_credits,
        SUM(CASE WHEN transaction_type = 'debit' THEN amount ELSE 0 END) AS total_debits,
        (SELECT running_balance FROM banking.transactions 
         WHERE account_id = $1 AND transaction_date::DATE = $2
         ORDER BY transaction_date DESC LIMIT 1) AS closing_balance
      FROM banking.transactions
      WHERE account_id = $1
        AND transaction_date::DATE = $2
    `;
    
    const result = await db.query(query, [accountId, date]);
    return result.rows[0];
  }
}

// =============================================================================
// Bulk Operations
// =============================================================================

class BulkOperations {
  
  async insertTransactionsBatch(transactions) {
    // Use pg-format for safe bulk inserts
    const values = transactions.map(t => [
      t.accountId,
      t.transactionType,
      t.amount,
      t.currencyCode,
      t.description || '',
      t.referenceNumber
    ]);
    
    const query = format(`
      INSERT INTO banking.transactions (
        account_id, transaction_type, amount, currency_code,
        description, reference_number
      ) VALUES %L
      RETURNING transaction_id
    `, values);
    
    const result = await db.query(query);
    return result.rows.map(r => r.transaction_id);
  }
  
  async upsertCustomerPreferences(preferences) {
    // Batch upsert using unnest
    const customerIds = preferences.map(p => p.customerId);
    const prefData = preferences.map(p => JSON.stringify(p.preferences));
    
    const query = `
      INSERT INTO banking.customer_preferences (customer_id, preferences)
      SELECT unnest($1::UUID[]), unnest($2::JSONB[])
      ON CONFLICT (customer_id) DO UPDATE
      SET preferences = banking.customer_preferences.preferences || EXCLUDED.preferences,
          updated_at = NOW()
      RETURNING customer_id
    `;
    
    const result = await db.query(query, [customerIds, prefData]);
    return result.rowCount;
  }
}

// =============================================================================
// Exports
// =============================================================================

module.exports = {
  db,
  CustomerRepository,
  TransactionRepository,
  BulkOperations
};

// Usage Example
async function example() {
  const customerRepo = new CustomerRepository();
  const txnRepo = new TransactionRepository();
  
  // Find customers
  const customers = await customerRepo.search({ status: 'active', limit: 10 });
  console.log('Active customers:', customers.length);
  
  // Get statement
  // const statement = await txnRepo.getStatement(
  //   'account-uuid',
  //   '2024-01-01',
  //   '2024-01-31'
  // );
  
  await db.close();
}

// example().catch(console.error);
```

---

## Exercise 9.3: Connection Pooling with PgBouncer 🔴

### Scenario
Configure and optimize connection pooling for NeoBank's high-traffic production environment.

### Solution

```sql
-- Step 1: Create monitoring views for connection pool analysis
CREATE SCHEMA IF NOT EXISTS pooling;

-- Analyze connection usage patterns
CREATE OR REPLACE VIEW pooling.v_connection_analysis AS
WITH connection_stats AS (
    SELECT 
        usename,
        client_addr,
        application_name,
        state,
        EXTRACT(EPOCH FROM (NOW() - state_change)) AS seconds_in_state,
        EXTRACT(EPOCH FROM (NOW() - backend_start)) AS connection_age_seconds,
        wait_event_type,
        wait_event
    FROM pg_stat_activity
    WHERE backend_type = 'client backend'
)
SELECT 
    usename AS username,
    COUNT(*) AS total_connections,
    COUNT(*) FILTER (WHERE state = 'active') AS active,
    COUNT(*) FILTER (WHERE state = 'idle') AS idle,
    COUNT(*) FILTER (WHERE state = 'idle in transaction') AS idle_in_transaction,
    COUNT(*) FILTER (WHERE state = 'idle in transaction (aborted)') AS aborted,
    ROUND(AVG(connection_age_seconds)::NUMERIC, 2) AS avg_connection_age_seconds,
    MAX(seconds_in_state) AS max_seconds_in_current_state
FROM connection_stats
GROUP BY usename
ORDER BY total_connections DESC;

-- Detect long-running idle connections
CREATE OR REPLACE VIEW pooling.v_idle_connections AS
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    state_change,
    EXTRACT(EPOCH FROM (NOW() - state_change)) AS idle_seconds,
    query
FROM pg_stat_activity
WHERE state LIKE 'idle%'
  AND EXTRACT(EPOCH FROM (NOW() - state_change)) > 300  -- Idle > 5 minutes
ORDER BY idle_seconds DESC;

-- Step 2: PgBouncer configuration generator
CREATE OR REPLACE FUNCTION pooling.generate_pgbouncer_config()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_config TEXT;
BEGIN
    v_config := E'; PgBouncer Configuration for NeoBank\n';
    v_config := v_config || E'; Generated: ' || NOW()::TEXT || E'\n\n';
    
    v_config := v_config || E'[databases]\n';
    v_config := v_config || E'neobank = host=localhost port=5432 dbname=neobank\n';
    v_config := v_config || E'neobank_readonly = host=replica.neobank.local port=5432 dbname=neobank\n\n';
    
    v_config := v_config || E'[pgbouncer]\n';
    v_config := v_config || E'listen_addr = *\n';
    v_config := v_config || E'listen_port = 6432\n\n';
    
    v_config := v_config || E'; Authentication\n';
    v_config := v_config || E'auth_type = scram-sha-256\n';
    v_config := v_config || E'auth_file = /etc/pgbouncer/userlist.txt\n\n';
    
    v_config := v_config || E'; Pool Configuration\n';
    v_config := v_config || E'pool_mode = transaction\n';
    v_config := v_config || E'max_client_conn = 1000\n';
    v_config := v_config || E'default_pool_size = 20\n';
    v_config := v_config || E'min_pool_size = 5\n';
    v_config := v_config || E'reserve_pool_size = 5\n';
    v_config := v_config || E'reserve_pool_timeout = 3\n\n';
    
    v_config := v_config || E'; Connection Settings\n';
    v_config := v_config || E'server_lifetime = 3600\n';
    v_config := v_config || E'server_idle_timeout = 600\n';
    v_config := v_config || E'client_idle_timeout = 300\n';
    v_config := v_config || E'query_timeout = 30\n\n';
    
    v_config := v_config || E'; Logging\n';
    v_config := v_config || E'log_connections = 1\n';
    v_config := v_config || E'log_disconnections = 1\n';
    v_config := v_config || E'log_pooler_errors = 1\n';
    v_config := v_config || E'stats_period = 60\n\n';
    
    v_config := v_config || E'; Admin\n';
    v_config := v_config || E'admin_users = pgbouncer_admin\n';
    v_config := v_config || E'stats_users = pgbouncer_stats\n';
    
    RETURN v_config;
END;
$$;

SELECT pooling.generate_pgbouncer_config();

-- Step 3: Connection pool sizing calculator
CREATE OR REPLACE FUNCTION pooling.calculate_pool_size(
    p_max_db_connections INTEGER,  -- PostgreSQL max_connections
    p_avg_query_time_ms NUMERIC,   -- Average query execution time
    p_target_tps INTEGER,          -- Target transactions per second
    p_safety_margin NUMERIC DEFAULT 0.8  -- Use 80% of available connections
)
RETURNS TABLE (
    metric TEXT,
    value TEXT,
    explanation TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_effective_connections INTEGER;
    v_connections_per_tps NUMERIC;
    v_recommended_pool_size INTEGER;
BEGIN
    v_effective_connections := FLOOR(p_max_db_connections * p_safety_margin);
    v_connections_per_tps := p_avg_query_time_ms / 1000.0;  -- Connections needed per TPS
    v_recommended_pool_size := CEIL(p_target_tps * v_connections_per_tps);
    
    RETURN QUERY VALUES
        ('Max DB Connections', p_max_db_connections::TEXT, 
         'PostgreSQL max_connections setting'),
        ('Effective Connections', v_effective_connections::TEXT,
         'Available after safety margin'),
        ('Avg Query Time', p_avg_query_time_ms || ' ms',
         'Average transaction duration'),
        ('Target TPS', p_target_tps::TEXT,
         'Desired transactions per second'),
        ('Connections per TPS', ROUND(v_connections_per_tps, 3)::TEXT,
         'Connections needed to sustain 1 TPS'),
        ('Recommended Pool Size', v_recommended_pool_size::TEXT,
         'Minimum pool connections needed'),
        ('Can Support TPS', FLOOR(v_effective_connections / v_connections_per_tps)::TEXT,
         'Maximum TPS with current settings'),
        ('Bottleneck', 
         CASE 
             WHEN v_recommended_pool_size > v_effective_connections 
             THEN 'DATABASE - Need more connections or faster queries'
             ELSE 'NONE - Configuration sufficient'
         END,
         'Identified limitation');
END;
$$;

-- Example calculation
SELECT * FROM pooling.calculate_pool_size(
    200,   -- max_connections
    50,    -- avg 50ms query time
    2000   -- target 2000 TPS
);

-- Step 4: Monitor pool effectiveness (simulated PgBouncer stats)
CREATE TABLE IF NOT EXISTS pooling.pool_stats (
    stat_id BIGSERIAL PRIMARY KEY,
    pool_name VARCHAR(100),
    client_connections INTEGER,
    server_connections INTEGER,
    server_active INTEGER,
    server_idle INTEGER,
    max_wait_ms INTEGER,
    avg_query_time_ms NUMERIC,
    total_requests BIGINT,
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 5: Pool health check function
CREATE OR REPLACE FUNCTION pooling.check_pool_health()
RETURNS TABLE (
    check_name TEXT,
    status TEXT,
    current_value TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Connection utilization
    RETURN QUERY
    SELECT 
        'Connection Utilization'::TEXT,
        CASE 
            WHEN COUNT(*)::FLOAT / current_setting('max_connections')::FLOAT < 0.7 THEN '✅ OK'
            WHEN COUNT(*)::FLOAT / current_setting('max_connections')::FLOAT < 0.9 THEN '⚠️ WARNING'
            ELSE '🔴 CRITICAL'
        END,
        COUNT(*) || ' / ' || current_setting('max_connections'),
        CASE 
            WHEN COUNT(*)::FLOAT / current_setting('max_connections')::FLOAT >= 0.7 
            THEN 'Consider connection pooling or increasing max_connections'
            ELSE 'Healthy'
        END
    FROM pg_stat_activity
    WHERE backend_type = 'client backend';
    
    -- Idle in transaction
    RETURN QUERY
    SELECT 
        'Idle in Transaction',
        CASE 
            WHEN COUNT(*) = 0 THEN '✅ OK'
            WHEN COUNT(*) < 5 THEN '⚠️ WARNING'
            ELSE '🔴 CRITICAL'
        END,
        COUNT(*)::TEXT,
        'Long idle-in-transaction blocks other operations'
    FROM pg_stat_activity
    WHERE state = 'idle in transaction'
      AND NOW() - state_change > INTERVAL '1 minute';
    
    -- Connection age
    RETURN QUERY
    SELECT 
        'Avg Connection Age',
        CASE 
            WHEN AVG(EXTRACT(EPOCH FROM (NOW() - backend_start))) < 3600 THEN '✅ OK'
            ELSE '⚠️ REVIEW'
        END,
        ROUND(AVG(EXTRACT(EPOCH FROM (NOW() - backend_start))) / 60, 1)::TEXT || ' minutes',
        'Long-lived connections may indicate missing pooling'
    FROM pg_stat_activity
    WHERE backend_type = 'client backend';
END;
$$;

SELECT * FROM pooling.check_pool_health();
```

---

## Exercise 9.4: Concurrency Control and MVCC 🔴

### Scenario
Understand and manage concurrency issues in NeoBank's high-volume transaction processing system.

### Solution

```sql
-- Step 1: Create concurrency demonstration schema
CREATE SCHEMA IF NOT EXISTS concurrency;

-- Step 2: MVCC visibility demonstration
CREATE TABLE IF NOT EXISTS concurrency.mvcc_demo (
    id SERIAL PRIMARY KEY,
    value TEXT,
    version INTEGER DEFAULT 1
);

-- Function to show transaction visibility
CREATE OR REPLACE FUNCTION concurrency.show_mvcc_info(p_table_name TEXT)
RETURNS TABLE (
    ctid TID,
    xmin XID,
    xmax XID,
    xmin_committed BOOLEAN,
    xmax_committed BOOLEAN,
    current_snapshot TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
            ctid,
            xmin,
            xmax,
            xmin::TEXT::BIGINT < txid_current()::BIGINT AS xmin_committed,
            xmax = 0 OR xmax::TEXT::BIGINT > txid_current()::BIGINT AS xmax_valid,
            txid_current_snapshot()::TEXT
         FROM %I',
        p_table_name
    );
END;
$$;

-- Step 3: Lock monitoring and analysis
CREATE OR REPLACE VIEW concurrency.v_lock_analysis AS
SELECT 
    blocked.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocked_activity.application_name AS blocked_app,
    blocked_activity.query AS blocked_query,
    blocked.mode AS blocked_mode,
    blocking.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocking_activity.application_name AS blocking_app,
    blocking_activity.query AS blocking_query,
    blocking.mode AS blocking_mode,
    NOW() - blocked_activity.state_change AS blocked_duration
FROM pg_locks blocked
JOIN pg_stat_activity blocked_activity ON blocked.pid = blocked_activity.pid
JOIN pg_locks blocking ON blocked.locktype = blocking.locktype
    AND blocked.relation = blocking.relation
    AND blocked.pid != blocking.pid
JOIN pg_stat_activity blocking_activity ON blocking.pid = blocking_activity.pid
WHERE NOT blocked.granted
ORDER BY blocked_duration DESC;

-- Step 4: Deadlock detection helper
CREATE TABLE IF NOT EXISTS concurrency.deadlock_log (
    log_id BIGSERIAL PRIMARY KEY,
    deadlock_time TIMESTAMPTZ DEFAULT NOW(),
    process_id INTEGER,
    transaction_id XID,
    query_text TEXT,
    lock_info JSONB,
    resolution TEXT
);

-- Function to log potential deadlock conditions
CREATE OR REPLACE FUNCTION concurrency.detect_deadlock_risk()
RETURNS TABLE (
    session1_pid INTEGER,
    session1_locks TEXT,
    session2_pid INTEGER,
    session2_locks TEXT,
    risk_level TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Find sessions that hold locks and wait for locks
    RETURN QUERY
    WITH lock_holders AS (
        SELECT 
            l.pid,
            l.relation::REGCLASS::TEXT AS table_name,
            l.mode,
            l.granted,
            a.query
        FROM pg_locks l
        JOIN pg_stat_activity a ON l.pid = a.pid
        WHERE l.relation IS NOT NULL
    ),
    waiting_sessions AS (
        SELECT 
            pid,
            STRING_AGG(DISTINCT table_name || ' (' || mode || ')', ', ') AS waiting_for
        FROM lock_holders
        WHERE NOT granted
        GROUP BY pid
    ),
    holding_sessions AS (
        SELECT 
            pid,
            STRING_AGG(DISTINCT table_name || ' (' || mode || ')', ', ') AS holding
        FROM lock_holders
        WHERE granted
        GROUP BY pid
    )
    SELECT 
        w.pid,
        COALESCE(h1.holding, 'none'),
        l.pid,
        COALESCE(h2.holding, 'none'),
        CASE 
            WHEN h1.holding IS NOT NULL AND h2.holding IS NOT NULL 
            THEN 'HIGH - Both sessions hold locks'
            ELSE 'MEDIUM'
        END
    FROM waiting_sessions w
    JOIN lock_holders l ON w.waiting_for LIKE '%' || l.table_name || '%'
    LEFT JOIN holding_sessions h1 ON w.pid = h1.pid
    LEFT JOIN holding_sessions h2 ON l.pid = h2.pid
    WHERE w.pid != l.pid
      AND l.granted;
END;
$$;

-- Step 5: Optimistic locking implementation
ALTER TABLE banking.accounts ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;

CREATE OR REPLACE FUNCTION banking.update_account_optimistic(
    p_account_id UUID,
    p_new_balance NUMERIC,
    p_expected_version INTEGER
)
RETURNS TABLE (
    success BOOLEAN,
    new_version INTEGER,
    error_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_version INTEGER;
BEGIN
    -- Try to update with version check
    UPDATE banking.accounts
    SET current_balance = p_new_balance,
        version = version + 1,
        updated_at = NOW()
    WHERE account_id = p_account_id
      AND version = p_expected_version
    RETURNING version INTO v_current_version;
    
    IF FOUND THEN
        RETURN QUERY SELECT TRUE, v_current_version, NULL::TEXT;
    ELSE
        -- Check if record exists
        SELECT version INTO v_current_version
        FROM banking.accounts
        WHERE account_id = p_account_id;
        
        IF NOT FOUND THEN
            RETURN QUERY SELECT FALSE, NULL::INTEGER, 'Account not found'::TEXT;
        ELSE
            RETURN QUERY SELECT FALSE, v_current_version, 
                'Version mismatch - expected ' || p_expected_version || 
                ' but found ' || v_current_version;
        END IF;
    END IF;
END;
$$;

-- Step 6: Advisory locks for application-level locking
CREATE OR REPLACE FUNCTION concurrency.acquire_customer_lock(
    p_customer_id UUID,
    p_timeout_ms INTEGER DEFAULT 5000
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_lock_id BIGINT;
BEGIN
    -- Convert UUID to bigint for advisory lock
    v_lock_id := ('x' || SUBSTRING(p_customer_id::TEXT, 1, 16))::BIT(64)::BIGINT;
    
    -- Try to acquire lock with timeout
    PERFORM set_config('lock_timeout', p_timeout_ms || 'ms', TRUE);
    
    BEGIN
        IF pg_try_advisory_lock(v_lock_id) THEN
            RETURN TRUE;
        ELSE
            RETURN FALSE;
        END IF;
    EXCEPTION
        WHEN lock_not_available THEN
            RETURN FALSE;
    END;
END;
$$;

CREATE OR REPLACE FUNCTION concurrency.release_customer_lock(p_customer_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_lock_id BIGINT;
BEGIN
    v_lock_id := ('x' || SUBSTRING(p_customer_id::TEXT, 1, 16))::BIT(64)::BIGINT;
    RETURN pg_advisory_unlock(v_lock_id);
END;
$$;

-- Step 7: Transaction isolation level comparison
CREATE OR REPLACE FUNCTION concurrency.demonstrate_isolation_levels()
RETURNS TABLE (
    isolation_level TEXT,
    phenomenon TEXT,
    allowed BOOLEAN,
    example TEXT
)
LANGUAGE SQL
AS $$
    SELECT * FROM (VALUES
        ('READ UNCOMMITTED', 'Dirty Read', TRUE, 
         'Can see uncommitted changes from other transactions'),
        ('READ UNCOMMITTED', 'Non-repeatable Read', TRUE,
         'Same query can return different results in same transaction'),
        ('READ UNCOMMITTED', 'Phantom Read', TRUE,
         'New rows can appear in repeated queries'),
        
        ('READ COMMITTED', 'Dirty Read', FALSE,
         'Only sees committed data'),
        ('READ COMMITTED', 'Non-repeatable Read', TRUE,
         'Sees commits from other transactions'),
        ('READ COMMITTED', 'Phantom Read', TRUE,
         'New committed rows visible'),
        
        ('REPEATABLE READ', 'Dirty Read', FALSE,
         'Only committed data visible'),
        ('REPEATABLE READ', 'Non-repeatable Read', FALSE,
         'Snapshot taken at first query'),
        ('REPEATABLE READ', 'Phantom Read', FALSE,
         'PostgreSQL prevents phantoms too'),
        
        ('SERIALIZABLE', 'Dirty Read', FALSE,
         'Strictest isolation'),
        ('SERIALIZABLE', 'Non-repeatable Read', FALSE,
         'Complete isolation'),
        ('SERIALIZABLE', 'Phantom Read', FALSE,
         'Detects serialization anomalies')
    ) AS t(isolation_level, phenomenon, allowed, example);
$$;

SELECT * FROM concurrency.demonstrate_isolation_levels();

-- Step 8: MVCC bloat monitoring
CREATE OR REPLACE VIEW concurrency.v_table_bloat AS
SELECT 
    schemaname || '.' || relname AS table_name,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_ratio,
    last_vacuum,
    last_autovacuum,
    CASE 
        WHEN n_dead_tup > n_live_tup * 0.2 THEN '🔴 VACUUM NEEDED'
        WHEN n_dead_tup > n_live_tup * 0.1 THEN '🟡 MONITOR'
        ELSE '🟢 OK'
    END AS status
FROM pg_stat_user_tables
WHERE schemaname IN ('banking', 'lending', 'analytics')
ORDER BY dead_tuple_ratio DESC NULLS LAST;
```

---

## 🎯 Practice Challenges

### Challenge 9.1 🟡
Implement a retry mechanism in Python/Node.js that handles serialization failures gracefully.

### Challenge 9.2 🔴
Create a distributed lock manager using advisory locks with automatic timeout and deadlock prevention.

### Challenge 9.3 ⚫
Build a connection pool monitor that tracks connection lifecycle, query patterns, and automatically adjusts pool size based on load.

---

**Next: [Part 10 - Advanced Administration Exercises](10-advanced-administration-exercises.md)**
