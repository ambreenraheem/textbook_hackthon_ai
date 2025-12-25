# Implementation Plan: Physical AI & Humanoid Robotics Interactive Textbook Platform

**Branch**: `001-robotics-textbook-platform` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-robotics-textbook-platform/spec.md`

## Summary

Build an interactive educational platform combining a Docusaurus-based textbook website with an intelligent RAG-powered chatbot. The platform delivers comprehensive Physical AI and Humanoid Robotics curriculum content with real-time question answering, text selection-based contextual help, and hands-on coding exercises. Implementation follows a 4-phase prioritized approach: P1 (textbook content and navigation), P2 (RAG chatbot with citations), P3 (text selection Q&A), P4 (interactive exercises).

**Technical Approach**: Web application architecture with decoupled frontend (Docusaurus + React) and backend (FastAPI + RAG pipeline). Content ingestion pipeline processes markdown chapters into vector embeddings stored in Qdrant. Hybrid search (vector + BM25) with reranking ensures accurate retrieval. Streaming LLM responses provide instant user feedback. GitHub Actions CI/CD enables automated deployment to GitHub Pages (frontend) and Render/Railway (backend).

## Technical Context

**Language/Version**: Python 3.10+ (backend), TypeScript 5.x + Node.js 18+ (frontend)
**Primary Dependencies**:
- **Frontend**: Docusaurus 3.x, React 18, Tailwind CSS 3.x, Framer Motion
- **Backend**: FastAPI 0.104+, Pydantic 2.x, Uvicorn, LangChain 0.1.x
- **AI/LLM**: OpenAI Python SDK 1.x (GPT-4 for chat, text-embedding-3-small for embeddings)
- **Databases**: Neon Serverless Postgres (conversations), Qdrant Cloud Free Tier (vector store)
- **DevOps**: GitHub Actions, Docker, pytest, Playwright

**Storage**:
- **Vector DB**: Qdrant Cloud (1536-dim vectors, HNSW index, metadata filtering)
- **Relational DB**: Neon Serverless Postgres (conversations, sessions, logs)
- **Static Assets**: GitHub Pages CDN (built Docusaurus site)

**Testing**:
- **Backend**: pytest + pytest-asyncio (unit, integration, contract tests)
- **Frontend**: Vitest + React Testing Library (component tests), Playwright (E2E)
- **RAG Pipeline**: Custom retrieval quality metrics (precision@k, NDCG)

**Target Platform**:
- **Frontend**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- **Backend**: Linux containers on Render/Railway (Docker-based deployment)
- **Development**: Windows/macOS/Linux (cross-platform support)

**Project Type**: Web application (Option 2: frontend + backend separation)

**Performance Goals**:
- Page load: <2s p95 for Docusaurus pages (target: 1.5s median)
- Search indexing: <5min for full textbook rebuild
- RAG retrieval: <200ms p95 for vector search (target: 100ms median)
- LLM first token: <1s p95 (streaming enabled)
- Chat endpoint: <500ms p95 total latency (retrieve + generate)
- Concurrent users: 1,000 simultaneous chatbot sessions
- Embedding generation: <10s for 10,000-word chapter

**Constraints**:
- API rate limits: OpenAI (10,000 TPM tier 1), Qdrant Cloud Free (1M vectors, 100 QPS)
- Memory: Backend container <512MB base (scales to 2GB under load)
- Storage: Neon Free Tier (0.5GB), GitHub Pages (1GB total repo size)
- Latency: <3s p95 end-to-end chatbot response time
- Accessibility: WCAG 2.1 Level AA compliance mandatory
- Security: No user auth required, but input validation and rate limiting essential

**Scale/Scope**:
- Content: 10 major chapters, ~50 sections, ~100,000 words total
- Users: 1,000 peak concurrent, ~10,000 monthly active students
- Conversations: ~5,000 chat sessions/month, 50,000 messages/month
- Embeddings: ~2,000 content chunks (avg 500 tokens each)
- Deployment: Single production environment, GitHub Pages for static site

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Educational Excellence ✅ PASS
- ✅ Content structure optimizes for both human reading (Docusaurus) and RAG retrieval (semantic chunking)
- ✅ Each chapter includes hands-on exercises (P4 user story)
- ✅ Code examples are syntax-highlighted and copy-able
- ✅ Peer review enforced via PR process before content deployment

### II. RAG-First Architecture ✅ PASS
- ✅ Hybrid search (vector + BM25) with reranking pipeline designed
- ✅ Chatbot citations link directly to textbook sections (FR-012, FR-032)
- ✅ Text selection-based Q&A implemented (P3 user story, FR-018)
- ✅ Retrieval quality metrics tracked (precision@k, NDCG in observability)

### III. Skills-Based Development ✅ PASS
- ✅ All 10 skills explicitly mapped to implementation phases:
  - **P1**: content-writer, docusaurus-developer, frontend-designer
  - **P2**: rag-specialist, chatbot-engineer, backend-engineer, database-engineer, vector-db-specialist
  - **P3**: integration-specialist (text selection), chatbot-engineer
  - **P4**: content-writer (exercises), docusaurus-developer
  - **Continuous**: deployment-expert (CI/CD)
- ✅ Skill boundaries respected: frontend (Docusaurus), backend (FastAPI), RAG (LangChain), deployment (GitHub Actions)

### IV. Test-Driven Development ✅ PASS
- ✅ TDD enforced for backend (pytest before implementation)
- ✅ TDD enforced for RAG pipeline (retrieval quality tests before ingestion logic)
- ✅ 80% coverage target for backend + RAG (measured via pytest-cov)
- ✅ Contract tests for all API endpoints (Pydantic schemas + test fixtures)

### V. Integration Testing ✅ PASS
- ✅ End-to-end RAG pipeline: markdown → chunking → embedding → retrieval → LLM response
- ✅ API contract tests: FastAPI endpoints with request/response validation
- ✅ Frontend-backend integration: chatbot widget → API → streaming response
- ✅ Text selection integration: browser event → API context → RAG retrieval
- ✅ Deployment validation: build → deploy → smoke tests

### VI. Observability & Performance ✅ PASS
- ✅ Structured logging with correlation IDs (Python logging + FastAPI middleware)
- ✅ Performance metrics: latency (p95, p99), throughput, error rates
- ✅ RAG quality metrics: retrieval precision, embedding generation time, LLM latency
- ✅ Frontend metrics: page load time, widget interaction latency
- ✅ Performance targets met: <2s page load, <200ms retrieval, <1s first token, <500ms API response

### VII. Simplicity & YAGNI ✅ PASS
- ✅ Proven tech stack only: Docusaurus, FastAPI, OpenAI, Qdrant, Neon
- ✅ No premature optimization: start with simple chunking, improve if retrieval quality insufficient
- ✅ No unnecessary abstractions: direct API calls, straightforward data models
- ✅ Reasonable defaults: 500-token chunks, 5 retrieval results, 0.7 similarity threshold

**Constitution Check Status**: ✅ ALL GATES PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/001-robotics-textbook-platform/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── api-spec.yaml    # OpenAPI 3.1 spec for FastAPI endpoints
│   └── rag-pipeline.md  # RAG pipeline contract (input/output formats)
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend)

backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── chat.py                    # /api/chat endpoint (streaming)
│   │   ├── health.py                  # /api/health endpoint
│   │   └── middleware.py              # CORS, logging, error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── conversation.py            # SQLAlchemy models (Neon Postgres)
│   │   └── schemas.py                 # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag.py                     # RAG pipeline orchestration
│   │   ├── retrieval.py               # Qdrant vector search + BM25 hybrid
│   │   ├── reranking.py               # Cross-encoder reranking
│   │   ├── embeddings.py              # OpenAI embedding generation
│   │   └── llm.py                     # OpenAI chat completion (streaming)
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── chunker.py                 # Semantic chunking for markdown
│   │   ├── parser.py                  # Markdown parsing with metadata
│   │   └── pipeline.py                # End-to-end ingestion orchestration
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                 # Structured logging setup
│       └── config.py                  # Environment variable configuration
├── tests/
│   ├── contract/
│   │   ├── test_api_chat.py           # API contract tests
│   │   └── test_schemas.py            # Pydantic schema validation
│   ├── integration/
│   │   ├── test_rag_pipeline.py       # End-to-end RAG flow
│   │   └── test_database.py           # Neon Postgres integration
│   └── unit/
│       ├── test_chunker.py            # Chunking logic
│       ├── test_retrieval.py          # Qdrant queries
│       └── test_reranking.py          # Reranking algorithm
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Backend container image
└── README.md                          # Backend setup instructions

frontend/
├── docs/                              # Docusaurus content directory
│   ├── intro.md                       # Homepage
│   ├── chapters/
│   │   ├── 01-introduction/           # Chapter 1: Introduction to Physical AI
│   │   ├── 02-kinematics/             # Chapter 2: Robot Kinematics
│   │   ├── 03-dynamics/               # Chapter 3: Robot Dynamics
│   │   ├── 04-control/                # Chapter 4: Control Systems
│   │   ├── 05-perception/             # Chapter 5: Perception & Sensing
│   │   ├── 06-planning/               # Chapter 6: Motion Planning
│   │   ├── 07-learning/               # Chapter 7: Robot Learning
│   │   ├── 08-manipulation/           # Chapter 8: Manipulation
│   │   ├── 09-locomotion/             # Chapter 9: Locomotion
│   │   └── 10-hri/                    # Chapter 10: Human-Robot Interaction
│   └── exercises/                     # Hands-on exercises
├── src/
│   ├── components/
│   │   ├── ChatbotWidget/             # Chatbot UI component
│   │   │   ├── index.tsx              # Main widget component
│   │   │   ├── MessageList.tsx        # Message display
│   │   │   ├── InputArea.tsx          # User input field
│   │   │   ├── CitationLink.tsx       # Clickable citation component
│   │   │   └── styles.module.css      # Widget-specific styles
│   │   └── TextSelection/             # Text selection handler
│   │       ├── index.tsx              # Selection event listener
│   │       └── SelectionPopup.tsx     # "Ask about this" popup
│   ├── services/
│   │   ├── api.ts                     # Backend API client
│   │   └── storage.ts                 # Session storage for conversation
│   ├── theme/                         # Docusaurus theme customization
│   │   └── Root.tsx                   # Global wrapper (inject chatbot)
│   └── css/
│       └── custom.css                 # Global styles
├── static/
│   └── img/                           # Diagrams and images
├── docusaurus.config.js               # Docusaurus configuration
├── sidebars.js                        # Sidebar structure
├── package.json                       # Node dependencies
└── tsconfig.json                      # TypeScript configuration

.github/
└── workflows/
    ├── frontend-deploy.yml            # GitHub Pages deployment
    └── backend-deploy.yml             # Render/Railway deployment

docs/
└── architecture.md                    # System architecture diagrams

.env.example                           # Environment variable template
README.md                              # Project root README
```

**Structure Decision**: Web application architecture selected due to:
1. Clear separation of concerns: Docusaurus (static content generation) vs FastAPI (dynamic chat API)
2. Independent scaling: Frontend on CDN (GitHub Pages), backend on cloud platform (Render/Railway)
3. Skill boundary alignment: frontend-designer/docusaurus-developer own frontend/, backend-engineer/rag-specialist own backend/
4. Deployment flexibility: Frontend changes don't require backend redeployment and vice versa

## Complexity Tracking

> **No violations detected** - Constitution Check passed all gates. This section left empty as intended.

## Phase 0: Research & Technology Decisions

*(See [research.md](./research.md) for full details)*

### Key Technology Choices

**Decision 1: Docusaurus 3.x for Frontend**
- **Rationale**: Industry-standard for technical documentation, built-in search (Algolia), MDX support for interactive components, excellent SEO, responsive by default
- **Alternatives considered**: VitePress (less mature ecosystem), GitBook (less customizable), custom Next.js (over-engineering)
- **Impact**: Faster development, proven accessibility, easy content authoring

**Decision 2: FastAPI for Backend**
- **Rationale**: Async-native (essential for streaming), automatic OpenAPI docs, Pydantic validation, excellent performance, Python ecosystem compatibility
- **Alternatives considered**: Flask (no native async), Django (too heavy), Node.js Express (team Python expertise)
- **Impact**: Type-safe API contracts, built-in validation, easy integration with LangChain/OpenAI

**Decision 3: Hybrid Search (Qdrant Vector + BM25 Keyword)**
- **Rationale**: Vector search handles semantic queries, BM25 handles exact keyword matches (equations, code, technical terms), reranking combines strengths
- **Alternatives considered**: Vector-only (misses exact matches), keyword-only (poor semantic understanding), Elasticsearch hybrid (more complex setup)
- **Impact**: Higher retrieval accuracy (target: 80%+ precision@5), handles both "explain inverse kinematics" and "show equation for PID controller"

**Decision 4: OpenAI Embeddings (text-embedding-3-small)**
- **Rationale**: Cost-effective ($0.02/1M tokens), 1536 dimensions (Qdrant free tier compatible), excellent quality, official SDK support
- **Alternatives considered**: text-embedding-3-large (higher cost, marginal quality gain), open-source BERT (lower quality, hosting complexity)
- **Impact**: Predictable costs (~$0.20 for full textbook embedding), reliable performance, easy integration

**Decision 5: Semantic Chunking Strategy**
- **Rationale**: Preserve markdown structure (headings as boundaries), target 400-600 tokens/chunk (fits context window, good retrieval granularity), include metadata (chapter, section, page)
- **Alternatives considered**: Fixed-size chunking (breaks mid-sentence), sentence-level (too granular, retrieval noise)
- **Impact**: Better citation accuracy (references align with content structure), improved retrieval relevance

**Decision 6: Streaming LLM Responses**
- **Rationale**: Perceived performance boost (first token <1s), progress feedback (typing indicator), better UX for long answers
- **Alternatives considered**: Non-streaming (simpler but feels slow), Server-Sent Events vs WebSocket (SSE sufficient for one-way streaming)
- **Impact**: User engagement improvement, reduced perceived latency

## Phase 1: Design & Contracts

### Data Model

*(See [data-model.md](./data-model.md) for full details)*

#### Entity: ContentChunk (Qdrant Vector DB)
- **Fields**:
  - `id` (UUID): Unique chunk identifier
  - `text` (string): Chunk content (400-600 tokens)
  - `vector` (float[]): 1536-dim embedding
  - `chapter` (string): Chapter title
  - `section` (string): Section heading
  - `page` (integer): Logical page number
  - `url` (string): Docusaurus URL path
  - `created_at` (timestamp)
- **Indexes**: HNSW index on vector field, metadata filters on chapter/section
- **Relationships**: Referenced by Citation entities (via chunk_id)

#### Entity: Conversation (Neon Postgres)
- **Fields**:
  - `id` (UUID, PK): Unique conversation ID
  - `session_id` (string): Browser session identifier
  - `created_at` (timestamp)
  - `updated_at` (timestamp)
- **Relationships**: Has many Message entities
- **Validation**: session_id required, timestamps auto-managed

#### Entity: Message (Neon Postgres)
- **Fields**:
  - `id` (UUID, PK): Unique message ID
  - `conversation_id` (UUID, FK): Parent conversation
  - `role` (enum): 'user' | 'assistant'
  - `content` (text): Message text
  - `cited_chunks` (JSON[]): Array of chunk IDs referenced in response
  - `created_at` (timestamp)
- **Relationships**: Belongs to Conversation
- **Validation**: role in ['user', 'assistant'], content non-empty

### API Contracts

*(See [contracts/api-spec.yaml](./contracts/api-spec.yaml) for OpenAPI spec)*

#### Endpoint: POST /api/chat
- **Purpose**: Submit user question, receive streaming RAG-enhanced answer
- **Request**:
  ```json
  {
    "session_id": "string (UUID)",
    "message": "string (1-2000 chars)",
    "selected_text": "string | null (optional context)",
    "conversation_id": "string (UUID) | null"
  }
  ```
- **Response**: Server-Sent Events stream
  ```
  event: token
  data: {"token": "string"}

  event: citation
  data: {"chunk_id": "uuid", "chapter": "string", "section": "string", "url": "string"}

  event: done
  data: {"conversation_id": "uuid", "message_id": "uuid"}
  ```
- **Errors**: 400 (invalid request), 429 (rate limit), 500 (server error)

#### Endpoint: GET /api/health
- **Purpose**: Health check for deployment monitoring
- **Response**:
  ```json
  {
    "status": "healthy",
    "services": {
      "database": "ok",
      "vector_db": "ok",
      "openai": "ok"
    }
  }
  ```

### Developer Quickstart

*(See [quickstart.md](./quickstart.md) for full guide)*

**Prerequisites**: Python 3.10+, Node.js 18+, Docker (optional)

**Setup Steps**:
1. Clone repo: `git clone <repo> && cd <repo>`
2. Backend setup:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   cp ../.env.example .env  # Fill in OPENAI_API_KEY, DATABASE_URL, QDRANT_URL
   pytest  # Run tests
   uvicorn src.api.main:app --reload  # Start dev server
   ```
3. Frontend setup:
   ```bash
   cd frontend
   npm install
   npm start  # Start Docusaurus dev server (localhost:3000)
   ```
4. Ingestion pipeline:
   ```bash
   cd backend
   python -m src.ingestion.pipeline --input ../frontend/docs --output ./chunks.json
   ```

**Architecture Overview**:
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Docusaurus │         │   FastAPI    │         │   OpenAI    │
│  (Frontend) │────────▶│   Backend    │────────▶│   API       │
│             │  HTTP   │              │  HTTP   │             │
│  Chatbot    │◀────────│  RAG Pipeline│◀────────│  LLM +      │
│  Widget     │  SSE    │              │         │  Embeddings │
└─────────────┘         └──────┬───────┘         └─────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼──────┐       ┌──────▼─────┐
              │   Qdrant   │       │    Neon    │
              │  (Vectors) │       │ (Postgres) │
              └────────────┘       └────────────┘
```

## Next Steps

1. **Run `/sp.tasks`** to generate implementation task breakdown
2. **Content Creation**: Write initial 2-3 chapters (content-writer skill)
3. **Backend Development**: Implement RAG pipeline (TDD, 80% coverage target)
4. **Frontend Integration**: Build chatbot widget, integrate with Docusaurus
5. **Deployment**: Set up GitHub Actions CI/CD, deploy to staging
6. **Testing**: End-to-end validation, performance benchmarking, accessibility audit
7. **Iteration**: Measure retrieval quality, tune chunking/reranking, optimize performance
