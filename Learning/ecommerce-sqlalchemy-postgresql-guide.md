# Complete SQLAlchemy & PostgreSQL Guide: Ecommerce Applications
## Monolithic vs Microservice Architectures

This comprehensive guide demonstrates all SQLAlchemy and PostgreSQL concepts through practical ecommerce applications. We'll build the same ecommerce system using both monolithic and microservice architectures to understand the trade-offs and implementation differences.

## Table of Contents

1. [Overview & Architecture Comparison](#1-overview--architecture-comparison)
2. [Database Design & PostgreSQL Setup](#2-database-design--postgresql-setup)
3. [Monolithic Ecommerce Application](#3-monolithic-ecommerce-application)
4. [Microservice Ecommerce Application](#4-microservice-ecommerce-application)
5. [Advanced SQLAlchemy Concepts](#5-advanced-sqlalchemy-concepts)
6. [PostgreSQL Advanced Features](#6-postgresql-advanced-features)
7. [Performance & Optimization](#7-performance--optimization)
8. [Testing Strategies](#8-testing-strategies)
9. [Deployment & DevOps](#9-deployment--devops)
10. [Best Practices & Patterns](#10-best-practices--patterns)

---

## 1. Overview & Architecture Comparison

### 1.1 Ecommerce Domain Overview

Our ecommerce system will include:
- **User Management**: Customers, vendors, administrators
- **Product Catalog**: Products, categories, variants, inventory
- **Shopping**: Cart, wishlist, recommendations
- **Orders**: Order processing, payment, fulfillment
- **Reviews**: Product reviews and ratings
- **Analytics**: Sales reports, user behavior tracking

### 1.2 Architecture Comparison

#### Monolithic Architecture
```
┌─────────────────────────────────────┐
│           Web Application           │
├─────────────────────────────────────┤
│  Controllers (FastAPI/Flask)        │
├─────────────────────────────────────┤
│  Business Logic Services            │
├─────────────────────────────────────┤
│  Data Access Layer (SQLAlchemy)     │
├─────────────────────────────────────┤
│        Single PostgreSQL DB         │
└─────────────────────────────────────┘
```

**Pros:**
- Simple deployment and testing
- Strong consistency through ACID transactions
- Easy to develop initially
- Simple debugging and monitoring

**Cons:**
- Single point of failure
- Difficult to scale individual components
- Technology stack lock-in
- Large codebase becomes hard to maintain

#### Microservice Architecture
```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ User Service │ │Product Service│ │Order Service │ │Payment Service│
│              │ │              │ │              │ │              │
│ PostgreSQL   │ │ PostgreSQL   │ │ PostgreSQL   │ │ PostgreSQL   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
        │                │                │                │
        └────────────────┼────────────────┼────────────────┘
                         │                │
              ┌──────────────────────────────────┐
              │        API Gateway               │
              └──────────────────────────────────┘
```

**Pros:**
- Independent scalability
- Technology diversity
- Fault isolation
- Team autonomy

**Cons:**
- Distributed system complexity
- Network latency
- Data consistency challenges
- Increased operational overhead

---

## 2. Database Design & PostgreSQL Setup

### 2.1 Environment Setup

**docker-compose.yml** - PostgreSQL Setup:
```yaml
version: '3.8'

services:
  # Main PostgreSQL for monolithic app
  postgres_monolith:
    image: postgres:15
    container_name: ecommerce_monolith_db
    environment:
      POSTGRES_DB: ecommerce_monolith
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_monolith_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c pg_stat_statements.track=all
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c work_mem=4MB

  # Microservice databases
  postgres_users:
    image: postgres:15
    container_name: ecommerce_users_db
    environment:
      POSTGRES_DB: ecommerce_users
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5433:5432"
    volumes:
      - postgres_users_data:/var/lib/postgresql/data

  postgres_products:
    image: postgres:15
    container_name: ecommerce_products_db
    environment:
      POSTGRES_DB: ecommerce_products
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5434:5432"
    volumes:
      - postgres_products_data:/var/lib/postgresql/data

  postgres_orders:
    image: postgres:15
    container_name: ecommerce_orders_db
    environment:
      POSTGRES_DB: ecommerce_orders
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5435:5432"
    volumes:
      - postgres_orders_data:/var/lib/postgresql/data

  postgres_payments:
    image: postgres:15
    container_name: ecommerce_payments_db
    environment:
      POSTGRES_DB: ecommerce_payments
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5436:5432"
    volumes:
      - postgres_payments_data:/var/lib/postgresql/data

  # Redis for caching and sessions
  redis:
    image: redis:7-alpine
    container_name: ecommerce_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # Message broker for microservices
  rabbitmq:
    image: rabbitmq:3-management
    container_name: ecommerce_rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: password
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

volumes:
  postgres_monolith_data:
  postgres_users_data:
  postgres_products_data:
  postgres_orders_data:
  postgres_payments_data:
  redis_data:
  rabbitmq_data:
```

**init-scripts/init.sql** - PostgreSQL Extensions and Initial Setup:
```sql
-- Extensions for advanced PostgreSQL features
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "hstore";

-- Custom types
CREATE TYPE order_status AS ENUM (
    'pending', 'confirmed', 'processing', 'shipped', 
    'delivered', 'cancelled', 'refunded'
);

CREATE TYPE payment_status AS ENUM (
    'pending', 'authorized', 'captured', 'failed', 
    'cancelled', 'refunded', 'partially_refunded'
);

CREATE TYPE user_role AS ENUM ('customer', 'vendor', 'admin', 'support');

CREATE TYPE product_status AS ENUM ('draft', 'active', 'inactive', 'discontinued');

-- Functions for common operations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to generate SKUs
CREATE OR REPLACE FUNCTION generate_sku()
RETURNS TEXT AS $$
BEGIN
    RETURN 'SKU-' || UPPER(substring(md5(random()::text) from 1 for 8));
END;
$$ LANGUAGE plpgsql;
```

### 2.2 Common Configuration

**requirements.txt**:
```txt
# Core frameworks
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Database & Caching
redis==5.0.1
celery==5.3.4

# HTTP & API
httpx==0.25.2
requests==2.31.0

# Data validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
factory-boy==3.3.0

# Development
black==23.11.0
isort==5.12.0
mypy==1.7.1

# Monitoring
prometheus-client==0.19.0
```

**shared/config.py** - Configuration Management:
```python
"""
Shared configuration for both monolithic and microservice architectures.
Demonstrates SQLAlchemy configuration patterns and PostgreSQL connection management.
"""
from functools import lru_cache
from typing import Optional, Dict, Any
import os
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator


class DatabaseConfig(BaseSettings):
    """Database configuration with connection pooling and performance settings."""
    
    # Connection settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "ecommerce_monolith"
    POSTGRES_PORT: int = 5432
    
    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    # Connection pool settings
    POOL_SIZE: int = 20
    MAX_OVERFLOW: int = 30
    POOL_PRE_PING: bool = True
    POOL_RECYCLE: int = 3600  # 1 hour
    
    # Query settings
    ECHO_SQL: bool = False
    QUERY_TIMEOUT: int = 30
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=str(values.get("POSTGRES_PORT")),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


class RedisConfig(BaseSettings):
    """Redis configuration for caching and sessions."""
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    CACHE_TTL: int = 3600  # 1 hour default
    SESSION_TTL: int = 86400  # 24 hours

    class Config:
        env_file = ".env"


class SecurityConfig(BaseSettings):
    """Security and authentication configuration."""
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Password policy
    MIN_PASSWORD_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGITS: bool = True
    REQUIRE_SYMBOLS: bool = False

    class Config:
        env_file = ".env"


class AppConfig(BaseSettings):
    """Main application configuration."""
    APP_NAME: str = "Ecommerce Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File uploads
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    
    # Email settings
    EMAIL_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"


# Microservice-specific configurations
class MicroserviceConfig(BaseSettings):
    """Configuration for microservice communication."""
    SERVICE_NAME: str
    SERVICE_PORT: int
    
    # Service discovery
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    
    # Message broker
    RABBITMQ_URL: str = "amqp://admin:password@localhost:5672/"
    
    # Health check
    HEALTH_CHECK_INTERVAL: int = 30
    
    # Tracing
    JAEGER_ENABLED: bool = False
    JAEGER_HOST: str = "localhost"
    JAEGER_PORT: int = 14268

    class Config:
        env_file = ".env"


@lru_cache()
def get_database_config() -> DatabaseConfig:
    return DatabaseConfig()


@lru_cache()
def get_redis_config() -> RedisConfig:
    return RedisConfig()


@lru_cache()
def get_security_config() -> SecurityConfig:
    return SecurityConfig()


@lru_cache()
def get_app_config() -> AppConfig:
    return AppConfig()


def get_microservice_config(service_name: str, port: int) -> MicroserviceConfig:
    return MicroserviceConfig(SERVICE_NAME=service_name, SERVICE_PORT=port)
```

---

## 3. Monolithic Ecommerce Application

### 3.1 Database Models

**monolithic/models/base.py** - Base Model with Advanced Features:
```python
"""
Base model classes demonstrating advanced SQLAlchemy patterns.
Includes audit trails, soft deletes, and performance optimizations.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy import (
    Column, DateTime, String, Boolean, Text, Integer, 
    event, Index, text, MetaData
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session
from sqlalchemy.sql import func


# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
Base = declarative_base(metadata=metadata)


class TimestampMixin:
    """Mixin for automatic timestamp management."""
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )


class UUIDMixin:
    """Mixin for UUID primary keys."""
    
    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
            server_default=text("uuid_generate_v4()")
        )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    
    @hybrid_property
    def is_active(self):
        return not self.is_deleted
    
    def soft_delete(self):
        """Soft delete the record."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class AuditMixin:
    """Mixin for audit trail functionality."""
    
    created_by_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    updated_by_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Store additional audit information as JSON
    audit_info = Column(JSONB, nullable=True)
    
    def set_audit_info(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Set audit information for the record."""
        self.audit_info = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": str(user_id),
            "details": details or {}
        }


class VersionMixin:
    """Mixin for optimistic locking."""
    
    version = Column(Integer, nullable=False, default=1, server_default="1")


class BaseModel(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """
    Base model class with all common functionality.
    Demonstrates SQLAlchemy best practices and PostgreSQL features.
    """
    __abstract__ = True
    
    def to_dict(self, exclude_fields: Optional[list] = None) -> Dict[str, Any]:
        """Convert model to dictionary."""
        exclude_fields = exclude_fields or []
        exclude_fields.extend(['_sa_instance_state'])
        
        result = {}
        for column in self.__table__.columns:
            if column.name not in exclude_fields:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    value = value.isoformat()
                result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any], exclude_fields: Optional[list] = None):
        """Update model from dictionary."""
        exclude_fields = exclude_fields or ['id', 'created_at', 'version']
        
        for key, value in data.items():
            if key not in exclude_fields and hasattr(self, key):
                setattr(self, key, value)
    
    @classmethod
    def get_active_query(cls, session: Session):
        """Get query for active (non-deleted) records."""
        return session.query(cls).filter(cls.is_deleted == False)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# Event listeners for automatic audit trail
@event.listens_for(BaseModel, 'before_insert', propagate=True)
def receive_before_insert(mapper, connection, target):
    """Set audit info on insert."""
    if hasattr(target, 'set_audit_info'):
        # In a real app, you'd get user_id from the current context
        target.set_audit_info("system", "create")


@event.listens_for(BaseModel, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Set audit info on update."""
    if hasattr(target, 'set_audit_info'):
        # In a real app, you'd get user_id from the current context
        target.set_audit_info("system", "update")


# Index for common queries
Index('ix_base_model_active_created', BaseModel.is_deleted, BaseModel.created_at)
```

**monolithic/models/user.py** - User Management Models:
```python
"""
User management models demonstrating SQLAlchemy relationships and PostgreSQL features.
Includes customers, vendors, roles, and authentication.
"""
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import (
    Column, String, Boolean, DateTime, Text, Integer, 
    ForeignKey, Table, Enum, Index, CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import enum

from .base import BaseModel


class UserRole(str, enum.Enum):
    """User role enumeration."""
    CUSTOMER = "customer"
    VENDOR = "vendor"
    ADMIN = "admin"
    SUPPORT = "support"


class UserStatus(str, enum.Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


# Association table for user roles (many-to-many)
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now()),
    Column('assigned_by_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Index('ix_user_roles_user_role', 'user_id', 'role_id'),
)


class Role(BaseModel):
    """Role model for RBAC (Role-Based Access Control)."""
    
    __tablename__ = 'roles'
    
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    permissions = Column(JSONB, nullable=False, default=list)
    is_system_role = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    
    __table_args__ = (
        Index('ix_roles_name', 'name'),
        CheckConstraint('char_length(name) >= 2', name='ck_role_name_length'),
    )


class User(BaseModel):
    """
    User model demonstrating advanced SQLAlchemy features:
    - Polymorphic inheritance (Customer/Vendor)
    - Complex relationships
    - Hybrid properties
    - PostgreSQL-specific features
    """
    
    __tablename__ = 'users'
    
    # Basic information
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(DateTime(timezone=True))
    
    # Account status
    status = Column(
        Enum(UserStatus, name='user_status'),
        nullable=False,
        default=UserStatus.PENDING_VERIFICATION,
        index=True
    )
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Security
    last_login_at = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Preferences and metadata
    preferences = Column(JSONB, default=dict)
    metadata_info = Column(JSONB, default=dict)
    timezone = Column(String(50), default='UTC')
    language = Column(String(10), default='en')
    
    # Polymorphic identity for inheritance
    user_type = Column(String(20), nullable=False, index=True)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    login_sessions = relationship("LoginSession", back_populates="user", cascade="all, delete-orphan")
    
    # Polymorphic configuration
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type,
        'with_polymorphic': '*'
    }
    
    __table_args__ = (
        CheckConstraint('char_length(email) >= 5', name='ck_user_email_length'),
        CheckConstraint('char_length(username) >= 3', name='ck_user_username_length'),
        CheckConstraint('char_length(first_name) >= 1', name='ck_user_first_name_length'),
        CheckConstraint('char_length(last_name) >= 1', name='ck_user_last_name_length'),
        Index('ix_users_name', 'first_name', 'last_name'),
        Index('ix_users_status_type', 'status', 'user_type'),
    )
    
    @hybrid_property
    def full_name(self):
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_property
    def is_active(self):
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @hybrid_property
    def is_locked(self):
        """Check if user account is locked."""
        return (self.locked_until and 
                self.locked_until > datetime.utcnow())
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def get_permissions(self) -> List[str]:
        """Get all permissions for the user."""
        permissions = set()
        for role in self.roles:
            permissions.update(role.permissions)
        return list(permissions)
    
    def lock_account(self, duration_minutes: int = 30):
        """Lock user account for specified duration."""
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        self.failed_login_attempts = 0
    
    def unlock_account(self):
        """Unlock user account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    @validates('email')
    def validate_email(self, key, address):
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, address):
            raise ValueError("Invalid email format")
        return address.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        """Validate username format."""
        import re
        if not re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
            raise ValueError("Username must be 3-50 characters and contain only letters, numbers, and underscores")
        return username.lower()


class Customer(User):
    """Customer model extending User with customer-specific fields."""
    
    __tablename__ = 'customers'
    
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    
    # Customer-specific fields
    customer_since = Column(DateTime(timezone=True), server_default=func.now())
    total_orders = Column(Integer, default=0, nullable=False)
    total_spent = Column(Integer, default=0, nullable=False)  # Amount in cents
    loyalty_points = Column(Integer, default=0, nullable=False)
    customer_tier = Column(String(20), default='bronze')  # bronze, silver, gold, platinum
    
    # Marketing preferences
    email_marketing_consent = Column(Boolean, default=False)
    sms_marketing_consent = Column(Boolean, default=False)
    
    # Relationships
    orders = relationship("Order", back_populates="customer")
    cart_items = relationship("CartItem", back_populates="customer")
    wishlists = relationship("Wishlist", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    
    __mapper_args__ = {
        'polymorphic_identity': 'customer',
    }
    
    @hybrid_property
    def average_order_value(self):
        """Calculate average order value."""
        if self.total_orders == 0:
            return 0
        return self.total_spent / self.total_orders


class Vendor(User):
    """Vendor model extending User with vendor-specific fields."""
    
    __tablename__ = 'vendors'
    
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    
    # Business information
    business_name = Column(String(255), nullable=False)
    business_description = Column(Text)
    business_registration_number = Column(String(100))
    tax_id = Column(String(50))
    
    # Vendor status and verification
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_date = Column(DateTime(timezone=True))
    verification_documents = Column(JSONB, default=list)
    
    # Performance metrics
    rating = Column(Integer, default=0)  # 0-5 stars * 100 (e.g., 450 = 4.5 stars)
    total_reviews = Column(Integer, default=0, nullable=False)
    total_sales = Column(Integer, default=0, nullable=False)  # Amount in cents
    
    # Store settings
    store_settings = Column(JSONB, default=dict)
    
    # Relationships
    products = relationship("Product", back_populates="vendor")
    
    __mapper_args__ = {
        'polymorphic_identity': 'vendor',
    }
    
    __table_args__ = (
        Index('ix_vendors_business_name', 'business_name'),
        Index('ix_vendors_verified', 'is_verified'),
        CheckConstraint('rating >= 0 AND rating <= 500', name='ck_vendor_rating_range'),
    )
    
    @hybrid_property
    def average_rating(self):
        """Get average rating as float."""
        return self.rating / 100.0 if self.rating else 0.0


class Address(BaseModel):
    """Address model with geocoding and validation."""
    
    __tablename__ = 'addresses'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Address components
    label = Column(String(50))  # e.g., "Home", "Work", "Billing"
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company = Column(String(255))
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state_province = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    
    # Geocoding information
    latitude = Column(String(50))
    longitude = Column(String(50))
    
    # Address metadata
    is_default = Column(Boolean, default=False, nullable=False)
    is_billing_default = Column(Boolean, default=False, nullable=False)
    is_shipping_default = Column(Boolean, default=False, nullable=False)
    delivery_instructions = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    
    __table_args__ = (
        Index('ix_addresses_user_id', 'user_id'),
        Index('ix_addresses_user_defaults', 'user_id', 'is_default'),
        CheckConstraint('char_length(postal_code) >= 3', name='ck_address_postal_code'),
    )
    
    @hybrid_property
    def full_address(self):
        """Get formatted full address."""
        lines = [self.address_line_1]
        if self.address_line_2:
            lines.append(self.address_line_2)
        lines.append(f"{self.city}, {self.state_province} {self.postal_code}")
        lines.append(self.country)
        return "\n".join(lines)


class LoginSession(BaseModel):
    """Track user login sessions for security monitoring."""
    
    __tablename__ = 'login_sessions'
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Session information
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(INET)
    user_agent = Column(Text)
    device_info = Column(JSONB, default=dict)
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Location information (from IP)
    country = Column(String(100))
    city = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="login_sessions")
    
    __table_args__ = (
        Index('ix_login_sessions_user_active', 'user_id', 'is_active'),
        Index('ix_login_sessions_expires', 'expires_at'),
    )
    
    @hybrid_property
    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
    
    def extend_session(self, hours: int = 24):
        """Extend session expiry."""
        self.expires_at = datetime.utcnow() + timedelta(hours=hours)
        self.last_activity_at = datetime.utcnow()
    
    def terminate(self):
        """Terminate the session."""
        self.is_active = False
```

**monolithic/models/product.py** - Product Catalog Models:
```python
"""
Product catalog models demonstrating complex relationships, 
inheritance, and PostgreSQL advanced features.
"""
from decimal import Decimal
from typing import List, Optional, Dict, Any
import enum

from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Boolean, 
    ForeignKey, DateTime, Table, Enum, Index, 
    CheckConstraint, UniqueConstraint, event
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, TSVECTOR
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from .base import BaseModel


class ProductStatus(str, enum.Enum):
    """Product status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class InventoryStatus(str, enum.Enum):
    """Inventory status enumeration."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    BACKORDER = "backorder"
    DISCONTINUED = "discontinued"


# Association tables for many-to-many relationships
product_categories = Table(
    'product_categories',
    BaseModel.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True),
    Column('category_id', UUID(as_uuid=True), ForeignKey('categories.id'), primary_key=True),
    Index('ix_product_categories_product', 'product_id'),
    Index('ix_product_categories_category', 'category_id'),
)

product_tags = Table(
    'product_tags',
    BaseModel.metadata,
    Column('product_id', UUID(as_uuid=True), ForeignKey('products.id'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True),
)


class Category(BaseModel):
    """
    Hierarchical category model using adjacency list pattern.
    Demonstrates recursive relationships and tree structures.
    """
    
    __tablename__ = 'categories'
    
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), index=True)
    level = Column(Integer, default=0, nullable=False, index=True)
    path = Column(String(500), index=True)  # Materialized path like /electronics/computers/laptops
    
    # Display and SEO
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    meta_title = Column(String(255))
    meta_description = Column(Text)
    
    # Category image and settings
    image_url = Column(String(500))
    banner_url = Column(String(500))
    settings = Column(JSONB, default=dict)
    
    # Search
    search_vector = Column(TSVECTOR)
    
    # Relationships
    parent = relationship("Category", remote_side="Category.id", back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")
    products = relationship("Product", secondary=product_categories, back_populates="categories")
    
    __table_args__ = (
        Index('ix_categories_parent_order', 'parent_id', 'display_order'),
        Index('ix_categories_path', 'path'),
        Index('ix_categories_search', 'search_vector', postgresql_using='gin'),
        CheckConstraint('level >= 0', name='ck_category_level_positive'),
        CheckConstraint('display_order >= 0', name='ck_category_order_positive'),
    )
    
    def get_ancestors(self) -> List['Category']:
        """Get all ancestor categories."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.append(current)
            current = current.parent
        return list(reversed(ancestors))
    
    def get_descendants(self) -> List['Category']:
        """Get all descendant categories (recursive)."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants
    
    @validates('slug')
    def validate_slug(self, key, slug):
        """Validate slug format."""
        import re
        if not re.match(r'^[a-z0-9-]+$', slug):
            raise ValueError("Slug must contain only lowercase letters, numbers, and hyphens")
        return slug


class Tag(BaseModel):
    """Tag model for flexible product categorization."""
    
    __tablename__ = 'tags'
    
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    
    # Relationships
    products = relationship("Product", secondary=product_tags, back_populates="tags")
    
    __table_args__ = (
        CheckConstraint('char_length(name) >= 2', name='ck_tag_name_length'),
    )


class Brand(BaseModel):
    """Brand model for product manufacturers."""
    
    __tablename__ = 'brands'
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    
    # SEO
    meta_title = Column(String(255))
    meta_description = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    products = relationship("Product", back_populates="brand")


class Product(BaseModel):
    """
    Main product model demonstrating advanced SQLAlchemy features:
    - Full-text search with PostgreSQL
    - JSON fields for flexible attributes
    - Complex pricing logic
    - Inventory management
    """
    
    __tablename__ = 'products'
    
    # Basic information
    name = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), nullable=False, unique=True, index=True)
    sku = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    short_description = Column(Text)
    
    # Vendor and brand
    vendor_id = Column(UUID(as_uuid=True), ForeignKey('vendors.id'), nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey('brands.id'), index=True)
    
    # Pricing (stored in cents to avoid floating point issues)
    base_price = Column(Integer, nullable=False)  # Base price in cents
    sale_price = Column(Integer)  # Sale price in cents (optional)
    cost_price = Column(Integer)  # Cost price for margin calculation
    
    # Physical properties
    weight = Column(Numeric(10, 3))  # Weight in kg
    dimensions = Column(JSONB)  # {"length": 10, "width": 5, "height": 3, "unit": "cm"}
    
    # Status and availability
    status = Column(
        Enum(ProductStatus, name='product_status'),
        nullable=False,
        default=ProductStatus.DRAFT,
        index=True
    )
    is_featured = Column(Boolean, default=False, nullable=False, index=True)
    is_digital = Column(Boolean, default=False, nullable=False)
    requires_shipping = Column(Boolean, default=True, nullable=False)
    
    # SEO and marketing
    meta_title = Column(String(255))
    meta_description = Column(Text)
    meta_keywords = Column(ARRAY(String))
    
    # Flexible attributes using JSON
    attributes = Column(JSONB, default=dict)  # Color, size, material, etc.
    specifications = Column(JSONB, default=dict)  # Technical specs
    
    # Search
    search_vector = Column(TSVECTOR)
    
    # Timestamps
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    vendor = relationship("Vendor", back_populates="products")
    brand = relationship("Brand", back_populates="products")
    categories = relationship("Category", secondary=product_categories, back_populates="products")
    tags = relationship("Tag", secondary=product_tags, back_populates="products")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    inventory = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product")
    
    __table_args__ = (
        Index('ix_products_vendor_status', 'vendor_id', 'status'),
        Index('ix_products_price_range', 'base_price', 'sale_price'),
        Index('ix_products_search', 'search_vector', postgresql_using='gin'),
        Index('ix_products_attributes', 'attributes', postgresql_using='gin'),
        CheckConstraint('base_price > 0', name='ck_product_base_price_positive'),
        CheckConstraint('sale_price IS NULL OR sale_price > 0', name='ck_product_sale_price_positive'),
        CheckConstraint('cost_price IS NULL OR cost_price >= 0', name='ck_product_cost_price_positive'),
    )
    
    @hybrid_property
    def current_price(self):
        """Get the current selling price (sale price if available, otherwise base price)."""
        return self.sale_price if self.sale_price else self.base_price
    
    @hybrid_property
    def current_price_decimal(self):
        """Get current price as Decimal for currency formatting."""
        return Decimal(self.current_price) / 100
    
    @hybrid_property
    def is_on_sale(self):
        """Check if product is currently on sale."""
        return self.sale_price is not None and self.sale_price < self.base_price
    
    @hybrid_property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if not self.is_on_sale:
            return 0
        return round(((self.base_price - self.sale_price) / self.base_price) * 100, 2)
    
    def get_primary_category(self):
        """Get the primary (first) category."""
        return self.categories[0] if self.categories else None
    
    def get_attribute(self, key: str, default=None):
        """Get a specific attribute value."""
        return self.attributes.get(key, default) if self.attributes else default
    
    def set_attribute(self, key: str, value: Any):
        """Set a specific attribute value."""
        if not self.attributes:
            self.attributes = {}
        self.attributes[key] = value
    
    @validates('sku')
    def validate_sku(self, key, sku):
        """Validate SKU format."""
        import re
        if not re.match(r'^[A-Z0-9-]{3,50}$', sku.upper()):
            raise ValueError("SKU must be 3-50 characters and contain only uppercase letters, numbers, and hyphens")
        return sku.upper()


class ProductVariant(BaseModel):
    """
    Product variants for products with different options (color, size, etc.).
    Demonstrates inheritance and polymorphism.
    """
    
    __tablename__ = 'product_variants'
    
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    
    # Variant information
    name = Column(String(255), nullable=False)  # e.g., "Red - Large"
    sku = Column(String(100), nullable=False, unique=True, index=True)
    
    # Variant-specific pricing
    price_adjustment = Column(Integer, default=0)  # Price difference from base product in cents
    cost_price = Column(Integer)
    
    # Variant attributes
    attributes = Column(JSONB, nullable=False)  # {"color": "red", "size": "large"}
    
    # Physical properties (can override product defaults)
    weight = Column(Numeric(10, 3))
    dimensions = Column(JSONB)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    inventory = relationship("InventoryVariant", back_populates="variant", uselist=False, cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_product_variants_product', 'product_id'),
        Index('ix_product_variants_attributes', 'attributes', postgresql_using='gin'),
        UniqueConstraint('product_id', 'sku', name='uq_product_variant_sku'),
    )
    
    @hybrid_property
    def final_price(self):
        """Calculate final price including adjustment."""
        return self.product.current_price + self.price_adjustment
    
    def get_attribute(self, key: str, default=None):
        """Get variant attribute value."""
        return self.attributes.get(key, default) if self.attributes else default


class ProductImage(BaseModel):
    """Product image model with ordering and metadata."""
    
    __tablename__ = 'product_images'
    
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    
    # Image information
    url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    title = Column(String(255))
    
    # Image metadata
    filename = Column(String(255))
    file_size = Column(Integer)  # Size in bytes
    width = Column(Integer)
    height = Column(Integer)
    mime_type = Column(String(50))
    
    # Ordering and status
    display_order = Column(Integer, default=0, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="images")
    
    __table_args__ = (
        Index('ix_product_images_product_order', 'product_id', 'display_order'),
        Index('ix_product_images_primary', 'product_id', 'is_primary'),
    )


class Inventory(BaseModel):
    """
    Inventory management for products.
    Demonstrates business logic integration and automatic calculations.
    """
    
    __tablename__ = 'inventory'
    
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, unique=True, index=True)
    
    # Stock levels
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)  # Reserved for pending orders
    quantity_on_order = Column(Integer, default=0, nullable=False)  # Incoming stock
    
    # Thresholds
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    reorder_point = Column(Integer, default=20, nullable=False)
    reorder_quantity = Column(Integer, default=100, nullable=False)
    
    # Status
    status = Column(
        Enum(InventoryStatus, name='inventory_status'),
        nullable=False,
        default=InventoryStatus.IN_STOCK,
        index=True
    )
    
    # Tracking
    track_inventory = Column(Boolean, default=True, nullable=False)
    allow_backorder = Column(Boolean, default=False, nullable=False)
    
    # Location (for multi-warehouse)
    warehouse_location = Column(String(100))
    bin_location = Column(String(50))
    
    # Relationships
    product = relationship("Product", back_populates="inventory")
    movements = relationship("InventoryMovement", back_populates="inventory", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_inventory_status', 'status'),
        Index('ix_inventory_low_stock', 'quantity_on_hand', 'low_stock_threshold'),
        CheckConstraint('quantity_on_hand >= 0', name='ck_inventory_on_hand_positive'),
        CheckConstraint('quantity_reserved >= 0', name='ck_inventory_reserved_positive'),
        CheckConstraint('quantity_on_order >= 0', name='ck_inventory_on_order_positive'),
        CheckConstraint('low_stock_threshold >= 0', name='ck_inventory_threshold_positive'),
        CheckConstraint('reorder_point >= 0', name='ck_inventory_reorder_point_positive'),
        CheckConstraint('reorder_quantity > 0', name='ck_inventory_reorder_quantity_positive'),
    )
    
    @hybrid_property
    def available_quantity(self):
        """Calculate available quantity (on hand - reserved)."""
        return self.quantity_on_hand - self.quantity_reserved
    
    @hybrid_property
    def is_low_stock(self):
        """Check if inventory is below low stock threshold."""
        return self.available_quantity <= self.low_stock_threshold
    
    @hybrid_property
    def needs_reorder(self):
        """Check if inventory needs reordering."""
        return self.available_quantity <= self.reorder_point
    
    def reserve_quantity(self, quantity: int) -> bool:
        """Reserve quantity for an order."""
        if quantity <= 0:
            return False
        
        if self.available_quantity >= quantity:
            self.quantity_reserved += quantity
            self.update_status()
            return True
        
        return False
    
    def release_reservation(self, quantity: int):
        """Release reserved quantity."""
        if quantity <= 0:
            return
        
        self.quantity_reserved = max(0, self.quantity_reserved - quantity)
        self.update_status()
    
    def add_stock(self, quantity: int, reason: str = "Manual adjustment"):
        """Add stock and create movement record."""
        if quantity <= 0:
            return
        
        self.quantity_on_hand += quantity
        self.update_status()
        
        # Create movement record
        movement = InventoryMovement(
            inventory_id=self.id,
            movement_type='in',
            quantity=quantity,
            reason=reason,
            reference_type='manual',
            resulting_quantity=self.quantity_on_hand
        )
        self.movements.append(movement)
    
    def remove_stock(self, quantity: int, reason: str = "Manual adjustment"):
        """Remove stock and create movement record."""
        if quantity <= 0:
            return
        
        # Ensure we don't go negative
        actual_quantity = min(quantity, self.quantity_on_hand)
        self.quantity_on_hand -= actual_quantity
        self.update_status()
        
        # Create movement record
        movement = InventoryMovement(
            inventory_id=self.id,
            movement_type='out',
            quantity=actual_quantity,
            reason=reason,
            reference_type='manual',
            resulting_quantity=self.quantity_on_hand
        )
        self.movements.append(movement)
    
    def update_status(self):
        """Update inventory status based on current quantities."""
        if not self.track_inventory:
            self.status = InventoryStatus.IN_STOCK
            return
        
        available = self.available_quantity
        
        if available <= 0:
            if self.allow_backorder:
                self.status = InventoryStatus.BACKORDER
            else:
                self.status = InventoryStatus.OUT_OF_STOCK
        elif available <= self.low_stock_threshold:
            self.status = InventoryStatus.LOW_STOCK
        else:
            self.status = InventoryStatus.IN_STOCK


class InventoryVariant(BaseModel):
    """Inventory tracking for product variants."""
    
    __tablename__ = 'inventory_variants'
    
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.id'), nullable=False, unique=True, index=True)
    
    # Stock levels
    quantity_on_hand = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)
    
    # Thresholds
    low_stock_threshold = Column(Integer, default=5, nullable=False)
    
    # Relationships
    variant = relationship("ProductVariant", back_populates="inventory")
    
    __table_args__ = (
        CheckConstraint('quantity_on_hand >= 0', name='ck_inventory_variant_on_hand_positive'),
        CheckConstraint('quantity_reserved >= 0', name='ck_inventory_variant_reserved_positive'),
    )
    
    @hybrid_property
    def available_quantity(self):
        """Calculate available quantity."""
        return self.quantity_on_hand - self.quantity_reserved


class InventoryMovement(BaseModel):
    """Track all inventory movements for audit trail."""
    
    __tablename__ = 'inventory_movements'
    
    inventory_id = Column(UUID(as_uuid=True), ForeignKey('inventory.id'), nullable=False, index=True)
    
    # Movement details
    movement_type = Column(String(10), nullable=False, index=True)  # 'in' or 'out'
    quantity = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    
    # Reference information
    reference_type = Column(String(50))  # 'order', 'return', 'adjustment', etc.
    reference_id = Column(UUID(as_uuid=True))
    
    # Resulting quantities
    resulting_quantity = Column(Integer, nullable=False)
    
    # Additional metadata
    notes = Column(Text)
    metadata_info = Column(JSONB, default=dict)
    
    # Relationships
    inventory = relationship("Inventory", back_populates="movements")
    
    __table_args__ = (
        Index('ix_inventory_movements_reference', 'reference_type', 'reference_id'),
        Index('ix_inventory_movements_date', 'created_at'),
        CheckConstraint('quantity > 0', name='ck_inventory_movement_quantity_positive'),
        CheckConstraint('movement_type IN (\'in\', \'out\')', name='ck_inventory_movement_type'),
    )


# Event listeners for automatic updates
@event.listens_for(Product, 'before_insert')
@event.listens_for(Product, 'before_update')
def update_product_search_vector(mapper, connection, target):
    """Update search vector for full-text search."""
    search_text = f"{target.name} {target.description or ''} {target.short_description or ''}"
    # In a real application, you'd use PostgreSQL's to_tsvector function
    # This is a simplified version
    target.search_vector = search_text


@event.listens_for(Category, 'before_insert')
@event.listens_for(Category, 'before_update')
def update_category_path(mapper, connection, target):
    """Update materialized path for category hierarchy."""
    if target.parent_id:
        # In a real application, you'd fetch the parent's path from the database
        # This is a simplified version
        target.path = f"/parent_path/{target.slug}"
        target.level = 1  # Simplified
    else:
        target.path = f"/{target.slug}"
        target.level = 0


@event.listens_for(Inventory, 'after_update')
def check_reorder_trigger(mapper, connection, target):
    """Trigger reorder notification when inventory is low."""
    if target.needs_reorder and target.track_inventory:
        # In a real application, you'd send a notification or create a purchase order
        print(f"Reorder needed for product {target.product_id}: {target.available_quantity} remaining")
```

### 3.2 Order Management Models

**monolithic/models/order.py** - Order and Shopping Cart Models:
```python
"""
Order management models demonstrating complex business logic,
state machines, and financial calculations.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
import enum

from sqlalchemy import (
    Column, String, Text, Integer, Numeric, Boolean, 
    ForeignKey, DateTime, Index, CheckConstraint,
    UniqueConstraint, event
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func

from .base import BaseModel


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ShippingStatus(str, enum.Enum):
    """Shipping status enumeration."""
    PENDING = "pending"
    PREPARING = "preparing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED_DELIVERY = "failed_delivery"
    RETURNED = "returned"


class Order(BaseModel):
    """
    Order model demonstrating complex business logic and state management.
    Includes pricing calculations, tax handling, and shipping integration.
    """
    
    __tablename__ = 'orders'
    
    # Order identification
    order_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False, index=True)
    
    # Order status
    status = Column(
        Enum(OrderStatus, name='order_status'),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True
    )
    payment_status = Column(
        Enum(PaymentStatus, name='payment_status'),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True
    )
    shipping_status = Column(
        Enum(ShippingStatus, name='shipping_status'),
        nullable=False,
        default=ShippingStatus.PENDING,
        index=True
    )
    
    # Pricing (all amounts in cents)
    subtotal = Column(Integer, nullable=False, default=0)
    tax_amount = Column(Integer, nullable=False, default=0)
    shipping_cost = Column(Integer, nullable=False, default=0)
    discount_amount = Column(Integer, nullable=False, default=0)
    total_amount = Column(Integer, nullable=False, default=0)
    
    # Customer information (snapshot at time of order)
    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(20))
    
    # Billing address (denormalized for historical record)
    billing_address = Column(JSONB, nullable=False)
    
    # Shipping information
    shipping_address = Column(JSONB, nullable=False)
    shipping_method = Column(String(100))
    tracking_number = Column(String(100), index=True)
    estimated_delivery_date = Column(DateTime(timezone=True))
    actual_delivery_date = Column(DateTime(timezone=True))
    
    # Discounts and promotions
    coupon_code = Column(String(50), index=True)
    coupon_discount = Column(Integer, default=0)
    
    # Order metadata
    currency = Column(String(3), default='USD', nullable=False)
    exchange_rate = Column(Numeric(10, 6), default=1.0)
    order_source = Column(String(50), default='web')  # web, mobile, api
    user_agent = Column(Text)
    ip_address = Column(String(45))
    
    # Important dates
    confirmed_at = Column(DateTime(timezone=True))
    shipped_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))
    
    # Order notes
    customer_notes = Column(Text)
    internal_notes = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_orders_customer_status', 'customer_id', 'status'),
        Index('ix_orders_date_status', 'created_at', 'status'),
        Index('ix_orders_total', 'total_amount'),
        CheckConstraint('subtotal >= 0', name='ck_order_subtotal_positive'),
        CheckConstraint('tax_amount >= 0', name='ck_order_tax_positive'),
        CheckConstraint('shipping_cost >= 0', name='ck_order_shipping_positive'),
        CheckConstraint('discount_amount >= 0', name='ck_order_discount_positive'),
        CheckConstraint('total_amount >= 0', name='ck_order_total_positive'),
    )
    
    @hybrid_property
    def subtotal_decimal(self):
        """Get subtotal as Decimal for currency formatting."""
        return Decimal(self.subtotal) / 100
    
    @hybrid_property
    def total_decimal(self):
        """Get total as Decimal for currency formatting."""
        return Decimal(self.total_amount) / 100
    
    @hybrid_property
    def is_paid(self):
        """Check if order is fully paid."""
        return self.payment_status in [PaymentStatus.CAPTURED, PaymentStatus.AUTHORIZED]
    
    @hybrid_property
    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    @hybrid_property
    def can_be_shipped(self):
        """Check if order can be shipped."""
        return (self.status == OrderStatus.CONFIRMED and 
                self.payment_status in [PaymentStatus.CAPTURED, PaymentStatus.AUTHORIZED])
    
    def calculate_totals(self):
        """Calculate order totals from items."""
        self.subtotal = sum(item.total_price for item in self.items)
        
        # Calculate tax (simplified - in reality you'd use a tax service)
        tax_rate = Decimal('0.08')  # 8% tax rate
        self.tax_amount = int(self.subtotal * tax_rate)
        
        # Apply discounts
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
    
    def add_item(self, product, quantity: int, unit_price: int, variant=None):
        """Add an item to the order."""
        # Check if item already exists
        existing_item = None
        for item in self.items:
            if (item.product_id == product.id and 
                item.variant_id == (variant.id if variant else None)):
                existing_item = item
                break
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.calculate_total()
        else:
            order_item = OrderItem(
                order_id=self.id,
                product_id=product.id,
                variant_id=variant.id if variant else None,
                quantity=quantity,
                unit_price=unit_price,
                product_name=product.name,
                product_sku=variant.sku if variant else product.sku
            )
            order_item.calculate_total()
            self.items.append(order_item)
        
        self.calculate_totals()
    
    def update_status(self, new_status: OrderStatus, notes: str = None, user_id: str = None):
        """Update order status with history tracking."""
        old_status = self.status
        self.status = new_status
        
        # Update timestamps
        now = datetime.utcnow()
        if new_status == OrderStatus.CONFIRMED:
            self.confirmed_at = now
        elif new_status == OrderStatus.SHIPPED:
            self.shipped_at = now
        elif new_status == OrderStatus.DELIVERED:
            self.delivered_at = now
        elif new_status == OrderStatus.CANCELLED:
            self.cancelled_at = now
        
        # Create status history record
        history = OrderStatusHistory(
            order_id=self.id,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
            changed_by_id=user_id
        )
        self.status_history.append(history)
    
    def cancel(self, reason: str = None, user_id: str = None):
        """Cancel the order."""
        if not self.can_be_cancelled:
            raise ValueError("Order cannot be cancelled in current status")
        
        # Release reserved inventory
        for item in self.items:
            if item.product.inventory:
                item.product.inventory.release_reservation(item.quantity)
        
        self.update_status(OrderStatus.CANCELLED, reason, user_id)
    
    @validates('order_number')
    def validate_order_number(self, key, order_number):
        """Validate order number format."""
        import re
        if not re.match(r'^ORD-\d{8}-[A-Z0-9]{6}$', order_number):
            raise ValueError("Invalid order number format")
        return order_number


class OrderItem(BaseModel):
    """Individual items within an order."""
    
    __tablename__ = 'order_items'
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.id'), index=True)
    
    # Item details (snapshot at time of order)
    product_name = Column(String(500), nullable=False)
    product_sku = Column(String(100), nullable=False)
    product_description = Column(Text)
    
    # Pricing and quantity
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)  # Price in cents
    total_price = Column(Integer, nullable=False)  # Total for this line item
    
    # Product snapshot
    product_attributes = Column(JSONB, default=dict)  # Snapshot of product attributes
    variant_attributes = Column(JSONB, default=dict)  # Snapshot of variant attributes
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    
    __table_args__ = (
        Index('ix_order_items_order', 'order_id'),
        Index('ix_order_items_product', 'product_id'),
        CheckConstraint('quantity > 0', name='ck_order_item_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='ck_order_item_price_positive'),
        CheckConstraint('total_price >= 0', name='ck_order_item_total_positive'),
    )
    
    def calculate_total(self):
        """Calculate total price for this item."""
        self.total_price = self.quantity * self.unit_price
    
    @hybrid_property
    def unit_price_decimal(self):
        """Get unit price as Decimal."""
        return Decimal(self.unit_price) / 100
    
    @hybrid_property
    def total_price_decimal(self):
        """Get total price as Decimal."""
        return Decimal(self.total_price) / 100


class OrderStatusHistory(BaseModel):
    """Track order status changes for audit trail."""
    
    __tablename__ = 'order_status_history'
    
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False, index=True)
    
    # Status change details
    old_status = Column(Enum(OrderStatus, name='order_status'), nullable=False)
    new_status = Column(Enum(OrderStatus, name='order_status'), nullable=False)
    
    # Change metadata
    notes = Column(Text)
    changed_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
    changed_by = relationship("User")
    
    __table_args__ = (
        Index('ix_order_status_history_order', 'order_id'),
        Index('ix_order_status_history_date', 'created_at'),
    )


class CartItem(BaseModel):
    """Shopping cart items for customers."""
    
    __tablename__ = 'cart_items'
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.id'), index=True)
    
    # Cart item details
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Price snapshot (updated when item is added/modified)
    unit_price = Column(Integer, nullable=False)  # Price at time of adding to cart
    
    # Relationships
    customer = relationship("Customer", back_populates="cart_items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    
    __table_args__ = (
        Index('ix_cart_items_customer', 'customer_id'),
        Index('ix_cart_items_product', 'product_id'),
        UniqueConstraint('customer_id', 'product_id', 'variant_id', name='uq_cart_customer_product_variant'),
        CheckConstraint('quantity > 0', name='ck_cart_item_quantity_positive'),
        CheckConstraint('unit_price >= 0', name='ck_cart_item_price_positive'),
    )
    
    @hybrid_property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.quantity * self.unit_price
    
    @hybrid_property
    def total_price_decimal(self):
        """Get total price as Decimal."""
        return Decimal(self.total_price) / 100
    
    def update_price(self):
        """Update price from current product/variant price."""
        if self.variant:
            self.unit_price = self.variant.final_price
        else:
            self.unit_price = self.product.current_price


class Wishlist(BaseModel):
    """Customer wishlist functionality."""
    
    __tablename__ = 'wishlists'
    
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.id'), nullable=False)
    name = Column(String(255), nullable=False, default='My Wishlist')
    description = Column(Text)
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    customer = relationship("Customer", back_populates="wishlists")
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('ix_wishlists_customer', 'customer_id'),
        UniqueConstraint('customer_id', 'name', name='uq_wishlist_customer_name'),
    )


class WishlistItem(BaseModel):
    """Items in customer wishlists."""
    
    __tablename__ = 'wishlist_items'
    
    wishlist_id = Column(UUID(as_uuid=True), ForeignKey('wishlists.id'), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.id'), nullable=False, index=True)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.id'), index=True)
    
    # Item details
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(Text)
    priority = Column(Integer, default=0)  # For ordering items
    
    # Relationships
    wishlist = relationship("Wishlist", back_populates="items")
    product = relationship("Product")
    variant = relationship("ProductVariant")
    
    __table_args__ = (
        Index('ix_wishlist_items_wishlist', 'wishlist_id'),
        Index('ix_wishlist_items_product', 'product_id'),
        UniqueConstraint('wishlist_id', 'product_id', 'variant_id', name='uq_wishlist_product_variant'),
    )


# Event listeners for automatic updates
@event.listens_for(OrderItem, 'before_insert')
@event.listens_for(OrderItem, 'before_update')
def calculate_order_item_total(mapper, connection, target):
    """Automatically calculate order item total."""
    target.calculate_total()


@event.listens_for(Order, 'before_insert')
@event.listens_for(Order, 'before_update')
def generate_order_number(mapper, connection, target):
    """Generate order number if not set."""
    if not target.order_number:
        import random
        import string
        date_part = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        target.order_number = f"ORD-{date_part}-{random_part}"


@event.listens_for(CartItem, 'before_insert')
def update_cart_item_price(mapper, connection, target):
    """Update cart item price from current product price."""
    target.update_price()
```
