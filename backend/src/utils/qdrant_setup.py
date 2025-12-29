"""
Qdrant Cloud collection setup script.

Creates and configures the textbook_chunks collection for RAG retrieval.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType
from src.config.settings import get_settings


def create_collection():
    """
    Create and configure the Qdrant collection for textbook chunks.

    Creates:
    - Collection with 1536-dimensional vectors (text-embedding-3-small)
    - HNSW index for fast approximate nearest neighbor search
    - Payload indexes for metadata filtering (chapter, section, page)
    """
    settings = get_settings()

    print(f"Connecting to Qdrant at {settings.qdrant_url}...")
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    # Check if collection already exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if settings.qdrant_collection_name in collection_names:
        print(f"[WARNING] Collection '{settings.qdrant_collection_name}' already exists!")
        response = input("Do you want to recreate it? (yes/no): ").strip().lower()
        if response == "yes":
            print(f"Deleting existing collection '{settings.qdrant_collection_name}'...")
            client.delete_collection(collection_name=settings.qdrant_collection_name)
        else:
            print("Skipping collection creation.")
            return

    print(f"Creating collection '{settings.qdrant_collection_name}'...")
    client.create_collection(
        collection_name=settings.qdrant_collection_name,
        vectors_config=VectorParams(
            size=settings.embedding_dimensions,  # 1536 for text-embedding-3-small
            distance=Distance.COSINE  # Cosine similarity for semantic search
        )
    )
    print(f"[OK] Collection '{settings.qdrant_collection_name}' created successfully!")

    # Create payload indexes for fast metadata filtering
    print("Creating payload indexes...")

    # Index on 'chapter' field for filtering by chapter
    client.create_payload_index(
        collection_name=settings.qdrant_collection_name,
        field_name="chapter",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("[OK] Created index on 'chapter' field")

    # Index on 'section' field for filtering by section
    client.create_payload_index(
        collection_name=settings.qdrant_collection_name,
        field_name="section",
        field_schema=PayloadSchemaType.KEYWORD
    )
    print("[OK] Created index on 'section' field")

    # Index on 'page' field for filtering by page number
    client.create_payload_index(
        collection_name=settings.qdrant_collection_name,
        field_name="page",
        field_schema=PayloadSchemaType.INTEGER
    )
    print("[OK] Created index on 'page' field")

    # Verify collection info
    collection_info = client.get_collection(collection_name=settings.qdrant_collection_name)
    print(f"\n[COLLECTION INFO]")
    print(f"   Name: {settings.qdrant_collection_name}")
    print(f"   Vector size: {collection_info.config.params.vectors.size}")
    print(f"   Distance: {collection_info.config.params.vectors.distance}")
    print(f"   Points count: {collection_info.points_count}")

    print(f"\n[SUCCESS] Qdrant setup complete! Collection '{settings.qdrant_collection_name}' is ready for use.")


if __name__ == "__main__":
    try:
        create_collection()
    except Exception as e:
        print(f"\n[ERROR] Error setting up Qdrant: {e}")
        sys.exit(1)
