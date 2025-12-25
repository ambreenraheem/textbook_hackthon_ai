# Physical AI & Humanoid Robotics - Interactive Textbook Platform

An interactive educational platform combining a comprehensive robotics textbook with an AI-powered chatbot for contextual learning assistance.

## 🎯 Project Overview

This platform provides students and educators with:

- **📚 Comprehensive Textbook**: Docusaurus-based website covering Physical AI and Humanoid Robotics topics
- **🤖 AI Chatbot**: RAG-powered assistant with citations linking directly to textbook content
- **💬 Contextual Q&A**: Highlight any text to get detailed explanations with relevant context
- **💻 Hands-On Exercises**: Copy-paste code examples for practical learning

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Docusaurus)                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  Textbook  │  │  Chatbot   │  │  Text Selection Q&A  │  │
│  │   Pages    │  │   Widget   │  │      Handler         │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ SSE (Server-Sent Events)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │  Chat API  │  │    RAG     │  │   LLM Integration    │  │
│  │ /api/chat  │  │  Pipeline  │  │  (OpenAI GPT-4)      │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
┌────────▼──────────┐        ┌──────────▼────────┐
│  Qdrant Cloud     │        │  Neon Postgres    │
│  (Vector DB)      │        │  (Conversations)  │
│  - Embeddings     │        │  - Messages       │
│  - Hybrid Search  │        │  - Sessions       │
└───────────────────┘        └───────────────────┘
```

## 🚀 Tech Stack

### Frontend
- **Docusaurus 3.9.2**: Static site generator optimized for documentation
- **React 18.3.1**: UI components
- **TypeScript 5.x**: Type-safe development
- **Tailwind CSS**: Styling

### Backend
- **FastAPI 0.104.1**: High-performance async API framework
- **Python 3.10+**: Modern Python features
- **Uvicorn**: ASGI server
- **Pydantic 2.5.0**: Data validation

### AI/RAG Pipeline
- **OpenAI GPT-4 Turbo**: Language model for chat responses
- **text-embedding-3-small**: 1536-dim embeddings
- **LangChain 0.1.0**: RAG orchestration
- **Qdrant Cloud**: Vector database (1M vectors free tier)
- **Hybrid Search**: Vector + BM25 + Cross-encoder reranking

### Databases
- **Qdrant Cloud**: Vector embeddings + metadata
- **Neon Serverless Postgres**: Conversations + messages

### Deployment
- **GitHub Pages**: Frontend hosting (static site)
- **Render/Railway**: Backend API hosting
- **GitHub Actions**: CI/CD pipelines

## 📋 Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18.x+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **OpenAI API Key** ([Get one](https://platform.openai.com/signup))
- **Qdrant Cloud Account** ([Free tier](https://cloud.qdrant.io/))
- **Neon Postgres Account** ([Free tier](https://neon.tech/))

## 🛠️ Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/ambreenraheem/textbook_hackthon_ai.git
cd textbook_hackthon_ai
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```env
OPENAI_API_KEY=sk-proj-...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-key
DATABASE_URL=postgresql://user:pass@host/db
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run tests
pytest

# Start server
uvicorn src.api.main:app --reload
```

Backend will be available at http://localhost:8000

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start
```

Frontend will be available at http://localhost:3000

## 📚 Documentation

- **[Quickstart Guide](specs/001-robotics-textbook-platform/quickstart.md)**: Detailed setup instructions (<15 min)
- **[Specification](specs/001-robotics-textbook-platform/spec.md)**: Full requirements and user stories
- **[Implementation Plan](specs/001-robotics-textbook-platform/plan.md)**: Technical architecture and design
- **[Task Breakdown](specs/001-robotics-textbook-platform/tasks.md)**: 90 implementation tasks across 7 phases
- **[API Specification](specs/001-robotics-textbook-platform/contracts/api-spec.yaml)**: OpenAPI 3.1 contract
- **[RAG Pipeline](specs/001-robotics-textbook-platform/contracts/rag-pipeline.md)**: Component contracts
- **[Data Model](specs/001-robotics-textbook-platform/data-model.md)**: Entity schemas

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/
pytest tests/contract/
```

### Frontend Tests

```bash
cd frontend

# Run component tests
npm test

# Run E2E tests
npm run test:e2e
```

## 🎓 Features by Priority

### P1: Browse Textbook Content (MVP) ✅
- Docusaurus-based textbook with 10 chapters
- Search functionality
- Responsive design
- Code highlighting

### P2: Intelligent Chatbot (Key Differentiator)
- RAG-powered Q&A
- Hybrid search (vector + keyword)
- Citations with direct links
- Streaming responses

### P3: Text Selection Q&A
- Highlight any text in the textbook
- "Ask about this" popup
- Contextual chatbot queries

### P4: Hands-On Exercises
- Python code examples
- Copy-to-clipboard functionality
- Interactive exercises

## 📈 Project Status

**Current Phase**: Phase 1 - Setup ✅ COMPLETED

### Completed Tasks (6/90):
- ✅ T001: Project root structure
- ✅ T002: Python backend initialization
- ✅ T003: Docusaurus frontend initialization
- ✅ T004: Environment configuration
- ✅ T005: Backend dependencies
- ✅ T006: Gitignore setup

### Next Phase: Phase 2 - Foundational Infrastructure (11 tasks)
- Database setup (Neon Postgres + Qdrant)
- Backend core (FastAPI app, middleware, schemas)
- **BLOCKING**: All user stories depend on Phase 2 completion

## 🤝 Development Workflow

This project follows **Spec-Driven Development (SDD)** with strict **Test-Driven Development (TDD)**:

1. **Specification**: Requirements documented in `specs/`
2. **Planning**: Architecture in `plan.md`, research in `research.md`
3. **Tasks**: Broken down in `tasks.md` with dependencies
4. **TDD**: Tests written first (Red → Green → Refactor)
5. **Implementation**: Code with 80%+ coverage
6. **Integration Testing**: End-to-end validation

### Constitution Principles

All development follows 7 core principles:

1. **Educational Excellence**: Content quality first
2. **RAG-First Architecture**: Citations, context, accuracy
3. **Skills-Based Development**: 10 specialized skill areas
4. **TDD (NON-NEGOTIABLE)**: Tests before implementation
5. **Integration Testing**: E2E validation required
6. **Observability & Performance**: Logging, metrics, targets
7. **Simplicity & YAGNI**: No premature optimization

See [Constitution]((.specify/memory/constitution.md) for details.

## 🔧 Specialized Skills

This project utilizes 10 specialized development skills:

| Skill | Responsibility | Phase |
|-------|---------------|-------|
| **content-writer** | Textbook chapters, exercises | 3, 6, 7 |
| **docusaurus-developer** | Site config, sidebars, theme | 3, 6 |
| **frontend-designer** | React components, CSS, UX | 3, 4, 5 |
| **chatbot-engineer** | Chat widget, SSE client | 4, 5 |
| **rag-specialist** | Retrieval, chunking, reranking | 4 |
| **backend-engineer** | FastAPI endpoints, middleware | 2, 4, 7 |
| **database-engineer** | SQLAlchemy, Alembic migrations | 2 |
| **vector-db-specialist** | Qdrant setup, indexing | 2, 4 |
| **deployment-expert** | CI/CD, Docker, hosting | 1, 7 |
| **integration-specialist** | E2E tests, validation | 5, 7 |

See [Skills README](.claude/skills/README.md) for details.

## 📊 Performance Targets

- **Page Load**: <2s p95 (target: 1.5s median)
- **RAG Retrieval**: <200ms p95 (target: 100ms median)
- **LLM First Token**: <1s p95
- **Chat Endpoint**: <500ms p95 total latency
- **Precision@5**: ≥80% for relevant chunks
- **Test Coverage**: ≥80% for backend/RAG

## 🐛 Troubleshooting

See [Quickstart Guide - Troubleshooting](specs/001-robotics-textbook-platform/quickstart.md#troubleshooting) for common issues.

## 📜 License

ISC License

## 🙏 Acknowledgments

Built with:
- [Docusaurus](https://docusaurus.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Qdrant](https://qdrant.tech/)
- [OpenAI](https://openai.com/)
- [Neon](https://neon.tech/)

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**
