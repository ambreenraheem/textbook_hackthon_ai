# Content Ingestion Module

This module provides a complete pipeline for ingesting textbook content into the Qdrant vector database for RAG-based retrieval.

## Overview

The ingestion pipeline consists of four main stages:

1. **Parsing**: Extract structured content from MDX/Markdown files
2. **Chunking**: Split content into semantic chunks (400-600 tokens)
3. **Embedding**: Generate vector embeddings using OpenAI text-embedding-3-small
4. **Storage**: Store chunks and embeddings in Qdrant

## Components

### 1. Parser (`parser.py`)

Extracts structured information from markdown/MDX files:

- **Frontmatter metadata**: Title, description, keywords, etc.
- **Section hierarchy**: Headings at all levels (H1-H6)
- **Code blocks**: Language-tagged code snippets
- **MDX components**: Preserved as text in content

**Key Classes**:
- `MarkdownParser`: Main parser class
- `ParsedDocument`: Container for parsed content
- `Section`: Individual section with heading and content
- `CodeBlock`: Code block with language metadata

**Usage**:
```python
from src.ingestion.parser import MarkdownParser
from pathlib import Path

parser = MarkdownParser()

# Parse single file
doc = parser.parse_file(Path("frontend/docs/intro.md"))
print(f"Title: {doc.title}")
print(f"Sections: {len(doc.sections)}")

# Parse entire directory
docs = parser.parse_directory(Path("frontend/docs"))
print(f"Parsed {len(docs)} documents")
```

### 2. Chunker (`chunker.py`)

Splits documents into semantic chunks optimized for retrieval:

- **Target size**: 400-600 tokens
- **Respects boundaries**: Splits at heading/paragraph boundaries
- **Overlap**: 50 tokens between chunks for context
- **Metadata preservation**: Chapter, section, URL, etc.

**Key Classes**:
- `SemanticChunker`: Main chunking class
- `ContentChunk`: Individual chunk with metadata

**Usage**:
```python
from src.ingestion.chunker import SemanticChunker

chunker = SemanticChunker(
    min_chunk_size=400,
    max_chunk_size=600,
    overlap_size=50
)

# Chunk single document
chunks = chunker.chunk_document(parsed_doc)
print(f"Created {len(chunks)} chunks")

# Chunk multiple documents
all_chunks = chunker.chunk_documents(parsed_docs)
```

### 3. Embeddings (`services/embeddings.py`)

Generates vector embeddings using OpenAI's text-embedding-3-small model:

- **Batch processing**: Up to 100 texts per API call
- **Rate limiting**: Exponential backoff for rate limits
- **Caching**: File-based cache to avoid recomputation
- **Progress tracking**: Logs batch progress

**Key Classes**:
- `EmbeddingGenerator`: Main embedding service
- `EmbeddingCache`: File-based embedding cache

**Usage**:
```python
from src.services.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(
    batch_size=100,
    use_cache=True
)

# Single embedding
embedding = generator.generate_embedding("Your text here")
print(f"Embedding dimension: {len(embedding)}")  # 1536

# Batch embeddings
texts = [chunk.text for chunk in chunks]
embeddings = generator.generate_embeddings_batch(texts, show_progress=True)
```

### 4. Pipeline (`pipeline.py`)

Orchestrates the complete ingestion workflow:

- **Parse → Chunk → Embed → Store**
- **Progress tracking**: Logs each stage
- **Statistics**: Reports files, chunks, embeddings, duration
- **Validation**: Verifies successful ingestion

**Key Classes**:
- `IngestionPipeline`: Main orchestrator

**Usage**:
```python
from src.ingestion.pipeline import IngestionPipeline
from pathlib import Path

pipeline = IngestionPipeline(
    input_dir=Path("frontend/docs"),
    rebuild=True,  # Rebuild collection from scratch
    batch_size=100,
    use_cache=True
)

# Run pipeline
stats = pipeline.run()
print(f"Processed {stats['files_parsed']} files")
print(f"Created {stats['chunks_created']} chunks")
print(f"Duration: {stats['duration_seconds']:.2f}s")

# Validate
if pipeline.validate():
    print("Validation passed!")
```

## CLI Interface

The ingestion pipeline provides a command-line interface for easy execution:

```bash
# Basic usage (default: frontend/docs)
python backend/ingest_content.py

# Rebuild collection from scratch
python backend/ingest_content.py --rebuild

# Custom input directory
python backend/ingest_content.py --input path/to/docs

# Validate after ingestion
python backend/ingest_content.py --validate

# Disable cache (force regenerate embeddings)
python backend/ingest_content.py --no-cache

# Custom batch size
python backend/ingest_content.py --batch-size 50

# Combined options
python backend/ingest_content.py --rebuild --validate --batch-size 100
```

## Configuration

The pipeline uses settings from `backend/src/config/settings.py`:

```python
# Embedding Configuration
embedding_model = "text-embedding-3-small"
embedding_dimensions = 1536

# Chunking Configuration
chunk_size = 500  # Target size (min: 400, max: 600)
chunk_overlap = 50  # Overlap between chunks

# Qdrant Configuration
qdrant_url = "https://your-cluster.qdrant.io"
qdrant_collection_name = "textbook_chunks"
```

## Environment Variables

Required environment variables (in `.env`):

```bash
# OpenAI API Key
OPENAI_API_KEY=sk-...

# Qdrant Configuration
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION_NAME=textbook_chunks
```

## Data Flow

```
MDX Files
   ↓
[Parser]
   ↓
ParsedDocuments (metadata + sections)
   ↓
[Chunker]
   ↓
ContentChunks (400-600 tokens each)
   ↓
[Embedding Generator]
   ↓
Embeddings (1536-dim vectors)
   ↓
[Qdrant Client]
   ↓
Qdrant Vector Database
```

## Chunk Metadata

Each chunk stored in Qdrant includes:

```json
{
  "text": "The actual chunk text content...",
  "chapter": "Part 1: Foundations - Chapter 1",
  "title": "Introduction to Physical AI",
  "section": "What is Physical AI?",
  "heading_path": "Introduction > What is Physical AI? > Key Characteristics",
  "url": "/docs/part-01-foundations/ch01-intro-physical-ai",
  "description": "Explore the evolution from digital AI...",
  "keywords": ["physical AI", "embodied AI", "robotics"],
  "source_file": "E:\\path\\to\\ch01-intro-physical-ai.mdx",
  "chunk_index": 0,
  "token_count": 487,
  "line_start": 23,
  "line_end": 65,
  "created_at": "2025-12-30T10:30:00Z"
}
```

## Performance

Typical ingestion performance (based on textbook content):

- **Parsing**: ~100 files/second
- **Chunking**: ~500 sections/second
- **Embedding**: ~100 chunks/second (batch API)
- **Storage**: ~1000 points/second (batch upload)

**Example**: 50 chapters, ~2000 chunks, ~30 minutes total

## Error Handling

The pipeline includes comprehensive error handling:

1. **File errors**: Logs and skips files that fail to parse
2. **Rate limits**: Automatic retry with exponential backoff
3. **API errors**: Retry up to 3 times before failing
4. **Validation**: Post-ingestion checks for data integrity

## Caching

Embedding cache location: `backend/.cache/embeddings/`

Cache benefits:
- **Avoid recomputation**: Cached embeddings are reused
- **Cost savings**: Reduces OpenAI API calls
- **Speed**: Instant retrieval for cached texts

Clear cache:
```python
from src.services.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()
generator.clear_cache()
```

## Testing

Run ingestion tests:

```bash
# Unit tests
pytest backend/tests/test_parser.py
pytest backend/tests/test_chunker.py
pytest backend/tests/test_embeddings.py

# Integration test
pytest backend/tests/test_ingestion_pipeline.py
```

## Troubleshooting

### Issue: "Rate limit exceeded"
**Solution**: Reduce `--batch-size` or wait and retry

### Issue: "Collection already exists"
**Solution**: Use `--rebuild` flag to recreate collection

### Issue: "No documents found"
**Solution**: Check input directory path and file extensions

### Issue: "Token count exceeds limit"
**Solution**: Reduce `max_chunk_size` in chunker configuration

## Best Practices

1. **Initial ingestion**: Use `--rebuild` flag
2. **Incremental updates**: Run without `--rebuild` (appends new content)
3. **Validation**: Always use `--validate` for production
4. **Monitoring**: Check logs for errors and statistics
5. **Cache management**: Clear cache when changing chunking strategy

## Next Steps

After ingestion, the content is ready for RAG retrieval:

1. Query embedding generation
2. Vector similarity search in Qdrant
3. Reranking with cross-encoder
4. Context injection into LLM prompts

See `backend/src/services/retrieval.py` for retrieval implementation.
