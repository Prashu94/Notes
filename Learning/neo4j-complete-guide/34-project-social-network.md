# Chapter 34: Project - Social Network

## Project Overview

Build a complete social network application using Neo4j that demonstrates:
- User profiles and connections
- Posts and interactions
- Friend recommendations
- Activity feeds
- Graph-based features

---

## 34.1 Data Model

### Schema Design

```
(:User {
    id: UUID,
    username: STRING (unique),
    email: STRING (unique),
    passwordHash: STRING,
    displayName: STRING,
    bio: STRING,
    profilePicture: STRING,
    location: STRING,
    createdAt: DATETIME,
    lastLogin: DATETIME
})

(:Post {
    id: UUID,
    content: STRING,
    mediaUrl: STRING,
    createdAt: DATETIME,
    updatedAt: DATETIME
})

(:Comment {
    id: UUID,
    content: STRING,
    createdAt: DATETIME
})

(:Tag {
    name: STRING (unique)
})

(:Location {
    name: STRING,
    latitude: FLOAT,
    longitude: FLOAT
})

Relationships:
(User)-[:FOLLOWS {since: DATETIME}]->(User)
(User)-[:POSTED {at: DATETIME}]->(Post)
(User)-[:LIKED {at: DATETIME}]->(Post)
(User)-[:COMMENTED {at: DATETIME}]->(Comment)
(Comment)-[:ON]->(Post)
(Post)-[:TAGGED]->(Tag)
(Post)-[:AT]->(Location)
(User)-[:MENTIONED_IN]->(Post)
```

### Create Constraints and Indexes

```cypher
// Unique constraints
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE;
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;

// Indexes for common queries
CREATE INDEX user_username_lookup IF NOT EXISTS FOR (u:User) ON (u.username);
CREATE INDEX post_created IF NOT EXISTS FOR (p:Post) ON (p.createdAt);
CREATE INDEX tag_name_lookup IF NOT EXISTS FOR (t:Tag) ON (t.name);

// Full-text index for search
CREATE FULLTEXT INDEX user_search IF NOT EXISTS 
FOR (u:User) ON EACH [u.username, u.displayName, u.bio];

CREATE FULLTEXT INDEX post_search IF NOT EXISTS 
FOR (p:Post) ON EACH [p.content];
```

---

## 34.2 Core Features Implementation

### User Management

```python
# social_network/repositories/user_repository.py
import uuid
from typing import List, Dict, Optional
from datetime import datetime

class UserRepository:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, username: str, email: str, 
                    password_hash: str, display_name: str = None) -> Dict:
        def _create(tx, user_id, username, email, password_hash, display_name):
            result = tx.run("""
                CREATE (u:User {
                    id: $id,
                    username: $username,
                    email: $email,
                    passwordHash: $passwordHash,
                    displayName: $displayName,
                    createdAt: datetime(),
                    followerCount: 0,
                    followingCount: 0,
                    postCount: 0
                })
                RETURN u {.*, nodeId: elementId(u)} AS user
            """, id=user_id, username=username, email=email,
                passwordHash=password_hash, displayName=display_name or username)
            return result.single()["user"]
        
        user_id = str(uuid.uuid4())
        with self.db.session() as session:
            return session.execute_write(
                _create, user_id, username, email, password_hash, display_name
            )
    
    def get_user_profile(self, username: str, viewer_username: str = None) -> Optional[Dict]:
        def _get(tx, username, viewer_username):
            result = tx.run("""
                MATCH (u:User {username: $username})
                OPTIONAL MATCH (u)-[:POSTED]->(post:Post)
                WITH u, count(post) AS postCount
                OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower:User)
                WITH u, postCount, count(follower) AS followerCount
                OPTIONAL MATCH (u)-[:FOLLOWS]->(following:User)
                WITH u, postCount, followerCount, count(following) AS followingCount
                
                // Check if viewer follows this user
                OPTIONAL MATCH (viewer:User {username: $viewer})-[f:FOLLOWS]->(u)
                
                RETURN u {
                    .*,
                    postCount: postCount,
                    followerCount: followerCount,
                    followingCount: followingCount,
                    isFollowing: f IS NOT NULL
                } AS profile
            """, username=username, viewer=viewer_username)
            record = result.single()
            return record["profile"] if record else None
        
        with self.db.session() as session:
            return session.execute_read(_get, username, viewer_username)
    
    def follow_user(self, follower_username: str, 
                    followed_username: str) -> bool:
        def _follow(tx, follower, followed):
            result = tx.run("""
                MATCH (follower:User {username: $follower})
                MATCH (followed:User {username: $followed})
                WHERE follower <> followed
                MERGE (follower)-[r:FOLLOWS]->(followed)
                ON CREATE SET r.since = datetime()
                WITH follower, followed, r
                SET follower.followingCount = 
                    COALESCE(follower.followingCount, 0) + 
                    CASE WHEN r.since = datetime() THEN 1 ELSE 0 END,
                    followed.followerCount = 
                    COALESCE(followed.followerCount, 0) + 
                    CASE WHEN r.since = datetime() THEN 1 ELSE 0 END
                RETURN true AS success
            """, follower=follower, followed=followed)
            return result.single() is not None
        
        with self.db.session() as session:
            return session.execute_write(_follow, follower_username, followed_username)
    
    def unfollow_user(self, follower_username: str, 
                      followed_username: str) -> bool:
        def _unfollow(tx, follower, followed):
            result = tx.run("""
                MATCH (follower:User {username: $follower})-[r:FOLLOWS]->(followed:User {username: $followed})
                DELETE r
                SET follower.followingCount = follower.followingCount - 1,
                    followed.followerCount = followed.followerCount - 1
                RETURN true AS success
            """, follower=follower, followed=followed)
            return result.single() is not None
        
        with self.db.session() as session:
            return session.execute_write(_unfollow, follower_username, followed_username)
    
    def get_followers(self, username: str, skip: int = 0, 
                      limit: int = 20) -> List[Dict]:
        def _get_followers(tx, username, skip, limit):
            result = tx.run("""
                MATCH (u:User {username: $username})<-[r:FOLLOWS]-(follower:User)
                RETURN follower {
                    .id, .username, .displayName, .profilePicture,
                    followedAt: r.since
                } AS follower
                ORDER BY r.since DESC
                SKIP $skip LIMIT $limit
            """, username=username, skip=skip, limit=limit)
            return [record["follower"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_followers, username, skip, limit)
    
    def get_following(self, username: str, skip: int = 0, 
                      limit: int = 20) -> List[Dict]:
        def _get_following(tx, username, skip, limit):
            result = tx.run("""
                MATCH (u:User {username: $username})-[r:FOLLOWS]->(following:User)
                RETURN following {
                    .id, .username, .displayName, .profilePicture,
                    followedAt: r.since
                } AS following
                ORDER BY r.since DESC
                SKIP $skip LIMIT $limit
            """, username=username, skip=skip, limit=limit)
            return [record["following"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_following, username, skip, limit)
    
    def search_users(self, query: str, limit: int = 20) -> List[Dict]:
        def _search(tx, query, limit):
            result = tx.run("""
                CALL db.index.fulltext.queryNodes('user_search', $query + '*')
                YIELD node, score
                RETURN node {
                    .id, .username, .displayName, .profilePicture, .bio,
                    score: score
                } AS user
                ORDER BY score DESC
                LIMIT $limit
            """, query=query, limit=limit)
            return [record["user"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_search, query, limit)
```

### Post Management

```python
# social_network/repositories/post_repository.py
import uuid
import re
from typing import List, Dict, Optional

class PostRepository:
    def __init__(self, db):
        self.db = db
    
    def create_post(self, author_username: str, content: str, 
                    media_url: str = None) -> Dict:
        def _create(tx, post_id, author, content, media_url):
            # Extract mentions and hashtags
            mentions = re.findall(r'@(\w+)', content)
            hashtags = re.findall(r'#(\w+)', content)
            
            result = tx.run("""
                MATCH (author:User {username: $author})
                CREATE (p:Post {
                    id: $id,
                    content: $content,
                    mediaUrl: $mediaUrl,
                    createdAt: datetime(),
                    likeCount: 0,
                    commentCount: 0,
                    shareCount: 0
                })
                CREATE (author)-[:POSTED {at: datetime()}]->(p)
                
                // Create tags
                WITH author, p
                UNWIND $hashtags AS tagName
                MERGE (t:Tag {name: toLower(tagName)})
                MERGE (p)-[:TAGGED]->(t)
                
                // Link mentioned users
                WITH author, p
                UNWIND $mentions AS mentionedUsername
                MATCH (mentioned:User {username: mentionedUsername})
                MERGE (mentioned)-[:MENTIONED_IN]->(p)
                
                // Update author's post count
                SET author.postCount = COALESCE(author.postCount, 0) + 1
                
                RETURN p {
                    .*,
                    author: author {.username, .displayName, .profilePicture}
                } AS post
            """, id=post_id, author=author, content=content, 
                mediaUrl=media_url, hashtags=hashtags, mentions=mentions)
            return result.single()["post"]
        
        post_id = str(uuid.uuid4())
        with self.db.session() as session:
            return session.execute_write(
                _create, post_id, author_username, content, media_url
            )
    
    def get_post(self, post_id: str, viewer_username: str = None) -> Optional[Dict]:
        def _get(tx, post_id, viewer):
            result = tx.run("""
                MATCH (author:User)-[:POSTED]->(p:Post {id: $postId})
                OPTIONAL MATCH (p)-[:TAGGED]->(tag:Tag)
                OPTIONAL MATCH (viewer:User {username: $viewer})-[liked:LIKED]->(p)
                RETURN p {
                    .*,
                    author: author {.username, .displayName, .profilePicture},
                    tags: collect(DISTINCT tag.name),
                    isLiked: liked IS NOT NULL
                } AS post
            """, postId=post_id, viewer=viewer)
            record = result.single()
            return record["post"] if record else None
        
        with self.db.session() as session:
            return session.execute_read(_get, post_id, viewer_username)
    
    def like_post(self, username: str, post_id: str) -> bool:
        def _like(tx, username, post_id):
            result = tx.run("""
                MATCH (u:User {username: $username})
                MATCH (p:Post {id: $postId})
                MERGE (u)-[r:LIKED]->(p)
                ON CREATE SET r.at = datetime(), p.likeCount = p.likeCount + 1
                RETURN r IS NOT NULL AS success
            """, username=username, postId=post_id)
            return result.single()["success"]
        
        with self.db.session() as session:
            return session.execute_write(_like, username, post_id)
    
    def unlike_post(self, username: str, post_id: str) -> bool:
        def _unlike(tx, username, post_id):
            result = tx.run("""
                MATCH (u:User {username: $username})-[r:LIKED]->(p:Post {id: $postId})
                DELETE r
                SET p.likeCount = p.likeCount - 1
                RETURN true AS success
            """, username=username, postId=post_id)
            return result.single() is not None
        
        with self.db.session() as session:
            return session.execute_write(_unlike, username, post_id)
    
    def add_comment(self, username: str, post_id: str, 
                    content: str) -> Dict:
        def _comment(tx, comment_id, username, post_id, content):
            result = tx.run("""
                MATCH (u:User {username: $username})
                MATCH (p:Post {id: $postId})
                CREATE (c:Comment {
                    id: $commentId,
                    content: $content,
                    createdAt: datetime()
                })
                CREATE (u)-[:COMMENTED {at: datetime()}]->(c)
                CREATE (c)-[:ON]->(p)
                SET p.commentCount = p.commentCount + 1
                RETURN c {
                    .*,
                    author: u {.username, .displayName, .profilePicture}
                } AS comment
            """, commentId=comment_id, username=username, 
                postId=post_id, content=content)
            return result.single()["comment"]
        
        comment_id = str(uuid.uuid4())
        with self.db.session() as session:
            return session.execute_write(
                _comment, comment_id, username, post_id, content
            )
    
    def get_comments(self, post_id: str, skip: int = 0, 
                     limit: int = 20) -> List[Dict]:
        def _get_comments(tx, post_id, skip, limit):
            result = tx.run("""
                MATCH (u:User)-[:COMMENTED]->(c:Comment)-[:ON]->(p:Post {id: $postId})
                RETURN c {
                    .*,
                    author: u {.username, .displayName, .profilePicture}
                } AS comment
                ORDER BY c.createdAt DESC
                SKIP $skip LIMIT $limit
            """, postId=post_id, skip=skip, limit=limit)
            return [record["comment"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_comments, post_id, skip, limit)
```

### Feed Generation

```python
# social_network/repositories/feed_repository.py
from typing import List, Dict

class FeedRepository:
    def __init__(self, db):
        self.db = db
    
    def get_home_feed(self, username: str, skip: int = 0, 
                      limit: int = 20) -> List[Dict]:
        """Get posts from followed users."""
        def _get_feed(tx, username, skip, limit):
            result = tx.run("""
                MATCH (viewer:User {username: $username})-[:FOLLOWS]->(following:User)
                MATCH (following)-[:POSTED]->(p:Post)
                
                OPTIONAL MATCH (p)-[:TAGGED]->(tag:Tag)
                OPTIONAL MATCH (viewer)-[liked:LIKED]->(p)
                
                RETURN p {
                    .*,
                    author: following {.username, .displayName, .profilePicture},
                    tags: collect(DISTINCT tag.name),
                    isLiked: liked IS NOT NULL
                } AS post
                ORDER BY p.createdAt DESC
                SKIP $skip LIMIT $limit
            """, username=username, skip=skip, limit=limit)
            return [record["post"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_feed, username, skip, limit)
    
    def get_explore_feed(self, username: str, skip: int = 0, 
                         limit: int = 20) -> List[Dict]:
        """Get trending and recommended posts."""
        def _get_explore(tx, username, skip, limit):
            result = tx.run("""
                // Get posts from last 7 days, weighted by engagement
                MATCH (author:User)-[:POSTED]->(p:Post)
                WHERE p.createdAt > datetime() - duration({days: 7})
                  AND NOT (:User {username: $username})-[:FOLLOWS]->(author)
                  AND author.username <> $username
                
                // Calculate engagement score
                WITH p, author,
                     p.likeCount * 1.0 + p.commentCount * 2.0 + p.shareCount * 3.0 AS engagementScore,
                     duration.between(p.createdAt, datetime()).hours AS ageHours
                
                // Time decay factor
                WITH p, author, engagementScore / (ageHours + 1) AS score
                
                OPTIONAL MATCH (p)-[:TAGGED]->(tag:Tag)
                OPTIONAL MATCH (viewer:User {username: $username})-[liked:LIKED]->(p)
                
                RETURN p {
                    .*,
                    author: author {.username, .displayName, .profilePicture},
                    tags: collect(DISTINCT tag.name),
                    isLiked: liked IS NOT NULL,
                    score: score
                } AS post
                ORDER BY score DESC
                SKIP $skip LIMIT $limit
            """, username=username, skip=skip, limit=limit)
            return [record["post"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_explore, username, skip, limit)
    
    def get_user_posts(self, username: str, viewer_username: str = None,
                       skip: int = 0, limit: int = 20) -> List[Dict]:
        """Get posts by a specific user."""
        def _get_posts(tx, username, viewer, skip, limit):
            result = tx.run("""
                MATCH (author:User {username: $username})-[:POSTED]->(p:Post)
                OPTIONAL MATCH (p)-[:TAGGED]->(tag:Tag)
                OPTIONAL MATCH (viewer:User {username: $viewer})-[liked:LIKED]->(p)
                
                RETURN p {
                    .*,
                    author: author {.username, .displayName, .profilePicture},
                    tags: collect(DISTINCT tag.name),
                    isLiked: liked IS NOT NULL
                } AS post
                ORDER BY p.createdAt DESC
                SKIP $skip LIMIT $limit
            """, username=username, viewer=viewer, skip=skip, limit=limit)
            return [record["post"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_posts, username, viewer_username, skip, limit)
    
    def get_hashtag_feed(self, tag: str, skip: int = 0, 
                         limit: int = 20) -> List[Dict]:
        """Get posts with a specific hashtag."""
        def _get_by_tag(tx, tag, skip, limit):
            result = tx.run("""
                MATCH (author:User)-[:POSTED]->(p:Post)-[:TAGGED]->(t:Tag {name: $tag})
                OPTIONAL MATCH (p)-[:TAGGED]->(allTags:Tag)
                
                RETURN p {
                    .*,
                    author: author {.username, .displayName, .profilePicture},
                    tags: collect(DISTINCT allTags.name)
                } AS post
                ORDER BY p.createdAt DESC
                SKIP $skip LIMIT $limit
            """, tag=tag.lower(), skip=skip, limit=limit)
            return [record["post"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_by_tag, tag, skip, limit)
```

### Friend Recommendations

```python
# social_network/repositories/recommendation_repository.py
from typing import List, Dict

class RecommendationRepository:
    def __init__(self, db):
        self.db = db
    
    def get_friend_suggestions(self, username: str, 
                                limit: int = 10) -> List[Dict]:
        """Suggest users based on mutual connections."""
        def _get_suggestions(tx, username, limit):
            result = tx.run("""
                MATCH (user:User {username: $username})-[:FOLLOWS]->(friend)-[:FOLLOWS]->(suggestion:User)
                WHERE user <> suggestion 
                  AND NOT (user)-[:FOLLOWS]->(suggestion)
                
                WITH suggestion, count(DISTINCT friend) AS mutualCount,
                     collect(DISTINCT friend.username)[0..3] AS mutualFriends
                
                RETURN suggestion {
                    .id, .username, .displayName, .profilePicture, .bio,
                    mutualCount: mutualCount,
                    mutualFriends: mutualFriends,
                    reason: 'mutual_friends'
                } AS suggestion
                ORDER BY mutualCount DESC
                LIMIT $limit
            """, username=username, limit=limit)
            return [record["suggestion"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_suggestions, username, limit)
    
    def get_similar_interest_users(self, username: str, 
                                    limit: int = 10) -> List[Dict]:
        """Suggest users with similar interests (based on liked posts/tags)."""
        def _get_similar(tx, username, limit):
            result = tx.run("""
                // Find tags the user engages with
                MATCH (user:User {username: $username})-[:LIKED|POSTED]->(:Post)-[:TAGGED]->(tag:Tag)
                WITH user, tag, count(*) AS engagement
                ORDER BY engagement DESC
                LIMIT 10
                
                // Find other users engaging with same tags
                WITH user, collect(tag) AS userTags
                MATCH (suggestion:User)-[:LIKED|POSTED]->(:Post)-[:TAGGED]->(t:Tag)
                WHERE suggestion <> user 
                  AND NOT (user)-[:FOLLOWS]->(suggestion)
                  AND t IN userTags
                
                WITH suggestion, count(DISTINCT t) AS commonTags,
                     collect(DISTINCT t.name)[0..3] AS sharedInterests
                
                RETURN suggestion {
                    .id, .username, .displayName, .profilePicture,
                    commonTags: commonTags,
                    sharedInterests: sharedInterests,
                    reason: 'similar_interests'
                } AS suggestion
                ORDER BY commonTags DESC
                LIMIT $limit
            """, username=username, limit=limit)
            return [record["suggestion"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_similar, username, limit)
    
    def get_trending_topics(self, limit: int = 10) -> List[Dict]:
        """Get trending hashtags."""
        def _get_trending(tx, limit):
            result = tx.run("""
                MATCH (p:Post)-[:TAGGED]->(t:Tag)
                WHERE p.createdAt > datetime() - duration({hours: 24})
                
                WITH t, count(p) AS postCount,
                     sum(p.likeCount) AS totalLikes,
                     sum(p.commentCount) AS totalComments
                
                WITH t, postCount, totalLikes, totalComments,
                     postCount * 1.0 + totalLikes * 0.5 + totalComments * 0.3 AS trendScore
                
                RETURN t {
                    .name,
                    postCount: postCount,
                    trendScore: trendScore
                } AS topic
                ORDER BY trendScore DESC
                LIMIT $limit
            """, limit=limit)
            return [record["topic"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_trending, limit)
```

---

## 34.3 Sample Data Generation

```cypher
// Generate sample users
UNWIND range(1, 100) AS i
CREATE (u:User {
    id: apoc.create.uuid(),
    username: 'user' + i,
    email: 'user' + i + '@example.com',
    displayName: 'User ' + i,
    passwordHash: '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.PfPq3XcYMBXqhS',
    bio: 'This is user ' + i + ' bio',
    createdAt: datetime() - duration({days: randomInteger(1, 365)}),
    followerCount: 0,
    followingCount: 0,
    postCount: 0
})

// Create follow relationships
MATCH (u1:User), (u2:User)
WHERE u1 <> u2 AND rand() < 0.1
MERGE (u1)-[:FOLLOWS {since: datetime() - duration({days: randomInteger(1, 100)})}]->(u2)

// Update follower counts
MATCH (u:User)
OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower)
WITH u, count(follower) AS followers
OPTIONAL MATCH (u)-[:FOLLOWS]->(following)
WITH u, followers, count(following) AS followingCount
SET u.followerCount = followers, u.followingCount = followingCount

// Create sample posts
MATCH (u:User)
UNWIND range(1, randomInteger(1, 10)) AS i
CREATE (p:Post {
    id: apoc.create.uuid(),
    content: 'This is post ' + i + ' by ' + u.username + ' #test #sample',
    createdAt: datetime() - duration({days: randomInteger(1, 30)}),
    likeCount: 0,
    commentCount: 0,
    shareCount: 0
})
CREATE (u)-[:POSTED]->(p)

// Create tags
MATCH (p:Post)
WITH p, split(p.content, '#') AS parts
UNWIND parts[1..] AS tagPart
WITH p, trim(split(tagPart, ' ')[0]) AS tagName
WHERE tagName <> ''
MERGE (t:Tag {name: toLower(tagName)})
MERGE (p)-[:TAGGED]->(t)

// Create likes
MATCH (u:User), (p:Post)
WHERE rand() < 0.05
MERGE (u)-[:LIKED {at: datetime() - duration({days: randomInteger(1, 7)})}]->(p)

// Update like counts
MATCH (p:Post)
OPTIONAL MATCH (p)<-[:LIKED]-(liker)
WITH p, count(liker) AS likes
SET p.likeCount = likes

// Update post counts
MATCH (u:User)
OPTIONAL MATCH (u)-[:POSTED]->(p:Post)
WITH u, count(p) AS posts
SET u.postCount = posts
```

---

## 34.4 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/users/register` | POST | Register new user |
| `/users/login` | POST | Login user |
| `/users/{username}` | GET | Get user profile |
| `/users/{username}/follow` | POST | Follow user |
| `/users/{username}/unfollow` | POST | Unfollow user |
| `/users/{username}/followers` | GET | Get followers |
| `/users/{username}/following` | GET | Get following |
| `/users/search` | GET | Search users |
| `/posts` | POST | Create post |
| `/posts/{id}` | GET | Get post |
| `/posts/{id}/like` | POST | Like post |
| `/posts/{id}/unlike` | POST | Unlike post |
| `/posts/{id}/comments` | GET/POST | Get/Add comments |
| `/feed/home` | GET | Home feed |
| `/feed/explore` | GET | Explore feed |
| `/feed/hashtag/{tag}` | GET | Hashtag feed |
| `/recommendations/users` | GET | User suggestions |
| `/trending` | GET | Trending topics |

---

## Summary

This social network project demonstrates:

1. **Graph Data Modeling**: Users, posts, relationships
2. **Core Social Features**: Following, posting, liking
3. **Feed Algorithms**: Chronological and engagement-based
4. **Recommendations**: Graph traversal for suggestions
5. **Search**: Full-text search integration

---

## Exercises

### Exercise 34.1: Notifications
1. Add notification system
2. Track mentions, likes, follows
3. Implement real-time updates

### Exercise 34.2: Direct Messages
1. Add messaging between users
2. Create conversation threads
3. Implement read receipts

### Exercise 34.3: Analytics
1. Track user engagement
2. Build analytics dashboard
3. Identify influential users

---

**Next Chapter: [Chapter 35: Project - Recommendation Engine](35-project-recommendation-engine.md)**
