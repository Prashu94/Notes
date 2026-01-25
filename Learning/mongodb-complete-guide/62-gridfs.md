# Chapter 62: GridFS

## Table of Contents
- [GridFS Overview](#gridfs-overview)
- [GridFS Architecture](#gridfs-architecture)
- [Storing Files](#storing-files)
- [Retrieving Files](#retrieving-files)
- [File Management](#file-management)
- [Advanced Operations](#advanced-operations)
- [Summary](#summary)

---

## GridFS Overview

### What is GridFS?

```
┌─────────────────────────────────────────────────────────────────────┐
│                       GridFS Overview                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  GridFS is MongoDB's specification for storing and retrieving       │
│  files that exceed the BSON document size limit of 16MB.           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Large File (50MB)                         │   │
│  │  ┌─────────────────────────────────────────────────────────┐│   │
│  │  │                     PDF Document                        ││   │
│  │  └─────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     GridFS                                   │   │
│  │                                                              │   │
│  │  Split into 255KB chunks                                    │   │
│  │                                                              │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐       ┌────────┐       │   │
│  │  │Chunk 0 │  │Chunk 1 │  │Chunk 2 │  ...  │Chunk N │       │   │
│  │  │ 255KB  │  │ 255KB  │  │ 255KB  │       │ <255KB │       │   │
│  │  └────────┘  └────────┘  └────────┘       └────────┘       │   │
│  │                                                              │   │
│  │  Metadata stored in fs.files                                │   │
│  │  Chunks stored in fs.chunks                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Use Cases:                                                        │
│  • Large media files (images, videos, audio)                       │
│  • Document storage (PDFs, Office documents)                       │
│  • Scientific data files                                           │
│  • Backup and archive systems                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use GridFS

| Use Case | GridFS | Alternative |
|----------|--------|-------------|
| Files > 16MB | ✓ Required | N/A |
| Files < 16MB with metadata | ✓ Optional | BinData in document |
| Streaming large files | ✓ Good | Object storage |
| Frequent partial reads | ✓ Good | Object storage |
| Need file system abstraction | ✓ Good | External storage |
| CDN delivery | Consider | Object storage (S3, etc.) |

---

## GridFS Architecture

### Collection Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GridFS Collections                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  fs.files (Metadata Collection)                              │   │
│  │  ┌─────────────────────────────────────────────────────────┐│   │
│  │  │ {                                                       ││   │
│  │  │   _id: ObjectId("..."),                                 ││   │
│  │  │   length: 52428800,        // Total file size (bytes)   ││   │
│  │  │   chunkSize: 261120,       // Size of each chunk        ││   │
│  │  │   uploadDate: ISODate(),   // Upload timestamp          ││   │
│  │  │   filename: "video.mp4",   // Original filename         ││   │
│  │  │   metadata: {...}          // Custom metadata           ││   │
│  │  │ }                                                       ││   │
│  │  └─────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  fs.chunks (Chunk Collection)                                │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │ {                                                      │ │   │
│  │  │   _id: ObjectId("..."),                                │ │   │
│  │  │   files_id: ObjectId("..."),  // Reference to fs.files │ │   │
│  │  │   n: 0,                        // Chunk sequence number│ │   │
│  │  │   data: BinData(...)           // Binary chunk data    │ │   │
│  │  │ }                                                      │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │ { _id: ..., files_id: ..., n: 1, data: BinData(...) }  │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │ { _id: ..., files_id: ..., n: 2, data: BinData(...) }  │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Indexes (created automatically):                                  │
│  • fs.files: { filename: 1, uploadDate: 1 }                       │
│  • fs.chunks: { files_id: 1, n: 1 } (unique)                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Chunk Size

```javascript
// Default chunk size: 255 KB (261120 bytes)
// Can be customized between 1 byte and 16 MB

// Smaller chunks:
// + Better for partial reads
// + Lower memory usage per chunk
// - More documents = more overhead

// Larger chunks:
// + Fewer documents
// + Better sequential read performance
// - Higher memory per chunk
```

---

## Storing Files

### Using mongofiles Command-Line Tool

```bash
# Upload a file
mongofiles -d mydb put large_video.mp4

# Upload with custom collection prefix
mongofiles -d mydb --prefix=media put video.mp4

# Upload with metadata
mongofiles -d mydb put document.pdf --metadata '{"author": "John", "category": "reports"}'

# Upload from stdin
cat large_file.bin | mongofiles -d mydb put --replace -l - uploaded_file.bin
```

### Using MongoDB Driver (Node.js)

```javascript
const { MongoClient, GridFSBucket } = require('mongodb')
const fs = require('fs')

async function uploadFile(dbName, filePath, filename) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    // Create GridFS bucket
    const bucket = new GridFSBucket(db, {
      bucketName: 'fs',      // Collection prefix (default: fs)
      chunkSizeBytes: 261120 // Chunk size (default: 255KB)
    })
    
    // Create upload stream
    const uploadStream = bucket.openUploadStream(filename, {
      metadata: {
        contentType: 'application/pdf',
        author: 'John Doe',
        tags: ['report', '2024']
      }
    })
    
    // Pipe file to GridFS
    const fileStream = fs.createReadStream(filePath)
    
    return new Promise((resolve, reject) => {
      fileStream
        .pipe(uploadStream)
        .on('error', reject)
        .on('finish', () => {
          console.log(`File uploaded with id: ${uploadStream.id}`)
          resolve(uploadStream.id)
        })
    })
    
  } finally {
    await client.close()
  }
}

// Usage
uploadFile('mydb', '/path/to/document.pdf', 'document.pdf')
```

### Using MongoDB Driver (Python)

```python
from pymongo import MongoClient
import gridfs

def upload_file(db_name, file_path, filename, metadata=None):
    client = MongoClient('mongodb://localhost:27017')
    db = client[db_name]
    
    # Create GridFS instance
    fs = gridfs.GridFS(db)
    
    # Read and store file
    with open(file_path, 'rb') as f:
        file_id = fs.put(
            f,
            filename=filename,
            metadata=metadata or {},
            content_type='application/pdf'
        )
    
    print(f"File uploaded with id: {file_id}")
    return file_id

# Usage
upload_file('mydb', '/path/to/document.pdf', 'document.pdf', {
    'author': 'John Doe',
    'category': 'reports'
})
```

### Upload with Custom Chunk Size

```javascript
// Node.js - Custom chunk size
const bucket = new GridFSBucket(db, {
  chunkSizeBytes: 1024 * 1024  // 1MB chunks
})

// Python - Custom chunk size
import gridfs

# Create GridFS with custom chunk size (1MB)
fs = gridfs.GridFS(db, collection='largefiles')

# Or using GridFSBucket
from gridfs import GridFSBucket
bucket = GridFSBucket(db, chunk_size_bytes=1024*1024)
```

---

## Retrieving Files

### Using mongofiles Command-Line Tool

```bash
# Download a file
mongofiles -d mydb get large_video.mp4

# Download to specific location
mongofiles -d mydb get large_video.mp4 -l /output/path/video.mp4

# List all files
mongofiles -d mydb list

# Search for files
mongofiles -d mydb search "video"
```

### Download File (Node.js)

```javascript
const { MongoClient, GridFSBucket } = require('mongodb')
const fs = require('fs')

async function downloadFile(dbName, filename, outputPath) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    const bucket = new GridFSBucket(db)
    
    // Create download stream
    const downloadStream = bucket.openDownloadStreamByName(filename)
    
    // Create write stream
    const writeStream = fs.createWriteStream(outputPath)
    
    return new Promise((resolve, reject) => {
      downloadStream
        .pipe(writeStream)
        .on('error', reject)
        .on('finish', () => {
          console.log(`File downloaded to: ${outputPath}`)
          resolve()
        })
    })
    
  } finally {
    await client.close()
  }
}

// Download by ID
async function downloadFileById(dbName, fileId, outputPath) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    const bucket = new GridFSBucket(db)
    
    const downloadStream = bucket.openDownloadStream(fileId)
    const writeStream = fs.createWriteStream(outputPath)
    
    return new Promise((resolve, reject) => {
      downloadStream
        .pipe(writeStream)
        .on('error', reject)
        .on('finish', resolve)
    })
    
  } finally {
    await client.close()
  }
}
```

### Streaming Files (HTTP Response)

```javascript
const express = require('express')
const { MongoClient, GridFSBucket } = require('mongodb')

const app = express()

app.get('/files/:filename', async (req, res) => {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db('mydb')
    const bucket = new GridFSBucket(db)
    
    // Find file metadata
    const files = await bucket.find({ filename: req.params.filename }).toArray()
    
    if (files.length === 0) {
      return res.status(404).json({ error: 'File not found' })
    }
    
    const file = files[0]
    
    // Set response headers
    res.set('Content-Type', file.metadata?.contentType || 'application/octet-stream')
    res.set('Content-Length', file.length)
    res.set('Content-Disposition', `attachment; filename="${file.filename}"`)
    
    // Stream file to response
    const downloadStream = bucket.openDownloadStreamByName(req.params.filename)
    downloadStream.pipe(res)
    
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})

// Range requests for video streaming
app.get('/stream/:filename', async (req, res) => {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db('mydb')
    const bucket = new GridFSBucket(db)
    
    const files = await bucket.find({ filename: req.params.filename }).toArray()
    
    if (files.length === 0) {
      return res.status(404).json({ error: 'File not found' })
    }
    
    const file = files[0]
    const fileSize = file.length
    
    // Handle range request
    const range = req.headers.range
    
    if (range) {
      const parts = range.replace(/bytes=/, '').split('-')
      const start = parseInt(parts[0], 10)
      const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1
      
      const chunkSize = end - start + 1
      
      res.status(206)
      res.set({
        'Content-Range': `bytes ${start}-${end}/${fileSize}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunkSize,
        'Content-Type': 'video/mp4'
      })
      
      const downloadStream = bucket.openDownloadStreamByName(req.params.filename, {
        start: start,
        end: end + 1
      })
      
      downloadStream.pipe(res)
    } else {
      res.set({
        'Content-Length': fileSize,
        'Content-Type': 'video/mp4'
      })
      
      bucket.openDownloadStreamByName(req.params.filename).pipe(res)
    }
    
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})
```

### Partial Read (Seeking)

```javascript
// Read specific byte range
async function readPartial(dbName, filename, start, end) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    const downloadStream = bucket.openDownloadStreamByName(filename, {
      start: start,
      end: end
    })
    
    const chunks = []
    
    return new Promise((resolve, reject) => {
      downloadStream
        .on('data', chunk => chunks.push(chunk))
        .on('error', reject)
        .on('end', () => resolve(Buffer.concat(chunks)))
    })
    
  } finally {
    await client.close()
  }
}

// Usage: Read bytes 1000-2000
const partialData = await readPartial('mydb', 'video.mp4', 1000, 2000)
```

---

## File Management

### Listing Files

```javascript
// List all files
async function listFiles(dbName, query = {}) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    const files = await bucket.find(query)
      .sort({ uploadDate: -1 })
      .toArray()
    
    return files.map(f => ({
      id: f._id,
      filename: f.filename,
      size: f.length,
      uploadDate: f.uploadDate,
      metadata: f.metadata
    }))
    
  } finally {
    await client.close()
  }
}

// List with filter
const pdfFiles = await listFiles('mydb', { 
  'metadata.contentType': 'application/pdf' 
})
```

### Deleting Files

```javascript
// Delete by ID
async function deleteFile(dbName, fileId) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    await bucket.delete(fileId)
    console.log(`Deleted file: ${fileId}`)
    
  } finally {
    await client.close()
  }
}

// Delete by filename (all revisions)
async function deleteByFilename(dbName, filename) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    const files = await bucket.find({ filename }).toArray()
    
    for (const file of files) {
      await bucket.delete(file._id)
      console.log(`Deleted: ${file._id}`)
    }
    
    console.log(`Deleted ${files.length} file(s)`)
    
  } finally {
    await client.close()
  }
}
```

### Renaming Files

```javascript
// Rename a file
async function renameFile(dbName, fileId, newFilename) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    await bucket.rename(fileId, newFilename)
    console.log(`Renamed to: ${newFilename}`)
    
  } finally {
    await client.close()
  }
}
```

### Updating Metadata

```javascript
// Update file metadata
async function updateMetadata(dbName, fileId, metadata) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    // Update directly in fs.files collection
    await db.collection('fs.files').updateOne(
      { _id: fileId },
      { $set: { metadata: metadata } }
    )
    
    console.log('Metadata updated')
    
  } finally {
    await client.close()
  }
}

// Add to existing metadata
async function addMetadata(dbName, fileId, additionalMetadata) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    const updateFields = {}
    for (const [key, value] of Object.entries(additionalMetadata)) {
      updateFields[`metadata.${key}`] = value
    }
    
    await db.collection('fs.files').updateOne(
      { _id: fileId },
      { $set: updateFields }
    )
    
  } finally {
    await client.close()
  }
}
```

---

## Advanced Operations

### File Versioning

```javascript
// Upload with version tracking
async function uploadVersion(dbName, filePath, filename, version) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    const uploadStream = bucket.openUploadStream(filename, {
      metadata: {
        version: version,
        uploadedAt: new Date(),
        isLatest: true
      }
    })
    
    // Mark previous versions as not latest
    await db.collection('fs.files').updateMany(
      { 
        filename: filename,
        'metadata.isLatest': true,
        _id: { $ne: uploadStream.id }
      },
      { $set: { 'metadata.isLatest': false } }
    )
    
    const fs = require('fs')
    const fileStream = fs.createReadStream(filePath)
    
    return new Promise((resolve, reject) => {
      fileStream
        .pipe(uploadStream)
        .on('error', reject)
        .on('finish', () => resolve(uploadStream.id))
    })
    
  } finally {
    await client.close()
  }
}

// Get latest version
async function getLatestVersion(dbName, filename) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    const files = await bucket.find({
      filename: filename,
      'metadata.isLatest': true
    }).toArray()
    
    return files[0] || null
    
  } finally {
    await client.close()
  }
}

// Get all versions
async function getAllVersions(dbName, filename) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    return await bucket.find({ filename })
      .sort({ uploadDate: -1 })
      .toArray()
    
  } finally {
    await client.close()
  }
}
```

### Checksum Verification

```javascript
const crypto = require('crypto')

// Upload with checksum
async function uploadWithChecksum(dbName, filePath, filename) {
  const client = new MongoClient('mongodb://localhost:27017')
  const fs = require('fs')
  
  try {
    // Calculate checksum first
    const hash = crypto.createHash('md5')
    const fileBuffer = fs.readFileSync(filePath)
    hash.update(fileBuffer)
    const checksum = hash.digest('hex')
    
    await client.connect()
    const db = client.db(dbName)
    const bucket = new GridFSBucket(db)
    
    const uploadStream = bucket.openUploadStream(filename, {
      metadata: {
        checksum: checksum,
        checksumAlgorithm: 'md5'
      }
    })
    
    const fileStream = fs.createReadStream(filePath)
    
    return new Promise((resolve, reject) => {
      fileStream
        .pipe(uploadStream)
        .on('error', reject)
        .on('finish', () => resolve({
          fileId: uploadStream.id,
          checksum: checksum
        }))
    })
    
  } finally {
    await client.close()
  }
}

// Verify downloaded file
async function verifyDownload(dbName, fileId, downloadPath) {
  const client = new MongoClient('mongodb://localhost:27017')
  const fs = require('fs')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    // Get stored checksum
    const fileDoc = await db.collection('fs.files').findOne({ _id: fileId })
    const storedChecksum = fileDoc.metadata?.checksum
    
    if (!storedChecksum) {
      console.log('No checksum stored for this file')
      return null
    }
    
    // Calculate checksum of downloaded file
    const hash = crypto.createHash('md5')
    const fileBuffer = fs.readFileSync(downloadPath)
    hash.update(fileBuffer)
    const calculatedChecksum = hash.digest('hex')
    
    const isValid = storedChecksum === calculatedChecksum
    
    console.log(`Stored: ${storedChecksum}`)
    console.log(`Calculated: ${calculatedChecksum}`)
    console.log(`Valid: ${isValid}`)
    
    return isValid
    
  } finally {
    await client.close()
  }
}
```

### Cleanup Orphan Chunks

```javascript
// Find and remove orphan chunks
async function cleanupOrphanChunks(dbName) {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db(dbName)
    
    // Get all file IDs
    const fileIds = await db.collection('fs.files')
      .distinct('_id')
    
    // Find chunks without corresponding files
    const orphanChunks = await db.collection('fs.chunks').find({
      files_id: { $nin: fileIds }
    }).toArray()
    
    console.log(`Found ${orphanChunks.length} orphan chunks`)
    
    if (orphanChunks.length > 0) {
      const result = await db.collection('fs.chunks').deleteMany({
        files_id: { $nin: fileIds }
      })
      
      console.log(`Deleted ${result.deletedCount} orphan chunks`)
    }
    
    return orphanChunks.length
    
  } finally {
    await client.close()
  }
}
```

---

## Summary

### GridFS Collections

| Collection | Purpose |
|------------|---------|
| fs.files | File metadata |
| fs.chunks | Binary data chunks |

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| chunkSize | 255 KB | Size of each chunk |
| bucketName | 'fs' | Collection prefix |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Use appropriate chunk size | Balance performance |
| Store checksums | Verify integrity |
| Index metadata fields | Fast queries |
| Clean up orphans | Save storage |
| Use streaming | Memory efficiency |

### GridFS vs Alternatives

| Criteria | GridFS | Object Storage (S3) |
|----------|--------|-------------------|
| Setup complexity | Low | Medium |
| Scalability | MongoDB limits | Virtually unlimited |
| Cost | Database storage | Separate service |
| Consistency | Strong | Eventual |
| Backup | With MongoDB | Separate |

---

## Practice Questions

1. What is the default chunk size in GridFS?
2. What are the two collections used by GridFS?
3. How do you store custom metadata with a file?
4. How do you implement partial reads in GridFS?
5. What is the purpose of the files_id field in chunks?
6. How do you stream a GridFS file as an HTTP response?
7. How do you implement file versioning with GridFS?
8. When should you consider alternatives to GridFS?

---

## Hands-On Exercises

### Exercise 1: GridFS File Manager

```javascript
// Complete GridFS file management system

class GridFSManager {
  constructor(connectionString, dbName, bucketName = 'fs') {
    this.connectionString = connectionString
    this.dbName = dbName
    this.bucketName = bucketName
    this.client = null
  }
  
  async connect() {
    const { MongoClient } = require('mongodb')
    this.client = new MongoClient(this.connectionString)
    await this.client.connect()
    this.db = this.client.db(this.dbName)
    this.bucket = new (require('mongodb').GridFSBucket)(this.db, {
      bucketName: this.bucketName
    })
  }
  
  async close() {
    if (this.client) {
      await this.client.close()
    }
  }
  
  // Upload file
  async upload(filePath, filename, metadata = {}) {
    const fs = require('fs')
    const crypto = require('crypto')
    
    // Calculate checksum
    const hash = crypto.createHash('sha256')
    const fileBuffer = fs.readFileSync(filePath)
    hash.update(fileBuffer)
    const checksum = hash.digest('hex')
    
    const uploadStream = this.bucket.openUploadStream(filename, {
      metadata: {
        ...metadata,
        checksum: checksum,
        originalPath: filePath,
        uploadedAt: new Date()
      }
    })
    
    const fileStream = fs.createReadStream(filePath)
    
    return new Promise((resolve, reject) => {
      fileStream
        .pipe(uploadStream)
        .on('error', reject)
        .on('finish', () => resolve({
          id: uploadStream.id,
          filename: filename,
          checksum: checksum
        }))
    })
  }
  
  // Download file
  async download(filename, outputPath) {
    const fs = require('fs')
    
    const downloadStream = this.bucket.openDownloadStreamByName(filename)
    const writeStream = fs.createWriteStream(outputPath)
    
    return new Promise((resolve, reject) => {
      downloadStream
        .pipe(writeStream)
        .on('error', reject)
        .on('finish', resolve)
    })
  }
  
  // List files with pagination
  async list(options = {}) {
    const { page = 1, limit = 20, filter = {} } = options
    
    const skip = (page - 1) * limit
    
    const files = await this.bucket.find(filter)
      .sort({ uploadDate: -1 })
      .skip(skip)
      .limit(limit)
      .toArray()
    
    const total = await this.db.collection(`${this.bucketName}.files`)
      .countDocuments(filter)
    
    return {
      files: files.map(f => ({
        id: f._id,
        filename: f.filename,
        size: f.length,
        uploadDate: f.uploadDate,
        metadata: f.metadata
      })),
      pagination: {
        page: page,
        limit: limit,
        total: total,
        pages: Math.ceil(total / limit)
      }
    }
  }
  
  // Delete file
  async delete(fileId) {
    await this.bucket.delete(fileId)
  }
  
  // Get file info
  async getInfo(filename) {
    const files = await this.bucket.find({ filename }).toArray()
    return files[0] || null
  }
  
  // Search files
  async search(query) {
    const regex = new RegExp(query, 'i')
    return await this.bucket.find({
      $or: [
        { filename: regex },
        { 'metadata.tags': regex }
      ]
    }).toArray()
  }
  
  // Get storage stats
  async getStats() {
    const filesStats = await this.db.collection(`${this.bucketName}.files`)
      .aggregate([
        { $group: {
          _id: null,
          totalFiles: { $sum: 1 },
          totalSize: { $sum: '$length' },
          avgSize: { $avg: '$length' }
        }}
      ]).toArray()
    
    return filesStats[0] || {
      totalFiles: 0,
      totalSize: 0,
      avgSize: 0
    }
  }
}

// Usage example
async function demo() {
  const manager = new GridFSManager('mongodb://localhost:27017', 'filestore')
  
  await manager.connect()
  
  // Upload
  const result = await manager.upload('./test.pdf', 'test.pdf', {
    contentType: 'application/pdf',
    tags: ['document', 'test']
  })
  console.log('Uploaded:', result)
  
  // List
  const files = await manager.list({ page: 1, limit: 10 })
  console.log('Files:', files)
  
  // Stats
  const stats = await manager.getStats()
  console.log('Stats:', stats)
  
  await manager.close()
}
```

### Exercise 2: Image Thumbnail Generator

```javascript
// Store images with auto-generated thumbnails

const sharp = require('sharp')  // npm install sharp

class ImageStore {
  constructor(client, dbName) {
    this.db = client.db(dbName)
    this.bucket = new (require('mongodb').GridFSBucket)(this.db, {
      bucketName: 'images'
    })
    this.thumbBucket = new (require('mongodb').GridFSBucket)(this.db, {
      bucketName: 'thumbnails'
    })
  }
  
  // Upload image with thumbnail
  async uploadImage(filePath, filename, options = {}) {
    const { thumbWidth = 200, thumbHeight = 200 } = options
    const fs = require('fs')
    
    // Get image info
    const imageInfo = await sharp(filePath).metadata()
    
    // Upload original
    const uploadStream = this.bucket.openUploadStream(filename, {
      metadata: {
        contentType: `image/${imageInfo.format}`,
        width: imageInfo.width,
        height: imageInfo.height,
        hasThumb: true
      }
    })
    
    const fileStream = fs.createReadStream(filePath)
    
    const originalId = await new Promise((resolve, reject) => {
      fileStream
        .pipe(uploadStream)
        .on('error', reject)
        .on('finish', () => resolve(uploadStream.id))
    })
    
    // Generate and upload thumbnail
    const thumbBuffer = await sharp(filePath)
      .resize(thumbWidth, thumbHeight, { fit: 'inside' })
      .toBuffer()
    
    const thumbStream = this.thumbBucket.openUploadStream(`thumb_${filename}`, {
      metadata: {
        originalId: originalId,
        width: thumbWidth,
        height: thumbHeight
      }
    })
    
    const thumbId = await new Promise((resolve, reject) => {
      thumbStream.end(thumbBuffer)
      thumbStream.on('error', reject)
      thumbStream.on('finish', () => resolve(thumbStream.id))
    })
    
    // Update original with thumb reference
    await this.db.collection('images.files').updateOne(
      { _id: originalId },
      { $set: { 'metadata.thumbnailId': thumbId } }
    )
    
    return {
      originalId,
      thumbnailId: thumbId,
      filename,
      dimensions: {
        original: { width: imageInfo.width, height: imageInfo.height },
        thumbnail: { width: thumbWidth, height: thumbHeight }
      }
    }
  }
  
  // Get image
  getImageStream(imageId) {
    return this.bucket.openDownloadStream(imageId)
  }
  
  // Get thumbnail
  getThumbnailStream(thumbnailId) {
    return this.thumbBucket.openDownloadStream(thumbnailId)
  }
  
  // Get thumbnail by original ID
  async getThumbnailByOriginal(originalId) {
    const file = await this.db.collection('images.files')
      .findOne({ _id: originalId })
    
    if (file?.metadata?.thumbnailId) {
      return this.thumbBucket.openDownloadStream(file.metadata.thumbnailId)
    }
    return null
  }
}
```

### Exercise 3: GridFS Statistics Dashboard

```javascript
// GridFS storage statistics

function gridFSStats(bucketName = 'fs') {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              GRIDFS STATISTICS                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const filesCollection = `${bucketName}.files`
  const chunksCollection = `${bucketName}.chunks`
  
  // File statistics
  const fileStats = db.getCollection(filesCollection).aggregate([
    { $group: {
      _id: null,
      totalFiles: { $sum: 1 },
      totalSize: { $sum: '$length' },
      avgSize: { $avg: '$length' },
      minSize: { $min: '$length' },
      maxSize: { $max: '$length' }
    }}
  ]).toArray()[0] || { totalFiles: 0, totalSize: 0 }
  
  print("┌─ FILE STATISTICS ─────────────────────────────────────────┐")
  print(`│  Total Files: ${fileStats.totalFiles}`.padEnd(60) + "│")
  print(`│  Total Size: ${(fileStats.totalSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Average Size: ${(fileStats.avgSize / 1024).toFixed(2)} KB`.padEnd(60) + "│")
  print(`│  Min Size: ${(fileStats.minSize / 1024).toFixed(2)} KB`.padEnd(60) + "│")
  print(`│  Max Size: ${(fileStats.maxSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Chunk statistics
  const chunkStats = db.getCollection(chunksCollection).aggregate([
    { $group: {
      _id: null,
      totalChunks: { $sum: 1 },
      avgChunkSize: { $avg: { $bsonSize: '$data' } }
    }}
  ]).toArray()[0] || { totalChunks: 0 }
  
  print("┌─ CHUNK STATISTICS ────────────────────────────────────────┐")
  print(`│  Total Chunks: ${chunkStats.totalChunks}`.padEnd(60) + "│")
  print(`│  Average Chunk Size: ${((chunkStats.avgChunkSize || 0) / 1024).toFixed(2)} KB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Files by content type
  const byType = db.getCollection(filesCollection).aggregate([
    { $group: {
      _id: '$metadata.contentType',
      count: { $sum: 1 },
      totalSize: { $sum: '$length' }
    }},
    { $sort: { totalSize: -1 } },
    { $limit: 5 }
  ]).toArray()
  
  if (byType.length > 0) {
    print("┌─ TOP CONTENT TYPES ───────────────────────────────────────┐")
    byType.forEach(t => {
      const type = (t._id || 'unknown').substring(0, 25).padEnd(27)
      const count = String(t.count).padStart(5)
      const size = ((t.totalSize / 1024 / 1024).toFixed(2) + ' MB').padStart(12)
      print(`│  ${type} ${count} files  ${size} │`)
    })
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Recent uploads
  const recent = db.getCollection(filesCollection).find()
    .sort({ uploadDate: -1 })
    .limit(5)
    .toArray()
  
  if (recent.length > 0) {
    print("┌─ RECENT UPLOADS ──────────────────────────────────────────┐")
    recent.forEach(f => {
      const date = f.uploadDate.toISOString().substring(0, 10)
      const name = f.filename.substring(0, 30).padEnd(32)
      const size = ((f.length / 1024).toFixed(1) + ' KB').padStart(12)
      print(`│  ${date}  ${name} ${size} │`)
    })
    print("└────────────────────────────────────────────────────────────┘")
  }
  
  return { fileStats, chunkStats, byType }
}

// Run statistics
gridFSStats()
```

---

[← Previous: Change Streams](61-change-streams.md) | [Next: Time Series Collections →](63-time-series.md)
