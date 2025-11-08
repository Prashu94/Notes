# PostgreSQL and Node.js

## Overview

Node.js is widely used for building scalable server-side applications with PostgreSQL. This comprehensive guide covers database connectivity, connection pooling, ORMs (Prisma, Sequelize, TypeORM), query builders, transactions, migrations, and best practices for Node.js-PostgreSQL integration.

## Table of Contents

- [Node.js PostgreSQL Drivers](#nodejs-postgresql-drivers)
- [pg (node-postgres) Basics](#pg-node-postgres-basics)
- [Connection Pooling](#connection-pooling)
- [Query Builders](#query-builders)
- [ORMs](#orms)
- [Transactions](#transactions)
- [Migrations](#migrations)
- [TypeScript Integration](#typescript-integration)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Node.js PostgreSQL Drivers

### Available Drivers

```javascript
// PostgreSQL drivers for Node.js:

// 1. pg (node-postgres) - Most popular
// - Pure JavaScript and native bindings available
// - Full PostgreSQL support
// - Connection pooling built-in
const { Pool, Client } = require('pg');

// 2. pg-promise - Promise-based wrapper
// - Built on top of pg
// - Better promise support
// - Automatic connection management
const pgp = require('pg-promise')();

// 3. postgres - Modern, lightweight
// - Fast and minimal
// - Template tag syntax
// - No external dependencies
const postgres = require('postgres');

// Installing drivers:
// npm install pg
// npm install pg-promise
// npm install postgres

// TypeScript types:
// npm install --save-dev @types/pg
```

## pg (node-postgres) Basics

### Connecting to Database

```javascript
const { Client, Pool } = require('pg');

// Using Client (single connection)
const client = new Client({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'password',
});

// Connect
client.connect()
  .then(() => console.log('Connected'))
  .catch(err => console.error('Connection error', err));

// Using connection string
const client2 = new Client({
  connectionString: 'postgresql://user:password@localhost:5432/mydb',
  ssl: {
    rejectUnauthorized: false // For development only
  }
});

// Using environment variables
const client3 = new Client({
  host: process.env.PGHOST || 'localhost',
  port: process.env.PGPORT || 5432,
  database: process.env.PGDATABASE || 'mydb',
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD,
});

// Async/await connection
async function connectDatabase() {
  try {
    await client.connect();
    console.log('Connected to PostgreSQL');
  } catch (err) {
    console.error('Connection error', err);
  }
}

connectDatabase();

// Close connection
client.end()
  .then(() => console.log('Connection closed'))
  .catch(err => console.error('Error closing connection', err));
```

### Executing Queries

```javascript
const { Client } = require('pg');

const client = new Client({
  connectionString: 'postgresql://user:password@localhost:5432/mydb'
});

async function runQueries() {
  await client.connect();
  
  try {
    // Simple query
    const res = await client.query('SELECT NOW()');
    console.log(res.rows[0]);
    
    // Query with parameters (prevents SQL injection)
    const userId = 1;
    const userRes = await client.query(
      'SELECT * FROM users WHERE id = $1',
      [userId]
    );
    console.log(userRes.rows[0]);
    
    // Insert with RETURNING
    const insertRes = await client.query(
      'INSERT INTO users (username, email) VALUES ($1, $2) RETURNING *',
      ['alice', 'alice@example.com']
    );
    console.log('Inserted user:', insertRes.rows[0]);
    
    // Update
    const updateRes = await client.query(
      'UPDATE users SET email = $1 WHERE username = $2 RETURNING *',
      ['newemail@example.com', 'alice']
    );
    console.log(`Updated ${updateRes.rowCount} rows`);
    
    // Delete
    const deleteRes = await client.query(
      'DELETE FROM users WHERE id = $1',
      [1]
    );
    console.log(`Deleted ${deleteRes.rowCount} rows`);
    
    // Query with named parameters (using object)
    const { rows } = await client.query({
      text: 'SELECT * FROM users WHERE username = $1 AND email = $2',
      values: ['alice', 'alice@example.com']
    });
    console.log(rows);
    
  } catch (err) {
    console.error('Query error', err);
  } finally {
    await client.end();
  }
}

runQueries();

// Callback style (legacy)
client.query('SELECT * FROM users', (err, res) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log(res.rows);
  client.end();
});
```

### Prepared Statements

```javascript
const { Client } = require('pg');

const client = new Client({
  connectionString: 'postgresql://user:password@localhost:5432/mydb'
});

async function preparedStatements() {
  await client.connect();
  
  try {
    // Prepared statement (automatically cached by pg)
    const queryConfig = {
      text: 'SELECT * FROM users WHERE id = $1',
      values: [1]
    };
    
    // First execution: prepares statement
    const res1 = await client.query(queryConfig);
    console.log(res1.rows);
    
    // Subsequent executions: uses prepared statement
    queryConfig.values = [2];
    const res2 = await client.query(queryConfig);
    console.log(res2.rows);
    
    // Explicit prepared statement
    const preparedQuery = {
      name: 'fetch-user',
      text: 'SELECT * FROM users WHERE id = $1',
      values: [1]
    };
    
    const res3 = await client.query(preparedQuery);
    console.log(res3.rows);
    
  } catch (err) {
    console.error('Error', err);
  } finally {
    await client.end();
  }
}

preparedStatements();
```

## Connection Pooling

### Using Pool

```javascript
const { Pool } = require('pg');

// Create connection pool
const pool = new Pool({
  host: 'localhost',
  port: 5432,
  database: 'mydb',
  user: 'postgres',
  password: 'password',
  max: 20, // Maximum pool size
  idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
  connectionTimeoutMillis: 2000, // Return error after 2 seconds if no connection available
});

// Query using pool (automatically manages connections)
async function queryWithPool() {
  try {
    const res = await pool.query('SELECT * FROM users WHERE id = $1', [1]);
    console.log(res.rows[0]);
  } catch (err) {
    console.error('Query error', err);
  }
}

queryWithPool();

// Acquire client from pool for multiple queries
async function multipleQueries() {
  const client = await pool.connect();
  
  try {
    const res1 = await client.query('SELECT * FROM users');
    console.log(res1.rows);
    
    const res2 = await client.query('SELECT * FROM orders');
    console.log(res2.rows);
  } catch (err) {
    console.error('Error', err);
  } finally {
    // Release client back to pool
    client.release();
  }
}

multipleQueries();

// Pool events
pool.on('connect', (client) => {
  console.log('New client connected to pool');
});

pool.on('acquire', (client) => {
  console.log('Client acquired from pool');
});

pool.on('error', (err, client) => {
  console.error('Unexpected error on idle client', err);
});

pool.on('remove', (client) => {
  console.log('Client removed from pool');
});

// Graceful shutdown
async function shutdown() {
  await pool.end();
  console.log('Pool has ended');
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Pool helper function
function query(text, params) {
  return pool.query(text, params);
}

// Usage
async function example() {
  const { rows } = await query('SELECT * FROM users WHERE id = $1', [1]);
  console.log(rows[0]);
}

example();
```

### Pool Configuration

```javascript
const { Pool } = require('pg');

// Production configuration
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? {
    rejectUnauthorized: false
  } : false,
  max: 20, // Max pool size
  min: 5, // Min pool size
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  application_name: 'my-node-app',
  statement_timeout: 30000, // 30 second query timeout
  query_timeout: 30000,
});

// Environment-based configuration
const isDevelopment = process.env.NODE_ENV === 'development';
const pool2 = new Pool({
  host: process.env.PGHOST,
  port: process.env.PGPORT,
  database: process.env.PGDATABASE,
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  max: isDevelopment ? 5 : 20,
  idleTimeoutMillis: isDevelopment ? 10000 : 30000,
});

// Monitor pool metrics
function logPoolStats() {
  console.log('Pool stats:', {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount,
  });
}

setInterval(logPoolStats, 60000); // Log every minute
```

## Query Builders

### Slonik

```javascript
const { createPool } = require('slonik');

const pool = createPool('postgresql://user:password@localhost/mydb', {
  maximumPoolSize: 10,
});

// Basic query
const result = await pool.query(sql`
  SELECT * FROM users WHERE id = ${userId}
`);

console.log(result.rows);

// Insert
const newUser = await pool.one(sql`
  INSERT INTO users (username, email)
  VALUES (${username}, ${email})
  RETURNING *
`);

// Update
const updatedUser = await pool.one(sql`
  UPDATE users
  SET email = ${newEmail}
  WHERE id = ${userId}
  RETURNING *
`);

// Transactions
await pool.transaction(async (connection) => {
  await connection.query(sql`
    INSERT INTO accounts (user_id, balance) VALUES (${userId}, ${1000})
  `);
  
  await connection.query(sql`
    INSERT INTO audit_log (action) VALUES (${'account_created'})
  `);
});

// Type safety with TypeScript
interface User {
  id: number;
  username: string;
  email: string;
}

const user = await pool.one<User>(sql`
  SELECT id, username, email FROM users WHERE id = ${1}
`);

console.log(user.username); // Type-safe!
```

### Knex.js

```javascript
const knex = require('knex')({
  client: 'postgresql',
  connection: {
    host: 'localhost',
    port: 5432,
    user: 'postgres',
    password: 'password',
    database: 'mydb',
  },
  pool: {
    min: 2,
    max: 10
  }
});

// Select
const users = await knex('users')
  .select('*')
  .where('id', 1);

console.log(users);

// Select with conditions
const activeUsers = await knex('users')
  .select('id', 'username', 'email')
  .where('active', true)
  .andWhere('created_at', '>', '2024-01-01')
  .orderBy('created_at', 'desc')
  .limit(10);

// Insert
const [newUser] = await knex('users')
  .insert({
    username: 'alice',
    email: 'alice@example.com'
  })
  .returning('*');

console.log('Created user:', newUser);

// Update
const updatedCount = await knex('users')
  .where('id', 1)
  .update({
    email: 'newemail@example.com'
  });

// Delete
const deletedCount = await knex('users')
  .where('id', 1)
  .delete();

// Join
const ordersWithUsers = await knex('orders')
  .join('users', 'orders.user_id', 'users.id')
  .select('orders.*', 'users.username');

// Transaction
await knex.transaction(async (trx) => {
  await trx('accounts')
    .where('id', 1)
    .decrement('balance', 100);
  
  await trx('accounts')
    .where('id', 2)
    .increment('balance', 100);
});

// Raw queries
const result = await knex.raw('SELECT * FROM users WHERE id = ?', [1]);
console.log(result.rows);

// Close connection
await knex.destroy();
```

## ORMs

### Prisma

```javascript
// Install Prisma
// npm install prisma --save-dev
// npm install @prisma/client

// Initialize Prisma
// npx prisma init

// Define schema (prisma/schema.prisma)
/*
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        Int      @id @default(autoincrement())
  username  String   @unique
  email     String   @unique
  createdAt DateTime @default(now())
  orders    Order[]
}

model Order {
  id        Int      @id @default(autoincrement())
  userId    Int
  total     Int
  createdAt DateTime @default(now())
  user      User     @relation(fields: [userId], references: [id])
}
*/

// Generate Prisma Client
// npx prisma generate

// Migrate database
// npx prisma migrate dev --name init

// Use Prisma Client
const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  // Create
  const user = await prisma.user.create({
    data: {
      username: 'alice',
      email: 'alice@example.com',
    },
  });
  console.log('Created user:', user);
  
  // Find one
  const foundUser = await prisma.user.findUnique({
    where: { id: 1 },
  });
  
  // Find many
  const users = await prisma.user.findMany({
    where: {
      email: {
        contains: '@example.com',
      },
    },
    orderBy: {
      createdAt: 'desc',
    },
    take: 10,
  });
  
  // Update
  const updatedUser = await prisma.user.update({
    where: { id: 1 },
    data: { email: 'newemail@example.com' },
  });
  
  // Delete
  const deletedUser = await prisma.user.delete({
    where: { id: 1 },
  });
  
  // Relations
  const userWithOrders = await prisma.user.findUnique({
    where: { id: 1 },
    include: {
      orders: true,
    },
  });
  
  console.log(userWithOrders.orders);
  
  // Create with relations
  const newUser = await prisma.user.create({
    data: {
      username: 'bob',
      email: 'bob@example.com',
      orders: {
        create: [
          { total: 100 },
          { total: 200 },
        ],
      },
    },
    include: {
      orders: true,
    },
  });
  
  // Transactions
  const [updatedUser1, updatedUser2] = await prisma.$transaction([
    prisma.user.update({ where: { id: 1 }, data: { email: 'email1@example.com' } }),
    prisma.user.update({ where: { id: 2 }, data: { email: 'email2@example.com' } }),
  ]);
  
  // Raw queries
  const result = await prisma.$queryRaw`SELECT * FROM users WHERE id = ${1}`;
  console.log(result);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

### Sequelize

```javascript
const { Sequelize, DataTypes } = require('sequelize');

// Create Sequelize instance
const sequelize = new Sequelize('mydb', 'postgres', 'password', {
  host: 'localhost',
  port: 5432,
  dialect: 'postgres',
  pool: {
    max: 10,
    min: 0,
    acquire: 30000,
    idle: 10000,
  },
  logging: console.log, // Set to false to disable logging
});

// Test connection
async function testConnection() {
  try {
    await sequelize.authenticate();
    console.log('Connection established successfully');
  } catch (error) {
    console.error('Unable to connect:', error);
  }
}

testConnection();

// Define models
const User = sequelize.define('User', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  username: {
    type: DataTypes.STRING(50),
    allowNull: false,
    unique: true,
  },
  email: {
    type: DataTypes.STRING(100),
    allowNull: false,
    unique: true,
  },
}, {
  tableName: 'users',
  timestamps: true,
});

const Order = sequelize.define('Order', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  userId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: User,
      key: 'id',
    },
  },
  total: {
    type: DataTypes.INTEGER,
    allowNull: false,
  },
}, {
  tableName: 'orders',
  timestamps: true,
});

// Define relationships
User.hasMany(Order, { foreignKey: 'userId' });
Order.belongsTo(User, { foreignKey: 'userId' });

// Sync models (create tables)
await sequelize.sync({ force: false }); // Set to true to drop and recreate

// CRUD operations
async function crudOperations() {
  // Create
  const user = await User.create({
    username: 'alice',
    email: 'alice@example.com',
  });
  console.log('Created user:', user.toJSON());
  
  // Find one
  const foundUser = await User.findOne({
    where: { username: 'alice' },
  });
  
  // Find all
  const users = await User.findAll({
    where: {
      email: {
        [Sequelize.Op.like]: '%@example.com',
      },
    },
    order: [['createdAt', 'DESC']],
    limit: 10,
  });
  
  // Update
  const [updatedCount] = await User.update(
    { email: 'newemail@example.com' },
    { where: { id: 1 } }
  );
  
  // Delete
  const deletedCount = await User.destroy({
    where: { id: 1 },
  });
  
  // With associations
  const userWithOrders = await User.findOne({
    where: { id: 1 },
    include: [Order],
  });
  
  console.log(userWithOrders.Orders);
}

crudOperations();

// Transactions
await sequelize.transaction(async (t) => {
  const user = await User.create({
    username: 'bob',
    email: 'bob@example.com',
  }, { transaction: t });
  
  await Order.create({
    userId: user.id,
    total: 100,
  }, { transaction: t });
});

// Raw queries
const [results, metadata] = await sequelize.query(
  'SELECT * FROM users WHERE id = :id',
  {
    replacements: { id: 1 },
    type: Sequelize.QueryTypes.SELECT,
  }
);

console.log(results);

// Close connection
await sequelize.close();
```

### TypeORM

```javascript
// Install TypeORM
// npm install typeorm reflect-metadata pg

// tsconfig.json
/*
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}
*/

import "reflect-metadata";
import { DataSource, Entity, PrimaryGeneratedColumn, Column, OneToMany, ManyToOne } from "typeorm";

// Define entities
@Entity('users')
class User {
  @PrimaryGeneratedColumn()
  id: number;
  
  @Column({ type: 'varchar', length: 50, unique: true })
  username: string;
  
  @Column({ type: 'varchar', length: 100, unique: true })
  email: string;
  
  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
  
  @OneToMany(() => Order, order => order.user)
  orders: Order[];
}

@Entity('orders')
class Order {
  @PrimaryGeneratedColumn()
  id: number;
  
  @Column()
  userId: number;
  
  @Column()
  total: number;
  
  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
  
  @ManyToOne(() => User, user => user.orders)
  user: User;
}

// Create data source
const AppDataSource = new DataSource({
  type: "postgres",
  host: "localhost",
  port: 5432,
  username: "postgres",
  password: "password",
  database: "mydb",
  synchronize: true, // Auto-create tables (dev only)
  logging: true,
  entities: [User, Order],
  migrations: [],
  subscribers: [],
});

// Initialize
await AppDataSource.initialize();

// CRUD operations
const userRepository = AppDataSource.getRepository(User);
const orderRepository = AppDataSource.getRepository(Order);

// Create
const user = new User();
user.username = 'alice';
user.email = 'alice@example.com';
await userRepository.save(user);

// Find one
const foundUser = await userRepository.findOne({
  where: { id: 1 },
});

// Find many
const users = await userRepository.find({
  where: { email: Like('%@example.com') },
  order: { createdAt: 'DESC' },
  take: 10,
});

// Update
await userRepository.update({ id: 1 }, { email: 'newemail@example.com' });

// Delete
await userRepository.delete({ id: 1 });

// With relations
const userWithOrders = await userRepository.findOne({
  where: { id: 1 },
  relations: ['orders'],
});

// Query builder
const users2 = await userRepository
  .createQueryBuilder('user')
  .where('user.email LIKE :email', { email: '%@example.com' })
  .orderBy('user.createdAt', 'DESC')
  .take(10)
  .getMany();

// Transactions
await AppDataSource.transaction(async (manager) => {
  const user = new User();
  user.username = 'bob';
  user.email = 'bob@example.com';
  await manager.save(user);
  
  const order = new Order();
  order.userId = user.id;
  order.total = 100;
  await manager.save(order);
});

// Raw queries
const rawUsers = await AppDataSource.query('SELECT * FROM users WHERE id = $1', [1]);

// Close connection
await AppDataSource.destroy();
```

## Transactions

### Basic Transactions

```javascript
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: 'postgresql://user:password@localhost/mydb'
});

// Transaction with client
async function transferMoney(fromAccountId, toAccountId, amount) {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    // Deduct from sender
    await client.query(
      'UPDATE accounts SET balance = balance - $1 WHERE id = $2',
      [amount, fromAccountId]
    );
    
    // Add to receiver
    await client.query(
      'UPDATE accounts SET balance = balance + $1 WHERE id = $2',
      [amount, toAccountId]
    );
    
    await client.query('COMMIT');
    console.log('Transaction successful');
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('Transaction failed, rolled back', err);
    throw err;
  } finally {
    client.release();
  }
}

transferMoney(1, 2, 100);

// Transaction helper function
async function withTransaction(callback) {
  const client = await pool.connect();
  
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

// Usage
await withTransaction(async (client) => {
  await client.query('INSERT INTO users (username) VALUES ($1)', ['alice']);
  await client.query('INSERT INTO audit_log (action) VALUES ($1)', ['user_created']);
});
```

### Savepoints

```javascript
async function transactionWithSavepoint() {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    await client.query('INSERT INTO users (username) VALUES ($1)', ['alice']);
    
    // Create savepoint
    await client.query('SAVEPOINT my_savepoint');
    
    try {
      await client.query('INSERT INTO users (username) VALUES ($1)', ['bob']);
      // This might fail due to constraint
    } catch (err) {
      // Rollback to savepoint
      await client.query('ROLLBACK TO SAVEPOINT my_savepoint');
      console.log('Rolled back to savepoint');
    }
    
    await client.query('INSERT INTO users (username) VALUES ($1)', ['charlie']);
    
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

transactionWithSavepoint();
```

## Migrations

### Node-pg-migrate

```javascript
// Install
// npm install node-pg-migrate

// package.json scripts
/*
{
  "scripts": {
    "migrate": "node-pg-migrate",
    "migrate:up": "node-pg-migrate up",
    "migrate:down": "node-pg-migrate down"
  }
}
*/

// Create migration
// npm run migrate create create-users-table

// Migration file: migrations/1234567890_create-users-table.js
exports.up = (pgm) => {
  pgm.createTable('users', {
    id: 'id',
    username: { type: 'varchar(50)', notNull: true, unique: true },
    email: { type: 'varchar(100)', notNull: true, unique: true },
    created_at: {
      type: 'timestamp',
      notNull: true,
      default: pgm.func('current_timestamp'),
    },
  });
  
  pgm.createIndex('users', 'username');
};

exports.down = (pgm) => {
  pgm.dropTable('users');
};

// Run migrations
// npm run migrate up

// Rollback
// npm run migrate down
```

## TypeScript Integration

### TypeScript with pg

```typescript
import { Pool, QueryResult } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

interface User {
  id: number;
  username: string;
  email: string;
  created_at: Date;
}

async function getUser(id: number): Promise<User | null> {
  const result: QueryResult<User> = await pool.query(
    'SELECT * FROM users WHERE id = $1',
    [id]
  );
  
  return result.rows[0] || null;
}

async function getUsers(): Promise<User[]> {
  const result: QueryResult<User> = await pool.query('SELECT * FROM users');
  return result.rows;
}

async function createUser(username: string, email: string): Promise<User> {
  const result: QueryResult<User> = await pool.query(
    'INSERT INTO users (username, email) VALUES ($1, $2) RETURNING *',
    [username, email]
  );
  
  return result.rows[0];
}

// Type-safe query builder
class UserRepository {
  constructor(private pool: Pool) {}
  
  async findById(id: number): Promise<User | null> {
    const { rows } = await this.pool.query<User>(
      'SELECT * FROM users WHERE id = $1',
      [id]
    );
    return rows[0] || null;
  }
  
  async findAll(): Promise<User[]> {
    const { rows } = await this.pool.query<User>('SELECT * FROM users');
    return rows;
  }
  
  async create(username: string, email: string): Promise<User> {
    const { rows } = await this.pool.query<User>(
      'INSERT INTO users (username, email) VALUES ($1, $2) RETURNING *',
      [username, email]
    );
    return rows[0];
  }
}

const userRepo = new UserRepository(pool);
const user = await userRepo.findById(1);
```

## Performance Optimization

### Optimization Techniques

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
});

// 1. Use connection pooling (already shown)

// 2. Batch inserts
async function batchInsert(users) {
  const client = await pool.connect();
  
  try {
    await client.query('BEGIN');
    
    for (const user of users) {
      await client.query(
        'INSERT INTO users (username, email) VALUES ($1, $2)',
        [user.username, user.email]
      );
    }
    
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

// 3. Use COPY for bulk inserts
const { from: copyFrom } = require('pg-copy-streams');
const fs = require('fs');

async function bulkInsertWithCopy() {
  const client = await pool.connect();
  
  try {
    const stream = client.query(
      copyFrom('COPY users (username, email) FROM STDIN CSV')
    );
    
    const fileStream = fs.createReadStream('users.csv');
    fileStream.pipe(stream);
    
    await new Promise((resolve, reject) => {
      stream.on('finish', resolve);
      stream.on('error', reject);
    });
    
    console.log('Bulk insert complete');
  } finally {
    client.release();
  }
}

// 4. Prepared statements (automatically used by pg)

// 5. Use indexes (database side)
await pool.query('CREATE INDEX idx_users_username ON users(username)');

// 6. Connection reuse with transactions
async function multipleOperations() {
  const client = await pool.connect();
  
  try {
    // Reuse same connection for multiple queries
    await client.query('SELECT * FROM users');
    await client.query('SELECT * FROM orders');
    await client.query('SELECT * FROM products');
  } finally {
    client.release();
  }
}

// 7. Query optimization
// Use EXPLAIN to analyze queries
const explainResult = await pool.query('EXPLAIN ANALYZE SELECT * FROM users WHERE username = $1', ['alice']);
console.log(explainResult.rows);
```

## Best Practices

### Best Practices Checklist

```javascript
const { Pool } = require('pg');

// 1. Use environment variables for configuration
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false,
});

// 2. Always use parameterized queries (prevent SQL injection)
// BAD:
// await pool.query(`SELECT * FROM users WHERE username = '${username}'`);

// GOOD:
await pool.query('SELECT * FROM users WHERE username = $1', [username]);

// 3. Use connection pooling (not individual clients)
// BAD: Creating new client for each request
// GOOD: Using pool (shown above)

// 4. Always release clients back to pool
async function goodPractice() {
  const client = await pool.connect();
  try {
    await client.query('SELECT * FROM users');
  } finally {
    client.release(); // Always release!
  }
}

// 5. Handle errors properly
async function withErrorHandling() {
  try {
    const result = await pool.query('SELECT * FROM users WHERE id = $1', [1]);
    return result.rows[0];
  } catch (err) {
    console.error('Database error:', err);
    throw err; // Re-throw or handle appropriately
  }
}

// 6. Use transactions for related operations
async function transactionExample() {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('INSERT INTO users (username) VALUES ($1)', ['alice']);
    await client.query('INSERT INTO audit_log (action) VALUES ($1)', ['user_created']);
    await client.query('COMMIT');
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    client.release();
  }
}

// 7. Graceful shutdown
async function gracefulShutdown() {
  await pool.end();
  console.log('Pool has ended');
}

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// 8. Monitor pool health
function monitorPool() {
  console.log('Pool stats:', {
    totalCount: pool.totalCount,
    idleCount: pool.idleCount,
    waitingCount: pool.waitingCount,
  });
}

setInterval(monitorPool, 60000);

// 9. Set query timeouts
pool.query({
  text: 'SELECT * FROM large_table',
  values: [],
  rowMode: 'array',
}, (err, res) => {
  if (err) console.error(err);
});

// 10. Use TypeScript for type safety
// See TypeScript section above
```

## Summary

PostgreSQL and Node.js integration provides:
- **pg (node-postgres)**: Industry-standard PostgreSQL driver
- **Connection Pooling**: Efficient connection management with Pool
- **ORMs**: Prisma, Sequelize, TypeORM for object-relational mapping
- **Query Builders**: Knex.js, Slonik for flexible query building
- **Transactions**: ACID compliance with BEGIN/COMMIT/ROLLBACK
- **TypeScript**: Full type safety support
- **Performance**: Bulk operations, prepared statements, connection reuse

Node.js offers excellent PostgreSQL support for building scalable applications.

## Next Steps

- Study [PostgreSQL and Python](./39-postgresql-and-python.md)
- Learn [Query Optimization](./20-query-optimization.md)
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Practice [Performance Troubleshooting](./41-performance-troubleshooting.md)
