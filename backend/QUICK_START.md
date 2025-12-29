# RAG Pipeline Quick Start Guide

Get the RAG chatbot running in 5 minutes!

## Prerequisites

- Python 3.10+
- PostgreSQL database (Neon Serverless)
- Qdrant Cloud cluster
- OpenAI API key

## Step 1: Environment Setup

Create `.env` file in project root:

```bash
# Copy from .env.example
cp .env.example .env

# Edit with your credentials
OPENAI_API_KEY=sk-your-key-here
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-key
DATABASE_URL=postgresql://user:password@host/database
```

## Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 3: Initialize Database

```bash
python -c "from src.utils.database import create_tables; create_tables()"
```

Expected output:
```
INFO - Creating database tables
INFO - Database tables created successfully
```

## Step 4: Setup Qdrant

```bash
python src/utils/qdrant_setup.py
```

Expected output:
```
[OK] Collection 'textbook_chunks' created successfully!
[SUCCESS] Qdrant setup complete!
```

## Step 5: Run Tests (Optional)

```bash
python test_rag_pipeline.py
```

Expected output:
```
RESULTS: 11 passed, 0 failed
```

## Step 6: Start Server

```bash
python -m src.api.main
```

Server will start on http://localhost:8000

## Step 7: Test API

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Send Chat Message
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

You should see streaming response with tokens and citations!

## Step 8: View API Docs

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Common Issues

### Database Connection Error
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "from src.utils.database import check_database_connection; print(check_database_connection())"
```

### Qdrant Connection Error
```bash
# Verify credentials
echo $QDRANT_URL
echo $QDRANT_API_KEY

# Test connection
python src/utils/qdrant_setup.py
```

### OpenAI API Error
```bash
# Verify key
echo $OPENAI_API_KEY

# Test with simple embedding
python -c "from src.services.embeddings import EmbeddingGenerator; print(len(EmbeddingGenerator().generate_embedding('test')))"
```

## Next Steps

1. **Ingest Content**: Populate Qdrant with textbook chunks
   ```bash
   python src/ingestion/pipeline.py --input docs/ --output qdrant
   ```

2. **Test E2E**: Connect frontend to backend

3. **Monitor**: Check logs in `logs/` directory

4. **Optimize**: Tune retrieval parameters in `.env`

## Development Workflow

### Run with Auto-Reload
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### View Logs
```bash
tail -f logs/app.log
```

### Run Specific Test
```bash
pytest backend/tests/services/test_retrieval.py -v
```

## Production Deployment

### Using Docker
```bash
docker build -t textbook-backend .
docker run -p 8000:8000 --env-file .env textbook-backend
```

### Using systemd
```bash
# Create service file
sudo nano /etc/systemd/system/textbook-api.service

[Unit]
Description=Textbook Chatbot API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable textbook-api
sudo systemctl start textbook-api
```

## Support

- **Setup Issues**: See `SETUP_RAG.md`
- **Service Details**: See `src/services/README.md`
- **API Reference**: http://localhost:8000/docs
- **Test Suite**: `python test_rag_pipeline.py`

---

**Ready to go!** 🚀

Your RAG-powered chatbot backend is now running and ready to answer questions about Physical AI & Humanoid Robotics!
