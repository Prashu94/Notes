# Chapter 35: Project - Recommendation Engine

## Project Overview

Build a comprehensive recommendation engine using Neo4j that demonstrates:
- Collaborative filtering
- Content-based filtering
- Hybrid recommendations
- Real-time personalization
- A/B testing support

---

## 35.1 Data Model

### E-commerce Schema

```
(:User {
    id: UUID,
    email: STRING,
    name: STRING,
    joinedAt: DATETIME,
    preferences: MAP
})

(:Product {
    id: UUID,
    sku: STRING,
    name: STRING,
    description: STRING,
    price: FLOAT,
    rating: FLOAT,
    reviewCount: INT,
    embedding: LIST<FLOAT>
})

(:Category {
    id: UUID,
    name: STRING,
    slug: STRING
})

(:Brand {
    name: STRING
})

(:Order {
    id: UUID,
    total: FLOAT,
    createdAt: DATETIME
})

(:Session {
    id: UUID,
    startedAt: DATETIME,
    deviceType: STRING
})

Relationships:
(User)-[:PURCHASED {quantity, price, date}]->(Product)
(User)-[:VIEWED {timestamp, duration}]->(Product)
(User)-[:RATED {rating, date}]->(Product)
(User)-[:ADDED_TO_CART {timestamp}]->(Product)
(User)-[:WISHLISTED {date}]->(Product)
(Product)-[:IN_CATEGORY]->(Category)
(Product)-[:MADE_BY]->(Brand)
(Category)-[:SUBCATEGORY_OF]->(Category)
(User)-[:PLACED]->(Order)
(Order)-[:CONTAINS {quantity, price}]->(Product)
(User)-[:HAS_SESSION]->(Session)
(Session)-[:VIEWED {timestamp}]->(Product)
```

### Setup

```cypher
// Constraints
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT product_sku IF NOT EXISTS FOR (p:Product) REQUIRE p.sku IS UNIQUE;
CREATE CONSTRAINT category_slug IF NOT EXISTS FOR (c:Category) REQUIRE c.slug IS UNIQUE;

// Indexes
CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name);
CREATE INDEX product_price IF NOT EXISTS FOR (p:Product) ON (p.price);

// Vector index for content-based
CREATE VECTOR INDEX product_embeddings IF NOT EXISTS
FOR (p:Product) ON p.embedding
OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}

// Full-text search
CREATE FULLTEXT INDEX product_search IF NOT EXISTS 
FOR (p:Product) ON EACH [p.name, p.description];
```

---

## 35.2 Collaborative Filtering

### User-Based Collaborative Filtering

```python
# recommendations/collaborative.py
from typing import List, Dict

class CollaborativeRecommender:
    def __init__(self, db):
        self.db = db
    
    def get_similar_users(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Find users with similar purchase/rating patterns."""
        def _find_similar(tx, user_id, limit):
            result = tx.run("""
                MATCH (target:User {id: $userId})-[r1:PURCHASED|RATED]->(product)<-[r2:PURCHASED|RATED]-(similar:User)
                WHERE target <> similar
                
                WITH target, similar, 
                     count(DISTINCT product) AS commonProducts,
                     collect({
                         product: product.id,
                         targetRating: CASE WHEN r1:RATED THEN r1.rating ELSE null END,
                         similarRating: CASE WHEN r2:RATED THEN r2.rating ELSE null END
                     }) AS interactions
                
                // Calculate similarity score
                WITH similar, commonProducts, interactions,
                     [i IN interactions WHERE i.targetRating IS NOT NULL AND i.similarRating IS NOT NULL | i] AS ratedBoth
                
                WITH similar, commonProducts,
                     CASE 
                         WHEN size(ratedBoth) > 0 
                         THEN reduce(s = 0.0, i IN ratedBoth | 
                              s + (5 - abs(i.targetRating - i.similarRating))) / (5.0 * size(ratedBoth))
                         ELSE 0.5 
                     END AS ratingSimilarity,
                     commonProducts * 1.0 / 20 AS overlapScore
                
                WITH similar, 
                     overlapScore * 0.4 + ratingSimilarity * 0.6 AS similarityScore,
                     commonProducts
                
                RETURN similar {
                    .id, .name,
                    similarity: similarityScore,
                    commonProducts: commonProducts
                } AS similarUser
                ORDER BY similarityScore DESC
                LIMIT $limit
            """, userId=user_id, limit=limit)
            return [record["similarUser"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_find_similar, user_id, limit)
    
    def recommend_from_similar_users(self, user_id: str, 
                                      limit: int = 20) -> List[Dict]:
        """Recommend products that similar users liked."""
        def _recommend(tx, user_id, limit):
            result = tx.run("""
                // Find similar users (top 50)
                MATCH (target:User {id: $userId})-[:PURCHASED|RATED]->(common)<-[:PURCHASED|RATED]-(similar:User)
                WHERE target <> similar
                WITH target, similar, count(common) AS overlap
                ORDER BY overlap DESC
                LIMIT 50
                
                // Get products they bought/rated highly
                MATCH (similar)-[r:PURCHASED|RATED]->(rec:Product)
                WHERE NOT (target)-[:PURCHASED]->(rec)
                  AND (r:PURCHASED OR r.rating >= 4)
                
                // Weight by user similarity and product rating
                WITH rec, similar, overlap,
                     CASE WHEN r:RATED THEN r.rating ELSE 4.0 END AS rating
                
                // Aggregate recommendations
                WITH rec, 
                     sum(overlap * rating) AS score,
                     count(DISTINCT similar) AS recommenderCount,
                     avg(rating) AS avgRating
                
                // Get product details
                OPTIONAL MATCH (rec)-[:IN_CATEGORY]->(cat:Category)
                OPTIONAL MATCH (rec)-[:MADE_BY]->(brand:Brand)
                
                RETURN rec {
                    .id, .sku, .name, .price, .rating,
                    category: cat.name,
                    brand: brand.name,
                    recommendationScore: score,
                    recommenderCount: recommenderCount,
                    avgRatingFromSimilar: avgRating
                } AS recommendation
                ORDER BY score DESC
                LIMIT $limit
            """, userId=user_id, limit=limit)
            return [record["recommendation"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_recommend, user_id, limit)
```

### Item-Based Collaborative Filtering

```python
def get_similar_products(self, product_id: str, limit: int = 10) -> List[Dict]:
    """Find products frequently bought together."""
    def _find_similar(tx, product_id, limit):
        result = tx.run("""
            MATCH (p:Product {id: $productId})<-[:PURCHASED]-(u:User)-[:PURCHASED]->(similar:Product)
            WHERE p <> similar
            
            WITH similar, count(DISTINCT u) AS coPurchases
            
            // Get total purchases for normalization
            MATCH (p:Product {id: $productId})<-[:PURCHASED]-(buyer1)
            WITH similar, coPurchases, count(buyer1) AS productPurchases
            
            MATCH (similar)<-[:PURCHASED]-(buyer2)
            WITH similar, coPurchases, productPurchases, count(buyer2) AS similarPurchases
            
            // Calculate Jaccard similarity
            WITH similar, coPurchases,
                 toFloat(coPurchases) / (productPurchases + similarPurchases - coPurchases) AS jaccard
            
            OPTIONAL MATCH (similar)-[:IN_CATEGORY]->(cat:Category)
            OPTIONAL MATCH (similar)-[:MADE_BY]->(brand:Brand)
            
            RETURN similar {
                .id, .sku, .name, .price, .rating,
                category: cat.name,
                brand: brand.name,
                similarity: jaccard,
                coPurchases: coPurchases
            } AS product
            ORDER BY jaccard DESC
            LIMIT $limit
        """, productId=product_id, limit=limit)
        return [record["product"] for record in result]
    
    with self.db.session() as session:
        return session.execute_read(_find_similar, product_id, limit)

def get_frequently_bought_together(self, product_ids: List[str], 
                                    limit: int = 5) -> List[Dict]:
    """Get products frequently bought with the given products."""
    def _get_fbt(tx, product_ids, limit):
        result = tx.run("""
            MATCH (p:Product)<-[:CONTAINS]-(o:Order)-[:CONTAINS]->(fbt:Product)
            WHERE p.id IN $productIds AND NOT fbt.id IN $productIds
            
            WITH fbt, count(DISTINCT o) AS frequency
            
            OPTIONAL MATCH (fbt)-[:IN_CATEGORY]->(cat:Category)
            
            RETURN fbt {
                .id, .sku, .name, .price, .rating,
                category: cat.name,
                frequency: frequency
            } AS product
            ORDER BY frequency DESC
            LIMIT $limit
        """, productIds=product_ids, limit=limit)
        return [record["product"] for record in result]
    
    with self.db.session() as session:
        return session.execute_read(_get_fbt, product_ids, limit)
```

---

## 35.3 Content-Based Filtering

```python
# recommendations/content_based.py
from typing import List, Dict

class ContentBasedRecommender:
    def __init__(self, db, embedding_service):
        self.db = db
        self.embedding_service = embedding_service
    
    def recommend_similar_products(self, product_id: str, 
                                    limit: int = 10) -> List[Dict]:
        """Find products with similar content/attributes."""
        def _recommend(tx, product_id, limit):
            result = tx.run("""
                MATCH (source:Product {id: $productId})
                
                // Vector similarity search
                CALL db.index.vector.queryNodes('product_embeddings', $limit + 1, source.embedding)
                YIELD node AS similar, score
                WHERE similar <> source
                
                OPTIONAL MATCH (similar)-[:IN_CATEGORY]->(cat:Category)
                OPTIONAL MATCH (similar)-[:MADE_BY]->(brand:Brand)
                
                RETURN similar {
                    .id, .sku, .name, .price, .rating, .description,
                    category: cat.name,
                    brand: brand.name,
                    similarity: score
                } AS product
                LIMIT $limit
            """, productId=product_id, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_recommend, product_id, limit)
    
    def recommend_by_text_query(self, query: str, limit: int = 20) -> List[Dict]:
        """Semantic search for products."""
        # Generate embedding for query
        query_embedding = self.embedding_service.embed(query)
        
        def _search(tx, embedding, limit):
            result = tx.run("""
                CALL db.index.vector.queryNodes('product_embeddings', $limit, $embedding)
                YIELD node AS product, score
                
                OPTIONAL MATCH (product)-[:IN_CATEGORY]->(cat:Category)
                OPTIONAL MATCH (product)-[:MADE_BY]->(brand:Brand)
                
                RETURN product {
                    .id, .sku, .name, .price, .rating,
                    category: cat.name,
                    brand: brand.name,
                    relevance: score
                } AS product
            """, embedding=embedding, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_search, query_embedding, limit)
    
    def recommend_by_category_preference(self, user_id: str, 
                                          limit: int = 20) -> List[Dict]:
        """Recommend based on user's category preferences."""
        def _recommend(tx, user_id, limit):
            result = tx.run("""
                // Analyze user's category preferences
                MATCH (u:User {id: $userId})-[r:PURCHASED|RATED]->(p:Product)-[:IN_CATEGORY]->(cat:Category)
                WITH cat, 
                     count(*) AS interactions,
                     avg(CASE WHEN r:RATED THEN r.rating ELSE 4.0 END) AS avgRating
                ORDER BY interactions DESC, avgRating DESC
                LIMIT 5
                
                // Find top products in preferred categories
                WITH collect(cat) AS preferredCategories
                MATCH (rec:Product)-[:IN_CATEGORY]->(c:Category)
                WHERE c IN preferredCategories
                  AND NOT (:User {id: $userId})-[:PURCHASED]->(rec)
                
                OPTIONAL MATCH (rec)-[:MADE_BY]->(brand:Brand)
                
                RETURN rec {
                    .id, .sku, .name, .price, .rating, .reviewCount,
                    category: c.name,
                    brand: brand.name
                } AS product
                ORDER BY rec.rating DESC, rec.reviewCount DESC
                LIMIT $limit
            """, userId=user_id, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_recommend, user_id, limit)
```

---

## 35.4 Hybrid Recommendations

```python
# recommendations/hybrid.py
from typing import List, Dict
from collections import defaultdict

class HybridRecommender:
    def __init__(self, db, collaborative, content_based):
        self.db = db
        self.collaborative = collaborative
        self.content_based = content_based
    
    def get_personalized_recommendations(self, user_id: str,
                                          limit: int = 20,
                                          weights: Dict = None) -> List[Dict]:
        """Combine multiple recommendation strategies."""
        weights = weights or {
            'collaborative': 0.4,
            'content': 0.3,
            'trending': 0.2,
            'new': 0.1
        }
        
        # Gather recommendations from each source
        collab_recs = self.collaborative.recommend_from_similar_users(user_id, limit * 2)
        content_recs = self.content_based.recommend_by_category_preference(user_id, limit * 2)
        trending_recs = self._get_trending_products(limit * 2)
        new_recs = self._get_new_arrivals(user_id, limit * 2)
        
        # Score and combine
        scores = defaultdict(lambda: {'score': 0, 'sources': [], 'product': None})
        
        for rec in collab_recs:
            pid = rec['id']
            scores[pid]['score'] += rec.get('recommendationScore', 1) * weights['collaborative']
            scores[pid]['sources'].append('collaborative')
            scores[pid]['product'] = rec
        
        for rec in content_recs:
            pid = rec['id']
            scores[pid]['score'] += rec.get('rating', 3) / 5 * weights['content']
            scores[pid]['sources'].append('content')
            if not scores[pid]['product']:
                scores[pid]['product'] = rec
        
        for rec in trending_recs:
            pid = rec['id']
            scores[pid]['score'] += rec.get('trendScore', 1) * weights['trending']
            scores[pid]['sources'].append('trending')
            if not scores[pid]['product']:
                scores[pid]['product'] = rec
        
        for rec in new_recs:
            pid = rec['id']
            scores[pid]['score'] += weights['new']
            scores[pid]['sources'].append('new')
            if not scores[pid]['product']:
                scores[pid]['product'] = rec
        
        # Sort and return
        sorted_recs = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        return [
            {
                **item['product'],
                'hybridScore': item['score'],
                'sources': item['sources']
            }
            for pid, item in sorted_recs[:limit]
        ]
    
    def _get_trending_products(self, limit: int) -> List[Dict]:
        """Get trending products based on recent activity."""
        def _get_trending(tx, limit):
            result = tx.run("""
                // Recent purchases and views
                MATCH (p:Product)<-[r:PURCHASED|VIEWED]-()
                WHERE r.date > datetime() - duration({days: 7})
                   OR r.timestamp > datetime() - duration({days: 7})
                
                WITH p, 
                     sum(CASE WHEN r:PURCHASED THEN 3 ELSE 1 END) AS activityScore
                
                OPTIONAL MATCH (p)-[:IN_CATEGORY]->(cat:Category)
                
                RETURN p {
                    .id, .sku, .name, .price, .rating,
                    category: cat.name,
                    trendScore: activityScore
                } AS product
                ORDER BY activityScore DESC
                LIMIT $limit
            """, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_trending, limit)
    
    def _get_new_arrivals(self, user_id: str, limit: int) -> List[Dict]:
        """Get new products user hasn't seen."""
        def _get_new(tx, user_id, limit):
            result = tx.run("""
                MATCH (p:Product)
                WHERE p.createdAt > datetime() - duration({days: 30})
                  AND NOT (:User {id: $userId})-[:VIEWED|PURCHASED]->(p)
                
                OPTIONAL MATCH (p)-[:IN_CATEGORY]->(cat:Category)
                
                RETURN p {
                    .id, .sku, .name, .price, .rating,
                    category: cat.name,
                    isNew: true
                } AS product
                ORDER BY p.createdAt DESC
                LIMIT $limit
            """, userId=user_id, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_new, user_id, limit)
```

---

## 35.5 Real-Time Personalization

```python
# recommendations/realtime.py
from typing import List, Dict
from datetime import datetime

class RealtimeRecommender:
    def __init__(self, db):
        self.db = db
    
    def get_session_based_recommendations(self, session_id: str,
                                           limit: int = 10) -> List[Dict]:
        """Recommend based on current session activity."""
        def _recommend(tx, session_id, limit):
            result = tx.run("""
                // Get products viewed in this session
                MATCH (s:Session {id: $sessionId})-[v:VIEWED]->(viewed:Product)
                WITH viewed ORDER BY v.timestamp DESC LIMIT 5
                
                // Find similar products to recently viewed
                MATCH (viewed)<-[:PURCHASED]-(:User)-[:PURCHASED]->(similar:Product)
                WHERE similar <> viewed
                  AND NOT (s)-[:VIEWED]->(similar)
                
                WITH similar, count(*) AS relevance
                
                OPTIONAL MATCH (similar)-[:IN_CATEGORY]->(cat:Category)
                
                RETURN similar {
                    .id, .sku, .name, .price, .rating,
                    category: cat.name,
                    relevance: relevance,
                    reason: 'session_based'
                } AS product
                ORDER BY relevance DESC
                LIMIT $limit
            """, sessionId=session_id, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_recommend, session_id, limit)
    
    def get_cart_recommendations(self, user_id: str, 
                                  cart_product_ids: List[str],
                                  limit: int = 5) -> List[Dict]:
        """Recommend products to add to cart."""
        def _recommend(tx, user_id, cart_ids, limit):
            result = tx.run("""
                // Products in cart
                MATCH (cart:Product) WHERE cart.id IN $cartIds
                
                // Find complementary products
                MATCH (cart)<-[:CONTAINS]-(o:Order)-[:CONTAINS]->(complement:Product)
                WHERE NOT complement.id IN $cartIds
                
                WITH complement, count(DISTINCT o) AS frequency
                
                // Exclude already purchased by user
                OPTIONAL MATCH (u:User {id: $userId})-[:PURCHASED]->(complement)
                WITH complement, frequency WHERE u IS NULL
                
                OPTIONAL MATCH (complement)-[:IN_CATEGORY]->(cat:Category)
                
                RETURN complement {
                    .id, .sku, .name, .price, .rating,
                    category: cat.name,
                    frequency: frequency,
                    reason: 'frequently_bought_together'
                } AS product
                ORDER BY frequency DESC
                LIMIT $limit
            """, userId=user_id, cartIds=cart_product_ids, limit=limit)
            return [record["product"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_recommend, user_id, cart_product_ids, limit)
    
    def track_view(self, user_id: str, session_id: str, 
                   product_id: str, duration: float = None):
        """Track product view for future recommendations."""
        def _track(tx, user_id, session_id, product_id, duration):
            tx.run("""
                MATCH (u:User {id: $userId})
                MATCH (p:Product {id: $productId})
                
                // User-level view tracking
                MERGE (u)-[v:VIEWED]->(p)
                ON CREATE SET v.firstViewed = datetime(), v.viewCount = 1
                ON MATCH SET v.lastViewed = datetime(), v.viewCount = v.viewCount + 1
                SET v.totalDuration = COALESCE(v.totalDuration, 0) + COALESCE($duration, 0)
                
                // Session-level view tracking
                WITH u, p
                MATCH (s:Session {id: $sessionId})
                MERGE (s)-[sv:VIEWED]->(p)
                ON CREATE SET sv.timestamp = datetime()
                SET sv.duration = COALESCE($duration, 0)
            """, userId=user_id, sessionId=session_id, 
                productId=product_id, duration=duration)
        
        with self.db.session() as session:
            session.execute_write(_track, user_id, session_id, product_id, duration)
```

---

## 35.6 Recommendation API

```python
# recommendations/api.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from .schemas import ProductRecommendation, RecommendationType
from .hybrid import HybridRecommender
from .realtime import RealtimeRecommender

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/personalized", response_model=List[ProductRecommendation])
async def get_personalized(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    recommender: HybridRecommender = Depends(get_hybrid_recommender)
):
    """Get personalized recommendations for user."""
    return recommender.get_personalized_recommendations(user_id, limit)

@router.get("/similar/{product_id}", response_model=List[ProductRecommendation])
async def get_similar_products(
    product_id: str,
    limit: int = Query(10, ge=1, le=50),
    recommender: ContentBasedRecommender = Depends(get_content_recommender)
):
    """Get products similar to a given product."""
    return recommender.recommend_similar_products(product_id, limit)

@router.get("/frequently-bought-together", response_model=List[ProductRecommendation])
async def get_fbt(
    product_ids: List[str] = Query(...),
    limit: int = Query(5, ge=1, le=20),
    recommender: CollaborativeRecommender = Depends(get_collab_recommender)
):
    """Get products frequently bought together."""
    return recommender.get_frequently_bought_together(product_ids, limit)

@router.get("/session/{session_id}", response_model=List[ProductRecommendation])
async def get_session_recommendations(
    session_id: str,
    limit: int = Query(10, ge=1, le=50),
    recommender: RealtimeRecommender = Depends(get_realtime_recommender)
):
    """Get recommendations based on current session."""
    return recommender.get_session_based_recommendations(session_id, limit)

@router.get("/cart", response_model=List[ProductRecommendation])
async def get_cart_recommendations(
    user_id: str,
    cart_product_ids: List[str] = Query(...),
    limit: int = Query(5, ge=1, le=20),
    recommender: RealtimeRecommender = Depends(get_realtime_recommender)
):
    """Get recommendations to add to cart."""
    return recommender.get_cart_recommendations(user_id, cart_product_ids, limit)

@router.post("/track/view")
async def track_view(
    user_id: str,
    session_id: str,
    product_id: str,
    duration: Optional[float] = None,
    recommender: RealtimeRecommender = Depends(get_realtime_recommender)
):
    """Track product view event."""
    recommender.track_view(user_id, session_id, product_id, duration)
    return {"status": "tracked"}
```

---

## 35.7 Performance Optimization

### Caching Recommendations

```python
from functools import lru_cache
from datetime import datetime, timedelta
import redis

class CachedRecommender:
    def __init__(self, recommender, redis_client):
        self.recommender = recommender
        self.redis = redis_client
        self.ttl = 3600  # 1 hour
    
    def get_recommendations(self, user_id: str, rec_type: str, 
                           limit: int = 20) -> List[Dict]:
        cache_key = f"recs:{user_id}:{rec_type}:{limit}"
        
        # Try cache
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Generate recommendations
        if rec_type == 'personalized':
            recs = self.recommender.get_personalized_recommendations(user_id, limit)
        elif rec_type == 'trending':
            recs = self.recommender._get_trending_products(limit)
        else:
            recs = []
        
        # Cache results
        self.redis.setex(cache_key, self.ttl, json.dumps(recs))
        
        return recs
    
    def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached recommendations for a user."""
        pattern = f"recs:{user_id}:*"
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
```

### Pre-computing Similarity

```cypher
// Pre-compute product similarity and store
CALL gds.graph.project('productGraph', 'Product', 
    {PURCHASED: {type: 'PURCHASED', orientation: 'UNDIRECTED'}})

CALL gds.nodeSimilarity.write('productGraph', {
    writeRelationshipType: 'SIMILAR_TO',
    writeProperty: 'score',
    topK: 10,
    similarityCutoff: 0.1
})
YIELD nodesCompared, relationshipsWritten

// Now queries can use pre-computed similarity
MATCH (p:Product {id: $productId})-[s:SIMILAR_TO]->(similar:Product)
RETURN similar {.id, .name, similarity: s.score}
ORDER BY s.score DESC
LIMIT 10
```

---

## Summary

This recommendation engine demonstrates:

| Strategy | Use Case |
|----------|----------|
| User-based CF | "Users like you also bought" |
| Item-based CF | "Frequently bought together" |
| Content-based | "Similar products" |
| Hybrid | Personalized home page |
| Real-time | Session-based suggestions |

### Best Practices

1. **Combine strategies** for better coverage
2. **Cache aggressively** for performance
3. **Track everything** for continuous improvement
4. **A/B test** recommendation strategies
5. **Handle cold start** with popularity/trending

---

## Exercises

### Exercise 35.1: Add Reviews
1. Include review sentiment in recommendations
2. Weight by review helpfulness
3. Filter products with negative reviews

### Exercise 35.2: Time Decay
1. Weight recent interactions higher
2. Implement seasonal recommendations
3. Handle product lifecycle stages

### Exercise 35.3: Diversity
1. Ensure category diversity in results
2. Avoid recommending same brand repeatedly
3. Include serendipity factor

---

**Next Chapter: [Chapter 36: Project - Knowledge Graph](36-project-knowledge-graph.md)**
