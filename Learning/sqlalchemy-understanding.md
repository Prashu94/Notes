# SQLAlchemy Complete Learning Guide with PostgreSQL Projects

## Table of Contents
1. [Project Setup](#project-setup)
2. [Core Concepts](#core-concepts)
3. [Project 1: Basic CRUD API](#project-1-basic-crud-api)
4. [Project 2: Advanced Relationships](#project-2-advanced-relationships)
5. [Project 3: Working with Existing Database](#project-3-working-with-existing-database)
6. [Project 4: Transaction Management](#project-4-transaction-management)
7. [Project 5: Advanced Features](#project-5-advanced-features)
8. [Testing Strategies](#testing-strategies)
9. [Best Practices](#best-practices)

## Project Setup

### Prerequisites
- Python 3.8+
- PostgreSQL installed and running
- Basic knowledge of Python and SQL

### Installation
```bash
# Create virtual environment
python -m venv sqlalchemy_env
source sqlalchemy_env/bin/activate  # On Mac/Linux

# Install dependencies
pip install sqlalchemy psycopg2-binary fastapi uvicorn python-dotenv alembic pytest pytest-asyncio
```

### Environment Setup
```bash
# .env file
DATABASE_URL=postgresql://username:password@localhost:5432/sqlalchemy_db
DATABASE_URL_ASYNC=postgresql+asyncpg://username:password@localhost:5432/sqlalchemy_db
```

## Core Concepts

### 1. Database Connection and Engine
```python
# database.py
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL_ASYNC = os.getenv("DATABASE_URL_ASYNC")

# Synchronous Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Log SQL statements
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)

# Asynchronous Engine
async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=True,
    pool_size=10,
    max_overflow=20,
)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session

import asyncio
import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine, async_engine, get_db, get_async_db, Base

def test_sync_database_connection():
    """Test synchronous database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            assert result.fetchone()[0] == 1
        print("✓ Synchronous database connection successful")
        return True
    except Exception as e:
        print(f"✗ Synchronous database connection failed: {e}")
        return False

async def test_async_database_connection():
    """Test asynchronous database connection"""
    try:
        async with async_engine.begin() as connection:
            result = await connection.execute(text("SELECT 1 as test"))
            assert result.fetchone()[0] == 1
        print("✓ Asynchronous database connection successful")
        return True
    except Exception as e:
        print(f"✗ Asynchronous database connection failed: {e}")
        return False

def test_sync_session_factory():
    """Test synchronous session creation"""
    try:
        db_gen = get_db()
        db = next(db_gen)
        result = db.execute(text("SELECT 1 as test"))
        assert result.fetchone()[0] == 1
        db.close()
        print("✓ Synchronous session factory working")
        return True
    except Exception as e:
        print(f"✗ Synchronous session factory failed: {e}")
        return False

async def test_async_session_factory():
    """Test asynchronous session creation"""
    try:
        async_db_gen = get_async_db()
        db = await async_db_gen.__anext__()
        result = await db.execute(text("SELECT 1 as test"))
        assert result.fetchone()[0] == 1
        await db.close()
        print("✓ Asynchronous session factory working")
        return True
    except Exception as e:
        print(f"✗ Asynchronous session factory failed: {e}")
        return False

def test_engine_configuration():
    """Test engine configuration parameters"""
    assert engine.pool.size() >= 0
    assert hasattr(engine, 'echo')
    print("✓ Engine configuration verified")
    return True

async def run_all_tests():
    """Run all database tests"""
    print("Running database tests...\n")
    
    # Synchronous tests
    test_sync_database_connection()
    test_sync_session_factory()
    test_engine_configuration()
    
    # Asynchronous tests
    await test_async_database_connection()
    await test_async_session_factory()
    
    print("\nDatabase tests completed!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
```

## Project 1: Basic CRUD API

### Models Definition
```python
# models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text)
    age = Column(Integer)
    location = Column(String(100))
    
    user = relationship("User", back_populates="profile")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    posts = relationship("Post", back_populates="category")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    author = relationship("User", back_populates="posts")
    category = relationship("Category", back_populates="posts")
    tags = relationship("Tag", secondary="post_tags", back_populates="posts")

# Many-to-Many Association Table
from sqlalchemy import Table
post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    
    posts = relationship("Post", secondary="post_tags", back_populates="tags")
```

### CRUD Operations
```python
# crud.py
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select, update, delete, and_, or_, func, case, distinct
from sqlalchemy.exc import IntegrityError
from models import User, Post, Category, Tag, UserProfile, UserStatus
from typing import List, Optional

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, full_name: str) -> User:
        """Create a new user with error handling"""
        try:
            user = User(username=username, email=email, full_name=full_name)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"User creation failed: {str(e)}")
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID with relationships"""
        return self.db.query(User).options(
            joinedload(User.profile),
            selectinload(User.posts)
        ).filter(User.id == user_id).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user fields"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
    
    # Advanced Query Methods
    def search_users(self, query: str) -> List[User]:
        """Full-text search across multiple fields"""
        return self.db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%")
            )
        ).all()
    
    def get_active_users_with_posts(self) -> List[User]:
        """Get active users who have posts"""
        return self.db.query(User).join(Post).filter(
            User.is_active == True
        ).distinct().all()
    
    def get_user_statistics(self):
        """Get user statistics using aggregation"""
        return self.db.query(
            func.count(User.id).label('total_users'),
            func.count(case((User.is_active == True, 1))).label('active_users'),
            func.count(case((User.status == UserStatus.SUSPENDED, 1))).label('suspended_users')
        ).first()

class PostCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(self, title: str, content: str, author_id: int, 
                   category_id: int = None, tag_names: List[str] = None) -> Post:
        """Create post with tags"""
        post = Post(title=title, content=content, author_id=author_id, category_id=category_id)
        
        if tag_names:
            tags = []
            for tag_name in tag_names:
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                tags.append(tag)
            post.tags = tags
        
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post
    
    def get_posts_with_filters(self, author_id: int = None, category_id: int = None,
                              tag_name: str = None) -> List[Post]:
        """Get posts with various filters"""
        query = self.db.query(Post).options(
            joinedload(Post.author),
            joinedload(Post.category),
            selectinload(Post.tags)
        )
        
        if author_id:
            query = query.filter(Post.author_id == author_id)
        if category_id:
            query = query.filter(Post.category_id == category_id)
        if tag_name:
            query = query.join(Post.tags).filter(Tag.name == tag_name)
            
        return query.all()
    
    def get_posts_by_price_range(self, min_price: float, max_price: float) -> List[Post]:
        """Get posts within price range"""
        return self.db.query(Post).filter(
            and_(Post.price >= min_price, Post.price <= max_price)
        ).all()
```

### FastAPI Application
```python
# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from crud import UserCRUD, PostCRUD
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SQLAlchemy Complete API", version="1.0.0")

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int
    category_id: Optional[int] = None
    tag_names: Optional[List[str]] = None

# User Endpoints
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    crud = UserCRUD(db)
    try:
        return crud.create_user(user.username, user.email, user.full_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    crud = UserCRUD(db)
    user = crud.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    crud = UserCRUD(db)
    return crud.get_users(skip=skip, limit=limit)

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, full_name: str = None, db: Session = Depends(get_db)):
    crud = UserCRUD(db)
    user = crud.update_user(user_id, full_name=full_name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    crud = UserCRUD(db)
    if not crud.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Project 2: Advanced Relationships

### Complex Models with Multiple Relationship Types
```python
# advanced_models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Self-referential Many-to-Many (User following)
user_followers = Table(
    'user_followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id'))
)

# Polymorphic relationships
class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    
    # Polymorphic fields
    commentable_id = Column(Integer, nullable=False)
    commentable_type = Column(String(50), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    author = relationship("User")
    
    __mapper_args__ = {
        'polymorphic_on': commentable_type,
        'polymorphic_identity': 'comment'
    }

# Advanced User model with self-referential relationship
class AdvancedUser(Base):
    __tablename__ = 'advanced_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    
    # Self-referential Many-to-Many
    following = relationship(
        "AdvancedUser",
        secondary=user_followers,
        primaryjoin=id == user_followers.c.follower_id,
        secondaryjoin=id == user_followers.c.followed_id,
        backref="followers"
    )
    
    # One-to-Many self-referential (Manager-Employee)
    manager_id = Column(Integer, ForeignKey('advanced_users.id'))
    subordinates = relationship("AdvancedUser", backref="manager", remote_side=[id])

# Hybrid Properties and Custom Query Methods
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)  # Price in cents
    tax_rate = Column(Integer)  # Tax rate in basis points (e.g., 825 = 8.25%)
    
    @hybrid_property
    def price_dollars(self):
        return self.price / 100
    
    @price_dollars.expression
    def price_dollars(cls):
        return cls.price / 100
    
    @hybrid_property
    def total_price(self):
        return self.price * (1 + self.tax_rate / 10000) / 100
    
    @total_price.expression
    def total_price(cls):
        return cls.price * (1 + cls.tax_rate / 10000.0) / 100
```

### Advanced Querying Techniques
```python
# advanced_queries.py
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, select, case, exists, and_, or_, text
from advanced_models import AdvancedUser, Product, Comment

class AdvancedQueries:
    def __init__(self, db: Session):
        self.db = db
    
    def get_users_with_follower_count(self):
        """Get users with their follower count using subquery"""
        follower_count = (
            self.db.query(func.count(user_followers.c.follower_id))
            .filter(user_followers.c.followed_id == AdvancedUser.id)
            .correlate(AdvancedUser)
            .scalar_subquery()
        )
        
        return self.db.query(
            AdvancedUser,
            follower_count.label('follower_count')
        ).all()
    
    def get_mutual_followers(self, user1_id: int, user2_id: int):
        """Find mutual followers between two users"""
        user1_followers = aliased(user_followers, name='u1f')
        user2_followers = aliased(user_followers, name='u2f')
        
        return self.db.query(AdvancedUser).join(
            user1_followers, AdvancedUser.id == user1_followers.c.follower_id
        ).join(
            user2_followers, AdvancedUser.id == user2_followers.c.follower_id
        ).filter(
            and_(
                user1_followers.c.followed_id == user1_id,
                user2_followers.c.followed_id == user2_id
            )
        ).all()
    
    def get_products_with_price_categories(self):
        """Categorize products by price ranges"""
        return self.db.query(
            Product,
            case(
                (Product.price_dollars < 10, 'Cheap'),
                (Product.price_dollars < 50, 'Moderate'),
                else_='Expensive'
            ).label('price_category')
        ).all()
    
    def get_hierarchical_users(self):
        """Get organizational hierarchy using recursive CTE"""
        # Note: This requires PostgreSQL
        hierarchy_cte = text("""
        WITH RECURSIVE user_hierarchy AS (
            -- Base case: top-level managers
            SELECT id, username, manager_id, 0 as level, username as path
            FROM advanced_users
            WHERE manager_id IS NULL
            
            UNION ALL
            
            -- Recursive case
            SELECT u.id, u.username, u.manager_id, uh.level + 1,
                   uh.path || ' -> ' || u.username
            FROM advanced_users u
            JOIN user_hierarchy uh ON u.manager_id = uh.id
        )
        SELECT * FROM user_hierarchy ORDER BY level, username;
        """)
        
        return self.db.execute(hierarchy_cte).fetchall()
    
    def window_functions_example(self):
        """Demonstrate window functions"""
        return self.db.query(
            Product.name,
            Product.price_dollars,
            func.rank().over(order_by=Product.price_dollars.desc()).label('price_rank'),
            func.dense_rank().over(order_by=Product.price_dollars.desc()).label('price_dense_rank'),
            func.row_number().over(order_by=Product.name).label('row_num'),
            func.lag(Product.price_dollars, 1).over(order_by=Product.price_dollars).label('prev_price'),
            func.lead(Product.price_dollars, 1).over(order_by=Product.price_dollars).label('next_price')
        ).all()
```

## Project 3: Working with Existing Database

### Reflecting Existing Tables
```python
# existing_db.py
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

class ExistingDatabaseHandler:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.metadata = MetaData()
        
    def reflect_all_tables(self):
        """Reflect all tables from existing database"""
        self.metadata.reflect(bind=self.engine)
        return self.metadata.tables.keys()
    
    def get_table_info(self, table_name: str):
        """Get detailed information about a specific table"""
        inspector = inspect(self.engine)
        
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        indexes = inspector.get_indexes(table_name)
        
        return {
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes
        }
    
    def create_automap_classes(self):
        """Create SQLAlchemy models from existing tables"""
        Base = automap_base()
        Base.prepare(self.engine, reflect=True)
        
        # Access tables as classes
        return Base.classes
    
    def manual_table_definition(self, table_name: str):
        """Manually define a table structure"""
        return Table(table_name, self.metadata, autoload_with=self.engine)

# Example usage with existing tables
def work_with_existing_tables():
    handler = ExistingDatabaseHandler("postgresql://user:pass@localhost/existing_db")
    
    # Reflect all tables
    tables = handler.reflect_all_tables()
    print("Available tables:", tables)
    
    # Create automap classes
    classes = handler.create_automap_classes()
    
    # Example: If you have an existing 'customers' table
    if hasattr(classes, 'customers'):
        Customer = classes.customers
        
        # Now you can use it like a normal SQLAlchemy model
        session = sessionmaker(bind=handler.engine)()
        customers = session.query(Customer).all()
        
    # Manual table reflection
    if 'orders' in tables:
        orders_table = handler.manual_table_definition('orders')
        
        # Use with raw SQL
        with handler.engine.connect() as conn:
            result = conn.execute(orders_table.select())
            for row in result:
                print(row)
```

### Migration with Alembic
```python
# alembic configuration
# Run these commands in terminal:

# Initialize Alembic
# alembic init alembic

# alembic/env.py modifications:
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
from models import Base  # Import your models

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## Project 4: Transaction Management

### Advanced Transaction Patterns
```python
# transactions.py
from sqlalchemy.orm import Session
from sqlalchemy import event
from contextlib import contextmanager
import logging

class TransactionManager:
    def __init__(self, session: Session):
        self.session = session
        
    @contextmanager
    def transaction(self):
        """Basic transaction context manager"""
        try:
            yield self.session
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logging.error(f"Transaction failed: {e}")
            raise
        finally:
            self.session.close()
    
    @contextmanager
    def nested_transaction(self):
        """Nested transaction using savepoints"""
        savepoint = self.session.begin_nested()
        try:
            yield self.session
            savepoint.commit()
        except Exception as e:
            savepoint.rollback()
            logging.error(f"Nested transaction failed: {e}")
            raise
    
    def bulk_operations(self, operations: list):
        """Execute multiple operations in a single transaction"""
        try:
            for operation in operations:
                operation(self.session)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise

# Advanced transaction examples
class BankingService:
    def __init__(self, session: Session):
        self.session = session
    
    def transfer_money(self, from_account_id: int, to_account_id: int, amount: float):
        """Money transfer with transaction isolation"""
        with self.session.begin():
            # Lock accounts to prevent concurrent modifications
            from_account = self.session.query(Account).with_for_update().filter(
                Account.id == from_account_id
            ).first()
            
            to_account = self.session.query(Account).with_for_update().filter(
                Account.id == to_account_id
            ).first()
            
            if not from_account or not to_account:
                raise ValueError("Account not found")
            
            if from_account.balance < amount:
                raise ValueError("Insufficient funds")
            
            # Perform the transfer
            from_account.balance -= amount
            to_account.balance += amount
            
            # Log the transaction
            transaction_log = TransactionLog(
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                transaction_type='transfer'
            )
            self.session.add(transaction_log)
    
    def batch_update_with_savepoints(self, updates: list):
        """Batch updates with individual savepoint handling"""
        successful_updates = []
        failed_updates = []
        
        for update in updates:
            with self.session.begin_nested() as savepoint:
                try:
                    # Perform update
                    account = self.session.query(Account).filter(
                        Account.id == update['account_id']
                    ).first()
                    
                    account.balance += update['amount']
                    successful_updates.append(update)
                    
                except Exception as e:
                    savepoint.rollback()
                    failed_updates.append({'update': update, 'error': str(e)})
        
        return successful_updates, failed_updates

# Event-driven transaction handling
@event.listens_for(Session, "before_commit")
def before_commit_handler(session):
    """Execute before commit"""
    logging.info("About to commit transaction")

@event.listens_for(Session, "after_commit")
def after_commit_handler(session):
    """Execute after successful commit"""
    logging.info("Transaction committed successfully")

@event.listens_for(Session, "after_rollback")
def after_rollback_handler(session):
    """Execute after rollback"""
    logging.warning("Transaction rolled back")

# Custom transaction decorator
def transactional(func):
    """Decorator for automatic transaction handling"""
    def wrapper(*args, **kwargs):
        session = kwargs.get('session') or args[0] if args else None
        if not isinstance(session, Session):
            raise ValueError("Session not found in arguments")
        
        try:
            result = func(*args, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            logging.error(f"Transaction failed in {func.__name__}: {e}")
            raise
    return wrapper

@transactional
def create_user_with_profile(session: Session, user_data: dict, profile_data: dict):
    """Example of using transaction decorator"""
    user = User(**user_data)
    session.add(user)
    session.flush()  # Get the user ID without committing
    
    profile = UserProfile(user_id=user.id, **profile_data)
    session.add(profile)
    
    return user
```

### Connection Pooling and Performance
```python
# connection_management.py
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool, StaticPool
import time
import logging

# Advanced engine configuration
def create_optimized_engine(database_url: str):
    return create_engine(
        database_url,
        # Pool settings
        poolclass=QueuePool,
        pool_size=20,              # Number of permanent connections
        max_overflow=30,           # Additional connections beyond pool_size
        pool_pre_ping=True,        # Validate connections before use
        pool_recycle=3600,         # Recycle connections after 1 hour
        
        # Connection settings
        connect_args={
            "connect_timeout": 10,
            "application_name": "sqlalchemy_app",
        },
        
        # Execution settings
        echo=False,                # Set to True for SQL logging
        future=True,              # Use SQLAlchemy 2.0 style
    )

# Connection event handlers for monitoring
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set connection-specific settings"""
    if 'postgresql' in str(dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("SET timezone TO 'UTC'")
        cursor.close()

@event.listens_for(Engine, "checkout")
def checkout_handler(dbapi_connection, connection_record, connection_proxy):
    """Log connection checkout"""
    logging.debug(f"Connection checked out: {id(dbapi_connection)}")

@event.listens_for(Engine, "checkin")
def checkin_handler(dbapi_connection, connection_record):
    """Log connection checkin"""
    logging.debug(f"Connection checked in: {id(dbapi_connection)}")

# Connection retry mechanism
import time
from sqlalchemy.exc import OperationalError

def execute_with_retry(session, statement, max_retries=3, delay=1):
    """Execute statement with retry logic"""
    for attempt in range(max_retries):
        try:
            return session.execute(statement)
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            logging.warning(f"Database operation failed (attempt {attempt + 1}): {e}")
            time.sleep(delay * (2 ** attempt))  # Exponential backoff
```

## Project 5: Advanced Features

### Raw SQL and Hybrid Queries
```python
# raw_sql_queries.py
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from typing import List, Dict, Any

class RawSQLQueries:
    def __init__(self, session: Session):
        self.session = session
    
    def execute_raw_sql(self, query: str, params: dict = None) -> List[Dict]:
        """Execute raw SQL with parameters"""
        result = self.session.execute(text(query), params or {})
        return [dict(row._mapping) for row in result]
    
    def complex_reporting_query(self) -> List[Dict]:
        """Complex reporting query using raw SQL"""
        query = text("""
        WITH monthly_stats AS (
            SELECT 
                DATE_TRUNC('month', created_at) as month,
                COUNT(*) as post_count,
                COUNT(DISTINCT author_id) as unique_authors,
                AVG(CASE WHEN price IS NOT NULL THEN price ELSE 0 END) as avg_price
            FROM posts 
            WHERE created_at >= NOW() - INTERVAL '12 months'
            GROUP BY DATE_TRUNC('month', created_at)
        ),
        category_stats AS (
            SELECT 
                c.name as category_name,
                COUNT(p.id) as post_count,
                AVG(p.price) as avg_price
            FROM categories c
            LEFT JOIN posts p ON c.id = p.category_id
            GROUP BY c.id, c.name
        )
        SELECT 
            ms.month,
            ms.post_count,
            ms.unique_authors,
            ms.avg_price,
            cs.category_name,
            cs.post_count as category_post_count
        FROM monthly_stats ms
        CROSS JOIN category_stats cs
        ORDER BY ms.month DESC, cs.post_count DESC;
        """)
        
        return self.execute_raw_sql(query)
    
    def stored_procedure_call(self, procedure_name: str, *args):
        """Call stored procedure"""
        placeholders = ', '.join([':arg' + str(i) for i in range(len(args))])
        query = text(f"CALL {procedure_name}({placeholders})")
        params = {f'arg{i}': arg for i, arg in enumerate(args)}
        
        return self.session.execute(query, params)
    
    def bulk_upsert(self, table_name: str, records: List[Dict]):
        """PostgreSQL UPSERT operation"""
        if not records:
            return
        
        columns = list(records[0].keys())
        values_placeholder = ', '.join([f":{col}" for col in columns])
        conflict_columns = ['id']  # Assuming id is the conflict column
        
        update_clause = ', '.join([
            f"{col} = EXCLUDED.{col}" for col in columns if col not in conflict_columns
        ])
        
        query = text(f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({values_placeholder})
        ON CONFLICT ({', '.join(conflict_columns)})
        DO UPDATE SET {update_clause}
        """)
        
        self.session.execute(query, records)
        self.session.commit()

# Full-text search implementation
class FullTextSearch:
    def __init__(self, session: Session):
        self.session = session
    
    def setup_full_text_search(self):
        """Set up PostgreSQL full-text search"""
        setup_queries = [
            # Add tsvector column
            text("ALTER TABLE posts ADD COLUMN IF NOT EXISTS search_vector tsvector;"),
            
            # Create index
            text("CREATE INDEX IF NOT EXISTS posts_search_idx ON posts USING GIN(search_vector);"),
            
            # Create trigger to update search_vector
            text("""
            CREATE OR REPLACE FUNCTION posts_search_trigger() RETURNS trigger AS $$
            BEGIN
                NEW.search_vector := to_tsvector('english', 
                    COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.content, '')
                );
                RETURN NEW;
            END
            $$ LANGUAGE plpgsql;
            """),
            
            text("""
            DROP TRIGGER IF EXISTS posts_search_update ON posts;
            CREATE TRIGGER posts_search_update 
                BEFORE INSERT OR UPDATE ON posts
                FOR EACH ROW EXECUTE FUNCTION posts_search_trigger();
            """),
        ]
        
        for query in setup_queries:
            self.session.execute(query)
        self.session.commit()
    
    def search_posts(self, search_term: str, limit: int = 10):
        """Full-text search with ranking"""
        query = text("""
        SELECT p.*, ts_rank(p.search_vector, plainto_tsquery(:search_term)) as rank
        FROM posts p
        WHERE p.search_vector @@ plainto_tsquery(:search_term)
        ORDER BY rank DESC
        LIMIT :limit;
        """)
        
        return self.execute_raw_sql(query, {
            'search_term': search_term,
            'limit': limit
        })

# Custom SQL functions and aggregates
from sqlalchemy.sql import functions

class CustomSQLFunctions:
    @staticmethod
    def levenshtein_distance(str1, str2):
        """Custom PostgreSQL function for string similarity"""
        return func.levenshtein(str1, str2)
    
    @staticmethod
    def json_extract_path(json_column, *path_elements):
        """Extract path from JSON column"""
        return func.json_extract_path_text(json_column, *path_elements)
    
    @staticmethod
    def array_length(array_column):
        """Get array length in PostgreSQL"""
        return func.array_length(array_column, 1)

# Materialized views management
class MaterializedViewManager:
    def __init__(self, session: Session):
        self.session = session
    
    def create_user_stats_view(self):
        """Create materialized view for user statistics"""
        query = text("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS user_stats_mv AS
        SELECT 
            u.id,
            u.username,
            COUNT(p.id) as post_count,
            AVG(p.price) as avg_post_price,
            MIN(p.created_at) as first_post_date,
            MAX(p.created_at) as last_post_date
        FROM users u
        LEFT JOIN posts p ON u.id = p.author_id
        GROUP BY u.id, u.username;
        
        CREATE UNIQUE INDEX IF NOT EXISTS user_stats_mv_id_idx ON user_stats_mv(id);
        """)
        
        self.session.execute(query)
        self.session.commit()
    
    def refresh_materialized_view(self, view_name: str):
        """Refresh materialized view"""
        query = text(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view_name};")
        self.session.execute(query)
        self.session.commit()
```

### Async SQLAlchemy
```python
# async_operations.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload, joinedload
from database import async_engine
from models import User, Post

AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

class AsyncUserCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_user(self, username: str, email: str, full_name: str) -> User:
        """Async user creation"""
        user = User(username=username, email=email, full_name=full_name)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_user_with_posts(self, user_id: int) -> User:
        """Get user with posts using async"""
        stmt = select(User).options(selectinload(User.posts)).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_users_paginated(self, offset: int = 0, limit: int = 10):
        """Async pagination"""
        stmt = select(User).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
    
    async def bulk_update_users(self, updates: list):
        """Async bulk operations"""
        for update_data in updates:
            stmt = update(User).where(User.id == update_data['id']).values(
                **{k: v for k, v in update_data.items() if k != 'id'}
            )
            await self.session.execute(stmt)
        await self.session.commit()
    
    async def search_users_async(self, query: str):
        """Async search with complex conditions"""
        stmt = select(User).where(
            User.username.ilike(f"%{query}%") | 
            User.email.ilike(f"%{query}%") |
            User.full_name.ilike(f"%{query}%")
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

# Async context manager for database operations
class AsyncDatabaseManager:
    @classmethod
    async def get_session(cls):
        """Get async session"""
        async with AsyncSessionLocal() as session:
            yield session
    
    @classmethod
    async def execute_in_transaction(cls, operations):
        """Execute multiple operations in a transaction"""
        async with AsyncSessionLocal() as session:
            try:
                results = []
                for operation in operations:
                    result = await operation(session)
                    results.append(result)
                await session.commit()
                return results
            except Exception as e:
                await session.rollback()
                raise e

# Example usage
async def main():
    async with AsyncSessionLocal() as session:
        crud = AsyncUserCRUD(session)
        
        # Create user
        user = await crud.create_user("async_user", "async@example.com", "Async User")
        print(f"Created user: {user.id}")
        
        # Get user with posts
        user_with_posts = await crud.get_user_with_posts(user.id)
        print(f"User posts count: {len(user_with_posts.posts) if user_with_posts else 0}")
        
        # Bulk operations
        await crud.bulk_update_users([
            {'id': user.id, 'full_name': 'Updated Async User'}
        ])

if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Strategies

### Comprehensive Testing Setup
```python
# test_models.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from models import User, Post, Category, Tag
from crud import UserCRUD, PostCRUD

# Test database setup
@pytest.fixture(scope="session")
def engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True
    )

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# Test fixtures
@pytest.fixture
def sample_user(db_session):
    user = User(username="testuser", email="test@example.com", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def sample_category(db_session):
    category = Category(name="Test Category", description="Test Description")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

# CRUD Tests
class TestUserCRUD:
    def test_create_user(self, db_session):
        crud = UserCRUD(db_session)
        user = crud.create_user("newuser", "new@example.com", "New User")
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.is_active is True
    
    def test_create_user_duplicate_username(self, db_session, sample_user):
        crud = UserCRUD(db_session)
        
        with pytest.raises(ValueError):
            crud.create_user(sample_user.username, "another@example.com", "Another User")
    
    def test_get_user(self, db_session, sample_user):
        crud = UserCRUD(db_session)
        retrieved_user = crud.get_user(sample_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == sample_user.id
        assert retrieved_user.username == sample_user.username
    
    def test_update_user(self, db_session, sample_user):
        crud = UserCRUD(db_session)
        updated_user = crud.update_user(sample_user.id, full_name="Updated Name")
        
        assert updated_user.full_name == "Updated Name"
        assert updated_user.username == sample_user.username  # Unchanged
    
    def test_delete_user(self, db_session, sample_user):
        crud = UserCRUD(db_session)
        result = crud.delete_user(sample_user.id)
        
        assert result is True
        assert crud.get_user(sample_user.id) is None
    
    def test_search_users(self, db_session):
        crud = UserCRUD(db_session)
        
        # Create test users
        crud.create_user("john_doe", "john@example.com", "John Doe")
        crud.create_user("jane_smith", "jane@example.com", "Jane Smith")
        crud.create_user("bob_johnson", "bob@example.com", "Bob Johnson")
        
        # Search by username
        results = crud.search_users("john")
        assert len(results) == 2  # john_doe and bob_johnson
        
        # Search by email domain
        results = crud.search_users("example.com")
        assert len(results) == 3
        
        # Search by full name
        results = crud.search_users("Jane")
        assert len(results) == 1
        assert results[0].full_name == "Jane Smith"

class TestPostCRUD:
    def test_create_post_with_tags(self, db_session, sample_user, sample_category):
        crud = PostCRUD(db_session)
        post = crud.create_post(
            title="Test Post",
            content="Test content",
            author_id=sample_user.id,
            category_id=sample_category.id,
            tag_names=["python", "sqlalchemy", "testing"]
        )
        
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.author_id == sample_user.id
        assert len(post.tags) == 3
        assert "python" in [tag.name for tag in post.tags]
    
    def test_get_posts_with_filters(self, db_session, sample_user, sample_category):
        crud = PostCRUD(db_session)
        
        # Create test posts
        post1 = crud.create_post("Post 1", "Content 1", sample_user.id, sample_category.id)
        post2 = crud.create_post("Post 2", "Content 2", sample_user.id, tag_names=["python"])
        
        # Filter by author
        posts = crud.get_posts_with_filters(author_id=sample_user.id)
        assert len(posts) == 2
        
        # Filter by category
        posts = crud.get_posts_with_filters(category_id=sample_category.id)
        assert len(posts) == 1
        assert posts[0].id == post1.id
        
        # Filter by tag
        posts = crud.get_posts_with_filters(tag_name="python")
        assert len(posts) == 1
        assert posts[0].id == post2.id

# Integration Tests
class TestIntegration:
    def test_user_with_posts_and_profile(self, db_session):
        # Create user
        user_crud = UserCRUD(db_session)
        user = user_crud.create_user("integration_user", "int@example.com", "Integration User")
        
        # Create posts
        post_crud = PostCRUD(db_session)
        post1 = post_crud.create_post("Post 1", "Content 1", user.id)
        post2 = post_crud.create_post("Post 2", "Content 2", user.id)
        
        # Verify relationships
        retrieved_user = user_crud.get_user(user.id)
        assert len(retrieved_user.posts) == 2
        assert retrieved_user.posts[0].author.username == "integration_user"

# Performance Tests
class TestPerformance:
    def test_bulk_create_performance(self, db_session):
        """Test bulk creation performance"""
        import time
        
        start_time = time.time()
        
        users = []
        for i in range(1000):
            user = User(
                username=f"user_{i}",
                email=f"user_{i}@example.com",
                full_name=f"User {i}"
            )
            users.append(user)
        
        db_session.add_all(users)
        db_session.commit()
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Created 1000 users in {execution_time:.2f} seconds")
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert db_session.query(User).count() == 1000

# Run tests with: pytest test_models.py -v
```

## Best Practices

### Configuration and Environment Management
```python
# config.py
import os
from typing import Optional
from pydantic import BaseSettings, validator

class DatabaseSettings(BaseSettings):
    database_url: str
    database_url_async: Optional[str] = None
    echo_sql: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    
    @validator('database_url_async', pre=True, always=True)
    def set_async_url(cls, v, values):
        if not v:
            sync_url = values.get('database_url', '')
            if sync_url.startswith('postgresql://'):
                return sync_url.replace('postgresql://', 'postgresql+asyncpg://')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False

class ApplicationSettings(BaseSettings):
    app_name: str = "SQLAlchemy Learning API"
    debug: bool = False
    testing: bool = False
    
    # Database settings
    db: DatabaseSettings = DatabaseSettings()
    
    # Redis settings (for caching)
    redis_url: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = ApplicationSettings()
```

### Logging and Monitoring
```python
# logging_config.py
import logging
import time
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# SQL query timing
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()
    logger.debug(f"Start Query: {statement[:100]}...")

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    logger.info(f"Query completed in {total:.4f}s")
    
    # Log slow queries
    if total > 1.0:  # Queries taking more than 1 second
        logger.warning(f"Slow query detected: {total:.4f}s - {statement[:200]}...")

# Connection pool monitoring
@event.listens_for(Engine, "connect")
def connect(dbapi_conn, connection_record):
    logger.info(f"New database connection established")

@event.listens_for(Engine, "checkout")
def checkout(dbapi_conn, connection_record, connection_proxy):
    logger.debug(f"Connection checked out from pool")

@event.listens_for(Engine, "checkin")
def checkin(dbapi_conn, connection_record):
    logger.debug(f"Connection returned to pool")
```

### Security Best Practices
```python
# security.py
from sqlalchemy import text
from sqlalchemy.orm import Session
import hashlib
import secrets

class SecurityManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{hashed.hex()}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = hashed.split(':')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return new_hash.hex() == hash_value
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_sql_input(input_string: str) -> str:
        """Basic SQL injection prevention"""
        dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
        for char in dangerous_chars:
            input_string = input_string.replace(char, '')
        return input_string
    
    @staticmethod
    def safe_query_execution(session: Session, query: str, params: dict):
        """Execute query with parameter binding"""
        # Always use parameterized queries
        return session.execute(text(query), params)

# Row Level Security example (PostgreSQL)
def setup_row_level_security(session: Session):
    """Set up row-level security policies"""
    policies = [
        # Enable RLS on users table
        text("ALTER TABLE users ENABLE ROW LEVEL SECURITY;"),
        
        # Create policy for users to only see their own data
        text("""
        CREATE POLICY user_self_policy ON users
        FOR ALL
        TO application_role
        USING (id = current_setting('app.current_user_id')::INTEGER);
        """),
        
        # Create policy for posts
        text("""
        CREATE POLICY post_owner_policy ON posts
        FOR ALL
        TO application_role
        USING (author_id = current_setting('app.current_user_id')::INTEGER);
        """),
    ]
    
    for policy in policies:
        try:
            session.execute(policy)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Policy creation failed: {e}")
```

## Running the Projects

### Terminal Commands

```bash
# 1. Set up the environment
python -m venv sqlalchemy_env
source sqlalchemy_env/bin/activate  # On Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up PostgreSQL database
createdb sqlalchemy_db

# 4. Initialize Alembic migrations
alembic init alembic

# 5. Create first migration
alembic revision --autogenerate -m "Initial migration"

# 6. Apply migrations
alembic upgrade head

# 7. Run the FastAPI application
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 8. Run tests
pytest -v

# 9. Check test coverage
pytest --cov=. --cov-report=html

# 10. Load sample data (create a script)
python load_sample_data.py
```

### Requirements File
```txt
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
fastapi>=0.68.0
uvicorn>=0.15.0
python-dotenv>=0.19.0
alembic>=1.7.0
pytest>=6.2.0
pytest-asyncio>=0.15.0
pytest-cov>=2.12.0
pydantic>=1.8.0
asyncpg>=0.24.0
redis>=3.5.0
```

This comprehensive guide covers all major SQLAlchemy concepts through practical projects. Each section builds upon the previous one, ensuring you learn progressively while building real-world applications. The projects include modern async support, comprehensive testing, and