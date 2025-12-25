# RAG Specialist Skill

## Metadata
- **Skill Name**: rag-specialist
- **Job**: Design and implement Retrieval-Augmented Generation (RAG) pipeline
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Architects and implements the complete RAG pipeline for the textbook chatbot, including content chunking, embedding generation, vector search, and context-aware response generation.

## Example Tasks
- Design content chunking strategy
- Implement embedding generation pipeline
- Build hybrid search (vector + keyword)
- Create reranking mechanism
- Implement context window optimization
- Build citation extraction system
- Design prompt templates for LLM
- Optimize retrieval quality and relevance

## Required Knowledge
- RAG architecture patterns
- Vector embeddings and similarity search
- Text chunking strategies
- Prompt engineering
- LLM context management
- Information retrieval principles
- Embedding models (OpenAI, sentence-transformers)

## Key Technologies
- OpenAI Embeddings API (text-embedding-3-large)
- Qdrant vector database
- LangChain (optional, for orchestration)
- Sentence transformers (optional)
- FAISS (for local testing)
- Python async libraries

## RAG Pipeline Architecture
```
User Query
    ↓
Query Enhancement
    ↓
Embedding Generation
    ↓
Vector Search (Qdrant)
    ↓
Reranking
    ↓
Context Assembly
    ↓
Prompt Construction
    ↓
LLM Generation (OpenAI)
    ↓
Citation Extraction
    ↓
Response + Citations
```

## Workflow Steps

### 1. Content Chunking Strategy
```python
from typing import List, Dict
import tiktoken

class ContentChunker:
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        encoding_name: str = "cl100k_base"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)

    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Chunk text with metadata preservation"""
        chunks = []
        tokens = self.encoding.encode(text)

        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": len(chunks),
                    "start_char": i,
                }
            })

        return chunks
```

### 2. Embedding Generation
```python
from openai import AsyncOpenAI
import numpy as np

class EmbeddingGenerator:
    def __init__(self, model: str = "text-embedding-3-large"):
        self.client = AsyncOpenAI()
        self.model = model

    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """Generate embeddings in batches"""
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            response = await self.client.embeddings.create(
                model=self.model,
                input=batch
            )

            embeddings.extend([e.embedding for e in response.data])

        return embeddings
```

### 3. RAG Service Implementation
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class RAGService:
    def __init__(
        self,
        qdrant_client: QdrantClient,
        collection_name: str = "textbook_content"
    ):
        self.qdrant = qdrant_client
        self.collection_name = collection_name
        self.embedding_generator = EmbeddingGenerator()

    async def retrieve_context(
        self,
        query: str,
        selected_text: Optional[str] = None,
        top_k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict]:
        """Retrieve relevant context chunks"""

        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embeddings([query])

        # Search Qdrant
        search_results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_embedding[0],
            limit=top_k,
            score_threshold=score_threshold
        )

        # If selected text is provided, boost its relevance
        if selected_text:
            search_results = self._boost_selected_text(
                search_results,
                selected_text
            )

        # Extract and format context
        context_chunks = []
        for result in search_results:
            context_chunks.append({
                "text": result.payload["text"],
                "metadata": result.payload["metadata"],
                "score": result.score
            })

        return context_chunks

    def _boost_selected_text(
        self,
        results: List,
        selected_text: str
    ) -> List:
        """Boost chunks containing or related to selected text"""
        # Implementation for boosting relevant chunks
        pass
```

### 4. Prompt Engineering
```python
class PromptTemplate:
    SYSTEM_PROMPT = """You are an expert teaching assistant for the Physical AI
    and Humanoid Robotics textbook. Your role is to:

    1. Answer questions accurately based on the provided context
    2. Cite specific sections when making claims
    3. Admit when information is not in the context
    4. Explain concepts clearly and pedagogically
    5. Relate concepts to practical applications

    Always be helpful, accurate, and educational."""

    @staticmethod
    def build_rag_prompt(
        query: str,
        context_chunks: List[Dict],
        selected_text: Optional[str] = None
    ) -> str:
        """Build the complete RAG prompt"""

        context_str = "\n\n".join([
            f"[Source {i+1}: {chunk['metadata']['source']}]\n{chunk['text']}"
            for i, chunk in enumerate(context_chunks)
        ])

        if selected_text:
            prompt = f"""Selected Text:
{selected_text}

Question: {query}

Relevant Context:
{context_str}

Please answer the question focusing on the selected text,
but use the additional context for comprehensive explanation.
Include citations to specific sources."""
        else:
            prompt = f"""Question: {query}

Relevant Context:
{context_str}

Please answer the question based on the context provided.
Include citations to specific sources."""

        return prompt
```

### 5. Response Generation with Citations
```python
from openai import AsyncOpenAI

class ResponseGenerator:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def generate_response(
        self,
        user_message: str,
        context: List[Dict],
        selected_text: Optional[str] = None
    ) -> Dict:
        """Generate response with citations"""

        prompt = PromptTemplate.build_rag_prompt(
            query=user_message,
            context_chunks=context,
            selected_text=selected_text
        )

        response = await self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": PromptTemplate.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Extract citations from response
        citations = self._extract_citations(
            response.choices[0].message.content,
            context
        )

        return {
            "content": response.choices[0].message.content,
            "citations": citations,
            "context_used": context
        }

    def _extract_citations(
        self,
        response_text: str,
        context: List[Dict]
    ) -> List[Dict]:
        """Extract and format citations from response"""
        citations = []

        # Look for citation markers like [Source 1]
        import re
        citation_pattern = r'\[Source (\d+)\]'
        matches = re.finditer(citation_pattern, response_text)

        for match in matches:
            source_idx = int(match.group(1)) - 1
            if source_idx < len(context):
                chunk = context[source_idx]
                citations.append({
                    "text": chunk["text"][:200] + "...",
                    "source": chunk["metadata"]["source"],
                    "page_url": chunk["metadata"]["url"],
                    "score": chunk["score"]
                })

        return citations
```

### 6. Hybrid Search Implementation
```python
class HybridSearchRAG(RAGService):
    """RAG with hybrid vector + keyword search"""

    async def retrieve_context(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict]:
        # Vector search
        vector_results = await super().retrieve_context(query, top_k=top_k)

        # Keyword search (using Qdrant's payload filtering)
        keyword_results = self._keyword_search(query, top_k=top_k)

        # Combine and rerank
        combined_results = self._rerank(vector_results, keyword_results)

        return combined_results[:top_k]

    def _rerank(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict]
    ) -> List[Dict]:
        """Rerank results using RRF (Reciprocal Rank Fusion)"""
        # Implementation
        pass
```

## Integration Points
- **backend-engineer**: Integrates into FastAPI service
- **vector-db-specialist**: Uses Qdrant operations
- **database-engineer**: Stores metadata and logs
- **content-writer**: Optimizes content for retrieval

## Success Criteria
- [ ] Retrieval precision > 85% on test queries
- [ ] Average retrieval time < 500ms
- [ ] Citations are accurate and relevant
- [ ] Context window is optimally utilized
- [ ] Handles edge cases (no results, ambiguous queries)
- [ ] Selected text queries work accurately
- [ ] Embedding generation is batched efficiently
- [ ] Response quality is high

## Optimization Strategies

### Chunking Optimization
- Semantic chunking (preserve paragraph boundaries)
- Optimal chunk size (512-1024 tokens)
- Overlap for context continuity
- Metadata preservation (chapter, section, page)

### Retrieval Optimization
- Hybrid search (vector + keyword)
- Reranking with cross-encoder
- Query expansion and reformulation
- Metadata filtering (by chapter, topic)

### Response Optimization
- Context compression
- Prompt caching
- Streaming responses
- Citation tracking

## Evaluation Metrics
```python
class RAGEvaluator:
    """Evaluate RAG pipeline quality"""

    def calculate_retrieval_precision(
        self,
        retrieved_docs: List[Dict],
        relevant_docs: List[Dict]
    ) -> float:
        """Calculate precision of retrieval"""
        pass

    def calculate_answer_relevance(
        self,
        question: str,
        answer: str,
        context: List[Dict]
    ) -> float:
        """Evaluate answer relevance using LLM"""
        pass

    def calculate_citation_accuracy(
        self,
        answer: str,
        citations: List[Dict]
    ) -> float:
        """Verify citation accuracy"""
        pass
```

## Best Practices
- Use semantic chunking for better context
- Implement query enhancement (expansion, rephrasing)
- Use reranking for better precision
- Cache embeddings for frequently accessed content
- Monitor retrieval metrics continuously
- A/B test different chunking strategies
- Use metadata filtering for scoped searches
- Implement fallback strategies
- Log failed retrievals for improvement
- Optimize prompt templates iteratively

## Testing Strategy
- Unit tests for each component
- Integration tests for full pipeline
- Evaluation on golden dataset
- A/B testing different strategies
- User feedback collection
- Performance benchmarking

## Output Artifacts
- RAG service implementation
- Chunking strategy code
- Embedding generation pipeline
- Prompt templates
- Evaluation scripts
- Performance metrics dashboard
- Documentation and best practices guide
