# Research & Technology Decisions: Physical AI & Humanoid Robotics Interactive Textbook Platform

**Date**: 2025-12-26
**Feature**: 001-robotics-textbook-platform
**Purpose**: Document all technology choices, research findings, and rationale for implementation decisions

## Research Questions & Resolutions

### RQ-001: Frontend Framework Selection

**Question**: Which framework should we use for the interactive textbook website?

**Research Conducted**:
- Evaluated Docusaurus 3.x, VitePress, GitBook, custom Next.js solution
- Analyzed documentation site best practices (2024 industry standards)
- Compared SEO capabilities, accessibility support, content authoring DX
- Reviewed MDX support for interactive components
- Assessed built-in search capabilities and performance

**Decision**: **Docusaurus 3.x**

**Rationale**:
1. **Industry Standard**: Used by Meta, Microsoft, Stripe for technical docs - proven at scale
2. **Built-in Features**: Algolia DocSearch integration, versioning, i18n support, dark mode
3. **MDX Support**: Allows embedding React components directly in markdown for interactive content
4. **SEO & Accessibility**: Excellent out-of-box SEO, WCAG 2.1 AA compliant by default
5. **Developer Experience**: Hot reload, plugin ecosystem, easy content authoring
6. **Performance**: Static site generation ensures fast page loads (<2s target achievable)

**Alternatives Considered**:
- **VitePress**: Faster build times but less mature ecosystem, limited plugin support
- **GitBook**: Beautiful UI but less customizable, paid tiers for advanced features
- **Custom Next.js**: Over-engineering for documentation site, slower development time

**Impact**: Enables rapid content authoring, ensures accessibility compliance, provides professional documentation UX

---

### RQ-002: Backend Framework for RAG Pipeline

**Question**: Which Python framework should handle the RAG chatbot API?

**Research Conducted**:
- Compared FastAPI, Flask, Django for async API support
- Evaluated streaming response capabilities (Server-Sent Events)
- Reviewed automatic API documentation generation
- Assessed Pydantic integration for request/response validation
- Analyzed performance benchmarks for async workloads

**Decision**: **FastAPI 0.104+**

**Rationale**:
1. **Async Native**: Built on Starlette/Uvicorn - essential for streaming LLM responses without blocking
2. **Automatic Documentation**: OpenAPI/Swagger UI generated from code - improves developer onboarding
3. **Pydantic Integration**: Type-safe request/response schemas - prevents runtime errors
4. **Performance**: Comparable to Node.js Express, ~3x faster than Flask for async workloads
5. **Ecosystem**: Excellent compatibility with LangChain, OpenAI SDK, SQLAlchemy

**Alternatives Considered**:
- **Flask**: No native async support (requires gevent/eventlet), manual schema validation
- **Django**: Too heavy for API-only service, REST framework adds unnecessary complexity
- **Node.js Express**: Team has stronger Python expertise, harder to integrate with ML/NLP libraries

**Impact**: Type-safe API contracts, built-in docs, efficient streaming, easy LLM integration

---

### RQ-003: Vector Database Selection

**Question**: Where should we store content embeddings for RAG retrieval?

**Research Conducted**:
- Evaluated Qdrant Cloud, Pinecone, Weaviate, ChromaDB, pgvector (Postgres extension)
- Compared free tier limits, vector dimensionality support, query performance
- Reviewed hybrid search capabilities (vector + keyword)
- Assessed metadata filtering performance
- Analyzed cloud deployment options and pricing

**Decision**: **Qdrant Cloud Free Tier**

**Rationale**:
1. **Free Tier Generosity**: 1M vectors, 100 QPS - sufficient for 2,000 textbook chunks + growth headroom
2. **Hybrid Search**: Native BM25 + vector search with reranking - critical for technical content (equations, code)
3. **Metadata Filtering**: Efficient filtering by chapter/section for citation generation
4. **HNSW Index**: Fast approximate nearest neighbor search (<100ms p95 target achievable)
5. **Cloud Managed**: No infrastructure management, automatic backups, high availability

**Alternatives Considered**:
- **Pinecone**: Similar capabilities but free tier only 100K vectors - too restrictive
- **Weaviate**: Requires self-hosting or paid cloud tier - adds operational complexity
- **ChromaDB**: In-memory only (non-free tiers) - data loss risk, scaling challenges
- **pgvector**: Extension for Neon Postgres - slower queries, no built-in BM25, limited to 2K dims

**Impact**: Scalable vector storage, hybrid search for better retrieval, managed infrastructure

---

### RQ-004: Relational Database for Conversations

**Question**: Where should we store conversation history and session data?

**Research Conducted**:
- Evaluated Neon Serverless Postgres, Supabase, PlanetScale, Railway Postgres
- Compared free tier storage limits, connection pooling, pricing
- Reviewed async driver support (asyncpg)
- Assessed backup/recovery capabilities

**Decision**: **Neon Serverless Postgres (Free Tier)**

**Rationale**:
1. **Serverless Scaling**: Auto-pause when idle - cost-effective for hackathon/demo workload
2. **Free Tier**: 0.5GB storage, 1 project - sufficient for ~50K messages
3. **PostgreSQL Compatibility**: Full Postgres features, SQLAlchemy support, JSON columns
4. **Async Support**: Works with asyncpg for FastAPI async operations
5. **Managed Service**: Automated backups, connection pooling, monitoring

**Alternatives Considered**:
- **Supabase**: Similar features but more complex setup, focused on auth (not needed)
- **PlanetScale**: MySQL-based - team more familiar with Postgres
- **Railway Postgres**: Good but Neon's serverless model better for variable traffic

**Impact**: Cost-effective conversation storage, async-ready, familiar Postgres ecosystem

---

### RQ-005: LLM and Embedding Models

**Question**: Which models should we use for chat generation and content embedding?

**Research Conducted**:
- Compared OpenAI GPT-4, GPT-3.5, Claude, open-source LLMs (Llama 2, Mistral)
- Evaluated embedding models: OpenAI text-embedding-3-small/large, Cohere, open-source (BGE, E5)
- Analyzed pricing, quality benchmarks, API reliability
- Reviewed token limits, streaming support, context windows

**Decision**:
- **Chat LLM**: **GPT-4 Turbo** (fallback to GPT-3.5 for cost optimization)
- **Embeddings**: **text-embedding-3-small (1536 dims)**

**Rationale (Chat LLM)**:
1. **Quality**: GPT-4 superior for technical explanations, handles complex robotics concepts
2. **Streaming**: Native SSE support for instant user feedback
3. **Reliability**: 99.9% uptime SLA, robust API, extensive documentation
4. **Context Window**: 128K tokens - handles long retrieval contexts + conversation history
5. **Fallback Strategy**: Can downgrade to GPT-3.5 if cost becomes issue ($0.01/1K tokens vs $0.10/1K)

**Rationale (Embeddings)**:
1. **Cost**: $0.02/1M tokens - full textbook embedding costs ~$0.20
2. **Quality**: MTEB benchmark scores competitive with larger models for Q&A tasks
3. **Dimensionality**: 1536 dims compatible with Qdrant free tier, good balance of quality/storage
4. **Consistency**: Same provider as LLM - unified API, simpler integration

**Alternatives Considered**:
- **Claude**: Excellent quality but no official vector embedding model, higher pricing
- **Open-source LLMs**: Quality gap for technical content, hosting complexity, latency issues
- **text-embedding-3-large**: Marginal quality improvement (~2% MTEB) not worth 3x cost increase

**Impact**: High-quality responses, cost-effective embeddings, reliable infrastructure

---

### RQ-006: RAG Chunking Strategy

**Question**: How should we split textbook content into chunks for embedding?

**Research Conducted**:
- Reviewed chunking strategies: fixed-size, sentence-level, semantic (markdown structure)
- Analyzed chunk size vs retrieval quality tradeoffs (100, 500, 1000, 2000 tokens)
- Evaluated metadata inclusion approaches (chapter, section, page numbers)
- Studied overlap strategies for context preservation

**Decision**: **Semantic Chunking with Markdown Structure Preservation**

**Specification**:
- **Chunk Boundaries**: Markdown headings (##, ###) define chunk start/end
- **Target Size**: 400-600 tokens per chunk (adjust if needed based on heading density)
- **Metadata**: Include chapter title, section heading, logical page number, Docusaurus URL
- **Overlap**: 50-token overlap between adjacent chunks for context continuity
- **Code Blocks**: Keep code examples intact within chunks (don't split mid-code)

**Rationale**:
1. **Content Coherence**: Headings represent semantic boundaries - chunks are topically coherent
2. **Citation Accuracy**: Citations align with textbook structure ("See Chapter 3, Section 2.1")
3. **Retrieval Quality**: 400-600 tokens balances specificity (too small = noise) vs context (too large = dilution)
4. **User Experience**: Retrieved chunks map to actual textbook sections, clickable links work correctly

**Alternatives Considered**:
- **Fixed-size (512 tokens)**: Breaks mid-sentence/mid-paragraph, poor citation UX
- **Sentence-level**: Too granular, retrieval noise, citation overload
- **Large chunks (2000 tokens)**: Dilutes relevance signal, slower LLM processing

**Impact**: Better citation UX, improved retrieval relevance, alignment with content structure

---

### RQ-007: Hybrid Search Implementation

**Question**: Should we use pure vector search or hybrid vector + keyword search?

**Research Conducted**:
- Analyzed typical user queries: semantic ("explain inverse kinematics") vs keyword ("PID equation")
- Reviewed RAG best practices for technical documentation
- Compared pure vector vs hybrid search retrieval accuracy benchmarks
- Evaluated reranking approaches (cross-encoder, LLM-based)

**Decision**: **Hybrid Search (Vector + BM25) with Cross-Encoder Reranking**

**Workflow**:
1. **Vector Search**: Qdrant similarity search → top 20 results (0.6 similarity threshold)
2. **BM25 Keyword Search**: Qdrant BM25 search → top 20 results (on same corpus)
3. **Merge**: Combine results using reciprocal rank fusion (RRF)
4. **Rerank**: Cross-encoder model (MiniLM or Cohere Rerank API) → top 5 final results
5. **LLM Context**: Pass top 5 chunks to GPT-4 with citations

**Rationale**:
1. **Technical Content Handling**: BM25 excels at finding exact equations, code snippets, technical terms
2. **Semantic Understanding**: Vector search handles natural language queries ("how does a robot arm move?")
3. **Complementary Strengths**: Hybrid retrieves 15-20% more relevant docs than vector-only (industry benchmarks)
4. **Reranking**: Cross-encoder refines ranking using query-chunk interaction, improves precision@5 by ~10%

**Alternatives Considered**:
- **Vector-only**: Misses exact keyword matches for equations, code, abbreviations
- **Keyword-only**: Poor on paraphrased/semantic queries
- **No reranking**: Suboptimal ranking, lower LLM answer quality

**Impact**: Higher retrieval accuracy (target: 80%+ precision@5), handles diverse query types

---

### RQ-008: Frontend-Backend Communication for Chatbot

**Question**: How should the chatbot widget communicate with the backend for streaming responses?

**Research Conducted**:
- Compared WebSockets, Server-Sent Events (SSE), HTTP polling
- Evaluated browser compatibility, firewall/proxy traversal
- Analyzed implementation complexity, error handling
- Reviewed streaming best practices for LLM applications

**Decision**: **Server-Sent Events (SSE) over HTTP**

**Implementation**:
- **Backend**: FastAPI `StreamingResponse` with `text/event-stream` content type
- **Frontend**: `EventSource` API for consuming SSE stream
- **Events**: `token` (LLM output), `citation` (chunk reference), `done` (completion signal)
- **Error Handling**: Automatic reconnection (EventSource built-in), exponential backoff

**Rationale**:
1. **Simplicity**: SSE is HTTP-based, easier setup than WebSockets, no upgrade handshake complexity
2. **Browser Support**: Native `EventSource` API in all modern browsers (Chrome 90+, Firefox 88+, Safari 14+)
3. **One-Way Stream**: Chatbot only needs server→client streaming (user messages via POST)
4. **Firewall/Proxy Friendly**: HTTP-based, no special ports or protocols
5. **Auto-Reconnect**: Built-in reconnection on connection loss

**Alternatives Considered**:
- **WebSockets**: Bidirectional (overkill for one-way stream), more complex error handling, firewall issues
- **HTTP Polling**: High latency, wasteful (most polls return empty), poor UX for streaming

**Impact**: Simple streaming implementation, good UX (instant feedback), reliable connection

---

### RQ-009: Deployment Strategy

**Question**: Where should we deploy the frontend and backend?

**Research Conducted**:
- Evaluated hosting options: GitHub Pages, Vercel, Netlify (frontend); Render, Railway, Fly.io, AWS (backend)
- Compared free tier limits, cold start times, deployment ease
- Reviewed CI/CD integration with GitHub Actions
- Assessed custom domain support, SSL certificates

**Decision**:
- **Frontend**: **GitHub Pages** (static site hosting)
- **Backend**: **Render Free Tier** (primary) or **Railway** (fallback)

**Rationale (GitHub Pages)**:
1. **Free**: Unlimited bandwidth for public repos, 1GB storage limit (sufficient)
2. **GitHub Actions Integration**: Native deployment workflow, automatic builds on push to main
3. **CDN**: Global edge network, excellent page load performance
4. **Custom Domain**: Free SSL certificates via Let's Encrypt
5. **Simplicity**: No configuration complexity, just push to `gh-pages` branch

**Rationale (Render)**:
1. **Free Tier**: 750 hours/month, Docker support, persistent storage (500MB)
2. **Cold Starts**: ~30s spin-up from idle (acceptable for demo/hackathon)
3. **Automatic Deploys**: GitHub integration, auto-deploy on push to main
4. **Managed Services**: Built-in health checks, logs, metrics
5. **PostgreSQL Add-on**: Free 90-day trial (Neon as primary, Render as backup)

**Alternatives Considered**:
- **Vercel/Netlify (frontend)**: Similar features but GitHub Pages simpler for Docusaurus
- **Railway (backend)**: Excellent DX but free tier ends Jan 2024 (Render more sustainable)
- **Fly.io**: Great performance but complexity overkill for simple API
- **AWS**: Over-engineering, complex pricing, steep learning curve

**Impact**: Zero-cost deployment, automated CI/CD, reliable hosting

---

### RQ-010: Testing Strategy

**Question**: What testing approach should we use to ensure quality and meet 80% coverage target?

**Research Conducted**:
- Reviewed TDD best practices for FastAPI + React applications
- Analyzed testing pyramid (unit, integration, E2E) tradeoffs
- Evaluated testing frameworks: pytest vs unittest, Vitest vs Jest, Playwright vs Cypress
- Studied RAG-specific testing approaches (retrieval quality metrics)

**Decision**: **Multi-Layer Testing Strategy**

**Backend Testing**:
- **Unit Tests** (pytest + pytest-asyncio):
  - Chunking logic (`test_chunker.py`)
  - Embedding generation (`test_embeddings.py`)
  - Reranking algorithms (`test_reranking.py`)
  - Target: 80%+ coverage

- **Integration Tests** (pytest + Docker):
  - End-to-end RAG pipeline (`test_rag_pipeline.py`)
  - Qdrant queries (`test_retrieval.py`)
  - Neon Postgres operations (`test_database.py`)

- **Contract Tests** (pytest + FastAPI TestClient):
  - API endpoint validation (`test_api_chat.py`)
  - Pydantic schema validation (`test_schemas.py`)
  - SSE streaming behavior

**Frontend Testing**:
- **Component Tests** (Vitest + React Testing Library):
  - ChatbotWidget rendering and interactions
  - TextSelection popup behavior
  - CitationLink navigation

- **End-to-End Tests** (Playwright):
  - Full user journey: browse → ask question → receive answer with citations
  - Text selection → contextual Q&A
  - Mobile responsiveness

**RAG Quality Metrics**:
- **Precision@K**: Relevant chunks in top K results (target: 80% @ K=5)
- **NDCG**: Normalized discounted cumulative gain (ranking quality)
- **Citation Accuracy**: % of citations that correctly link to content (target: 95%)

**Rationale**:
1. **TDD Compliance**: Write tests before implementation (constitution requirement)
2. **Fast Feedback**: Unit tests run in <5s, integration tests <30s
3. **Confidence**: Integration + E2E tests catch cross-component issues
4. **Quality Metrics**: RAG-specific metrics ensure retrieval quality

**Impact**: High confidence in deployments, early bug detection, measurable quality

---

## Technology Stack Summary

### Frontend
- **Framework**: Docusaurus 3.x
- **UI Library**: React 18
- **Styling**: Tailwind CSS 3.x + Custom CSS modules
- **Animation**: Framer Motion (for chatbot transitions)
- **Build**: Webpack (Docusaurus default)
- **Testing**: Vitest, React Testing Library, Playwright
- **Deployment**: GitHub Pages via GitHub Actions

### Backend
- **Framework**: FastAPI 0.104+
- **Runtime**: Python 3.10+ with Uvicorn
- **Validation**: Pydantic 2.x
- **ORM**: SQLAlchemy 2.x (async)
- **RAG**: LangChain 0.1.x
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Deployment**: Render (Docker container)

### AI/ML
- **LLM**: OpenAI GPT-4 Turbo (chat completions)
- **Embeddings**: OpenAI text-embedding-3-small (1536 dims)
- **SDK**: OpenAI Python SDK 1.x

### Databases
- **Vector DB**: Qdrant Cloud Free Tier (HNSW index)
- **Relational DB**: Neon Serverless Postgres
- **Caching**: In-memory (Python dict for session data)

### DevOps
- **CI/CD**: GitHub Actions
- **Containers**: Docker + Docker Compose
- **Monitoring**: FastAPI logs + Render metrics
- **Version Control**: Git + GitHub

## Risk Mitigation

**Risk 1: OpenAI API Rate Limits**
- **Mitigation**: Implement exponential backoff, queue system for high traffic, tier upgrade path ($5/month = 40K TPM)

**Risk 2: Qdrant Free Tier Exceeded (1M vectors)**
- **Mitigation**: Current plan = 2K chunks, 500x headroom; if needed, upgrade to Qdrant Cloud Starter ($25/month)

**Risk 3: Cold Starts on Render (30s)**
- **Mitigation**: Keep-alive ping every 10 minutes, user messaging ("Warming up server..."), Railway as fallback

**Risk 4: Retrieval Quality <80% Precision@5**
- **Mitigation**: Iterate on chunking strategy, add reranking, fine-tune similarity thresholds, A/B test hybrid search weights

**Risk 5: Page Load >2s on GitHub Pages**
- **Mitigation**: Image optimization, code splitting, lazy loading for chatbot widget, CDN caching

## Next Steps

1. **Proceed to Phase 1**: Create `data-model.md`, `contracts/api-spec.yaml`, `quickstart.md`
2. **Validate Decisions**: Prototype RAG pipeline with sample chapter to test chunking + retrieval
3. **Baseline Metrics**: Measure initial retrieval quality, establish improvement targets
4. **Iterate**: Adjust chunking, reranking, similarity thresholds based on empirical results
