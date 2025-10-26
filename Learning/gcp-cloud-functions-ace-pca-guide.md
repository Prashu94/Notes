# Google Cloud Functions - Comprehensive Guide for ACE & PCA Certifications

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [Architecture Patterns](#architecture-patterns)
4. [Development & Deployment](#development--deployment)
5. [Security & IAM](#security--iam)
6. [Monitoring & Observability](#monitoring--observability)
7. [Performance & Optimization](#performance--optimization)
8. [Integration Patterns](#integration-patterns)
9. [Cost Management](#cost-management)
10. [Best Practices](#best-practices)
11. [Exam Focus Areas](#exam-focus-areas)
12. [Common Scenarios](#common-scenarios)
13. [Troubleshooting](#troubleshooting)

## Overview

### What is Google Cloud Functions?
Google Cloud Functions is a serverless execution environment for building and connecting cloud services. It's a Functions-as-a-Service (FaaS) platform that automatically manages the underlying infrastructure, scaling, and availability.

### Key Characteristics
- **Event-driven**: Responds to events from various Google Cloud services
- **Serverless**: No server management required
- **Auto-scaling**: Automatically scales from zero to thousands of instances
- **Pay-per-use**: Billed only for actual execution time and resources used
- **Multi-language support**: Supports Node.js, Python, Go, Java, .NET, Ruby, PHP

### Generations
- **Cloud Functions 1st gen**: Original version with Cloud Build-based deployment
- **Cloud Functions 2nd gen**: Built on Cloud Run, improved performance and features

## Key Concepts

### Function Types

#### HTTP Functions
```javascript
// Node.js HTTP Function example
exports.helloWorld = (req, res) => {
  res.send('Hello, World!');
};
```

#### Event-driven Functions (Background Functions)
```javascript
// Cloud Storage trigger example
exports.processFile = (file, context) => {
  console.log(`File: ${file.name}`);
  console.log(`Event: ${context.eventType}`);
};
```

#### CloudEvent Functions (2nd gen)
```javascript
// CloudEvent function example
const functions = require('@google-cloud/functions-framework');

functions.cloudEvent('processCloudEvent', (cloudEvent) => {
  console.log('CloudEvent:', cloudEvent);
});
```

### Triggers

#### HTTP Triggers
- Direct HTTP requests
- RESTful APIs
- Webhooks
- Web applications

#### Cloud Storage Triggers
- Object creation (`google.storage.object.finalize`)
- Object deletion (`google.storage.object.delete`)
- Object metadata updates (`google.storage.object.metadataUpdate`)

#### Pub/Sub Triggers
- Message publishing
- Topic subscriptions
- Event routing

#### Cloud Firestore Triggers
- Document creation, updates, deletion
- Real-time data processing

#### Firebase Triggers
- Authentication events
- Real-time database changes
- Remote Config updates

#### Cloud Scheduler Triggers
- Cron-based scheduling
- Time-based execution

#### Eventarc Triggers (2nd gen)
- Cloud Audit Logs
- Direct events from 100+ Google Cloud sources

### Runtime Environments

#### Supported Runtimes
| Language | 1st Gen Versions | 2nd Gen Versions |
|----------|------------------|------------------|
| Node.js  | 10, 12, 14, 16, 18 | 16, 18, 20 |
| Python   | 3.7, 3.8, 3.9, 3.10 | 3.8, 3.9, 3.10, 3.11 |
| Go       | 1.11, 1.13, 1.16, 1.18, 1.19 | 1.18, 1.19, 1.20 |
| Java     | 11, 17 | 11, 17 |
| .NET     | 3.1, 6 | 6 |
| Ruby     | 2.6, 2.7, 3.0 | 3.0, 3.1 |
| PHP      | 7.4, 8.1 | 8.1, 8.2 |

## Architecture Patterns

### Microservices Architecture
```
[Client] → [API Gateway] → [Cloud Functions] → [Cloud SQL/Firestore]
                        → [Cloud Functions] → [Cloud Storage]
                        → [Cloud Functions] → [Pub/Sub]
```

### Event-Driven Architecture
```
[Cloud Storage] → [Cloud Function] → [Process Data] → [BigQuery]
[Pub/Sub Topic] → [Cloud Function] → [Transform] → [Cloud SQL]
[Firestore] → [Cloud Function] → [Trigger Workflow] → [Cloud Tasks]
```

### Data Pipeline Pattern
```
[Data Source] → [Cloud Function] → [Cloud Dataflow] → [BigQuery]
              → [Validation]    → [Error Handling] → [Cloud Storage]
```

### API Gateway Pattern
```
[Mobile App] → [Cloud Endpoints/API Gateway] → [Cloud Functions] → [Backend Services]
[Web App]    →                              → [Authentication] → [Database]
```

## Development & Deployment

### Function Structure (Node.js Example)

#### package.json
```json
{
  "name": "my-function",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "@google-cloud/storage": "^6.0.0",
    "@google-cloud/firestore": "^6.0.0"
  },
  "engines": {
    "node": "18"
  }
}
```

#### index.js
```javascript
const {Storage} = require('@google-cloud/storage');
const {Firestore} = require('@google-cloud/firestore');

const storage = new Storage();
const firestore = new Firestore();

exports.processUpload = async (file, context) => {
  try {
    const fileName = file.name;
    const bucketName = file.bucket;
    
    // Process the uploaded file
    const bucket = storage.bucket(bucketName);
    const fileObj = bucket.file(fileName);
    
    // Read file content
    const [content] = await fileObj.download();
    
    // Store metadata in Firestore
    await firestore.collection('uploads').add({
      fileName: fileName,
      bucketName: bucketName,
      uploadTime: context.timestamp,
      size: file.size,
      contentType: file.contentType
    });
    
    console.log(`Processed file: ${fileName}`);
  } catch (error) {
    console.error('Error processing file:', error);
    throw error;
  }
};
```

### Deployment Methods

#### gcloud CLI
```bash
# Deploy HTTP function
gcloud functions deploy my-http-function \
  --runtime nodejs18 \
  --trigger-http \
  --allow-unauthenticated \
  --memory 256MB \
  --timeout 60s

# Deploy background function
gcloud functions deploy process-upload \
  --runtime nodejs18 \
  --trigger-bucket my-storage-bucket \
  --memory 512MB \
  --timeout 120s

# Deploy Pub/Sub function
gcloud functions deploy process-message \
  --runtime python39 \
  --trigger-topic my-topic \
  --set-env-vars PROJECT_ID=my-project

# Deploy 2nd gen function
gcloud functions deploy my-function-gen2 \
  --gen2 \
  --runtime nodejs18 \
  --trigger-http \
  --region us-central1
```

#### Terraform
```hcl
resource "google_cloudfunctions_function" "function" {
  name        = "my-function"
  description = "Process uploaded files"
  runtime     = "nodejs18"

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.zip.name
  
  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = google_storage_bucket.trigger_bucket.name
  }

  environment_variables = {
    PROJECT_ID = var.project_id
  }
}
```

#### Cloud Build (CI/CD)
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['functions', 'deploy', 'my-function',
           '--runtime', 'nodejs18',
           '--trigger-http',
           '--source', '.']
```

### Environment Variables & Configuration
```bash
# Set environment variables
gcloud functions deploy my-function \
  --set-env-vars KEY1=value1,KEY2=value2

# Use .env.yaml file
gcloud functions deploy my-function \
  --env-vars-file .env.yaml
```

```yaml
# .env.yaml
DATABASE_URL: "postgresql://user:pass@host:5432/db"
API_KEY: "your-api-key"
DEBUG: "true"
```

## Security & IAM

### IAM Roles

#### Predefined Roles
- `roles/cloudfunctions.admin`: Full access to Cloud Functions
- `roles/cloudfunctions.developer`: Deploy and manage functions
- `roles/cloudfunctions.viewer`: Read-only access
- `roles/cloudfunctions.invoker`: Invoke functions

#### Service Accounts
```bash
# Create service account
gcloud iam service-accounts create my-function-sa \
  --display-name="Cloud Function Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:my-function-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# Deploy with service account
gcloud functions deploy my-function \
  --service-account="my-function-sa@PROJECT_ID.iam.gserviceaccount.com"
```

### Authentication & Authorization

#### HTTP Function Security
```javascript
// Verify Firebase ID token
const admin = require('firebase-admin');

exports.secureFunction = async (req, res) => {
  const idToken = req.headers.authorization?.split('Bearer ')[1];
  
  try {
    const decodedToken = await admin.auth().verifyIdToken(idToken);
    const uid = decodedToken.uid;
    
    // Process authenticated request
    res.json({ message: `Hello ${uid}` });
  } catch (error) {
    res.status(401).json({ error: 'Unauthorized' });
  }
};
```

#### VPC Security
```bash
# Deploy function in VPC
gcloud functions deploy my-function \
  --vpc-connector projects/PROJECT_ID/locations/REGION/connectors/CONNECTOR_NAME \
  --egress-settings vpc-connector
```

### Secrets Management

#### Secret Manager Integration
```javascript
const {SecretManagerServiceClient} = require('@google-cloud/secret-manager');

const client = new SecretManagerServiceClient();

async function getSecret(secretName) {
  const [version] = await client.accessSecretVersion({
    name: `projects/PROJECT_ID/secrets/${secretName}/versions/latest`,
  });
  
  return version.payload.data.toString();
}

exports.functionWithSecret = async (req, res) => {
  const apiKey = await getSecret('api-key');
  // Use the secret
};
```

## Monitoring & Observability

### Cloud Logging
```javascript
const {Logging} = require('@google-cloud/logging');
const logging = new Logging();

exports.myFunction = (req, res) => {
  // Structured logging
  console.log(JSON.stringify({
    severity: 'INFO',
    message: 'Function executed',
    requestId: req.get('X-Request-ID'),
    userId: req.user?.id
  }));
  
  res.send('Done');
};
```

### Cloud Monitoring
```javascript
const monitoring = require('@google-cloud/monitoring');

const client = new monitoring.MetricServiceClient();

exports.functionWithMetrics = async (req, res) => {
  const projectId = process.env.GOOGLE_CLOUD_PROJECT;
  
  // Create custom metric
  const dataPoint = {
    interval: {
      endTime: {
        seconds: Date.now() / 1000,
      },
    },
    value: {
      doubleValue: 1,
    },
  };

  const timeSeriesData = {
    metric: {
      type: 'custom.googleapis.com/function/executions',
    },
    resource: {
      type: 'cloud_function',
      labels: {
        function_name: 'my-function',
        region: 'us-central1',
      },
    },
    points: [dataPoint],
  };

  await client.createTimeSeries({
    name: client.projectPath(projectId),
    timeSeries: [timeSeriesData],
  });
  
  res.send('Metric recorded');
};
```

### Error Reporting
```javascript
const {ErrorReporting} = require('@google-cloud/error-reporting');
const errors = new ErrorReporting();

exports.functionWithErrorHandling = (req, res) => {
  try {
    // Function logic
    throw new Error('Something went wrong');
  } catch (error) {
    errors.report(error);
    res.status(500).send('Internal Server Error');
  }
};
```

### Cloud Trace
```javascript
const tracer = require('@google-cloud/trace-agent').start();

exports.tracedFunction = async (req, res) => {
  const span = tracer.createChildSpan({name: 'process-request'});
  
  try {
    // Add span annotations
    span.addLabel('userId', req.user?.id);
    
    // Simulate work
    await new Promise(resolve => setTimeout(resolve, 100));
    
    span.endSpan();
    res.send('Processed');
  } catch (error) {
    span.addLabel('error', error.message);
    span.endSpan();
    throw error;
  }
};
```

## Performance & Optimization

### Cold Start Optimization

#### Global Variables
```javascript
// Initialize outside the function handler
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();

let cachedData = null;

exports.optimizedFunction = async (req, res) => {
  // Reuse initialized clients and cached data
  if (!cachedData) {
    cachedData = await loadExpensiveData();
  }
  
  // Function logic
  res.send('Done');
};
```

#### Connection Pooling
```javascript
const mysql = require('mysql2/promise');

// Create connection pool (reused across invocations)
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  connectionLimit: 1,
  acquireTimeout: 60000,
  timeout: 60000,
});

exports.databaseFunction = async (req, res) => {
  const connection = await pool.getConnection();
  
  try {
    const [rows] = await connection.execute('SELECT * FROM users');
    res.json(rows);
  } finally {
    connection.release();
  }
};
```

### Memory & CPU Optimization
```bash
# Configure memory allocation
gcloud functions deploy my-function \
  --memory 1GB \
  --timeout 540s

# 2nd gen with CPU allocation
gcloud functions deploy my-function-gen2 \
  --gen2 \
  --memory 2Gi \
  --cpu 2
```

### Concurrency Settings
```bash
# 1st gen: Max instances
gcloud functions deploy my-function \
  --max-instances 100

# 2nd gen: Concurrency per instance
gcloud functions deploy my-function-gen2 \
  --gen2 \
  --concurrency 100 \
  --max-instances 50
```

## Integration Patterns

### Pub/Sub Integration
```javascript
exports.pubsubFunction = (message, context) => {
  const data = message.data 
    ? Buffer.from(message.data, 'base64').toString()
    : 'No data';
  
  console.log('Message:', data);
  console.log('Attributes:', message.attributes);
  console.log('Message ID:', context.eventId);
};
```

### Cloud Storage Integration
```javascript
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();

exports.processFile = async (file, context) => {
  const bucket = storage.bucket(file.bucket);
  const fileObj = bucket.file(file.name);
  
  // Process based on file type
  if (file.contentType.startsWith('image/')) {
    await processImage(fileObj);
  } else if (file.contentType === 'application/json') {
    await processJSON(fileObj);
  }
};

async function processImage(file) {
  // Image processing logic
}

async function processJSON(file) {
  const [content] = await file.download();
  const jsonData = JSON.parse(content.toString());
  // Process JSON data
}
```

### Firestore Integration
```javascript
const {Firestore} = require('@google-cloud/firestore');
const firestore = new Firestore();

exports.firestoreFunction = (change, context) => {
  const before = change.before.exists ? change.before.data() : null;
  const after = change.after.exists ? change.after.data() : null;
  
  if (!before && after) {
    // Document created
    console.log('Document created:', after);
  } else if (before && after) {
    // Document updated
    console.log('Document updated:', {before, after});
  } else if (before && !after) {
    // Document deleted
    console.log('Document deleted:', before);
  }
};
```

### API Gateway Integration
```yaml
# openapi.yaml
swagger: '2.0'
info:
  title: My API
  version: '1.0'
host: my-api-gateway.com
schemes:
  - https
paths:
  /users:
    get:
      operationId: getUsers
      x-google-backend:
        address: https://REGION-PROJECT.cloudfunctions.net/get-users
      responses:
        200:
          description: Success
```

## Cost Management

### Pricing Factors
- **Invocations**: Number of function executions
- **Compute Time**: GB-seconds of memory * execution time
- **Networking**: Outbound data transfer
- **CPU Time**: CPU-seconds (2nd gen only)

### Cost Optimization Strategies

#### Right-sizing Memory
```bash
# Test different memory allocations
gcloud functions deploy my-function --memory 128MB  # Minimum
gcloud functions deploy my-function --memory 256MB  # Default
gcloud functions deploy my-function --memory 512MB  # Higher performance
```

#### Timeout Optimization
```bash
# Set appropriate timeout
gcloud functions deploy my-function \
  --timeout 60s  # Don't set longer than needed
```

#### Instance Management
```bash
# Control scaling
gcloud functions deploy my-function \
  --min-instances 1 \    # Reduce cold starts
  --max-instances 100    # Control costs
```

### Cost Monitoring
```javascript
// Log execution metrics for cost analysis
exports.costAwareFunction = (req, res) => {
  const startTime = Date.now();
  const startMemory = process.memoryUsage().heapUsed;
  
  // Function logic here
  
  const duration = Date.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;
  
  console.log(JSON.stringify({
    duration,
    memoryUsed,
    timestamp: new Date().toISOString()
  }));
  
  res.send('Done');
};
```

## Best Practices

### Code Organization

#### Single Responsibility
```javascript
// Good: Each function has a single responsibility
exports.validateUser = (req, res) => { /* validation logic */ };
exports.createUser = (req, res) => { /* creation logic */ };
exports.sendWelcomeEmail = (message, context) => { /* email logic */ };
```

#### Error Handling
```javascript
exports.robustFunction = async (req, res) => {
  try {
    // Validate input
    if (!req.body || !req.body.data) {
      return res.status(400).json({ error: 'Missing required data' });
    }
    
    // Process request
    const result = await processData(req.body.data);
    
    res.json({ success: true, result });
  } catch (error) {
    console.error('Function error:', error);
    
    // Return appropriate error response
    if (error.code === 'INVALID_INPUT') {
      res.status(400).json({ error: error.message });
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
};
```

#### Idempotency
```javascript
const {Firestore} = require('@google-cloud/firestore');
const firestore = new Firestore();

exports.idempotentFunction = async (message, context) => {
  const messageId = context.eventId;
  
  // Check if already processed
  const processedDoc = await firestore
    .collection('processed')
    .doc(messageId)
    .get();
    
  if (processedDoc.exists) {
    console.log(`Message ${messageId} already processed`);
    return;
  }
  
  try {
    // Process message
    await processMessage(message);
    
    // Mark as processed
    await firestore
      .collection('processed')
      .doc(messageId)
      .set({ processedAt: new Date() });
      
  } catch (error) {
    console.error('Processing failed:', error);
    throw error; // Will retry
  }
};
```

### Security Best Practices

#### Input Validation
```javascript
const Joi = require('joi');

const schema = Joi.object({
  email: Joi.string().email().required(),
  name: Joi.string().min(3).max(50).required(),
  age: Joi.number().integer().min(0).max(120)
});

exports.validatedFunction = (req, res) => {
  const { error, value } = schema.validate(req.body);
  
  if (error) {
    return res.status(400).json({
      error: 'Validation failed',
      details: error.details
    });
  }
  
  // Process validated data
  processUserData(value);
  res.json({ success: true });
};
```

#### CORS Handling
```javascript
const cors = require('cors')({
  origin: ['https://myapp.com', 'https://staging.myapp.com'],
  credentials: true
});

exports.corsFunction = (req, res) => {
  cors(req, res, () => {
    // Function logic
    res.json({ message: 'CORS enabled' });
  });
};
```

### Performance Best Practices

#### Async/Await Usage
```javascript
// Good: Proper async handling
exports.asyncFunction = async (req, res) => {
  try {
    const [user, orders, preferences] = await Promise.all([
      getUser(req.params.id),
      getUserOrders(req.params.id),
      getUserPreferences(req.params.id)
    ]);
    
    res.json({ user, orders, preferences });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Failed to fetch data' });
  }
};
```

#### Streaming for Large Responses
```javascript
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();

exports.streamFile = (req, res) => {
  const bucket = storage.bucket('my-bucket');
  const file = bucket.file(req.params.filename);
  
  res.setHeader('Content-Type', 'application/octet-stream');
  
  file.createReadStream()
    .on('error', (error) => {
      console.error('Stream error:', error);
      res.status(500).send('Error streaming file');
    })
    .pipe(res);
};
```

## Exam Focus Areas

### ACE Exam Focus

#### Deployment and Management
- Function deployment using gcloud CLI
- Environment variable configuration
- Runtime selection and versioning
- Basic IAM permissions

#### Key Commands
```bash
# Deploy function
gcloud functions deploy FUNCTION_NAME \
  --runtime RUNTIME \
  --trigger-http \
  --allow-unauthenticated

# List functions
gcloud functions list

# View function details
gcloud functions describe FUNCTION_NAME

# View logs
gcloud functions logs read FUNCTION_NAME

# Delete function
gcloud functions delete FUNCTION_NAME
```

#### Common Triggers
- HTTP triggers for REST APIs
- Cloud Storage triggers for file processing
- Pub/Sub triggers for messaging
- Cloud Scheduler for cron jobs

### PCA Exam Focus

#### Architecture Design
- Microservices vs. monolithic architectures
- Event-driven architecture patterns
- API Gateway integration
- Multi-region deployment strategies

#### Advanced Patterns
- Circuit breaker patterns
- Saga patterns for distributed transactions
- CQRS with event sourcing
- Fan-out/fan-in patterns

#### Security Architecture
- IAM best practices
- VPC integration
- Secret management
- Authentication flows

#### Cost Optimization
- Right-sizing memory allocation
- Instance scaling strategies
- Cold start mitigation
- Resource sharing patterns

## Common Scenarios

### Scenario 1: File Processing Pipeline
**Requirements**: Process uploaded images, create thumbnails, extract metadata

```javascript
const {Storage} = require('@google-cloud/storage');
const sharp = require('sharp');

const storage = new Storage();

exports.processImage = async (file, context) => {
  if (!file.contentType.startsWith('image/')) {
    console.log('Not an image file, skipping');
    return;
  }
  
  const bucket = storage.bucket(file.bucket);
  const originalFile = bucket.file(file.name);
  
  try {
    // Download original image
    const [imageBuffer] = await originalFile.download();
    
    // Create thumbnail
    const thumbnail = await sharp(imageBuffer)
      .resize(200, 200, { fit: 'inside' })
      .jpeg({ quality: 80 })
      .toBuffer();
    
    // Upload thumbnail
    const thumbnailName = `thumbnails/${file.name}`;
    const thumbnailFile = bucket.file(thumbnailName);
    
    await thumbnailFile.save(thumbnail, {
      metadata: { contentType: 'image/jpeg' }
    });
    
    // Extract and store metadata
    const metadata = await sharp(imageBuffer).metadata();
    
    await storeMetadata({
      originalFile: file.name,
      thumbnailFile: thumbnailName,
      width: metadata.width,
      height: metadata.height,
      format: metadata.format,
      size: file.size
    });
    
    console.log(`Processed image: ${file.name}`);
  } catch (error) {
    console.error('Error processing image:', error);
    throw error;
  }
};
```

### Scenario 2: Real-time Data Processing
**Requirements**: Process IoT sensor data from Pub/Sub, validate, and store

```javascript
const {BigQuery} = require('@google-cloud/bigquery');
const {PubSub} = require('@google-cloud/pubsub');

const bigquery = new BigQuery();
const pubsub = new PubSub();

exports.processSensorData = async (message, context) => {
  try {
    const data = JSON.parse(Buffer.from(message.data, 'base64').toString());
    
    // Validate sensor data
    const validatedData = validateSensorData(data);
    
    if (!validatedData.isValid) {
      console.log('Invalid sensor data:', validatedData.errors);
      
      // Send to dead letter queue
      await pubsub.topic('sensor-data-errors').publish(message.data);
      return;
    }
    
    // Enrich data
    const enrichedData = await enrichSensorData(validatedData.data);
    
    // Store in BigQuery
    await bigquery
      .dataset('iot_data')
      .table('sensor_readings')
      .insert([enrichedData]);
    
    // Trigger alerts if needed
    if (enrichedData.temperature > 80) {
      await triggerAlert(enrichedData);
    }
    
    console.log('Processed sensor data:', enrichedData.sensorId);
  } catch (error) {
    console.error('Error processing sensor data:', error);
    throw error; // Will retry
  }
};

function validateSensorData(data) {
  const errors = [];
  
  if (!data.sensorId) errors.push('Missing sensorId');
  if (!data.timestamp) errors.push('Missing timestamp');
  if (typeof data.temperature !== 'number') errors.push('Invalid temperature');
  if (typeof data.humidity !== 'number') errors.push('Invalid humidity');
  
  return {
    isValid: errors.length === 0,
    data,
    errors
  };
}

async function enrichSensorData(data) {
  // Add location data, device info, etc.
  return {
    ...data,
    location: await getLocationBySensorId(data.sensorId),
    processedAt: new Date().toISOString()
  };
}
```

### Scenario 3: API Gateway with Authentication
**Requirements**: Create authenticated REST API for user management

```javascript
const admin = require('firebase-admin');

admin.initializeApp();

exports.userAPI = async (req, res) => {
  // CORS handling
  res.set('Access-Control-Allow-Origin', '*');
  
  if (req.method === 'OPTIONS') {
    res.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.set('Access-Control-Allow-Headers', 'Authorization, Content-Type');
    res.status(204).send('');
    return;
  }
  
  try {
    // Authenticate request
    const user = await authenticateRequest(req);
    
    // Route request
    switch (req.method) {
      case 'GET':
        if (req.path === '/profile') {
          return await getUserProfile(req, res, user);
        }
        break;
      case 'POST':
        if (req.path === '/profile') {
          return await createUserProfile(req, res, user);
        }
        break;
      case 'PUT':
        if (req.path === '/profile') {
          return await updateUserProfile(req, res, user);
        }
        break;
      default:
        res.status(405).json({ error: 'Method not allowed' });
    }
  } catch (error) {
    if (error.code === 'UNAUTHENTICATED') {
      res.status(401).json({ error: 'Unauthorized' });
    } else {
      console.error('API Error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
};

async function authenticateRequest(req) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw { code: 'UNAUTHENTICATED', message: 'Missing authorization header' };
  }
  
  const idToken = authHeader.split('Bearer ')[1];
  return await admin.auth().verifyIdToken(idToken);
}
```

## Troubleshooting

### Common Issues and Solutions

#### Cold Start Performance
**Problem**: Function takes too long to start
**Solutions**:
- Use minimum instances to keep functions warm
- Optimize initialization code
- Use smaller deployment packages
- Consider 2nd gen functions for better performance

```bash
# Keep functions warm
gcloud functions deploy my-function \
  --min-instances 1

# Optimize package size
gcloud functions deploy my-function \
  --ignore-file .gcloudignore
```

#### Memory Issues
**Problem**: Function runs out of memory
**Solutions**:
- Increase memory allocation
- Optimize memory usage in code
- Use streaming for large data processing

```bash
# Increase memory
gcloud functions deploy my-function \
  --memory 1GB
```

#### Timeout Issues
**Problem**: Function times out
**Solutions**:
- Increase timeout limit
- Optimize slow operations
- Use async processing for long tasks

```bash
# Increase timeout (max 540s for 1st gen, 3600s for 2nd gen)
gcloud functions deploy my-function \
  --timeout 540s
```

#### Permission Errors
**Problem**: Function can't access other services
**Solutions**:
- Check IAM permissions
- Verify service account configuration
- Enable required APIs

```bash
# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:FUNCTION_SA@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### Debugging Techniques

#### Local Development
```bash
# Functions Framework for local testing
npm install @google-cloud/functions-framework

# Run locally
npx functions-framework --target=myFunction --port=8080
```

#### Logging and Monitoring
```javascript
exports.debugFunction = (req, res) => {
  // Structured logging
  console.log(JSON.stringify({
    level: 'INFO',
    message: 'Function started',
    requestId: req.get('X-Request-ID'),
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  }));
  
  // Function logic with debug info
  try {
    const result = processRequest(req.body);
    
    console.log(JSON.stringify({
      level: 'INFO',
      message: 'Request processed successfully',
      result: result
    }));
    
    res.json({ success: true, result });
  } catch (error) {
    console.error(JSON.stringify({
      level: 'ERROR',
      message: 'Request processing failed',
      error: error.message,
      stack: error.stack
    }));
    
    res.status(500).json({ error: 'Processing failed' });
  }
};
```

### Performance Monitoring
```bash
# View function metrics
gcloud functions describe my-function \
  --format="value(status.updateTime)"

# Check execution count and duration
gcloud logging read "resource.type=cloud_function" \
  --format="table(timestamp,textPayload)" \
  --limit=10
```

---

## Summary

Google Cloud Functions is a powerful serverless platform that enables event-driven computing at scale. For both ACE and PCA certifications, understanding the following key areas is crucial:

### ACE Focus Areas:
- Basic deployment and configuration
- Common trigger types
- IAM and security basics
- Monitoring and logging

### PCA Focus Areas:
- Advanced architecture patterns
- Integration strategies
- Performance optimization
- Cost management
- Security best practices

### Key Takeaways:
1. **Start Simple**: Begin with basic HTTP functions before moving to complex event-driven architectures
2. **Think Serverless**: Design for stateless, event-driven patterns
3. **Optimize Early**: Consider performance and cost implications from the beginning
4. **Security First**: Implement proper authentication, authorization, and input validation
5. **Monitor Everything**: Use Cloud Logging, Monitoring, and Error Reporting effectively

This comprehensive guide covers the essential concepts and practical implementations needed to succeed in both Google Cloud certification exams while building production-ready serverless applications.