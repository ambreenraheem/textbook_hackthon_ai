# Vector Database Specialist Skill

## Metadata
- **Skill Name**: vector-db-specialist
- **Job**: Manage Qdrant Cloud vector database for RAG system
- **Version**: 1.0.0
- **Created**: 2025-12-26

## Purpose
Sets up, configures, and optimizes Qdrant Cloud vector database for storing and retrieving textbook content embeddings to power the RAG chatbot.

## Example Tasks
- Set up Qdrant Cloud Free Tier cluster
- Design collection schema with metadata
- Implement vector ingestion pipeline
- Optimize vector search parameters
- Create hybrid search capabilities
- Implement filtering and faceting
- Monitor collection performance
- Manage vector database scaling

## Required Knowledge
- Vector databases and embeddings
- Qdrant architecture and API
- Vector similarity search (cosine, dot product, euclidean)
- HNSW algorithm principles
- Metadata filtering
- Python async programming
- Batch processing

## Key Technologies
- Qdrant Cloud
- Qdrant Python Client
- OpenAI Embeddings API
- Vector similarity metrics
- HNSW indexing

## Qdrant Architecture
```
┌────────────────────────────────────────┐
│   Qdrant Cloud Cluster                 │
│                                        │
│   Collection: textbook_content         │
│   ┌────────────────────────────────┐  │
│   │  Vectors (1536 dimensions)     │  │
│   │  text-embedding-3-large        │  │
│   └────────────────────────────────┘  │
│                                        │
│   Payload (Metadata):                  │
│   ┌────────────────────────────────┐  │
│   │  - text (string)               │  │
│   │  - chapter (string)            │  │
│   │  - section (string)            │  │
│   │  - page_url (string)           │  │
│   │  - chunk_index (int)           │  │
│   │  - keywords (string[])         │  │
│   └────────────────────────────────┘  │
│                                        │
│   Indexes:                             │
│   - HNSW for vector search             │
│   - Keyword indexes for filtering      │
└────────────────────────────────────────┘
```

## Workflow Steps

### 1. Set Up Qdrant Cloud

**Sign up and create cluster:**
1. Go to https://cloud.qdrant.io
2. Create free tier cluster
3. Choose region (closest to backend)
4. Get API key and cluster URL

**Connection Info:**
```
URL: https://xxx-xxx-xxx.aws.cloud.qdrant.io
API Key: <your-api-key>
```

### 2. Initialize Qdrant Client

**app/services/qdrant_client.py**
```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import settings

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=60,
        )
        self.collection_name = "textbook_content"

    async def ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,  # text-embedding-3-large dimension
                    distance=Distance.COSINE,
                    on_disk=False,  # Keep in memory for speed
                ),
                # Optimize for search speed
                hnsw_config={
                    "m": 16,              # Number of edges per node
                    "ef_construct": 100,  # Build-time accuracy
                },
                # Enable payload index for filtering
                optimizers_config={
                    "memmap_threshold": 20000,
                },
            )

            # Create payload indexes
            self._create_payload_indexes()

    def _create_payload_indexes(self):
        """Create indexes for metadata filtering"""
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="chapter",
            field_schema="keyword",
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="section",
            field_schema="keyword",
        )
        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="keywords",
            field_schema="keyword",
        )
```

### 3. Vector Ingestion Pipeline

**app/services/ingestion.py**
```python
from typing import List, Dict
from qdrant_client.models import PointStruct
import uuid

class ContentIngestion:
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant = qdrant_service
        self.embedding_generator = EmbeddingGenerator()

    async def ingest_content(
        self,
        chunks: List[Dict],
        batch_size: int = 100
    ):
        """Ingest content chunks with embeddings"""

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]

            # Generate embeddings for batch
            texts = [chunk["text"] for chunk in batch]
            embeddings = await self.embedding_generator.generate_embeddings(
                texts
            )

            # Create points
            points = []
            for chunk, embedding in zip(batch, embeddings):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "chapter": chunk["metadata"]["chapter"],
                        "section": chunk["metadata"]["section"],
                        "page_url": chunk["metadata"]["page_url"],
                        "chunk_index": chunk["metadata"]["chunk_index"],
                        "keywords": chunk["metadata"].get("keywords", []),
                        "title": chunk["metadata"].get("title", ""),
                    }
                )
                points.append(point)

            # Upload to Qdrant
            self.qdrant.client.upsert(
                collection_name=self.qdrant.collection_name,
                points=points
            )

            print(f"Ingested batch {i//batch_size + 1}")
```

### 4. Vector Search Implementation

**app/services/vector_search.py**
```python
from typing import List, Dict, Optional
from qdrant_client.models import Filter, FieldCondition, MatchValue

class VectorSearch:
    def __init__(self, qdrant_service: QdrantService):
        self.qdrant = qdrant_service
        self.embedding_generator = EmbeddingGenerator()

    async def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
        filter_chapter: Optional[str] = None,
        filter_section: Optional[str] = None,
    ) -> List[Dict]:
        """Search for relevant content"""

        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embeddings(
            [query]
        )

        # Build filter
        search_filter = None
        if filter_chapter or filter_section:
            conditions = []
            if filter_chapter:
                conditions.append(
                    FieldCondition(
                        key="chapter",
                        match=MatchValue(value=filter_chapter)
                    )
                )
            if filter_section:
                conditions.append(
                    FieldCondition(
                        key="section",
                        match=MatchValue(value=filter_section)
                    )
                )

            search_filter = Filter(must=conditions)

        # Search
        results = self.qdrant.client.search(
            collection_name=self.qdrant.collection_name,
            query_vector=query_embedding[0],
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=search_filter,
            with_payload=True,
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.payload["text"],
                "metadata": {
                    "chapter": result.payload["chapter"],
                    "section": result.payload["section"],
                    "page_url": result.payload["page_url"],
                    "title": result.payload.get("title", ""),
                },
                "score": result.score,
                "id": result.id,
            })

        return formatted_results
```

### 5. Hybrid Search (Vector + Keyword)

**app/services/hybrid_search.py**
```python
class HybridSearch(VectorSearch):
    """Combines vector search with keyword filtering"""

    async def hybrid_search(
        self,
        query: str,
        keywords: List[str] = None,
        top_k: int = 10,
    ) -> List[Dict]:
        """Perform hybrid search"""

        # Vector search
        vector_results = await self.search(
            query=query,
            top_k=top_k * 2,  # Get more for reranking
        )

        # Keyword boost
        if keywords:
            vector_results = self._boost_by_keywords(
                vector_results,
                keywords
            )

        # Re-rank and return top_k
        return vector_results[:top_k]

    def _boost_by_keywords(
        self,
        results: List[Dict],
        keywords: List[str]
    ) -> List[Dict]:
        """Boost results containing keywords"""
        for result in results:
            keyword_score = 0
            text_lower = result["text"].lower()

            for keyword in keywords:
                if keyword.lower() in text_lower:
                    keyword_score += 0.1

            # Boost score
            result["score"] = min(1.0, result["score"] + keyword_score)

        # Re-sort by score
        return sorted(results, key=lambda x: x["score"], reverse=True)
```

### 6. Batch Operations

**app/services/batch_operations.py**
```python
class BatchOperations:
    """Efficient batch operations for Qdrant"""

    def __init__(self, qdrant_service: QdrantService):
        self.qdrant = qdrant_service

    async def batch_search(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> List[List[Dict]]:
        """Search multiple queries in batch"""

        # Generate embeddings
        query_embeddings = await self.embedding_generator.generate_embeddings(
            queries
        )

        # Batch search
        results = []
        for embedding in query_embeddings:
            batch_results = self.qdrant.client.search(
                collection_name=self.qdrant.collection_name,
                query_vector=embedding,
                limit=top_k,
            )
            results.append(batch_results)

        return results

    async def update_metadata(
        self,
        point_ids: List[str],
        metadata_updates: List[Dict]
    ):
        """Batch update metadata without changing vectors"""

        for point_id, metadata in zip(point_ids, metadata_updates):
            self.qdrant.client.set_payload(
                collection_name=self.qdrant.collection_name,
                payload=metadata,
                points=[point_id],
            )
```

## Integration Points
- **rag-specialist**: Provides vector retrieval
- **backend-engineer**: Integrates into FastAPI
- **content-writer**: Ingests content chunks
- **deployment-expert**: Manages Qdrant Cloud setup

## Success Criteria
- [ ] Qdrant collection created with correct schema
- [ ] All content successfully ingested
- [ ] Search returns relevant results (>85% precision)
- [ ] Search latency < 200ms
- [ ] Metadata filtering works correctly
- [ ] Batch operations are optimized
- [ ] Monitoring is configured
- [ ] Backup strategy is in place

## Performance Optimization

### Vector Search Optimization
```python
# Optimize HNSW parameters
hnsw_config = {
    "m": 16,              # Higher = better recall, more memory
    "ef_construct": 100,  # Higher = better index quality
}

# Search-time optimization
search_params = {
    "hnsw_ef": 128,      # Higher = better recall, slower search
    "exact": False,      # Use approximate search
}
```

### Memory Optimization
- Use `on_disk=True` for large collections (>1M vectors)
- Optimize payload size (only store necessary metadata)
- Use quantization for reduced memory (if needed)

### Indexing Strategy
```python
# Create selective indexes
self.client.create_payload_index(
    collection_name=self.collection_name,
    field_name="chapter",
    field_schema="keyword",  # For exact matches
)
```

## Monitoring and Maintenance

### Collection Statistics
```python
def get_collection_info(self):
    """Get collection statistics"""
    info = self.qdrant.client.get_collection(
        self.collection_name
    )

    return {
        "vectors_count": info.vectors_count,
        "indexed_vectors_count": info.indexed_vectors_count,
        "points_count": info.points_count,
        "segments_count": info.segments_count,
        "status": info.status,
    }
```

### Health Checks
```python
async def health_check(self) -> bool:
    """Check Qdrant cluster health"""
    try:
        collections = self.qdrant.client.get_collections()
        return True
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        return False
```

## Data Management

### Backup Strategy
```python
async def export_collection(self, output_path: str):
    """Export collection to file"""
    # Scroll through all points
    points = []
    offset = None

    while True:
        result = self.qdrant.client.scroll(
            collection_name=self.collection_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=True,
        )

        points.extend(result[0])
        offset = result[1]

        if offset is None:
            break

    # Save to file
    import json
    with open(output_path, 'w') as f:
        json.dump([p.dict() for p in points], f)
```

### Restore from Backup
```python
async def restore_collection(self, backup_path: str):
    """Restore collection from backup"""
    import json

    with open(backup_path, 'r') as f:
        points_data = json.load(f)

    # Recreate points
    points = [PointStruct(**p) for p in points_data]

    # Upload in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        self.qdrant.client.upsert(
            collection_name=self.collection_name,
            points=points[i:i + batch_size]
        )
```

## Best Practices
- Use appropriate vector dimensions (1536 for text-embedding-3-large)
- Choose correct distance metric (cosine for embeddings)
- Index only frequently filtered fields
- Use batch operations for bulk uploads
- Monitor collection size and performance
- Implement retry logic for API calls
- Use async operations where possible
- Regularly backup important collections
- Test different HNSW parameters for your use case
- Keep payload size minimal

## Testing

**tests/test_qdrant.py**
```python
import pytest
from app.services.qdrant_client import QdrantService

@pytest.fixture
def qdrant_service():
    return QdrantService()

@pytest.mark.asyncio
async def test_search(qdrant_service):
    results = await qdrant_service.search(
        query="What is physical AI?",
        top_k=5
    )
    assert len(results) <= 5
    assert all("score" in r for r in results)
```

## Qdrant Cloud Free Tier Limits
- 1 GB storage
- 1 cluster
- Suitable for up to ~100K vectors (1536 dimensions)
- Adequate for textbook RAG system

## Scaling Considerations
- Monitor storage usage in Qdrant dashboard
- Implement collection sharding if needed
- Consider paid tier for larger textbooks
- Optimize chunk size to fit more content

## Output Artifacts
- Qdrant client service code
- Collection schema configuration
- Ingestion pipeline scripts
- Search and retrieval implementations
- Batch operation utilities
- Backup and restore scripts
- Performance optimization guide
- Monitoring dashboards
