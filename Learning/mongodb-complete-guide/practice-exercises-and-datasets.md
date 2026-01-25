# MongoDB Practice Exercises and Datasets

## Table of Contents
- [Sample Datasets](#sample-datasets)
- [Exercise 1: E-Commerce Platform](#exercise-1-e-commerce-platform)
- [Exercise 2: Social Media Analytics](#exercise-2-social-media-analytics)
- [Exercise 3: IoT Sensor Data](#exercise-3-iot-sensor-data)
- [Exercise 4: Movie Database](#exercise-4-movie-database)
- [Exercise 5: Banking System](#exercise-5-banking-system)
- [Exercise 6: Healthcare Records](#exercise-6-healthcare-records)
- [Exercise 7: Real-Time Analytics Dashboard](#exercise-7-real-time-analytics-dashboard)
- [Exercise 8: Content Management System](#exercise-8-content-management-system)
- [Capstone Project](#capstone-project)

---

## Sample Datasets

### Official MongoDB Sample Datasets

MongoDB Atlas provides free sample datasets. Load them with:

```bash
# Connect to Atlas and load sample data via UI
# Or use mongorestore with these datasets
```

**Atlas Sample Datasets:**
| Dataset | Description | Size | Link |
|---------|-------------|------|------|
| sample_mflix | Movie data with comments | ~25MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-mflix/) |
| sample_airbnb | Airbnb listings | ~55MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-airbnb/) |
| sample_analytics | Financial data | ~10MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-analytics/) |
| sample_geospatial | Shipwrecks locations | ~1MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-geospatial/) |
| sample_restaurants | NYC restaurants | ~7MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-restaurants/) |
| sample_supplies | Sales data | ~2MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-supplies/) |
| sample_training | Various training data | ~60MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-training/) |
| sample_weatherdata | Weather measurements | ~3MB | [Atlas Docs](https://www.mongodb.com/docs/atlas/sample-data/sample-weatherdata/) |

### External Dataset Sources

| Source | Description | Link |
|--------|-------------|------|
| Kaggle | Thousands of datasets (CSV/JSON) | https://www.kaggle.com/datasets |
| data.gov | US Government open data | https://data.gov |
| GitHub awesome-json-datasets | Curated JSON datasets | https://github.com/jdorfman/awesome-json-datasets |
| JSONPlaceholder | Fake REST API for testing | https://jsonplaceholder.typicode.com |
| OpenWeatherMap | Weather data API | https://openweathermap.org/api |
| The Movie DB | Movie and TV data | https://www.themoviedb.org/documentation/api |
| NYC Open Data | New York City datasets | https://opendata.cityofnewyork.us |
| WHO | Health statistics | https://www.who.int/data |

### Quick Dataset Import Commands

```bash
# Import JSON file
mongoimport --db mydb --collection products --file products.json --jsonArray

# Import from URL
curl -o restaurants.json https://raw.githubusercontent.com/mongodb/docs-assets/primer-dataset/primer-dataset.json
mongoimport --db test --collection restaurants --file restaurants.json

# Import CSV
mongoimport --db mydb --collection users --type csv --headerline --file users.csv
```

---

## Exercise 1: E-Commerce Platform

### Dataset Setup

```javascript
// Create the e-commerce database with sample data
use ecommerce_practice

// Categories
db.categories.insertMany([
  { _id: ObjectId(), name: "Electronics", slug: "electronics", parentId: null },
  { _id: ObjectId(), name: "Smartphones", slug: "smartphones", parentId: ObjectId("...") },
  { _id: ObjectId(), name: "Laptops", slug: "laptops", parentId: ObjectId("...") },
  { _id: ObjectId(), name: "Clothing", slug: "clothing", parentId: null },
  { _id: ObjectId(), name: "Men's Wear", slug: "mens-wear", parentId: ObjectId("...") },
  { _id: ObjectId(), name: "Women's Wear", slug: "womens-wear", parentId: ObjectId("...") }
])

// Products (run this to generate 1000 products)
const categories = ["electronics", "smartphones", "laptops", "clothing", "mens-wear", "womens-wear"]
const brands = ["Apple", "Samsung", "Sony", "Nike", "Adidas", "Dell", "HP", "Lenovo"]

for (let i = 1; i <= 1000; i++) {
  db.products.insertOne({
    sku: `SKU-${String(i).padStart(6, '0')}`,
    name: `Product ${i}`,
    description: `Description for product ${i}`,
    category: categories[Math.floor(Math.random() * categories.length)],
    brand: brands[Math.floor(Math.random() * brands.length)],
    price: Math.round((Math.random() * 1000 + 10) * 100) / 100,
    costPrice: Math.round((Math.random() * 500 + 5) * 100) / 100,
    inventory: {
      quantity: Math.floor(Math.random() * 500),
      warehouse: ["WH-001", "WH-002", "WH-003"][Math.floor(Math.random() * 3)],
      reorderLevel: 20
    },
    ratings: {
      average: Math.round((Math.random() * 2 + 3) * 10) / 10,
      count: Math.floor(Math.random() * 500)
    },
    tags: ["tag1", "tag2", "featured"].slice(0, Math.floor(Math.random() * 3) + 1),
    isActive: Math.random() > 0.1,
    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    updatedAt: new Date()
  })
}

// Users (generate 500 users)
const cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
const states = ["NY", "CA", "IL", "TX", "AZ", "PA"]

for (let i = 1; i <= 500; i++) {
  const cityIndex = Math.floor(Math.random() * cities.length)
  db.users.insertOne({
    email: `user${i}@example.com`,
    name: `User ${i}`,
    passwordHash: "hashed_password",
    phone: `+1${String(Math.floor(Math.random() * 9000000000) + 1000000000)}`,
    address: {
      street: `${Math.floor(Math.random() * 9999)} Main St`,
      city: cities[cityIndex],
      state: states[cityIndex],
      zip: String(Math.floor(Math.random() * 90000) + 10000),
      country: "USA"
    },
    preferences: {
      newsletter: Math.random() > 0.5,
      notifications: Math.random() > 0.3
    },
    tier: ["bronze", "silver", "gold", "platinum"][Math.floor(Math.random() * 4)],
    createdAt: new Date(Date.now() - Math.random() * 730 * 24 * 60 * 60 * 1000),
    lastLogin: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
  })
}

// Orders (generate 5000 orders)
const statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
const userIds = db.users.find({}, {_id: 1}).toArray().map(u => u._id)
const productDocs = db.products.find({}, {_id: 1, price: 1, name: 1}).toArray()

for (let i = 1; i <= 5000; i++) {
  const itemCount = Math.floor(Math.random() * 5) + 1
  const items = []
  let subtotal = 0
  
  for (let j = 0; j < itemCount; j++) {
    const product = productDocs[Math.floor(Math.random() * productDocs.length)]
    const quantity = Math.floor(Math.random() * 3) + 1
    const price = product.price
    items.push({
      productId: product._id,
      name: product.name,
      quantity: quantity,
      price: price,
      total: quantity * price
    })
    subtotal += quantity * price
  }
  
  const tax = Math.round(subtotal * 0.08 * 100) / 100
  const shipping = subtotal > 100 ? 0 : 9.99
  
  db.orders.insertOne({
    orderNumber: `ORD-${String(i).padStart(8, '0')}`,
    userId: userIds[Math.floor(Math.random() * userIds.length)],
    items: items,
    subtotal: Math.round(subtotal * 100) / 100,
    tax: tax,
    shipping: shipping,
    total: Math.round((subtotal + tax + shipping) * 100) / 100,
    status: statuses[Math.floor(Math.random() * statuses.length)],
    paymentMethod: ["credit_card", "paypal", "bank_transfer"][Math.floor(Math.random() * 3)],
    shippingAddress: {
      street: `${Math.floor(Math.random() * 9999)} Shipping St`,
      city: cities[Math.floor(Math.random() * cities.length)],
      state: states[Math.floor(Math.random() * states.length)],
      zip: String(Math.floor(Math.random() * 90000) + 10000)
    },
    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    updatedAt: new Date()
  })
}

// Create indexes
db.products.createIndex({ category: 1, price: 1 })
db.products.createIndex({ "inventory.quantity": 1 })
db.products.createIndex({ name: "text", description: "text" })
db.users.createIndex({ email: 1 }, { unique: true })
db.orders.createIndex({ userId: 1, createdAt: -1 })
db.orders.createIndex({ status: 1, createdAt: -1 })
```

### Exercises

#### Exercise 1.1: Basic Queries
**Task:** Find all products in the "electronics" category with price between $100 and $500, sorted by rating (highest first).

<details>
<summary>Solution</summary>

```javascript
db.products.find({
  category: "electronics",
  price: { $gte: 100, $lte: 500 }
}).sort({ "ratings.average": -1 })
```
</details>

#### Exercise 1.2: Inventory Management
**Task:** Find all products that need reordering (quantity below reorder level) and return product name, current quantity, and warehouse.

<details>
<summary>Solution</summary>

```javascript
db.products.find({
  $expr: { $lt: ["$inventory.quantity", "$inventory.reorderLevel"] }
}, {
  name: 1,
  "inventory.quantity": 1,
  "inventory.warehouse": 1,
  "inventory.reorderLevel": 1
})
```
</details>

#### Exercise 1.3: Sales Analytics
**Task:** Calculate total revenue by month for the past year, showing month, order count, and total revenue.

<details>
<summary>Solution</summary>

```javascript
db.orders.aggregate([
  {
    $match: {
      createdAt: { $gte: new Date(new Date().setFullYear(new Date().getFullYear() - 1)) },
      status: { $nin: ["cancelled"] }
    }
  },
  {
    $group: {
      _id: {
        year: { $year: "$createdAt" },
        month: { $month: "$createdAt" }
      },
      orderCount: { $sum: 1 },
      totalRevenue: { $sum: "$total" },
      avgOrderValue: { $avg: "$total" }
    }
  },
  {
    $sort: { "_id.year": 1, "_id.month": 1 }
  },
  {
    $project: {
      _id: 0,
      year: "$_id.year",
      month: "$_id.month",
      orderCount: 1,
      totalRevenue: { $round: ["$totalRevenue", 2] },
      avgOrderValue: { $round: ["$avgOrderValue", 2] }
    }
  }
])
```
</details>

#### Exercise 1.4: Customer Segmentation
**Task:** Segment customers by their total spending: "VIP" (>$5000), "Regular" ($1000-$5000), "Occasional" (<$1000).

<details>
<summary>Solution</summary>

```javascript
db.orders.aggregate([
  {
    $match: { status: { $ne: "cancelled" } }
  },
  {
    $group: {
      _id: "$userId",
      totalSpent: { $sum: "$total" },
      orderCount: { $sum: 1 }
    }
  },
  {
    $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "user"
    }
  },
  {
    $unwind: "$user"
  },
  {
    $addFields: {
      segment: {
        $switch: {
          branches: [
            { case: { $gte: ["$totalSpent", 5000] }, then: "VIP" },
            { case: { $gte: ["$totalSpent", 1000] }, then: "Regular" }
          ],
          default: "Occasional"
        }
      }
    }
  },
  {
    $group: {
      _id: "$segment",
      customerCount: { $sum: 1 },
      avgSpending: { $avg: "$totalSpent" },
      totalRevenue: { $sum: "$totalSpent" }
    }
  },
  {
    $sort: { totalRevenue: -1 }
  }
])
```
</details>

#### Exercise 1.5: Product Performance Dashboard
**Task:** Create a product performance report showing: product name, category, total units sold, total revenue, average order quantity, and profit margin.

<details>
<summary>Solution</summary>

```javascript
db.orders.aggregate([
  { $match: { status: "delivered" } },
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.productId",
      totalUnitsSold: { $sum: "$items.quantity" },
      totalRevenue: { $sum: "$items.total" },
      orderCount: { $sum: 1 }
    }
  },
  {
    $lookup: {
      from: "products",
      localField: "_id",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: "$product" },
  {
    $project: {
      _id: 0,
      productName: "$product.name",
      category: "$product.category",
      totalUnitsSold: 1,
      totalRevenue: { $round: ["$totalRevenue", 2] },
      avgOrderQuantity: { $round: [{ $divide: ["$totalUnitsSold", "$orderCount"] }, 2] },
      profitMargin: {
        $round: [{
          $multiply: [
            { $divide: [
              { $subtract: ["$product.price", "$product.costPrice"] },
              "$product.price"
            ]},
            100
          ]
        }, 2]
      }
    }
  },
  { $sort: { totalRevenue: -1 } },
  { $limit: 20 }
])
```
</details>

#### Exercise 1.6: Cart Abandonment Analysis
**Task:** Find users who have items in their cart (pending orders) but haven't completed a purchase in the last 7 days.

<details>
<summary>Solution</summary>

```javascript
const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)

db.orders.aggregate([
  {
    $facet: {
      pendingOrders: [
        { $match: { status: "pending" } },
        { $group: { _id: "$userId", pendingCount: { $sum: 1 } } }
      ],
      recentPurchases: [
        {
          $match: {
            status: "delivered",
            createdAt: { $gte: sevenDaysAgo }
          }
        },
        { $group: { _id: "$userId" } }
      ]
    }
  },
  {
    $project: {
      abandonedCarts: {
        $filter: {
          input: "$pendingOrders",
          cond: { $not: { $in: ["$$this._id", "$recentPurchases._id"] } }
        }
      }
    }
  },
  { $unwind: "$abandonedCarts" },
  {
    $lookup: {
      from: "users",
      localField: "abandonedCarts._id",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" },
  {
    $project: {
      userId: "$abandonedCarts._id",
      email: "$user.email",
      name: "$user.name",
      pendingOrderCount: "$abandonedCarts.pendingCount"
    }
  }
])
```
</details>

---

## Exercise 2: Social Media Analytics

### Dataset Setup

```javascript
use social_media_practice

// Users
for (let i = 1; i <= 1000; i++) {
  db.users.insertOne({
    username: `user_${i}`,
    displayName: `User ${i}`,
    email: `user${i}@social.com`,
    bio: `Bio for user ${i}. Interests include technology, sports, and music.`,
    profileImage: `https://avatars.example.com/${i}.jpg`,
    followers: [],
    following: [],
    followerCount: 0,
    followingCount: 0,
    isVerified: Math.random() > 0.95,
    joinedAt: new Date(Date.now() - Math.random() * 730 * 24 * 60 * 60 * 1000),
    lastActive: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
  })
}

// Create follow relationships
const allUsers = db.users.find({}, {_id: 1}).toArray()
allUsers.forEach(user => {
  const followCount = Math.floor(Math.random() * 50)
  const toFollow = allUsers
    .filter(u => !u._id.equals(user._id))
    .sort(() => Math.random() - 0.5)
    .slice(0, followCount)
    .map(u => u._id)
  
  db.users.updateOne(
    { _id: user._id },
    { 
      $set: { following: toFollow, followingCount: toFollow.length }
    }
  )
  
  // Update followers
  toFollow.forEach(followedId => {
    db.users.updateOne(
      { _id: followedId },
      { 
        $push: { followers: user._id },
        $inc: { followerCount: 1 }
      }
    )
  })
})

// Posts
const hashtags = ["#tech", "#news", "#sports", "#music", "#food", "#travel", "#photography", "#art"]
const userIds = db.users.find({}, {_id: 1, username: 1}).toArray()

for (let i = 1; i <= 10000; i++) {
  const author = userIds[Math.floor(Math.random() * userIds.length)]
  const postHashtags = hashtags.sort(() => Math.random() - 0.5).slice(0, Math.floor(Math.random() * 4))
  
  db.posts.insertOne({
    authorId: author._id,
    authorUsername: author.username,
    content: `This is post ${i}. ${postHashtags.join(" ")} Some interesting content here.`,
    hashtags: postHashtags,
    media: Math.random() > 0.7 ? [{
      type: ["image", "video"][Math.floor(Math.random() * 2)],
      url: `https://media.example.com/${i}.jpg`
    }] : [],
    likes: [],
    likeCount: 0,
    comments: [],
    commentCount: 0,
    shares: Math.floor(Math.random() * 100),
    isPublic: Math.random() > 0.1,
    createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000),
    updatedAt: new Date()
  })
}

// Add likes and comments to posts
const postIds = db.posts.find({}, {_id: 1}).toArray()
postIds.forEach(post => {
  const likeCount = Math.floor(Math.random() * 200)
  const likers = userIds
    .sort(() => Math.random() - 0.5)
    .slice(0, likeCount)
    .map(u => u._id)
  
  const commentCount = Math.floor(Math.random() * 20)
  const comments = []
  for (let i = 0; i < commentCount; i++) {
    const commenter = userIds[Math.floor(Math.random() * userIds.length)]
    comments.push({
      _id: new ObjectId(),
      authorId: commenter._id,
      authorUsername: commenter.username,
      content: `Comment ${i + 1} on this post`,
      createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
    })
  }
  
  db.posts.updateOne(
    { _id: post._id },
    {
      $set: {
        likes: likers,
        likeCount: likers.length,
        comments: comments,
        commentCount: comments.length
      }
    }
  )
})

// Create indexes
db.users.createIndex({ username: 1 }, { unique: true })
db.users.createIndex({ followerCount: -1 })
db.posts.createIndex({ authorId: 1, createdAt: -1 })
db.posts.createIndex({ hashtags: 1, createdAt: -1 })
db.posts.createIndex({ likeCount: -1, createdAt: -1 })
db.posts.createIndex({ content: "text" })
```

### Exercises

#### Exercise 2.1: Trending Hashtags
**Task:** Find the top 10 trending hashtags in the last 24 hours based on post count and engagement (likes + comments).

<details>
<summary>Solution</summary>

```javascript
const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

db.posts.aggregate([
  {
    $match: {
      createdAt: { $gte: oneDayAgo },
      isPublic: true
    }
  },
  { $unwind: "$hashtags" },
  {
    $group: {
      _id: "$hashtags",
      postCount: { $sum: 1 },
      totalLikes: { $sum: "$likeCount" },
      totalComments: { $sum: "$commentCount" },
      totalShares: { $sum: "$shares" }
    }
  },
  {
    $addFields: {
      engagementScore: {
        $add: [
          "$totalLikes",
          { $multiply: ["$totalComments", 2] },
          { $multiply: ["$totalShares", 3] }
        ]
      }
    }
  },
  { $sort: { engagementScore: -1 } },
  { $limit: 10 },
  {
    $project: {
      hashtag: "$_id",
      postCount: 1,
      totalLikes: 1,
      totalComments: 1,
      totalShares: 1,
      engagementScore: 1,
      _id: 0
    }
  }
])
```
</details>

#### Exercise 2.2: Influencer Identification
**Task:** Find potential influencers: users with follower count > 100, engagement rate > 5%, and at least 10 posts in the last month.

<details>
<summary>Solution</summary>

```javascript
const oneMonthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)

db.users.aggregate([
  {
    $match: {
      followerCount: { $gt: 100 }
    }
  },
  {
    $lookup: {
      from: "posts",
      let: { userId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$authorId", "$$userId"] },
            createdAt: { $gte: oneMonthAgo }
          }
        },
        {
          $group: {
            _id: null,
            postCount: { $sum: 1 },
            totalLikes: { $sum: "$likeCount" },
            totalComments: { $sum: "$commentCount" }
          }
        }
      ],
      as: "recentActivity"
    }
  },
  { $unwind: { path: "$recentActivity", preserveNullAndEmptyArrays: false } },
  {
    $match: {
      "recentActivity.postCount": { $gte: 10 }
    }
  },
  {
    $addFields: {
      engagementRate: {
        $multiply: [
          {
            $divide: [
              { $add: ["$recentActivity.totalLikes", "$recentActivity.totalComments"] },
              { $multiply: ["$followerCount", "$recentActivity.postCount"] }
            ]
          },
          100
        ]
      }
    }
  },
  {
    $match: {
      engagementRate: { $gt: 5 }
    }
  },
  {
    $project: {
      username: 1,
      displayName: 1,
      followerCount: 1,
      isVerified: 1,
      recentPostCount: "$recentActivity.postCount",
      engagementRate: { $round: ["$engagementRate", 2] }
    }
  },
  { $sort: { engagementRate: -1 } },
  { $limit: 20 }
])
```
</details>

#### Exercise 2.3: User Feed Generation
**Task:** Generate a personalized feed for a user showing posts from people they follow, sorted by recency and engagement.

<details>
<summary>Solution</summary>

```javascript
// For a specific user
const userId = db.users.findOne({ username: "user_1" })._id

db.users.aggregate([
  { $match: { _id: userId } },
  {
    $lookup: {
      from: "posts",
      let: { followingList: "$following" },
      pipeline: [
        {
          $match: {
            $expr: { $in: ["$authorId", "$$followingList"] },
            isPublic: true
          }
        },
        {
          $addFields: {
            recencyScore: {
              $divide: [
                1,
                { $add: [
                  1,
                  { $divide: [
                    { $subtract: [new Date(), "$createdAt"] },
                    3600000  // hours
                  ]}
                ]}
              ]
            },
            engagementScore: {
              $add: [
                "$likeCount",
                { $multiply: ["$commentCount", 2] }
              ]
            }
          }
        },
        {
          $addFields: {
            feedScore: {
              $add: [
                { $multiply: ["$recencyScore", 100] },
                { $multiply: ["$engagementScore", 0.1] }
              ]
            }
          }
        },
        { $sort: { feedScore: -1 } },
        { $limit: 50 },
        {
          $project: {
            authorUsername: 1,
            content: 1,
            hashtags: 1,
            likeCount: 1,
            commentCount: 1,
            createdAt: 1,
            feedScore: 1
          }
        }
      ],
      as: "feed"
    }
  },
  { $unwind: "$feed" },
  { $replaceRoot: { newRoot: "$feed" } }
])
```
</details>

#### Exercise 2.4: Mutual Connections
**Task:** For a given user, find users who follow them AND they follow back (mutual connections).

<details>
<summary>Solution</summary>

```javascript
const userId = db.users.findOne({ username: "user_1" })._id

db.users.aggregate([
  { $match: { _id: userId } },
  {
    $project: {
      mutualConnections: {
        $setIntersection: ["$followers", "$following"]
      }
    }
  },
  { $unwind: "$mutualConnections" },
  {
    $lookup: {
      from: "users",
      localField: "mutualConnections",
      foreignField: "_id",
      as: "mutualUser"
    }
  },
  { $unwind: "$mutualUser" },
  {
    $project: {
      _id: "$mutualUser._id",
      username: "$mutualUser.username",
      displayName: "$mutualUser.displayName",
      followerCount: "$mutualUser.followerCount",
      isVerified: "$mutualUser.isVerified"
    }
  },
  { $sort: { followerCount: -1 } }
])
```
</details>

#### Exercise 2.5: Content Analytics Dashboard
**Task:** Create a dashboard showing: total posts, average engagement per post, best posting hour, and content type breakdown.

<details>
<summary>Solution</summary>

```javascript
const userId = db.users.findOne({ username: "user_1" })._id

db.posts.aggregate([
  { $match: { authorId: userId } },
  {
    $facet: {
      overview: [
        {
          $group: {
            _id: null,
            totalPosts: { $sum: 1 },
            totalLikes: { $sum: "$likeCount" },
            totalComments: { $sum: "$commentCount" },
            totalShares: { $sum: "$shares" },
            avgLikes: { $avg: "$likeCount" },
            avgComments: { $avg: "$commentCount" }
          }
        }
      ],
      byHour: [
        {
          $group: {
            _id: { $hour: "$createdAt" },
            postCount: { $sum: 1 },
            avgEngagement: { $avg: { $add: ["$likeCount", "$commentCount"] } }
          }
        },
        { $sort: { avgEngagement: -1 } },
        { $limit: 1 }
      ],
      byContentType: [
        {
          $addFields: {
            contentType: {
              $cond: {
                if: { $gt: [{ $size: "$media" }, 0] },
                then: { $arrayElemAt: ["$media.type", 0] },
                else: "text"
              }
            }
          }
        },
        {
          $group: {
            _id: "$contentType",
            count: { $sum: 1 },
            avgEngagement: { $avg: { $add: ["$likeCount", "$commentCount"] } }
          }
        }
      ],
      topPosts: [
        { $sort: { likeCount: -1 } },
        { $limit: 5 },
        {
          $project: {
            content: { $substr: ["$content", 0, 100] },
            likeCount: 1,
            commentCount: 1,
            createdAt: 1
          }
        }
      ]
    }
  },
  {
    $project: {
      overview: { $arrayElemAt: ["$overview", 0] },
      bestPostingHour: { $arrayElemAt: ["$byHour", 0] },
      contentTypeBreakdown: "$byContentType",
      topPosts: "$topPosts"
    }
  }
])
```
</details>

---

## Exercise 3: IoT Sensor Data

### Dataset Setup

```javascript
use iot_practice

// Devices
const deviceTypes = ["temperature", "humidity", "pressure", "motion", "air_quality"]
const locations = [
  { building: "Building A", floor: 1, room: "101" },
  { building: "Building A", floor: 1, room: "102" },
  { building: "Building A", floor: 2, room: "201" },
  { building: "Building B", floor: 1, room: "101" },
  { building: "Building B", floor: 2, room: "201" }
]

for (let i = 1; i <= 50; i++) {
  const location = locations[Math.floor(Math.random() * locations.length)]
  db.devices.insertOne({
    deviceId: `DEV-${String(i).padStart(4, '0')}`,
    type: deviceTypes[Math.floor(Math.random() * deviceTypes.length)],
    location: location,
    status: ["active", "inactive", "maintenance"][Math.floor(Math.random() * 10) < 8 ? 0 : Math.floor(Math.random() * 2) + 1],
    firmware: `v${Math.floor(Math.random() * 3) + 1}.${Math.floor(Math.random() * 10)}.${Math.floor(Math.random() * 10)}`,
    installedAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    lastMaintenance: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000)
  })
}

// Sensor readings (time series data - 1 week of data)
const devices = db.devices.find({}, {deviceId: 1, type: 1}).toArray()

// Create time series collection
db.createCollection("readings", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "minutes"
  }
})

// Generate readings for the past 7 days (every 5 minutes)
const now = new Date()
const startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)

devices.forEach(device => {
  const readings = []
  let currentTime = new Date(startTime)
  
  while (currentTime <= now) {
    let value
    switch (device.type) {
      case "temperature":
        value = 20 + Math.random() * 10 + Math.sin(currentTime.getHours() / 24 * Math.PI * 2) * 5
        break
      case "humidity":
        value = 40 + Math.random() * 30
        break
      case "pressure":
        value = 1000 + Math.random() * 50
        break
      case "motion":
        value = Math.random() > 0.7 ? 1 : 0
        break
      case "air_quality":
        value = Math.floor(Math.random() * 200)
        break
    }
    
    readings.push({
      timestamp: new Date(currentTime),
      metadata: {
        deviceId: device.deviceId,
        type: device.type
      },
      value: Math.round(value * 100) / 100,
      unit: device.type === "temperature" ? "°C" : 
            device.type === "humidity" ? "%" :
            device.type === "pressure" ? "hPa" :
            device.type === "motion" ? "detected" : "AQI"
    })
    
    currentTime = new Date(currentTime.getTime() + 5 * 60 * 1000)  // 5 minutes
  }
  
  // Batch insert
  for (let i = 0; i < readings.length; i += 1000) {
    db.readings.insertMany(readings.slice(i, i + 1000))
  }
})

// Alerts
db.createCollection("alerts")
db.alerts.createIndex({ deviceId: 1, timestamp: -1 })
db.alerts.createIndex({ severity: 1, acknowledged: 1 })

// Create indexes
db.devices.createIndex({ deviceId: 1 }, { unique: true })
db.devices.createIndex({ "location.building": 1, type: 1 })
```

### Exercises

#### Exercise 3.1: Real-Time Dashboard Query
**Task:** Get the latest reading for each active device, showing device info and current value.

<details>
<summary>Solution</summary>

```javascript
db.devices.aggregate([
  { $match: { status: "active" } },
  {
    $lookup: {
      from: "readings",
      let: { devId: "$deviceId" },
      pipeline: [
        { $match: { $expr: { $eq: ["$metadata.deviceId", "$$devId"] } } },
        { $sort: { timestamp: -1 } },
        { $limit: 1 }
      ],
      as: "latestReading"
    }
  },
  { $unwind: { path: "$latestReading", preserveNullAndEmptyArrays: true } },
  {
    $project: {
      deviceId: 1,
      type: 1,
      location: 1,
      currentValue: "$latestReading.value",
      unit: "$latestReading.unit",
      lastUpdate: "$latestReading.timestamp",
      timeSinceUpdate: {
        $divide: [
          { $subtract: [new Date(), "$latestReading.timestamp"] },
          60000  // minutes
        ]
      }
    }
  },
  { $sort: { "location.building": 1, "location.floor": 1 } }
])
```
</details>

#### Exercise 3.2: Anomaly Detection
**Task:** Find temperature readings that are more than 2 standard deviations from the hourly average.

<details>
<summary>Solution</summary>

```javascript
db.readings.aggregate([
  {
    $match: {
      "metadata.type": "temperature",
      timestamp: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
    }
  },
  {
    $group: {
      _id: {
        deviceId: "$metadata.deviceId",
        hour: { $hour: "$timestamp" }
      },
      readings: { $push: { value: "$value", timestamp: "$timestamp" } },
      avg: { $avg: "$value" },
      stdDev: { $stdDevPop: "$value" }
    }
  },
  { $unwind: "$readings" },
  {
    $addFields: {
      deviation: { $abs: { $subtract: ["$readings.value", "$avg"] } },
      threshold: { $multiply: ["$stdDev", 2] }
    }
  },
  {
    $match: {
      $expr: { $gt: ["$deviation", "$threshold"] }
    }
  },
  {
    $project: {
      deviceId: "$_id.deviceId",
      hour: "$_id.hour",
      anomalyValue: "$readings.value",
      timestamp: "$readings.timestamp",
      hourlyAvg: { $round: ["$avg", 2] },
      stdDev: { $round: ["$stdDev", 2] },
      deviationAmount: { $round: ["$deviation", 2] }
    }
  },
  { $sort: { timestamp: -1 } }
])
```
</details>

#### Exercise 3.3: Building Energy Report
**Task:** Calculate average temperature by building and floor for the past 24 hours, identifying floors that might need HVAC adjustment.

<details>
<summary>Solution</summary>

```javascript
const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

db.readings.aggregate([
  {
    $match: {
      "metadata.type": "temperature",
      timestamp: { $gte: oneDayAgo }
    }
  },
  {
    $lookup: {
      from: "devices",
      localField: "metadata.deviceId",
      foreignField: "deviceId",
      as: "device"
    }
  },
  { $unwind: "$device" },
  {
    $group: {
      _id: {
        building: "$device.location.building",
        floor: "$device.location.floor"
      },
      avgTemp: { $avg: "$value" },
      minTemp: { $min: "$value" },
      maxTemp: { $max: "$value" },
      readingCount: { $sum: 1 },
      devices: { $addToSet: "$metadata.deviceId" }
    }
  },
  {
    $addFields: {
      temperatureVariance: { $subtract: ["$maxTemp", "$minTemp"] },
      hvacRecommendation: {
        $switch: {
          branches: [
            { case: { $lt: ["$avgTemp", 18] }, then: "Increase heating" },
            { case: { $gt: ["$avgTemp", 26] }, then: "Increase cooling" },
            { case: { $gt: ["$temperatureVariance", 5] }, then: "Check HVAC balance" }
          ],
          default: "Optimal"
        }
      }
    }
  },
  {
    $project: {
      _id: 0,
      building: "$_id.building",
      floor: "$_id.floor",
      avgTemp: { $round: ["$avgTemp", 1] },
      minTemp: { $round: ["$minTemp", 1] },
      maxTemp: { $round: ["$maxTemp", 1] },
      temperatureVariance: { $round: ["$temperatureVariance", 1] },
      deviceCount: { $size: "$devices" },
      hvacRecommendation: 1
    }
  },
  { $sort: { building: 1, floor: 1 } }
])
```
</details>

#### Exercise 3.4: Device Health Monitoring
**Task:** Identify devices that haven't reported data in the last hour or have irregular reporting patterns.

<details>
<summary>Solution</summary>

```javascript
const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

db.devices.aggregate([
  { $match: { status: "active" } },
  {
    $lookup: {
      from: "readings",
      let: { devId: "$deviceId" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$metadata.deviceId", "$$devId"] },
            timestamp: { $gte: oneDayAgo }
          }
        },
        {
          $group: {
            _id: null,
            lastReading: { $max: "$timestamp" },
            readingCount: { $sum: 1 },
            avgInterval: {
              $avg: {
                $divide: [
                  { $subtract: ["$timestamp", oneDayAgo] },
                  60000
                ]
              }
            }
          }
        }
      ],
      as: "stats"
    }
  },
  { $unwind: { path: "$stats", preserveNullAndEmptyArrays: true } },
  {
    $addFields: {
      healthStatus: {
        $switch: {
          branches: [
            {
              case: { $eq: ["$stats", null] },
              then: "No data"
            },
            {
              case: { $lt: ["$stats.lastReading", oneHourAgo] },
              then: "Offline"
            },
            {
              case: { $lt: ["$stats.readingCount", 200] },  // Expected ~288 for 5-min intervals
              then: "Intermittent"
            }
          ],
          default: "Healthy"
        }
      },
      minutesSinceLastReading: {
        $cond: {
          if: { $ne: ["$stats", null] },
          then: {
            $divide: [
              { $subtract: [new Date(), "$stats.lastReading"] },
              60000
            ]
          },
          else: null
        }
      }
    }
  },
  {
    $match: {
      healthStatus: { $ne: "Healthy" }
    }
  },
  {
    $project: {
      deviceId: 1,
      type: 1,
      location: 1,
      healthStatus: 1,
      lastReading: "$stats.lastReading",
      minutesSinceLastReading: { $round: ["$minutesSinceLastReading", 0] },
      readingsIn24h: "$stats.readingCount"
    }
  },
  { $sort: { healthStatus: 1, minutesSinceLastReading: -1 } }
])
```
</details>

---

## Exercise 4: Movie Database

### Dataset Setup

Use MongoDB's sample_mflix dataset or create your own:

```javascript
use movies_practice

// Genres
const genres = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Documentary", "Animation", "Adventure"]

// Movies
for (let i = 1; i <= 2000; i++) {
  const movieGenres = genres.sort(() => Math.random() - 0.5).slice(0, Math.floor(Math.random() * 3) + 1)
  const year = 1970 + Math.floor(Math.random() * 55)
  
  db.movies.insertOne({
    title: `Movie ${i}`,
    year: year,
    released: new Date(`${year}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`),
    runtime: 80 + Math.floor(Math.random() * 100),
    genres: movieGenres,
    director: `Director ${Math.floor(Math.random() * 200) + 1}`,
    writers: [`Writer ${Math.floor(Math.random() * 300) + 1}`],
    cast: Array.from({length: Math.floor(Math.random() * 5) + 3}, () => `Actor ${Math.floor(Math.random() * 500) + 1}`),
    plot: `Plot summary for movie ${i}. An exciting story about adventure and discovery.`,
    languages: ["English", "Spanish", "French"].slice(0, Math.floor(Math.random() * 2) + 1),
    countries: ["USA", "UK", "France", "Germany"].slice(0, Math.floor(Math.random() * 2) + 1),
    awards: {
      wins: Math.floor(Math.random() * 10),
      nominations: Math.floor(Math.random() * 20),
      text: `${Math.floor(Math.random() * 10)} wins & ${Math.floor(Math.random() * 20)} nominations`
    },
    imdb: {
      rating: Math.round((Math.random() * 4 + 5) * 10) / 10,
      votes: Math.floor(Math.random() * 500000) + 1000
    },
    tomatoes: {
      viewer: {
        rating: Math.round((Math.random() * 2 + 3) * 10) / 10,
        numReviews: Math.floor(Math.random() * 100000) + 100
      },
      critic: {
        rating: Math.round((Math.random() * 3 + 5) * 10) / 10,
        numReviews: Math.floor(Math.random() * 300) + 10
      }
    },
    budget: Math.floor(Math.random() * 200000000) + 1000000,
    boxOffice: Math.floor(Math.random() * 500000000) + 500000
  })
}

// Reviews
const movieIds = db.movies.find({}, {_id: 1}).toArray()
for (let i = 1; i <= 50000; i++) {
  db.reviews.insertOne({
    movieId: movieIds[Math.floor(Math.random() * movieIds.length)]._id,
    userId: `user_${Math.floor(Math.random() * 1000) + 1}`,
    rating: Math.floor(Math.random() * 5) + 1,
    review: `This is review ${i}. ${["Great movie!", "Average film.", "Disappointing.", "Must watch!", "Entertaining."][Math.floor(Math.random() * 5)]}`,
    helpful: {
      yes: Math.floor(Math.random() * 100),
      no: Math.floor(Math.random() * 20)
    },
    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000)
  })
}

// Indexes
db.movies.createIndex({ genres: 1, "imdb.rating": -1 })
db.movies.createIndex({ year: 1, "imdb.rating": -1 })
db.movies.createIndex({ title: "text", plot: "text" })
db.reviews.createIndex({ movieId: 1, createdAt: -1 })
```

### Exercises

#### Exercise 4.1: Genre Analysis
**Task:** Find the top-rated movie for each genre with at least 10,000 IMDB votes.

<details>
<summary>Solution</summary>

```javascript
db.movies.aggregate([
  { $match: { "imdb.votes": { $gte: 10000 } } },
  { $unwind: "$genres" },
  { $sort: { "imdb.rating": -1 } },
  {
    $group: {
      _id: "$genres",
      topMovie: { $first: "$$ROOT" }
    }
  },
  {
    $project: {
      genre: "$_id",
      title: "$topMovie.title",
      year: "$topMovie.year",
      imdbRating: "$topMovie.imdb.rating",
      imdbVotes: "$topMovie.imdb.votes",
      director: "$topMovie.director"
    }
  },
  { $sort: { imdbRating: -1 } }
])
```
</details>

#### Exercise 4.2: Director Performance
**Task:** Rank directors by their average movie rating (min 3 movies), showing total movies, average rating, and total box office.

<details>
<summary>Solution</summary>

```javascript
db.movies.aggregate([
  {
    $group: {
      _id: "$director",
      movieCount: { $sum: 1 },
      avgRating: { $avg: "$imdb.rating" },
      totalBoxOffice: { $sum: "$boxOffice" },
      movies: { $push: { title: "$title", rating: "$imdb.rating" } }
    }
  },
  { $match: { movieCount: { $gte: 3 } } },
  {
    $project: {
      director: "$_id",
      movieCount: 1,
      avgRating: { $round: ["$avgRating", 2] },
      totalBoxOffice: 1,
      topMovies: { $slice: [
        { $sortArray: { input: "$movies", sortBy: { rating: -1 } } },
        3
      ]}
    }
  },
  { $sort: { avgRating: -1 } },
  { $limit: 20 }
])
```
</details>

#### Exercise 4.3: Review Sentiment Analysis
**Task:** For each movie, calculate review statistics and identify controversial movies (high variance in ratings).

<details>
<summary>Solution</summary>

```javascript
db.reviews.aggregate([
  {
    $group: {
      _id: "$movieId",
      reviewCount: { $sum: 1 },
      avgRating: { $avg: "$rating" },
      ratingStdDev: { $stdDevPop: "$rating" },
      ratingDistribution: {
        $push: "$rating"
      }
    }
  },
  { $match: { reviewCount: { $gte: 10 } } },
  {
    $lookup: {
      from: "movies",
      localField: "_id",
      foreignField: "_id",
      as: "movie"
    }
  },
  { $unwind: "$movie" },
  {
    $addFields: {
      isControversial: { $gt: ["$ratingStdDev", 1.5] },
      ratingBreakdown: {
        "1star": { $size: { $filter: { input: "$ratingDistribution", cond: { $eq: ["$$this", 1] } } } },
        "2star": { $size: { $filter: { input: "$ratingDistribution", cond: { $eq: ["$$this", 2] } } } },
        "3star": { $size: { $filter: { input: "$ratingDistribution", cond: { $eq: ["$$this", 3] } } } },
        "4star": { $size: { $filter: { input: "$ratingDistribution", cond: { $eq: ["$$this", 4] } } } },
        "5star": { $size: { $filter: { input: "$ratingDistribution", cond: { $eq: ["$$this", 5] } } } }
      }
    }
  },
  {
    $project: {
      title: "$movie.title",
      imdbRating: "$movie.imdb.rating",
      reviewCount: 1,
      avgUserRating: { $round: ["$avgRating", 2] },
      ratingStdDev: { $round: ["$ratingStdDev", 2] },
      isControversial: 1,
      ratingBreakdown: 1
    }
  },
  { $sort: { ratingStdDev: -1 } },
  { $limit: 20 }
])
```
</details>

#### Exercise 4.4: Decade Trends
**Task:** Analyze how movie characteristics have changed by decade (avg runtime, avg rating, most popular genres).

<details>
<summary>Solution</summary>

```javascript
db.movies.aggregate([
  {
    $addFields: {
      decade: { $subtract: ["$year", { $mod: ["$year", 10] }] }
    }
  },
  { $unwind: "$genres" },
  {
    $group: {
      _id: {
        decade: "$decade",
        genre: "$genres"
      },
      count: { $sum: 1 },
      avgRating: { $avg: "$imdb.rating" }
    }
  },
  { $sort: { "_id.decade": 1, count: -1 } },
  {
    $group: {
      _id: "$_id.decade",
      genres: { $push: { genre: "$_id.genre", count: "$count", avgRating: "$avgRating" } }
    }
  },
  {
    $lookup: {
      from: "movies",
      let: { dec: "$_id" },
      pipeline: [
        {
          $addFields: {
            decade: { $subtract: ["$year", { $mod: ["$year", 10] }] }
          }
        },
        { $match: { $expr: { $eq: ["$decade", "$$dec"] } } },
        {
          $group: {
            _id: null,
            movieCount: { $sum: 1 },
            avgRuntime: { $avg: "$runtime" },
            avgRating: { $avg: "$imdb.rating" },
            avgBudget: { $avg: "$budget" },
            avgBoxOffice: { $avg: "$boxOffice" }
          }
        }
      ],
      as: "stats"
    }
  },
  { $unwind: "$stats" },
  {
    $project: {
      decade: "$_id",
      movieCount: "$stats.movieCount",
      avgRuntime: { $round: ["$stats.avgRuntime", 0] },
      avgRating: { $round: ["$stats.avgRating", 2] },
      avgBudget: { $round: ["$stats.avgBudget", 0] },
      avgBoxOffice: { $round: ["$stats.avgBoxOffice", 0] },
      topGenres: { $slice: ["$genres", 3] }
    }
  },
  { $sort: { decade: 1 } }
])
```
</details>

---

## Exercise 5: Banking System

### Dataset Setup

```javascript
use banking_practice

// Customers
for (let i = 1; i <= 1000; i++) {
  db.customers.insertOne({
    customerId: `CUST-${String(i).padStart(6, '0')}`,
    name: `Customer ${i}`,
    email: `customer${i}@bank.com`,
    phone: `+1${String(Math.floor(Math.random() * 9000000000) + 1000000000)}`,
    dateOfBirth: new Date(1950 + Math.floor(Math.random() * 50), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
    address: {
      street: `${Math.floor(Math.random() * 9999)} Bank St`,
      city: ["New York", "Los Angeles", "Chicago", "Houston"][Math.floor(Math.random() * 4)],
      state: ["NY", "CA", "IL", "TX"][Math.floor(Math.random() * 4)],
      zip: String(Math.floor(Math.random() * 90000) + 10000)
    },
    kycStatus: ["pending", "verified", "rejected"][Math.floor(Math.random() * 10) < 8 ? 1 : Math.floor(Math.random() * 2)],
    creditScore: 300 + Math.floor(Math.random() * 550),
    createdAt: new Date(Date.now() - Math.random() * 1825 * 24 * 60 * 60 * 1000)
  })
}

// Accounts
const customers = db.customers.find({}, {_id: 1, customerId: 1}).toArray()
const accountTypes = ["checking", "savings", "money_market", "cd"]

customers.forEach(customer => {
  const numAccounts = Math.floor(Math.random() * 3) + 1
  for (let i = 0; i < numAccounts; i++) {
    const type = accountTypes[Math.floor(Math.random() * accountTypes.length)]
    db.accounts.insertOne({
      accountNumber: `ACC-${String(Math.floor(Math.random() * 900000000) + 100000000)}`,
      customerId: customer._id,
      type: type,
      balance: NumberDecimal(String(Math.round(Math.random() * 100000 * 100) / 100)),
      currency: "USD",
      interestRate: type === "savings" ? 0.02 : type === "money_market" ? 0.03 : type === "cd" ? 0.04 : 0,
      status: ["active", "dormant", "closed"][Math.floor(Math.random() * 10) < 9 ? 0 : Math.floor(Math.random() * 2) + 1],
      openedAt: new Date(Date.now() - Math.random() * 1460 * 24 * 60 * 60 * 1000),
      lastActivity: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000)
    })
  }
})

// Transactions
const accounts = db.accounts.find({ status: "active" }, {_id: 1, accountNumber: 1, balance: 1}).toArray()
const txTypes = ["deposit", "withdrawal", "transfer", "payment", "fee", "interest"]

for (let i = 1; i <= 100000; i++) {
  const account = accounts[Math.floor(Math.random() * accounts.length)]
  const type = txTypes[Math.floor(Math.random() * txTypes.length)]
  const amount = type === "fee" ? Math.random() * 50 : 
                 type === "interest" ? Math.random() * 100 :
                 Math.random() * 5000 + 10
  
  const tx = {
    transactionId: `TXN-${String(i).padStart(10, '0')}`,
    accountId: account._id,
    accountNumber: account.accountNumber,
    type: type,
    amount: NumberDecimal(String(Math.round(amount * 100) / 100)),
    currency: "USD",
    description: `${type.charAt(0).toUpperCase() + type.slice(1)} transaction`,
    status: ["completed", "pending", "failed"][Math.floor(Math.random() * 10) < 9 ? 0 : Math.floor(Math.random() * 2) + 1],
    timestamp: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    metadata: {}
  }
  
  if (type === "transfer") {
    const toAccount = accounts[Math.floor(Math.random() * accounts.length)]
    tx.metadata.toAccountId = toAccount._id
    tx.metadata.toAccountNumber = toAccount.accountNumber
  }
  
  db.transactions.insertOne(tx)
}

// Indexes
db.customers.createIndex({ customerId: 1 }, { unique: true })
db.customers.createIndex({ creditScore: 1 })
db.accounts.createIndex({ accountNumber: 1 }, { unique: true })
db.accounts.createIndex({ customerId: 1, type: 1 })
db.transactions.createIndex({ accountId: 1, timestamp: -1 })
db.transactions.createIndex({ type: 1, timestamp: -1 })
db.transactions.createIndex({ transactionId: 1 }, { unique: true })
```

### Exercises

#### Exercise 5.1: Account Statement
**Task:** Generate a monthly statement for an account showing opening balance, all transactions, and closing balance.

<details>
<summary>Solution</summary>

```javascript
const accountNumber = db.accounts.findOne()?.accountNumber
const startDate = new Date("2024-01-01")
const endDate = new Date("2024-02-01")

db.accounts.aggregate([
  { $match: { accountNumber: accountNumber } },
  {
    $lookup: {
      from: "transactions",
      let: { accId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$accountId", "$$accId"] },
            timestamp: { $lt: startDate },
            status: "completed"
          }
        },
        {
          $group: {
            _id: null,
            openingBalance: {
              $sum: {
                $cond: [
                  { $in: ["$type", ["deposit", "interest", "transfer_in"]] },
                  { $toDouble: "$amount" },
                  { $multiply: [{ $toDouble: "$amount" }, -1] }
                ]
              }
            }
          }
        }
      ],
      as: "opening"
    }
  },
  {
    $lookup: {
      from: "transactions",
      let: { accId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$accountId", "$$accId"] },
            timestamp: { $gte: startDate, $lt: endDate },
            status: "completed"
          }
        },
        { $sort: { timestamp: 1 } },
        {
          $project: {
            transactionId: 1,
            type: 1,
            amount: 1,
            description: 1,
            timestamp: 1
          }
        }
      ],
      as: "transactions"
    }
  },
  {
    $addFields: {
      openingBalance: { $ifNull: [{ $arrayElemAt: ["$opening.openingBalance", 0] }, 0] },
      periodActivity: {
        credits: {
          $reduce: {
            input: "$transactions",
            initialValue: 0,
            in: {
              $cond: [
                { $in: ["$$this.type", ["deposit", "interest"]] },
                { $add: ["$$value", { $toDouble: "$$this.amount" }] },
                "$$value"
              ]
            }
          }
        },
        debits: {
          $reduce: {
            input: "$transactions",
            initialValue: 0,
            in: {
              $cond: [
                { $in: ["$$this.type", ["withdrawal", "payment", "fee", "transfer"]] },
                { $add: ["$$value", { $toDouble: "$$this.amount" }] },
                "$$value"
              ]
            }
          }
        }
      }
    }
  },
  {
    $project: {
      accountNumber: 1,
      type: 1,
      statementPeriod: { start: startDate, end: endDate },
      openingBalance: { $round: ["$openingBalance", 2] },
      totalCredits: { $round: ["$periodActivity.credits", 2] },
      totalDebits: { $round: ["$periodActivity.debits", 2] },
      closingBalance: {
        $round: [{
          $add: [
            "$openingBalance",
            "$periodActivity.credits",
            { $multiply: ["$periodActivity.debits", -1] }
          ]
        }, 2]
      },
      transactionCount: { $size: "$transactions" },
      transactions: 1
    }
  }
])
```
</details>

#### Exercise 5.2: Fraud Detection
**Task:** Identify suspicious transactions: multiple large withdrawals in short time, unusual transaction patterns.

<details>
<summary>Solution</summary>

```javascript
const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

db.transactions.aggregate([
  {
    $match: {
      type: "withdrawal",
      timestamp: { $gte: oneDayAgo },
      status: "completed"
    }
  },
  {
    $group: {
      _id: "$accountId",
      withdrawals: { $push: { amount: "$amount", timestamp: "$timestamp", txId: "$transactionId" } },
      totalWithdrawn: { $sum: { $toDouble: "$amount" } },
      withdrawalCount: { $sum: 1 },
      avgAmount: { $avg: { $toDouble: "$amount" } }
    }
  },
  {
    $lookup: {
      from: "transactions",
      let: { accId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$accountId", "$$accId"] },
            type: "withdrawal",
            timestamp: { $lt: oneDayAgo }
          }
        },
        {
          $group: {
            _id: null,
            historicalAvg: { $avg: { $toDouble: "$amount" } },
            historicalCount: { $sum: 1 }
          }
        }
      ],
      as: "historical"
    }
  },
  { $unwind: { path: "$historical", preserveNullAndEmptyArrays: true } },
  {
    $addFields: {
      suspiciousFlags: {
        $filter: {
          input: [
            {
              $cond: [
                { $gte: ["$withdrawalCount", 5] },
                "High frequency (5+ withdrawals in 24h)",
                null
              ]
            },
            {
              $cond: [
                { $gte: ["$totalWithdrawn", 10000] },
                "Large total amount (>$10,000)",
                null
              ]
            },
            {
              $cond: [
                { $and: [
                  { $ne: ["$historical", null] },
                  { $gt: ["$avgAmount", { $multiply: ["$historical.historicalAvg", 3] }] }
                ]},
                "Amount significantly higher than historical average",
                null
              ]
            }
          ],
          cond: { $ne: ["$$this", null] }
        }
      }
    }
  },
  {
    $match: {
      $expr: { $gt: [{ $size: "$suspiciousFlags" }, 0] }
    }
  },
  {
    $lookup: {
      from: "accounts",
      localField: "_id",
      foreignField: "_id",
      as: "account"
    }
  },
  { $unwind: "$account" },
  {
    $project: {
      accountNumber: "$account.accountNumber",
      withdrawalCount: 1,
      totalWithdrawn: { $round: ["$totalWithdrawn", 2] },
      avgAmount: { $round: ["$avgAmount", 2] },
      suspiciousFlags: 1,
      recentWithdrawals: { $slice: ["$withdrawals", 5] }
    }
  },
  { $sort: { totalWithdrawn: -1 } }
])
```
</details>

#### Exercise 5.3: Customer 360 View
**Task:** Create a comprehensive customer profile showing all accounts, total balance, recent transactions, and risk assessment.

<details>
<summary>Solution</summary>

```javascript
const customerId = db.customers.findOne()?.customerId

db.customers.aggregate([
  { $match: { customerId: customerId } },
  {
    $lookup: {
      from: "accounts",
      localField: "_id",
      foreignField: "customerId",
      as: "accounts"
    }
  },
  {
    $lookup: {
      from: "transactions",
      let: { accountIds: "$accounts._id" },
      pipeline: [
        { $match: { $expr: { $in: ["$accountId", "$$accountIds"] } } },
        { $sort: { timestamp: -1 } },
        { $limit: 10 },
        {
          $project: {
            accountNumber: 1,
            type: 1,
            amount: 1,
            timestamp: 1,
            status: 1
          }
        }
      ],
      as: "recentTransactions"
    }
  },
  {
    $addFields: {
      totalBalance: {
        $reduce: {
          input: "$accounts",
          initialValue: 0,
          in: { $add: ["$$value", { $toDouble: "$$this.balance" }] }
        }
      },
      accountSummary: {
        $map: {
          input: "$accounts",
          as: "acc",
          in: {
            accountNumber: "$$acc.accountNumber",
            type: "$$acc.type",
            balance: "$$acc.balance",
            status: "$$acc.status"
          }
        }
      }
    }
  },
  {
    $addFields: {
      riskProfile: {
        $switch: {
          branches: [
            {
              case: { $and: [
                { $lt: ["$creditScore", 600] },
                { $lt: ["$totalBalance", 1000] }
              ]},
              then: "High Risk"
            },
            {
              case: { $or: [
                { $lt: ["$creditScore", 650] },
                { $lt: ["$totalBalance", 5000] }
              ]},
              then: "Medium Risk"
            }
          ],
          default: "Low Risk"
        }
      },
      relationshipValue: {
        $switch: {
          branches: [
            { case: { $gte: ["$totalBalance", 100000] }, then: "Platinum" },
            { case: { $gte: ["$totalBalance", 50000] }, then: "Gold" },
            { case: { $gte: ["$totalBalance", 10000] }, then: "Silver" }
          ],
          default: "Standard"
        }
      }
    }
  },
  {
    $project: {
      customerId: 1,
      name: 1,
      email: 1,
      creditScore: 1,
      kycStatus: 1,
      customerSince: "$createdAt",
      accountCount: { $size: "$accounts" },
      totalBalance: { $round: ["$totalBalance", 2] },
      accountSummary: 1,
      recentTransactions: 1,
      riskProfile: 1,
      relationshipValue: 1
    }
  }
])
```
</details>

---

## Exercise 6: Healthcare Records

### Dataset Setup

```javascript
use healthcare_practice

// Patients
const conditions = ["Diabetes", "Hypertension", "Asthma", "Heart Disease", "Allergies", "None"]
const medications = ["Metformin", "Lisinopril", "Albuterol", "Aspirin", "Omeprazole"]

for (let i = 1; i <= 500; i++) {
  const patientConditions = conditions.filter(() => Math.random() > 0.7)
  const patientMedications = medications.filter(() => Math.random() > 0.6)
  
  db.patients.insertOne({
    patientId: `PAT-${String(i).padStart(6, '0')}`,
    name: `Patient ${i}`,
    dateOfBirth: new Date(1940 + Math.floor(Math.random() * 70), Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
    gender: ["Male", "Female"][Math.floor(Math.random() * 2)],
    bloodType: ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"][Math.floor(Math.random() * 8)],
    contact: {
      phone: `+1${String(Math.floor(Math.random() * 9000000000) + 1000000000)}`,
      email: `patient${i}@health.com`,
      emergencyContact: {
        name: `Emergency Contact ${i}`,
        phone: `+1${String(Math.floor(Math.random() * 9000000000) + 1000000000)}`,
        relationship: ["Spouse", "Parent", "Child", "Sibling"][Math.floor(Math.random() * 4)]
      }
    },
    insurance: {
      provider: ["BlueCross", "Aetna", "UnitedHealth", "Cigna"][Math.floor(Math.random() * 4)],
      policyNumber: `INS-${Math.floor(Math.random() * 900000) + 100000}`,
      groupNumber: `GRP-${Math.floor(Math.random() * 9000) + 1000}`
    },
    medicalHistory: {
      conditions: patientConditions.length > 0 ? patientConditions : ["None"],
      allergies: Math.random() > 0.7 ? ["Penicillin", "Sulfa", "Latex"].slice(0, Math.floor(Math.random() * 2) + 1) : [],
      medications: patientMedications,
      surgeries: Math.random() > 0.8 ? [{
        procedure: "Appendectomy",
        date: new Date(Date.now() - Math.random() * 3650 * 24 * 60 * 60 * 1000)
      }] : []
    },
    registeredAt: new Date(Date.now() - Math.random() * 1825 * 24 * 60 * 60 * 1000)
  })
}

// Doctors
const specialties = ["General Practice", "Cardiology", "Orthopedics", "Dermatology", "Pediatrics", "Neurology"]

for (let i = 1; i <= 50; i++) {
  db.doctors.insertOne({
    doctorId: `DOC-${String(i).padStart(4, '0')}`,
    name: `Dr. ${["Smith", "Johnson", "Williams", "Brown", "Jones"][Math.floor(Math.random() * 5)]} ${i}`,
    specialty: specialties[Math.floor(Math.random() * specialties.length)],
    qualifications: ["MD", "MBBS", "PhD"][Math.floor(Math.random() * 3)],
    experience: Math.floor(Math.random() * 30) + 5,
    availability: {
      monday: { start: "09:00", end: "17:00" },
      tuesday: { start: "09:00", end: "17:00" },
      wednesday: { start: "09:00", end: "17:00" },
      thursday: { start: "09:00", end: "17:00" },
      friday: { start: "09:00", end: "13:00" }
    }
  })
}

// Appointments
const patients = db.patients.find({}, {_id: 1, patientId: 1}).toArray()
const doctors = db.doctors.find({}, {_id: 1, doctorId: 1, specialty: 1}).toArray()
const appointmentTypes = ["Consultation", "Follow-up", "Emergency", "Routine Checkup", "Procedure"]

for (let i = 1; i <= 5000; i++) {
  const patient = patients[Math.floor(Math.random() * patients.length)]
  const doctor = doctors[Math.floor(Math.random() * doctors.length)]
  const appointmentDate = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000 + Math.random() * 30 * 24 * 60 * 60 * 1000)
  
  db.appointments.insertOne({
    appointmentId: `APT-${String(i).padStart(8, '0')}`,
    patientId: patient._id,
    doctorId: doctor._id,
    type: appointmentTypes[Math.floor(Math.random() * appointmentTypes.length)],
    scheduledAt: appointmentDate,
    duration: [15, 30, 45, 60][Math.floor(Math.random() * 4)],
    status: appointmentDate < new Date() 
      ? ["completed", "no-show", "cancelled"][Math.floor(Math.random() * 10) < 8 ? 0 : Math.floor(Math.random() * 2) + 1]
      : ["scheduled", "confirmed"][Math.floor(Math.random() * 2)],
    notes: `Appointment notes for ${patient.patientId}`,
    vitals: appointmentDate < new Date() && Math.random() > 0.2 ? {
      bloodPressure: { systolic: 110 + Math.floor(Math.random() * 40), diastolic: 60 + Math.floor(Math.random() * 30) },
      heartRate: 60 + Math.floor(Math.random() * 40),
      temperature: 97 + Math.random() * 3,
      weight: 120 + Math.random() * 100,
      height: 60 + Math.random() * 18
    } : null,
    diagnosis: appointmentDate < new Date() ? ["Routine checkup - healthy", "Upper respiratory infection", "Hypertension monitoring"][Math.floor(Math.random() * 3)] : null,
    prescriptions: appointmentDate < new Date() && Math.random() > 0.5 ? [{
      medication: medications[Math.floor(Math.random() * medications.length)],
      dosage: "500mg",
      frequency: "twice daily",
      duration: "7 days"
    }] : []
  })
}

// Indexes
db.patients.createIndex({ patientId: 1 }, { unique: true })
db.patients.createIndex({ "medicalHistory.conditions": 1 })
db.doctors.createIndex({ doctorId: 1 }, { unique: true })
db.doctors.createIndex({ specialty: 1 })
db.appointments.createIndex({ patientId: 1, scheduledAt: -1 })
db.appointments.createIndex({ doctorId: 1, scheduledAt: -1 })
db.appointments.createIndex({ status: 1, scheduledAt: 1 })
```

### Exercises

#### Exercise 6.1: Patient Medical Summary
**Task:** Generate a complete medical summary for a patient including all appointments, current medications, and health trends.

<details>
<summary>Solution</summary>

```javascript
const patientId = db.patients.findOne()?.patientId

db.patients.aggregate([
  { $match: { patientId: patientId } },
  {
    $lookup: {
      from: "appointments",
      localField: "_id",
      foreignField: "patientId",
      pipeline: [
        { $match: { status: "completed" } },
        { $sort: { scheduledAt: -1 } }
      ],
      as: "appointments"
    }
  },
  {
    $addFields: {
      age: {
        $floor: {
          $divide: [
            { $subtract: [new Date(), "$dateOfBirth"] },
            365.25 * 24 * 60 * 60 * 1000
          ]
        }
      },
      recentVitals: {
        $filter: {
          input: "$appointments",
          cond: { $ne: ["$$this.vitals", null] }
        }
      }
    }
  },
  {
    $addFields: {
      vitalsTrend: {
        bloodPressure: {
          $map: {
            input: { $slice: ["$recentVitals", 5] },
            as: "v",
            in: {
              date: "$$v.scheduledAt",
              systolic: "$$v.vitals.bloodPressure.systolic",
              diastolic: "$$v.vitals.bloodPressure.diastolic"
            }
          }
        },
        avgHeartRate: {
          $avg: {
            $map: {
              input: { $slice: ["$recentVitals", 5] },
              as: "v",
              in: "$$v.vitals.heartRate"
            }
          }
        }
      }
    }
  },
  {
    $project: {
      patientId: 1,
      name: 1,
      age: 1,
      gender: 1,
      bloodType: 1,
      contact: 1,
      insurance: 1,
      currentConditions: "$medicalHistory.conditions",
      allergies: "$medicalHistory.allergies",
      currentMedications: "$medicalHistory.medications",
      surgicalHistory: "$medicalHistory.surgeries",
      totalAppointments: { $size: "$appointments" },
      lastAppointment: { $arrayElemAt: ["$appointments.scheduledAt", 0] },
      recentDiagnoses: {
        $slice: [{
          $filter: {
            input: "$appointments",
            cond: { $ne: ["$$this.diagnosis", null] }
          }
        }, 5]
      },
      vitalsTrend: 1
    }
  }
])
```
</details>

#### Exercise 6.2: Doctor Schedule Optimization
**Task:** Find doctors with appointment gaps and suggest optimal scheduling.

<details>
<summary>Solution</summary>

```javascript
const targetDate = new Date()
targetDate.setHours(0, 0, 0, 0)
const nextDay = new Date(targetDate)
nextDay.setDate(nextDay.getDate() + 1)

db.doctors.aggregate([
  {
    $lookup: {
      from: "appointments",
      let: { docId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$doctorId", "$$docId"] },
            scheduledAt: { $gte: targetDate, $lt: nextDay },
            status: { $in: ["scheduled", "confirmed"] }
          }
        },
        { $sort: { scheduledAt: 1 } },
        {
          $project: {
            appointmentId: 1,
            scheduledAt: 1,
            duration: 1,
            endTime: { $add: ["$scheduledAt", { $multiply: ["$duration", 60000] }] }
          }
        }
      ],
      as: "appointments"
    }
  },
  {
    $addFields: {
      appointmentCount: { $size: "$appointments" },
      workHours: 8,
      totalBookedMinutes: {
        $sum: "$appointments.duration"
      }
    }
  },
  {
    $addFields: {
      utilizationRate: {
        $multiply: [
          { $divide: ["$totalBookedMinutes", { $multiply: ["$workHours", 60] }] },
          100
        ]
      },
      availableSlots: {
        $subtract: [
          { $multiply: ["$workHours", 60] },
          "$totalBookedMinutes"
        ]
      }
    }
  },
  {
    $project: {
      doctorId: 1,
      name: 1,
      specialty: 1,
      date: targetDate,
      appointmentCount: 1,
      totalBookedMinutes: 1,
      availableMinutes: "$availableSlots",
      utilizationRate: { $round: ["$utilizationRate", 1] },
      appointments: {
        $map: {
          input: "$appointments",
          as: "apt",
          in: {
            time: { $dateToString: { format: "%H:%M", date: "$$apt.scheduledAt" } },
            duration: "$$apt.duration"
          }
        }
      },
      recommendation: {
        $switch: {
          branches: [
            { case: { $lt: ["$utilizationRate", 50] }, then: "Low utilization - can accept more appointments" },
            { case: { $lt: ["$utilizationRate", 80] }, then: "Moderate utilization - some slots available" },
            { case: { $lt: ["$utilizationRate", 95] }, then: "High utilization - limited availability" }
          ],
          default: "Fully booked"
        }
      }
    }
  },
  { $sort: { utilizationRate: 1 } }
])
```
</details>

---

## Exercise 7: Real-Time Analytics Dashboard

### Dataset Setup

```javascript
use analytics_practice

// Website events (create time series collection)
db.createCollection("events", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "seconds"
  }
})

// Generate events for the past 7 days
const eventTypes = ["pageview", "click", "scroll", "form_submit", "purchase", "add_to_cart", "search"]
const pages = ["/", "/products", "/about", "/contact", "/cart", "/checkout", "/product/1", "/product/2"]
const devices = ["desktop", "mobile", "tablet"]
const browsers = ["Chrome", "Firefox", "Safari", "Edge"]
const countries = ["US", "UK", "CA", "DE", "FR", "AU", "JP"]

const now = new Date()
const startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)

// Generate 500,000 events
for (let batch = 0; batch < 50; batch++) {
  const events = []
  for (let i = 0; i < 10000; i++) {
    const eventTime = new Date(startTime.getTime() + Math.random() * 7 * 24 * 60 * 60 * 1000)
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    
    events.push({
      timestamp: eventTime,
      metadata: {
        sessionId: `sess_${Math.floor(Math.random() * 50000)}`,
        userId: Math.random() > 0.3 ? `user_${Math.floor(Math.random() * 10000)}` : null,
        device: devices[Math.floor(Math.random() * devices.length)],
        browser: browsers[Math.floor(Math.random() * browsers.length)],
        country: countries[Math.floor(Math.random() * countries.length)]
      },
      eventType: eventType,
      page: pages[Math.floor(Math.random() * pages.length)],
      referrer: Math.random() > 0.5 ? ["google.com", "facebook.com", "twitter.com", "direct"][Math.floor(Math.random() * 4)] : null,
      value: eventType === "purchase" ? Math.round(Math.random() * 500 * 100) / 100 : null,
      duration: eventType === "pageview" ? Math.floor(Math.random() * 300) : null
    })
  }
  db.events.insertMany(events)
  print(`Batch ${batch + 1}/50 inserted`)
}

// Create indexes
db.events.createIndex({ eventType: 1, timestamp: -1 })
```

### Exercises

#### Exercise 7.1: Real-Time Metrics
**Task:** Calculate real-time metrics for the last hour: active users, page views, conversion rate, and revenue.

<details>
<summary>Solution</summary>

```javascript
const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)

db.events.aggregate([
  { $match: { timestamp: { $gte: oneHourAgo } } },
  {
    $facet: {
      activeUsers: [
        { $group: { _id: "$metadata.userId" } },
        { $match: { _id: { $ne: null } } },
        { $count: "count" }
      ],
      activeSessions: [
        { $group: { _id: "$metadata.sessionId" } },
        { $count: "count" }
      ],
      pageViews: [
        { $match: { eventType: "pageview" } },
        { $count: "count" }
      ],
      purchases: [
        { $match: { eventType: "purchase" } },
        {
          $group: {
            _id: null,
            count: { $sum: 1 },
            revenue: { $sum: "$value" }
          }
        }
      ],
      addToCarts: [
        { $match: { eventType: "add_to_cart" } },
        { $count: "count" }
      ],
      byDevice: [
        {
          $group: {
            _id: "$metadata.device",
            sessions: { $addToSet: "$metadata.sessionId" }
          }
        },
        {
          $project: {
            device: "$_id",
            sessionCount: { $size: "$sessions" }
          }
        }
      ],
      topPages: [
        { $match: { eventType: "pageview" } },
        { $group: { _id: "$page", views: { $sum: 1 } } },
        { $sort: { views: -1 } },
        { $limit: 5 }
      ]
    }
  },
  {
    $project: {
      activeUsers: { $ifNull: [{ $arrayElemAt: ["$activeUsers.count", 0] }, 0] },
      activeSessions: { $ifNull: [{ $arrayElemAt: ["$activeSessions.count", 0] }, 0] },
      pageViews: { $ifNull: [{ $arrayElemAt: ["$pageViews.count", 0] }, 0] },
      purchases: { $ifNull: [{ $arrayElemAt: ["$purchases.count", 0] }, 0] },
      revenue: { $ifNull: [{ $arrayElemAt: ["$purchases.revenue", 0] }, 0] },
      addToCarts: { $ifNull: [{ $arrayElemAt: ["$addToCarts.count", 0] }, 0] },
      conversionRate: {
        $cond: {
          if: { $gt: [{ $arrayElemAt: ["$addToCarts.count", 0] }, 0] },
          then: {
            $multiply: [
              { $divide: [
                { $ifNull: [{ $arrayElemAt: ["$purchases.count", 0] }, 0] },
                { $arrayElemAt: ["$addToCarts.count", 0] }
              ]},
              100
            ]
          },
          else: 0
        }
      },
      deviceBreakdown: "$byDevice",
      topPages: "$topPages"
    }
  }
])
```
</details>

#### Exercise 7.2: Funnel Analysis
**Task:** Analyze the conversion funnel: homepage → product page → add to cart → checkout → purchase.

<details>
<summary>Solution</summary>

```javascript
const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)

db.events.aggregate([
  { $match: { timestamp: { $gte: oneDayAgo } } },
  { $sort: { "metadata.sessionId": 1, timestamp: 1 } },
  {
    $group: {
      _id: "$metadata.sessionId",
      events: { $push: { type: "$eventType", page: "$page" } }
    }
  },
  {
    $addFields: {
      funnelSteps: {
        visitedHome: {
          $gt: [
            { $size: { $filter: { input: "$events", cond: { $eq: ["$$this.page", "/"] } } } },
            0
          ]
        },
        visitedProduct: {
          $gt: [
            { $size: { $filter: { input: "$events", cond: { $regexMatch: { input: "$$this.page", regex: /^\/product/ } } } } },
            0
          ]
        },
        addedToCart: {
          $gt: [
            { $size: { $filter: { input: "$events", cond: { $eq: ["$$this.type", "add_to_cart"] } } } },
            0
          ]
        },
        visitedCheckout: {
          $gt: [
            { $size: { $filter: { input: "$events", cond: { $eq: ["$$this.page", "/checkout"] } } } },
            0
          ]
        },
        purchased: {
          $gt: [
            { $size: { $filter: { input: "$events", cond: { $eq: ["$$this.type", "purchase"] } } } },
            0
          ]
        }
      }
    }
  },
  {
    $group: {
      _id: null,
      totalSessions: { $sum: 1 },
      step1_home: { $sum: { $cond: ["$funnelSteps.visitedHome", 1, 0] } },
      step2_product: { $sum: { $cond: ["$funnelSteps.visitedProduct", 1, 0] } },
      step3_addToCart: { $sum: { $cond: ["$funnelSteps.addedToCart", 1, 0] } },
      step4_checkout: { $sum: { $cond: ["$funnelSteps.visitedCheckout", 1, 0] } },
      step5_purchase: { $sum: { $cond: ["$funnelSteps.purchased", 1, 0] } }
    }
  },
  {
    $project: {
      _id: 0,
      funnel: [
        { step: "Homepage", sessions: "$step1_home", rate: { $multiply: [{ $divide: ["$step1_home", "$totalSessions"] }, 100] } },
        { step: "Product Page", sessions: "$step2_product", rate: { $multiply: [{ $divide: ["$step2_product", "$totalSessions"] }, 100] } },
        { step: "Add to Cart", sessions: "$step3_addToCart", rate: { $multiply: [{ $divide: ["$step3_addToCart", "$totalSessions"] }, 100] } },
        { step: "Checkout", sessions: "$step4_checkout", rate: { $multiply: [{ $divide: ["$step4_checkout", "$totalSessions"] }, 100] } },
        { step: "Purchase", sessions: "$step5_purchase", rate: { $multiply: [{ $divide: ["$step5_purchase", "$totalSessions"] }, 100] } }
      ],
      overallConversion: {
        $multiply: [
          { $divide: ["$step5_purchase", "$step1_home"] },
          100
        ]
      }
    }
  }
])
```
</details>

---

## Exercise 8: Content Management System

### Dataset Setup

```javascript
use cms_practice

// Authors
for (let i = 1; i <= 50; i++) {
  db.authors.insertOne({
    authorId: `AUTH-${String(i).padStart(4, '0')}`,
    name: `Author ${i}`,
    email: `author${i}@cms.com`,
    bio: `Bio for author ${i}. Experienced writer specializing in technology and lifestyle.`,
    avatar: `https://avatars.example.com/author${i}.jpg`,
    role: ["editor", "writer", "admin"][Math.floor(Math.random() * 3)],
    createdAt: new Date(Date.now() - Math.random() * 730 * 24 * 60 * 60 * 1000)
  })
}

// Categories
const categories = [
  { name: "Technology", slug: "technology", description: "Tech news and reviews" },
  { name: "Lifestyle", slug: "lifestyle", description: "Living well" },
  { name: "Business", slug: "business", description: "Business and finance" },
  { name: "Health", slug: "health", description: "Health and wellness" },
  { name: "Travel", slug: "travel", description: "Travel guides and tips" }
]
db.categories.insertMany(categories)

// Articles with full content blocks
const authors = db.authors.find({}, {_id: 1}).toArray()
const categoryDocs = db.categories.find({}, {_id: 1, slug: 1}).toArray()
const statuses = ["draft", "review", "published", "archived"]
const tags = ["featured", "trending", "editor-pick", "breaking", "exclusive"]

for (let i = 1; i <= 1000; i++) {
  const author = authors[Math.floor(Math.random() * authors.length)]
  const category = categoryDocs[Math.floor(Math.random() * categoryDocs.length)]
  const status = statuses[Math.floor(Math.random() * 10) < 7 ? 2 : Math.floor(Math.random() * 4)]
  const createdAt = new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000)
  
  db.articles.insertOne({
    title: `Article ${i}: ${["The Future of", "Understanding", "A Guide to", "Exploring"][Math.floor(Math.random() * 4)]} ${category.slug}`,
    slug: `article-${i}-${category.slug}`,
    authorId: author._id,
    categoryId: category._id,
    content: {
      blocks: [
        { type: "paragraph", text: `Introduction paragraph for article ${i}. This is an engaging opening.` },
        { type: "heading", level: 2, text: "Main Section" },
        { type: "paragraph", text: "Detailed content explaining the main topic." },
        { type: "image", url: `https://images.example.com/${i}.jpg`, caption: "Illustration" },
        { type: "paragraph", text: "Conclusion and summary of key points." }
      ]
    },
    excerpt: `Excerpt for article ${i}. A brief summary of the content.`,
    featuredImage: `https://images.example.com/featured${i}.jpg`,
    tags: tags.filter(() => Math.random() > 0.7),
    status: status,
    seo: {
      metaTitle: `Article ${i} | CMS`,
      metaDescription: `Read about ${category.slug} in this comprehensive article.`,
      keywords: [category.slug, "article", "guide"]
    },
    stats: {
      views: Math.floor(Math.random() * 50000),
      likes: Math.floor(Math.random() * 1000),
      shares: Math.floor(Math.random() * 500),
      comments: Math.floor(Math.random() * 100)
    },
    publishedAt: status === "published" ? new Date(createdAt.getTime() + Math.random() * 7 * 24 * 60 * 60 * 1000) : null,
    createdAt: createdAt,
    updatedAt: new Date(createdAt.getTime() + Math.random() * 30 * 24 * 60 * 60 * 1000)
  })
}

// Comments
const articleIds = db.articles.find({ status: "published" }, {_id: 1}).toArray()

for (let i = 1; i <= 10000; i++) {
  const article = articleIds[Math.floor(Math.random() * articleIds.length)]
  
  db.comments.insertOne({
    articleId: article._id,
    userId: `user_${Math.floor(Math.random() * 5000) + 1}`,
    userName: `User ${Math.floor(Math.random() * 5000) + 1}`,
    content: `This is comment ${i}. ${["Great article!", "Very informative.", "I disagree.", "Thanks for sharing.", "Interesting perspective."][Math.floor(Math.random() * 5)]}`,
    status: ["approved", "pending", "spam"][Math.floor(Math.random() * 10) < 9 ? 0 : Math.floor(Math.random() * 2) + 1],
    likes: Math.floor(Math.random() * 50),
    replies: [],
    createdAt: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000)
  })
}

// Indexes
db.articles.createIndex({ slug: 1 }, { unique: true })
db.articles.createIndex({ status: 1, publishedAt: -1 })
db.articles.createIndex({ categoryId: 1, status: 1 })
db.articles.createIndex({ tags: 1, status: 1 })
db.articles.createIndex({ title: "text", "content.blocks.text": "text" })
db.comments.createIndex({ articleId: 1, status: 1, createdAt: -1 })
```

### Exercises

#### Exercise 8.1: Editorial Dashboard
**Task:** Create an editorial dashboard showing: articles by status, top performing content, author productivity.

<details>
<summary>Solution</summary>

```javascript
db.articles.aggregate([
  {
    $facet: {
      byStatus: [
        { $group: { _id: "$status", count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ],
      topPerforming: [
        { $match: { status: "published" } },
        {
          $addFields: {
            engagementScore: {
              $add: [
                "$stats.views",
                { $multiply: ["$stats.likes", 10] },
                { $multiply: ["$stats.shares", 20] },
                { $multiply: ["$stats.comments", 5] }
              ]
            }
          }
        },
        { $sort: { engagementScore: -1 } },
        { $limit: 10 },
        {
          $lookup: {
            from: "categories",
            localField: "categoryId",
            foreignField: "_id",
            as: "category"
          }
        },
        { $unwind: "$category" },
        {
          $project: {
            title: 1,
            category: "$category.name",
            stats: 1,
            engagementScore: 1,
            publishedAt: 1
          }
        }
      ],
      authorProductivity: [
        { $match: { createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) } } },
        {
          $group: {
            _id: "$authorId",
            articlesWritten: { $sum: 1 },
            published: { $sum: { $cond: [{ $eq: ["$status", "published"] }, 1, 0] } },
            totalViews: { $sum: "$stats.views" }
          }
        },
        {
          $lookup: {
            from: "authors",
            localField: "_id",
            foreignField: "_id",
            as: "author"
          }
        },
        { $unwind: "$author" },
        {
          $project: {
            authorName: "$author.name",
            articlesWritten: 1,
            published: 1,
            totalViews: 1,
            publishRate: {
              $multiply: [
                { $divide: ["$published", "$articlesWritten"] },
                100
              ]
            }
          }
        },
        { $sort: { articlesWritten: -1 } },
        { $limit: 10 }
      ],
      categoryPerformance: [
        { $match: { status: "published" } },
        {
          $group: {
            _id: "$categoryId",
            articleCount: { $sum: 1 },
            totalViews: { $sum: "$stats.views" },
            avgViews: { $avg: "$stats.views" }
          }
        },
        {
          $lookup: {
            from: "categories",
            localField: "_id",
            foreignField: "_id",
            as: "category"
          }
        },
        { $unwind: "$category" },
        {
          $project: {
            category: "$category.name",
            articleCount: 1,
            totalViews: 1,
            avgViews: { $round: ["$avgViews", 0] }
          }
        },
        { $sort: { totalViews: -1 } }
      ]
    }
  }
])
```
</details>

---

## Capstone Project

### Multi-Tenant SaaS Analytics Platform

Build a complete analytics platform that combines concepts from all exercises:

**Requirements:**
1. Multi-tenant data isolation
2. Real-time event tracking
3. User behavior analysis
4. Custom dashboards per tenant
5. Alerting system

**Dataset:**
```javascript
use saas_analytics

// Tenants
db.tenants.insertMany([
  {
    tenantId: "tenant_001",
    name: "Acme Corp",
    plan: "enterprise",
    settings: { dataRetention: 365, maxUsers: 1000 },
    createdAt: new Date()
  },
  {
    tenantId: "tenant_002", 
    name: "Startup Inc",
    plan: "starter",
    settings: { dataRetention: 30, maxUsers: 10 },
    createdAt: new Date()
  }
])

// Generate tenant-specific data
// ... implement data generation for events, users, dashboards
```

**Capstone Tasks:**
1. Design the complete schema with proper indexing
2. Implement tenant data isolation
3. Create real-time aggregation pipelines
4. Build a recommendation system using aggregation
5. Implement change streams for live updates
6. Create materialized views for dashboard performance

---

## Additional Resources

### Online Practice Platforms

| Platform | Description | Link |
|----------|-------------|------|
| MongoDB University | Free courses with labs | https://learn.mongodb.com |
| HackerRank | MongoDB challenges | https://www.hackerrank.com/domains/databases |
| LeetCode | Database problems | https://leetcode.com/problemset/database/ |
| W3Schools | Interactive tutorials | https://www.w3schools.com/mongodb/ |

### Books and Documentation

- [MongoDB: The Definitive Guide](https://www.oreilly.com/library/view/mongodb-the-definitive/9781491954454/)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [MongoDB Aggregation Framework](https://www.mongodb.com/docs/manual/aggregation/)

### Community Resources

- [MongoDB Community Forums](https://www.mongodb.com/community/forums/)
- [Stack Overflow MongoDB Tag](https://stackoverflow.com/questions/tagged/mongodb)
- [MongoDB Blog](https://www.mongodb.com/blog)

---

[Back to Index →](README.md)
