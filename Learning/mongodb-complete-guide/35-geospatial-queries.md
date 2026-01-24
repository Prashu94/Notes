# Chapter 35: Geospatial Queries

## Table of Contents
- [Introduction to Geospatial Data](#introduction-to-geospatial-data)
- [GeoJSON Data Types](#geojson-data-types)
- [Geospatial Indexes](#geospatial-indexes)
- [$geoWithin Queries](#geowithin-queries)
- [$geoIntersects Queries](#geointersects-queries)
- [$near and $nearSphere](#near-and-nearsphere)
- [$geoNear Aggregation](#geonear-aggregation)
- [Practical Applications](#practical-applications)
- [Summary](#summary)

---

## Introduction to Geospatial Data

MongoDB provides powerful geospatial capabilities for storing and querying location data. It supports both GeoJSON objects and legacy coordinate pairs.

### Geospatial Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Geospatial Capabilities                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Index Types:                                                      │
│  ├── 2dsphere - For GeoJSON and spherical geometry                 │
│  └── 2d - For legacy coordinate pairs (flat geometry)              │
│                                                                     │
│  Query Operators:                                                  │
│  ├── $geoWithin - Objects within specified shape                   │
│  ├── $geoIntersects - Objects intersecting shape                   │
│  ├── $near - Objects near point (sorted by distance)               │
│  ├── $nearSphere - Like $near with spherical geometry              │
│  └── $geoNear - Aggregation stage for geospatial                   │
│                                                                     │
│  Supported Shapes:                                                 │
│  ├── Point, LineString, Polygon                                    │
│  ├── MultiPoint, MultiLineString, MultiPolygon                     │
│  └── GeometryCollection                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Restaurants collection
db.restaurants.drop()
db.restaurants.insertMany([
  {
    _id: 1,
    name: "Pizza Palace",
    cuisine: "Italian",
    location: {
      type: "Point",
      coordinates: [-73.97, 40.77]  // [longitude, latitude]
    },
    address: "123 Main St, New York"
  },
  {
    _id: 2,
    name: "Burger Barn",
    cuisine: "American",
    location: {
      type: "Point",
      coordinates: [-73.98, 40.76]
    },
    address: "456 Oak Ave, New York"
  },
  {
    _id: 3,
    name: "Sushi Supreme",
    cuisine: "Japanese",
    location: {
      type: "Point",
      coordinates: [-73.96, 40.78]
    },
    address: "789 Elm St, New York"
  },
  {
    _id: 4,
    name: "Taco Town",
    cuisine: "Mexican",
    location: {
      type: "Point",
      coordinates: [-73.99, 40.75]
    },
    address: "321 Pine Rd, New York"
  },
  {
    _id: 5,
    name: "Curry Corner",
    cuisine: "Indian",
    location: {
      type: "Point",
      coordinates: [-73.95, 40.79]
    },
    address: "654 Cedar Blvd, New York"
  }
])

// Places with various geometries
db.places.drop()
db.places.insertMany([
  {
    _id: 1,
    name: "Central Park",
    type: "park",
    area: {
      type: "Polygon",
      coordinates: [[
        [-73.981, 40.768],
        [-73.958, 40.768],
        [-73.958, 40.800],
        [-73.981, 40.800],
        [-73.981, 40.768]  // Must close polygon
      ]]
    }
  },
  {
    _id: 2,
    name: "Broadway",
    type: "street",
    path: {
      type: "LineString",
      coordinates: [
        [-73.99, 40.75],
        [-73.98, 40.76],
        [-73.97, 40.77],
        [-73.96, 40.78]
      ]
    }
  },
  {
    _id: 3,
    name: "Times Square",
    type: "landmark",
    location: {
      type: "Point",
      coordinates: [-73.985, 40.758]
    }
  }
])

// Delivery zones
db.deliveryZones.drop()
db.deliveryZones.insertMany([
  {
    _id: 1,
    restaurant: "Pizza Palace",
    zone: {
      type: "Polygon",
      coordinates: [[
        [-73.98, 40.76],
        [-73.96, 40.76],
        [-73.96, 40.78],
        [-73.98, 40.78],
        [-73.98, 40.76]
      ]]
    }
  },
  {
    _id: 2,
    restaurant: "Burger Barn",
    zone: {
      type: "Polygon",
      coordinates: [[
        [-74.00, 40.74],
        [-73.96, 40.74],
        [-73.96, 40.78],
        [-74.00, 40.78],
        [-74.00, 40.74]
      ]]
    }
  }
])

// Create geospatial indexes
db.restaurants.createIndex({ location: "2dsphere" })
db.places.createIndex({ area: "2dsphere" })
db.places.createIndex({ path: "2dsphere" })
db.places.createIndex({ location: "2dsphere" })
db.deliveryZones.createIndex({ zone: "2dsphere" })
```

---

## GeoJSON Data Types

### Point

```javascript
// A single location
{
  type: "Point",
  coordinates: [-73.97, 40.77]  // [longitude, latitude]
}

// Insert point location
db.stores.insertOne({
  name: "Main Store",
  location: {
    type: "Point",
    coordinates: [-122.4194, 37.7749]  // San Francisco
  }
})
```

### LineString

```javascript
// A path or route
{
  type: "LineString",
  coordinates: [
    [-73.99, 40.75],
    [-73.98, 40.76],
    [-73.97, 40.77]
  ]
}

// Insert route
db.routes.insertOne({
  name: "Bus Route 42",
  path: {
    type: "LineString",
    coordinates: [
      [-122.43, 37.77],
      [-122.42, 37.78],
      [-122.41, 37.79],
      [-122.40, 37.80]
    ]
  }
})
```

### Polygon

```javascript
// A closed area (first and last point must be same)
{
  type: "Polygon",
  coordinates: [[
    [-73.98, 40.76],   // Exterior ring
    [-73.96, 40.76],
    [-73.96, 40.78],
    [-73.98, 40.78],
    [-73.98, 40.76]    // Close the ring
  ]]
}

// Polygon with hole
{
  type: "Polygon",
  coordinates: [
    [  // Exterior ring
      [-73.98, 40.76],
      [-73.94, 40.76],
      [-73.94, 40.80],
      [-73.98, 40.80],
      [-73.98, 40.76]
    ],
    [  // Interior ring (hole)
      [-73.97, 40.77],
      [-73.95, 40.77],
      [-73.95, 40.79],
      [-73.97, 40.79],
      [-73.97, 40.77]
    ]
  ]
}
```

### Multi-Geometries

```javascript
// MultiPoint
{
  type: "MultiPoint",
  coordinates: [
    [-73.97, 40.77],
    [-73.98, 40.76],
    [-73.96, 40.78]
  ]
}

// MultiLineString
{
  type: "MultiLineString",
  coordinates: [
    [[-73.99, 40.75], [-73.98, 40.76]],
    [[-73.97, 40.77], [-73.96, 40.78]]
  ]
}

// MultiPolygon
{
  type: "MultiPolygon",
  coordinates: [
    [[[-73.98, 40.76], [-73.96, 40.76], [-73.96, 40.78], [-73.98, 40.78], [-73.98, 40.76]]],
    [[[-73.95, 40.76], [-73.93, 40.76], [-73.93, 40.78], [-73.95, 40.78], [-73.95, 40.76]]]
  ]
}
```

### GeometryCollection

```javascript
{
  type: "GeometryCollection",
  geometries: [
    {
      type: "Point",
      coordinates: [-73.97, 40.77]
    },
    {
      type: "LineString",
      coordinates: [[-73.98, 40.76], [-73.96, 40.78]]
    }
  ]
}
```

---

## Geospatial Indexes

### 2dsphere Index

```javascript
// For GeoJSON data and spherical geometry
db.collection.createIndex({ location: "2dsphere" })

// Compound index with 2dsphere
db.restaurants.createIndex({ location: "2dsphere", cuisine: 1 })

// Check index
db.restaurants.getIndexes()
```

### 2d Index (Legacy)

```javascript
// For legacy coordinate pairs [x, y]
db.legacyPlaces.createIndex({ coordinates: "2d" })

// With bounds
db.legacyPlaces.createIndex(
  { coordinates: "2d" },
  { min: -200, max: 200 }
)

// Legacy coordinate format
db.legacyPlaces.insertOne({
  name: "Old Store",
  coordinates: [40.77, -73.97]  // [lat, long] or [x, y]
})
```

### Index Comparison

| Feature | 2dsphere | 2d |
|---------|----------|-----|
| Data format | GeoJSON | Legacy pairs |
| Calculations | Spherical | Flat |
| Queries | All geo queries | Limited |
| Accuracy | Earth-accurate | Approximate |
| Use case | Real-world locations | Gaming, flat maps |

---

## $geoWithin Queries

### Find Points Within Polygon

```javascript
// Restaurants within a bounding box
db.restaurants.find({
  location: {
    $geoWithin: {
      $geometry: {
        type: "Polygon",
        coordinates: [[
          [-73.99, 40.75],
          [-73.95, 40.75],
          [-73.95, 40.79],
          [-73.99, 40.79],
          [-73.99, 40.75]
        ]]
      }
    }
  }
})
```

### $box (Rectangle)

```javascript
// Using $box for rectangle (legacy format)
db.restaurants.find({
  location: {
    $geoWithin: {
      $box: [
        [-73.99, 40.75],  // Bottom-left
        [-73.95, 40.79]   // Top-right
      ]
    }
  }
})
```

### $center (Circle - Flat)

```javascript
// Circle using flat geometry
db.restaurants.find({
  location: {
    $geoWithin: {
      $center: [[-73.97, 40.77], 0.02]  // [center, radius in coordinate units]
    }
  }
})
```

### $centerSphere (Circle - Spherical)

```javascript
// Circle using spherical geometry
// Radius in radians: distance / earth_radius
// Earth radius ≈ 6371 km or 3959 miles

// Find restaurants within 1 km
const radiusKm = 1
const earthRadiusKm = 6371
const radiansRadius = radiusKm / earthRadiusKm

db.restaurants.find({
  location: {
    $geoWithin: {
      $centerSphere: [[-73.97, 40.77], radiansRadius]
    }
  }
})

// Find restaurants within 1 mile
const radiusMiles = 1
const earthRadiusMiles = 3959
const radiansMiles = radiusMiles / earthRadiusMiles

db.restaurants.find({
  location: {
    $geoWithin: {
      $centerSphere: [[-73.97, 40.77], radiansMiles]
    }
  }
})
```

### $polygon (Legacy)

```javascript
// Legacy polygon format
db.restaurants.find({
  location: {
    $geoWithin: {
      $polygon: [
        [-73.99, 40.75],
        [-73.95, 40.75],
        [-73.95, 40.79],
        [-73.99, 40.79]
      ]
    }
  }
})
```

---

## $geoIntersects Queries

### Points Intersecting Polygon

```javascript
// Find points inside delivery zone
db.restaurants.find({
  location: {
    $geoIntersects: {
      $geometry: {
        type: "Polygon",
        coordinates: [[
          [-73.98, 40.76],
          [-73.96, 40.76],
          [-73.96, 40.78],
          [-73.98, 40.78],
          [-73.98, 40.76]
        ]]
      }
    }
  }
})
```

### Line Intersecting Polygon

```javascript
// Find if route passes through park
db.places.find({
  type: "park",
  area: {
    $geoIntersects: {
      $geometry: {
        type: "LineString",
        coordinates: [
          [-73.99, 40.77],
          [-73.95, 40.77]
        ]
      }
    }
  }
})
```

### Polygon Intersecting Polygon

```javascript
// Find delivery zones overlapping an area
db.deliveryZones.find({
  zone: {
    $geoIntersects: {
      $geometry: {
        type: "Polygon",
        coordinates: [[
          [-73.98, 40.76],
          [-73.97, 40.76],
          [-73.97, 40.77],
          [-73.98, 40.77],
          [-73.98, 40.76]
        ]]
      }
    }
  }
})
```

---

## $near and $nearSphere

### Basic $near Query

```javascript
// Find restaurants near a point (sorted by distance)
// Requires 2dsphere index
db.restaurants.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.97, 40.77]
      }
    }
  }
})
// Results sorted by distance (closest first)
```

### $near with Distance Limits

```javascript
// Find within min/max distance (in meters)
db.restaurants.find({
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.97, 40.77]
      },
      $maxDistance: 1000,  // 1 km
      $minDistance: 100    // 100 m
    }
  }
})
```

### $nearSphere

```javascript
// Spherical distance calculation
db.restaurants.find({
  location: {
    $nearSphere: {
      $geometry: {
        type: "Point",
        coordinates: [-73.97, 40.77]
      },
      $maxDistance: 1000  // meters
    }
  }
})

// With legacy coordinates
db.restaurants.find({
  location: {
    $nearSphere: [-73.97, 40.77],
    $maxDistance: 1000 / 6378100  // Convert meters to radians
  }
})
```

### Combine with Other Filters

```javascript
// Find nearby Italian restaurants
db.restaurants.find({
  cuisine: "Italian",
  location: {
    $near: {
      $geometry: {
        type: "Point",
        coordinates: [-73.97, 40.77]
      },
      $maxDistance: 2000
    }
  }
})
```

---

## $geoNear Aggregation

### Basic $geoNear

```javascript
// $geoNear must be first stage in pipeline
db.restaurants.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-73.97, 40.77]
      },
      distanceField: "distance",  // Required
      spherical: true
    }
  }
])
// Returns documents with calculated distance field
```

### $geoNear with Options

```javascript
db.restaurants.aggregate([
  {
    $geoNear: {
      near: {
        type: "Point",
        coordinates: [-73.97, 40.77]
      },
      distanceField: "distance",
      maxDistance: 2000,              // meters
      minDistance: 100,               // meters
      query: { cuisine: "Italian" },  // Additional filter
      spherical: true,
      distanceMultiplier: 0.001       // Convert to km
    }
  },
  { $limit: 5 }
])
```

### Include Location Information

```javascript
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.97, 40.77] },
      distanceField: "distance",
      includeLocs: "matchedLocation",  // Field name for matched location
      spherical: true
    }
  },
  {
    $project: {
      name: 1,
      cuisine: 1,
      distance: { $round: ["$distance", 0] },
      matchedLocation: 1
    }
  }
])
```

### $geoNear with Grouping

```javascript
// Find nearest restaurant of each cuisine type
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.97, 40.77] },
      distanceField: "distance",
      spherical: true
    }
  },
  {
    $group: {
      _id: "$cuisine",
      nearestRestaurant: { $first: "$name" },
      distance: { $first: "$distance" }
    }
  },
  { $sort: { distance: 1 } }
])
```

---

## Practical Applications

### Store Locator

```javascript
// Find nearest stores with details
function findNearestStores(longitude, latitude, maxDistanceKm = 5, limit = 10) {
  return db.restaurants.aggregate([
    {
      $geoNear: {
        near: { type: "Point", coordinates: [longitude, latitude] },
        distanceField: "distanceMeters",
        maxDistance: maxDistanceKm * 1000,
        spherical: true
      }
    },
    {
      $project: {
        name: 1,
        cuisine: 1,
        address: 1,
        distanceKm: { $round: [{ $divide: ["$distanceMeters", 1000] }, 2] },
        distanceMiles: { $round: [{ $divide: ["$distanceMeters", 1609.34] }, 2] }
      }
    },
    { $limit: limit }
  ]).toArray()
}

// Use it
const nearbyStores = findNearestStores(-73.97, 40.77, 2, 5)
nearbyStores.forEach(store => {
  print(`${store.name} (${store.cuisine}) - ${store.distanceKm} km / ${store.distanceMiles} miles`)
})
```

### Delivery Zone Check

```javascript
// Check if location is within delivery zone
function isDeliverable(restaurantId, longitude, latitude) {
  const result = db.deliveryZones.findOne({
    _id: restaurantId,
    zone: {
      $geoIntersects: {
        $geometry: {
          type: "Point",
          coordinates: [longitude, latitude]
        }
      }
    }
  })
  return result !== null
}

// Test
print("Can Pizza Palace deliver to [-73.97, 40.77]?", isDeliverable(1, -73.97, 40.77))
```

### Route Analysis

```javascript
// Find all points along a route
db.restaurants.find({
  location: {
    $geoIntersects: {
      $geometry: {
        type: "LineString",
        coordinates: [
          [-73.99, 40.75],
          [-73.98, 40.76],
          [-73.97, 40.77],
          [-73.96, 40.78],
          [-73.95, 40.79]
        ]
      }
    }
  }
})

// Find restaurants within 500m of route
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.97, 40.77] },  // Point on route
      distanceField: "distance",
      maxDistance: 500,
      spherical: true
    }
  }
])
```

### Geofencing

```javascript
// Define geofence regions
db.geofences.drop()
db.geofences.insertMany([
  {
    name: "Downtown Zone",
    type: "restricted",
    boundary: {
      type: "Polygon",
      coordinates: [[
        [-73.99, 40.75],
        [-73.97, 40.75],
        [-73.97, 40.77],
        [-73.99, 40.77],
        [-73.99, 40.75]
      ]]
    }
  },
  {
    name: "Business District",
    type: "premium",
    boundary: {
      type: "Polygon",
      coordinates: [[
        [-73.98, 40.76],
        [-73.96, 40.76],
        [-73.96, 40.78],
        [-73.98, 40.78],
        [-73.98, 40.76]
      ]]
    }
  }
])

db.geofences.createIndex({ boundary: "2dsphere" })

// Check which zones a point is in
function checkGeofences(longitude, latitude) {
  return db.geofences.find({
    boundary: {
      $geoIntersects: {
        $geometry: {
          type: "Point",
          coordinates: [longitude, latitude]
        }
      }
    }
  }).toArray()
}

// Test
const zones = checkGeofences(-73.97, 40.77)
print("Location is in zones:", zones.map(z => z.name).join(", "))
```

### Distance Matrix

```javascript
// Calculate distances between multiple points
function distanceMatrix(locations) {
  const results = []
  
  for (let i = 0; i < locations.length; i++) {
    for (let j = i + 1; j < locations.length; j++) {
      const from = locations[i]
      const to = locations[j]
      
      // Use aggregation to get distance
      const result = db.restaurants.aggregate([
        {
          $geoNear: {
            near: { type: "Point", coordinates: from.coordinates },
            distanceField: "distance",
            spherical: true,
            query: { _id: to.id }
          }
        }
      ]).toArray()
      
      if (result.length > 0) {
        results.push({
          from: from.name,
          to: to.name,
          distanceMeters: Math.round(result[0].distance)
        })
      }
    }
  }
  
  return results
}
```

---

## Summary

### GeoJSON Types

| Type | Description | Example Use |
|------|-------------|-------------|
| Point | Single location | Store location |
| LineString | Path/route | Delivery route |
| Polygon | Closed area | Delivery zone |
| MultiPoint | Multiple points | Store chain |
| MultiPolygon | Multiple areas | Service regions |

### Query Operators

| Operator | Description | Sorted |
|----------|-------------|--------|
| `$geoWithin` | Within shape | No |
| `$geoIntersects` | Intersects shape | No |
| `$near` | Near point | Yes |
| `$nearSphere` | Near point (spherical) | Yes |
| `$geoNear` | Aggregation near | Yes |

### Distance Units

| Context | Unit |
|---------|------|
| `$maxDistance` with 2dsphere | Meters |
| `$centerSphere` radius | Radians |
| `$geoNear` distanceField | Meters |
| Legacy 2d queries | Coordinate units |

### What's Next?

In the next chapter, we'll begin Part 7: Transactions, starting with Transaction Fundamentals.

---

## Practice Questions

1. What's the difference between 2dsphere and 2d indexes?
2. In GeoJSON, what's the coordinate order?
3. How do you find points within a circle using spherical geometry?
4. What's the difference between $geoWithin and $geoIntersects?
5. Why must $geoNear be the first stage in aggregation?
6. How do you convert distance to kilometers in $geoNear?
7. What happens if you don't close a polygon's coordinates?
8. How do you find the nearest restaurant of each cuisine type?

---

## Hands-On Exercises

### Exercise 1: Basic Geospatial Queries

```javascript
// Find restaurants using different methods

// 1. Within a bounding box
print("1. Restaurants within bounding box:")
db.restaurants.find({
  location: {
    $geoWithin: {
      $box: [[-73.99, 40.75], [-73.95, 40.79]]
    }
  }
}).forEach(r => print("  -", r.name))

// 2. Within a circle (1 km radius)
print("\n2. Restaurants within 1km of [-73.97, 40.77]:")
const radiusKm = 1
const earthRadiusKm = 6371
db.restaurants.find({
  location: {
    $geoWithin: {
      $centerSphere: [[-73.97, 40.77], radiusKm / earthRadiusKm]
    }
  }
}).forEach(r => print("  -", r.name))

// 3. Sorted by distance
print("\n3. Restaurants sorted by distance:")
db.restaurants.find({
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [-73.97, 40.77] },
      $maxDistance: 5000
    }
  }
}).forEach(r => print("  -", r.name))
```

### Exercise 2: $geoNear Aggregation

```javascript
// Get distance information

// 1. Basic distance query
print("1. Restaurants with distance:")
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.97, 40.77] },
      distanceField: "distance",
      spherical: true
    }
  },
  {
    $project: {
      name: 1,
      cuisine: 1,
      distanceKm: { $round: [{ $divide: ["$distance", 1000] }, 2] }
    }
  }
]).forEach(r => print(`  - ${r.name} (${r.cuisine}): ${r.distanceKm} km`))

// 2. Nearest of each cuisine
print("\n2. Nearest restaurant by cuisine:")
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.97, 40.77] },
      distanceField: "distance",
      spherical: true
    }
  },
  {
    $group: {
      _id: "$cuisine",
      restaurant: { $first: "$name" },
      distance: { $first: { $round: [{ $divide: ["$distance", 1000] }, 2] } }
    }
  },
  { $sort: { distance: 1 } }
]).forEach(r => print(`  - ${r._id}: ${r.restaurant} (${r.distance} km)`))

// 3. With cuisine filter
print("\n3. Italian restaurants within 2km:")
db.restaurants.aggregate([
  {
    $geoNear: {
      near: { type: "Point", coordinates: [-73.97, 40.77] },
      distanceField: "distance",
      maxDistance: 2000,
      query: { cuisine: "Italian" },
      spherical: true
    }
  }
]).forEach(r => print(`  - ${r.name}: ${Math.round(r.distance)}m`))
```

### Exercise 3: Intersection Queries

```javascript
// Test intersection scenarios

// 1. Points in delivery zones
print("1. Restaurants in delivery zone 1:")
const zone1 = db.deliveryZones.findOne({ _id: 1 })
db.restaurants.find({
  location: {
    $geoIntersects: { $geometry: zone1.zone }
  }
}).forEach(r => print("  -", r.name))

// 2. Check if point is in any zone
function getZonesForPoint(lon, lat) {
  return db.deliveryZones.find({
    zone: {
      $geoIntersects: {
        $geometry: { type: "Point", coordinates: [lon, lat] }
      }
    }
  }).toArray()
}

print("\n2. Zones covering [-73.97, 40.77]:")
getZonesForPoint(-73.97, 40.77).forEach(z => print("  -", z.restaurant))

// 3. Overlapping zones
print("\n3. Zone overlap check:")
const z1 = db.deliveryZones.findOne({ _id: 1 })
const z2 = db.deliveryZones.findOne({ _id: 2 })
const overlap = db.deliveryZones.findOne({
  _id: 1,
  zone: { $geoIntersects: { $geometry: z2.zone } }
})
print("  Zones overlap:", overlap !== null)
```

### Exercise 4: Store Locator Function

```javascript
// Build a complete store locator

function storeLocator(options) {
  const {
    longitude,
    latitude,
    maxDistanceKm = 5,
    cuisine = null,
    limit = 10,
    sortBy = "distance"
  } = options
  
  const pipeline = [
    {
      $geoNear: {
        near: { type: "Point", coordinates: [longitude, latitude] },
        distanceField: "distance",
        maxDistance: maxDistanceKm * 1000,
        spherical: true,
        ...(cuisine && { query: { cuisine } })
      }
    },
    {
      $project: {
        name: 1,
        cuisine: 1,
        address: 1,
        distanceKm: { $round: [{ $divide: ["$distance", 1000] }, 2] },
        distanceMeters: { $round: ["$distance", 0] }
      }
    }
  ]
  
  if (sortBy === "name") {
    pipeline.push({ $sort: { name: 1 } })
  }
  // Default is already sorted by distance from $geoNear
  
  pipeline.push({ $limit: limit })
  
  return db.restaurants.aggregate(pipeline).toArray()
}

// Test the locator
print("=== Store Locator Results ===")

print("\n1. All restaurants within 5km:")
storeLocator({ longitude: -73.97, latitude: 40.77 }).forEach(r => {
  print(`  - ${r.name} (${r.cuisine}): ${r.distanceKm}km`)
})

print("\n2. Italian restaurants only:")
storeLocator({ longitude: -73.97, latitude: 40.77, cuisine: "Italian" }).forEach(r => {
  print(`  - ${r.name}: ${r.distanceKm}km`)
})

print("\n3. Within 1km:")
storeLocator({ longitude: -73.97, latitude: 40.77, maxDistanceKm: 1 }).forEach(r => {
  print(`  - ${r.name}: ${r.distanceMeters}m`)
})
```

### Exercise 5: Geofencing System

```javascript
// Build a geofencing system

// Setup test geofences
db.testFences.drop()
db.testFences.insertMany([
  {
    name: "Zone A",
    type: "delivery",
    fee: 0,
    boundary: {
      type: "Polygon",
      coordinates: [[
        [-73.98, 40.76], [-73.96, 40.76],
        [-73.96, 40.78], [-73.98, 40.78],
        [-73.98, 40.76]
      ]]
    }
  },
  {
    name: "Zone B",
    type: "delivery",
    fee: 5,
    boundary: {
      type: "Polygon",
      coordinates: [[
        [-74.00, 40.74], [-73.94, 40.74],
        [-73.94, 40.80], [-74.00, 40.80],
        [-74.00, 40.74]
      ]]
    }
  },
  {
    name: "No Service",
    type: "restricted",
    boundary: {
      type: "Polygon",
      coordinates: [[
        [-73.92, 40.74], [-73.90, 40.74],
        [-73.90, 40.76], [-73.92, 40.76],
        [-73.92, 40.74]
      ]]
    }
  }
])
db.testFences.createIndex({ boundary: "2dsphere" })

// Geofence checker
function checkDelivery(longitude, latitude) {
  const zones = db.testFences.find({
    boundary: {
      $geoIntersects: {
        $geometry: { type: "Point", coordinates: [longitude, latitude] }
      }
    }
  }).toArray()
  
  if (zones.length === 0) {
    return { deliverable: false, reason: "Location not in service area" }
  }
  
  const restrictedZone = zones.find(z => z.type === "restricted")
  if (restrictedZone) {
    return { deliverable: false, reason: `Location in ${restrictedZone.name}` }
  }
  
  // Find cheapest delivery zone
  const deliveryZones = zones.filter(z => z.type === "delivery")
  const cheapestZone = deliveryZones.sort((a, b) => a.fee - b.fee)[0]
  
  return {
    deliverable: true,
    zone: cheapestZone.name,
    fee: cheapestZone.fee
  }
}

// Test various locations
print("=== Delivery Check Results ===")
const testLocations = [
  { name: "Location 1", lon: -73.97, lat: 40.77 },
  { name: "Location 2", lon: -73.95, lat: 40.75 },
  { name: "Location 3", lon: -73.91, lat: 40.75 },
  { name: "Location 4", lon: -73.80, lat: 40.70 }
]

testLocations.forEach(loc => {
  const result = checkDelivery(loc.lon, loc.lat)
  if (result.deliverable) {
    print(`${loc.name}: ✓ Deliverable (${result.zone}, $${result.fee} fee)`)
  } else {
    print(`${loc.name}: ✗ Not deliverable - ${result.reason}`)
  }
})
```

---

[← Previous: Evaluation Operators](34-evaluation-operators.md) | [Next: Transaction Fundamentals →](36-transaction-fundamentals.md)
