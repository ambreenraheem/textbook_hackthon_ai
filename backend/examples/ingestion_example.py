"""
Example usage of the content ingestion pipeline.

This script demonstrates how to use the parser, chunker, embeddings,
and pipeline components programmatically.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.ingestion.parser import MarkdownParser
from src.ingestion.chunker import SemanticChunker
from src.services.embeddings import EmbeddingGenerator
from src.ingestion.pipeline import IngestionPipeline
from src.utils.app_logging import setup_logging


def example_parser():
    """Example: Parse a single markdown file."""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Parsing a Single File")
    print("=" * 60)

    parser = MarkdownParser()

    # Parse a file
    file_path = Path("frontend/docs/intro.md")
    if file_path.exists():
        doc = parser.parse_file(file_path)

        print(f"\nFile: {doc.file_path}")
        print(f"Title: {doc.title}")
        print(f"Chapter: {doc.chapter}")
        print(f"URL: {doc.url_path}")
        print(f"Sections: {len(doc.sections)}")

        # Show first section
        if doc.sections:
            section = doc.sections[0]
            print(f"\nFirst Section:")
            print(f"  Heading: {section.heading}")
            print(f"  Level: {section.level}")
            print(f"  Content length: {len(section.content)} chars")
            print(f"  Code blocks: {len(section.code_blocks)}")
    else:
        print(f"File not found: {file_path}")


def example_chunker():
    """Example: Chunk a parsed document."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Chunking a Document")
    print("=" * 60)

    parser = MarkdownParser()
    chunker = SemanticChunker(
        min_chunk_size=400,
        max_chunk_size=600,
        overlap_size=50
    )

    # Parse a file
    file_path = Path("frontend/docs/intro.md")
    if file_path.exists():
        doc = parser.parse_file(file_path)

        # Chunk it
        chunks = chunker.chunk_document(doc)

        print(f"\nCreated {len(chunks)} chunks")

        # Show statistics
        if chunks:
            token_counts = [c.token_count for c in chunks]
            print(f"Average tokens per chunk: {sum(token_counts) / len(token_counts):.0f}")
            print(f"Min tokens: {min(token_counts)}")
            print(f"Max tokens: {max(token_counts)}")

            # Show first chunk
            chunk = chunks[0]
            print(f"\nFirst Chunk:")
            print(f"  Text preview: {chunk.text[:100]}...")
            print(f"  Token count: {chunk.token_count}")
            print(f"  Chapter: {chunk.metadata['chapter']}")
            print(f"  Section: {chunk.metadata['section']}")
            print(f"  Heading path: {chunk.metadata['heading_path']}")
    else:
        print(f"File not found: {file_path}")


def example_embeddings():
    """Example: Generate embeddings for text."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Generating Embeddings")
    print("=" * 60)

    generator = EmbeddingGenerator(
        batch_size=10,
        use_cache=True
    )

    # Single embedding
    text = "Physical AI combines artificial intelligence with physical embodiment."
    embedding = generator.generate_embedding(text)

    print(f"\nGenerated embedding for text:")
    print(f"  Text: {text}")
    print(f"  Embedding dimension: {len(embedding)}")
    print(f"  First 5 values: {embedding[:5]}")

    # Batch embeddings
    texts = [
        "Humanoid robots are designed to mimic human form and function.",
        "ROS 2 is the Robot Operating System for modern robotics.",
        "Computer vision enables robots to perceive their environment."
    ]

    embeddings = generator.generate_embeddings_batch(texts, show_progress=True)

    print(f"\nGenerated {len(embeddings)} embeddings in batch")
    print(f"Each embedding has {len(embeddings[0])} dimensions")


def example_pipeline():
    """Example: Run the complete pipeline."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Complete Ingestion Pipeline")
    print("=" * 60)

    # Setup logging
    setup_logging()

    # Create pipeline
    pipeline = IngestionPipeline(
        input_dir=Path("frontend/docs"),
        rebuild=False,  # Don't rebuild in example
        batch_size=50,
        use_cache=True
    )

    print("\nNote: This example shows the pipeline structure.")
    print("To actually run ingestion, use: python backend/ingest_content.py")
    print("\nPipeline configuration:")
    print(f"  Input directory: {pipeline.input_dir}")
    print(f"  Rebuild: {pipeline.rebuild}")
    print(f"  Batch size: {pipeline.batch_size}")
    print(f"  Collection: {pipeline.settings.qdrant_collection_name}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("CONTENT INGESTION PIPELINE - EXAMPLES")
    print("=" * 60)

    try:
        example_parser()
        example_chunker()
        example_embeddings()
        example_pipeline()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
