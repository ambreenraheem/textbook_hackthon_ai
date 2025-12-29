# Content Ingestion System

Complete documentation for the textbook content ingestion pipeline.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Components](#components)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

## Overview

The content ingestion pipeline transforms textbook MDX files into searchable vector embeddings stored in Qdrant for RAG-based retrieval.

### Pipeline Stages

```
MDX Files → Parser → Chunker → Embeddings → Qdrant
```

1. **Parse**: Extract metadata and sections from MDX files
2. **Chunk**: Split content into 400-600 token semantic chunks
3. **Embed**: Generate 1536-dim vectors with OpenAI text-embedding-3-small
4. **Store**: Upload chunks and embeddings to Qdrant

### Key Features

- **Semantic chunking**: Respects heading and paragraph boundaries
- **Batch processing**: Efficient API usage with batching
- **Caching**: Avoids recomputing embeddings
- **Progress tracking**: Real-time logs and statistics
- **Validation**: Post-ingestion data integrity checks

## Quick Start

### Prerequisites

1. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure environment** (`.env`):
```bash
OPENAI_API_KEY=sk-...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION_NAME=textbook_chunks
```

3. **Setup Qdrant collection**:
```bash
python backend/src/utils/qdrant_setup.py
```

### Run Ingestion

```bash
# Basic ingestion (appends to existing collection)
python backend/ingest_content.py

# Rebuild from scratch
python backend/ingest_content.py --rebuild --validate

# Custom input directory
python backend/ingest_content.py --input frontend/docs

# All options
python backend/ingest_content.py \
  --rebuild \
  --validate \
  --batch-size 100 \
  --input frontend/docs
```

### Expected Output

```
================================================================================
STARTING CONTENT INGESTION PIPELINE
================================================================================

[STEP 1/4] Parsing markdown files from frontend/docs
✓ Parsed 45 documents

[STEP 2/4] Chunking documents into semantic chunks
✓ Created 1,847 chunks

[STEP 3/4] Generating embeddings
Cache stats - Hits: 0, Misses: 1847
Processing batch 1/19 (100 texts)
Processing batch 2/19 (100 texts)
...
✓ Generated 1,847 embeddings

[STEP 4/4] Storing in Qdrant
Uploading batch 1/19 (100 points)
Uploading batch 2/19 (100 points)
...
✓ Stored 1,847 points in Qdrant

================================================================================
INGESTION PIPELINE COMPLETE
================================================================================
Files parsed:          45
Chunks created:        1,847
Embeddings generated:  1,847
Points stored:         1,847
Errors:                0
Duration:              892.34s
================================================================================
Average time per chunk: 0.483s

Validating ingestion...
Collection 'textbook_chunks' contains 1847 points
Testing sample search...
✓ Sample search successful
  Sample result: Introduction to Physical AI
✓ Validation passed

✓ Ingestion completed successfully
```

## Architecture

### Component Overview

```
src/
├── ingestion/
│   ├── parser.py       # MDX/Markdown parsing
│   ├── chunker.py      # Semantic chunking
│   ├── pipeline.py     # Pipeline orchestration
│   └── README.md       # Component documentation
├── services/
│   └── embeddings.py   # OpenAI embedding generation
├── config/
│   └── settings.py     # Configuration management
└── utils/
    ├── app_logging.py  # Structured logging
    └── qdrant_setup.py # Qdrant initialization

ingest_content.py       # CLI entry point
```

### Data Flow

```mermaid
graph LR
    A[MDX Files] --> B[MarkdownParser]
    B --> C[ParsedDocument]
    C --> D[SemanticChunker]
    D --> E[ContentChunk]
    E --> F[EmbeddingGenerator]
    F --> G[Embeddings]
    E --> H[Qdrant]
    G --> H
```

## Components

### 1. MarkdownParser

**Purpose**: Extract structured content from MDX files

**Input**:
- Path to `.md` or `.mdx` file

**Output**:
- `ParsedDocument` with metadata, sections, and code blocks

**Key Methods**:
- `parse_file(path)`: Parse single file
- `parse_directory(dir, pattern)`: Parse all files in directory
- `extract_plain_text(content)`: Strip markdown formatting

**Example**:
```python
from src.ingestion.parser import MarkdownParser

parser = MarkdownParser()
doc = parser.parse_file(Path("docs/ch01-intro.mdx"))

print(f"Title: {doc.title}")
print(f"Sections: {len(doc.sections)}")
```

### 2. SemanticChunker

**Purpose**: Split documents into optimal-sized chunks

**Configuration**:
- `min_chunk_size`: 400 tokens (default)
- `max_chunk_size`: 600 tokens (default)
- `overlap_size`: 50 tokens (default)

**Output**:
- `ContentChunk` with text, metadata, and token count

**Key Methods**:
- `chunk_document(doc)`: Chunk single document
- `chunk_documents(docs)`: Chunk multiple documents
- `count_tokens(text)`: Count tokens in text

**Example**:
```python
from src.ingestion.chunker import SemanticChunker

chunker = SemanticChunker()
chunks = chunker.chunk_document(parsed_doc)

print(f"Created {len(chunks)} chunks")
print(f"Avg tokens: {sum(c.token_count for c in chunks) / len(chunks):.0f}")
```

### 3. EmbeddingGenerator

**Purpose**: Generate vector embeddings with OpenAI API

**Configuration**:
- `model`: text-embedding-3-small (1536 dimensions)
- `batch_size`: 100 texts per API call
- `max_retries`: 3 retry attempts
- `use_cache`: Enable file-based caching

**Output**:
- List of 1536-dimensional float vectors

**Key Methods**:
- `generate_embedding(text)`: Single embedding
- `generate_embeddings_batch(texts)`: Batch embeddings
- `clear_cache()`: Clear embedding cache

**Example**:
```python
from src.services.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(batch_size=100, use_cache=True)
embeddings = generator.generate_embeddings_batch(texts, show_progress=True)
```

### 4. IngestionPipeline

**Purpose**: Orchestrate complete ingestion workflow

**Configuration**:
- `input_dir`: Directory containing MDX files
- `rebuild`: Recreate Qdrant collection
- `batch_size`: Embedding batch size
- `use_cache`: Enable embedding cache

**Output**:
- Statistics dictionary with counts and duration

**Key Methods**:
- `run()`: Execute full pipeline
- `validate()`: Verify successful ingestion

**Example**:
```python
from src.ingestion.pipeline import IngestionPipeline

pipeline = IngestionPipeline(
    input_dir=Path("frontend/docs"),
    rebuild=True,
    batch_size=100
)

stats = pipeline.run()
pipeline.validate()
```

## Configuration

### Environment Variables

Required variables in `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...                  # OpenAI API key

# Qdrant Configuration
QDRANT_URL=https://xyz.qdrant.io       # Qdrant cluster URL
QDRANT_API_KEY=abc123...               # Qdrant API key
QDRANT_COLLECTION_NAME=textbook_chunks # Collection name

# Embedding Configuration (optional)
EMBEDDING_MODEL=text-embedding-3-small # OpenAI model
EMBEDDING_DIMENSIONS=1536              # Embedding size

# Chunking Configuration (optional)
CHUNK_SIZE=500                         # Target chunk size
CHUNK_OVERLAP=50                       # Overlap between chunks
```

### Settings (settings.py)

```python
from src.config.settings import get_settings

settings = get_settings()

# Access configuration
print(settings.embedding_model)        # text-embedding-3-small
print(settings.embedding_dimensions)   # 1536
print(settings.chunk_size)             # 500
print(settings.chunk_overlap)          # 50
```

## Usage

### CLI Interface

```bash
# View help
python backend/ingest_content.py --help

# Basic ingestion
python backend/ingest_content.py

# Rebuild collection
python backend/ingest_content.py --rebuild

# Validate after ingestion
python backend/ingest_content.py --validate

# Custom input directory
python backend/ingest_content.py --input path/to/docs

# Disable cache
python backend/ingest_content.py --no-cache

# Custom batch size
python backend/ingest_content.py --batch-size 50

# Combined options
python backend/ingest_content.py --rebuild --validate --batch-size 100
```

### Programmatic Usage

```python
from pathlib import Path
from src.ingestion.pipeline import IngestionPipeline
from src.utils.app_logging import setup_logging

# Setup logging
setup_logging()

# Create and run pipeline
pipeline = IngestionPipeline(
    input_dir=Path("frontend/docs"),
    rebuild=True,
    batch_size=100,
    use_cache=True
)

# Run ingestion
stats = pipeline.run()

# Validate
if pipeline.validate():
    print("Ingestion successful!")
else:
    print("Validation failed!")
```

### Examples

See `backend/examples/ingestion_example.py` for detailed examples:

```bash
python backend/examples/ingestion_example.py
```

## Monitoring

### Logs

Logs are written to stdout with structured format:

**Development**:
```
2025-12-30 10:30:00 - ingestion.pipeline - INFO - [abc-123] - Parsing markdown files
```

**Production** (JSON):
```json
{
  "timestamp": "2025-12-30T10:30:00Z",
  "level": "INFO",
  "logger": "ingestion.pipeline",
  "correlation_id": "abc-123",
  "message": "Parsing markdown files"
}
```

### Progress Tracking

The pipeline logs progress at each stage:

1. **Parsing**: Files parsed count
2. **Chunking**: Chunks created, token statistics
3. **Embedding**: Batch progress, cache hits/misses
4. **Storage**: Batch upload progress

### Statistics

Final statistics include:

- Files parsed
- Chunks created
- Embeddings generated
- Points stored
- Errors encountered
- Total duration
- Average time per chunk

## Troubleshooting

### Common Issues

#### Issue: Rate Limit Exceeded

**Error**:
```
openai.RateLimitError: Rate limit exceeded
```

**Solutions**:
1. Reduce batch size: `--batch-size 50`
2. Wait and retry (automatic backoff)
3. Check OpenAI quota and usage

#### Issue: Collection Already Exists

**Error**:
```
Collection 'textbook_chunks' already exists
```

**Solutions**:
1. Use `--rebuild` to recreate: `python ingest_content.py --rebuild`
2. Or continue appending (default behavior)

#### Issue: No Documents Found

**Error**:
```
No documents found to process!
```

**Solutions**:
1. Check input directory path
2. Verify `.md` or `.mdx` files exist
3. Use absolute path or relative to project root

#### Issue: Token Count Exceeds Limit

**Error**:
```
This model's maximum context length is 8192 tokens
```

**Solutions**:
1. Reduce `max_chunk_size` in chunker
2. Check for extremely long sections
3. Verify chunking configuration

#### Issue: Qdrant Connection Failed

**Error**:
```
Failed to connect to Qdrant
```

**Solutions**:
1. Verify `QDRANT_URL` in `.env`
2. Check `QDRANT_API_KEY` is correct
3. Ensure Qdrant cluster is running
4. Test connection: `python src/utils/qdrant_setup.py`

### Validation Failures

If validation fails after ingestion:

1. **Check collection**: Verify points were stored
```python
from qdrant_client import QdrantClient
from src.config.settings import get_settings

settings = get_settings()
client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
info = client.get_collection(settings.qdrant_collection_name)
print(f"Points: {info.points_count}")
```

2. **Test search**: Verify embeddings work
```python
results = client.search(
    collection_name=settings.qdrant_collection_name,
    query_vector=[0.0] * 1536,
    limit=5
)
print(f"Results: {len(results)}")
```

3. **Check logs**: Review error messages
4. **Rebuild**: Try `--rebuild` flag

### Performance Issues

If ingestion is slow:

1. **Enable caching**: Remove `--no-cache` flag
2. **Increase batch size**: `--batch-size 200`
3. **Check network**: Verify connection speed
4. **Monitor API usage**: Check OpenAI dashboard

### Cache Management

Clear cache if needed:

```python
from src.services.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator()
generator.clear_cache()
```

Or manually:
```bash
rm -rf backend/.cache/embeddings
```

## Best Practices

1. **Initial ingestion**: Use `--rebuild --validate`
2. **Incremental updates**: Run without `--rebuild`
3. **Production**: Enable caching for speed
4. **Development**: Use `--no-cache` to force regeneration
5. **Monitoring**: Always check validation results
6. **Logging**: Review logs for errors and warnings
7. **Testing**: Run tests before production ingestion

## Next Steps

After successful ingestion:

1. **Test retrieval**: Query the vector database
2. **Implement RAG**: Build retrieval service
3. **Add reranking**: Improve result quality
4. **Monitor usage**: Track searches and performance

See `backend/src/services/retrieval.py` for retrieval implementation.
