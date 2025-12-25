# Database Engineer Skill

## Metadata
- **Skill Name**: database-engineer
- **Job**: Design and manage Neon Serverless Postgres database
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Designs database schema, manages migrations, optimizes queries, and maintains the Neon Serverless Postgres database for the textbook chatbot application.

## Example Tasks
- Design database schema for conversations and content
- Create database migrations with Alembic
- Set up Neon Postgres project
- Optimize database queries and indexes
- Implement connection pooling
- Create database backup strategy
- Monitor database performance
- Manage database security and access control

## Required Knowledge
- PostgreSQL 15+
- SQL and database design principles
- Alembic (migration tool)
- SQLAlchemy ORM
- Database indexing and optimization
- Connection pooling
- Database security best practices

## Key Technologies
- Neon Serverless Postgres
- PostgreSQL 15+
- SQLAlchemy 2.x
- Alembic
- asyncpg (async driver)
- pgvector (for vector storage - optional)

## Database Architecture
```
┌─────────────────────────────────────┐
│   Neon Serverless Postgres          │
│                                     │
│   ┌─────────────────────────────┐  │
│   │  conversations              │  │
│   │  - id (PK)                  │  │
│   │  - session_id (unique)      │  │
│   │  - user_id                  │  │
│   │  - created_at               │  │
│   │  - updated_at               │  │
│   └──────────┬──────────────────┘  │
│              │                      │
│   ┌──────────▼──────────────────┐  │
│   │  messages                   │  │
│   │  - id (PK)                  │  │
│   │  - conversation_id (FK)     │  │
│   │  - role                     │  │
│   │  - content                  │  │
│   │  - citations (JSON)         │  │
│   │  - created_at               │  │
│   └─────────────────────────────┘  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │  content_metadata           │  │
│   │  - id (PK)                  │  │
│   │  - chapter                  │  │
│   │  - section                  │  │
│   │  - page_url                 │  │
│   │  - created_at               │  │
│   │  - updated_at               │  │
│   └─────────────────────────────┘  │
│                                     │
│   ┌─────────────────────────────┐  │
│   │  analytics                  │  │
│   │  - id (PK)                  │  │
│   │  - event_type               │  │
│   │  - user_id                  │  │
│   │  - metadata (JSON)          │  │
│   │  - timestamp                │  │
│   └─────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Workflow Steps

### 1. Set Up Neon Postgres Project

**Create Neon Project:**
1. Sign up at https://neon.tech
2. Create new project: "textbook-chatbot"
3. Choose region closest to backend deployment
4. Get connection string

**Connection String Format:**
```
postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

### 2. Database Configuration

**app/core/config.py**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600

    # Neon-specific
    DATABASE_SSL_MODE: str = "require"

    class Config:
        env_file = ".env"

settings = Settings()
```

**app/db/session.py**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,  # Verify connections before using
)

# Create session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency for FastAPI
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 3. Database Models

**app/models/base.py**
```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
```

**app/models/conversation.py**
```python
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import uuid

class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        UUID(as_uuid=True),
        unique=True,
        default=uuid.uuid4,
        index=True
    )
    user_id = Column(String, nullable=True, index=True)

    # Relationships
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)
    selected_text = Column(Text, nullable=True)
    page_context = Column(String, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('ix_messages_conversation_created',
              'conversation_id', 'created_at'),
    )
```

**app/models/content.py**
```python
from sqlalchemy import Column, Integer, String, Text
from .base import Base, TimestampMixin

class ContentMetadata(Base, TimestampMixin):
    __tablename__ = "content_metadata"

    id = Column(Integer, primary_key=True, index=True)
    chapter = Column(String, index=True)
    section = Column(String, index=True)
    title = Column(String, nullable=False)
    page_url = Column(String, unique=True, nullable=False)
    description = Column(Text)
    keywords = Column(String)  # Comma-separated

    __table_args__ = (
        Index('ix_content_chapter_section', 'chapter', 'section'),
    )
```

**app/models/analytics.py**
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from .base import Base

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)  # 'query', 'feedback', etc.
    user_id = Column(String, nullable=True, index=True)
    conversation_id = Column(Integer, nullable=True, index=True)
    metadata = Column(JSON)
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    __table_args__ = (
        Index('ix_analytics_type_timestamp', 'event_type', 'timestamp'),
    )
```

### 4. Alembic Migrations

**Initialize Alembic:**
```bash
alembic init alembic
```

**alembic/env.py**
```python
from app.models.base import Base
from app.models import conversation, content, analytics
from app.core.config import settings

# Import all models
target_metadata = Base.metadata

# Database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

**Create Migration:**
```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 5. Optimized Queries

**app/crud/conversation.py**
```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation import Conversation, Message

class ConversationCRUD:
    @staticmethod
    async def get_conversation_with_messages(
        db: AsyncSession,
        session_id: str
    ) -> Conversation:
        """Get conversation with all messages - optimized"""
        stmt = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.session_id == session_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: int,
        role: str,
        content: str,
        citations: dict = None
    ) -> Message:
        """Create new message"""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            citations=citations
        )
        db.add(message)
        await db.flush()  # Get ID without committing
        return message
```

### 6. Database Indexes

**Key Indexes to Create:**
```sql
-- Conversation lookups
CREATE INDEX ix_conversations_session_id ON conversations(session_id);
CREATE INDEX ix_conversations_user_id ON conversations(user_id);

-- Message queries
CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX ix_messages_conversation_created
    ON messages(conversation_id, created_at DESC);

-- Analytics queries
CREATE INDEX ix_analytics_type_timestamp
    ON analytics(event_type, timestamp DESC);
CREATE INDEX ix_analytics_user_id ON analytics(user_id);

-- Content metadata
CREATE INDEX ix_content_chapter_section ON content_metadata(chapter, section);
CREATE INDEX ix_content_page_url ON content_metadata(page_url);
```

## Integration Points
- **backend-engineer**: Provides database models and CRUD operations
- **rag-specialist**: Stores conversation history and metadata
- **chatbot-engineer**: Persists chat sessions
- **deployment-expert**: Manages database in production

## Success Criteria
- [ ] Database schema is normalized and efficient
- [ ] Migrations run successfully
- [ ] Connection pooling is configured
- [ ] Indexes optimize query performance
- [ ] Foreign keys maintain referential integrity
- [ ] Timestamps are properly managed
- [ ] Backups are configured
- [ ] Monitoring is set up

## Performance Optimization

### Connection Pooling
```python
# Optimal settings for Neon Serverless
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # Max connections in pool
    max_overflow=20,        # Extra connections when needed
    pool_timeout=30,        # Seconds to wait for connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Verify before use
)
```

### Query Optimization
- Use indexes on frequently queried columns
- Implement eager loading for relationships
- Use pagination for large result sets
- Cache frequent queries
- Use database-level constraints

### Neon-Specific Optimizations
- Enable Autoscaling in Neon dashboard
- Use connection pooling (PgBouncer built-in)
- Monitor with Neon metrics
- Use read replicas for analytics queries

## Backup and Recovery

### Neon Built-in Backups
- Point-in-Time Recovery (PITR) available
- Automatic daily backups
- Manual snapshots before major changes

### Backup Strategy
```python
# Export data for additional backup
import asyncio
from app.db.session import AsyncSessionLocal

async def backup_conversations():
    async with AsyncSessionLocal() as db:
        # Export to JSON or CSV
        pass
```

## Security Best Practices
- Use environment variables for credentials
- Enable SSL/TLS (required by Neon)
- Implement row-level security if needed
- Regular security audits
- Principle of least privilege
- Sanitize all inputs (SQLAlchemy handles this)

## Monitoring and Maintenance

### Neon Dashboard Monitoring
- Query performance metrics
- Connection pool usage
- Storage usage
- Compute usage

### Application-Level Monitoring
```python
# Log slow queries
import time
from functools import wraps

def log_query_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        if duration > 1.0:  # Log queries > 1 second
            logger.warning(f"Slow query: {func.__name__} took {duration}s")
        return result
    return wrapper
```

## Best Practices
- Use async operations throughout
- Implement proper error handling
- Version all schema changes with Alembic
- Document all models and relationships
- Use type hints consistently
- Implement soft deletes for important data
- Regular database maintenance
- Monitor query performance
- Keep Neon connection string secure
- Use parameterized queries (SQLAlchemy does this)

## Testing

**tests/test_database.py**
```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.models.base import Base

@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()
```

## Output Artifacts
- Database models in `/app/models`
- Alembic migration files
- CRUD operations in `/app/crud`
- Database session management
- SQL schema documentation
- Performance optimization guide
- Backup and recovery procedures
- Neon project configuration
