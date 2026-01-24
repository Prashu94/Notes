# Chapter 36: Transaction Fundamentals

## Table of Contents
- [Introduction to Transactions](#introduction-to-transactions)
- [ACID Properties](#acid-properties)
- [Transaction Support in MongoDB](#transaction-support-in-mongodb)
- [Single Document Atomicity](#single-document-atomicity)
- [Multi-Document Transactions](#multi-document-transactions)
- [Transaction Sessions](#transaction-sessions)
- [Basic Transaction Syntax](#basic-transaction-syntax)
- [Summary](#summary)

---

## Introduction to Transactions

Transactions allow multiple read and write operations to be executed as a single atomic unit. MongoDB supports both single-document atomicity and multi-document transactions.

### Transaction Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Transaction Support                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Single-Document Operations (Always Atomic)                        │
│  ├── Insert one document                                           │
│  ├── Update one document                                           │
│  ├── Delete one document                                           │
│  └── All fields in one document updated atomically                 │
│                                                                     │
│  Multi-Document Transactions (Since MongoDB 4.0+)                  │
│  ├── Multiple documents across collections                         │
│  ├── Requires replica set or sharded cluster                       │
│  ├── Session-based operations                                      │
│  └── Commit or abort as a unit                                     │
│                                                                     │
│  Distributed Transactions (Since MongoDB 4.2+)                     │
│  └── Across sharded clusters                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use Transactions

| Scenario | Transaction Needed? |
|----------|---------------------|
| Update single document | No (already atomic) |
| Insert single document | No (already atomic) |
| Transfer between accounts | Yes (multi-document) |
| Order with inventory update | Yes (multi-document) |
| Complex data migration | Yes (consistency) |
| Read multiple related docs | Sometimes (read concern) |

---

## ACID Properties

### Understanding ACID

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ACID Properties                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Atomicity                                                         │
│  └── All operations succeed or all fail                            │
│      Transaction cannot be partially applied                       │
│                                                                     │
│  Consistency                                                       │
│  └── Database moves from one valid state to another               │
│      Data integrity rules are preserved                            │
│                                                                     │
│  Isolation                                                         │
│  └── Concurrent transactions don't interfere                       │
│      Each sees consistent snapshot of data                         │
│                                                                     │
│  Durability                                                        │
│  └── Committed transactions survive system failures               │
│      Data persisted to storage                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ACID in MongoDB

```javascript
// Atomicity Example
// Either both updates succeed or both fail
session.startTransaction()
try {
  // Debit from account A
  db.accounts.updateOne(
    { _id: "A" },
    { $inc: { balance: -100 } },
    { session }
  )
  
  // Credit to account B
  db.accounts.updateOne(
    { _id: "B" },
    { $inc: { balance: 100 } },
    { session }
  )
  
  session.commitTransaction()
  // Both updates applied
} catch (e) {
  session.abortTransaction()
  // Neither update applied
}

// Consistency: balance rules maintained
// Isolation: other sessions see consistent state
// Durability: committed changes persist
```

---

## Transaction Support in MongoDB

### Requirements

| Feature | Requirement |
|---------|-------------|
| Multi-document transactions | Replica set or sharded cluster |
| Distributed transactions | MongoDB 4.2+ with sharded cluster |
| Read concern | snapshot, majority, or local |
| Write concern | majority recommended |

### Version Support

```
MongoDB Version  | Transaction Support
-----------------|---------------------------------------
4.0              | Multi-document on replica sets
4.2              | Distributed transactions (sharded)
4.4              | Improved performance
5.0+             | Enhanced features and performance
```

### Standalone Limitations

```javascript
// ⚠️ Transactions require replica set
// Standalone MongoDB does NOT support multi-document transactions

// For development, convert standalone to single-node replica set:
// 1. Add to mongod.conf: replication.replSetName: "rs0"
// 2. Restart mongod
// 3. Run: rs.initiate()
```

---

## Single Document Atomicity

### Built-in Atomicity

```javascript
// All modifications to a single document are atomic
// No transaction needed

// Atomic insert
db.orders.insertOne({
  orderId: "ORD-001",
  customer: "Alice",
  items: [
    { product: "Widget", qty: 2, price: 25 },
    { product: "Gadget", qty: 1, price: 50 }
  ],
  total: 100,
  status: "pending"
})

// Atomic update of multiple fields
db.orders.updateOne(
  { orderId: "ORD-001" },
  {
    $set: { status: "completed", completedAt: new Date() },
    $inc: { total: 10 }  // Add shipping
  }
)
// All changes applied atomically

// Atomic array operations
db.orders.updateOne(
  { orderId: "ORD-001" },
  {
    $push: { items: { product: "Extra", qty: 1, price: 15 } },
    $inc: { total: 15 }
  }
)
```

### Embedding for Atomicity

```javascript
// Design documents to enable atomic operations

// ❌ Multiple documents (needs transaction)
// Orders collection
{ _id: "order1", customer: "Alice", total: 100 }
// OrderItems collection
{ orderId: "order1", product: "Widget", qty: 2 }
{ orderId: "order1", product: "Gadget", qty: 1 }

// ✅ Single document (atomic without transaction)
{
  _id: "order1",
  customer: "Alice",
  items: [
    { product: "Widget", qty: 2, price: 25 },
    { product: "Gadget", qty: 1, price: 50 }
  ],
  total: 100
}
```

---

## Multi-Document Transactions

### When Multi-Document Transactions Are Needed

```javascript
// Scenario 1: Transfer between accounts
// Must update two documents atomically

// Scenario 2: Order with inventory
// Must update order AND reduce inventory

// Scenario 3: User and audit log
// Must create record in both collections

// Setup example data
db.accounts.drop()
db.accounts.insertMany([
  { _id: "A", owner: "Alice", balance: 1000 },
  { _id: "B", owner: "Bob", balance: 500 }
])

db.inventory.drop()
db.inventory.insertMany([
  { _id: "WIDGET", name: "Widget", stock: 100, price: 25 },
  { _id: "GADGET", name: "Gadget", stock: 50, price: 50 }
])

db.orders.drop()
```

### Transaction Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Transaction Lifecycle                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Start Session                                                  │
│     └── client.startSession()                                      │
│                                                                     │
│  2. Start Transaction                                              │
│     └── session.startTransaction(options)                          │
│                                                                     │
│  3. Execute Operations                                             │
│     └── All operations include { session } option                  │
│                                                                     │
│  4. Commit or Abort                                                │
│     ├── session.commitTransaction() - Apply changes                │
│     └── session.abortTransaction() - Discard changes               │
│                                                                     │
│  5. End Session                                                    │
│     └── session.endSession()                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Transaction Sessions

### Creating a Session

```javascript
// In mongosh (MongoDB Shell)
const session = db.getMongo().startSession()

// Or with options
const session = db.getMongo().startSession({
  causalConsistency: true
})
```

### Session Options

| Option | Description | Default |
|--------|-------------|---------|
| `causalConsistency` | Guarantees causal ordering | true |
| `readPreference` | Where to read from | primary |
| `readConcern` | Read isolation level | - |

### Transaction Options

```javascript
session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority" },
  readPreference: "primary"
})
```

### Read Concern Levels

| Level | Description |
|-------|-------------|
| `local` | Latest data (may be rolled back) |
| `majority` | Acknowledged by majority |
| `snapshot` | Point-in-time snapshot |
| `linearizable` | Real-time read |

### Write Concern Levels

| Level | Description |
|-------|-------------|
| `1` | Acknowledged by primary |
| `majority` | Acknowledged by majority |
| `0` | No acknowledgment |

---

## Basic Transaction Syntax

### Simple Transaction Example

```javascript
// Setup: Ensure replica set is running

// Start session
const session = db.getMongo().startSession()

try {
  // Start transaction
  session.startTransaction({
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority" }
  })
  
  // Operation 1: Debit account A
  db.accounts.updateOne(
    { _id: "A" },
    { $inc: { balance: -100 } },
    { session }
  )
  
  // Operation 2: Credit account B
  db.accounts.updateOne(
    { _id: "B" },
    { $inc: { balance: 100 } },
    { session }
  )
  
  // Commit the transaction
  session.commitTransaction()
  print("Transaction committed successfully")
  
} catch (error) {
  // Abort on error
  session.abortTransaction()
  print("Transaction aborted:", error.message)
  
} finally {
  // Always end session
  session.endSession()
}

// Verify results
db.accounts.find()
```

### Transaction with Validation

```javascript
const session = db.getMongo().startSession()

try {
  session.startTransaction()
  
  // Read current balance
  const accountA = db.accounts.findOne({ _id: "A" }, { session })
  
  // Validate
  if (accountA.balance < 100) {
    throw new Error("Insufficient funds")
  }
  
  // Perform transfer
  db.accounts.updateOne(
    { _id: "A" },
    { $inc: { balance: -100 } },
    { session }
  )
  
  db.accounts.updateOne(
    { _id: "B" },
    { $inc: { balance: 100 } },
    { session }
  )
  
  session.commitTransaction()
  print("Transfer completed")
  
} catch (error) {
  session.abortTransaction()
  print("Transfer failed:", error.message)
  
} finally {
  session.endSession()
}
```

### Using withTransaction Helper

```javascript
// Recommended approach - handles retries automatically
const session = db.getMongo().startSession()

try {
  session.withTransaction(() => {
    // All operations here
    db.accounts.updateOne(
      { _id: "A" },
      { $inc: { balance: -50 } },
      { session }
    )
    
    db.accounts.updateOne(
      { _id: "B" },
      { $inc: { balance: 50 } },
      { session }
    )
    
    // Return truthy value to commit
    return true
  })
  
  print("Transaction successful")
  
} catch (error) {
  print("Transaction failed:", error.message)
  
} finally {
  session.endSession()
}
```

### Cross-Collection Transaction

```javascript
// Order placement with inventory check
const session = db.getMongo().startSession()

try {
  session.startTransaction()
  
  const productId = "WIDGET"
  const quantity = 5
  
  // Check inventory
  const product = db.inventory.findOne({ _id: productId }, { session })
  
  if (!product || product.stock < quantity) {
    throw new Error("Insufficient inventory")
  }
  
  // Create order
  const order = {
    orderId: "ORD-" + Date.now(),
    product: productId,
    quantity: quantity,
    price: product.price * quantity,
    status: "confirmed",
    createdAt: new Date()
  }
  
  db.orders.insertOne(order, { session })
  
  // Update inventory
  db.inventory.updateOne(
    { _id: productId },
    { $inc: { stock: -quantity } },
    { session }
  )
  
  session.commitTransaction()
  print("Order placed:", order.orderId)
  
} catch (error) {
  session.abortTransaction()
  print("Order failed:", error.message)
  
} finally {
  session.endSession()
}

// Verify
print("\nInventory:")
db.inventory.find().forEach(printjson)
print("\nOrders:")
db.orders.find().forEach(printjson)
```

---

## Summary

### Transaction Types

| Type | MongoDB Version | Scope |
|------|-----------------|-------|
| Single-document | All | One document |
| Multi-document | 4.0+ | Replica set |
| Distributed | 4.2+ | Sharded cluster |

### ACID in MongoDB

| Property | Implementation |
|----------|----------------|
| Atomicity | All-or-nothing operations |
| Consistency | Schema validation, transactions |
| Isolation | Snapshot isolation |
| Durability | Write concern, journaling |

### Basic Transaction Pattern

```javascript
const session = db.getMongo().startSession()
try {
  session.startTransaction()
  // ... operations with { session }
  session.commitTransaction()
} catch (e) {
  session.abortTransaction()
} finally {
  session.endSession()
}
```

### What's Next?

In the next chapter, we'll explore Multi-Document Transaction Patterns in detail.

---

## Practice Questions

1. What ACID property ensures all-or-nothing execution?
2. When do you need multi-document transactions in MongoDB?
3. What's required to use multi-document transactions?
4. What's the difference between read concern "local" and "snapshot"?
5. Why should you use write concern "majority"?
6. What does session.abortTransaction() do?
7. How does single-document atomicity work?
8. What is the withTransaction helper?

---

## Hands-On Exercises

### Exercise 1: Single Document Atomicity

```javascript
// Demonstrate single-document atomicity

// Setup
db.atomicTest.drop()
db.atomicTest.insertOne({
  _id: 1,
  name: "Test Document",
  counter: 0,
  items: [],
  metadata: {}
})

// Multiple field updates (atomic)
print("1. Multi-field update:")
db.atomicTest.updateOne(
  { _id: 1 },
  {
    $set: { "metadata.updated": new Date() },
    $inc: { counter: 1 },
    $push: { items: "item1" }
  }
)
printjson(db.atomicTest.findOne({ _id: 1 }))

// Array operations (atomic)
print("\n2. Array operations:")
db.atomicTest.updateOne(
  { _id: 1 },
  {
    $push: { items: { $each: ["item2", "item3"] } },
    $inc: { counter: 1 }
  }
)
printjson(db.atomicTest.findOne({ _id: 1 }))

// Complex update (atomic)
print("\n3. Complex update:")
db.atomicTest.updateOne(
  { _id: 1, counter: { $gte: 0 } },
  {
    $set: { status: "active" },
    $currentDate: { lastModified: true },
    $inc: { counter: 5 }
  }
)
printjson(db.atomicTest.findOne({ _id: 1 }))
```

### Exercise 2: Basic Transaction

```javascript
// Simple money transfer transaction

// Setup accounts
db.accounts.drop()
db.accounts.insertMany([
  { _id: "ALICE", name: "Alice", balance: 1000 },
  { _id: "BOB", name: "Bob", balance: 500 }
])

print("Initial balances:")
db.accounts.find().forEach(a => print(`  ${a.name}: $${a.balance}`))

// Transfer function
function transfer(from, to, amount) {
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    // Check balance
    const fromAccount = db.accounts.findOne({ _id: from }, { session })
    if (!fromAccount || fromAccount.balance < amount) {
      throw new Error(`Insufficient funds in ${from}`)
    }
    
    // Debit
    db.accounts.updateOne(
      { _id: from },
      { $inc: { balance: -amount } },
      { session }
    )
    
    // Credit
    db.accounts.updateOne(
      { _id: to },
      { $inc: { balance: amount } },
      { session }
    )
    
    session.commitTransaction()
    return { success: true, message: `Transferred $${amount} from ${from} to ${to}` }
    
  } catch (error) {
    session.abortTransaction()
    return { success: false, message: error.message }
    
  } finally {
    session.endSession()
  }
}

// Test transfers
print("\n--- Transfer Tests ---")

// Valid transfer
let result = transfer("ALICE", "BOB", 200)
print(`\nTransfer 1: ${result.message}`)
db.accounts.find().forEach(a => print(`  ${a.name}: $${a.balance}`))

// Another valid transfer
result = transfer("BOB", "ALICE", 100)
print(`\nTransfer 2: ${result.message}`)
db.accounts.find().forEach(a => print(`  ${a.name}: $${a.balance}`))

// Invalid transfer (insufficient funds)
result = transfer("BOB", "ALICE", 10000)
print(`\nTransfer 3: ${result.message}`)
db.accounts.find().forEach(a => print(`  ${a.name}: $${a.balance}`))
```

### Exercise 3: Cross-Collection Transaction

```javascript
// Order placement with inventory management

// Setup
db.products.drop()
db.orders.drop()
db.products.insertMany([
  { _id: "LAPTOP", name: "Laptop", price: 999, stock: 10 },
  { _id: "PHONE", name: "Phone", price: 699, stock: 25 },
  { _id: "TABLET", name: "Tablet", price: 499, stock: 15 }
])

print("Initial inventory:")
db.products.find().forEach(p => print(`  ${p.name}: ${p.stock} units @ $${p.price}`))

// Place order function
function placeOrder(customer, items) {
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    let total = 0
    const orderItems = []
    
    // Process each item
    for (const item of items) {
      const product = db.products.findOne({ _id: item.productId }, { session })
      
      if (!product) {
        throw new Error(`Product ${item.productId} not found`)
      }
      
      if (product.stock < item.quantity) {
        throw new Error(`Insufficient stock for ${product.name}`)
      }
      
      // Update inventory
      db.products.updateOne(
        { _id: item.productId },
        { $inc: { stock: -item.quantity } },
        { session }
      )
      
      // Add to order items
      orderItems.push({
        productId: item.productId,
        name: product.name,
        quantity: item.quantity,
        price: product.price,
        subtotal: product.price * item.quantity
      })
      
      total += product.price * item.quantity
    }
    
    // Create order
    const order = {
      orderId: "ORD-" + Date.now(),
      customer: customer,
      items: orderItems,
      total: total,
      status: "confirmed",
      createdAt: new Date()
    }
    
    db.orders.insertOne(order, { session })
    
    session.commitTransaction()
    return { success: true, order: order }
    
  } catch (error) {
    session.abortTransaction()
    return { success: false, message: error.message }
    
  } finally {
    session.endSession()
  }
}

// Test orders
print("\n--- Order Tests ---")

// Valid order
let result = placeOrder("Alice", [
  { productId: "LAPTOP", quantity: 2 },
  { productId: "PHONE", quantity: 1 }
])
print("\nOrder 1:", result.success ? "Success" : result.message)
if (result.success) {
  print("  Order ID:", result.order.orderId)
  print("  Total: $" + result.order.total)
}

// Check inventory
print("\nUpdated inventory:")
db.products.find().forEach(p => print(`  ${p.name}: ${p.stock} units`))

// Invalid order (insufficient stock)
result = placeOrder("Bob", [
  { productId: "LAPTOP", quantity: 100 }
])
print("\nOrder 2:", result.success ? "Success" : result.message)

// Verify inventory unchanged
print("\nInventory after failed order:")
db.products.find().forEach(p => print(`  ${p.name}: ${p.stock} units`))
```

### Exercise 4: Transaction with Rollback

```javascript
// Demonstrate transaction rollback

db.testTxn.drop()
db.testTxn.insertMany([
  { _id: 1, value: 100 },
  { _id: 2, value: 200 },
  { _id: 3, value: 300 }
])

print("Initial state:")
db.testTxn.find().forEach(printjson)

// Transaction that will fail
const session = db.getMongo().startSession()

try {
  session.startTransaction()
  
  // First update (will be rolled back)
  db.testTxn.updateOne({ _id: 1 }, { $set: { value: 999 } }, { session })
  print("\nAfter first update (in transaction):")
  print("  _id: 1 value:", db.testTxn.findOne({ _id: 1 }, { session }).value)
  
  // Second update (will be rolled back)
  db.testTxn.updateOne({ _id: 2 }, { $set: { value: 888 } }, { session })
  print("  _id: 2 value:", db.testTxn.findOne({ _id: 2 }, { session }).value)
  
  // Simulate error
  throw new Error("Simulated failure")
  
  session.commitTransaction()
  
} catch (error) {
  print("\nError occurred:", error.message)
  session.abortTransaction()
  print("Transaction aborted!")
  
} finally {
  session.endSession()
}

// Verify rollback
print("\nAfter rollback (values restored):")
db.testTxn.find().forEach(printjson)
```

### Exercise 5: withTransaction Helper

```javascript
// Using withTransaction for automatic retry

db.counter.drop()
db.counter.insertOne({ _id: "main", value: 0 })

function incrementCounter(amount) {
  const session = db.getMongo().startSession()
  
  try {
    const result = session.withTransaction(() => {
      const current = db.counter.findOne({ _id: "main" }, { session })
      
      db.counter.updateOne(
        { _id: "main" },
        { 
          $inc: { value: amount },
          $push: { 
            history: {
              change: amount,
              newValue: current.value + amount,
              timestamp: new Date()
            }
          }
        },
        { session }
      )
      
      return current.value + amount
    })
    
    return { success: true, newValue: result }
    
  } catch (error) {
    return { success: false, message: error.message }
    
  } finally {
    session.endSession()
  }
}

// Test
print("Initial value:", db.counter.findOne().value)

for (let i = 1; i <= 5; i++) {
  const result = incrementCounter(i * 10)
  print(`Increment ${i}: +${i * 10} → ${result.success ? result.newValue : result.message}`)
}

print("\nFinal state:")
printjson(db.counter.findOne())
```

---

[← Previous: Geospatial Queries](35-geospatial-queries.md) | [Next: Multi-Document Transaction Patterns →](37-multi-document-transactions.md)
