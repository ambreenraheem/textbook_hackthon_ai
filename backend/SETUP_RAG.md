# RAG Pipeline Setup Guide

This guide covers setting up and testing the RAG (Retrieval-Augmented Generation) pipeline for the Physical AI & Humanoid Robotics textbook chatbot.

## Prerequisites

### 1. Environment Variables

Ensure your `.env` file in the project root contains:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_chunks

# Neon Postgres Configuration
DATABASE_URL=postgresql://user:password@host/database

# RAG Configuration (optional - has defaults)
LLM_MODEL=gpt-4-turbo-preview
MAX_TOKENS=2000
TEMPERATURE=0.7
RETRIEVAL_TOP_K=20
RERANK_TOP_N=5
MIN_SIMILARITY_SCORE=0.6

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Database

```bash
# Create database tables
cd backend
python -c "from src.utils.database import create_tables; create_tables()"
```

Expected output:
```
INFO - Initializing database connection
INFO - Database initialized successfully
INFO - Creating database tables
INFO - Database tables created successfully
```

### 4. Setup Qdrant Collection

```bash
cd backend
python src/utils/qdrant_setup.py
```

Expected output:
```
Connecting to Qdrant at https://your-cluster.qdrant.io...
Creating collection 'textbook_chunks'...
[OK] Collection 'textbook_chunks' created successfully!
Creating payload indexes...
[OK] Created index on 'chapter' field
[OK] Created index on 'section' field
[OK] Created index on 'page' field

[COLLECTION INFO]
   Name: textbook_chunks
   Vector size: 1536
   Distance: COSINE
   Points count: 0

[SUCCESS] Qdrant setup complete!
```

## Running the Server

### Development Mode

```bash
cd backend
python -m src.api.main
```

Or with uvicorn directly:

```bash
cd backend
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO - Starting FastAPI application in development environment
INFO - Initializing database connection
INFO - Database initialized successfully
INFO - Database tables created successfully
INFO - Database initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Production Mode

```bash
cd backend
export ENVIRONMENT=production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Testing the API

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "vector_db": "ok",
    "openai": "ok"
  },
  "timestamp": "2025-12-30T10:00:00Z"
}
```

### 2. Root Endpoint

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "name": "Physical AI & Humanoid Robotics Textbook API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

### 3. Interactive API Documentation

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 4. Chat Endpoint (SSE Streaming)

**Using curl**:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "What is inverse kinematics?",
    "selected_text": null,
    "conversation_id": null
  }' \
  --no-buffer
```

Expected output (SSE stream):
```
event: token
data: {"token": "Inverse"}

event: token
data: {"token": " kinematics"}

event: token
data: {"token": " is"}

...

event: citation
data: {"chunk_id": "uuid-here", "chapter": "Robot Kinematics", "section": "2.3 Inverse Kinematics", "url": "/chapters/02-kinematics#inverse-kinematics"}

event: done
data: {"conversation_id": "conv-uuid", "message_id": "msg-uuid"}
```

**Using Python**:

```python
import requests
import json
import uuid

def chat_stream(message, session_id=None):
    if session_id is None:
        session_id = str(uuid.uuid4())

    url = "http://localhost:8000/api/chat"
    payload = {
        "session_id": session_id,
        "message": message,
        "selected_text": None,
        "conversation_id": None
    }

    response = requests.post(url, json=payload, stream=True)

    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('event:'):
                event_type = line.split(':', 1)[1].strip()
            elif line.startswith('data:'):
                data = json.loads(line.split(':', 1)[1].strip())

                if event_type == 'token':
                    print(data['token'], end='', flush=True)
                elif event_type == 'citation':
                    print(f"\n[Citation: {data['chapter']} > {data['section']}]")
                elif event_type == 'done':
                    print(f"\n\n[Done - Conversation: {data['conversation_id']}]")

# Usage
chat_stream("What is inverse kinematics?")
```

**Using JavaScript (fetch)**:

```javascript
async function chat(message, sessionId) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId || crypto.randomUUID(),
      message: message,
      selected_text: null,
      conversation_id: null
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('event:')) {
        const eventType = line.split(':')[1].trim();
      } else if (line.startsWith('data:')) {
        const data = JSON.parse(line.split(':', 2)[1].trim());

        if (eventType === 'token') {
          console.log(data.token);
        } else if (eventType === 'citation') {
          console.log(`Citation: ${data.chapter} > ${data.section}`);
        } else if (eventType === 'done') {
          console.log(`Done - Conversation: ${data.conversation_id}`);
        }
      }
    }
  }
}

// Usage
chat('What is inverse kinematics?', 'session-uuid');
```

## Testing Individual Components

### Test Retrieval Service

```python
from src.services.retrieval import HybridRetriever

# Initialize retriever
retriever = HybridRetriever()

# Test vector search
chunks = retriever.vector_search(
    query="inverse kinematics",
    top_k=5
)
print(f"Found {len(chunks)} chunks")
for i, chunk in enumerate(chunks, 1):
    print(f"{i}. {chunk.chapter} > {chunk.section} (score: {chunk.score:.4f})")

# Test BM25 search
chunks = retriever.bm25_search(
    query="inverse kinematics",
    top_k=5
)
print(f"Found {len(chunks)} chunks")

# Test hybrid search
chunks = retriever.retrieve(
    query="inverse kinematics",
    top_k=5,
    use_hybrid=True
)
print(f"Found {len(chunks)} chunks (hybrid)")
```

### Test RAG Pipeline

```python
from src.services.rag import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Test retrieval
chunks = pipeline.retrieve_context(
    query="What is forward kinematics?",
    top_k=3
)
print(f"Retrieved {len(chunks)} chunks")

# Test context formatting
context = pipeline.format_context_for_llm(chunks)
print(context)

# Test full pipeline
messages, chunks = pipeline.process_query(
    query="Explain the DH convention",
    selected_text=None,
    conversation_history=None
)
print(f"Prepared {len(messages)} messages with {len(chunks)} chunks")
```

### Test Streaming LLM

```python
import asyncio
from src.services.llm import StreamingLLM
from src.services.rag import RAGPipeline

async def test_streaming():
    # Setup
    pipeline = RAGPipeline()
    llm = StreamingLLM()

    # Process query
    messages, chunks = pipeline.process_query(
        query="What is a robot?"
    )

    # Stream response
    print("Streaming response:")
    async for event in llm.stream_response(messages, chunks):
        if event["type"] == "token":
            print(event["data"]["token"], end="", flush=True)
        elif event["type"] == "citation":
            print(f"\n[Citation: {event['data']['chapter']}]")

    print("\n\nDone!")

# Run
asyncio.run(test_streaming())
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
- Verify `DATABASE_URL` in `.env`
- Check database server is running
- Ensure network connectivity to Neon

#### 2. Qdrant Connection Error

```
qdrant_client.http.exceptions.UnexpectedResponse: Unexpected Response: 401
```

**Solution**:
- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Check Qdrant cluster is running
- Verify API key has correct permissions

#### 3. OpenAI API Error

```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution**:
- Verify `OPENAI_API_KEY` in `.env`
- Check API key is valid and active
- Ensure billing is enabled

#### 4. Rate Limit Exceeded

```
HTTP 429: Rate limit exceeded
```

**Solution**:
- Wait 60 seconds before retrying
- Reduce request frequency
- Consider increasing rate limit in code

#### 5. No Chunks Retrieved

```
Retrieved 0 chunks for query
```

**Solution**:
- Verify Qdrant collection has data
- Check collection name matches `QDRANT_COLLECTION_NAME`
- Run ingestion pipeline to populate collection
- Lower `MIN_SIMILARITY_SCORE` threshold

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m src.api.main
```

This will show detailed logs for:
- Database queries
- Qdrant searches
- OpenAI API calls
- Token counts
- Error stack traces

### Performance Monitoring

Check logs for performance metrics:

```bash
grep "latency_ms" logs/app.log | tail -20
```

Expected latencies:
- Vector search: 50-200ms
- BM25 search: 100-500ms
- LLM TTFB: 300-1000ms
- Total request: 2-5 seconds

## Next Steps

1. **Ingest Content**: Run ingestion pipeline to populate Qdrant
2. **Test E2E**: Test complete flow from frontend to backend
3. **Monitor**: Set up logging and monitoring
4. **Optimize**: Tune retrieval parameters for quality
5. **Deploy**: Deploy to production environment

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Server-Sent Events Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
