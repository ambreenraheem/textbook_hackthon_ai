# Physical AI & Humanoid Robotics Textbook Constitution

<!--
Sync Impact Report:
Version change: 1.0.0 (initial creation)
Added sections:
  - Core Principles (7 principles: Educational Excellence, RAG-First Architecture, Skills-Based Development, Test-Driven Development, Integration Testing, Observability & Performance, Simplicity & YAGNI)
  - Technology Stack Requirements
  - Development Workflow
  - Governance
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section already exists
  ✅ spec-template.md - User scenarios align with educational focus
  ✅ tasks-template.md - Task categorization supports skills-based development
Follow-up TODOs: None - all placeholders filled
-->

## Core Principles

### I. Educational Excellence
The textbook MUST prioritize learning outcomes and pedagogical quality above all else.

- Content MUST be comprehensive, technically accurate, and accessible to students
- Each chapter MUST include hands-on exercises and practical demonstrations
- Code examples MUST be production-quality, well-documented, and illustrative
- Content structure MUST optimize for both human reading and RAG retrieval
- All technical content MUST be peer-reviewed for accuracy before deployment

**Rationale**: This is an educational product; student learning experience is the primary success metric.

### II. RAG-First Architecture
The chatbot integration is a core feature, not an afterthought.

- All content MUST be structured for optimal semantic chunking and retrieval
- The RAG pipeline MUST use hybrid search (vector + keyword) with reranking
- Chatbot responses MUST cite specific textbook sections with page/chapter references
- Text selection-based Q&A MUST be implemented to enable contextual queries
- Embedding quality and retrieval accuracy MUST be measured and optimized continuously

**Rationale**: The RAG chatbot is a key differentiator; poor retrieval quality undermines the entire value proposition.

### III. Skills-Based Development
Development MUST follow the 10 specialized skills defined in `.claude/skills/README.md`.

- Each feature MUST map to one or more skills with clear ownership boundaries
- Skill dependencies MUST be respected (see dependency graph in skills README)
- Cross-skill integration points MUST be explicitly documented
- Each skill MUST define its success criteria and output artifacts
- Code organization MUST reflect skill boundaries (frontend, backend, RAG, deployment)

**Rationale**: Skills provide clear separation of concerns and enable parallel development; violating boundaries creates coupling and blocks progress.

### IV. Test-Driven Development (NON-NEGOTIABLE)
TDD is mandatory for all backend and RAG pipeline code.

- Tests MUST be written before implementation
- All tests MUST fail initially, then pass after implementation
- Red-Green-Refactor cycle MUST be strictly enforced
- Test coverage MUST be measured; minimum 80% for backend and RAG components
- No feature branch merges without passing tests

**Rationale**: RAG systems and backend APIs are complex; untested code will break in production and degrade user experience.

### V. Integration Testing
Focus areas requiring integration tests:

- RAG pipeline: end-to-end content ingestion → embedding → retrieval → LLM response
- API contracts: FastAPI endpoints with request/response validation
- Chatbot widget: frontend-backend communication and streaming responses
- Text selection integration: browser selection → API → RAG → response
- GitHub Pages deployment: build → deploy → accessibility validation

**Rationale**: Integration points are where failures occur in multi-component systems; unit tests alone are insufficient.

### VI. Observability & Performance
Production deployment requires comprehensive monitoring and performance optimization.

- All API endpoints MUST log requests, errors, and latency (p95, p99)
- RAG pipeline MUST track: retrieval quality, embedding generation time, LLM response time
- Frontend MUST track: page load time, chatbot widget interaction latency, user engagement metrics
- Database queries MUST be optimized with proper indexing (verified via EXPLAIN ANALYZE)
- Error handling MUST include structured logging with correlation IDs for distributed tracing

**Performance Targets**:
- API response time: <500ms p95 for chat endpoints
- RAG retrieval: <200ms p95 for vector search
- Page load: <2s p95 for Docusaurus pages
- Chatbot streaming: first token <1s, smooth streaming thereafter

**Rationale**: Poor performance degrades learning experience; lack of observability makes debugging impossible in production.

### VII. Simplicity & YAGNI (You Aren't Gonna Need It)
Start simple, add complexity only when required by real needs.

- Use proven technologies from the defined stack; no experimental libraries
- Implement the simplest solution that meets requirements; no premature optimization
- Avoid over-engineering: no abstractions, patterns, or frameworks for hypothetical future needs
- Three similar lines of code are better than a premature abstraction
- Only add error handling, validation, or fallbacks for scenarios that can actually occur

**Rationale**: This is a hackathon project with tight deadlines; complexity slows development and increases bug surface area.

## Technology Stack Requirements

### Mandatory Technologies (NON-NEGOTIABLE)
- **Frontend**: Docusaurus 3.x, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python 3.10+), Pydantic, Uvicorn
- **Database**: Neon Serverless Postgres
- **Vector Database**: Qdrant Cloud (Free Tier)
- **AI/LLM**: OpenAI Agents/ChatKit SDKs
- **Deployment**: GitHub Pages (frontend), Render/Railway (backend)

### Prohibited Practices
- No hardcoded secrets or API keys (use `.env` with proper gitignore)
- No mixing frontend and backend in same runtime (strict separation)
- No custom embedding models (use OpenAI embeddings)
- No custom LLM endpoints (use OpenAI API)
- No manual deployment (use GitHub Actions CI/CD)

**Rationale**: Technology choices are constraints from the hackathon requirements; deviations waste time and create compatibility issues.

## Development Workflow

### Feature Development Lifecycle

1. **Specification** (`/sp.specify`):
   - Create feature spec with user stories prioritized (P1, P2, P3)
   - Each user story MUST be independently testable
   - Map feature to relevant skills from `.claude/skills/README.md`

2. **Planning** (`/sp.plan`):
   - Research existing codebase and dependencies
   - Design architecture with explicit skill boundaries
   - Define API contracts, data models, and integration points
   - Pass Constitution Check before proceeding

3. **Task Generation** (`/sp.tasks`):
   - Break down into testable tasks organized by user story
   - Identify parallel opportunities (mark with [P])
   - Include skill labels (e.g., [RAG], [Backend], [Frontend])
   - Ensure each user story can be implemented independently

4. **Implementation** (`/sp.implement`):
   - Follow TDD: write tests → verify failure → implement → verify pass
   - Commit frequently with descriptive messages
   - Run integration tests at checkpoints
   - Document architectural decisions with `/sp.adr` when significant

5. **Review & Deployment**:
   - Code review for code quality, test coverage, skill boundary compliance
   - Verify Constitution Check compliance
   - Deploy via CI/CD (no manual deployments)
   - Monitor performance and error rates post-deployment

### Branching & Commits
- Feature branches: `###-feature-name` format
- Commit messages: conventional commits (feat, fix, docs, test, refactor)
- Pull requests MUST include: description, testing evidence, skill compliance verification
- Main branch MUST always be deployable

### Quality Gates (MUST PASS before merge)
- All tests passing (unit, integration, contract)
- Constitution Check compliance verified
- Code review approval (1+ reviewer)
- No unresolved TODOs or placeholders
- Performance benchmarks met (if applicable)

## Governance

### Constitution Authority
This constitution supersedes all other development practices and guidelines. In case of conflict, constitution rules take precedence.

### Amendment Process
1. Propose amendment with rationale and impact analysis
2. Document affected templates, skills, and features
3. Update constitution version (semantic versioning: MAJOR.MINOR.PATCH)
4. Propagate changes to all dependent artifacts
5. Require team approval before ratification

**Versioning Policy**:
- **MAJOR**: Backward-incompatible principle changes (e.g., removing TDD requirement)
- **MINOR**: New principle added or materially expanded (e.g., adding security principle)
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Review
- All pull requests MUST verify Constitution Check compliance
- Any complexity or principle violation MUST be justified in Complexity Tracking table
- Constitution violations without justification MUST be rejected

### Complexity Justification
When a feature requires violating a principle (e.g., adding a 4th project, introducing new abstraction), document:
- **Violation**: What principle is being violated
- **Why Needed**: Specific problem that cannot be solved within constitution
- **Simpler Alternative Rejected Because**: Why the constitutional approach is insufficient

### Runtime Development Guidance
For AI agent and developer guidance during active development, refer to:
- **Primary**: `CLAUDE.md` (agent-specific instructions)
- **Skills**: `.claude/skills/README.md` (role-based development patterns)
- **Constitution**: `.specify/memory/constitution.md` (this file - non-negotiable rules)

**Version**: 1.0.0 | **Ratified**: 2025-12-26 | **Last Amended**: 2025-12-26
