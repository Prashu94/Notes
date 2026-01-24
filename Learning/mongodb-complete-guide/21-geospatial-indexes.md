# Chapter 21: Geospatial Indexes

## Table of Contents
- [Introduction to Geospatial Indexes](#introduction-to-geospatial-indexes)
- [GeoJSON Objects](#geojson-objects)
- [2dsphere Index](#2dsphere-index)
- [2d Index](#2d-index)
- [Geospatial Query Operators](#geospatial-query-operators)
- [Proximity Queries](#proximity-queries)
- [Intersection Queries](#intersection-queries)
- [Aggregation with Geospatial](#aggregation-with-geospatial)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Introduction to Geospatial Indexes

MongoDB provides geospatial indexes to support queries for location data, enabling proximity searches, containment queries, and intersection operations.

### Index Types Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                Geospatial Index Types                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  2dsphere Index                                                     │
│  ├── For spherical geometry (Earth)                                │
│  ├── GeoJSON objects                                               │
│  ├── Calculates distances on sphere                                │
│  └── Recommended for most use cases                                │
│                                                                     │
│  2d Index                                                           │
│  ├── For flat (Euclidean) plane                                    │
│  ├── Legacy coordinate pairs                                       │
│  ├── Simple X,Y calculations                                       │
│  └── Use for flat maps/game coordinates                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## GeoJSON Objects

### Point

```javascript
// GeoJSON Point
{
  type: "Point",
  coordinates: [-73.97, 40.77]  // [longitude, latitude]
}

// Document with location
db.places.insertOne({
  name: "Central Park",
  location: {
    type: "Point",
    coordinates: [-73.9654, 40.7829]
  }
})
```

### LineString

```javascript
// GeoJSON LineString
{
  type: "LineString",
  coordinates: [
    [-73.97, 40.77],
    [-73.98, 40.76],
    [-73.99, 40.75]
  ]
}

// Route or path
db.routes.insertOne({
  name: "Walking Route",
  path: {
    type: "LineString",
    coordinates: [
      [-73.9857, 40.7484],  // Start: Empire State
      [-73.9776, 40.7614],  // Stop: Rockefeller
      [-73.9654, 40.7829]   // End: Central Park
    ]
  }
})
```

### Polygon

```javascript
// GeoJSON Polygon (closed ring)
{
  type: "Polygon",
  coordinates: [[
    [-73.98, 40.77],
    [-73.99, 40.76],
    [-73.97, 40.75],
    [-73.96, 40.76],
    [-73.98, 40.77]  // First and last must be same
  ]]
}

// Area/region
db.zones.insertOne({
  name: "Delivery Zone A",
  area: {
    type: "Polygon",
    coordinates: [[
      [-74.0, 40.75],
      [-74.0, 40.80],
      [-73.95, 40.80],
      [-73.95, 40.75],
      [-74.0, 40.75]
    ]]
  }
})
```

### Polygon with Hole

```javascript
// Polygon with inner ring (hole)
{
  type: "Polygon",
  coordinates: [
    // Outer ring
    [
      [-74.0, 40.7],
      [-74.0, 40.8],
      [-73.9, 40.8],
      [-73.9, 40.7],
      [-74.0, 40.7]
    ],
    // Inner ring (hole)
    [
      [-73.98, 40.73],
      [-73.98, 40.77],
      [-73.92, 40.77],
      [-73.92, 40.73],
      [-73.98, 40.73]
    ]
  ]
}
```

### MultiPoint, MultiLineString, MultiPolygon

```javascript
// MultiPoint
{
  type: "MultiPoint",
  coordinates: [
    [-73.97, 40.77],
    [-73.98, 40.76],
    [-73.96, 40.75]
  ]
}

// MultiPolygon (multiple regions)
db.territories.insertOne({
  name: "Sales Region",
  areas: {
    type: "MultiPolygon",
    coordinates: [
      [[[/* polygon 1 */]]],
      [[[/* polygon 2 */]]]
    ]
  }
})
```

### GeometryCollection

```javascript
{
  type: "GeometryCollection",
  geometries: [
    { type: "Point", coordinates: [-73.97, 40.77] },
    { type: "LineString", coordinates: [[...], [...]] }
  ]
}
```

---

## 2dsphere Index

### Creating 2dsphere Index

```javascript
// Basic 2dsphere index
db.places.createIndex({ location: "2dsphere" })

// Compound index
db.places.createIndex({ 
  category: 1, 
  location: "2dsphere" 
})

// With options
db.places.createIndex(
  { location: "2dsphere" },
  { name: "location_2dsphere" }
)
```

### Sample Data Setup

```javascript
// Insert sample locations
db.restaurants.insertMany([
  {
    name: "Joe's Pizza",
    cuisine: "Italian",
    location: {
      type: "Point",
      coordinates: [-73.9857, 40.7484]  // Manhattan
    }
  },
  {
    name: "Sushi Place",
    cuisine: "Japanese",
    location: {
      type: "Point",
      coordinates: [-73.9776, 40.7614]
    }
  },
  {
    name: "Burger Joint",
    cuisine: "American",
    location: {
      type: "Point",
      coordinates: [-73.9654, 40.7829]
    }
  },
  {
    name: "Taco Shop",
    cuisine: "Mexican",
    location: {
      type: "Point",
      coordinates: [-73.9950, 40.7282]
    }
  }
])

db.restaurants.createIndex({ location: "2dsphere" })
```

---

## 2d Index

### Creating 2d Index

```javascript
// Legacy coordinate format: [x, y] or [lng, lat]
db.legacyPlaces.insertMany([
  { name: "Point A", loc: [40, 5] },
  { name: "Point B", loc: [42, 7] },
  { name: "Point C", loc: [38, 3] }
])

// Create 2d index
db.legacyPlaces.createIndex({ loc: "2d" })

// With bounds (for game maps, etc.)
db.gameObjects.createIndex(
  { position: "2d" },
  { min: 0, max: 1000 }  // Coordinate bounds
)
```

### When to Use 2d

```javascript
// Use 2d for:
// - Flat coordinate systems
// - Game maps
// - Floor plans
// - Non-geographic data

// Example: Game world
db.gameWorld.insertMany([
  { item: "treasure", position: [250, 150] },
  { item: "enemy", position: [300, 200] },
  { item: "player", position: [275, 175] }
])

db.gameWorld.createIndex({ position: "2d" })
```

---

## Geospatial Query Operators

### $near - Find Nearby

```javascript
// Find restaurants near a point
db.restaurants.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.98, 40.75]
      },
      $maxDistance: 2000,  // 2km in meters
      $minDistance: 100    // At least 100m away
    }
  }
})

// Results are sorted by distance (closest first)
```

### $nearSphere

```javascript
// Same as $near but explicitly spherical
db.restaurants.find({
  location: {
    $nearSphere: {
      $geometry: {
        type: "Point",
        coordinates: [-73.98, 40.75]
      },
      $maxDistance: 5000
    }
  }
})

// Legacy format
db.legacyPlaces.find({
  loc: {
    $nearSphere: [40, 5],
    $maxDistance: 0.1  // Radians for legacy
  }
})
```

### $geoWithin - Containment

```javascript
// Find all restaurants within a polygon
db.restaurants.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[
          [-74.0, 40.7],
          [-74.0, 40.8],
          [-73.9, 40.8],
          [-73.9, 40.7],
          [-74.0, 40.7]
        ]]
      }
    }
  }
})

// Within a circle ($centerSphere)
db.restaurants.find({
  location: {
    $geoWithin: {
      $centerSphere: [
        [-73.98, 40.75],  // Center point
        5 / 6378.1       // Radius in radians (5km / Earth radius)
      ]
    }
  }
})
```

### $geoWithin with $box

```javascript
// Rectangle query
db.restaurants.find({
  location: {
    $geoWithin: {
      $box: [
        [-74.0, 40.7],   // Bottom-left
        [-73.9, 40.8]    // Top-right
      ]
    }
  }
})
```

### $geoIntersects

```javascript
// Find zones that intersect with a point
db.zones.find({
  area: {
    $geoIntersects: {
      $geometry: {
        type: "Point",
        coordinates: [-73.97, 40.76]
      }
    }
  }
})

// Find routes that intersect with a zone
db.routes.find({
  path: {
    $geoIntersects: {
      $geometry: {
        type: "Polygon",
        coordinates: [[/* ... */]]
      }
    }
  }
})
```

---

## Proximity Queries

### Find Nearest with $near

```javascript
// Find 5 nearest restaurants
db.restaurants.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.98, 40.75]
      }
    }
  }
}).limit(5)
```

### $geoNear Aggregation

```javascript
// Detailed proximity query with distance
db.restaurants.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-73.98, 40.75]
      },
      distanceField: "distance",  // Add distance to results
      maxDistance: 3000,
      spherical: true,
      query: { cuisine: "Italian" }  // Additional filter
    }
  },
  {
    $project: {
      name: 1,
      cuisine: 1,
      distance: { $round: ["$distance", 0] }  // Round to meters
    }
  }
])

// Example output:
{
  "name": "Joe's Pizza",
  "cuisine": "Italian",
  "distance": 850  // 850 meters away
}
```

### Distance in Different Units

```javascript
// Distance in kilometers
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.98, 40.75] },
      distanceField: "distanceInMeters",
      spherical: true
    }
  },
  {
    $addFields: {
      distanceInKm: { $divide: ["$distanceInMeters", 1000] },
      distanceInMiles: { $divide: ["$distanceInMeters", 1609.34] }
    }
  }
])
```

---

## Intersection Queries

### Point in Polygon

```javascript
// Check if user location is in delivery zone
db.deliveryZones.insertOne({
  name: "Zone A",
  area: {
    type: "Polygon",
    coordinates: [[
      [-74.0, 40.7],
      [-74.0, 40.8],
      [-73.9, 40.8],
      [-73.9, 40.7],
      [-74.0, 40.7]
    ]]
  }
})

db.deliveryZones.createIndex({ area: "2dsphere" })

// Find zones containing user's location
const userLocation = {
  type: "Point",
  coordinates: [-73.95, 40.75]
}

db.deliveryZones.find({
  area: {
    $geoIntersects: {
      $geometry: userLocation
    }
  }
})
```

### Line Intersects Polygon

```javascript
// Check if delivery route passes through restricted zone
db.restrictedZones.insertOne({
  name: "Construction Area",
  area: {
    type: "Polygon",
    coordinates: [[
      [-73.98, 40.76],
      [-73.98, 40.77],
      [-73.96, 40.77],
      [-73.96, 40.76],
      [-73.98, 40.76]
    ]]
  }
})

const deliveryRoute = {
  type: "LineString",
  coordinates: [
    [-73.99, 40.75],
    [-73.97, 40.765],  // Passes through
    [-73.95, 40.78]
  ]
}

db.restrictedZones.find({
  area: {
    $geoIntersects: {
      $geometry: deliveryRoute
    }
  }
})
```

---

## Aggregation with Geospatial

### $geoNear Stage

```javascript
// Full $geoNear aggregation
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.98, 40.75] },
      distanceField: "distance",
      maxDistance: 5000,
      query: { cuisine: { $in: ["Italian", "Mexican"] } },
      includeLocs: "location",  // Include matched location
      spherical: true,
      key: "location"  // Specify index field if multiple geo indexes
    }
  },
  { $limit: 10 },
  {
    $project: {
      name: 1,
      cuisine: 1,
      distanceKm: { $divide: ["$distance", 1000] }
    }
  }
])
```

### Group by Distance Bands

```javascript
// Group restaurants by distance bands
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.98, 40.75] },
      distanceField: "distance",
      spherical: true
    }
  },
  {
    $bucket: {
      groupBy: "$distance",
      boundaries: [0, 500, 1000, 2000, 5000, 10000],
      default: "Far",
      output: {
        count: { $sum: 1 },
        restaurants: { $push: "$name" }
      }
    }
  }
])

// Output:
// { _id: 0, count: 2, restaurants: [...] }      // 0-500m
// { _id: 500, count: 3, restaurants: [...] }   // 500-1000m
// { _id: 1000, count: 5, restaurants: [...] }  // 1-2km
```

### Combined with Other Stages

```javascript
// Find nearby restaurants with rating > 4
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.98, 40.75] },
      distanceField: "distance",
      maxDistance: 2000,
      spherical: true
    }
  },
  {
    $lookup: {
      from: "reviews",
      localField: "_id",
      foreignField: "restaurantId",
      as: "reviews"
    }
  },
  {
    $addFields: {
      avgRating: { $avg: "$reviews.rating" }
    }
  },
  {
    $match: {
      avgRating: { $gte: 4 }
    }
  },
  {
    $project: {
      name: 1,
      distance: 1,
      avgRating: { $round: ["$avgRating", 1] }
    }
  },
  { $limit: 5 }
])
```

---

## Best Practices

### 1. Use Correct Format

```javascript
// ✓ Correct: longitude first, latitude second
{ type: "Point", coordinates: [-73.97, 40.77] }

// ✗ Wrong: latitude first
{ type: "Point", coordinates: [40.77, -73.97] }

// Mnemonic: "longitude, latitude" = "x, y"
```

### 2. Validate GeoJSON

```javascript
// MongoDB validates GeoJSON on insert/index
// Ensure polygons are closed
const validPolygon = {
  type: "Polygon",
  coordinates: [[
    [0, 0],
    [0, 1],
    [1, 1],
    [1, 0],
    [0, 0]  // Must close
  ]]
}

// Use external validation for user input
```

### 3. Index Strategy

```javascript
// Compound index for filtered geo queries
db.restaurants.createIndex({ 
  cuisine: 1, 
  location: "2dsphere" 
})

// Query must include prefix
db.restaurants.find({
  cuisine: "Italian",
  location: { $near: { $geometry: point } }
})
```

### 4. Query Performance

```javascript
// Set appropriate $maxDistance
db.places.find({
  location: {
    $near: {
      $geometry: point,
      $maxDistance: 5000  // Limit search radius
    }
  }
}).limit(20)  // Limit results

// $geoWithin is often faster than $near
// because it doesn't need to sort by distance
```

### 5. Handling Large Areas

```javascript
// For very large areas, consider:
// 1. Multiple smaller polygons
// 2. Bounding box pre-filter
// 3. Geohash bucketing

// Bounding box optimization
db.places.find({
  location: {
    $geoWithin: {
      $box: [[-80, 35], [-70, 45]]  // Fast bounding box
    }
  },
  // Additional precise filter if needed
})
```

---

## Summary

### Index Types

| Index | Use Case |
|-------|----------|
| **2dsphere** | Earth geometry, GeoJSON |
| **2d** | Flat plane, legacy coordinates |

### Query Operators

| Operator | Description |
|----------|-------------|
| **$near** | Find nearby, sorted by distance |
| **$geoWithin** | Find within area |
| **$geoIntersects** | Find intersecting |
| **$geoNear** | Aggregation with distance |

### What's Next?

In the next chapter, we'll explore Index Management and administration.

---

## Practice Questions

1. What's the difference between 2dsphere and 2d indexes?
2. What is the correct order for GeoJSON coordinates?
3. How do you find documents within a specific radius?
4. What's the difference between $near and $geoWithin?
5. How do you include distance in query results?
6. When would you use $geoIntersects?
7. How do you create a compound geospatial index?
8. What are best practices for geospatial query performance?

---

## Hands-On Exercises

### Exercise 1: Setup and Basic Queries

```javascript
// Setup
db.geo_places.drop()
db.geo_places.insertMany([
  {
    name: "Coffee Shop A",
    type: "cafe",
    location: { type: "Point", coordinates: [-73.985, 40.748] }
  },
  {
    name: "Coffee Shop B",
    type: "cafe",
    location: { type: "Point", coordinates: [-73.975, 40.752] }
  },
  {
    name: "Restaurant A",
    type: "restaurant",
    location: { type: "Point", coordinates: [-73.990, 40.745] }
  },
  {
    name: "Restaurant B",
    type: "restaurant",
    location: { type: "Point", coordinates: [-73.970, 40.755] }
  },
  {
    name: "Bar A",
    type: "bar",
    location: { type: "Point", coordinates: [-73.982, 40.750] }
  }
])

// Create 2dsphere index
db.geo_places.createIndex({ location: "2dsphere" })

// Find nearest places
const myLocation = { type: "Point", coordinates: [-73.980, 40.750] }

print("Nearest places:")
db.geo_places.find({
  location: { $near: { $geometry: myLocation } }
}).limit(3).forEach(doc => print("  -", doc.name, `(${doc.type})`))
```

### Exercise 2: Distance Queries

```javascript
// Find places within 500 meters
print("Places within 500m:")
db.geo_places.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.980, 40.750] },
      $maxDistance: 500
    }
  }
}).forEach(doc => print("  -", doc.name))

// Find places with distance using aggregation
print("\nPlaces with distance:")
db.geo_places.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.980, 40.750] },
      distanceField: "distance",
      spherical: true
    }
  },
  {
    $project: {
      name: 1,
      type: 1,
      distanceMeters: { $round: ["$distance", 0] }
    }
  },
  { $limit: 5 }
]).forEach(doc => {
  print(`  - ${doc.name}: ${doc.distanceMeters}m`)
})
```

### Exercise 3: Polygon Containment

```javascript
// Create delivery zones
db.geo_zones.drop()
db.geo_zones.insertMany([
  {
    name: "Zone A",
    area: {
      type: "Polygon",
      coordinates: [[
        [-73.995, 40.745],
        [-73.995, 40.755],
        [-73.980, 40.755],
        [-73.980, 40.745],
        [-73.995, 40.745]
      ]]
    }
  },
  {
    name: "Zone B",
    area: {
      type: "Polygon",
      coordinates: [[
        [-73.980, 40.745],
        [-73.980, 40.755],
        [-73.965, 40.755],
        [-73.965, 40.745],
        [-73.980, 40.745]
      ]]
    }
  }
])

db.geo_zones.createIndex({ area: "2dsphere" })

// Check which zone a point is in
const testPoint = { type: "Point", coordinates: [-73.972, 40.750] }

print("Point location zones:")
db.geo_zones.find({
  area: { $geoIntersects: { $geometry: testPoint } }
}).forEach(doc => print("  - In zone:", doc.name))

// Find all places in Zone A
print("\nPlaces in Zone A:")
const zoneA = db.geo_zones.findOne({ name: "Zone A" })
db.geo_places.find({
  location: { $geoWithin: { $geometry: zoneA.area } }
}).forEach(doc => print("  -", doc.name))
```

### Exercise 4: Compound Geospatial Index

```javascript
// Create compound index
db.geo_places.dropIndexes()
db.geo_places.createIndex({ type: 1, location: "2dsphere" })

// Find nearest cafes only
print("Nearest cafes:")
db.geo_places.find({
  type: "cafe",
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.980, 40.750] }
    }
  }
}).forEach(doc => print("  -", doc.name))

// Find restaurants within 1km
print("\nRestaurants within 1km:")
db.geo_places.find({
  type: "restaurant",
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.980, 40.750] },
      $maxDistance: 1000
    }
  }
}).forEach(doc => print("  -", doc.name))
```

### Exercise 5: Route Intersection

```javascript
// Create a route
db.geo_routes.drop()
db.geo_routes.insertOne({
  name: "Delivery Route 1",
  path: {
    type: "LineString",
    coordinates: [
      [-73.995, 40.740],
      [-73.985, 40.750],
      [-73.970, 40.760]
    ]
  }
})

db.geo_routes.createIndex({ path: "2dsphere" })

// Check if route passes through zones
print("Route passes through:")
db.geo_zones.find({
  area: {
    $geoIntersects: {
      $geometry: db.geo_routes.findOne().path
    }
  }
}).forEach(doc => print("  -", doc.name))
```

---

[← Previous: Text Indexes](20-text-indexes.md) | [Next: Index Management →](22-index-management.md)
