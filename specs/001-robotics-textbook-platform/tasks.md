# Tasks: Physical AI & Humanoid Robotics Interactive Textbook Platform

**Input**: Design documents from `/specs/001-robotics-textbook-platform/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] [Skill] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- **[Skill]**: Primary skill responsible (see `.claude/skills/README.md` for 10 specialized skills)
- Include exact file paths in descriptions

## Path Conventions

Web application structure (frontend/ and backend/ directories):
- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/docs/`, `frontend/src/`, `frontend/tests/`
- **Root**: `.github/workflows/`, `.env.example`, `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

**Skills**: deployment-expert, backend-engineer, docusaurus-developer

- [ ] T001 [P] [SETUP] [deployment-expert] Create project root structure with backend/, frontend/, .github/workflows/ directories
- [ ] T002 [P] [SETUP] [backend-engineer] Initialize Python backend: create backend/ with src/, tests/, requirements.txt, Dockerfile
- [ ] T003 [P] [SETUP] [docusaurus-developer] Initialize Docusaurus frontend: `npx create-docusaurus@latest frontend classic --typescript`
- [ ] T004 [P] [SETUP] [deployment-expert] Create .env.example with required environment variables (OPENAI_API_KEY, DATABASE_URL, QDRANT_URL, QDRANT_API_KEY)
- [ ] T005 [P] [SETUP] [backend-engineer] Create backend/requirements.txt with dependencies (FastAPI, Uvicorn, Pydantic, SQLAlchemy, asyncpg, qdrant-client, openai, langchain, pytest)
- [ ] T006 [P] [SETUP] [deployment-expert] Create .gitignore for Python (.venv, __pycache__, .env) and Node.js (node_modules/, build/, .docusaurus/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Skills**: database-engineer, vector-db-specialist, backend-engineer

### Database Setup

- [ ] T007 [database-engineer] Create Neon Serverless Postgres database and configure connection string in .env
- [ ] T008 [database-engineer] Create SQLAlchemy models in backend/src/models/conversation.py (Conversation, Message models per data-model.md)
- [ ] T009 [database-engineer] Create Alembic migration for initial schema in backend/alembic/versions/001_initial_schema.py
- [ ] T010 [database-engineer] Run migration to create conversations and messages tables in Neon Postgres

### Vector Database Setup

- [ ] T011 [vector-db-specialist] Create Qdrant Cloud cluster (Free Tier) and configure API key in .env
- [ ] T012 [vector-db-specialist] Create collection setup script in backend/src/utils/qdrant_setup.py (textbook_chunks collection, 1536 dims, cosine distance)
- [ ] T013 [vector-db-specialist] Run collection setup to initialize Qdrant with HNSW index and metadata indexes (chapter, section)

### Backend Core Infrastructure

- [ ] T014 [backend-engineer] Create FastAPI app in backend/src/api/main.py with CORS middleware, logging middleware, error handlers
- [ ] T015 [backend-engineer] Create Pydantic schemas in backend/src/models/schemas.py (ChatRequest, TokenEvent, CitationEvent, DoneEvent per contracts/api-spec.yaml)
- [ ] T016 [backend-engineer] Create configuration module in backend/src/utils/config.py (load environment variables, validate required keys)
- [ ] T017 [backend-engineer] Create structured logging setup in backend/src/utils/logging.py (correlation IDs, JSON formatting)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse and Read Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Students can access comprehensive online textbook with navigation, search, and responsive design

**Independent Test**: Navigate to localhost:3000, browse chapters, use search, verify mobile responsiveness

**Skills**: content-writer, docusaurus-developer, frontend-designer

### Content Creation

- [ ] T018 [P] [US1] [content-writer] Write Chapter 1: Introduction to Physical AI in frontend/docs/chapters/01-introduction/index.md (1000-1500 words, includes overview, key concepts, hands-on exercise)
- [ ] T019 [P] [US1] [content-writer] Write Chapter 2: Robot Kinematics in frontend/docs/chapters/02-kinematics/index.md (1500-2000 words, forward/inverse kinematics, DH parameters, Python examples)
- [ ] T020 [P] [US1] [content-writer] Write Chapter 3: Robot Dynamics in frontend/docs/chapters/03-dynamics/index.md (1500-2000 words, equations of motion, Lagrangian mechanics, code examples)

### Docusaurus Configuration

- [ ] T021 [US1] [docusaurus-developer] Configure docusaurus.config.js with site metadata, navbar, footer, theme config (dark mode, search)
- [ ] T022 [US1] [docusaurus-developer] Create sidebars.js with hierarchical chapter structure (10 chapters from plan.md)
- [ ] T023 [US1] [docusaurus-developer] Configure Algolia DocSearch in docusaurus.config.js (or use local search plugin)
- [ ] T024 [US1] [docusaurus-developer] Create custom homepage in frontend/src/pages/index.tsx with hero section, chapter overview, call-to-action

### Frontend Styling & Responsiveness

- [ ] T025 [P] [US1] [frontend-designer] Install and configure Tailwind CSS in frontend/ (postcss.config.js, tailwind.config.js)
- [ ] T026 [P] [US1] [frontend-designer] Create custom CSS in frontend/src/css/custom.css (typography, code blocks, responsive breakpoints)
- [ ] T027 [US1] [frontend-designer] Test responsive design on mobile (320px), tablet (768px), desktop (1024px+) viewports
- [ ] T028 [US1] [frontend-designer] Add syntax highlighting for code blocks (Prism.js theme customization in docusaurus.config.js)

### Testing & Validation

- [ ] T029 [US1] [docusaurus-developer] Run Docusaurus build: `npm run build` in frontend/ and verify zero errors
- [ ] T030 [US1] [frontend-designer] Run Lighthouse accessibility audit, ensure WCAG 2.1 AA compliance (score ≥90)
- [ ] T031 [US1] [docusaurus-developer] Test search functionality with sample queries ("kinematics", "PID controller", "sensor fusion")

**Checkpoint**: User Story 1 (MVP) is complete and deployable - students can read textbook content

---

## Phase 4: User Story 2 - Ask Questions Using Intelligent Chatbot (Priority: P2)

**Goal**: Students can ask questions and receive RAG-powered answers with citations

**Independent Test**: Open chatbot widget, ask robotics questions, verify citations link to content

**Skills**: rag-specialist, backend-engineer, chatbot-engineer, vector-db-specialist

### Tests for User Story 2 (TDD: Write These First) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T032 [P] [US2] [rag-specialist] Contract test for POST /api/chat in backend/tests/contract/test_api_chat.py (validate request/response schemas match contracts/api-spec.yaml)
- [ ] T033 [P] [US2] [backend-engineer] Integration test for RAG pipeline in backend/tests/integration/test_rag_pipeline.py (markdown → chunk → embed → retrieve → LLM flow)
- [ ] T034 [P] [US2] [vector-db-specialist] Unit test for hybrid search in backend/tests/unit/test_retrieval.py (vector + BM25 + reranking logic)

### Content Ingestion Pipeline

- [ ] T035 [P] [US2] [rag-specialist] Create markdown parser in backend/src/ingestion/parser.py (extract headings, sections, code blocks, metadata)
- [ ] T036 [P] [US2] [rag-specialist] Create semantic chunker in backend/src/ingestion/chunker.py (400-600 tokens/chunk, heading boundaries, overlap handling)
- [ ] T037 [US2] [rag-specialist] Create embedding generator in backend/src/services/embeddings.py (OpenAI text-embedding-3-small, batch processing)
- [ ] T038 [US2] [rag-specialist] Create ingestion pipeline orchestrator in backend/src/ingestion/pipeline.py (CLI tool: --input, --output, --rebuild flags)
- [ ] T039 [US2] [rag-specialist] Run ingestion pipeline on Chapters 1-3: `python -m src.ingestion.pipeline --input ../frontend/docs/chapters`

### RAG Retrieval & Reranking

- [ ] T040 [P] [US2] [vector-db-specialist] Implement hybrid search in backend/src/services/retrieval.py (Qdrant vector search + BM25, reciprocal rank fusion)
- [ ] T041 [P] [US2] [rag-specialist] Implement cross-encoder reranking in backend/src/services/reranking.py (MiniLM or Cohere Rerank API, top-5 selection)
- [ ] T042 [US2] [rag-specialist] Create RAG pipeline orchestrator in backend/src/services/rag.py (retrieve → rerank → format context for LLM)

### LLM Integration

- [ ] T043 [US2] [backend-engineer] Implement streaming LLM in backend/src/services/llm.py (OpenAI GPT-4 Turbo, Server-Sent Events, citation extraction)
- [ ] T044 [US2] [backend-engineer] Create /api/chat endpoint in backend/src/api/chat.py (accept ChatRequest, stream TokenEvent/CitationEvent/DoneEvent)
- [ ] T045 [US2] [backend-engineer] Implement conversation persistence (create/update Conversation and Message records in Neon Postgres)

### Frontend Chatbot Widget

- [ ] T046 [P] [US2] [chatbot-engineer] Create ChatbotWidget component in frontend/src/components/ChatbotWidget/index.tsx (minimizable, draggable, floating UI)
- [ ] T047 [P] [US2] [chatbot-engineer] Create MessageList component in frontend/src/components/ChatbotWidget/MessageList.tsx (display user/assistant messages, scrollable)
- [ ] T048 [P] [US2] [chatbot-engineer] Create InputArea component in frontend/src/components/ChatbotWidget/InputArea.tsx (text input, send button, typing indicator)
- [ ] T049 [P] [US2] [chatbot-engineer] Create CitationLink component in frontend/src/components/ChatbotWidget/CitationLink.tsx (clickable citation, scroll to referenced section)
- [ ] T050 [US2] [chatbot-engineer] Implement SSE client in frontend/src/services/api.ts (EventSource for streaming, token buffering, error handling)
- [ ] T051 [US2] [chatbot-engineer] Integrate ChatbotWidget into Docusaurus in frontend/src/theme/Root.tsx (global wrapper, session ID management)
- [ ] T052 [US2] [frontend-designer] Style ChatbotWidget with Tailwind CSS in frontend/src/components/ChatbotWidget/styles.module.css (dark mode support, responsive)

### Testing & Validation

- [ ] T053 [US2] [rag-specialist] Measure retrieval quality: Precision@5, NDCG (create test set of 20 questions, target: ≥80% precision)
- [ ] T054 [US2] [backend-engineer] Run pytest with coverage: `pytest --cov=src --cov-report=html` (target: ≥80% coverage)
- [ ] T055 [US2] [chatbot-engineer] Test chatbot with 5 sample questions, verify citations are clickable and correct

**Checkpoint**: User Story 2 is complete - students can ask questions and receive cited answers

---

## Phase 5: User Story 3 - Get Contextual Help from Selected Text (Priority: P3)

**Goal**: Students can select text and ask questions with that text as context

**Independent Test**: Highlight text, click "Ask about this", verify chatbot opens with context

**Skills**: integration-specialist, chatbot-engineer, frontend-designer

### Tests for User Story 3 (TDD: Write These First) ⚠️

- [ ] T056 [P] [US3] [integration-specialist] Integration test for text selection flow in frontend/tests/e2e/text-selection.spec.ts (Playwright: select text → popup → chatbot opens)

### Implementation

- [ ] T057 [P] [US3] [integration-specialist] Create text selection handler in frontend/src/components/TextSelection/index.tsx (detect selection event, extract text)
- [ ] T058 [P] [US3] [frontend-designer] Create SelectionPopup component in frontend/src/components/TextSelection/SelectionPopup.tsx ("Ask about this" button, positioned near selection)
- [ ] T059 [US3] [chatbot-engineer] Update ChatbotWidget to accept selected_text prop, prepopulate input or show context badge
- [ ] T060 [US3] [backend-engineer] Update /api/chat endpoint to handle selected_text field in ChatRequest (append to prompt context)

### Testing & Validation

- [ ] T061 [US3] [integration-specialist] Test text selection on various content types (paragraphs, code blocks, equations)
- [ ] T062 [US3] [chatbot-engineer] Verify chatbot responses use selected text as context (ask "Explain this" for complex paragraph)

**Checkpoint**: User Story 3 is complete - students can get contextual help from selected text

---

## Phase 6: User Story 4 - Access Hands-On Exercises and Code Examples (Priority: P4)

**Goal**: Students can access interactive code examples and hands-on exercises

**Independent Test**: Navigate to exercise sections, copy code, verify exercises are clear and actionable

**Skills**: content-writer, docusaurus-developer

### Content Creation

- [ ] T063 [P] [US4] [content-writer] Create hands-on exercise for Chapter 1 in frontend/docs/exercises/01-intro-exercise.md (PID controller simulation, step-by-step instructions)
- [ ] T064 [P] [US4] [content-writer] Create hands-on exercise for Chapter 2 in frontend/docs/exercises/02-kinematics-exercise.md (forward kinematics calculation, Python code)
- [ ] T065 [P] [US4] [content-writer] Add "Copy Code" functionality to code blocks (Docusaurus code block meta strings: `python title="robot_controller.py" showLineNumbers`)

### Docusaurus Enhancement

- [ ] T066 [US4] [docusaurus-developer] Create exercises section in sidebars.js (link to all exercise pages)
- [ ] T067 [US4] [docusaurus-developer] Test code copying functionality (click "Copy" button, paste in editor, verify it works)

**Checkpoint**: User Story 4 is complete - students can access and use hands-on exercises

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, deployment, and final quality checks

**Skills**: deployment-expert, backend-engineer, frontend-designer, content-writer

### Deployment & CI/CD

- [ ] T068 [P] [deployment-expert] Create GitHub Actions workflow for frontend deployment in .github/workflows/frontend-deploy.yml (build Docusaurus, deploy to GitHub Pages)
- [ ] T069 [P] [deployment-expert] Create GitHub Actions workflow for backend deployment in .github/workflows/backend-deploy.yml (build Docker image, deploy to Render)
- [x] T070 [deployment-expert] Create Dockerfile for backend in backend/Dockerfile (Python 3.10, install deps, run Uvicorn)
- [ ] T071 [deployment-expert] Configure Render service (connect GitHub repo, set environment variables, auto-deploy on main branch push)
- [ ] T072 [deployment-expert] Configure GitHub Pages (Settings → Pages, deploy from gh-pages branch)

### Health & Monitoring

- [x] T073 [P] [backend-engineer] Create /api/health endpoint in backend/src/api/health.py (check Postgres, Qdrant, OpenAI connectivity)
- [x] T074 [P] [backend-engineer] Add request logging middleware to FastAPI app (log all requests with latency, status code, correlation ID)
- [ ] T075 [deployment-expert] Set up Render health checks (ping /api/health every 5 minutes, alert on failure)

### Documentation

- [x] T076 [P] [content-writer] Create project README.md at root with project overview, setup instructions, deployment status badges
- [x] T077 [P] [backend-engineer] Create backend/README.md with API documentation, development setup, testing instructions
- [x] T078 [P] [docusaurus-developer] Create frontend/README.md with Docusaurus setup, content authoring guide, deployment instructions

### Content Completion

- [x] T079 [P] [content-writer] Write remaining chapters 4-10 (Control, Perception, Planning, Learning, Manipulation, Locomotion, HRI) in frontend/docs/chapters/ (~1500 words each)
- [ ] T080 [content-writer] Re-run ingestion pipeline for all 10 chapters: `python -m src.ingestion.pipeline --input ../frontend/docs/chapters --rebuild`

### Performance Optimization

- [ ] T081 [P] [frontend-designer] Optimize images in frontend/static/img/ (compress, resize, use WebP format where possible)
- [x] T082 [P] [docusaurus-developer] Enable code splitting in docusaurus.config.js (lazy load chatbot widget)
- [x] T083 [backend-engineer] Add caching headers to FastAPI responses (Cache-Control for health endpoint)

### Security Hardening

- [x] T084 [P] [backend-engineer] Add rate limiting to /api/chat endpoint (max 60 requests/minute per session_id, 429 response on exceed)
- [x] T085 [P] [backend-engineer] Add input validation to ChatRequest (sanitize message field, prevent injection attacks)

### Final Validation

- [ ] T086 [deployment-expert] Run end-to-end smoke test on production deployment (browse site, ask chatbot question, verify citation links)
- [ ] T087 [frontend-designer] Run Lighthouse audit on production URL (Performance ≥90, Accessibility ≥90, Best Practices ≥90, SEO ≥90)
- [ ] T088 [rag-specialist] Measure production retrieval quality with test set (verify Precision@5 ≥80%, citation accuracy ≥95%)
- [ ] T089 [backend-engineer] Run load test on /api/chat endpoint (simulate 100 concurrent users, verify <500ms p95 latency)
- [ ] T090 [deployment-expert] Run quickstart.md validation: fresh clone → setup → verify all steps work (≤15 minutes total)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - **Requires US1 content to exist for RAG testing**
  - User Story 3 (P3): Depends on US2 chatbot widget - **Must complete US2 first**
  - User Story 4 (P4): Can start after Foundational - No dependencies on other stories
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### Within Each User Story

**User Story 1 (P1)**:
- Content creation tasks (T018-T020) can run in parallel
- Docusaurus config tasks (T021-T024) sequential (config → sidebars → search → homepage)
- Frontend styling tasks (T025-T026) can run in parallel
- Testing tasks (T029-T031) run after all implementation complete

**User Story 2 (P2)**:
- **TDD: Tests (T032-T034) MUST be written and FAIL before implementation**
- Ingestion tasks (T035-T039) sequential (parser → chunker → embedder → pipeline → run)
- Retrieval tasks (T040-T042) can start after ingestion pipeline exists
- LLM tasks (T043-T045) can run in parallel with retrieval
- Frontend widget tasks (T046-T052) can run in parallel (components are independent)
- Testing tasks (T053-T055) run after all implementation complete

**User Story 3 (P3)**:
- Test (T056) MUST be written first
- Implementation tasks (T057-T060) can run in parallel if team has multiple developers
- Testing tasks (T061-T062) run after implementation

**User Story 4 (P4)**:
- Content tasks (T063-T065) can run in parallel
- Docusaurus tasks (T066-T067) sequential

### Parallel Opportunities

- **Setup**: All tasks (T001-T006) can run in parallel
- **Foundational**: T007-T010 (database) || T011-T013 (vector DB) || T014-T017 (backend core)
- **US1 Content**: T018 || T019 || T020 (all chapters independent)
- **US1 Styling**: T025 || T026 (CSS tasks independent)
- **US2 Tests**: T032 || T033 || T034 (all tests independent)
- **US2 Ingestion**: T035 || T036 (parser and chunker independent until T038 orchestrator)
- **US2 RAG**: T040 || T041 (retrieval and reranking independent)
- **US2 Frontend**: T046 || T047 || T048 || T049 (all widget components independent)
- **US3**: T057 || T058 (selection handler and popup independent)
- **US4**: T063 || T064 || T065 (all exercises independent)
- **Polish Deployment**: T068 || T069 (frontend and backend workflows independent)
- **Polish Docs**: T076 || T077 || T078 (all READMEs independent)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T017) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T018-T031)
4. **STOP and VALIDATE**: Test User Story 1 independently, verify all acceptance scenarios pass
5. Deploy to staging, share with stakeholders for feedback

**Deliverable**: Functional textbook website with 3 chapters, search, responsive design

### Incremental Delivery (Recommended)

1. **Sprint 1**: Setup + Foundational (T001-T017) → Foundation ready
2. **Sprint 2**: User Story 1 (T018-T031) → Deploy MVP, gather feedback
3. **Sprint 3**: User Story 2 Tests + Implementation (T032-T055) → Deploy chatbot feature
4. **Sprint 4**: User Story 3 (T056-T062) → Deploy text selection feature
5. **Sprint 5**: User Story 4 + Polish (T063-T090) → Final deployment, full feature set

**Benefits**: Each sprint delivers value, allows for course correction, reduces risk

### Parallel Team Strategy

With 3 developers:

1. **Week 1**: All developers complete Setup + Foundational together (pair programming on critical infrastructure)
2. **Week 2**:
   - Developer A: User Story 1 (content + Docusaurus)
   - Developer B: User Story 2 backend (ingestion + RAG)
   - Developer C: User Story 2 frontend (chatbot widget)
3. **Week 3**:
   - Developer A: User Story 3 (text selection)
   - Developer B: User Story 4 (exercises) + Polish (deployment)
   - Developer C: Content completion (chapters 4-10) + testing
4. **Week 4**: All developers collaborate on final validation, performance testing, deployment

---

## Notes

- **[P] tasks** = different files, no dependencies, safe to parallelize
- **[Story] label** maps task to specific user story for traceability
- **[Skill] label** identifies primary responsible role (aligns with `.claude/skills/README.md`)
- Each user story should be independently completable and testable
- **TDD is NON-NEGOTIABLE**: Tests for US2 and US3 MUST be written and FAIL before implementation (Constitution Principle IV)
- Verify tests fail before implementing (Red phase), then implement to make them pass (Green phase)
- Commit after each task or logical group (e.g., all US1 content tasks)
- Stop at any checkpoint to validate story independently before proceeding
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Total Task Count

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 11 tasks (BLOCKING)
- **Phase 3 (User Story 1 - P1)**: 14 tasks → **MVP**
- **Phase 4 (User Story 2 - P2)**: 24 tasks → **Key Differentiator**
- **Phase 5 (User Story 3 - P3)**: 7 tasks
- **Phase 6 (User Story 4 - P4)**: 5 tasks
- **Phase 7 (Polish)**: 23 tasks
- **TOTAL**: **90 tasks**

**Estimated Effort**:
- MVP (Phases 1-3): ~31 tasks, ~2-3 weeks (1-2 developers)
- Full Feature Set (All Phases): ~90 tasks, ~5-6 weeks (1-2 developers)
- Parallel Team (3 developers): ~4 weeks for full feature set
