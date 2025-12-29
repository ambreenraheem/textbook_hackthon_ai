"""
Content ingestion pipeline orchestrator.

Orchestrates the full pipeline: parse → chunk → embed → store
Provides CLI interface for running the ingestion process.
"""
import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from src.config.settings import get_settings
from src.ingestion.parser import MarkdownParser
from src.ingestion.chunker import SemanticChunker, ContentChunk
from src.services.embeddings import EmbeddingGenerator
from src.utils.app_logging import get_logger, setup_logging

logger = get_logger(__name__)


class IngestionPipeline:
    """
    Content ingestion pipeline orchestrator.

    Coordinates parsing, chunking, embedding, and storage of textbook content.
    """

    def __init__(
        self,
        input_dir: Path,
        rebuild: bool = False,
        batch_size: int = 100,
        use_cache: bool = True
    ):
        """
        Initialize the ingestion pipeline.

        Args:
            input_dir: Directory containing markdown files
            rebuild: Whether to rebuild collection from scratch
            batch_size: Batch size for embedding generation
            use_cache: Whether to use embedding cache
        """
        self.input_dir = input_dir
        self.rebuild = rebuild
        self.batch_size = batch_size

        # Initialize components
        self.settings = get_settings()
        self.parser = MarkdownParser()
        self.chunker = SemanticChunker(
            min_chunk_size=self.settings.chunk_size - 100,  # 400
            max_chunk_size=self.settings.chunk_size + 100,  # 600
            overlap_size=self.settings.chunk_overlap
        )
        self.embedding_generator = EmbeddingGenerator(
            batch_size=batch_size,
            use_cache=use_cache
        )

        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key
        )

        self.logger = get_logger(__name__)

    def run(self) -> dict:
        """
        Run the complete ingestion pipeline.

        Returns:
            Dictionary with pipeline statistics

        Raises:
            Exception: If pipeline fails at any stage
        """
        start_time = time.time()

        self.logger.info("=" * 80)
        self.logger.info("STARTING CONTENT INGESTION PIPELINE")
        self.logger.info("=" * 80)

        stats = {
            'files_parsed': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'points_stored': 0,
            'errors': 0,
            'duration_seconds': 0
        }

        try:
            # Step 1: Parse markdown files
            self.logger.info(f"\n[STEP 1/4] Parsing markdown files from {self.input_dir}")
            documents = self._parse_documents()
            stats['files_parsed'] = len(documents)
            self.logger.info(f"✓ Parsed {len(documents)} documents")

            if not documents:
                self.logger.warning("No documents found to process!")
                return stats

            # Step 2: Chunk documents
            self.logger.info(f"\n[STEP 2/4] Chunking documents into semantic chunks")
            chunks = self._chunk_documents(documents)
            stats['chunks_created'] = len(chunks)
            self.logger.info(f"✓ Created {len(chunks)} chunks")

            if not chunks:
                self.logger.warning("No chunks created!")
                return stats

            # Step 3: Generate embeddings
            self.logger.info(f"\n[STEP 3/4] Generating embeddings")
            embeddings = self._generate_embeddings(chunks)
            stats['embeddings_generated'] = len(embeddings)
            self.logger.info(f"✓ Generated {len(embeddings)} embeddings")

            # Step 4: Store in Qdrant
            self.logger.info(f"\n[STEP 4/4] Storing in Qdrant")

            # Rebuild collection if requested
            if self.rebuild:
                self._rebuild_collection()

            stored_count = self._store_in_qdrant(chunks, embeddings)
            stats['points_stored'] = stored_count
            self.logger.info(f"✓ Stored {stored_count} points in Qdrant")

            # Calculate duration
            duration = time.time() - start_time
            stats['duration_seconds'] = duration

            # Print summary
            self._print_summary(stats)

            return stats

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            stats['errors'] += 1
            raise

    def _parse_documents(self) -> List:
        """
        Parse all markdown documents in input directory.

        Returns:
            List of ParsedDocument objects
        """
        try:
            documents = self.parser.parse_directory(self.input_dir)
            return documents
        except Exception as e:
            self.logger.error(f"Failed to parse documents: {e}")
            raise

    def _chunk_documents(self, documents: List) -> List[ContentChunk]:
        """
        Chunk all documents into semantic chunks.

        Args:
            documents: List of ParsedDocument objects

        Returns:
            List of ContentChunk objects
        """
        try:
            chunks = self.chunker.chunk_documents(documents)
            return chunks
        except Exception as e:
            self.logger.error(f"Failed to chunk documents: {e}")
            raise

    def _generate_embeddings(self, chunks: List[ContentChunk]) -> List[List[float]]:
        """
        Generate embeddings for all chunks.

        Args:
            chunks: List of ContentChunk objects

        Returns:
            List of embedding vectors
        """
        try:
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_generator.generate_embeddings_batch(
                texts,
                show_progress=True
            )
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise

    def _store_in_qdrant(
        self,
        chunks: List[ContentChunk],
        embeddings: List[List[float]]
    ) -> int:
        """
        Store chunks and embeddings in Qdrant.

        Args:
            chunks: List of ContentChunk objects
            embeddings: List of embedding vectors

        Returns:
            Number of points stored
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunk count ({len(chunks)}) doesn't match embedding count ({len(embeddings)})"
            )

        try:
            # Create points for batch upload
            points = []

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Generate unique ID
                point_id = str(uuid.uuid4())

                # Create point
                point = PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        'text': chunk.text,
                        'chapter': chunk.metadata.get('chapter', ''),
                        'title': chunk.metadata.get('title', ''),
                        'section': chunk.metadata.get('section', ''),
                        'heading_path': chunk.metadata.get('heading_path', ''),
                        'url': chunk.metadata.get('url', ''),
                        'description': chunk.metadata.get('description', ''),
                        'keywords': chunk.metadata.get('keywords', []),
                        'source_file': chunk.source_file,
                        'chunk_index': chunk.metadata.get('chunk_index', 0),
                        'token_count': chunk.token_count,
                        'line_start': chunk.line_start,
                        'line_end': chunk.line_end,
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                points.append(point)

            # Upload in batches
            batch_size = 100
            total_stored = 0

            for batch_start in range(0, len(points), batch_size):
                batch_end = min(batch_start + batch_size, len(points))
                batch = points[batch_start:batch_end]

                self.logger.info(
                    f"Uploading batch {batch_start // batch_size + 1}/"
                    f"{(len(points) + batch_size - 1) // batch_size} "
                    f"({len(batch)} points)"
                )

                self.qdrant_client.upsert(
                    collection_name=self.settings.qdrant_collection_name,
                    points=batch
                )

                total_stored += len(batch)

            return total_stored

        except Exception as e:
            self.logger.error(f"Failed to store in Qdrant: {e}")
            raise

    def _rebuild_collection(self):
        """Rebuild Qdrant collection from scratch."""
        self.logger.info("Rebuilding collection...")

        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.settings.qdrant_collection_name in collection_names:
                self.logger.info(
                    f"Deleting existing collection '{self.settings.qdrant_collection_name}'"
                )
                self.qdrant_client.delete_collection(
                    collection_name=self.settings.qdrant_collection_name
                )

            # Recreate collection
            from qdrant_client.models import Distance, VectorParams

            self.logger.info(
                f"Creating collection '{self.settings.qdrant_collection_name}'"
            )
            self.qdrant_client.create_collection(
                collection_name=self.settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=self.settings.embedding_dimensions,
                    distance=Distance.COSINE
                )
            )

            self.logger.info("✓ Collection rebuilt successfully")

        except Exception as e:
            self.logger.error(f"Failed to rebuild collection: {e}")
            raise

    def _print_summary(self, stats: dict):
        """
        Print pipeline summary statistics.

        Args:
            stats: Pipeline statistics dictionary
        """
        self.logger.info("\n" + "=" * 80)
        self.logger.info("INGESTION PIPELINE COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Files parsed:          {stats['files_parsed']}")
        self.logger.info(f"Chunks created:        {stats['chunks_created']}")
        self.logger.info(f"Embeddings generated:  {stats['embeddings_generated']}")
        self.logger.info(f"Points stored:         {stats['points_stored']}")
        self.logger.info(f"Errors:                {stats['errors']}")
        self.logger.info(f"Duration:              {stats['duration_seconds']:.2f}s")
        self.logger.info("=" * 80)

        if stats['chunks_created'] > 0:
            avg_time_per_chunk = stats['duration_seconds'] / stats['chunks_created']
            self.logger.info(f"Average time per chunk: {avg_time_per_chunk:.3f}s")

    def validate(self) -> bool:
        """
        Validate that content was ingested correctly.

        Returns:
            True if validation passes, False otherwise
        """
        self.logger.info("\nValidating ingestion...")

        try:
            # Get collection info
            collection_info = self.qdrant_client.get_collection(
                collection_name=self.settings.qdrant_collection_name
            )

            point_count = collection_info.points_count

            self.logger.info(f"Collection '{self.settings.qdrant_collection_name}' contains {point_count} points")

            if point_count == 0:
                self.logger.warning("Collection is empty!")
                return False

            # Try a sample search
            self.logger.info("Testing sample search...")

            sample_results = self.qdrant_client.search(
                collection_name=self.settings.qdrant_collection_name,
                query_vector=[0.0] * self.settings.embedding_dimensions,
                limit=1
            )

            if sample_results:
                self.logger.info("✓ Sample search successful")
                self.logger.info(f"  Sample result: {sample_results[0].payload.get('section', 'N/A')}")
            else:
                self.logger.warning("Sample search returned no results")
                return False

            self.logger.info("✓ Validation passed")
            return True

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            return False


def main():
    """CLI entry point for ingestion pipeline."""
    parser = argparse.ArgumentParser(
        description="Ingest textbook content into Qdrant vector database"
    )

    parser.add_argument(
        '--input',
        type=str,
        default='frontend/docs',
        help='Input directory containing markdown files (default: frontend/docs)'
    )

    parser.add_argument(
        '--rebuild',
        action='store_true',
        help='Rebuild collection from scratch (deletes existing data)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for embedding generation (default: 100)'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable embedding cache'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate ingestion after completion'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    # Resolve input path
    input_path = Path(args.input)
    if not input_path.is_absolute():
        # Make relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        input_path = project_root / input_path

    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_path}")
        sys.exit(1)

    # Create pipeline
    pipeline = IngestionPipeline(
        input_dir=input_path,
        rebuild=args.rebuild,
        batch_size=args.batch_size,
        use_cache=not args.no_cache
    )

    try:
        # Run pipeline
        stats = pipeline.run()

        # Validate if requested
        if args.validate:
            if not pipeline.validate():
                logger.error("Validation failed!")
                sys.exit(1)

        logger.info("\n✓ Ingestion completed successfully")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
