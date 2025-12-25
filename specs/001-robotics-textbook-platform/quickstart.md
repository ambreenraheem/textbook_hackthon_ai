# Developer Quickstart Guide: Physical AI & Humanoid Robotics Textbook Platform

**Date**: 2025-12-26
**Feature**: 001-robotics-textbook-platform
**Purpose**: Get developers up and running with local development environment in <15 minutes

## Prerequisites

### Required Software
- **Python**: 3.10 or higher ([Download](https://www.python.org/downloads/))
- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **Git**: Latest version ([Download](https://git-scm.com/))
- **Code Editor**: VS Code recommended ([Download](https://code.visualstudio.com/))

### Required Accounts & API Keys
- **OpenAI API Key**: Sign up at [platform.openai.com](https://platform.openai.com/signup)
- **Qdrant Cloud**: Free tier at [cloud.qdrant.io](https://cloud.qdrant.io/)
- **Neon Postgres**: Free tier at [neon.tech](https://neon.tech/)

### Verify Prerequisites
```bash
# Check Python version (should be 3.10+)
python --version

# Check Node.js version (should be 18.x+)
node --version

# Check npm version
npm --version

# Check Git
git --version
```

---

## Quick Setup (5 Minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/textbook_hackthon_ai.git
cd textbook_hackthon_ai
```

### Step 2: Set Up Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys (use your preferred editor)
# Windows:
notepad .env

# macOS/Linux:
nano .env
```

**Required Environment Variables**:
```env
# OpenAI API
OPENAI_API_KEY=sk-proj-...your-key-here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# Neon Serverless Postgres
DATABASE_URL=postgresql://user:password@ep-name.region.aws.neon.tech/dbname?sslmode=require

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Verify setup with tests
pytest
```

**Expected output**: All tests pass ✅

### Step 4: Frontend Setup
```bash
# Open new terminal, navigate to project root
cd frontend

# Install dependencies
npm install

# Verify setup
npm run build
```

**Expected output**: Build completes successfully ✅

---

## Running the Application

### Terminal 1: Start Backend Server
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run development server with hot reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test backend**: Open [http://localhost:8000/docs](http://localhost:8000/docs) to see auto-generated API docs (Swagger UI)

### Terminal 2: Start Frontend Dev Server
```bash
cd frontend

# Run Docusaurus development server
npm start
```

**Expected output**:
```
[INFO] Starting the development server...
[SUCCESS] Docusaurus website is running at http://localhost:3000/
```

**Test frontend**: Open [http://localhost:3000](http://localhost:3000) to see the textbook homepage

---

## Initial Content Ingestion

Before the chatbot can work, you need to ingest textbook content into the vector database.

### Step 1: Create Sample Chapter (If None Exist)
```bash
cd frontend/docs/chapters
mkdir 01-introduction
```

Create `frontend/docs/chapters/01-introduction/index.md`:
```markdown
---
sidebar_position: 1
---

# Introduction to Physical AI

Welcome to the world of Physical AI and Humanoid Robotics!

## What is Physical AI?

Physical AI refers to artificial intelligence systems that interact with the physical world through sensors, actuators, and embodied agents (robots). Unlike purely software-based AI, Physical AI must deal with real-world constraints like physics, uncertainty, and real-time requirements.

## Key Concepts

### Sensing
Robots perceive their environment through sensors:
- Cameras (vision)
- LIDAR (depth sensing)
- IMUs (inertial measurement)
- Force/torque sensors (touch)

### Acting
Robots interact with the world through actuators:
- Electric motors
- Hydraulic actuators
- Pneumatic systems

### Intelligence
AI algorithms process sensor data and generate control commands:
- Perception (computer vision, object detection)
- Planning (path planning, task planning)
- Control (PID, MPC, reinforcement learning)

## Hands-On Exercise

Try this simple robot control simulation:

\`\`\`python
import numpy as np

def pid_controller(setpoint, current, kp=1.0, ki=0.1, kd=0.05):
    """
    Simple PID controller for robot joint control.

    Args:
        setpoint: Desired position
        current: Current position
        kp, ki, kd: PID gains

    Returns:
        Control signal
    """
    error = setpoint - current
    # Simplified PID (in real systems, maintain integral and derivative state)
    control = kp * error
    return control

# Example: Control robot joint to 45 degrees
target = 45.0
position = 0.0
control_signal = pid_controller(target, position)
print(f"Control signal: {control_signal}")
\`\`\`

**Try it**: Run this code and observe how the controller responds to error.
```

### Step 2: Run Ingestion Pipeline
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Ingest all chapters from frontend/docs
python -m src.ingestion.pipeline \
  --input ../frontend/docs/chapters \
  --collection textbook_chunks \
  --batch-size 100
```

**Expected output**:
```
[INFO] Starting content ingestion...
[INFO] Found 1 markdown files
[INFO] Processing: 01-introduction/index.md
[INFO] Created 3 chunks from 01-introduction/index.md
[INFO] Generating embeddings (batch 1/1)...
[INFO] Uploading to Qdrant collection 'textbook_chunks'...
[SUCCESS] Ingestion complete! 3 chunks indexed.
[INFO] Total processing time: 5.2s
```

### Step 3: Test the Chatbot
1. Open [http://localhost:3000](http://localhost:3000)
2. Click the chatbot icon (bottom-right corner)
3. Ask: "What is Physical AI?"
4. Verify you receive an answer with citations

**Expected behavior**: Chatbot responds with answer + clickable citations to the introduction chapter

---

## Project Structure Overview

```
textbook_hackthon_ai/
├── backend/                      # FastAPI backend + RAG pipeline
│   ├── src/
│   │   ├── api/                  # API endpoints
│   │   │   ├── main.py           # FastAPI app
│   │   │   └── chat.py           # /api/chat endpoint
│   │   ├── services/             # Business logic
│   │   │   ├── rag.py            # RAG orchestration
│   │   │   ├── retrieval.py      # Hybrid search
│   │   │   └── llm.py            # OpenAI integration
│   │   ├── models/               # Database models
│   │   │   └── conversation.py   # SQLAlchemy models
│   │   └── ingestion/            # Content processing
│   │       ├── chunker.py        # Markdown chunking
│   │       └── pipeline.py       # Ingestion orchestration
│   ├── tests/                    # pytest tests
│   │   ├── unit/
│   │   ├── integration/
│   │   └── contract/
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Docusaurus textbook site
│   ├── docs/                     # Textbook content (markdown)
│   │   ├── intro.md              # Homepage
│   │   └── chapters/             # Chapter directories
│   │       ├── 01-introduction/
│   │       ├── 02-kinematics/
│   │       └── ...
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatbotWidget/    # Chatbot UI
│   │   │   └── TextSelection/    # Text selection handler
│   │   └── theme/
│   │       └── Root.tsx          # Global wrapper (inject chatbot)
│   ├── docusaurus.config.js      # Docusaurus configuration
│   └── package.json              # Node dependencies
│
├── specs/                        # Design documents
│   └── 001-robotics-textbook-platform/
│       ├── spec.md               # Requirements
│       ├── plan.md               # Implementation plan
│       ├── data-model.md         # Entity schemas
│       └── contracts/            # API contracts
│
└── .env.example                  # Environment variable template
```

---

## Common Development Tasks

### Run Tests

**Backend**:
```bash
cd backend
pytest                      # Run all tests
pytest tests/unit/          # Run unit tests only
pytest tests/integration/   # Run integration tests
pytest --cov=src            # Run with coverage report
```

**Frontend**:
```bash
cd frontend
npm test                    # Run component tests
npm run test:e2e            # Run end-to-end tests (Playwright)
```

### Rebuild Vector Database
```bash
cd backend
python -m src.ingestion.pipeline --input ../frontend/docs/chapters --rebuild
```
*Note*: `--rebuild` flag deletes existing collection and recreates it

### View API Documentation
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Check Database Migrations
```bash
cd backend
alembic history             # Show migration history
alembic current             # Show current revision
alembic upgrade head        # Apply pending migrations
alembic downgrade -1        # Rollback one migration
```

### Add New Chapter
1. Create directory: `frontend/docs/chapters/NN-chapter-name/`
2. Add `index.md` with frontmatter
3. Run ingestion pipeline: `python -m src.ingestion.pipeline --input ../frontend/docs/chapters`
4. Verify in chatbot

### Debug RAG Pipeline
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG  # or set in .env

# Run backend with verbose logs
uvicorn src.api.main:app --reload --log-level debug

# Test retrieval directly (Python REPL)
cd backend
python
>>> from src.services.retrieval import retrieve_chunks
>>> results = retrieve_chunks("What is inverse kinematics?")
>>> print(results)
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'src'`
**Solution**: Ensure you're running from `backend/` directory and virtual environment is activated

### Issue: Backend won't start - `ConnectionRefusedError` to Postgres
**Solution**: Verify `DATABASE_URL` in `.env` is correct. Test connection:
```bash
psql $DATABASE_URL
```

### Issue: Chatbot returns "No results found" for every question
**Solution**: Run ingestion pipeline to populate vector database

### Issue: Frontend build fails - `Module not found: 'react'`
**Solution**: Delete `node_modules` and reinstall:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Slow LLM responses (>10s)
**Solution**: Check OpenAI API rate limits. Verify you're not on free tier with severe throttling.

### Issue: CORS errors in browser console
**Solution**: Ensure `CORS_ORIGINS` in `.env` includes `http://localhost:3000`

---

## Next Steps

1. **Read the Specification**: Review `specs/001-robotics-textbook-platform/spec.md` for full requirements
2. **Explore the Architecture**: Check `specs/001-robotics-textbook-platform/plan.md` for technical design
3. **Write Content**: Add chapters to `frontend/docs/chapters/`
4. **Run Tests**: Ensure all tests pass before making changes
5. **Start Development**: Pick a user story from the spec and implement it following TDD

## Useful Resources

- **Docusaurus Docs**: https://docusaurus.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **OpenAI API Docs**: https://platform.openai.com/docs
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/

## Getting Help

- **Issues**: Open an issue on GitHub
- **Questions**: Check `docs/architecture.md` for system design overview
- **Constitution**: Review `.specify/memory/constitution.md` for development principles

---

**Happy Coding!** 🤖📚
