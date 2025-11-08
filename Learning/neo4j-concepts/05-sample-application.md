# Sample Application: Social Network with Movie Recommendations

A complete social network application using Neo4j with Python, featuring user management, friendships, movie ratings, and personalized recommendations.

## Table of Contents
1. [Application Overview](#application-overview)
2. [Data Model](#data-model)
3. [Setup and Installation](#setup-and-installation)
4. [Complete Implementation](#complete-implementation)
5. [Usage Examples](#usage-examples)
6. [Advanced Features](#advanced-features)

---

## Application Overview

### Features
- ✅ User registration and authentication
- ✅ Friend connections and social graph
- ✅ Movie database with genres and actors
- ✅ Rating and reviewing movies
- ✅ Personalized movie recommendations
- ✅ Friend activity feed
- ✅ Similar users discovery
- ✅ Movie search and filtering

### Technology Stack
- **Database**: Neo4j
- **Language**: Python 3.8+
- **Driver**: neo4j-driver
- **Additional**: python-dotenv, pandas (optional)

---

## Data Model

### Node Types

```cypher
// Users
(:User {
    userId: string,
    username: string,
    email: string,
    name: string,
    joinedAt: datetime
})

// Movies
(:Movie {
    movieId: string,
    title: string,
    year: integer,
    plot: string,
    runtime: integer,
    poster: string
})

// Genres
(:Genre {
    name: string
})

// Actors
(:Actor {
    actorId: string,
    name: string,
    born: integer
})
```

### Relationship Types

```cypher
// Social relationships
(User)-[:FRIENDS_WITH {since: date}]->(User)
(User)-[:FOLLOWS {since: datetime}]->(User)

// Movie interactions
(User)-[:RATED {rating: float, timestamp: datetime}]->(Movie)
(User)-[:REVIEWED {text: string, timestamp: datetime}]->(Movie)
(User)-[:WATCHED {timestamp: datetime}]->(Movie)
(User)-[:WANTS_TO_WATCH]->(Movie)

// Movie metadata
(Movie)-[:HAS_GENRE]->(Genre)
(Actor)-[:ACTED_IN {role: string}]->(Movie)
```

### Visual Schema

```
    User ──FRIENDS_WITH──▶ User
     │         FOLLOWS
     │
     ├──RATED────────────▶ Movie ──HAS_GENRE──▶ Genre
     │                       ▲
     ├──REVIEWED────────────│
     │                       │
     ├──WATCHED──────────────│
     │                       │
     └──WANTS_TO_WATCH───────┘
                             │
                    Actor ───ACTED_IN────┘
```

---

## Setup and Installation

### 1. Prerequisites

```bash
# Install required packages
pip install neo4j python-dotenv pandas
```

### 2. Environment Configuration

Create `.env` file:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

### 3. Database Setup

```cypher
// Create constraints (run in Neo4j Browser)
CREATE CONSTRAINT user_userId IF NOT EXISTS FOR (u:User) REQUIRE u.userId IS UNIQUE;
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT movie_movieId IF NOT EXISTS FOR (m:Movie) REQUIRE m.movieId IS UNIQUE;
CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE;
CREATE CONSTRAINT actor_actorId IF NOT EXISTS FOR (a:Actor) REQUIRE a.actorId IS UNIQUE;

// Create indexes
CREATE INDEX user_username IF NOT EXISTS FOR (u:User) ON (u.username);
CREATE INDEX movie_title IF NOT EXISTS FOR (m:Movie) ON (m.title);
CREATE INDEX movie_year IF NOT EXISTS FOR (m:Movie) ON (m.year);

// Create full-text search index
CREATE FULLTEXT INDEX movie_search IF NOT EXISTS 
FOR (m:Movie) ON EACH [m.title, m.plot];
```

---

## Complete Implementation

### Core Database Class

```python
# social_network_app.py

import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class SocialNetworkApp:
    """Complete social network application with Neo4j"""
    
    def __init__(self):
        """Initialize database connection"""
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
    
    # ==================== USER MANAGEMENT ====================
    
    def create_user(self, username: str, email: str, name: str) -> Dict:
        """Create a new user"""
        query = """
        CREATE (u:User {
            userId: $userId,
            username: $username,
            email: $email,
            name: $name,
            joinedAt: datetime()
        })
        RETURN u
        """
        user_id = str(uuid.uuid4())
        
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                userId=user_id,
                username=username,
                email=email,
                name=name
            )
            record = result.single()
            return dict(record["u"])
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        query = """
        MATCH (u:User {username: $username})
        RETURN u
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username)
            record = result.single()
            return dict(record["u"]) if record else None
    
    def search_users(self, search_term: str, limit: int = 10) -> List[Dict]:
        """Search users by username or name"""
        query = """
        MATCH (u:User)
        WHERE toLower(u.username) CONTAINS toLower($term) 
           OR toLower(u.name) CONTAINS toLower($term)
        RETURN u.username AS username, u.name AS name, u.email AS email
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, term=search_term, limit=limit)
            return [dict(record) for record in result]
    
    # ==================== FRIENDSHIPS ====================
    
    def add_friend(self, username1: str, username2: str) -> bool:
        """Create bidirectional friendship"""
        query = """
        MATCH (u1:User {username: $username1})
        MATCH (u2:User {username: $username2})
        MERGE (u1)-[r1:FRIENDS_WITH {since: date()}]->(u2)
        MERGE (u2)-[r2:FRIENDS_WITH {since: date()}]->(u1)
        RETURN r1, r2
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username1=username1, username2=username2)
            return result.single() is not None
    
    def remove_friend(self, username1: str, username2: str) -> bool:
        """Remove friendship"""
        query = """
        MATCH (u1:User {username: $username1})-[r:FRIENDS_WITH]-(u2:User {username: $username2})
        DELETE r
        RETURN count(r) AS deleted
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username1=username1, username2=username2)
            record = result.single()
            return record["deleted"] > 0
    
    def get_friends(self, username: str) -> List[Dict]:
        """Get all friends of a user"""
        query = """
        MATCH (u:User {username: $username})-[r:FRIENDS_WITH]->(friend:User)
        RETURN friend.username AS username,
               friend.name AS name,
               r.since AS friendsSince
        ORDER BY r.since DESC
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username)
            return [dict(record) for record in result]
    
    def get_friend_suggestions(self, username: str, limit: int = 10) -> List[Dict]:
        """Get friend suggestions (friends of friends)"""
        query = """
        MATCH (u:User {username: $username})-[:FRIENDS_WITH]->(friend)-[:FRIENDS_WITH]->(suggestion:User)
        WHERE u <> suggestion 
          AND NOT (u)-[:FRIENDS_WITH]-(suggestion)
        WITH suggestion, count(DISTINCT friend) AS mutualFriends
        RETURN suggestion.username AS username,
               suggestion.name AS name,
               mutualFriends
        ORDER BY mutualFriends DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username, limit=limit)
            return [dict(record) for record in result]
    
    # ==================== MOVIES ====================
    
    def create_movie(self, title: str, year: int, plot: str = "", 
                    runtime: int = 0, poster: str = "") -> Dict:
        """Create a new movie"""
        query = """
        CREATE (m:Movie {
            movieId: $movieId,
            title: $title,
            year: $year,
            plot: $plot,
            runtime: $runtime,
            poster: $poster
        })
        RETURN m
        """
        movie_id = str(uuid.uuid4())
        
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                movieId=movie_id,
                title=title,
                year=year,
                plot=plot,
                runtime=runtime,
                poster=poster
            )
            record = result.single()
            return dict(record["m"])
    
    def add_genre_to_movie(self, movie_id: str, genre_name: str):
        """Add genre to movie"""
        query = """
        MATCH (m:Movie {movieId: $movieId})
        MERGE (g:Genre {name: $genreName})
        MERGE (m)-[:HAS_GENRE]->(g)
        RETURN m, g
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, movieId=movie_id, genreName=genre_name)
            return result.single() is not None
    
    def add_actor_to_movie(self, movie_id: str, actor_name: str, role: str = ""):
        """Add actor to movie"""
        query = """
        MATCH (m:Movie {movieId: $movieId})
        MERGE (a:Actor {name: $actorName})
        ON CREATE SET a.actorId = $actorId
        MERGE (a)-[r:ACTED_IN]->(m)
        SET r.role = $role
        RETURN a, r, m
        """
        actor_id = str(uuid.uuid4())
        
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                movieId=movie_id,
                actorName=actor_name,
                actorId=actor_id,
                role=role
            )
            return result.single() is not None
    
    def search_movies(self, search_term: str, limit: int = 20) -> List[Dict]:
        """Search movies by title or plot"""
        query = """
        CALL db.index.fulltext.queryNodes('movie_search', $term)
        YIELD node, score
        WITH node AS m, score
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        RETURN m.movieId AS movieId,
               m.title AS title,
               m.year AS year,
               m.plot AS plot,
               collect(DISTINCT g.name) AS genres,
               score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, term=search_term, limit=limit)
            return [dict(record) for record in result]
    
    def get_movie_details(self, movie_id: str) -> Optional[Dict]:
        """Get complete movie details with genres and actors"""
        query = """
        MATCH (m:Movie {movieId: $movieId})
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        OPTIONAL MATCH (a:Actor)-[r:ACTED_IN]->(m)
        WITH m, 
             collect(DISTINCT g.name) AS genres,
             collect(DISTINCT {name: a.name, role: r.role}) AS cast
        OPTIONAL MATCH (u:User)-[rat:RATED]->(m)
        RETURN m.movieId AS movieId,
               m.title AS title,
               m.year AS year,
               m.plot AS plot,
               m.runtime AS runtime,
               genres,
               cast,
               avg(rat.rating) AS avgRating,
               count(rat) AS numRatings
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, movieId=movie_id)
            record = result.single()
            return dict(record) if record else None
    
    # ==================== RATINGS & REVIEWS ====================
    
    def rate_movie(self, username: str, movie_id: str, rating: float, 
                   review_text: str = "") -> bool:
        """Rate a movie (1-5 stars) and optionally review it"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        query = """
        MATCH (u:User {username: $username})
        MATCH (m:Movie {movieId: $movieId})
        MERGE (u)-[r:RATED]->(m)
        SET r.rating = $rating,
            r.timestamp = datetime()
        WITH u, m, r
        FOREACH (x IN CASE WHEN $reviewText <> '' THEN [1] ELSE [] END |
            MERGE (u)-[rev:REVIEWED]->(m)
            SET rev.text = $reviewText,
                rev.timestamp = datetime()
        )
        RETURN r
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(
                query,
                username=username,
                movieId=movie_id,
                rating=rating,
                reviewText=review_text
            )
            return result.single() is not None
    
    def get_user_ratings(self, username: str) -> List[Dict]:
        """Get all movies rated by user"""
        query = """
        MATCH (u:User {username: $username})-[r:RATED]->(m:Movie)
        OPTIONAL MATCH (u)-[rev:REVIEWED]->(m)
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        RETURN m.movieId AS movieId,
               m.title AS title,
               m.year AS year,
               r.rating AS rating,
               r.timestamp AS ratedAt,
               rev.text AS review,
               collect(DISTINCT g.name) AS genres
        ORDER BY r.timestamp DESC
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username)
            return [dict(record) for record in result]
    
    def get_movie_reviews(self, movie_id: str) -> List[Dict]:
        """Get all reviews for a movie"""
        query = """
        MATCH (u:User)-[rev:REVIEWED]->(m:Movie {movieId: $movieId})
        OPTIONAL MATCH (u)-[r:RATED]->(m)
        RETURN u.username AS username,
               u.name AS name,
               rev.text AS review,
               r.rating AS rating,
               rev.timestamp AS reviewedAt
        ORDER BY rev.timestamp DESC
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, movieId=movie_id)
            return [dict(record) for record in result]
    
    # ==================== RECOMMENDATIONS ====================
    
    def get_collaborative_recommendations(self, username: str, limit: int = 10) -> List[Dict]:
        """
        Collaborative filtering: recommend movies liked by similar users
        Based on users who rated similar movies highly
        """
        query = """
        // Find users with similar taste
        MATCH (u:User {username: $username})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(other:User)
        WHERE r1.rating >= 4 AND r2.rating >= 4 AND u <> other
        WITH other, count(DISTINCT m) AS commonMovies, u
        ORDER BY commonMovies DESC
        LIMIT 10
        
        // Get movies they liked that target user hasn't seen
        MATCH (other)-[r:RATED]->(rec:Movie)
        WHERE r.rating >= 4
          AND NOT EXISTS((u)-[:RATED]->(rec))
        WITH rec, avg(r.rating) AS avgRating, count(DISTINCT other) AS numRecommenders
        
        OPTIONAL MATCH (rec)-[:HAS_GENRE]->(g:Genre)
        RETURN rec.movieId AS movieId,
               rec.title AS title,
               rec.year AS year,
               avgRating,
               numRecommenders,
               collect(DISTINCT g.name) AS genres
        ORDER BY numRecommenders DESC, avgRating DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username, limit=limit)
            return [dict(record) for record in result]
    
    def get_friend_recommendations(self, username: str, limit: int = 10) -> List[Dict]:
        """Recommend movies that friends have rated highly"""
        query = """
        MATCH (u:User {username: $username})-[:FRIENDS_WITH]->(friend:User)
        MATCH (friend)-[r:RATED]->(m:Movie)
        WHERE r.rating >= 4
          AND NOT EXISTS((u)-[:RATED]->(m))
        WITH m, avg(r.rating) AS avgRating, count(DISTINCT friend) AS friendsWhoLiked
        
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        RETURN m.movieId AS movieId,
               m.title AS title,
               m.year AS year,
               avgRating,
               friendsWhoLiked,
               collect(DISTINCT g.name) AS genres
        ORDER BY friendsWhoLiked DESC, avgRating DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username, limit=limit)
            return [dict(record) for record in result]
    
    def get_genre_based_recommendations(self, username: str, limit: int = 10) -> List[Dict]:
        """Recommend movies based on user's favorite genres"""
        query = """
        // Find user's favorite genres
        MATCH (u:User {username: $username})-[r:RATED]->(m:Movie)-[:HAS_GENRE]->(g:Genre)
        WHERE r.rating >= 4
        WITH g, count(*) AS genreCount
        ORDER BY genreCount DESC
        LIMIT 3
        
        // Find highly rated movies in those genres
        MATCH (g)<-[:HAS_GENRE]-(rec:Movie)<-[r2:RATED]-(other:User)
        WHERE NOT EXISTS((:User {username: $username})-[:RATED]->(rec))
        WITH rec, avg(r2.rating) AS avgRating, count(r2) AS numRatings, collect(DISTINCT g.name) AS genres
        WHERE numRatings >= 5 AND avgRating >= 4
        
        RETURN rec.movieId AS movieId,
               rec.title AS title,
               rec.year AS year,
               avgRating,
               numRatings,
               genres
        ORDER BY avgRating DESC, numRatings DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username, limit=limit)
            return [dict(record) for record in result]
    
    # ==================== SOCIAL FEATURES ====================
    
    def get_activity_feed(self, username: str, limit: int = 20) -> List[Dict]:
        """Get recent activity from friends"""
        query = """
        MATCH (u:User {username: $username})-[:FRIENDS_WITH]->(friend:User)
        MATCH (friend)-[r:RATED]->(m:Movie)
        OPTIONAL MATCH (friend)-[rev:REVIEWED]->(m)
        RETURN friend.username AS username,
               friend.name AS name,
               m.title AS movie,
               m.movieId AS movieId,
               r.rating AS rating,
               rev.text AS review,
               r.timestamp AS timestamp,
               'rating' AS activityType
        ORDER BY r.timestamp DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username, limit=limit)
            return [dict(record) for record in result]
    
    def get_user_stats(self, username: str) -> Dict:
        """Get user statistics"""
        query = """
        MATCH (u:User {username: $username})
        OPTIONAL MATCH (u)-[:FRIENDS_WITH]->(friend:User)
        OPTIONAL MATCH (u)-[r:RATED]->(m:Movie)
        OPTIONAL MATCH (u)-[rev:REVIEWED]->(m2:Movie)
        RETURN u.username AS username,
               u.name AS name,
               u.joinedAt AS joinedAt,
               count(DISTINCT friend) AS friendCount,
               count(DISTINCT m) AS moviesRated,
               count(DISTINCT m2) AS moviesReviewed,
               avg(r.rating) AS avgRating
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, username=username)
            record = result.single()
            return dict(record) if record else None
    
    def get_popular_movies(self, limit: int = 20, min_ratings: int = 10) -> List[Dict]:
        """Get most popular movies"""
        query = """
        MATCH (m:Movie)<-[r:RATED]-(u:User)
        WITH m, avg(r.rating) AS avgRating, count(r) AS numRatings
        WHERE numRatings >= $minRatings
        OPTIONAL MATCH (m)-[:HAS_GENRE]->(g:Genre)
        RETURN m.movieId AS movieId,
               m.title AS title,
               m.year AS year,
               avgRating,
               numRatings,
               collect(DISTINCT g.name) AS genres
        ORDER BY avgRating DESC, numRatings DESC
        LIMIT $limit
        """
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, limit=limit, minRatings=min_ratings)
            return [dict(record) for record in result]
```

---

## Usage Examples

### Complete Demo Script

```python
# demo.py

from social_network_app import SocialNetworkApp


def main():
    # Initialize app
    app = SocialNetworkApp()
    
    try:
        print("🎬 Social Network Movie App Demo\n")
        
        # 1. Create users
        print("1️⃣ Creating users...")
        alice = app.create_user("alice", "alice@example.com", "Alice Johnson")
        bob = app.create_user("bob", "bob@example.com", "Bob Smith")
        charlie = app.create_user("charlie", "charlie@example.com", "Charlie Brown")
        print(f"✅ Created users: {alice['username']}, {bob['username']}, {charlie['username']}\n")
        
        # 2. Add friendships
        print("2️⃣ Creating friendships...")
        app.add_friend("alice", "bob")
        app.add_friend("alice", "charlie")
        print("✅ Alice is now friends with Bob and Charlie\n")
        
        # 3. Create movies
        print("3️⃣ Adding movies...")
        movie1 = app.create_movie(
            "The Matrix",
            1999,
            "A computer hacker learns about the true nature of reality.",
            136
        )
        app.add_genre_to_movie(movie1['movieId'], "Sci-Fi")
        app.add_genre_to_movie(movie1['movieId'], "Action")
        app.add_actor_to_movie(movie1['movieId'], "Keanu Reeves", "Neo")
        
        movie2 = app.create_movie(
            "Inception",
            2010,
            "A thief who steals corporate secrets through dream-sharing technology.",
            148
        )
        app.add_genre_to_movie(movie2['movieId'], "Sci-Fi")
        app.add_genre_to_movie(movie2['movieId'], "Thriller")
        app.add_actor_to_movie(movie2['movieId'], "Leonardo DiCaprio", "Cobb")
        
        movie3 = app.create_movie(
            "The Shawshank Redemption",
            1994,
            "Two imprisoned men bond over years, finding redemption.",
            142
        )
        app.add_genre_to_movie(movie3['movieId'], "Drama")
        print("✅ Added 3 movies\n")
        
        # 4. Rate movies
        print("4️⃣ Users rating movies...")
        app.rate_movie("alice", movie1['movieId'], 5.0, "Amazing movie! Mind-blowing.")
        app.rate_movie("alice", movie2['movieId'], 4.5, "Complex and brilliant!")
        app.rate_movie("bob", movie1['movieId'], 4.5, "Great action and story.")
        app.rate_movie("bob", movie3['movieId'], 5.0, "Best movie ever!")
        app.rate_movie("charlie", movie2['movieId'], 5.0)
        print("✅ Movies rated\n")
        
        # 5. Get movie details
        print("5️⃣ Movie details:")
        details = app.get_movie_details(movie1['movieId'])
        print(f"🎬 {details['title']} ({details['year']})")
        print(f"   Genres: {', '.join(details['genres'])}")
        print(f"   Cast: {', '.join([actor['name'] for actor in details['cast']])}")
        print(f"   Rating: {details['avgRating']:.1f}/5 ({details['numRatings']} ratings)\n")
        
        # 6. Get recommendations
        print("6️⃣ Recommendations for Alice:")
        recommendations = app.get_friend_recommendations("alice", limit=5)
        for rec in recommendations:
            print(f"   📽️  {rec['title']} ({rec['year']}) - "
                  f"{rec['friendsWhoLiked']} friends liked it")
        print()
        
        # 7. Friend suggestions
        print("7️⃣ Friend suggestions for Bob:")
        suggestions = app.get_friend_suggestions("bob", limit=5)
        for sug in suggestions:
            print(f"   👤 {sug['name']} (@{sug['username']}) - "
                  f"{sug['mutualFriends']} mutual friends")
        print()
        
        # 8. Activity feed
        print("8️⃣ Alice's friend activity:")
        feed = app.get_activity_feed("alice", limit=5)
        for activity in feed:
            print(f"   • {activity['name']} rated '{activity['movie']}' "
                  f"{activity['rating']}/5")
        print()
        
        # 9. User stats
        print("9️⃣ Alice's statistics:")
        stats = app.get_user_stats("alice")
        print(f"   Friends: {stats['friendCount']}")
        print(f"   Movies rated: {stats['moviesRated']}")
        print(f"   Average rating: {stats['avgRating']:.1f}/5")
        print()
        
        # 10. Search movies
        print("🔟 Searching for 'matrix':")
        results = app.search_movies("matrix", limit=5)
        for movie in results:
            print(f"   🎬 {movie['title']} ({movie['year']})")
        
        print("\n✅ Demo completed successfully!")
        
    finally:
        app.close()


if __name__ == "__main__":
    main()
```

---

## Advanced Features

### Analytics Queries

```python
def get_top_rated_by_genre(app, genre_name: str, limit: int = 10):
    """Get top-rated movies in a specific genre"""
    query = """
    MATCH (g:Genre {name: $genre})<-[:HAS_GENRE]-(m:Movie)<-[r:RATED]-(u:User)
    WITH m, avg(r.rating) AS avgRating, count(r) AS numRatings
    WHERE numRatings >= 5
    RETURN m.title AS title,
           m.year AS year,
           avgRating,
           numRatings
    ORDER BY avgRating DESC, numRatings DESC
    LIMIT $limit
    """
    
    with app.driver.session(database=app.database) as session:
        result = session.run(query, genre=genre_name, limit=limit)
        return [dict(record) for record in result]


def get_most_active_users(app, limit: int = 10):
    """Get users who rated the most movies"""
    query = """
    MATCH (u:User)-[r:RATED]->(m:Movie)
    WITH u, count(r) AS ratingsCount, avg(r.rating) AS avgRating
    RETURN u.username AS username,
           u.name AS name,
           ratingsCount,
           avgRating
    ORDER BY ratingsCount DESC
    LIMIT $limit
    """
    
    with app.driver.session(database=app.database) as session:
        result = session.run(query, limit=limit)
        return [dict(record) for record in result]


def get_movie_similarity(app, movie_id: str, limit: int = 10):
    """Find similar movies based on shared ratings"""
    query = """
    MATCH (m:Movie {movieId: $movieId})<-[r1:RATED]-(u:User)-[r2:RATED]->(other:Movie)
    WHERE m <> other AND abs(r1.rating - r2.rating) <= 1
    WITH other, count(DISTINCT u) AS commonRaters
    OPTIONAL MATCH (other)-[:HAS_GENRE]->(g:Genre)
    RETURN other.movieId AS movieId,
           other.title AS title,
           other.year AS year,
           commonRaters,
           collect(DISTINCT g.name) AS genres
    ORDER BY commonRaters DESC
    LIMIT $limit
    """
    
    with app.driver.session(database=app.database) as session:
        result = session.run(query, movieId=movie_id, limit=limit)
        return [dict(record) for record in result]
```

### Batch Data Import

```python
def import_movies_from_csv(app, csv_file_path: str):
    """Import movies from CSV file"""
    import pandas as pd
    
    df = pd.read_csv(csv_file_path)
    
    query = """
    UNWIND $movies AS movie
    CREATE (m:Movie {
        movieId: movie.movieId,
        title: movie.title,
        year: toInteger(movie.year),
        plot: movie.plot
    })
    WITH m, movie
    UNWIND split(movie.genres, '|') AS genre
    MERGE (g:Genre {name: trim(genre)})
    MERGE (m)-[:HAS_GENRE]->(g)
    """
    
    movies_data = df.to_dict('records')
    
    # Process in batches
    batch_size = 1000
    for i in range(0, len(movies_data), batch_size):
        batch = movies_data[i:i + batch_size]
        with app.driver.session(database=app.database) as session:
            session.run(query, movies=batch)
        print(f"Imported {min(i + batch_size, len(movies_data))} movies")
```

---

## Testing

```python
# test_app.py

import pytest
from social_network_app import SocialNetworkApp


@pytest.fixture
def app():
    app = SocialNetworkApp()
    yield app
    app.close()


def test_create_user(app):
    user = app.create_user("testuser", "test@example.com", "Test User")
    assert user['username'] == "testuser"
    assert user['email'] == "test@example.com"


def test_friendship(app):
    app.create_user("user1", "user1@example.com", "User One")
    app.create_user("user2", "user2@example.com", "User Two")
    
    result = app.add_friend("user1", "user2")
    assert result is True
    
    friends = app.get_friends("user1")
    assert len(friends) == 1
    assert friends[0]['username'] == "user2"


def test_movie_rating(app):
    app.create_user("rater", "rater@example.com", "Rater")
    movie = app.create_movie("Test Movie", 2024, "Test plot")
    
    result = app.rate_movie("rater", movie['movieId'], 4.5, "Great!")
    assert result is True
    
    ratings = app.get_user_ratings("rater")
    assert len(ratings) == 1
    assert ratings[0]['rating'] == 4.5
```

---

**Next**: See [06-rag-with-neo4j.md](06-rag-with-neo4j.md) for implementing RAG (Retrieval Augmented Generation) with LangChain and Neo4j.
