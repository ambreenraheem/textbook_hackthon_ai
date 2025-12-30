# Backend API - Physical AI Textbook Platform

FastAPI-powered backend providing RAG (Retrieval-Augmented Generation) chatbot functionality for the Physical AI & Humanoid Robotics textbook platform.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /api/chat          - Streaming chat endpoint (SSE)         │
│  /api/health        - Health check (Postgres + Qdrant)      │
│  /api/ping          - Simple availability check             │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                     RAG Pipeline                             │
│  ┌───────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │  Parser   │─>│  Chunker   │─>│  Embedding Generator │   │
│  └───────────┘  └────────────┘  └─────────────────────┘    │
│         │                                    │               │
│         v                                    v               │
│  ┌───────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │ Retrieval │<─│  Qdrant    │<─│   LLM Integration   │    │
│  └───────────┘  └────────────┘  └─────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Tech Stack

- **Framework**: FastAPI 0.104.1 (async, high-performance)
- **Language**: Python 3.11+
- **Server**: Uvicorn (ASGI)
- **AI/LLM**: OpenAI GPT-4 Turbo + text-embedding-3-small
- **RAG**: LangChain 0.1.0
- **Vector DB**: Qdrant Cloud
- **Database**: Neon Serverless Postgres (SQLAlchemy + asyncpg)
- **Validation**: Pydantic 2.5.0

## 📋 Prerequisites

- Python 3.11 or higher
- pip package manager
- OpenAI API key ([Get one](https://platform.openai.com/signup))
- Qdrant Cloud account ([Free tier](https://cloud.qdrant.io/))
- Neon Postgres account ([Free tier](https://neon.tech/))

## 🛠️ Local Development Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp ../.env.example ../.env
# Edit .env with your API keys
```

Required environment variables:
```env
# OpenAI
OPENAI_API_KEY=sk-...

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key

# Neon Postgres
DATABASE_URL=postgresql://user:pass@host/db

# Application
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### 4. Initialize Database

```bash
# Create tables
python -m alembic upgrade head

# Or run initialization script (if available)
python -m src.utils.database
```

### 5. Set Up Qdrant Collection

```bash
python -m src.utils.qdrant_setup
```

### 6. Run Development Server

```bash
# From backend/ directory
uvicorn src.api.main:app --reload --port 8000

# Or use Python directly
python -m src.api.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Health & Monitoring

#### `GET /api/health`
Comprehensive health check for all services.

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "timestamp": 1703001234.567,
  "services": {
    "postgres": {
      "status": "healthy",
      "latency_ms": 45.32,
      "message": "PostgreSQL connection successful"
    },
    "qdrant": {
      "status": "healthy",
      "latency_ms": 123.45,
      "collections": ["textbook_chunks"],
      "message": "Qdrant connected (1 collections)"
    },
    "openai": {
      "status": "healthy",
      "latency_ms": 234.56,
      "message": "OpenAI API accessible"
    }
  }
}
```

#### `GET /api/ping`
Simple availability check.

**Response (200 OK)**:
```json
{
  "status": "ok",
  "message": "pong",
  "timestamp": 1703001234.567
}
```

### Chat

#### `POST /api/chat`
Streaming chat endpoint with RAG-powered responses.

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "What is Physical AI?",
  "conversation_id": "optional-uuid",
  "selected_text": "optional-highlighted-text"
}
```

**Response**: Server-Sent Events (SSE) stream

Event types:
1. `token`: Streaming text tokens
```
event: token
data: {"content": "Physical AI "}
```

2. `citation`: Reference to textbook content
```
event: citation
data: {"page_id": "ch01-intro", "title": "Introduction to Physical AI", "url": "/docs/ch01"}
```

3. `done`: Stream completion
```
event: done
data: {"conversation_id": "uuid", "message_id": "uuid", "total_tokens": 1234}
```

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### Run Specific Test File

```bash
pytest tests/unit/test_retrieval.py -v
```

## 🗂️ Project Structure

```
backend/
├── src/
│   ├── api/               # API endpoints
│   │   ├── main.py        # FastAPI app + middleware
│   │   ├── chat.py        # Chat endpoint (SSE streaming)
│   │   └── health.py      # Health check endpoints
│   ├── config/            # Configuration
│   │   └── settings.py    # Environment variables
│   ├── models/            # Data models
│   │   ├── conversation.py  # SQLAlchemy models
│   │   └── schemas.py     # Pydantic schemas
│   ├── services/          # Business logic
│   │   ├── embeddings.py  # OpenAI embeddings
│   │   ├── retrieval.py   # Hybrid search (vector + BM25)
│   │   ├── rag.py         # RAG pipeline orchestration
│   │   └── llm.py         # OpenAI GPT-4 integration
│   ├── ingestion/         # Content ingestion pipeline
│   │   ├── parser.py      # Markdown parser
│   │   ├── chunker.py     # Semantic chunking
│   │   └── pipeline.py    # End-to-end ingestion
│   └── utils/             # Utilities
│       ├── database.py    # SQLAlchemy setup
│       ├── qdrant_setup.py  # Qdrant initialization
│       └── app_logging.py   # Structured logging
├── tests/                 # Test suite
│   ├── unit/
│   ├── integration/
│   └── contract/
├── alembic/               # Database migrations
├── Dockerfile             # Production container
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Deployment

### Docker Build

```bash
docker build -t physical-ai-backend .
docker run -p 8000:8000 --env-file ../.env physical-ai-backend
```

### Render Deployment

1. Connect GitHub repository to Render
2. Create new Web Service
3. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
4. Add environment variables in Render dashboard
5. Deploy!

See [docs/deployment.md](../docs/deployment.md) for detailed deployment guides.

## 🔧 Common Tasks

### Ingest Textbook Content

```bash
# Ingest all chapters
python -m src.ingestion.pipeline --input ../frontend/docs/chapters --rebuild

# Ingest specific directory
python -m src.ingestion.pipeline --input ../frontend/docs/part-01-foundations
```

### Create Database Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### View Logs

```bash
# Development (stdout)
tail -f logs/app.log

# Production (Render)
# View logs in Render dashboard
```

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test connection
python -c "from src.utils.database import SessionLocal; db = SessionLocal(); print('✅ Connected')"
```

### Qdrant Connection Issues

```bash
# Test Qdrant
python -c "from qdrant_client import QdrantClient; from src.config.settings import settings; client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY); print(client.get_collections())"
```

### OpenAI API Issues

```bash
# Test OpenAI
python -c "from openai import OpenAI; from src.config.settings import settings; client = OpenAI(api_key=settings.OPENAI_API_KEY); print(client.models.list())"
```

## 📝 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test: `pytest`
3. Commit: `git commit -m "feat: add your feature"`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

## 📄 License

See [LICENSE](../LICENSE) in root directory.

## 🔗 Related Documentation

- [Root README](../README.md) - Project overview
- [Frontend README](../frontend/README.md) - Docusaurus frontend
- [Deployment Guide](../docs/deployment.md) - Production deployment
- [API Specification](../specs/001-robotics-textbook-platform/contracts/api-spec.yaml) - OpenAPI spec
