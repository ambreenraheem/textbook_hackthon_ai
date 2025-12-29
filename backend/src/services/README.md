# RAG Services Implementation

This directory contains the core RAG (Retrieval-Augmented Generation) pipeline components for the Physical AI & Humanoid Robotics textbook chatbot.

## Architecture Overview

```
User Query → Retrieval → RAG Pipeline → Streaming LLM → SSE Response
              ↓              ↓                ↓             ↓
          Qdrant +      Context         GPT-4 Turbo    Citations +
          BM25         Formatting                       Tokens
```

## Services

### 1. Retrieval Service (`retrieval.py`)

**Purpose**: Hybrid search combining vector similarity and keyword matching.

**Key Components**:
- `HybridRetriever`: Main retrieval orchestrator
- `BM25`: Keyword search implementation
- `RetrievedChunk`: Data class for retrieved content

**Features**:
- Vector similarity search using Qdrant (cosine similarity)
- BM25 keyword search for exact term matching
- Reciprocal Rank Fusion (RRF) for combining results
- Metadata filtering (chapter, section)
- Configurable top-K retrieval

**Usage**:
```python
from src.services.retrieval import HybridRetriever

retriever = HybridRetriever()
chunks = retriever.retrieve(
    query="How do inverse kinematics work?",
    top_k=5,
    chapter_filter="Robot Kinematics"  # optional
)
```

**Algorithm Details**:

**BM25 Scoring**:
```
BM25(D, Q) = Σ IDF(qi) × (f(qi, D) × (k1 + 1)) / (f(qi, D) + k1 × (1 - b + b × |D| / avgdl))
```
- `k1`: Term frequency saturation (default: 1.5)
- `b`: Length normalization (default: 0.75)

**Reciprocal Rank Fusion (RRF)**:
```
RRF_score = Σ 1 / (k + rank_i)
```
- Combines rankings from vector and BM25 search
- `k`: Fusion parameter (default: 60)

### 2. RAG Pipeline (`rag.py`)

**Purpose**: Orchestrates retrieval and context preparation for LLM.

**Key Components**:
- `RAGPipeline`: Main orchestrator
- `ConversationMessage`: Message wrapper

**Features**:
- Context retrieval with optional selected text enhancement
- Context formatting with metadata (chapter, section, page)
- Conversation history management
- Token budget optimization
- System prompt configuration

**Usage**:
```python
from src.services.rag import RAGPipeline

pipeline = RAGPipeline()
messages, chunks = pipeline.process_query(
    query="Explain forward kinematics",
    selected_text="The Denavit-Hartenberg convention...",  # optional
    conversation_history=[("user", "What is a robot?"), ("assistant", "A robot is...")],  # optional
)
```

**Context Format**:
```
=== TEXTBOOK CONTEXT ===
[Chunk 1]
Source: Robot Kinematics > Forward Kinematics
Page: 42
Content: Forward kinematics involves calculating...

[Chunk 2]
Source: Robot Kinematics > DH Parameters
Page: 45
Content: The Denavit-Hartenberg convention...
=== END CONTEXT ===
```

**Token Optimization**:
- Estimates tokens (1 token ≈ 4 characters)
- Filters chunks to fit within budget (default: 4000 tokens)
- Prioritizes highest-ranked chunks

### 3. Streaming LLM Service (`llm.py`)

**Purpose**: Generate streaming responses with citation extraction.

**Key Components**:
- `StreamingLLM`: Async streaming handler
- `CitationExtractor`: Regex-based citation parser
- `SSEFormatter`: Server-Sent Events formatter

**Features**:
- Async streaming from OpenAI GPT-4 Turbo
- Real-time token emission
- Citation extraction from `[Chunk N]` references
- SSE-formatted events
- Error handling with retries

**Usage**:
```python
from src.services.llm import StreamingLLM

llm = StreamingLLM()
async for event in llm.stream_response(messages, chunks):
    if event["type"] == "token":
        print(event["data"]["token"], end="", flush=True)
    elif event["type"] == "citation":
        print(f"\n[Citation: {event['data']['chapter']}]")
```

**Event Types**:

1. **Token Event**:
```json
{
  "type": "token",
  "data": {"token": "kinematics"}
}
```

2. **Citation Event**:
```json
{
  "type": "citation",
  "data": {
    "chunk_id": "uuid",
    "chapter": "Robot Kinematics",
    "section": "2.3 Inverse Kinematics",
    "url": "/chapters/02-kinematics#inverse-kinematics"
  }
}
```

3. **Error Event**:
```json
{
  "type": "error",
  "data": {
    "error": "RateLimitError",
    "message": "API rate limit exceeded..."
  }
}
```

**Citation Extraction**:
- Regex pattern: `\[Chunk\s+(\d+(?:\s*,\s*\d+)*)\]`
- Matches: `[Chunk 1]`, `[Chunk 2, 3]`, etc.
- Maps chunk numbers to metadata

### 4. Embeddings Service (`embeddings.py`)

**Purpose**: Generate embeddings with caching and batching.

**Key Features**:
- File-based embedding cache
- Batch processing (100 texts/batch)
- Rate limiting with exponential backoff
- Progress tracking

**Usage**:
```python
from src.services.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()
embedding = generator.generate_embedding("What is a robot?")
embeddings = generator.generate_embeddings_batch(texts, show_progress=True)
```

## Configuration

All services use settings from `src/config/settings.py`:

```python
# RAG Configuration
llm_model: str = "gpt-4-turbo-preview"
max_tokens: int = 2000
temperature: float = 0.7

# Retrieval Configuration
retrieval_top_k: int = 20  # Retrieve 20 chunks before fusion
rerank_top_n: int = 5      # Return top 5 after fusion
min_similarity_score: float = 0.6

# Embedding Configuration
embedding_model: str = "text-embedding-3-small"
embedding_dimensions: int = 1536
```

## Error Handling

All services implement comprehensive error handling:

1. **OpenAI Errors**:
   - `RateLimitError`: Exponential backoff retry
   - `APITimeoutError`: Timeout notification
   - `APIError`: Generic API error handling

2. **Qdrant Errors**:
   - Connection failures
   - Collection not found
   - Invalid filters

3. **Database Errors**:
   - Connection failures
   - Transaction rollback
   - Constraint violations

## Logging

All services use structured logging with correlation IDs:

```python
logger.info(
    "Retrieved chunks for query",
    extra={
        "extra_fields": {
            "num_chunks": len(chunks),
            "query_length": len(query),
            "has_selected_text": selected_text is not None
        }
    }
)
```

## Performance Considerations

### Retrieval Performance
- Vector search: O(log N) with HNSW index
- BM25 search: O(N × M) where N=docs, M=query_terms
- RRF fusion: O(K) where K=top_k

### Token Budget
- System prompt: ~400 tokens
- Context (5 chunks): ~1500 tokens
- Conversation history (5 messages): ~500 tokens
- User query: ~100 tokens
- **Total input**: ~2500 tokens
- **Max output**: 2000 tokens
- **Total**: ~4500 tokens (within GPT-4 Turbo limit)

### Streaming Benefits
- Reduced perceived latency (TTFB: ~500ms)
- Real-time user feedback
- Better UX for long responses
- Lower memory footprint

## Testing

Run service tests:
```bash
pytest backend/tests/services/ -v
```

Test individual components:
```bash
# Test retrieval
pytest backend/tests/services/test_retrieval.py -v

# Test RAG pipeline
pytest backend/tests/services/test_rag.py -v

# Test streaming LLM
pytest backend/tests/services/test_llm.py -v
```

## Integration

Services are integrated in the chat API endpoint (`src/api/chat.py`):

```python
# Initialize services
rag_pipeline = RAGPipeline()
streaming_llm = StreamingLLM()

# Process query
messages, chunks = rag_pipeline.process_query(...)

# Stream response
async for event in streaming_llm.stream_response(messages, chunks):
    yield SSEFormatter.format_event(event["type"], event["data"])
```

## Future Enhancements

1. **Advanced Reranking**:
   - Cross-encoder reranking (e.g., BERT-based)
   - Cohere Rerank API integration
   - Custom relevance scoring

2. **Context Optimization**:
   - Chunk deduplication
   - Semantic compression
   - Dynamic context window adjustment

3. **Citation Improvements**:
   - Inline citation extraction (mid-stream)
   - Confidence scoring
   - Multi-modal citations (images, code)

4. **Performance Optimization**:
   - Query result caching
   - Embedding caching in Redis
   - Batch inference for multiple users

5. **Observability**:
   - Latency metrics (p50, p95, p99)
   - Retrieval quality metrics (MRR, NDCG)
   - LLM performance tracking
   - Cost monitoring (token usage)
