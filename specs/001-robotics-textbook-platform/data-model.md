# Data Model: Physical AI & Humanoid Robotics Interactive Textbook Platform

**Date**: 2025-12-26
**Feature**: 001-robotics-textbook-platform
**Purpose**: Define all data entities, relationships, validation rules, and storage strategies

## Overview

The platform uses two distinct storage systems:
1. **Qdrant Vector DB**: Stores content chunks with embeddings for semantic search
2. **Neon Serverless Postgres**: Stores conversation history, messages, and session data

## Entity Relationship Diagram

```
┌──────────────────┐
│  ContentChunk    │
│  (Qdrant)        │
│                  │
│  - id (UUID)     │
│  - text          │
│  - vector[1536]  │
│  - metadata      │
└────────┬─────────┘
         │
         │ referenced by
         │
┌────────▼──────────┐        ┌──────────────────┐
│  Message          │   ┌───▶│  Conversation    │
│  (Postgres)       │   │    │  (Postgres)      │
│                   │   │    │                  │
│  - id (UUID)      │   │    │  - id (UUID)     │
│  - role           │───┘    │  - session_id    │
│  - content        │  has   │  - created_at    │
│  - cited_chunks[] │  many  │  - updated_at    │
│  - created_at     │        └──────────────────┘
└───────────────────┘
```

## Entities

### 1. ContentChunk (Qdrant Vector DB)

**Purpose**: Represents a semantic unit of textbook content optimized for RAG retrieval

**Storage**: Qdrant Cloud collection named `textbook_chunks`

**Schema**:
```python
{
    "id": "uuid-v4",  # Unique chunk identifier
    "vector": [float] * 1536,  # OpenAI text-embedding-3-small
    "payload": {
        "text": str,  # Chunk content (400-600 tokens)
        "chapter": str,  # Chapter title (e.g., "Introduction to Physical AI")
        "section": str,  # Section heading (e.g., "2.1 Forward Kinematics")
        "page": int,  # Logical page number for citation
        "url": str,  # Docusaurus URL path (e.g., "/chapters/02-kinematics#forward")
        "chunk_index": int,  # Sequential number within chapter
        "created_at": str,  # ISO 8601 timestamp
        "word_count": int,  # Number of words in chunk
        "has_code": bool,  # Contains code blocks
        "has_equations": bool  # Contains mathematical equations
    }
}
```

**Indexes**:
- **Primary**: HNSW index on `vector` field (ef_construct=200, m=16)
- **Metadata Filters**: Indexed on `chapter`, `section`, `page` for fast filtering

**Validation Rules**:
- `id`: Must be valid UUID v4
- `vector`: Exactly 1536 dimensions, all floats
- `text`: 50-1000 tokens (validated during ingestion)
- `chapter`: Non-empty string, max 200 chars
- `section`: Non-empty string, max 300 chars
- `url`: Valid URL path starting with `/`
- `chunk_index`: Non-negative integer
- `created_at`: Valid ISO 8601 timestamp

**Relationships**:
- Referenced by `Message.cited_chunks` (loosely coupled via UUID)

**Sample Data**:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "vector": [0.023, -0.041, ...],  # 1536 floats
    "payload": {
        "text": "Forward kinematics is the process of computing the position and orientation of the end-effector...",
        "chapter": "Robot Kinematics",
        "section": "2.1 Forward Kinematics",
        "page": 15,
        "url": "/chapters/02-kinematics#forward-kinematics",
        "chunk_index": 3,
        "created_at": "2025-12-26T10:30:00Z",
        "word_count": 487,
        "has_code": true,
        "has_equations": true
    }
}
```

---

### 2. Conversation (Neon Postgres)

**Purpose**: Represents a user's chat session with the chatbot

**Storage**: Postgres table `conversations`

**Schema (SQLAlchemy)**:
```python
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_conversations_session_id', 'session_id'),
        Index('ix_conversations_created_at', 'created_at'),
    )
```

**Validation Rules**:
- `id`: Auto-generated UUID v4
- `session_id`: Required, 1-255 chars (browser-generated UUID)
- `created_at`: Auto-set on insert
- `updated_at`: Auto-updated on modification

**Relationships**:
- **Has Many**: `Message` (one conversation has multiple messages)
- **Cascade Delete**: Deleting conversation deletes all associated messages

**Sample Data**:
```json
{
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "session_id": "browser-session-abc123",
    "created_at": "2025-12-26T14:22:00Z",
    "updated_at": "2025-12-26T14:35:00Z"
}
```

---

### 3. Message (Neon Postgres)

**Purpose**: Represents a single message in a conversation (user question or assistant response)

**Storage**: Postgres table `messages`

**Schema (SQLAlchemy)**:
```python
class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(Enum('user', 'assistant', name='message_role'), nullable=False)
    content = Column(Text, nullable=False)
    cited_chunks = Column(JSON, nullable=True)  # Array of chunk UUIDs: ["uuid1", "uuid2"]
    selected_text = Column(Text, nullable=True)  # User-selected context (if P3 feature used)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('ix_messages_conversation_id', 'conversation_id'),
        Index('ix_messages_created_at', 'created_at'),
        Index('ix_messages_role', 'role'),
    )
```

**Validation Rules**:
- `id`: Auto-generated UUID v4
- `conversation_id`: Must reference valid `conversations.id`
- `role`: Must be 'user' or 'assistant'
- `content`: Required, 1-10,000 chars (user: 1-2000, assistant: 100-10,000)
- `cited_chunks`: Optional JSON array of UUIDs (assistant messages only)
- `selected_text`: Optional, max 5,000 chars (user messages only)
- `created_at`: Auto-set on insert

**Relationships**:
- **Belongs To**: `Conversation` (foreign key to conversations.id)
- **Loose Reference**: `ContentChunk` via `cited_chunks` (not enforced FK)

**Sample Data (User Message)**:
```json
{
    "id": "a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6",
    "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "role": "user",
    "content": "How do I calculate inverse kinematics for a 6-DOF robot arm?",
    "cited_chunks": null,
    "selected_text": null,
    "created_at": "2025-12-26T14:22:05Z"
}
```

**Sample Data (Assistant Message)**:
```json
{
    "id": "b2c3d4e5-f6g7-48h9-i0j1-k2l3m4n5o6p7",
    "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "role": "assistant",
    "content": "Inverse kinematics (IK) for a 6-DOF robot arm involves solving for the joint angles...",
    "cited_chunks": [
        "550e8400-e29b-41d4-a716-446655440000",
        "660e8400-e29b-41d4-a716-446655440001"
    ],
    "selected_text": null,
    "created_at": "2025-12-26T14:22:08Z"
}
```

---

## Data Flow

### Content Ingestion Pipeline
```
Markdown Files (frontend/docs/)
         ↓
    Parser (extract metadata)
         ↓
    Chunker (semantic boundaries)
         ↓
    Embedding Generator (OpenAI API)
         ↓
    Qdrant Uploader (batch insert)
         ↓
    ContentChunk entities created
```

### Chat Request Flow
```
User Question (ChatbotWidget)
         ↓
    POST /api/chat (FastAPI)
         ↓
    Create/Update Conversation + Message (Postgres)
         ↓
    Hybrid Search (Qdrant: vector + BM25)
         ↓
    Reranking (cross-encoder)
         ↓
    LLM Generation (OpenAI GPT-4, streaming)
         ↓
    Update Message.cited_chunks (Postgres)
         ↓
    SSE Stream to Frontend
```

## Storage Optimization

### Qdrant
- **Index Type**: HNSW (fast approximate nearest neighbor)
- **Quantization**: None (free tier doesn't support it, precision priority)
- **Sharding**: Single shard (2K chunks << 1M vector limit)
- **Replication**: Qdrant Cloud default (automatic)

### Postgres
- **Indexes**: Created on frequently queried columns (session_id, created_at, conversation_id)
- **Partitioning**: Not needed (low data volume)
- **Connection Pooling**: SQLAlchemy async pool (min=5, max=20)
- **JSON Storage**: `cited_chunks` stored as JSON array for flexibility

## Migration Strategy

### Initial Schema Setup
```sql
-- conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_conversations_session_id ON conversations(session_id);
CREATE INDEX ix_conversations_created_at ON conversations(created_at);

-- messages table
CREATE TYPE message_role AS ENUM ('user', 'assistant');

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    cited_chunks JSON,
    selected_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
CREATE INDEX ix_messages_created_at ON messages(created_at);
CREATE INDEX ix_messages_role ON messages(role);

-- Trigger for auto-updating conversations.updated_at
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations SET updated_at = NOW() WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_updated_at
    AFTER INSERT OR UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_updated_at();
```

### Qdrant Collection Setup
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

client.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(
        size=1536,  # text-embedding-3-small dimensionality
        distance=Distance.COSINE  # Cosine similarity for semantic search
    )
)

# Create payload indexes for metadata filtering
client.create_payload_index(
    collection_name="textbook_chunks",
    field_name="chapter",
    field_schema="keyword"
)

client.create_payload_index(
    collection_name="textbook_chunks",
    field_name="section",
    field_schema="keyword"
)
```

## Data Retention & Privacy

### Conversation Data
- **Retention**: 90 days (configurable via env var `CONVERSATION_RETENTION_DAYS`)
- **Deletion**: Automated cleanup job (daily cron, deletes conversations older than retention period)
- **Privacy**: No user auth = no PII stored, session IDs are ephemeral browser-generated UUIDs

### Content Chunks
- **Retention**: Indefinite (textbook content)
- **Updates**: New content ingestion creates new chunks, old chunks marked as `archived: true` (soft delete)
- **Versioning**: Chunk metadata includes `content_version` for tracking changes

## Performance Considerations

### Query Optimization
- **Postgres**: Use connection pooling, prepared statements, index-only scans where possible
- **Qdrant**: Batch upserts (100 chunks/batch), use filters to reduce search space

### Caching
- **Content Chunks**: Cache frequently retrieved chunks in Redis (future optimization if needed)
- **Embeddings**: Cache generated embeddings to avoid re-computing for identical text

### Scalability
- **Current Scale**: 2K chunks, 50K messages/month → well within free tier limits
- **Growth Path**: Qdrant (1M vectors), Neon (0.5GB) → upgrade when approaching 50% capacity
