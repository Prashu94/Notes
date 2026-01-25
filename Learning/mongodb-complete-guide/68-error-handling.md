# Chapter 68: Error Handling

## Table of Contents
- [Error Types Overview](#error-types-overview)
- [Common MongoDB Errors](#common-mongodb-errors)
- [Error Handling Strategies](#error-handling-strategies)
- [Retry Patterns](#retry-patterns)
- [Application-Level Handling](#application-level-handling)
- [Logging and Monitoring](#logging-and-monitoring)
- [Summary](#summary)

---

## Error Types Overview

### MongoDB Error Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Error Types                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      MongoError (Base)                       │   │
│  │                            │                                 │   │
│  │         ┌──────────────────┼──────────────────┐             │   │
│  │         │                  │                  │             │   │
│  │         ▼                  ▼                  ▼             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │MongoServer   │  │MongoNetwork  │  │MongoDriver   │      │   │
│  │  │Error         │  │Error         │  │Error         │      │   │
│  │  │              │  │              │  │              │      │   │
│  │  │• Write errors│  │• Timeout     │  │• Invalid     │      │   │
│  │  │• Query errors│  │• Connection  │  │  arguments   │      │   │
│  │  │• Auth errors │  │  refused     │  │• Config      │      │   │
│  │  │• Validation  │  │• DNS failure │  │  errors      │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  │                                                              │   │
│  │  Special Error Types:                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │MongoBulk     │  │MongoWrite    │  │MongoTopology │      │   │
│  │  │WriteError    │  │ConcernError  │  │ClosedError   │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Error Code Categories

| Code Range | Category | Examples |
|------------|----------|----------|
| 1-99 | General errors | InternalError, BadValue |
| 100-199 | Network errors | NetworkTimeout, HostNotFound |
| 200-299 | Write concern errors | WriteConcernFailed |
| 11000-11999 | Duplicate key | DuplicateKey, DuplicateKeyOnUpdate |
| 121 | Document validation | DocumentValidationFailure |
| 13-18 | Authorization | Unauthorized, AuthenticationFailed |
| 50 | Exceeded limits | ExceededTimeLimit |

---

## Common MongoDB Errors

### Duplicate Key Error (11000)

```javascript
// Handling duplicate key errors
async function createUser(userData) {
  try {
    const result = await db.collection('users').insertOne(userData)
    return { success: true, id: result.insertedId }
  } catch (error) {
    if (error.code === 11000) {
      // Extract the duplicate field
      const field = extractDuplicateKeyField(error)
      return {
        success: false,
        error: 'DUPLICATE_KEY',
        message: `A user with this ${field} already exists`,
        field: field
      }
    }
    throw error
  }
}

function extractDuplicateKeyField(error) {
  // Error message format: "E11000 duplicate key error collection: db.collection index: field_1 dup key: { field: value }"
  const match = error.message.match(/index: (\w+)_/)
  if (match) return match[1]
  
  // Alternative: check keyPattern
  if (error.keyPattern) {
    return Object.keys(error.keyPattern)[0]
  }
  
  return 'unknown'
}

// Upsert pattern to avoid duplicate key errors
async function upsertUser(email, userData) {
  return await db.collection('users').updateOne(
    { email: email },
    { 
      $set: userData,
      $setOnInsert: { createdAt: new Date() }
    },
    { upsert: true }
  )
}
```

### Document Validation Error (121)

```javascript
// Handle validation errors
async function createOrder(orderData) {
  try {
    const result = await db.collection('orders').insertOne(orderData)
    return { success: true, id: result.insertedId }
  } catch (error) {
    if (error.code === 121) {
      // Document failed schema validation
      const validationErrors = parseValidationError(error)
      return {
        success: false,
        error: 'VALIDATION_ERROR',
        message: 'Order data failed validation',
        details: validationErrors
      }
    }
    throw error
  }
}

function parseValidationError(error) {
  // Extract validation details from error
  const details = error.errInfo?.details
  
  if (!details) {
    return [{ message: error.message }]
  }
  
  // Parse JSON Schema validation errors
  const errors = []
  
  if (details.schemaRulesNotSatisfied) {
    details.schemaRulesNotSatisfied.forEach(rule => {
      if (rule.missingProperties) {
        rule.missingProperties.forEach(prop => {
          errors.push({
            field: prop,
            message: `Missing required field: ${prop}`
          })
        })
      }
      if (rule.propertiesNotSatisfied) {
        rule.propertiesNotSatisfied.forEach(prop => {
          errors.push({
            field: prop.propertyName,
            message: prop.description || 'Validation failed'
          })
        })
      }
    })
  }
  
  return errors
}
```

### Network and Timeout Errors

```javascript
const { MongoNetworkError, MongoServerSelectionError } = require('mongodb')

async function executeWithNetworkHandling(operation) {
  try {
    return await operation()
  } catch (error) {
    if (error instanceof MongoNetworkError) {
      // Network-related error
      console.error('Network error:', error.message)
      
      if (error.message.includes('ECONNREFUSED')) {
        throw new Error('Database connection refused. Is MongoDB running?')
      }
      
      if (error.message.includes('ETIMEDOUT')) {
        throw new Error('Database connection timed out. Check network.')
      }
      
      throw new Error('Network error communicating with database')
    }
    
    if (error instanceof MongoServerSelectionError) {
      // Server selection timeout
      console.error('Server selection error:', error.message)
      throw new Error('Unable to select database server. Check replica set status.')
    }
    
    throw error
  }
}
```

### Write Concern Errors

```javascript
const { MongoWriteConcernError } = require('mongodb')

async function writeWithConcern(collection, document) {
  try {
    return await collection.insertOne(document, {
      writeConcern: { w: 'majority', wtimeout: 5000 }
    })
  } catch (error) {
    if (error instanceof MongoWriteConcernError) {
      // Write succeeded on primary but failed to replicate
      console.error('Write concern error:', error.message)
      
      // The write may have partially succeeded
      return {
        success: 'partial',
        insertedId: error.result?.insertedId,
        message: 'Write may not be fully replicated'
      }
    }
    throw error
  }
}
```

### Bulk Write Errors

```javascript
const { MongoBulkWriteError } = require('mongodb')

async function bulkInsert(collection, documents) {
  try {
    const result = await collection.insertMany(documents, { ordered: false })
    return {
      success: true,
      insertedCount: result.insertedCount,
      insertedIds: result.insertedIds
    }
  } catch (error) {
    if (error instanceof MongoBulkWriteError) {
      // Some operations succeeded, some failed
      const writeErrors = error.writeErrors || []
      const successCount = error.result?.nInserted || 0
      
      // Categorize errors
      const duplicates = writeErrors.filter(e => e.code === 11000)
      const validationErrors = writeErrors.filter(e => e.code === 121)
      const otherErrors = writeErrors.filter(e => ![11000, 121].includes(e.code))
      
      return {
        success: 'partial',
        insertedCount: successCount,
        failedCount: writeErrors.length,
        errors: {
          duplicates: duplicates.map(e => ({
            index: e.index,
            message: 'Duplicate key'
          })),
          validation: validationErrors.map(e => ({
            index: e.index,
            message: e.errmsg
          })),
          other: otherErrors.map(e => ({
            index: e.index,
            code: e.code,
            message: e.errmsg
          }))
        }
      }
    }
    throw error
  }
}
```

---

## Error Handling Strategies

### Centralized Error Handler

```javascript
// Centralized MongoDB error handling
class MongoDBErrorHandler {
  static handle(error, context = {}) {
    const errorInfo = this.categorize(error)
    
    // Log error with context
    this.log(errorInfo, context)
    
    // Return user-friendly error
    return this.toUserError(errorInfo)
  }
  
  static categorize(error) {
    // Network errors
    if (error.name === 'MongoNetworkError') {
      return {
        category: 'NETWORK',
        code: error.code,
        message: error.message,
        retryable: true,
        severity: 'high'
      }
    }
    
    // Server selection errors
    if (error.name === 'MongoServerSelectionError') {
      return {
        category: 'CONNECTION',
        code: 'SERVER_SELECTION',
        message: error.message,
        retryable: true,
        severity: 'high'
      }
    }
    
    // Server errors
    if (error.name === 'MongoServerError') {
      return this.categorizeServerError(error)
    }
    
    // Bulk write errors
    if (error.name === 'MongoBulkWriteError') {
      return {
        category: 'BULK_WRITE',
        code: 'BULK_ERROR',
        message: error.message,
        writeErrors: error.writeErrors,
        retryable: false,
        severity: 'medium'
      }
    }
    
    // Unknown error
    return {
      category: 'UNKNOWN',
      code: error.code || 'UNKNOWN',
      message: error.message,
      retryable: false,
      severity: 'high'
    }
  }
  
  static categorizeServerError(error) {
    switch (error.code) {
      case 11000:
        return {
          category: 'DUPLICATE_KEY',
          code: 11000,
          message: error.message,
          keyPattern: error.keyPattern,
          retryable: false,
          severity: 'low'
        }
      
      case 121:
        return {
          category: 'VALIDATION',
          code: 121,
          message: error.message,
          details: error.errInfo,
          retryable: false,
          severity: 'low'
        }
      
      case 13:
      case 18:
        return {
          category: 'AUTHENTICATION',
          code: error.code,
          message: 'Authentication failed',
          retryable: false,
          severity: 'high'
        }
      
      case 50:
        return {
          category: 'TIMEOUT',
          code: 50,
          message: 'Operation exceeded time limit',
          retryable: true,
          severity: 'medium'
        }
      
      default:
        return {
          category: 'SERVER_ERROR',
          code: error.code,
          message: error.message,
          retryable: false,
          severity: 'medium'
        }
    }
  }
  
  static log(errorInfo, context) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      category: errorInfo.category,
      code: errorInfo.code,
      message: errorInfo.message,
      severity: errorInfo.severity,
      context: context
    }
    
    if (errorInfo.severity === 'high') {
      console.error('MongoDB Error:', JSON.stringify(logEntry))
    } else {
      console.warn('MongoDB Error:', JSON.stringify(logEntry))
    }
  }
  
  static toUserError(errorInfo) {
    const userMessages = {
      NETWORK: 'Unable to connect to the database. Please try again.',
      CONNECTION: 'Database connection issue. Please try again later.',
      DUPLICATE_KEY: 'This record already exists.',
      VALIDATION: 'The data provided is invalid.',
      AUTHENTICATION: 'Database authentication failed.',
      TIMEOUT: 'The operation took too long. Please try again.',
      BULK_WRITE: 'Some records could not be processed.',
      SERVER_ERROR: 'A database error occurred.',
      UNKNOWN: 'An unexpected error occurred.'
    }
    
    return {
      error: true,
      code: errorInfo.code,
      message: userMessages[errorInfo.category] || userMessages.UNKNOWN,
      retryable: errorInfo.retryable
    }
  }
}

// Usage
try {
  await db.collection('users').insertOne(userData)
} catch (error) {
  const result = MongoDBErrorHandler.handle(error, {
    operation: 'createUser',
    collection: 'users'
  })
  
  if (result.retryable) {
    // Could retry the operation
  }
  
  return result
}
```

### Error Wrapper Pattern

```javascript
// Wrapper for async operations with error handling
function withErrorHandling(operation, options = {}) {
  const {
    context = {},
    defaultValue = null,
    rethrow = true
  } = options
  
  return async (...args) => {
    try {
      return await operation(...args)
    } catch (error) {
      const handled = MongoDBErrorHandler.handle(error, {
        ...context,
        args: args.map(a => typeof a === 'object' ? '[object]' : a)
      })
      
      if (rethrow) {
        const appError = new Error(handled.message)
        appError.code = handled.code
        appError.retryable = handled.retryable
        throw appError
      }
      
      return defaultValue
    }
  }
}

// Usage
const safeInsert = withErrorHandling(
  async (data) => await db.collection('users').insertOne(data),
  { context: { operation: 'insertUser' } }
)

const result = await safeInsert({ name: 'John' })
```

---

## Retry Patterns

### Exponential Backoff Retry

```javascript
class RetryHandler {
  constructor(options = {}) {
    this.options = {
      maxRetries: 3,
      initialDelayMs: 100,
      maxDelayMs: 5000,
      backoffFactor: 2,
      jitter: true,
      retryableErrors: ['NETWORK', 'CONNECTION', 'TIMEOUT'],
      ...options
    }
  }
  
  async execute(operation) {
    let lastError
    let delay = this.options.initialDelayMs
    
    for (let attempt = 1; attempt <= this.options.maxRetries + 1; attempt++) {
      try {
        return await operation()
      } catch (error) {
        lastError = error
        const errorInfo = MongoDBErrorHandler.categorize(error)
        
        // Check if error is retryable
        if (!this.isRetryable(errorInfo) || attempt > this.options.maxRetries) {
          throw error
        }
        
        // Calculate delay with jitter
        const actualDelay = this.options.jitter 
          ? delay * (0.5 + Math.random())
          : delay
        
        console.log(`Retry attempt ${attempt}/${this.options.maxRetries} after ${Math.round(actualDelay)}ms`)
        
        await this.sleep(actualDelay)
        
        // Increase delay for next attempt
        delay = Math.min(delay * this.options.backoffFactor, this.options.maxDelayMs)
      }
    }
    
    throw lastError
  }
  
  isRetryable(errorInfo) {
    return errorInfo.retryable || 
           this.options.retryableErrors.includes(errorInfo.category)
  }
  
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// Usage
const retryHandler = new RetryHandler({
  maxRetries: 5,
  initialDelayMs: 200
})

const result = await retryHandler.execute(async () => {
  return await db.collection('orders').insertOne(orderData)
})
```

### Circuit Breaker Pattern

```javascript
class CircuitBreaker {
  constructor(options = {}) {
    this.options = {
      failureThreshold: 5,
      resetTimeout: 30000,
      halfOpenRequests: 3,
      ...options
    }
    
    this.state = 'CLOSED'  // CLOSED, OPEN, HALF_OPEN
    this.failures = 0
    this.successes = 0
    this.lastFailureTime = null
    this.halfOpenAttempts = 0
  }
  
  async execute(operation) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime >= this.options.resetTimeout) {
        this.state = 'HALF_OPEN'
        this.halfOpenAttempts = 0
        console.log('Circuit breaker: HALF_OPEN')
      } else {
        throw new Error('Circuit breaker is OPEN')
      }
    }
    
    try {
      const result = await operation()
      this.onSuccess()
      return result
    } catch (error) {
      this.onFailure()
      throw error
    }
  }
  
  onSuccess() {
    if (this.state === 'HALF_OPEN') {
      this.successes++
      if (this.successes >= this.options.halfOpenRequests) {
        this.state = 'CLOSED'
        this.failures = 0
        this.successes = 0
        console.log('Circuit breaker: CLOSED')
      }
    } else {
      this.failures = 0
    }
  }
  
  onFailure() {
    this.failures++
    this.lastFailureTime = Date.now()
    
    if (this.state === 'HALF_OPEN') {
      this.state = 'OPEN'
      console.log('Circuit breaker: OPEN (from HALF_OPEN)')
    } else if (this.failures >= this.options.failureThreshold) {
      this.state = 'OPEN'
      console.log('Circuit breaker: OPEN')
    }
  }
  
  getState() {
    return {
      state: this.state,
      failures: this.failures,
      lastFailureTime: this.lastFailureTime
    }
  }
}

// Usage
const circuitBreaker = new CircuitBreaker({
  failureThreshold: 5,
  resetTimeout: 30000
})

async function queryWithCircuitBreaker(filter) {
  return await circuitBreaker.execute(async () => {
    return await db.collection('products').find(filter).toArray()
  })
}
```

### Combined Retry with Circuit Breaker

```javascript
class ResilientExecutor {
  constructor(retryOptions = {}, circuitBreakerOptions = {}) {
    this.retryHandler = new RetryHandler(retryOptions)
    this.circuitBreaker = new CircuitBreaker(circuitBreakerOptions)
  }
  
  async execute(operation) {
    // Circuit breaker wraps retry logic
    return await this.circuitBreaker.execute(async () => {
      return await this.retryHandler.execute(operation)
    })
  }
  
  getStatus() {
    return {
      circuitBreaker: this.circuitBreaker.getState()
    }
  }
}

// Usage
const executor = new ResilientExecutor(
  { maxRetries: 3, initialDelayMs: 100 },
  { failureThreshold: 10, resetTimeout: 60000 }
)

try {
  const result = await executor.execute(async () => {
    return await db.collection('users').findOne({ id: userId })
  })
} catch (error) {
  if (error.message === 'Circuit breaker is OPEN') {
    // Service is temporarily unavailable
    return { error: 'Service temporarily unavailable' }
  }
  throw error
}
```

---

## Application-Level Handling

### Express.js Error Middleware

```javascript
// MongoDB error handler middleware for Express
function mongoDBErrorMiddleware(error, req, res, next) {
  // Already handled
  if (res.headersSent) {
    return next(error)
  }
  
  const errorInfo = MongoDBErrorHandler.categorize(error)
  
  // Map to HTTP status codes
  const statusCodes = {
    DUPLICATE_KEY: 409,      // Conflict
    VALIDATION: 400,         // Bad Request
    AUTHENTICATION: 401,     // Unauthorized
    TIMEOUT: 504,           // Gateway Timeout
    NETWORK: 503,           // Service Unavailable
    CONNECTION: 503,        // Service Unavailable
    SERVER_ERROR: 500,      // Internal Server Error
    UNKNOWN: 500            // Internal Server Error
  }
  
  const statusCode = statusCodes[errorInfo.category] || 500
  
  // Error response
  const response = {
    error: true,
    code: errorInfo.code,
    message: MongoDBErrorHandler.toUserError(errorInfo).message
  }
  
  // Add validation details in development
  if (process.env.NODE_ENV === 'development' && errorInfo.category === 'VALIDATION') {
    response.details = errorInfo.details
  }
  
  res.status(statusCode).json(response)
}

// Usage in Express app
app.use(mongoDBErrorMiddleware)
```

### Service Layer Error Handling

```javascript
// Service layer with comprehensive error handling
class UserService {
  constructor(db) {
    this.collection = db.collection('users')
    this.executor = new ResilientExecutor()
  }
  
  async create(userData) {
    try {
      // Validate before sending to DB
      this.validate(userData)
      
      const doc = {
        ...userData,
        email: userData.email.toLowerCase(),
        createdAt: new Date(),
        updatedAt: new Date()
      }
      
      const result = await this.executor.execute(async () => {
        return await this.collection.insertOne(doc)
      })
      
      return {
        success: true,
        user: { _id: result.insertedId, ...doc }
      }
      
    } catch (error) {
      return this.handleError(error, 'create')
    }
  }
  
  async findById(id) {
    try {
      const user = await this.executor.execute(async () => {
        return await this.collection.findOne({ _id: new ObjectId(id) })
      })
      
      if (!user) {
        return { success: false, error: 'NOT_FOUND', message: 'User not found' }
      }
      
      return { success: true, user }
      
    } catch (error) {
      return this.handleError(error, 'findById')
    }
  }
  
  async update(id, updates) {
    try {
      const result = await this.executor.execute(async () => {
        return await this.collection.findOneAndUpdate(
          { _id: new ObjectId(id) },
          { $set: { ...updates, updatedAt: new Date() } },
          { returnDocument: 'after' }
        )
      })
      
      if (!result) {
        return { success: false, error: 'NOT_FOUND', message: 'User not found' }
      }
      
      return { success: true, user: result }
      
    } catch (error) {
      return this.handleError(error, 'update')
    }
  }
  
  validate(userData) {
    const errors = []
    
    if (!userData.email || !this.isValidEmail(userData.email)) {
      errors.push({ field: 'email', message: 'Valid email is required' })
    }
    
    if (!userData.name || userData.name.length < 2) {
      errors.push({ field: 'name', message: 'Name must be at least 2 characters' })
    }
    
    if (errors.length > 0) {
      const error = new Error('Validation failed')
      error.code = 'VALIDATION_ERROR'
      error.details = errors
      throw error
    }
  }
  
  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }
  
  handleError(error, operation) {
    // Custom validation error
    if (error.code === 'VALIDATION_ERROR') {
      return {
        success: false,
        error: 'VALIDATION_ERROR',
        message: 'Validation failed',
        details: error.details
      }
    }
    
    // MongoDB error
    const errorInfo = MongoDBErrorHandler.handle(error, {
      service: 'UserService',
      operation
    })
    
    // Map specific errors
    if (errorInfo.code === 11000) {
      return {
        success: false,
        error: 'DUPLICATE_EMAIL',
        message: 'A user with this email already exists'
      }
    }
    
    return {
      success: false,
      error: errorInfo.code,
      message: errorInfo.message
    }
  }
}
```

---

## Logging and Monitoring

### Structured Error Logging

```javascript
class ErrorLogger {
  constructor(options = {}) {
    this.options = {
      serviceName: 'mongodb-service',
      environment: process.env.NODE_ENV || 'development',
      ...options
    }
  }
  
  log(error, context = {}) {
    const logEntry = this.createLogEntry(error, context)
    
    // Output based on severity
    if (logEntry.severity === 'error') {
      console.error(JSON.stringify(logEntry))
    } else if (logEntry.severity === 'warning') {
      console.warn(JSON.stringify(logEntry))
    } else {
      console.log(JSON.stringify(logEntry))
    }
    
    // Send to monitoring service
    this.sendToMonitoring(logEntry)
    
    return logEntry
  }
  
  createLogEntry(error, context) {
    const errorInfo = MongoDBErrorHandler.categorize(error)
    
    return {
      timestamp: new Date().toISOString(),
      service: this.options.serviceName,
      environment: this.options.environment,
      level: this.mapSeverity(errorInfo.severity),
      severity: errorInfo.severity,
      error: {
        name: error.name,
        code: errorInfo.code,
        category: errorInfo.category,
        message: error.message,
        stack: this.options.environment === 'development' ? error.stack : undefined
      },
      context: {
        ...context,
        retryable: errorInfo.retryable
      },
      metadata: {
        nodeVersion: process.version,
        pid: process.pid,
        hostname: require('os').hostname()
      }
    }
  }
  
  mapSeverity(severity) {
    const map = {
      high: 'error',
      medium: 'warning',
      low: 'info'
    }
    return map[severity] || 'error'
  }
  
  async sendToMonitoring(logEntry) {
    // Send to external monitoring (e.g., DataDog, Sentry, etc.)
    // Implementation depends on monitoring service
    
    // Example: Send to custom endpoint
    if (this.options.monitoringEndpoint) {
      try {
        await fetch(this.options.monitoringEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(logEntry)
        })
      } catch (e) {
        console.error('Failed to send to monitoring:', e.message)
      }
    }
  }
}

// Usage
const errorLogger = new ErrorLogger({
  serviceName: 'user-service',
  monitoringEndpoint: process.env.MONITORING_ENDPOINT
})

try {
  await db.collection('users').insertOne(userData)
} catch (error) {
  errorLogger.log(error, {
    operation: 'createUser',
    userId: userData.id
  })
  throw error
}
```

### Error Metrics Collection

```javascript
class ErrorMetrics {
  constructor() {
    this.counters = new Map()
    this.recentErrors = []
    this.maxRecentErrors = 100
  }
  
  record(error, context = {}) {
    const errorInfo = MongoDBErrorHandler.categorize(error)
    
    // Increment counter
    const key = `${errorInfo.category}:${errorInfo.code}`
    this.counters.set(key, (this.counters.get(key) || 0) + 1)
    
    // Track recent errors
    this.recentErrors.push({
      timestamp: new Date(),
      category: errorInfo.category,
      code: errorInfo.code,
      message: error.message,
      context
    })
    
    // Trim recent errors
    if (this.recentErrors.length > this.maxRecentErrors) {
      this.recentErrors.shift()
    }
  }
  
  getStats() {
    const now = Date.now()
    const oneHourAgo = now - 3600000
    const recentCount = this.recentErrors.filter(
      e => e.timestamp.getTime() > oneHourAgo
    ).length
    
    return {
      totalErrors: Array.from(this.counters.values()).reduce((a, b) => a + b, 0),
      errorsLastHour: recentCount,
      byCategory: Object.fromEntries(this.counters),
      recentErrors: this.recentErrors.slice(-10)
    }
  }
  
  reset() {
    this.counters.clear()
    this.recentErrors = []
  }
}

// Singleton metrics instance
const errorMetrics = new ErrorMetrics()

// Expose metrics endpoint
app.get('/metrics/errors', (req, res) => {
  res.json(errorMetrics.getStats())
})
```

---

## Summary

### Error Categories and Handling

| Category | Code | Retryable | Action |
|----------|------|-----------|--------|
| Duplicate Key | 11000 | No | Check constraint, inform user |
| Validation | 121 | No | Return validation errors |
| Network | Various | Yes | Retry with backoff |
| Timeout | 50 | Yes | Retry or increase timeout |
| Auth | 13, 18 | No | Check credentials |
| Server Selection | - | Yes | Check replica set |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Centralized error handling | Consistent error processing |
| Structured logging | Better debugging and monitoring |
| Retry with backoff | Handle transient failures |
| Circuit breaker | Prevent cascade failures |
| User-friendly messages | Better UX |

### Error Response Pattern

```javascript
// Consistent error response structure
{
  success: false,
  error: {
    code: 'ERROR_CODE',
    message: 'User-friendly message',
    details: [],        // Optional: validation details
    retryable: false    // Optional: can operation be retried
  }
}
```

---

## Practice Questions

1. What is the difference between retryable and non-retryable errors?
2. How do you handle duplicate key errors gracefully?
3. What is a circuit breaker and when should you use it?
4. How do you extract validation error details from MongoDB?
5. What is exponential backoff and why is it important?
6. How do you implement structured error logging?
7. When should you use ordered vs unordered bulk writes for error handling?
8. How do you map MongoDB errors to HTTP status codes?

---

[← Previous: Connection Pooling](67-connection-pooling.md) | [Next: Schema Validation →](69-schema-validation.md)
