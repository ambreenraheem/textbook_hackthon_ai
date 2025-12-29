"""
Embedding generation service using OpenAI text-embedding-3-small.

Provides batch processing, rate limiting, and caching for efficient
embedding generation.
"""
import time
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import asyncio
from openai import OpenAI, RateLimitError, APIError

from src.config.settings import get_settings
from src.utils.app_logging import get_logger

logger = get_logger(__name__)


class EmbeddingCache:
    """
    Simple file-based cache for embeddings.

    Caches embeddings to avoid recomputing them for the same text.
    Uses MD5 hash of text as cache key.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize embedding cache.

        Args:
            cache_dir: Directory for cache files (default: .cache/embeddings)
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent.parent / ".cache" / "embeddings"

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)

    def _get_cache_key(self, text: str, model: str) -> str:
        """
        Generate cache key from text and model.

        Args:
            text: Input text
            model: Model name

        Returns:
            MD5 hash as cache key
        """
        content = f"{model}:{text}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, text: str, model: str) -> Optional[List[float]]:
        """
        Get embedding from cache.

        Args:
            text: Input text
            model: Model name

        Returns:
            Cached embedding vector or None if not found
        """
        cache_key = self._get_cache_key(text, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return data['embedding']
            except Exception as e:
                self.logger.warning(f"Failed to read cache file {cache_file}: {e}")
                return None

        return None

    def set(self, text: str, model: str, embedding: List[float]):
        """
        Store embedding in cache.

        Args:
            text: Input text
            model: Model name
            embedding: Embedding vector
        """
        cache_key = self._get_cache_key(text, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'text': text[:100],  # Store snippet for debugging
                    'model': model,
                    'embedding': embedding
                }, f)
        except Exception as e:
            self.logger.warning(f"Failed to write cache file {cache_file}: {e}")

    def clear(self):
        """Clear all cached embeddings."""
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except Exception as e:
                self.logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        self.logger.info("Embedding cache cleared")


class EmbeddingGenerator:
    """
    Generate embeddings using OpenAI text-embedding-3-small.

    Features:
    - Batch processing for efficiency
    - Rate limiting with exponential backoff
    - Caching to avoid re-computation
    - Progress tracking
    """

    def __init__(
        self,
        batch_size: int = 100,
        max_retries: int = 3,
        use_cache: bool = True,
        cache_dir: Optional[Path] = None
    ):
        """
        Initialize embedding generator.

        Args:
            batch_size: Number of texts to process in one API call
            max_retries: Maximum retry attempts for rate limits
            use_cache: Whether to use embedding cache
            cache_dir: Directory for cache files
        """
        settings = get_settings()

        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.use_cache = use_cache

        if use_cache:
            self.cache = EmbeddingCache(cache_dir)
        else:
            self.cache = None

        self.logger = get_logger(__name__)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            Embedding vector (1536 dimensions)

        Raises:
            APIError: If API call fails after retries
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(text, self.model)
            if cached is not None:
                return cached

        # Generate embedding
        embedding = self._generate_with_retry([text])[0]

        # Cache result
        if self.cache:
            self.cache.set(text, self.model, embedding)

        return embedding

    def generate_embeddings_batch(
        self,
        texts: List[str],
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with batching.

        Args:
            texts: List of input texts
            show_progress: Whether to log progress

        Returns:
            List of embedding vectors

        Raises:
            APIError: If API call fails after retries
        """
        embeddings = []
        cache_hits = 0
        cache_misses = 0

        # Check cache for all texts
        uncached_indices = []
        uncached_texts = []

        for i, text in enumerate(texts):
            if self.cache:
                cached = self.cache.get(text, self.model)
                if cached is not None:
                    embeddings.append((i, cached))
                    cache_hits += 1
                    continue

            uncached_indices.append(i)
            uncached_texts.append(text)
            cache_misses += 1

        if show_progress and self.cache:
            self.logger.info(
                f"Cache stats - Hits: {cache_hits}, Misses: {cache_misses}"
            )

        # Generate embeddings for uncached texts in batches
        if uncached_texts:
            for batch_start in range(0, len(uncached_texts), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(uncached_texts))
                batch_texts = uncached_texts[batch_start:batch_end]

                if show_progress:
                    self.logger.info(
                        f"Processing batch {batch_start // self.batch_size + 1}/"
                        f"{(len(uncached_texts) + self.batch_size - 1) // self.batch_size} "
                        f"({len(batch_texts)} texts)"
                    )

                # Generate batch
                batch_embeddings = self._generate_with_retry(batch_texts)

                # Store in results and cache
                for i, embedding in enumerate(batch_embeddings):
                    original_index = uncached_indices[batch_start + i]
                    embeddings.append((original_index, embedding))

                    # Cache result
                    if self.cache:
                        self.cache.set(batch_texts[i], self.model, embedding)

        # Sort by original index
        embeddings.sort(key=lambda x: x[0])

        # Return just the embeddings
        return [emb for _, emb in embeddings]

    def _generate_with_retry(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings with retry logic for rate limits.

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors

        Raises:
            APIError: If API call fails after max retries
        """
        for attempt in range(self.max_retries):
            try:
                # Call OpenAI API
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts
                )

                # Extract embeddings
                embeddings = [item.embedding for item in response.data]

                return embeddings

            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"Rate limit hit, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries reached for rate limit: {e}")
                    raise

            except APIError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"API error, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries}): {e}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries reached for API error: {e}")
                    raise

            except Exception as e:
                self.logger.error(f"Unexpected error generating embeddings: {e}")
                raise

        raise APIError("Failed to generate embeddings after max retries")

    def clear_cache(self):
        """Clear the embedding cache."""
        if self.cache:
            self.cache.clear()
        else:
            self.logger.warning("Cache is disabled, nothing to clear")

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by the model.

        Returns:
            Embedding dimension (1536 for text-embedding-3-small)
        """
        settings = get_settings()
        return settings.embedding_dimensions
