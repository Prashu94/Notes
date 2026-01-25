# Chapter 33: Building Applications with Neo4j

## Learning Objectives
By the end of this chapter, you will:
- Design application architectures with Neo4j
- Build REST APIs backed by Neo4j
- Implement authentication and authorization
- Handle real-time data with Neo4j
- Deploy production-ready applications

---

## 33.1 Application Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│      (REST API / GraphQL / CLI)     │
├─────────────────────────────────────┤
│           Service Layer             │
│    (Business Logic / Use Cases)     │
├─────────────────────────────────────┤
│          Repository Layer           │
│      (Data Access / Neo4j Driver)   │
├─────────────────────────────────────┤
│            Data Layer               │
│         (Neo4j Database)            │
└─────────────────────────────────────┘
```

### Project Structure

```
my_neo4j_app/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Neo4j connection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── graph_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user_repository.py
│   └── models/
│       ├── __init__.py
│       └── user.py
├── tests/
│   └── ...
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 33.2 Building a FastAPI Application

### Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    neo4j_uri: str = "neo4j://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"
    
    jwt_secret: str = "your-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

### Database Connection

```python
# app/database.py
from neo4j import GraphDatabase
from contextlib import contextmanager
from app.config import get_settings

class Neo4jConnection:
    def __init__(self):
        self.settings = get_settings()
        self._driver = None
    
    def connect(self):
        self._driver = GraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_user, self.settings.neo4j_password)
        )
        self._driver.verify_connectivity()
    
    def disconnect(self):
        if self._driver:
            self._driver.close()
    
    @property
    def driver(self):
        return self._driver
    
    @contextmanager
    def session(self):
        session = self._driver.session(database=self.settings.neo4j_database)
        try:
            yield session
        finally:
            session.close()

# Singleton instance
db = Neo4jConnection()

def get_db():
    return db
```

### Pydantic Models

```python
# app/api/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class FriendshipCreate(BaseModel):
    friend_username: str

class FriendResponse(BaseModel):
    id: str
    username: str
    full_name: Optional[str]
    since: Optional[datetime]

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
```

### Repository Layer

```python
# app/repositories/user_repository.py
from typing import List, Optional, Dict
from app.database import Neo4jConnection

class UserRepository:
    def __init__(self, db: Neo4jConnection):
        self.db = db
    
    def create(self, username: str, email: str, 
               password_hash: str, full_name: str = None) -> Dict:
        def _create(tx, username, email, password_hash, full_name):
            result = tx.run("""
                CREATE (u:User {
                    username: $username,
                    email: $email,
                    password_hash: $password_hash,
                    full_name: $full_name,
                    created_at: datetime()
                })
                RETURN u {
                    .*, 
                    id: elementId(u)
                } AS user
            """, username=username, email=email, 
                password_hash=password_hash, full_name=full_name)
            return result.single()["user"]
        
        with self.db.session() as session:
            return session.execute_write(
                _create, username, email, password_hash, full_name
            )
    
    def find_by_username(self, username: str) -> Optional[Dict]:
        def _find(tx, username):
            result = tx.run("""
                MATCH (u:User {username: $username})
                RETURN u {.*, id: elementId(u)} AS user
            """, username=username)
            record = result.single()
            return record["user"] if record else None
        
        with self.db.session() as session:
            return session.execute_read(_find, username)
    
    def find_by_email(self, email: str) -> Optional[Dict]:
        def _find(tx, email):
            result = tx.run("""
                MATCH (u:User {email: $email})
                RETURN u {.*, id: elementId(u)} AS user
            """, email=email)
            record = result.single()
            return record["user"] if record else None
        
        with self.db.session() as session:
            return session.execute_read(_find, email)
    
    def update(self, username: str, properties: Dict) -> Optional[Dict]:
        def _update(tx, username, properties):
            result = tx.run("""
                MATCH (u:User {username: $username})
                SET u += $properties, u.updated_at = datetime()
                RETURN u {.*, id: elementId(u)} AS user
            """, username=username, properties=properties)
            record = result.single()
            return record["user"] if record else None
        
        with self.db.session() as session:
            return session.execute_write(_update, username, properties)
    
    def delete(self, username: str) -> bool:
        def _delete(tx, username):
            result = tx.run("""
                MATCH (u:User {username: $username})
                DETACH DELETE u
                RETURN count(u) AS deleted
            """, username=username)
            return result.single()["deleted"] > 0
        
        with self.db.session() as session:
            return session.execute_write(_delete, username)
    
    def add_friend(self, username: str, friend_username: str) -> bool:
        def _add_friend(tx, username, friend_username):
            result = tx.run("""
                MATCH (u:User {username: $username})
                MATCH (f:User {username: $friend_username})
                MERGE (u)-[r:FRIENDS_WITH]->(f)
                ON CREATE SET r.since = datetime()
                RETURN count(r) > 0 AS created
            """, username=username, friend_username=friend_username)
            return result.single()["created"]
        
        with self.db.session() as session:
            return session.execute_write(_add_friend, username, friend_username)
    
    def get_friends(self, username: str) -> List[Dict]:
        def _get_friends(tx, username):
            result = tx.run("""
                MATCH (u:User {username: $username})-[r:FRIENDS_WITH]-(friend:User)
                RETURN friend {
                    .username, 
                    .full_name, 
                    id: elementId(friend),
                    since: r.since
                } AS friend
            """, username=username)
            return [record["friend"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_friends, username)
    
    def get_friend_recommendations(self, username: str, 
                                    limit: int = 10) -> List[Dict]:
        def _get_recommendations(tx, username, limit):
            result = tx.run("""
                MATCH (u:User {username: $username})-[:FRIENDS_WITH]-(friend)
                      -[:FRIENDS_WITH]-(fof:User)
                WHERE u <> fof AND NOT (u)-[:FRIENDS_WITH]-(fof)
                RETURN fof {
                    .username, 
                    .full_name,
                    id: elementId(fof),
                    mutual_friends: count(DISTINCT friend)
                } AS recommendation
                ORDER BY recommendation.mutual_friends DESC
                LIMIT $limit
            """, username=username, limit=limit)
            return [record["recommendation"] for record in result]
        
        with self.db.session() as session:
            return session.execute_read(_get_recommendations, username, limit)
```

### Service Layer

```python
# app/services/user_service.py
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.repositories.user_repository import UserRepository
from app.config import get_settings
from app.api.schemas import UserCreate, UserResponse, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.settings = get_settings()
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    def create_access_token(self, username: str) -> str:
        expire = datetime.utcnow() + timedelta(seconds=self.settings.jwt_expiration)
        to_encode = {"sub": username, "exp": expire}
        return jwt.encode(
            to_encode, 
            self.settings.jwt_secret, 
            algorithm=self.settings.jwt_algorithm
        )
    
    def verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm]
            )
            return payload.get("sub")
        except JWTError:
            return None
    
    def register(self, user_data: UserCreate) -> dict:
        # Check if user exists
        if self.repository.find_by_username(user_data.username):
            raise ValueError("Username already exists")
        if self.repository.find_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Create user
        password_hash = self.hash_password(user_data.password)
        user = self.repository.create(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name
        )
        
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[Token]:
        user = self.repository.find_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user["password_hash"]):
            return None
        
        access_token = self.create_access_token(username)
        return Token(access_token=access_token)
    
    def get_user(self, username: str) -> Optional[dict]:
        return self.repository.find_by_username(username)
    
    def add_friend(self, username: str, friend_username: str) -> bool:
        if username == friend_username:
            raise ValueError("Cannot add yourself as friend")
        
        friend = self.repository.find_by_username(friend_username)
        if not friend:
            raise ValueError("User not found")
        
        return self.repository.add_friend(username, friend_username)
    
    def get_friends(self, username: str) -> List[dict]:
        return self.repository.get_friends(username)
    
    def get_recommendations(self, username: str) -> List[dict]:
        return self.repository.get_friend_recommendations(username)
```

### API Routes

```python
# app/api/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List

from app.api.schemas import (
    UserCreate, UserResponse, UserUpdate,
    FriendshipCreate, FriendResponse, Token
)
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_service():
    db = get_db()
    repository = UserRepository(db)
    return UserService(repository)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service)
):
    username = service.verify_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = service.get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Auth endpoints
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        user = service.register(user_data)
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            created_at=user["created_at"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(get_user_service)
):
    token = service.authenticate(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    return token

# User endpoints
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        created_at=current_user["created_at"]
    )

@router.get("/users/{username}", response_model=UserResponse)
async def get_user(
    username: str,
    service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    user = service.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user.get("full_name"),
        created_at=user["created_at"]
    )

# Friend endpoints
@router.post("/friends", status_code=status.HTTP_201_CREATED)
async def add_friend(
    friendship: FriendshipCreate,
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    try:
        service.add_friend(current_user["username"], friendship.friend_username)
        return {"message": "Friend added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/friends", response_model=List[FriendResponse])
async def get_friends(
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    friends = service.get_friends(current_user["username"])
    return [
        FriendResponse(
            id=f["id"],
            username=f["username"],
            full_name=f.get("full_name"),
            since=f.get("since")
        )
        for f in friends
    ]

@router.get("/friends/recommendations", response_model=List[FriendResponse])
async def get_friend_recommendations(
    current_user: dict = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    recommendations = service.get_recommendations(current_user["username"])
    return [
        FriendResponse(
            id=r["id"],
            username=r["username"],
            full_name=r.get("full_name"),
            since=None
        )
        for r in recommendations
    ]
```

### Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import db
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    yield
    # Shutdown
    db.disconnect()

app = FastAPI(
    title="Neo4j Social Network API",
    description="A social network API powered by Neo4j",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## 33.3 Docker Deployment

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  neo4j:
    image: neo4j:5-enterprise
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password123
      - NEO4J_ACCEPT_LICENSE_AGREEMENT=yes
      - NEO4J_PLUGINS=["apoc"]
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=neo4j://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password123
      - JWT_SECRET=your-super-secret-key
    depends_on:
      neo4j:
        condition: service_healthy

volumes:
  neo4j_data:
  neo4j_logs:
```

### Requirements

```text
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
neo4j==5.14.0
pydantic==2.5.2
pydantic-settings==2.1.0
python-jose==3.3.0
passlib==1.7.4
bcrypt==4.1.1
python-multipart==0.0.6
```

---

## 33.4 Testing

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    db.connect()
    yield
    # Teardown - clean test data
    with db.session() as session:
        session.run("MATCH (n:User) WHERE n.username STARTS WITH 'test_' DETACH DELETE n")
    db.disconnect()

def test_register_user():
    response = client.post("/api/v1/register", json={
        "username": "test_user1",
        "email": "test1@example.com",
        "password": "securepass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user1"
    assert data["email"] == "test1@example.com"

def test_login():
    # First register
    client.post("/api/v1/register", json={
        "username": "test_user2",
        "email": "test2@example.com",
        "password": "securepass123"
    })
    
    # Then login
    response = client.post("/api/v1/token", data={
        "username": "test_user2",
        "password": "securepass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_get_current_user():
    # Register and login
    client.post("/api/v1/register", json={
        "username": "test_user3",
        "email": "test3@example.com",
        "password": "securepass123"
    })
    
    login_response = client.post("/api/v1/token", data={
        "username": "test_user3",
        "password": "securepass123"
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "test_user3"
```

---

## Summary

### Application Architecture

| Layer | Responsibility |
|-------|---------------|
| API | HTTP endpoints, validation |
| Service | Business logic |
| Repository | Data access |
| Database | Neo4j connection |

### Best Practices

1. **Use layered architecture** for separation of concerns
2. **Dependency injection** for testability
3. **Connection pooling** for performance
4. **JWT authentication** for stateless auth
5. **Docker** for consistent deployment

---

## Exercises

### Exercise 33.1: Add Search
1. Implement full-text search for users
2. Add search endpoint
3. Include graph-based relevance

### Exercise 33.2: Add Posts
1. Create Post node type
2. Implement CRUD for posts
3. Add timeline feature using graph traversal

### Exercise 33.3: Deploy to Cloud
1. Deploy Neo4j to AuraDB
2. Deploy API to cloud provider
3. Configure environment variables

---

**Next Chapter: [Chapter 34: Project - Social Network](34-project-social-network.md)**
