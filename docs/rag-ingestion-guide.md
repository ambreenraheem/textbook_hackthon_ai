# RAG Ingestion Guide

Quick guide for ingesting textbook content into Qdrant for RAG-powered chatbot.

## 🚀 Quick Start

### Prerequisites

- Backend environment configured (.env with OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY)
- Qdrant collection initialized

### Initialize Qdrant Collection

```bash
cd backend
python -m src.utils.qdrant_setup
```

### Run Full Ingestion

```bash
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
```

**Time**: ~10-15 minutes
**Cost**: ~$0.50 (OpenAI embeddings)
**Result**: ~500-1000 chunks indexed

## 📝 Command Options

```bash
python -m src.ingestion.pipeline --input <path> [--rebuild] [--chunk-size 500]
```

**Examples**:

```bash
# Ingest specific part
python -m src.ingestion.pipeline --input ../frontend/docs/part-01-foundations

# Ingest single chapter
python -m src.ingestion.pipeline --input ../frontend/docs/part-01-foundations/ch01-intro-physical-ai.mdx

# Rebuild from scratch (deletes existing data first)
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
```

## 🔍 How It Works

1. **Parser**: Extracts text and metadata from MDX files
2. **Chunker**: Splits into 400-600 token chunks (respects headings)
3. **Embeddings**: Generates 1536-dim vectors (OpenAI text-embedding-3-small)
4. **Upload**: Stores in Qdrant with metadata for hybrid search

## 🐛 Troubleshooting

**"OpenAI API key not found"**:
```bash
export OPENAI_API_KEY=sk-...
```

**"Qdrant connection failed"**:
```bash
# Test connection
python -c "from qdrant_client import QdrantClient; from src.config.settings import settings; client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY); print(client.get_collections())"
```

**"Collection not found"**:
```bash
python -m src.utils.qdrant_setup
```

## ✅ Verify Ingestion

### Check Qdrant Dashboard

1. Go to https://cloud.qdrant.io/
2. Select cluster → Collections → `textbook_chunks`
3. Verify point count (~500-1000)

### Test Chatbot

1. Start backend: `uvicorn src.api.main:app --reload`
2. Open frontend: http://localhost:3000
3. Ask chatbot: "What is Physical AI?"
4. Should return response with citations

## 🔄 Re-Ingestion

**After adding new chapters**:
```bash
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild
```

**Incremental update** (faster):
```bash
python -m src.ingestion.pipeline --input ../frontend/docs/part-10-projects
```

## 💰 Cost

- **Full textbook**: ~$0.50 (OpenAI embeddings)
- **Single chapter**: ~$0.0001 (negligible)
- **Qdrant storage**: Free tier (1GB) is sufficient

---

**Ready to ingest all content?**
```bash
cd backend
python -m src.utils.qdrant_setup  # Initialize collection
python -m src.ingestion.pipeline --input ../frontend/docs --rebuild  # Ingest all
```
