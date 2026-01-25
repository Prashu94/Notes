# Chapter 63: Time Series Collections

## Table of Contents
- [Time Series Overview](#time-series-overview)
- [Creating Time Series Collections](#creating-time-series-collections)
- [Data Insertion](#data-insertion)
- [Querying Time Series Data](#querying-time-series-data)
- [Window Functions](#window-functions)
- [Performance Optimization](#performance-optimization)
- [Summary](#summary)

---

## Time Series Overview

### What is Time Series Data?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Time Series Data Concept                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Time series data is a sequence of data points indexed by time.    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Sensor Temperature                       │   │
│  │  °C                                                          │   │
│  │  25 ─      ●                        ●                        │   │
│  │     │    ●   ●                    ●   ●                      │   │
│  │  20 ─  ●       ●      ●●        ●       ●                    │   │
│  │     │            ●  ●    ●    ●          ●●                  │   │
│  │  15 ─              ●        ●               ●                │   │
│  │     │                                        ●●              │   │
│  │  10 ─                                          ●             │   │
│  │     └────────────────────────────────────────────────────    │   │
│  │       00:00  04:00  08:00  12:00  16:00  20:00  24:00        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Characteristics:                                                  │
│  • Timestamp is primary key                                        │
│  • Data arrives chronologically                                    │
│  • Rarely updated after insertion                                  │
│  • Often queried by time ranges                                    │
│  • High write throughput required                                  │
│                                                                     │
│  Common Use Cases:                                                 │
│  • IoT sensor readings                                             │
│  • Stock market prices                                             │
│  • Application metrics                                             │
│  • Server logs                                                     │
│  • Weather data                                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Time Series Collections Benefits

```
┌─────────────────────────────────────────────────────────────────────┐
│              Time Series Collection Architecture                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Regular Collection:                                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Document 1: { ts, metadata, value }                          │  │
│  │ Document 2: { ts, metadata, value }                          │  │
│  │ Document 3: { ts, metadata, value }                          │  │
│  │ ...thousands of individual documents                         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Time Series Collection:                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Bucket 1 (1 hour window):                                    │  │
│  │ { meta, min_ts, max_ts,                                      │  │
│  │   data: [val1, val2, val3, ...] }  // Compressed             │  │
│  │                                                               │  │
│  │ Bucket 2 (1 hour window):                                    │  │
│  │ { meta, min_ts, max_ts,                                      │  │
│  │   data: [val1, val2, val3, ...] }                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Benefits:                                                         │
│  ✓ Automatic bucketing                                             │
│  ✓ Columnar compression                                            │
│  ✓ 10x+ storage reduction                                          │
│  ✓ Faster aggregation queries                                      │
│  ✓ Built-in TTL support                                            │
│  ✓ Optimized indexes                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Creating Time Series Collections

### Basic Creation

```javascript
// Create time series collection
db.createCollection("sensorData", {
  timeseries: {
    timeField: "timestamp",        // Required: field containing timestamp
    metaField: "metadata",         // Optional: field containing metadata
    granularity: "seconds"         // Optional: time bucket granularity
  }
})

// Verify creation
db.sensorData.find().explain()
```

### Time Series Options

```javascript
// Complete options example
db.createCollection("weatherData", {
  timeseries: {
    timeField: "timestamp",
    metaField: "sensorInfo",
    granularity: "minutes"       // "seconds", "minutes", or "hours"
  },
  expireAfterSeconds: 86400 * 90  // 90 days TTL
})
```

### Granularity Options

| Granularity | Bucket Time Span | Best For |
|-------------|------------------|----------|
| seconds | 1 hour | High-frequency data (1+ per second) |
| minutes | 24 hours | Medium frequency (1 per minute) |
| hours | 30 days | Low frequency (1 per hour or less) |

```javascript
// High-frequency sensor data
db.createCollection("highFreqSensors", {
  timeseries: {
    timeField: "ts",
    metaField: "sensor",
    granularity: "seconds"  // Data every second or faster
  }
})

// Hourly metrics
db.createCollection("hourlyMetrics", {
  timeseries: {
    timeField: "hour",
    metaField: "server",
    granularity: "hours"  // Data every hour
  }
})
```

### BucketMaxSpan and BucketRounding (MongoDB 6.3+)

```javascript
// Custom bucket configuration
db.createCollection("customBuckets", {
  timeseries: {
    timeField: "timestamp",
    metaField: "device",
    bucketMaxSpanSeconds: 3600,     // 1 hour max span
    bucketRoundingSeconds: 3600     // Round to hour boundaries
  }
})
```

---

## Data Insertion

### Inserting Time Series Data

```javascript
// Single document insert
db.sensorData.insertOne({
  timestamp: new Date(),
  metadata: {
    sensorId: "sensor-001",
    location: "building-a",
    type: "temperature"
  },
  temperature: 23.5,
  humidity: 45.2,
  pressure: 1013.25
})

// Bulk insert
db.sensorData.insertMany([
  {
    timestamp: new Date("2024-01-15T10:00:00Z"),
    metadata: { sensorId: "sensor-001", location: "building-a" },
    temperature: 22.1
  },
  {
    timestamp: new Date("2024-01-15T10:01:00Z"),
    metadata: { sensorId: "sensor-001", location: "building-a" },
    temperature: 22.3
  },
  {
    timestamp: new Date("2024-01-15T10:02:00Z"),
    metadata: { sensorId: "sensor-002", location: "building-b" },
    temperature: 21.8
  }
])
```

### Metadata Field Best Practices

```javascript
// Good: Metadata identifies the measurement source
{
  timestamp: new Date(),
  metadata: {
    deviceId: "device-123",
    region: "us-west",
    type: "temperature"
  },
  value: 25.5
}

// Bad: Putting changing data in metadata
{
  timestamp: new Date(),
  metadata: {
    deviceId: "device-123",
    currentReading: 25.5  // Don't put measurements in metadata!
  }
}
```

### Efficient Bulk Loading

```javascript
// Generate test data
function generateSensorData(sensorId, startDate, count) {
  const data = []
  const baseTemp = 20 + Math.random() * 10
  
  for (let i = 0; i < count; i++) {
    const timestamp = new Date(startDate.getTime() + i * 60000) // 1 minute intervals
    data.push({
      timestamp: timestamp,
      metadata: {
        sensorId: sensorId,
        location: "datacenter-1"
      },
      temperature: baseTemp + (Math.random() - 0.5) * 5,
      humidity: 40 + Math.random() * 20,
      cpuUsage: Math.random() * 100
    })
  }
  
  return data
}

// Bulk insert with ordered: false for better performance
const data = generateSensorData("sensor-001", new Date("2024-01-01"), 10000)

db.sensorData.insertMany(data, { ordered: false })
```

---

## Querying Time Series Data

### Basic Time Range Queries

```javascript
// Query last hour
db.sensorData.find({
  timestamp: {
    $gte: new Date(Date.now() - 3600000),  // 1 hour ago
    $lt: new Date()
  }
})

// Query specific sensor in time range
db.sensorData.find({
  "metadata.sensorId": "sensor-001",
  timestamp: {
    $gte: ISODate("2024-01-15T00:00:00Z"),
    $lt: ISODate("2024-01-16T00:00:00Z")
  }
}).sort({ timestamp: 1 })
```

### Aggregation Queries

```javascript
// Hourly averages
db.sensorData.aggregate([
  {
    $match: {
      "metadata.sensorId": "sensor-001",
      timestamp: {
        $gte: ISODate("2024-01-15T00:00:00Z"),
        $lt: ISODate("2024-01-16T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: {
        year: { $year: "$timestamp" },
        month: { $month: "$timestamp" },
        day: { $dayOfMonth: "$timestamp" },
        hour: { $hour: "$timestamp" }
      },
      avgTemperature: { $avg: "$temperature" },
      minTemperature: { $min: "$temperature" },
      maxTemperature: { $max: "$temperature" },
      count: { $sum: 1 }
    }
  },
  { $sort: { "_id.hour": 1 } }
])

// Daily statistics by sensor
db.sensorData.aggregate([
  {
    $match: {
      timestamp: {
        $gte: ISODate("2024-01-01T00:00:00Z"),
        $lt: ISODate("2024-02-01T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: {
        sensor: "$metadata.sensorId",
        date: { $dateToString: { format: "%Y-%m-%d", date: "$timestamp" } }
      },
      avgTemp: { $avg: "$temperature" },
      avgHumidity: { $avg: "$humidity" },
      readings: { $sum: 1 }
    }
  },
  {
    $sort: { "_id.sensor": 1, "_id.date": 1 }
  }
])
```

### Date Bucketing with $dateTrunc

```javascript
// MongoDB 5.0+ date truncation
db.sensorData.aggregate([
  {
    $match: {
      "metadata.sensorId": "sensor-001",
      timestamp: {
        $gte: ISODate("2024-01-15T00:00:00Z"),
        $lt: ISODate("2024-01-16T00:00:00Z")
      }
    }
  },
  {
    $group: {
      _id: {
        $dateTrunc: {
          date: "$timestamp",
          unit: "hour",
          binSize: 1
        }
      },
      avgTemperature: { $avg: "$temperature" },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])

// 15-minute buckets
db.sensorData.aggregate([
  {
    $group: {
      _id: {
        $dateTrunc: {
          date: "$timestamp",
          unit: "minute",
          binSize: 15
        }
      },
      avgTemperature: { $avg: "$temperature" }
    }
  },
  { $sort: { _id: 1 } }
])
```

### Finding Anomalies

```javascript
// Find readings outside normal range
db.sensorData.aggregate([
  {
    $match: {
      "metadata.type": "temperature",
      timestamp: { $gte: ISODate("2024-01-01T00:00:00Z") }
    }
  },
  {
    $group: {
      _id: "$metadata.sensorId",
      avgTemp: { $avg: "$temperature" },
      stdDev: { $stdDevPop: "$temperature" }
    }
  },
  {
    $lookup: {
      from: "sensorData",
      let: { sensor: "$_id", avg: "$avgTemp", std: "$stdDev" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$metadata.sensorId", "$$sensor"] },
                {
                  $or: [
                    { $gt: ["$temperature", { $add: ["$$avg", { $multiply: ["$$std", 3] }] }] },
                    { $lt: ["$temperature", { $subtract: ["$$avg", { $multiply: ["$$std", 3] }] }] }
                  ]
                }
              ]
            }
          }
        }
      ],
      as: "anomalies"
    }
  }
])
```

---

## Window Functions

### Moving Average

```javascript
// Calculate moving average using $setWindowFields
db.sensorData.aggregate([
  {
    $match: {
      "metadata.sensorId": "sensor-001",
      timestamp: {
        $gte: ISODate("2024-01-15T00:00:00Z"),
        $lt: ISODate("2024-01-16T00:00:00Z")
      }
    }
  },
  {
    $setWindowFields: {
      partitionBy: "$metadata.sensorId",
      sortBy: { timestamp: 1 },
      output: {
        movingAvg: {
          $avg: "$temperature",
          window: {
            documents: [-5, 0]  // Current and 5 previous
          }
        },
        movingSum: {
          $sum: "$temperature",
          window: {
            documents: [-5, 0]
          }
        }
      }
    }
  },
  {
    $project: {
      timestamp: 1,
      temperature: 1,
      movingAvg: { $round: ["$movingAvg", 2] },
      movingSum: { $round: ["$movingSum", 2] }
    }
  }
])
```

### Time-Based Windows

```javascript
// Rolling average over time range
db.sensorData.aggregate([
  {
    $match: {
      "metadata.sensorId": "sensor-001"
    }
  },
  {
    $setWindowFields: {
      partitionBy: "$metadata.sensorId",
      sortBy: { timestamp: 1 },
      output: {
        rollingAvg: {
          $avg: "$temperature",
          window: {
            range: [-1, 0],  // 1 hour before to current
            unit: "hour"
          }
        }
      }
    }
  }
])

// Calculate hourly change
db.sensorData.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$metadata.sensorId",
      sortBy: { timestamp: 1 },
      output: {
        prevTemp: {
          $first: "$temperature",
          window: {
            range: [-1, -1],  // Exactly 1 hour ago
            unit: "hour"
          }
        }
      }
    }
  },
  {
    $addFields: {
      hourlyChange: {
        $subtract: ["$temperature", "$prevTemp"]
      }
    }
  }
])
```

### Cumulative Calculations

```javascript
// Cumulative sum
db.sensorData.aggregate([
  {
    $match: {
      "metadata.type": "energy"
    }
  },
  {
    $setWindowFields: {
      partitionBy: "$metadata.deviceId",
      sortBy: { timestamp: 1 },
      output: {
        cumulativeEnergy: {
          $sum: "$energyUsage",
          window: {
            documents: ["unbounded", "current"]
          }
        },
        runningCount: {
          $sum: 1,
          window: {
            documents: ["unbounded", "current"]
          }
        }
      }
    }
  }
])

// Rank readings
db.sensorData.aggregate([
  {
    $match: {
      "metadata.sensorId": "sensor-001"
    }
  },
  {
    $setWindowFields: {
      partitionBy: {
        $dateToString: { format: "%Y-%m-%d", date: "$timestamp" }
      },
      sortBy: { temperature: -1 },
      output: {
        dailyRank: { $rank: {} },
        dailyDenseRank: { $denseRank: {} },
        percentile: {
          $percentRank: {}
        }
      }
    }
  }
])
```

### Derivative Calculations

```javascript
// Rate of change
db.sensorData.aggregate([
  {
    $match: {
      "metadata.sensorId": "sensor-001"
    }
  },
  {
    $setWindowFields: {
      partitionBy: "$metadata.sensorId",
      sortBy: { timestamp: 1 },
      output: {
        prevTemp: {
          $shift: {
            output: "$temperature",
            by: -1
          }
        },
        prevTime: {
          $shift: {
            output: "$timestamp",
            by: -1
          }
        }
      }
    }
  },
  {
    $addFields: {
      derivative: {
        $cond: {
          if: { $eq: ["$prevTemp", null] },
          then: 0,
          else: {
            $divide: [
              { $subtract: ["$temperature", "$prevTemp"] },
              { 
                $divide: [
                  { $subtract: ["$timestamp", "$prevTime"] },
                  60000  // Convert ms to minutes
                ]
              }
            ]
          }
        }
      }
    }
  },
  {
    $project: {
      timestamp: 1,
      temperature: 1,
      derivative: { $round: ["$derivative", 4] }  // °C per minute
    }
  }
])
```

---

## Performance Optimization

### Index Strategies

```javascript
// Compound index on metadata and time
db.sensorData.createIndex(
  { "metadata.sensorId": 1, timestamp: -1 }
)

// Index for location-based queries
db.sensorData.createIndex(
  { "metadata.location": 1, timestamp: -1 }
)

// Check indexes
db.sensorData.getIndexes()
```

### TTL Configuration

```javascript
// Set expiration at creation
db.createCollection("metricsData", {
  timeseries: {
    timeField: "timestamp",
    metaField: "server",
    granularity: "minutes"
  },
  expireAfterSeconds: 2592000  // 30 days
})

// Modify TTL on existing collection
db.runCommand({
  collMod: "metricsData",
  expireAfterSeconds: 604800  // Change to 7 days
})
```

### Query Optimization

```javascript
// Use explain to analyze query performance
db.sensorData.find({
  "metadata.sensorId": "sensor-001",
  timestamp: {
    $gte: ISODate("2024-01-15T00:00:00Z"),
    $lt: ISODate("2024-01-16T00:00:00Z")
  }
}).explain("executionStats")

// Optimize aggregation with $match early
db.sensorData.aggregate([
  // Filter first to reduce documents
  {
    $match: {
      "metadata.sensorId": "sensor-001",
      timestamp: {
        $gte: ISODate("2024-01-15T00:00:00Z"),
        $lt: ISODate("2024-01-16T00:00:00Z")
      }
    }
  },
  // Then aggregate
  {
    $group: {
      _id: { $hour: "$timestamp" },
      avgTemp: { $avg: "$temperature" }
    }
  }
])
```

### Downsampling for Historical Data

```javascript
// Create downsampled collection for historical data
db.createCollection("sensorDataHourly", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "hours"
  }
})

// Downsample data periodically
function downsampleHourly(startDate, endDate) {
  db.sensorData.aggregate([
    {
      $match: {
        timestamp: { $gte: startDate, $lt: endDate }
      }
    },
    {
      $group: {
        _id: {
          sensor: "$metadata.sensorId",
          hour: {
            $dateTrunc: {
              date: "$timestamp",
              unit: "hour"
            }
          }
        },
        avgTemp: { $avg: "$temperature" },
        minTemp: { $min: "$temperature" },
        maxTemp: { $max: "$temperature" },
        avgHumidity: { $avg: "$humidity" },
        sampleCount: { $sum: 1 }
      }
    },
    {
      $project: {
        _id: 0,
        timestamp: "$_id.hour",
        metadata: { sensorId: "$_id.sensor" },
        temperature: {
          avg: { $round: ["$avgTemp", 2] },
          min: { $round: ["$minTemp", 2] },
          max: { $round: ["$maxTemp", 2] }
        },
        humidity: { $round: ["$avgHumidity", 2] },
        sampleCount: 1
      }
    },
    {
      $merge: {
        into: "sensorDataHourly",
        whenMatched: "replace",
        whenNotMatched: "insert"
      }
    }
  ])
}
```

---

## Summary

### Time Series Collection Options

| Option | Description |
|--------|-------------|
| timeField | Field containing the timestamp (required) |
| metaField | Field containing metadata |
| granularity | Bucket granularity (seconds, minutes, hours) |
| expireAfterSeconds | TTL for automatic deletion |
| bucketMaxSpanSeconds | Custom bucket span |
| bucketRoundingSeconds | Bucket boundary rounding |

### Window Function Types

| Function | Description |
|----------|-------------|
| $avg, $sum, $min, $max | Statistical calculations |
| $rank, $denseRank | Ranking within partitions |
| $percentRank | Percentile calculations |
| $shift | Access previous/next values |
| $first, $last | First/last in window |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Choose correct granularity | Optimal bucket sizes |
| Use metadata field | Efficient grouping |
| Index metadata + time | Fast queries |
| Use TTL | Automatic cleanup |
| Downsample old data | Storage efficiency |
| Early $match in pipelines | Query optimization |

---

## Practice Questions

1. What is the difference between granularity options?
2. What should be stored in the metaField?
3. How do time series collections achieve storage efficiency?
4. What is $dateTrunc used for?
5. How do you calculate a moving average?
6. How do you implement TTL on time series data?
7. What is downsampling and when should you use it?
8. How do window functions differ from regular aggregation?

---

## Hands-On Exercises

### Exercise 1: IoT Sensor Dashboard

```javascript
// Complete IoT monitoring system

// Create collections
db.createCollection("iotSensors", {
  timeseries: {
    timeField: "timestamp",
    metaField: "device",
    granularity: "seconds"
  },
  expireAfterSeconds: 86400 * 30  // 30 days retention
})

// Create indexes
db.iotSensors.createIndex({ "device.id": 1, timestamp: -1 })
db.iotSensors.createIndex({ "device.type": 1, timestamp: -1 })

// Insert sample data
function generateIoTData(deviceId, deviceType, count) {
  const data = []
  const startTime = new Date(Date.now() - count * 60000)
  
  for (let i = 0; i < count; i++) {
    data.push({
      timestamp: new Date(startTime.getTime() + i * 60000),
      device: {
        id: deviceId,
        type: deviceType,
        location: "datacenter-1"
      },
      temperature: 20 + Math.random() * 15,
      humidity: 30 + Math.random() * 40,
      powerConsumption: 50 + Math.random() * 100
    })
  }
  
  return data
}

// Insert data for multiple devices
['device-001', 'device-002', 'device-003'].forEach(deviceId => {
  const data = generateIoTData(deviceId, 'server', 1440)  // 24 hours
  db.iotSensors.insertMany(data, { ordered: false })
})

// Dashboard queries

// 1. Current status of all devices
function getCurrentStatus() {
  return db.iotSensors.aggregate([
    {
      $sort: { timestamp: -1 }
    },
    {
      $group: {
        _id: "$device.id",
        lastReading: { $first: "$$ROOT" }
      }
    },
    {
      $replaceRoot: { newRoot: "$lastReading" }
    },
    {
      $project: {
        deviceId: "$device.id",
        timestamp: 1,
        temperature: { $round: ["$temperature", 1] },
        humidity: { $round: ["$humidity", 1] },
        powerConsumption: { $round: ["$powerConsumption", 1] }
      }
    }
  ]).toArray()
}

// 2. Hourly statistics
function getHourlyStats(deviceId) {
  return db.iotSensors.aggregate([
    {
      $match: {
        "device.id": deviceId,
        timestamp: {
          $gte: new Date(Date.now() - 86400000)  // Last 24 hours
        }
      }
    },
    {
      $group: {
        _id: {
          $dateTrunc: {
            date: "$timestamp",
            unit: "hour"
          }
        },
        avgTemp: { $avg: "$temperature" },
        minTemp: { $min: "$temperature" },
        maxTemp: { $max: "$temperature" },
        avgPower: { $avg: "$powerConsumption" },
        readings: { $sum: 1 }
      }
    },
    {
      $sort: { _id: 1 }
    },
    {
      $project: {
        hour: "$_id",
        temperature: {
          avg: { $round: ["$avgTemp", 1] },
          min: { $round: ["$minTemp", 1] },
          max: { $round: ["$maxTemp", 1] }
        },
        avgPower: { $round: ["$avgPower", 1] },
        readings: 1
      }
    }
  ]).toArray()
}

// 3. Anomaly detection
function detectAnomalies(threshold = 2) {
  return db.iotSensors.aggregate([
    {
      $match: {
        timestamp: { $gte: new Date(Date.now() - 3600000) }  // Last hour
      }
    },
    {
      $setWindowFields: {
        partitionBy: "$device.id",
        sortBy: { timestamp: 1 },
        output: {
          avgTemp: {
            $avg: "$temperature",
            window: { documents: [-30, 0] }
          },
          stdTemp: {
            $stdDevPop: "$temperature",
            window: { documents: [-30, 0] }
          }
        }
      }
    },
    {
      $addFields: {
        zScore: {
          $cond: {
            if: { $eq: ["$stdTemp", 0] },
            then: 0,
            else: {
              $abs: {
                $divide: [
                  { $subtract: ["$temperature", "$avgTemp"] },
                  "$stdTemp"
                ]
              }
            }
          }
        }
      }
    },
    {
      $match: {
        zScore: { $gt: threshold }
      }
    },
    {
      $project: {
        deviceId: "$device.id",
        timestamp: 1,
        temperature: 1,
        avgTemp: { $round: ["$avgTemp", 2] },
        zScore: { $round: ["$zScore", 2] }
      }
    }
  ]).toArray()
}

// Test queries
print("Current Status:")
printjson(getCurrentStatus())

print("\nHourly Stats for device-001:")
printjson(getHourlyStats("device-001"))

print("\nAnomalies:")
printjson(detectAnomalies())
```

### Exercise 2: Stock Price Analysis

```javascript
// Stock market time series analysis

// Create collection
db.createCollection("stockPrices", {
  timeseries: {
    timeField: "timestamp",
    metaField: "symbol",
    granularity: "seconds"
  }
})

// Generate sample stock data
function generateStockData(symbol, days) {
  const data = []
  let price = 100 + Math.random() * 100  // Starting price
  const startDate = new Date(Date.now() - days * 86400000)
  
  // 390 minutes per trading day (9:30 AM - 4:00 PM)
  for (let day = 0; day < days; day++) {
    const dayStart = new Date(startDate.getTime() + day * 86400000)
    dayStart.setHours(9, 30, 0, 0)
    
    for (let minute = 0; minute < 390; minute++) {
      // Random walk with mean reversion
      const change = (Math.random() - 0.5) * 2 + (100 - price) * 0.001
      price = Math.max(1, price + change)
      
      const volume = Math.floor(1000 + Math.random() * 10000)
      
      data.push({
        timestamp: new Date(dayStart.getTime() + minute * 60000),
        symbol: { ticker: symbol, exchange: "NYSE" },
        open: price - Math.random() * 0.5,
        high: price + Math.random() * 0.5,
        low: price - Math.random() * 0.5,
        close: price,
        volume: volume
      })
    }
  }
  
  return data
}

// Insert data
['AAPL', 'GOOGL', 'MSFT'].forEach(symbol => {
  const data = generateStockData(symbol, 5)  // 5 days
  db.stockPrices.insertMany(data, { ordered: false })
})

// Technical analysis queries

// 1. Calculate VWAP (Volume Weighted Average Price)
function calculateVWAP(symbol, date) {
  const startOfDay = new Date(date)
  startOfDay.setHours(0, 0, 0, 0)
  const endOfDay = new Date(startOfDay.getTime() + 86400000)
  
  return db.stockPrices.aggregate([
    {
      $match: {
        "symbol.ticker": symbol,
        timestamp: { $gte: startOfDay, $lt: endOfDay }
      }
    },
    {
      $setWindowFields: {
        sortBy: { timestamp: 1 },
        output: {
          cumVolumePrice: {
            $sum: { $multiply: ["$close", "$volume"] },
            window: { documents: ["unbounded", "current"] }
          },
          cumVolume: {
            $sum: "$volume",
            window: { documents: ["unbounded", "current"] }
          }
        }
      }
    },
    {
      $addFields: {
        vwap: { $divide: ["$cumVolumePrice", "$cumVolume"] }
      }
    },
    {
      $project: {
        timestamp: 1,
        close: { $round: ["$close", 2] },
        volume: 1,
        vwap: { $round: ["$vwap", 2] }
      }
    }
  ]).toArray()
}

// 2. Moving averages (SMA)
function calculateSMA(symbol, periods = [5, 20, 50]) {
  return db.stockPrices.aggregate([
    {
      $match: { "symbol.ticker": symbol }
    },
    {
      $setWindowFields: {
        sortBy: { timestamp: 1 },
        output: Object.fromEntries(
          periods.map(p => [
            `sma${p}`,
            {
              $avg: "$close",
              window: { documents: [-(p-1), 0] }
            }
          ])
        )
      }
    },
    {
      $project: {
        timestamp: 1,
        close: { $round: ["$close", 2] },
        ...Object.fromEntries(
          periods.map(p => [`sma${p}`, { $round: [`$sma${p}`, 2] }])
        )
      }
    }
  ]).toArray()
}

// 3. Daily OHLC summary
function getDailyOHLC(symbol) {
  return db.stockPrices.aggregate([
    {
      $match: { "symbol.ticker": symbol }
    },
    {
      $group: {
        _id: {
          $dateToString: { format: "%Y-%m-%d", date: "$timestamp" }
        },
        open: { $first: "$open" },
        high: { $max: "$high" },
        low: { $min: "$low" },
        close: { $last: "$close" },
        volume: { $sum: "$volume" },
        trades: { $sum: 1 }
      }
    },
    {
      $sort: { _id: 1 }
    },
    {
      $project: {
        date: "$_id",
        open: { $round: ["$open", 2] },
        high: { $round: ["$high", 2] },
        low: { $round: ["$low", 2] },
        close: { $round: ["$close", 2] },
        volume: 1,
        trades: 1
      }
    }
  ]).toArray()
}

// 4. Bollinger Bands
function calculateBollingerBands(symbol, period = 20, multiplier = 2) {
  return db.stockPrices.aggregate([
    {
      $match: { "symbol.ticker": symbol }
    },
    {
      $setWindowFields: {
        sortBy: { timestamp: 1 },
        output: {
          sma: {
            $avg: "$close",
            window: { documents: [-(period-1), 0] }
          },
          stdDev: {
            $stdDevPop: "$close",
            window: { documents: [-(period-1), 0] }
          }
        }
      }
    },
    {
      $addFields: {
        upperBand: { $add: ["$sma", { $multiply: ["$stdDev", multiplier] }] },
        lowerBand: { $subtract: ["$sma", { $multiply: ["$stdDev", multiplier] }] }
      }
    },
    {
      $project: {
        timestamp: 1,
        close: { $round: ["$close", 2] },
        sma: { $round: ["$sma", 2] },
        upperBand: { $round: ["$upperBand", 2] },
        lowerBand: { $round: ["$lowerBand", 2] }
      }
    }
  ]).toArray()
}

// Test
print("Daily OHLC for AAPL:")
printjson(getDailyOHLC("AAPL"))

print("\nBollinger Bands sample:")
const bb = calculateBollingerBands("AAPL")
printjson(bb.slice(-5))  // Last 5 readings
```

### Exercise 3: Time Series Statistics Report

```javascript
// Comprehensive time series statistics

function timeSeriesReport(collectionName, timeField, metaField) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║            TIME SERIES STATISTICS REPORT                    ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const collection = db.getCollection(collectionName)
  
  // Basic stats
  const basicStats = collection.aggregate([
    {
      $group: {
        _id: null,
        totalDocuments: { $sum: 1 },
        firstTimestamp: { $min: `$${timeField}` },
        lastTimestamp: { $max: `$${timeField}` }
      }
    }
  ]).toArray()[0] || {}
  
  const duration = basicStats.lastTimestamp 
    ? (basicStats.lastTimestamp - basicStats.firstTimestamp) / 86400000 
    : 0
  
  print("┌─ OVERVIEW ────────────────────────────────────────────────┐")
  print(`│  Total Documents: ${basicStats.totalDocuments || 0}`.padEnd(60) + "│")
  print(`│  First Timestamp: ${basicStats.firstTimestamp?.toISOString() || 'N/A'}`.padEnd(60) + "│")
  print(`│  Last Timestamp: ${basicStats.lastTimestamp?.toISOString() || 'N/A'}`.padEnd(60) + "│")
  print(`│  Time Span: ${duration.toFixed(2)} days`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Data frequency
  if (basicStats.totalDocuments > 1) {
    const avgInterval = duration * 86400 / basicStats.totalDocuments  // seconds
    
    let frequency = ''
    if (avgInterval < 1) frequency = `${(1/avgInterval).toFixed(0)} per second`
    else if (avgInterval < 60) frequency = `Every ${avgInterval.toFixed(1)} seconds`
    else if (avgInterval < 3600) frequency = `Every ${(avgInterval/60).toFixed(1)} minutes`
    else frequency = `Every ${(avgInterval/3600).toFixed(1)} hours`
    
    print("┌─ DATA FREQUENCY ──────────────────────────────────────────┐")
    print(`│  Average Frequency: ${frequency}`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Meta field distribution
  if (metaField) {
    const metaStats = collection.aggregate([
      {
        $group: {
          _id: `$${metaField}`,
          count: { $sum: 1 }
        }
      },
      { $sort: { count: -1 } },
      { $limit: 10 }
    ]).toArray()
    
    if (metaStats.length > 0) {
      print("┌─ TOP METADATA VALUES ─────────────────────────────────────┐")
      metaStats.forEach(m => {
        const metaStr = JSON.stringify(m._id).substring(0, 35).padEnd(37)
        const countStr = String(m.count).padStart(8)
        print(`│  ${metaStr} ${countStr} docs │`)
      })
      print("└────────────────────────────────────────────────────────────┘\n")
    }
  }
  
  // Hourly distribution
  const hourlyDist = collection.aggregate([
    {
      $group: {
        _id: { $hour: `$${timeField}` },
        count: { $sum: 1 }
      }
    },
    { $sort: { _id: 1 } }
  ]).toArray()
  
  if (hourlyDist.length > 0) {
    const maxCount = Math.max(...hourlyDist.map(h => h.count))
    
    print("┌─ HOURLY DISTRIBUTION ─────────────────────────────────────┐")
    hourlyDist.forEach(h => {
      const hour = String(h._id).padStart(2, '0')
      const barLength = Math.round(h.count / maxCount * 30)
      const bar = '█'.repeat(barLength).padEnd(30)
      const count = String(h.count).padStart(8)
      print(`│  ${hour}:00 ${bar} ${count} │`)
    })
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Storage info
  const stats = collection.stats()
  const sizeMB = (stats.size / 1024 / 1024).toFixed(2)
  const storageSizeMB = (stats.storageSize / 1024 / 1024).toFixed(2)
  const compressionRatio = stats.size > 0 
    ? (stats.storageSize / stats.size * 100).toFixed(1) 
    : 100
  
  print("┌─ STORAGE ─────────────────────────────────────────────────┐")
  print(`│  Data Size: ${sizeMB} MB`.padEnd(60) + "│")
  print(`│  Storage Size: ${storageSizeMB} MB`.padEnd(60) + "│")
  print(`│  Compression Ratio: ${compressionRatio}%`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
}

// Run report
timeSeriesReport("sensorData", "timestamp", "metadata")
```

---

[← Previous: GridFS](62-gridfs.md) | [Next: Capped Collections →](64-capped-collections.md)
