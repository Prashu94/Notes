# Chapter 38: Transaction Error Handling

## Table of Contents
- [Transaction Errors Overview](#transaction-errors-overview)
- [Error Categories](#error-categories)
- [Transient Errors](#transient-errors)
- [Unknown Commit Errors](#unknown-commit-errors)
- [Retry Strategies](#retry-strategies)
- [Error Recovery Patterns](#error-recovery-patterns)
- [Monitoring and Debugging](#monitoring-and-debugging)
- [Summary](#summary)

---

## Transaction Errors Overview

Understanding and handling transaction errors is crucial for building robust applications. MongoDB transactions can fail for various reasons, and proper error handling ensures data consistency.

### Error Classification

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Transaction Error Types                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Transient Errors (Retryable)                                      │
│  ├── Write conflicts                                               │
│  ├── Network errors                                                │
│  ├── Primary election in progress                                  │
│  └── Temporary unavailability                                      │
│                                                                     │
│  Unknown Commit Result (Requires Check)                            │
│  ├── Commit timeout                                                │
│  ├── Network error during commit                                   │
│  └── Primary failover during commit                                │
│                                                                     │
│  Permanent Errors (Not Retryable)                                  │
│  ├── Validation errors                                             │
│  ├── Duplicate key errors                                          │
│  ├── Authentication failures                                       │
│  └── Invalid operations                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Setup test environment
db.accounts.drop()
db.accounts.insertMany([
  { _id: "A001", name: "Alice", balance: 1000 },
  { _id: "A002", name: "Bob", balance: 500 },
  { _id: "A003", name: "Charlie", balance: 750 }
])

db.transactionLog.drop()
```

---

## Error Categories

### Error Labels

```javascript
// MongoDB adds labels to help identify error types
// Key labels:
// - "TransientTransactionError" - Safe to retry whole transaction
// - "UnknownTransactionCommitResult" - Commit may have succeeded

// Check error labels
function hasErrorLabel(error, label) {
  return error.errorLabels && error.errorLabels.includes(label)
}

// Or use built-in method (if available)
// error.hasErrorLabel("TransientTransactionError")
```

### Common Error Codes

| Code | Name | Retryable | Description |
|------|------|-----------|-------------|
| 112 | WriteConflict | Yes | Another transaction modified the document |
| 251 | TransactionAborted | Yes | Transaction was aborted |
| 225 | TransactionExceededLifetimeLimitSeconds | No | Transaction too long |
| 11000 | DuplicateKey | No | Duplicate key violation |
| 121 | DocumentValidationFailure | No | Schema validation failed |

### Error Structure

```javascript
// MongoDB error structure
{
  "ok": 0,
  "errmsg": "Error message",
  "code": 112,
  "codeName": "WriteConflict",
  "errorLabels": ["TransientTransactionError"]
}
```

---

## Transient Errors

### Handling Write Conflicts

```javascript
// Write conflict occurs when two transactions modify the same document

function demonstrateWriteConflict() {
  // Session 1 starts transaction
  const session1 = db.getMongo().startSession()
  session1.startTransaction()
  
  // Session 2 starts transaction
  const session2 = db.getMongo().startSession()
  session2.startTransaction()
  
  try {
    // Both try to update same document
    db.accounts.updateOne(
      { _id: "A001" },
      { $inc: { balance: 100 } },
      { session: session1 }
    )
    
    // This will cause write conflict
    db.accounts.updateOne(
      { _id: "A001" },
      { $inc: { balance: 50 } },
      { session: session2 }
    )
    
    session1.commitTransaction()
    session2.commitTransaction()
    
  } catch (error) {
    print("Error:", error.codeName)
    print("Labels:", error.errorLabels)
    
    session1.abortTransaction()
    session2.abortTransaction()
    
  } finally {
    session1.endSession()
    session2.endSession()
  }
}
```

### Handling Transient Errors with Retry

```javascript
function transactionWithTransientRetry(operation, maxRetries = 3) {
  let retries = 0
  
  while (true) {
    const session = db.getMongo().startSession()
    
    try {
      session.startTransaction()
      
      const result = operation(session)
      
      session.commitTransaction()
      return { success: true, result, retries }
      
    } catch (error) {
      session.abortTransaction()
      
      // Check if transient error
      const isTransient = 
        error.hasErrorLabel?.("TransientTransactionError") ||
        error.errorLabels?.includes("TransientTransactionError") ||
        error.code === 112
      
      if (isTransient && retries < maxRetries) {
        retries++
        print(`Transient error, retry ${retries}/${maxRetries}...`)
        sleep(100 * retries)  // Backoff
        continue
      }
      
      return { success: false, error: error.message, code: error.code, retries }
      
    } finally {
      session.endSession()
    }
  }
}

// Test
const result = transactionWithTransientRetry((session) => {
  const account = db.accounts.findOne({ _id: "A001" }, { session })
  
  if (account.balance < 100) {
    throw new Error("Insufficient funds")
  }
  
  db.accounts.updateOne(
    { _id: "A001" },
    { $inc: { balance: -100 } },
    { session }
  )
  
  db.accounts.updateOne(
    { _id: "A002" },
    { $inc: { balance: 100 } },
    { session }
  )
  
  return "Transfer completed"
})

print("Result:", JSON.stringify(result))
```

---

## Unknown Commit Errors

### Understanding Unknown Commit Result

```javascript
// When commit fails with UnknownTransactionCommitResult:
// - Transaction may have been committed
// - Transaction may have been aborted
// - Must check or use idempotent operations

function handleUnknownCommitResult() {
  const session = db.getMongo().startSession()
  const txnId = ObjectId()
  
  try {
    session.startTransaction()
    
    // Use transaction ID for idempotency
    const existing = db.transactionLog.findOne({ _id: txnId }, { session })
    if (existing) {
      print("Transaction already processed")
      session.abortTransaction()
      return { success: true, status: "duplicate" }
    }
    
    // Perform operations
    db.accounts.updateOne(
      { _id: "A001" },
      { $inc: { balance: -50 } },
      { session }
    )
    
    // Log transaction
    db.transactionLog.insertOne({
      _id: txnId,
      type: "debit",
      account: "A001",
      amount: 50,
      timestamp: new Date()
    }, { session })
    
    session.commitTransaction()
    return { success: true, txnId }
    
  } catch (error) {
    const isUnknownResult = 
      error.hasErrorLabel?.("UnknownTransactionCommitResult") ||
      error.errorLabels?.includes("UnknownTransactionCommitResult")
    
    if (isUnknownResult) {
      print("Commit result unknown, checking...")
      
      // Check if transaction was logged
      const logged = db.transactionLog.findOne({ _id: txnId })
      if (logged) {
        return { success: true, status: "committed_verified" }
      }
      return { success: false, status: "commit_unknown" }
    }
    
    session.abortTransaction()
    return { success: false, error: error.message }
    
  } finally {
    session.endSession()
  }
}
```

### Retrying Unknown Commit

```javascript
function commitWithRetry(session, maxRetries = 3) {
  let retries = 0
  
  while (retries < maxRetries) {
    try {
      session.commitTransaction()
      return { committed: true, retries }
      
    } catch (error) {
      const isUnknown = 
        error.hasErrorLabel?.("UnknownTransactionCommitResult") ||
        error.errorLabels?.includes("UnknownTransactionCommitResult")
      
      if (isUnknown) {
        retries++
        print(`Commit unknown, retry ${retries}/${maxRetries}...`)
        sleep(100 * retries)
        continue
      }
      
      // Not retriable, throw
      throw error
    }
  }
  
  return { committed: false, status: "max_retries_exceeded" }
}
```

---

## Retry Strategies

### Comprehensive Retry Function

```javascript
function executeTransaction(operationFn, options = {}) {
  const {
    maxTransactionRetries = 3,
    maxCommitRetries = 3,
    backoffMs = 100,
    maxBackoffMs = 5000,
    transactionOptions = {}
  } = options
  
  let transactionRetries = 0
  
  while (transactionRetries < maxTransactionRetries) {
    const session = db.getMongo().startSession()
    
    try {
      session.startTransaction({
        readConcern: { level: "snapshot" },
        writeConcern: { w: "majority" },
        ...transactionOptions
      })
      
      // Execute operation
      const result = operationFn(session)
      
      // Commit with retry
      let commitRetries = 0
      while (commitRetries < maxCommitRetries) {
        try {
          session.commitTransaction()
          
          return {
            success: true,
            result,
            transactionRetries,
            commitRetries
          }
          
        } catch (commitError) {
          const isUnknown = commitError.errorLabels?.includes("UnknownTransactionCommitResult")
          
          if (isUnknown && commitRetries < maxCommitRetries - 1) {
            commitRetries++
            const delay = Math.min(backoffMs * Math.pow(2, commitRetries), maxBackoffMs)
            print(`Commit retry ${commitRetries}/${maxCommitRetries} after ${delay}ms`)
            sleep(delay)
            continue
          }
          
          throw commitError
        }
      }
      
    } catch (error) {
      const isTransient = error.errorLabels?.includes("TransientTransactionError")
      
      session.abortTransaction()
      
      if (isTransient && transactionRetries < maxTransactionRetries - 1) {
        transactionRetries++
        const delay = Math.min(backoffMs * Math.pow(2, transactionRetries), maxBackoffMs)
        print(`Transaction retry ${transactionRetries}/${maxTransactionRetries} after ${delay}ms`)
        sleep(delay)
        continue
      }
      
      return {
        success: false,
        error: error.message,
        code: error.code,
        transactionRetries
      }
      
    } finally {
      session.endSession()
    }
  }
  
  return {
    success: false,
    error: "Max retries exceeded",
    transactionRetries
  }
}

// Usage
const txnResult = executeTransaction((session) => {
  db.accounts.updateOne(
    { _id: "A001" },
    { $inc: { balance: -25 } },
    { session }
  )
  
  db.accounts.updateOne(
    { _id: "A003" },
    { $inc: { balance: 25 } },
    { session }
  )
  
  return "Transfer of $25 from A001 to A003"
})

print("Transaction result:", JSON.stringify(txnResult))
```

### Using withTransaction (Recommended)

```javascript
// withTransaction handles retries automatically
function safeTransaction(operationFn, options = {}) {
  const session = db.getMongo().startSession()
  
  try {
    const result = session.withTransaction(() => {
      return operationFn(session)
    }, {
      readConcern: { level: "snapshot" },
      writeConcern: { w: "majority" },
      maxCommitTimeMS: 5000,
      ...options
    })
    
    return { success: true, result }
    
  } catch (error) {
    return {
      success: false,
      error: error.message,
      code: error.code
    }
    
  } finally {
    session.endSession()
  }
}

// Test
const safe = safeTransaction((session) => {
  db.accounts.updateOne(
    { _id: "A002" },
    { $inc: { balance: 100 } },
    { session }
  )
  return "Credited A002"
})

print("Safe transaction:", JSON.stringify(safe))
```

---

## Error Recovery Patterns

### Idempotent Operations

```javascript
// Make operations idempotent using unique identifiers
function idempotentTransfer(transferId, from, to, amount) {
  const session = db.getMongo().startSession()
  
  try {
    return session.withTransaction(() => {
      // Check if already processed
      const existing = db.transfers.findOne({ _id: transferId }, { session })
      if (existing) {
        return { status: "already_processed", transfer: existing }
      }
      
      // Validate
      const source = db.accounts.findOne({ _id: from }, { session })
      if (!source || source.balance < amount) {
        throw new Error("Insufficient funds")
      }
      
      // Execute
      db.accounts.updateOne({ _id: from }, { $inc: { balance: -amount } }, { session })
      db.accounts.updateOne({ _id: to }, { $inc: { balance: amount } }, { session })
      
      // Record
      const transfer = {
        _id: transferId,
        from, to, amount,
        status: "completed",
        timestamp: new Date()
      }
      db.transfers.insertOne(transfer, { session })
      
      return { status: "completed", transfer }
    })
    
  } finally {
    session.endSession()
  }
}

// Can safely retry without duplicate effects
const transferId = "TXN-" + Date.now()

// First call
print("First call:", JSON.stringify(idempotentTransfer(transferId, "A001", "A002", 50)))

// Duplicate call (safe)
print("Duplicate:", JSON.stringify(idempotentTransfer(transferId, "A001", "A002", 50)))
```

### Compensation on Failure

```javascript
function transactionWithCompensation(steps) {
  const completed = []
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    for (const step of steps) {
      try {
        const result = step.execute(session)
        completed.push({ step: step.name, result, compensate: step.compensate })
      } catch (error) {
        throw new Error(`Step ${step.name} failed: ${error.message}`)
      }
    }
    
    session.commitTransaction()
    return { success: true, completed: completed.map(c => c.step) }
    
  } catch (error) {
    session.abortTransaction()
    
    // Run compensations in reverse order
    print("Running compensations...")
    const compensated = []
    
    for (let i = completed.length - 1; i >= 0; i--) {
      const { step, compensate } = completed[i]
      try {
        compensate()
        compensated.push(step)
        print(`  Compensated: ${step}`)
      } catch (compError) {
        print(`  Compensation failed for ${step}: ${compError.message}`)
      }
    }
    
    return {
      success: false,
      error: error.message,
      compensated
    }
    
  } finally {
    session.endSession()
  }
}

// Example usage
const result = transactionWithCompensation([
  {
    name: "reserve_inventory",
    execute: (session) => {
      db.products.updateOne(
        { _id: "P001", stock: { $gte: 5 } },
        { $inc: { stock: -5, reserved: 5 } },
        { session }
      )
      return "Reserved 5 units"
    },
    compensate: () => {
      db.products.updateOne(
        { _id: "P001" },
        { $inc: { stock: 5, reserved: -5 } }
      )
    }
  },
  {
    name: "charge_payment",
    execute: (session) => {
      const account = db.accounts.findOne({ _id: "A001" }, { session })
      if (account.balance < 500) {
        throw new Error("Insufficient funds")
      }
      db.accounts.updateOne(
        { _id: "A001" },
        { $inc: { balance: -500 } },
        { session }
      )
      return "Charged $500"
    },
    compensate: () => {
      db.accounts.updateOne(
        { _id: "A001" },
        { $inc: { balance: 500 } }
      )
    }
  }
])
```

### Dead Letter Queue

```javascript
// Store failed transactions for manual review
function executeWithDLQ(operationFn, context) {
  const session = db.getMongo().startSession()
  const txnId = ObjectId()
  
  try {
    session.startTransaction()
    
    const result = operationFn(session)
    
    session.commitTransaction()
    return { success: true, result }
    
  } catch (error) {
    session.abortTransaction()
    
    // Store in dead letter queue
    db.deadLetterQueue.insertOne({
      _id: txnId,
      type: "failed_transaction",
      context: context,
      error: {
        message: error.message,
        code: error.code,
        labels: error.errorLabels
      },
      timestamp: new Date(),
      status: "pending_review",
      retryCount: 0
    })
    
    return {
      success: false,
      error: error.message,
      dlqId: txnId
    }
    
  } finally {
    session.endSession()
  }
}

// Process DLQ items
function processDLQ(processor) {
  const items = db.deadLetterQueue.find({ status: "pending_review" }).toArray()
  
  for (const item of items) {
    print(`Processing DLQ item: ${item._id}`)
    
    try {
      const result = processor(item)
      
      db.deadLetterQueue.updateOne(
        { _id: item._id },
        {
          $set: {
            status: "resolved",
            resolution: result,
            resolvedAt: new Date()
          }
        }
      )
      
    } catch (error) {
      db.deadLetterQueue.updateOne(
        { _id: item._id },
        {
          $inc: { retryCount: 1 },
          $set: { lastError: error.message }
        }
      )
    }
  }
}
```

---

## Monitoring and Debugging

### Transaction Metrics

```javascript
// Log transaction metrics
function instrumentedTransaction(name, operationFn) {
  const session = db.getMongo().startSession()
  const startTime = new Date()
  const metrics = {
    name,
    startTime,
    operations: 0,
    retries: 0
  }
  
  try {
    session.startTransaction()
    
    // Wrap operation with counting
    const wrappedSession = {
      ...session,
      trackOperation: () => metrics.operations++
    }
    
    const result = operationFn(session, wrappedSession.trackOperation)
    
    session.commitTransaction()
    
    metrics.endTime = new Date()
    metrics.duration = metrics.endTime - metrics.startTime
    metrics.status = "committed"
    
    return { success: true, result, metrics }
    
  } catch (error) {
    session.abortTransaction()
    
    metrics.endTime = new Date()
    metrics.duration = metrics.endTime - metrics.startTime
    metrics.status = "aborted"
    metrics.error = error.message
    
    return { success: false, error: error.message, metrics }
    
  } finally {
    session.endSession()
    
    // Log metrics
    db.transactionMetrics.insertOne(metrics)
  }
}

// Usage
const instrumented = instrumentedTransaction("transfer", (session, track) => {
  track()
  db.accounts.updateOne({ _id: "A001" }, { $inc: { balance: -10 } }, { session })
  
  track()
  db.accounts.updateOne({ _id: "A002" }, { $inc: { balance: 10 } }, { session })
  
  return "Transfer completed"
})

print("Instrumented result:", JSON.stringify(instrumented, null, 2))
```

### Debugging Transactions

```javascript
// Debug helper
function debugTransaction(operationFn) {
  const session = db.getMongo().startSession()
  const debug = {
    sessionId: session.getSessionId(),
    operations: [],
    timeline: []
  }
  
  function logEvent(event, details = {}) {
    debug.timeline.push({
      timestamp: new Date(),
      event,
      ...details
    })
    print(`[${event}]`, JSON.stringify(details))
  }
  
  try {
    logEvent("session_started")
    
    session.startTransaction()
    logEvent("transaction_started")
    
    const result = operationFn(session, (opName, opDetails) => {
      debug.operations.push({ name: opName, ...opDetails })
      logEvent("operation", { name: opName })
    })
    
    logEvent("committing")
    session.commitTransaction()
    logEvent("committed")
    
    return { success: true, result, debug }
    
  } catch (error) {
    logEvent("error", { message: error.message, code: error.code })
    session.abortTransaction()
    logEvent("aborted")
    
    return { success: false, error: error.message, debug }
    
  } finally {
    session.endSession()
    logEvent("session_ended")
  }
}

// Test debugging
print("\n=== Debug Transaction ===\n")
debugTransaction((session, log) => {
  log("find_account", { id: "A001" })
  const account = db.accounts.findOne({ _id: "A001" }, { session })
  
  log("update_account", { id: "A001", operation: "debit" })
  db.accounts.updateOne({ _id: "A001" }, { $inc: { balance: -5 } }, { session })
  
  return "Debug test"
})
```

---

## Summary

### Error Types and Handling

| Error Type | Label | Action |
|------------|-------|--------|
| Transient | TransientTransactionError | Retry entire transaction |
| Unknown Commit | UnknownTransactionCommitResult | Retry commit or verify |
| Permanent | None | Don't retry, handle error |

### Retry Strategy

| Scenario | Strategy |
|----------|----------|
| Write conflict | Retry with backoff |
| Network error | Retry with backoff |
| Unknown commit | Retry commit only |
| Validation error | Don't retry |
| Duplicate key | Don't retry |

### Best Practices

| Practice | Description |
|----------|-------------|
| Use withTransaction | Built-in retry handling |
| Idempotent operations | Safe to retry |
| Dead letter queue | Handle persistent failures |
| Metrics and logging | Monitor transaction health |
| Exponential backoff | Reduce contention |

### What's Next?

In the next chapter, we'll begin Part 8: Replication, starting with Replica Set Architecture.

---

## Practice Questions

1. What does TransientTransactionError indicate?
2. When should you retry only the commit vs the entire transaction?
3. How do you make transactions idempotent?
4. What is a dead letter queue used for?
5. Why use exponential backoff?
6. What's the advantage of withTransaction?
7. How do you verify if a commit succeeded after UnknownTransactionCommitResult?
8. What metrics should you track for transactions?

---

## Hands-On Exercises

### Exercise 1: Error Handling

```javascript
// Practice different error scenarios

// Setup
db.errorTest.drop()
db.errorTest.insertMany([
  { _id: 1, value: 100, version: 1 },
  { _id: 2, value: 200, version: 1 }
])
db.errorTest.createIndex({ uniqueField: 1 }, { unique: true, sparse: true })

// Test 1: Insufficient balance error
print("Test 1: Business logic error")
const session1 = db.getMongo().startSession()
try {
  session1.startTransaction()
  
  const doc = db.errorTest.findOne({ _id: 1 }, { session: session1 })
  if (doc.value < 1000) {
    throw new Error("Insufficient value")
  }
  
  session1.commitTransaction()
  print("  Committed")
} catch (e) {
  session1.abortTransaction()
  print("  Error:", e.message)
} finally {
  session1.endSession()
}

// Test 2: Duplicate key error
print("\nTest 2: Duplicate key error")
const session2 = db.getMongo().startSession()
try {
  session2.startTransaction()
  
  db.errorTest.updateOne({ _id: 1 }, { $set: { uniqueField: "unique1" } }, { session: session2 })
  db.errorTest.updateOne({ _id: 2 }, { $set: { uniqueField: "unique1" } }, { session: session2 })  // Duplicate!
  
  session2.commitTransaction()
  print("  Committed")
} catch (e) {
  session2.abortTransaction()
  print("  Error:", e.codeName || e.message)
  print("  Code:", e.code)
} finally {
  session2.endSession()
}
```

### Exercise 2: Retry Implementation

```javascript
// Implement and test retry logic

function retryableTransfer(from, to, amount, maxRetries = 3) {
  let attempt = 0
  
  while (attempt < maxRetries) {
    attempt++
    print(`\nAttempt ${attempt}/${maxRetries}`)
    
    const session = db.getMongo().startSession()
    
    try {
      session.startTransaction()
      
      // Simulate occasional transient error
      if (attempt < 2 && Math.random() < 0.5) {
        const error = new Error("Simulated transient error")
        error.errorLabels = ["TransientTransactionError"]
        throw error
      }
      
      const source = db.accounts.findOne({ _id: from }, { session })
      if (!source || source.balance < amount) {
        throw new Error("Insufficient funds")
      }
      
      db.accounts.updateOne({ _id: from }, { $inc: { balance: -amount } }, { session })
      db.accounts.updateOne({ _id: to }, { $inc: { balance: amount } }, { session })
      
      session.commitTransaction()
      print("  Committed successfully!")
      return { success: true, attempts: attempt }
      
    } catch (error) {
      session.abortTransaction()
      
      const isTransient = error.errorLabels?.includes("TransientTransactionError")
      print(`  Error: ${error.message}`)
      print(`  Transient: ${isTransient}`)
      
      if (!isTransient) {
        return { success: false, error: error.message, attempts: attempt }
      }
      
      if (attempt < maxRetries) {
        print(`  Retrying in ${100 * attempt}ms...`)
        sleep(100 * attempt)
      }
      
    } finally {
      session.endSession()
    }
  }
  
  return { success: false, error: "Max retries exceeded", attempts: attempt }
}

// Test
print("=== Retry Test ===")
const result = retryableTransfer("A001", "A002", 15)
print("\nFinal result:", JSON.stringify(result))
```

### Exercise 3: Idempotent Operations

```javascript
// Implement idempotent operations

db.idempotentTest.drop()
db.idempotentTest.insertOne({ _id: "counter", value: 0 })
db.processedOps.drop()

function idempotentIncrement(operationId, amount) {
  const session = db.getMongo().startSession()
  
  try {
    return session.withTransaction(() => {
      // Check if already processed
      const existing = db.processedOps.findOne({ _id: operationId }, { session })
      if (existing) {
        return { status: "duplicate", previousResult: existing.result }
      }
      
      // Perform operation
      const before = db.idempotentTest.findOne({ _id: "counter" }, { session })
      
      db.idempotentTest.updateOne(
        { _id: "counter" },
        { $inc: { value: amount } },
        { session }
      )
      
      const after = db.idempotentTest.findOne({ _id: "counter" }, { session })
      
      // Record operation
      const result = { before: before.value, after: after.value, amount }
      db.processedOps.insertOne({
        _id: operationId,
        result,
        timestamp: new Date()
      }, { session })
      
      return { status: "processed", result }
    })
    
  } finally {
    session.endSession()
  }
}

// Test idempotency
print("=== Idempotency Test ===")

const opId = "OP-" + Date.now()

// First call
print("\nFirst call:")
printjson(idempotentIncrement(opId, 10))

// Duplicate call (should return previous result)
print("\nDuplicate call:")
printjson(idempotentIncrement(opId, 10))

// New operation
print("\nNew operation:")
printjson(idempotentIncrement("OP-" + (Date.now() + 1), 5))

// Check final state
print("\nFinal counter value:")
printjson(db.idempotentTest.findOne({ _id: "counter" }))
```

### Exercise 4: Transaction Monitoring

```javascript
// Build a transaction monitoring system

db.txnMonitor.drop()

function monitoredTransaction(name, operationFn) {
  const monitor = {
    id: ObjectId(),
    name,
    startTime: new Date(),
    operations: [],
    status: "started"
  }
  
  // Save initial state
  db.txnMonitor.insertOne(monitor)
  
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction()
    
    // Wrapper to track operations
    const tracker = {
      record: (opName, collection, filter) => {
        const op = {
          name: opName,
          collection,
          filter: JSON.stringify(filter),
          timestamp: new Date()
        }
        monitor.operations.push(op)
        db.txnMonitor.updateOne(
          { id: monitor.id },
          { $push: { operations: op } }
        )
      }
    }
    
    const result = operationFn(session, tracker)
    
    session.commitTransaction()
    
    // Update monitor
    db.txnMonitor.updateOne(
      { id: monitor.id },
      {
        $set: {
          status: "committed",
          endTime: new Date(),
          duration: new Date() - monitor.startTime,
          result: result
        }
      }
    )
    
    return { success: true, monitorId: monitor.id, result }
    
  } catch (error) {
    session.abortTransaction()
    
    db.txnMonitor.updateOne(
      { id: monitor.id },
      {
        $set: {
          status: "aborted",
          endTime: new Date(),
          duration: new Date() - monitor.startTime,
          error: error.message
        }
      }
    )
    
    return { success: false, monitorId: monitor.id, error: error.message }
    
  } finally {
    session.endSession()
  }
}

// Test monitoring
print("=== Transaction Monitoring ===")

const monResult = monitoredTransaction("transfer", (session, tracker) => {
  tracker.record("findOne", "accounts", { _id: "A001" })
  const account = db.accounts.findOne({ _id: "A001" }, { session })
  
  tracker.record("updateOne", "accounts", { _id: "A001" })
  db.accounts.updateOne({ _id: "A001" }, { $inc: { balance: -5 } }, { session })
  
  tracker.record("updateOne", "accounts", { _id: "A002" })
  db.accounts.updateOne({ _id: "A002" }, { $inc: { balance: 5 } }, { session })
  
  return "Transfer complete"
})

print("\nTransaction result:", monResult.success ? "Success" : "Failed")
print("\nMonitor record:")
printjson(db.txnMonitor.findOne({ id: monResult.monitorId }))
```

---

[← Previous: Multi-Document Transaction Patterns](37-multi-document-transactions.md) | [Next: Replica Set Architecture →](39-replica-set-architecture.md)
