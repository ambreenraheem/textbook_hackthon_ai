# RAG Pipeline Contract

**Date**: 2025-12-26
**Feature**: 001-robotics-textbook-platform
**Purpose**: Define input/output formats and data flow for the RAG (Retrieval-Augmented Generation) pipeline

## Pipeline Overview

The RAG pipeline transforms user questions into contextually accurate answers by:
1. **Retrieving** relevant textbook content chunks using hybrid search
2. **Reranking** results for optimal relevance
3. **Generating** LLM responses with citations
4. **Streaming** output to the user in real-time

## Pipeline Components

### Component 1: Content Ingestion

**Purpose**: Convert markdown textbook files into searchable vector embeddings

**Input**:
```python
{
    "source_path": str,  # Path to markdown file
    "content": str,  # Raw markdown content
    "metadata": {
        "chapter": str,  # Chapter title
        "chapter_number": int,  # e.g., 2
        "file_path": str  # Relative path from docs/
    }
}
```

**Processing Steps**:
1. Parse markdown → extract headings, sections, code blocks
2. Chunk content → semantic boundaries (400-600 tokens/chunk)
3. Generate embeddings → OpenAI text-embedding-3-small
4. Store in Qdrant → with metadata payload

**Output** (per chunk):
```python
{
    "id": "uuid",
    "text": str,  # Chunk content (400-600 tokens)
    "vector": List[float],  # 1536 dimensions
    "metadata": {
        "chapter": str,
        "section": str,
        "page": int,
        "url": str,
        "chunk_index": int,
        "created_at": str,  # ISO 8601
        "word_count": int,
        "has_code": bool,
        "has_equations": bool
    }
}
```

**Success Criteria**:
- 0 chunks lost (input count == output count)
- All vectors exactly 1536 dimensions
- All URLs valid and reachable
- Processing time <10s per 10K words

---

### Component 2: Hybrid Search Retrieval

**Purpose**: Find relevant content chunks for user query

**Input**:
```python
{
    "query": str,  # User's question (1-2000 chars)
    "filters": {
        "chapter": Optional[str],  # Filter by chapter
        "has_code": Optional[bool],  # Only code examples
        "has_equations": Optional[bool]  # Only equations
    },
    "top_k": int = 20  # Number of candidates to retrieve
}
```

**Processing Steps**:
1. **Vector Search**: Embed query → Qdrant similarity search → top 20 results (cosine > 0.6)
2. **Keyword Search**: Qdrant BM25 search → top 20 results
3. **Merge**: Reciprocal Rank Fusion (RRF) to combine rankings

**Output**:
```python
{
    "chunks": List[{
        "id": "uuid",
        "text": str,
        "score": float,  # Combined RRF score (0-1)
        "metadata": {
            "chapter": str,
            "section": str,
            "url": str,
            "page": int
        }
    }],
    "metrics": {
        "vector_search_latency_ms": int,
        "keyword_search_latency_ms": int,
        "total_latency_ms": int,
        "num_candidates": int
    }
}
```

**Success Criteria**:
- Latency <200ms p95
- Minimum 1 result returned (unless truly no relevant content)
- Scores in valid range [0, 1]

---

### Component 3: Reranking

**Purpose**: Refine chunk ranking using cross-encoder

**Input**:
```python
{
    "query": str,  # User's question
    "chunks": List[{
        "id": "uuid",
        "text": str,
        "score": float  # Initial RRF score
    }],
    "top_n": int = 5  # Final number of chunks to return
}
```

**Processing Steps**:
1. Compute query-chunk relevance scores using cross-encoder model
2. Sort by relevance score (descending)
3. Return top N chunks

**Output**:
```python
{
    "reranked_chunks": List[{
        "id": "uuid",
        "text": str,
        "relevance_score": float,  # 0-1, cross-encoder score
        "metadata": {
            "chapter": str,
            "section": str,
            "url": str,
            "page": int
        }
    }],
    "metrics": {
        "reranking_latency_ms": int,
        "score_distribution": {
            "min": float,
            "max": float,
            "mean": float
        }
    }
}
```

**Success Criteria**:
- Latency <100ms p95
- Top result relevance score ≥ 0.5 for well-formed queries
- Reranked order differs from initial order (reranking adds value)

---

### Component 4: LLM Generation

**Purpose**: Generate answer using retrieved context and stream to user

**Input**:
```python
{
    "query": str,  # User's question
    "context_chunks": List[{
        "id": "uuid",
        "text": str,
        "metadata": {
            "chapter": str,
            "section": str,
            "url": str
        }
    }],
    "conversation_history": List[{
        "role": "user" | "assistant",
        "content": str
    }],  # Previous messages (max 10 for context window management)
    "selected_text": Optional[str]  # User-selected context (P3 feature)
}
```

**Processing Steps**:
1. Build prompt with system instructions + context chunks + conversation history
2. Call OpenAI GPT-4 Turbo with streaming enabled
3. Stream tokens as they arrive
4. Track which chunks were cited in the response
5. Send citations as separate SSE events

**Output** (streaming):
```python
# Stream of events:
{
    "type": "token",
    "data": {"token": str}
}

{
    "type": "citation",
    "data": {
        "chunk_id": "uuid",
        "chapter": str,
        "section": str,
        "url": str
    }
}

{
    "type": "done",
    "data": {
        "conversation_id": "uuid",
        "message_id": "uuid",
        "total_tokens": int,
        "latency_ms": int
    }
}
```

**Success Criteria**:
- First token latency <1s p95
- Total response time <3s p95 for typical queries
- Citations match context chunks actually used (no hallucinated references)
- Streaming smooth (no long pauses between tokens)

---

## End-to-End Flow

### Example: User asks "How do I calculate inverse kinematics?"

**Step 1: Ingestion** (one-time, pre-deployment)
```
Input: frontend/docs/chapters/02-kinematics/inverse-kinematics.md
Output: 8 ContentChunks stored in Qdrant
```

**Step 2: User Submits Question**
```json
POST /api/chat
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "How do I calculate inverse kinematics for a 6-DOF robot arm?",
  "selected_text": null,
  "conversation_id": null
}
```

**Step 3: Hybrid Search**
```python
# Vector search: top 20 chunks (cosine similarity > 0.6)
# BM25 search: top 20 chunks (keyword matching "inverse kinematics", "6-DOF", "robot arm")
# RRF merge: 20 unique chunks ranked by combined score
```

**Step 4: Reranking**
```python
# Cross-encoder scores top 20 chunks
# Returns top 5: [chunk_A (0.92), chunk_B (0.87), chunk_C (0.81), chunk_D (0.76), chunk_E (0.68)]
```

**Step 5: LLM Generation**
```python
# Prompt template:
"""
You are an expert robotics educator. Answer the student's question using ONLY the provided textbook content.
Always cite specific chapters and sections when referencing content.

Context:
{chunk_A.text}
Source: {chunk_A.metadata.chapter}, {chunk_A.metadata.section}

{chunk_B.text}
Source: {chunk_B.metadata.chapter}, {chunk_B.metadata.section}

...

Student question: How do I calculate inverse kinematics for a 6-DOF robot arm?
"""

# GPT-4 streams response with inline citations
```

**Step 6: Stream to Frontend**
```
event: token
data: {"token": "To"}

event: token
data: {"token": " calculate"}

event: citation
data: {"chunk_id": "chunk_A_uuid", "chapter": "Robot Kinematics", "section": "2.3 Inverse Kinematics", "url": "/chapters/02-kinematics#inverse"}

event: token
data: {"token": " inverse"}

...

event: done
data: {"conversation_id": "new_uuid", "message_id": "msg_uuid"}
```

## Quality Metrics

### Retrieval Quality
- **Precision@5**: % of top 5 chunks relevant to query (target: ≥80%)
- **NDCG@5**: Normalized Discounted Cumulative Gain (target: ≥0.7)
- **Citation Accuracy**: % of citations that correctly link to content (target: ≥95%)

### Performance
- **Retrieval Latency**: p50, p95, p99 (target: <200ms p95)
- **LLM First Token**: p50, p95, p99 (target: <1s p95)
- **End-to-End Latency**: p50, p95, p99 (target: <3s p95)

### User Experience
- **Answer Relevance**: % of answers rated "helpful" by users (target: ≥85%)
- **Citation Usefulness**: % of users clicking citations (target: ≥50%)

## Error Handling

### Retrieval Failures
- **No results found**: Return helpful message ("I don't have information on that topic. Try asking about kinematics, dynamics, control systems...")
- **Qdrant timeout**: Retry once with exponential backoff, then fallback to cached popular chunks

### LLM Failures
- **OpenAI rate limit**: Queue request, return "High traffic, please wait 30 seconds..."
- **Streaming interruption**: Detect client disconnect, clean up resources, mark conversation as incomplete

### Data Quality Issues
- **Malformed chunks**: Log error, exclude from results, trigger re-ingestion job
- **Missing metadata**: Use defaults (chapter="Unknown", section="N/A"), log warning
