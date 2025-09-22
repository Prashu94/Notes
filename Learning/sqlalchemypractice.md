# SQLAlchemy Practice Problems

This document contains practice problems for SQLAlchemy with detailed solutions. Problems range from basic to advanced concepts.

## Prerequisites

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///practice.db')
Session = sessionmaker(bind=engine)
session = Session()
```

---

## Problem 1: Basic Model Definition

**Problem**: Create a `User` model with the following fields:
- `id` (Primary Key, Integer)
- `username` (String, max 80 characters, unique)
- `email` (String, max 120 characters)
- `created_at` (DateTime, default to current time)

**Solution**:
```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
```

---

## Problem 2: One-to-Many Relationship

**Problem**: Create `Post` model that has a many-to-one relationship with `User`. Each post should have:
- `id` (Primary Key)
- `title` (String, max 100 characters)
- `content` (String)
- `user_id` (Foreign Key to User)
- `created_at` (DateTime)

**Solution**:
```python
class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    author = relationship("User", back_populates="posts")
    
    def __repr__(self):
        return f"<Post(title='{self.title}', user_id={self.user_id})>"

# Update User model to include the relationship
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = relationship("Post", back_populates="author")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
```

---

## Problem 3: Basic CRUD Operations

**Problem**: Write functions to:
1. Create a new user
2. Get all users
3. Update a user's email
4. Delete a user

**Solution**:
```python
def create_user(username, email):
    """Create a new user"""
    user = User(username=username, email=email)
    session.add(user)
    session.commit()
    return user

def get_all_users():
    """Get all users"""
    return session.query(User).all()

def update_user_email(user_id, new_email):
    """Update user's email"""
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        user.email = new_email
        session.commit()
        return user
    return None

def delete_user(user_id):
    """Delete a user"""
    user = session.query(User).filter(User.id == user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return True
    return False
```

---

## Problem 4: Query Filtering

**Problem**: Write queries to:
1. Find users with username starting with 'john'
2. Find posts created in the last 7 days
3. Find users who have more than 5 posts

**Solution**:
```python
from sqlalchemy import func
from datetime import datetime, timedelta

def find_users_by_username_prefix(prefix):
    """Find users with username starting with given prefix"""
    return session.query(User).filter(User.username.like(f'{prefix}%')).all()

def find_recent_posts(days=7):
    """Find posts created in the last N days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    return session.query(Post).filter(Post.created_at >= cutoff_date).all()

def find_active_users(min_posts=5):
    """Find users who have more than min_posts posts"""
    return session.query(User).join(Post).group_by(User.id).having(func.count(Post.id) > min_posts).all()
```

---

## Problem 5: Many-to-Many Relationship

**Problem**: Create a many-to-many relationship between `User` and `Tag` models through posts. A user can have multiple tags, and a tag can belong to multiple users.

**Solution**:
```python
# Association table for many-to-many relationship
user_tags = Table('user_tags', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    # Many-to-many relationship
    users = relationship("User", secondary=user_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(name='{self.name}')>"

# Update User model to include tags relationship
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = relationship("Post", back_populates="author")
    tags = relationship("Tag", secondary=user_tags, back_populates="users")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"
```

---

## Problem 6: Advanced Queries with Joins

**Problem**: Write queries to:
1. Get all posts with their author information
2. Get users along with their post count
3. Find the most popular tags (used by most users)

**Solution**:
```python
def get_posts_with_authors():
    """Get all posts with their author information"""
    return session.query(Post, User).join(User, Post.user_id == User.id).all()

def get_users_with_post_count():
    """Get users along with their post count"""
    return session.query(
        User.username, 
        func.count(Post.id).label('post_count')
    ).outerjoin(Post).group_by(User.id).all()

def get_popular_tags(limit=10):
    """Find the most popular tags (used by most users)"""
    return session.query(
        Tag.name, 
        func.count(user_tags.c.user_id).label('user_count')
    ).join(user_tags).group_by(Tag.id).order_by(
        func.count(user_tags.c.user_id).desc()
    ).limit(limit).all()
```

---

## Problem 7: Subqueries and Window Functions

**Problem**: Find users who have posted more than the average number of posts.

**Solution**:
```python
def find_above_average_posters():
    """Find users who have posted more than the average number of posts"""
    
    # Subquery to calculate average posts per user
    avg_posts = session.query(
        func.avg(func.count(Post.id))
    ).join(User).group_by(User.id).subquery()
    
    # Main query
    user_post_counts = session.query(
        User.username,
        func.count(Post.id).label('post_count')
    ).join(Post).group_by(User.id).having(
        func.count(Post.id) > avg_posts.c.anon_1
    ).all()
    
    return user_post_counts
```

---

## Problem 8: Raw SQL and Hybrid Properties

**Problem**: Create a hybrid property that calculates the number of posts for each user and execute a raw SQL query.

**Solution**:
```python
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import text

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author")
    
    @hybrid_property
    def post_count(self):
        return len(self.posts)
    
    @post_count.expression
    def post_count(cls):
        return (
            session.query(func.count(Post.id))
            .filter(Post.user_id == cls.id)
            .label('post_count')
        )

def execute_raw_sql():
    """Execute raw SQL query"""
    result = session.execute(
        text("SELECT u.username, COUNT(p.id) as post_count "
             "FROM users u LEFT JOIN posts p ON u.id = p.user_id "
             "GROUP BY u.id ORDER BY post_count DESC")
    )
    return result.fetchall()
```

---

## Problem 9: Database Transactions and Error Handling

**Problem**: Create a function that creates a user and their first post in a single transaction with proper error handling.

**Solution**:
```python
def create_user_with_post(username, email, post_title, post_content):
    """Create user and their first post in a single transaction"""
    try:
        # Create user
        user = User(username=username, email=email)
        session.add(user)
        session.flush()  # Flush to get the user ID
        
        # Create post
        post = Post(
            title=post_title, 
            content=post_content, 
            user_id=user.id
        )
        session.add(post)
        
        # Commit transaction
        session.commit()
        return user, post
        
    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")
        return None, None
    finally:
        session.close()
```

---

## Problem 10: Performance Optimization

**Problem**: Optimize a query that fetches users with their posts and tags to avoid N+1 query problem.

**Solution**:
```python
def get_users_with_posts_and_tags_optimized():
    """Optimized query using eager loading to avoid N+1 problem"""
    from sqlalchemy.orm import joinedload
    
    return session.query(User).options(
        joinedload(User.posts),
        joinedload(User.tags)
    ).all()

def get_users_with_posts_and_tags_select_related():
    """Alternative approach using selectinload for better performance with large datasets"""
    from sqlalchemy.orm import selectinload
    
    return session.query(User).options(
        selectinload(User.posts),
        selectinload(User.tags)
    ).all()
```

---

## Practice Exercises

Try these additional exercises:

1. **Pagination**: Implement a function that returns paginated results for posts
2. **Search**: Create a full-text search function for posts
3. **Soft Delete**: Implement soft delete functionality for users
4. **Audit Trail**: Add created_by and updated_by fields to track changes
5. **Connection Pooling**: Configure connection pooling for better performance

## Setup Instructions

To run these examples:

1. Install SQLAlchemy: `pip install sqlalchemy`
2. Create the database tables: `Base.metadata.create_all(engine)`
3. Run the examples in a Python script or Jupyter notebook

Remember to always close sessions and handle exceptions properly in production code!