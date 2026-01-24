# Chapter 37: Multi-Document Transaction Patterns

## Table of Contents
- [Common Transaction Patterns](#common-transaction-patterns)
- [Money Transfer Pattern](#money-transfer-pattern)
- [Order Processing Pattern](#order-processing-pattern)
- [Saga Pattern](#saga-pattern)
- [Two-Phase Commit Pattern](#two-phase-commit-pattern)
- [Retry Logic](#retry-logic)
- [Transaction Best Practices](#transaction-best-practices)
- [Summary](#summary)

---

## Common Transaction Patterns

Multi-document transactions are essential when operations must be atomic across multiple documents or collections.

### Pattern Categories

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Multi-Document Transaction Patterns                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Financial Transactions                                            │
│  ├── Money transfers between accounts                              │
│  ├── Payment processing                                            │
│  └── Balance adjustments                                           │
│                                                                     │
│  E-Commerce Transactions                                           │
│  ├── Order placement with inventory                                │
│  ├── Cart checkout                                                 │
│  └── Reservation systems                                           │
│                                                                     │
│  Data Integrity Transactions                                       │
│  ├── Parent-child relationships                                    │
│  ├── Audit logging                                                 │
│  └── Cascading updates                                             │
│                                                                     │
│  Compensating Patterns                                             │
│  ├── Saga pattern                                                  │
│  ├── Two-phase commit                                              │
│  └── Event sourcing                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Banking accounts
db.accounts.drop()
db.accounts.insertMany([
  { _id: "ACC001", owner: "Alice", balance: 5000, currency: "USD", type: "checking" },
  { _id: "ACC002", owner: "Alice", balance: 10000, currency: "USD", type: "savings" },
  { _id: "ACC003", owner: "Bob", balance: 3000, currency: "USD", type: "checking" },
  { _id: "ACC004", owner: "Charlie", balance: 7500, currency: "USD", type: "checking" }
])

// Transaction history
db.transactions.drop()

// E-commerce products
db.products.drop()
db.products.insertMany([
  { _id: "PROD001", name: "Laptop", price: 999, stock: 50, reserved: 0 },
  { _id: "PROD002", name: "Phone", price: 699, stock: 100, reserved: 0 },
  { _id: "PROD003", name: "Tablet", price: 499, stock: 30, reserved: 0 },
  { _id: "PROD004", name: "Watch", price: 299, stock: 75, reserved: 0 }
])

// Orders
db.orders.drop()

// Reservations
db.reservations.drop()
```

---

## Money Transfer Pattern

### Basic Transfer

```javascript
function transferMoney(fromAccount, toAccount, amount, description = "") {
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction({
      readConcern: { level: "snapshot" },
      writeConcern: { w: "majority" }
    })
    
    const transactionId = ObjectId()
    const timestamp = new Date()
    
    // Validate source account
    const source = db.accounts.findOne({ _id: fromAccount }, { session })
    if (!source) {
      throw new Error(`Source account ${fromAccount} not found`)
    }
    if (source.balance < amount) {
      throw new Error(`Insufficient funds: available $${source.balance}, requested $${amount}`)
    }
    
    // Validate destination account
    const destination = db.accounts.findOne({ _id: toAccount }, { session })
    if (!destination) {
      throw new Error(`Destination account ${toAccount} not found`)
    }
    
    // Debit source account
    db.accounts.updateOne(
      { _id: fromAccount },
      {
        $inc: { balance: -amount },
        $set: { lastTransaction: timestamp }
      },
      { session }
    )
    
    // Credit destination account
    db.accounts.updateOne(
      { _id: toAccount },
      {
        $inc: { balance: amount },
        $set: { lastTransaction: timestamp }
      },
      { session }
    )
    
    // Record transaction
    db.transactions.insertOne({
      _id: transactionId,
      type: "transfer",
      from: fromAccount,
      to: toAccount,
      amount: amount,
      description: description,
      status: "completed",
      timestamp: timestamp
    }, { session })
    
    session.commitTransaction()
    
    return {
      success: true,
      transactionId: transactionId,
      message: `Transferred $${amount} from ${fromAccount} to ${toAccount}`
    }
    
  } catch (error) {
    session.abortTransaction()
    
    // Log failed transaction
    db.transactions.insertOne({
      type: "transfer",
      from: fromAccount,
      to: toAccount,
      amount: amount,
      description: description,
      status: "failed",
      error: error.message,
      timestamp: new Date()
    })
    
    return {
      success: false,
      error: error.message
    }
    
  } finally {
    session.endSession()
  }
}

// Test transfers
print("=== Money Transfer Tests ===\n")

print("Initial balances:")
db.accounts.find().forEach(a => print(`  ${a._id} (${a.owner}): $${a.balance}`))

// Valid transfer
let result = transferMoney("ACC001", "ACC003", 500, "Payment for services")
print("\nTransfer 1:", result.success ? "✓ " + result.message : "✗ " + result.error)

// Transfer between own accounts
result = transferMoney("ACC002", "ACC001", 1000, "Internal transfer")
print("Transfer 2:", result.success ? "✓ " + result.message : "✗ " + result.error)

// Insufficient funds
result = transferMoney("ACC003", "ACC004", 50000, "Large transfer")
print("Transfer 3:", result.success ? "✓ " + result.message : "✗ " + result.error)

print("\nFinal balances:")
db.accounts.find().forEach(a => print(`  ${a._id} (${a.owner}): $${a.balance}`))

print("\nTransaction history:")
db.transactions.find().forEach(t => {
  const status = t.status === "completed" ? "✓" : "✗"
  print(`  ${status} ${t.from} → ${t.to}: $${t.amount} (${t.status})`)
})
```

### Transfer with Validation Rules

```javascript
function transferWithRules(fromAccount, toAccount, amount, options = {}) {
  const {
    maxDailyLimit = 10000,
    minTransfer = 1,
    requireDescription = false,
    description = ""
  } = options
  
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    // Validate amount
    if (amount < minTransfer) {
      throw new Error(`Minimum transfer amount is $${minTransfer}`)
    }
    
    if (requireDescription && !description) {
      throw new Error("Description is required for this transfer")
    }
    
    // Check daily limit
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const dailyTotal = db.transactions.aggregate([
      {
        $match: {
          from: fromAccount,
          status: "completed",
          timestamp: { $gte: today }
        }
      },
      {
        $group: {
          _id: null,
          total: { $sum: "$amount" }
        }
      }
    ], { session }).toArray()
    
    const currentDailyTotal = dailyTotal.length > 0 ? dailyTotal[0].total : 0
    
    if (currentDailyTotal + amount > maxDailyLimit) {
      throw new Error(`Daily limit exceeded. Current: $${currentDailyTotal}, Limit: $${maxDailyLimit}`)
    }
    
    // Get accounts
    const source = db.accounts.findOne({ _id: fromAccount }, { session })
    const destination = db.accounts.findOne({ _id: toAccount }, { session })
    
    if (!source) throw new Error("Source account not found")
    if (!destination) throw new Error("Destination account not found")
    if (source.balance < amount) throw new Error("Insufficient funds")
    
    // Execute transfer
    db.accounts.updateOne({ _id: fromAccount }, { $inc: { balance: -amount } }, { session })
    db.accounts.updateOne({ _id: toAccount }, { $inc: { balance: amount } }, { session })
    
    db.transactions.insertOne({
      type: "transfer",
      from: fromAccount,
      to: toAccount,
      amount: amount,
      description: description,
      dailyTotal: currentDailyTotal + amount,
      status: "completed",
      timestamp: new Date()
    }, { session })
    
    session.commitTransaction()
    return { success: true, dailyTotal: currentDailyTotal + amount }
    
  } catch (error) {
    session.abortTransaction()
    return { success: false, error: error.message }
    
  } finally {
    session.endSession()
  }
}
```

---

## Order Processing Pattern

### Complete Order Workflow

```javascript
function placeOrder(customerId, items, paymentMethod) {
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    const orderId = "ORD-" + Date.now()
    const orderItems = []
    let total = 0
    
    // Process each item
    for (const item of items) {
      const product = db.products.findOne({ _id: item.productId }, { session })
      
      if (!product) {
        throw new Error(`Product ${item.productId} not found`)
      }
      
      const availableStock = product.stock - product.reserved
      if (availableStock < item.quantity) {
        throw new Error(`Insufficient stock for ${product.name}: available ${availableStock}, requested ${item.quantity}`)
      }
      
      // Reserve inventory
      db.products.updateOne(
        { _id: item.productId },
        { $inc: { reserved: item.quantity } },
        { session }
      )
      
      orderItems.push({
        productId: item.productId,
        name: product.name,
        price: product.price,
        quantity: item.quantity,
        subtotal: product.price * item.quantity
      })
      
      total += product.price * item.quantity
    }
    
    // Create order
    const order = {
      _id: orderId,
      customerId: customerId,
      items: orderItems,
      total: total,
      paymentMethod: paymentMethod,
      status: "pending",
      createdAt: new Date()
    }
    
    db.orders.insertOne(order, { session })
    
    // Process payment (simulated)
    if (paymentMethod === "account") {
      const account = db.accounts.findOne({ owner: customerId }, { session })
      if (!account || account.balance < total) {
        throw new Error("Insufficient account balance for payment")
      }
      
      db.accounts.updateOne(
        { _id: account._id },
        { $inc: { balance: -total } },
        { session }
      )
      
      db.orders.updateOne(
        { _id: orderId },
        { 
          $set: { 
            status: "paid",
            paymentAccount: account._id,
            paidAt: new Date()
          }
        },
        { session }
      )
    }
    
    session.commitTransaction()
    
    return {
      success: true,
      orderId: orderId,
      total: total,
      status: order.status
    }
    
  } catch (error) {
    session.abortTransaction()
    return {
      success: false,
      error: error.message
    }
    
  } finally {
    session.endSession()
  }
}

// Confirm order (ship and reduce actual stock)
function confirmOrder(orderId) {
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    const order = db.orders.findOne({ _id: orderId }, { session })
    
    if (!order) {
      throw new Error("Order not found")
    }
    
    if (order.status !== "paid" && order.status !== "pending") {
      throw new Error(`Cannot confirm order in status: ${order.status}`)
    }
    
    // Reduce stock and reserved count
    for (const item of order.items) {
      db.products.updateOne(
        { _id: item.productId },
        {
          $inc: {
            stock: -item.quantity,
            reserved: -item.quantity
          }
        },
        { session }
      )
    }
    
    // Update order status
    db.orders.updateOne(
      { _id: orderId },
      {
        $set: {
          status: "confirmed",
          confirmedAt: new Date()
        }
      },
      { session }
    )
    
    session.commitTransaction()
    return { success: true, message: "Order confirmed" }
    
  } catch (error) {
    session.abortTransaction()
    return { success: false, error: error.message }
    
  } finally {
    session.endSession()
  }
}

// Test order processing
print("\n=== Order Processing Tests ===\n")

print("Initial inventory:")
db.products.find().forEach(p => print(`  ${p.name}: ${p.stock} in stock, ${p.reserved} reserved`))

// Place order
let result = placeOrder("Alice", [
  { productId: "PROD001", quantity: 2 },
  { productId: "PROD002", quantity: 1 }
], "account")

print("\nOrder 1:", result.success ? `✓ ${result.orderId} - $${result.total}` : "✗ " + result.error)

// Check inventory after order
print("\nInventory after order:")
db.products.find({ _id: { $in: ["PROD001", "PROD002"] } }).forEach(p => {
  print(`  ${p.name}: ${p.stock} stock, ${p.reserved} reserved, ${p.stock - p.reserved} available`)
})

// Confirm order
if (result.success) {
  const confirmResult = confirmOrder(result.orderId)
  print("\nConfirm order:", confirmResult.success ? "✓ " + confirmResult.message : "✗ " + confirmResult.error)
  
  print("\nInventory after confirmation:")
  db.products.find({ _id: { $in: ["PROD001", "PROD002"] } }).forEach(p => {
    print(`  ${p.name}: ${p.stock} stock, ${p.reserved} reserved`)
  })
}
```

---

## Saga Pattern

### Implementing Saga for Distributed Operations

```javascript
// Saga pattern for order processing with compensation
function orderSaga(customerId, items, paymentMethod) {
  const sagaId = "SAGA-" + Date.now()
  const steps = []
  
  // Step 1: Reserve Inventory
  function reserveInventory(session) {
    const reserved = []
    
    for (const item of items) {
      const product = db.products.findOne({ _id: item.productId }, { session })
      if (!product || (product.stock - product.reserved) < item.quantity) {
        throw new Error(`Cannot reserve ${item.productId}`)
      }
      
      db.products.updateOne(
        { _id: item.productId },
        { $inc: { reserved: item.quantity } },
        { session }
      )
      
      reserved.push({ productId: item.productId, quantity: item.quantity })
    }
    
    return reserved
  }
  
  // Compensate: Release Inventory
  function releaseInventory(reserved) {
    for (const item of reserved) {
      db.products.updateOne(
        { _id: item.productId },
        { $inc: { reserved: -item.quantity } }
      )
    }
  }
  
  // Step 2: Process Payment
  function processPayment(total, session) {
    const account = db.accounts.findOne({ owner: customerId }, { session })
    if (!account || account.balance < total) {
      throw new Error("Payment failed: insufficient funds")
    }
    
    db.accounts.updateOne(
      { _id: account._id },
      { $inc: { balance: -total } },
      { session }
    )
    
    return { accountId: account._id, amount: total }
  }
  
  // Compensate: Refund Payment
  function refundPayment(payment) {
    db.accounts.updateOne(
      { _id: payment.accountId },
      { $inc: { balance: payment.amount } }
    )
  }
  
  // Step 3: Create Order
  function createOrder(items, total, session) {
    const orderId = "ORD-" + Date.now()
    const order = {
      _id: orderId,
      sagaId: sagaId,
      customerId: customerId,
      items: items,
      total: total,
      status: "completed",
      createdAt: new Date()
    }
    
    db.orders.insertOne(order, { session })
    return orderId
  }
  
  // Execute saga
  const session = db.getMongo().startSession()
  let reserved = null
  let payment = null
  
  try {
    session.startTransaction()
    
    // Step 1: Reserve
    reserved = reserveInventory(session)
    steps.push({ name: "reserve", status: "completed", data: reserved })
    
    // Calculate total
    const total = items.reduce((sum, item) => {
      const product = db.products.findOne({ _id: item.productId }, { session })
      return sum + (product.price * item.quantity)
    }, 0)
    
    // Step 2: Payment
    payment = processPayment(total, session)
    steps.push({ name: "payment", status: "completed", data: payment })
    
    // Step 3: Create Order
    const orderId = createOrder(items, total, session)
    steps.push({ name: "order", status: "completed", data: { orderId } })
    
    session.commitTransaction()
    
    // Log saga completion
    db.sagas.insertOne({
      _id: sagaId,
      type: "order",
      customerId: customerId,
      steps: steps,
      status: "completed",
      completedAt: new Date()
    })
    
    return { success: true, sagaId, orderId, steps }
    
  } catch (error) {
    session.abortTransaction()
    
    // Compensating transactions
    print("  Running compensations...")
    
    if (payment) {
      refundPayment(payment)
      steps.push({ name: "refund", status: "compensated" })
    }
    
    if (reserved) {
      releaseInventory(reserved)
      steps.push({ name: "release", status: "compensated" })
    }
    
    // Log saga failure
    db.sagas.insertOne({
      _id: sagaId,
      type: "order",
      customerId: customerId,
      steps: steps,
      status: "failed",
      error: error.message,
      failedAt: new Date()
    })
    
    return { success: false, sagaId, error: error.message, steps }
    
  } finally {
    session.endSession()
  }
}

// Test saga
print("\n=== Saga Pattern Test ===\n")

const sagaResult = orderSaga("Alice", [
  { productId: "PROD003", quantity: 3 },
  { productId: "PROD004", quantity: 2 }
], "account")

print("Saga Result:", sagaResult.success ? "Success" : "Failed")
print("Saga ID:", sagaResult.sagaId)
print("Steps:")
sagaResult.steps.forEach(s => print(`  - ${s.name}: ${s.status}`))
```

---

## Two-Phase Commit Pattern

### Implementing 2PC

```javascript
// Two-Phase Commit for distributed transaction simulation
function twoPhaseCommit(operations) {
  const txnId = "TXN-" + Date.now()
  const prepared = []
  
  // Phase 1: Prepare
  function preparePhase() {
    print("\n--- Phase 1: Prepare ---")
    
    for (const op of operations) {
      try {
        // Lock resources
        if (op.type === "debit") {
          const account = db.accounts.findOne({ _id: op.accountId })
          if (!account || account.balance < op.amount) {
            throw new Error(`Cannot prepare debit: ${op.accountId}`)
          }
          
          // Mark as prepared (lock)
          db.accounts.updateOne(
            { _id: op.accountId },
            {
              $set: {
                pendingTxn: txnId,
                pendingOp: "debit",
                pendingAmount: op.amount
              }
            }
          )
        } else if (op.type === "credit") {
          db.accounts.updateOne(
            { _id: op.accountId },
            {
              $set: {
                pendingTxn: txnId,
                pendingOp: "credit",
                pendingAmount: op.amount
              }
            }
          )
        }
        
        prepared.push({ ...op, status: "prepared" })
        print(`  ✓ Prepared: ${op.type} ${op.accountId}`)
        
      } catch (error) {
        print(`  ✗ Failed to prepare: ${op.accountId} - ${error.message}`)
        return false
      }
    }
    
    return true
  }
  
  // Phase 2: Commit
  function commitPhase() {
    print("\n--- Phase 2: Commit ---")
    
    for (const op of prepared) {
      const modifier = op.type === "debit" ? -1 : 1
      
      db.accounts.updateOne(
        { _id: op.accountId },
        {
          $inc: { balance: modifier * op.amount },
          $unset: { pendingTxn: "", pendingOp: "", pendingAmount: "" }
        }
      )
      
      print(`  ✓ Committed: ${op.type} ${op.accountId}`)
    }
    
    // Log completed transaction
    db.transactions.insertOne({
      _id: txnId,
      type: "2pc",
      operations: prepared,
      status: "committed",
      completedAt: new Date()
    })
    
    return true
  }
  
  // Rollback
  function rollback() {
    print("\n--- Rollback ---")
    
    for (const op of prepared) {
      db.accounts.updateOne(
        { _id: op.accountId },
        {
          $unset: { pendingTxn: "", pendingOp: "", pendingAmount: "" }
        }
      )
      
      print(`  ↩ Rolled back: ${op.accountId}`)
    }
    
    db.transactions.insertOne({
      _id: txnId,
      type: "2pc",
      operations: prepared,
      status: "aborted",
      abortedAt: new Date()
    })
  }
  
  // Execute 2PC
  print("=== Two-Phase Commit ===")
  print("Transaction ID:", txnId)
  
  if (preparePhase()) {
    if (commitPhase()) {
      return { success: true, txnId }
    }
  }
  
  rollback()
  return { success: false, txnId }
}

// Test 2PC
print("\nBefore 2PC:")
db.accounts.find({ _id: { $in: ["ACC001", "ACC003"] } }).forEach(a => {
  print(`  ${a._id}: $${a.balance}`)
})

const tpcResult = twoPhaseCommit([
  { type: "debit", accountId: "ACC001", amount: 300 },
  { type: "credit", accountId: "ACC003", amount: 300 }
])

print("\n2PC Result:", tpcResult.success ? "Committed" : "Aborted")

print("\nAfter 2PC:")
db.accounts.find({ _id: { $in: ["ACC001", "ACC003"] } }).forEach(a => {
  print(`  ${a._id}: $${a.balance}`)
})
```

---

## Retry Logic

### Transient Error Handling

```javascript
// Retry wrapper for transient errors
function withRetry(operation, maxRetries = 3, delayMs = 100) {
  let lastError = null
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return operation()
    } catch (error) {
      lastError = error
      
      // Check if retryable
      const isRetryable = 
        error.hasErrorLabel?.("TransientTransactionError") ||
        error.hasErrorLabel?.("UnknownTransactionCommitResult") ||
        error.code === 112 ||  // WriteConflict
        error.code === 251     // TransactionAborted
      
      if (!isRetryable || attempt === maxRetries) {
        throw error
      }
      
      print(`  Retry ${attempt}/${maxRetries} after ${delayMs}ms...`)
      sleep(delayMs)
      delayMs *= 2  // Exponential backoff
    }
  }
  
  throw lastError
}

// Transfer with retry
function transferWithRetry(from, to, amount) {
  return withRetry(() => {
    const session = db.getMongo().startSession()
    
    try {
      session.startTransaction()
      
      const source = db.accounts.findOne({ _id: from }, { session })
      if (!source || source.balance < amount) {
        throw new Error("Insufficient funds")
      }
      
      db.accounts.updateOne({ _id: from }, { $inc: { balance: -amount } }, { session })
      db.accounts.updateOne({ _id: to }, { $inc: { balance: amount } }, { session })
      
      session.commitTransaction()
      return { success: true }
      
    } catch (error) {
      session.abortTransaction()
      throw error
      
    } finally {
      session.endSession()
    }
  })
}
```

### Using withTransaction with Built-in Retry

```javascript
// withTransaction handles retries automatically
function safeTransfer(from, to, amount) {
  const session = db.getMongo().startSession()
  
  try {
    session.withTransaction(() => {
      const source = db.accounts.findOne({ _id: from }, { session })
      
      if (!source || source.balance < amount) {
        throw new Error("Insufficient funds")
      }
      
      db.accounts.updateOne(
        { _id: from },
        { $inc: { balance: -amount } },
        { session }
      )
      
      db.accounts.updateOne(
        { _id: to },
        { $inc: { balance: amount } },
        { session }
      )
    }, {
      readConcern: { level: "snapshot" },
      writeConcern: { w: "majority" },
      maxCommitTimeMS: 1000
    })
    
    return { success: true }
    
  } catch (error) {
    return { success: false, error: error.message }
    
  } finally {
    session.endSession()
  }
}
```

---

## Transaction Best Practices

### Design Guidelines

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Transaction Best Practices                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Keep Transactions Short                                        │
│     └── Minimize time between start and commit                     │
│                                                                     │
│  2. Limit Operations                                               │
│     └── Fewer operations = less lock contention                    │
│                                                                     │
│  3. Use Appropriate Isolation                                      │
│     └── snapshot for most cases                                    │
│                                                                     │
│  4. Handle Errors Properly                                         │
│     └── Always abort on error, use retry logic                     │
│                                                                     │
│  5. Consider Data Model                                            │
│     └── Embed when possible to avoid transactions                  │
│                                                                     │
│  6. Set Timeouts                                                   │
│     └── maxCommitTimeMS to prevent hanging                         │
│                                                                     │
│  7. Use Write Concern Majority                                     │
│     └── Ensures durability                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Anti-Patterns

```javascript
// ❌ DON'T: Long-running transaction
session.startTransaction()
// ... many operations over seconds/minutes
// Risk: Lock timeouts, aborts

// ❌ DON'T: Transaction for single document
session.startTransaction()
db.users.updateOne({ _id: 1 }, { $set: { name: "New" } }, { session })
session.commitTransaction()
// Single doc update is already atomic!

// ❌ DON'T: Ignore errors
try {
  session.startTransaction()
  // ... operations
  session.commitTransaction()
} catch (e) {
  // Forgot to abort!
}

// ✅ DO: Proper error handling
try {
  session.startTransaction()
  // ... operations
  session.commitTransaction()
} catch (e) {
  session.abortTransaction()
  throw e
} finally {
  session.endSession()
}
```

---

## Summary

### Transaction Patterns

| Pattern | Use Case |
|---------|----------|
| Money Transfer | Account-to-account transfers |
| Order Processing | E-commerce with inventory |
| Saga | Long-running distributed ops |
| Two-Phase Commit | Coordinated commits |

### Retry Strategies

| Approach | When to Use |
|----------|-------------|
| `withTransaction` | Automatic retry (recommended) |
| Manual retry | Custom retry logic needed |
| Exponential backoff | High contention scenarios |

### Best Practices Summary

| Practice | Reason |
|----------|--------|
| Short transactions | Reduce contention |
| Limited operations | Better performance |
| Proper error handling | Data consistency |
| Write concern majority | Durability |
| Timeout configuration | Prevent hanging |

### What's Next?

In the next chapter, we'll explore Transaction Error Handling in depth.

---

## Practice Questions

1. When should you use the Saga pattern vs regular transactions?
2. What are compensating transactions?
3. How does Two-Phase Commit work?
4. Why should transactions be kept short?
5. What's the difference between reserved and actual stock?
6. How do you handle transient transaction errors?
7. Why use withTransaction instead of manual commit?
8. What write concern is recommended for transactions?

---

## Hands-On Exercises

### Exercise 1: Complete Order System

```javascript
// Build a complete order system with all features

// Cleanup
db.orderSystem.accounts.drop()
db.orderSystem.products.drop()
db.orderSystem.orders.drop()
db.orderSystem.transactions.drop()

// Setup
db.orderSystem.accounts.insertMany([
  { _id: "CUST001", name: "Alice", balance: 2000 },
  { _id: "CUST002", name: "Bob", balance: 500 }
])

db.orderSystem.products.insertMany([
  { _id: "P001", name: "Item A", price: 100, stock: 10 },
  { _id: "P002", name: "Item B", price: 50, stock: 20 }
])

// Implement full order workflow
function orderWorkflow(customerId, items) {
  const session = db.getMongo().startSession()
  
  try {
    return session.withTransaction(() => {
      const orderId = "ORD" + Date.now()
      let total = 0
      
      // Validate and reserve
      for (const item of items) {
        const product = db.orderSystem.products.findOne({ _id: item.id }, { session })
        if (!product || product.stock < item.qty) {
          throw new Error(`Insufficient stock: ${item.id}`)
        }
        total += product.price * item.qty
        
        db.orderSystem.products.updateOne(
          { _id: item.id },
          { $inc: { stock: -item.qty } },
          { session }
        )
      }
      
      // Check balance
      const customer = db.orderSystem.accounts.findOne({ _id: customerId }, { session })
      if (!customer || customer.balance < total) {
        throw new Error("Insufficient funds")
      }
      
      // Charge customer
      db.orderSystem.accounts.updateOne(
        { _id: customerId },
        { $inc: { balance: -total } },
        { session }
      )
      
      // Create order
      db.orderSystem.orders.insertOne({
        _id: orderId,
        customer: customerId,
        items: items,
        total: total,
        status: "completed",
        timestamp: new Date()
      }, { session })
      
      return { orderId, total }
    })
    
  } finally {
    session.endSession()
  }
}

// Test
print("=== Order System Test ===\n")
print("Initial state:")
print("Accounts:", JSON.stringify(db.orderSystem.accounts.find().toArray()))
print("Products:", JSON.stringify(db.orderSystem.products.find().toArray()))

try {
  const result = orderWorkflow("CUST001", [
    { id: "P001", qty: 2 },
    { id: "P002", qty: 3 }
  ])
  print("\nOrder placed:", JSON.stringify(result))
} catch (e) {
  print("\nOrder failed:", e.message)
}

print("\nFinal state:")
print("Accounts:", JSON.stringify(db.orderSystem.accounts.find().toArray()))
print("Products:", JSON.stringify(db.orderSystem.products.find().toArray()))
```

---

[← Previous: Transaction Fundamentals](36-transaction-fundamentals.md) | [Next: Transaction Error Handling →](38-transaction-error-handling.md)
