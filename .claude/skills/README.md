# Skills Directory

## Project: Physical AI & Humanoid Robotics Textbook

This directory contains all the specialized skills required to build and deploy an interactive textbook with an embedded RAG-powered chatbot.

## Project Overview

**Hackathon I: Create a Textbook for Teaching Physical AI & Humanoid Robotics Course**

### Main Objectives:
1. **AI/Spec-Driven Book Creation**: Write a comprehensive textbook using Docusaurus and deploy it to GitHub Pages
2. **Integrated RAG Chatbot Development**: Build and embed a Retrieval-Augmented Generation (RAG) chatbot that can answer questions about the book's content, including answering questions based on user-selected text

### Technology Stack:
- **Frontend**: Docusaurus 3.x, React, TypeScript
- **Backend**: FastAPI (Python)
- **Database**: Neon Serverless Postgres
- **Vector Database**: Qdrant Cloud (Free Tier)
- **AI/LLM**: OpenAI Agents/ChatKit SDKs
- **Deployment**: GitHub Pages (frontend), Render/Railway (backend)

---

## Skills Overview

### 📚 Content & Documentation

#### 1. [content-writer](./content-writer.skill.md)
**Job**: Technical content creation for Physical AI & Humanoid Robotics textbook

**Key Responsibilities:**
- Write comprehensive chapters on robotics fundamentals
- Create tutorials and hands-on exercises
- Develop code examples and demonstrations
- Structure content with proper headings and organization
- Optimize content for RAG retrieval

**Technologies**: Markdown, MDX, LaTeX, Mermaid diagrams

**Example Tasks:**
- Write chapter on "Introduction to Physical AI"
- Create hands-on tutorial for robot sensor integration
- Develop glossary and reference materials

---

### 🎨 Frontend Development

#### 2. [docusaurus-developer](./docusaurus-developer.skill.md)
**Job**: Docusaurus book/documentation site development

**Key Responsibilities:**
- Initialize and configure Docusaurus project
- Create book structure with chapters and sections
- Configure navigation, sidebars, and table of contents
- Customize theme for educational content
- Optimize site performance and SEO

**Technologies**: Docusaurus 3.x, React, MDX, Node.js

**Example Tasks:**
- Set up Docusaurus with custom configuration
- Create sidebar structure for textbook chapters
- Configure search functionality

---

#### 3. [frontend-designer](./frontend-designer.skill.md)
**Job**: UI/UX design for educational textbook website

**Key Responsibilities:**
- Design responsive layout for textbook pages
- Create custom React components for interactive content
- Design and implement chatbot UI widget
- Implement dark/light mode theming
- Ensure accessibility (WCAG 2.1)

**Technologies**: React, CSS3, Tailwind CSS, Framer Motion

**Example Tasks:**
- Design chatbot widget UI
- Create interactive diagram components
- Implement responsive mobile layout

---

### 🤖 AI & Chatbot

#### 4. [chatbot-engineer](./chatbot-engineer.skill.md)
**Job**: Build interactive RAG-powered chatbot for textbook assistance

**Key Responsibilities:**
- Implement OpenAI Agents/ChatKit SDK integration
- Create conversation management system
- Build text selection-based question answering
- Implement streaming response UI
- Add conversation analytics

**Technologies**: OpenAI Agents SDK, ChatKit SDK, React, WebSocket/SSE

**Example Tasks:**
- Integrate OpenAI ChatKit for real-time chat
- Implement text selection Q&A feature
- Build conversation history persistence

---

#### 5. [rag-specialist](./rag-specialist.skill.md)
**Job**: Design and implement Retrieval-Augmented Generation (RAG) pipeline

**Key Responsibilities:**
- Design content chunking strategy
- Implement embedding generation pipeline
- Build hybrid search (vector + keyword)
- Create reranking mechanism
- Design prompt templates for LLM
- Optimize retrieval quality

**Technologies**: OpenAI Embeddings API, Qdrant, LangChain, Python

**Example Tasks:**
- Implement semantic chunking for textbook content
- Build hybrid search with reranking
- Optimize prompt templates for educational responses

---

### 🔧 Backend Development

#### 6. [backend-engineer](./backend-engineer.skill.md)
**Job**: FastAPI backend development for chatbot and data management

**Key Responsibilities:**
- Design and implement FastAPI REST API
- Create database models and schemas
- Build chat endpoint with streaming support
- Implement caching layer
- Write API documentation

**Technologies**: FastAPI, Python, SQLAlchemy, Pydantic, Uvicorn

**Example Tasks:**
- Create `/api/chat` endpoint with streaming
- Implement async database operations
- Build health check endpoints

---

#### 7. [database-engineer](./database-engineer.skill.md)
**Job**: Design and manage Neon Serverless Postgres database

**Key Responsibilities:**
- Design database schema for conversations and content
- Create database migrations with Alembic
- Optimize database queries and indexes
- Implement connection pooling
- Monitor database performance

**Technologies**: Neon Postgres, PostgreSQL, SQLAlchemy, Alembic, asyncpg

**Example Tasks:**
- Design schema for conversations and messages
- Create Alembic migrations
- Optimize queries with proper indexing

---

#### 8. [vector-db-specialist](./vector-db-specialist.skill.md)
**Job**: Manage Qdrant Cloud vector database for RAG system

**Key Responsibilities:**
- Set up Qdrant Cloud Free Tier cluster
- Design collection schema with metadata
- Implement vector ingestion pipeline
- Optimize vector search parameters
- Create hybrid search capabilities

**Technologies**: Qdrant Cloud, Qdrant Python Client, HNSW, Vector embeddings

**Example Tasks:**
- Set up Qdrant collection with 1536-dim vectors
- Implement batch vector ingestion
- Optimize HNSW search parameters

---

### 🚀 Deployment & Integration

#### 9. [deployment-expert](./deployment-expert.skill.md)
**Job**: Deploy Docusaurus site to GitHub Pages and backend services

**Key Responsibilities:**
- Configure GitHub Pages deployment for Docusaurus
- Set up GitHub Actions CI/CD pipeline
- Deploy FastAPI backend to cloud platform
- Configure environment variables and secrets
- Set up monitoring and logging

**Technologies**: GitHub Actions, GitHub Pages, Docker, Render/Railway

**Example Tasks:**
- Create GitHub Actions workflow for auto-deployment
- Deploy backend to Render with environment config
- Set up custom domain and SSL

---

#### 10. [integration-specialist](./integration-specialist.skill.md)
**Job**: Integrate RAG chatbot into Docusaurus textbook site

**Key Responsibilities:**
- Embed chatbot widget into Docusaurus pages
- Configure API endpoints and environment variables
- Implement text selection integration
- Set up CORS and authentication
- Optimize performance and caching

**Technologies**: React, Docusaurus plugin system, Fetch API, Browser APIs

**Example Tasks:**
- Integrate ChatbotWidget into Docusaurus Root
- Implement text selection event handler
- Configure production API endpoints

---

## Skill Dependencies

```
┌─────────────────────────────────────────────────┐
│            content-writer                       │
│  (Creates textbook content)                     │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│         docusaurus-developer                     │
│  (Structures content in Docusaurus)              │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│         frontend-designer                        │
│  (Designs UI/UX)                                 │
└──────────────┬───────────────────────────────────┘
               │
               ├─────────────────────┐
               ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│  chatbot-engineer    │  │  rag-specialist      │
│  (Chatbot UI/Logic)  │  │  (RAG Pipeline)      │
└──────────┬───────────┘  └────────┬─────────────┘
           │                       │
           └───────┬───────────────┘
                   ▼
┌──────────────────────────────────────────────────┐
│         backend-engineer                         │
│  (FastAPI Backend)                               │
└──────────────┬───────────────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌───────────────┐  ┌──────────────────┐
│database-eng   │  │vector-db-spec    │
│(Neon Postgres)│  │(Qdrant)          │
└───────────────┘  └──────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│         integration-specialist                   │
│  (Connects frontend + backend)                   │
└──────────────┬───────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────┐
│         deployment-expert                        │
│  (Deploys to GitHub Pages + Cloud)               │
└──────────────────────────────────────────────────┘
```

## How to Use These Skills

### For Development:
1. Start with **content-writer** to create initial content
2. Use **docusaurus-developer** to structure the site
3. Apply **frontend-designer** for UI/UX design
4. Implement **backend-engineer** and **database-engineer** for data layer
5. Add **vector-db-specialist** and **rag-specialist** for RAG functionality
6. Use **chatbot-engineer** to build chatbot interface
7. Apply **integration-specialist** to connect everything
8. Finally, use **deployment-expert** to deploy

### For Specific Tasks:
Each skill file contains:
- **Metadata**: Skill name, job description, version
- **Purpose**: What this skill accomplishes
- **Example Tasks**: Concrete examples of work
- **Required Knowledge**: Prerequisites
- **Key Technologies**: Tech stack
- **Workflow Steps**: Step-by-step implementation guide
- **Integration Points**: How it connects with other skills
- **Success Criteria**: Definition of done
- **Best Practices**: Recommended approaches
- **Output Artifacts**: What gets produced

## Quick Reference

| Skill | Primary Focus | Key Output |
|-------|---------------|------------|
| content-writer | Content Creation | MDX files, chapters |
| docusaurus-developer | Site Structure | Docusaurus config, sidebars |
| frontend-designer | UI/UX | React components, CSS |
| chatbot-engineer | Chatbot Interface | ChatbotWidget component |
| rag-specialist | RAG Pipeline | Embedding & retrieval logic |
| backend-engineer | API Development | FastAPI endpoints |
| database-engineer | Data Management | Database schema, migrations |
| vector-db-specialist | Vector Search | Qdrant collections, search |
| deployment-expert | CI/CD & Hosting | GitHub Actions, deployments |
| integration-specialist | System Integration | Integrated application |

## Getting Started

1. **Review all skills** to understand the full scope
2. **Identify dependencies** between skills for your current task
3. **Follow the workflow steps** in each skill file
4. **Check success criteria** to ensure quality
5. **Use integration points** to connect different components

## Contributing

When adding new skills:
1. Follow the existing skill file template
2. Include all required sections (metadata, purpose, workflow, etc.)
3. Provide concrete code examples
4. Define clear success criteria
5. Update this README with the new skill

## Resources

### Documentation
- [Docusaurus Documentation](https://docusaurus.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Qdrant Documentation](https://qdrant.tech/documentation)
- [Neon Documentation](https://neon.tech/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)

### Tools
- Node.js 18+ and npm/yarn
- Python 3.10+
- Git and GitHub
- VS Code or your preferred IDE

---

**Project**: Hackathon I - Physical AI & Humanoid Robotics Textbook
**Version**: 1.0.0
**Created**: 2025-12-26
**Skills Count**: 10
