# Backend Engineer Skill

## Metadata
- **Skill Name**: backend-engineer
- **Job**: FastAPI backend development for chatbot and data management
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Builds and maintains the FastAPI backend that powers the RAG chatbot, manages Neon Postgres database operations, and integrates with Qdrant vector database.

## Example Tasks
- Design and implement FastAPI REST API
- Create database models and schemas
- Implement authentication and authorization
- Build chat endpoint with streaming support
- Create content ingestion pipeline
- Implement caching layer
- Set up logging and monitoring
- Write API documentation

## Required Knowledge
- Python 3.10+
- FastAPI framework
- SQLAlchemy ORM
- Pydantic models
- Async/await patterns
- PostgreSQL
- RESTful API design
- Authentication (JWT, OAuth)

## Key Technologies
- FastAPI
- Python 3.10+
- SQLAlchemy 2.x
- Pydantic v2
- Uvicorn (ASGI server)
- PostgreSQL (Neon)
- Qdrant client
- OpenAI Python SDK

## Project Structure
```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── dependencies.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── content.py
│   │   └── health.py
│   ├── core/
│   │   ├── security.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── content.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── content.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py
│   │   ├── chat_service.py
│   │   └── content_service.py
│   └── db/
│       ├── __init__.py
│       ├── session.py
│       └── base.py
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## Workflow Steps

### 1. Initialize FastAPI Project
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Physical AI Textbook API",
    description="RAG-powered chatbot API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Database Configuration
```python
# db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")  # Neon Postgres URL

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### 3. Define Models
```python
# models/chat.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from .base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

### 4. Create Pydantic Schemas
```python
# schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    selected_text: Optional[str] = None
    page_context: Optional[str] = None
    conversation_id: Optional[str] = None

class Citation(BaseModel):
    text: str
    source: str
    page_url: str

class ChatResponse(BaseModel):
    response: str
    citations: List[Citation]
    conversation_id: str
    timestamp: datetime
```

### 5. Implement Chat Endpoint
```python
# api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.rag_service import RAGService
from ..db.session import get_db

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    rag_service: RAGService = Depends()
):
    try:
        # Retrieve relevant context from Qdrant
        context = await rag_service.retrieve_context(
            query=request.message,
            selected_text=request.selected_text,
            page_context=request.page_context
        )

        # Generate response using OpenAI
        response = await rag_service.generate_response(
            user_message=request.message,
            context=context
        )

        # Save to database
        # ... (database operations)

        return ChatResponse(
            response=response.content,
            citations=response.citations,
            conversation_id=conversation_id,
            timestamp=datetime.now()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 6. Implement Streaming Endpoint
```python
from fastapi.responses import StreamingResponse
import json

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    rag_service: RAGService = Depends()
):
    async def event_generator():
        async for chunk in rag_service.generate_response_stream(
            user_message=request.message,
            context=context
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

## Integration Points
- **chatbot-engineer**: Provides API endpoints
- **database-engineer**: Uses database schema
- **rag-specialist**: Implements RAG logic
- **vector-db-specialist**: Integrates Qdrant operations

## API Endpoints

### Chat Endpoints
- `POST /api/chat` - Send message and get response
- `POST /api/chat/stream` - Stream response with SSE
- `GET /api/chat/history/{conversation_id}` - Get conversation history
- `DELETE /api/chat/{conversation_id}` - Delete conversation

### Content Endpoints
- `POST /api/content/ingest` - Ingest new content
- `GET /api/content/search` - Search content
- `PUT /api/content/{id}` - Update content
- `DELETE /api/content/{id}` - Delete content

### Health Endpoints
- `GET /api/health` - Health check
- `GET /api/health/db` - Database health
- `GET /api/health/qdrant` - Qdrant health

## Environment Variables
```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
QDRANT_URL=https://xyz.qdrant.io
QDRANT_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_secret_key
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Success Criteria
- [ ] All API endpoints respond correctly
- [ ] Database operations are async and performant
- [ ] Streaming responses work smoothly
- [ ] Error handling is comprehensive
- [ ] API documentation is auto-generated
- [ ] Rate limiting is implemented
- [ ] Logging and monitoring are set up
- [ ] Tests cover >80% of code

## Testing
```python
# tests/test_chat.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_chat_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={
                "message": "What is physical AI?",
                "page_context": "/intro"
            }
        )
        assert response.status_code == 200
        assert "response" in response.json()
```

## Best Practices
- Use async/await for all I/O operations
- Implement proper error handling and logging
- Use dependency injection
- Validate all inputs with Pydantic
- Implement rate limiting
- Use connection pooling
- Cache frequent queries
- Version your API (e.g., /v1/chat)
- Document with OpenAPI/Swagger
- Implement health checks
- Use environment variables for config
- Write comprehensive tests

## Performance Optimization
- Use database connection pooling
- Implement Redis caching
- Use async operations throughout
- Optimize database queries
- Implement pagination
- Use background tasks for heavy operations
- Monitor with application performance monitoring (APM)

## Security Considerations
- Validate and sanitize all inputs
- Implement rate limiting
- Use HTTPS in production
- Implement CORS properly
- Hash sensitive data
- Use parameterized queries (SQLAlchemy handles this)
- Implement proper authentication
- Log security events
- Keep dependencies updated

## Output Artifacts
- FastAPI application code
- Database models and migrations
- API schemas (Pydantic)
- Service layer implementations
- API documentation (auto-generated)
- Environment configuration templates
- Docker configuration
- Test suite
