"""
Hybrid search retrieval service combining vector similarity and BM25 keyword search.

Implements:
- Vector similarity search using Qdrant
- BM25 keyword search for exact term matching
- Reciprocal Rank Fusion (RRF) for combining results
- Metadata filtering (chapter, section)
"""
import re
from typing import List, Dict, Optional, Tuple
from uuid import UUID
import numpy as np
from collections import defaultdict

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchParams

from src.config.settings import get_settings
from src.services.embeddings import EmbeddingGenerator
from src.utils.app_logging import get_logger

logger = get_logger(__name__)


class RetrievedChunk:
    """
    Represents a retrieved chunk with metadata and relevance score.
    """

    def __init__(
        self,
        chunk_id: UUID,
        content: str,
        score: float,
        chapter: str,
        section: str,
        page: Optional[int],
        url: str,
        metadata: Optional[Dict] = None
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.score = score
        self.chapter = chapter
        self.section = section
        self.page = page
        self.url = url
        self.metadata = metadata or {}

    def __repr__(self):
        return f"<RetrievedChunk(id={self.chunk_id}, score={self.score:.4f}, chapter={self.chapter})>"

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "chunk_id": str(self.chunk_id),
            "content": self.content,
            "score": self.score,
            "chapter": self.chapter,
            "section": self.section,
            "page": self.page,
            "url": self.url,
            "metadata": self.metadata
        }


class BM25:
    """
    Simple BM25 implementation for keyword search.

    BM25 is a probabilistic ranking function that scores documents based on
    term frequency and inverse document frequency.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 scorer.

        Args:
            k1: Term frequency saturation parameter (default: 1.5)
            b: Length normalization parameter (default: 0.75)
        """
        self.k1 = k1
        self.b = b
        self.logger = get_logger(__name__)

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into lowercase words.

        Args:
            text: Input text

        Returns:
            List of lowercase tokens
        """
        # Simple tokenization: lowercase, remove punctuation, split on whitespace
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return tokens

    def score_documents(
        self,
        query: str,
        documents: List[Tuple[UUID, str]]
    ) -> List[Tuple[UUID, float]]:
        """
        Score documents using BM25 algorithm.

        Args:
            query: Search query
            documents: List of (chunk_id, content) tuples

        Returns:
            List of (chunk_id, bm25_score) tuples, sorted by score descending
        """
        if not documents:
            return []

        # Tokenize query
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return [(doc_id, 0.0) for doc_id, _ in documents]

        # Tokenize documents
        doc_tokens = [(doc_id, self.tokenize(content)) for doc_id, content in documents]

        # Calculate document lengths and average length
        doc_lengths = {doc_id: len(tokens) for doc_id, tokens in doc_tokens}
        avg_doc_length = sum(doc_lengths.values()) / len(doc_lengths)

        # Calculate document frequency (DF) for each query term
        df = defaultdict(int)
        for _, tokens in doc_tokens:
            unique_tokens = set(tokens)
            for token in query_tokens:
                if token in unique_tokens:
                    df[token] += 1

        # Calculate IDF for each query term
        num_docs = len(documents)
        idf = {}
        for token in query_tokens:
            # IDF = log((N - df + 0.5) / (df + 0.5) + 1)
            idf[token] = np.log((num_docs - df[token] + 0.5) / (df[token] + 0.5) + 1.0)

        # Calculate BM25 score for each document
        scores = []
        for doc_id, tokens in doc_tokens:
            score = 0.0
            doc_length = doc_lengths[doc_id]

            # Count term frequencies in document
            tf = defaultdict(int)
            for token in tokens:
                tf[token] += 1

            # Sum BM25 scores for each query term
            for query_token in query_tokens:
                if query_token in tf:
                    # BM25 formula
                    term_freq = tf[query_token]
                    numerator = idf[query_token] * term_freq * (self.k1 + 1)
                    denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_length / avg_doc_length))
                    score += numerator / denominator

            scores.append((doc_id, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores


class HybridRetriever:
    """
    Hybrid retrieval combining vector similarity and BM25 keyword search.

    Uses Reciprocal Rank Fusion (RRF) to combine results from both methods.
    """

    def __init__(
        self,
        qdrant_client: Optional[QdrantClient] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None
    ):
        """
        Initialize hybrid retriever.

        Args:
            qdrant_client: Qdrant client (creates new if None)
            embedding_generator: Embedding generator (creates new if None)
        """
        settings = get_settings()

        # Initialize Qdrant client
        if qdrant_client is None:
            self.qdrant_client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key
            )
        else:
            self.qdrant_client = qdrant_client

        # Initialize embedding generator
        if embedding_generator is None:
            self.embedding_generator = EmbeddingGenerator(use_cache=False)
        else:
            self.embedding_generator = embedding_generator

        self.collection_name = settings.qdrant_collection_name
        self.bm25 = BM25()
        self.logger = get_logger(__name__)

    def vector_search(
        self,
        query: str,
        top_k: int = 20,
        chapter_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        min_score: float = 0.0
    ) -> List[RetrievedChunk]:
        """
        Perform vector similarity search.

        Args:
            query: Search query
            top_k: Number of results to return
            chapter_filter: Optional chapter filter
            section_filter: Optional section filter
            min_score: Minimum similarity score threshold

        Returns:
            List of retrieved chunks sorted by similarity score
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)

            # Build filter conditions
            filter_conditions = []
            if chapter_filter:
                filter_conditions.append(
                    FieldCondition(key="chapter", match=MatchValue(value=chapter_filter))
                )
            if section_filter:
                filter_conditions.append(
                    FieldCondition(key="section", match=MatchValue(value=section_filter))
                )

            query_filter = None
            if filter_conditions:
                query_filter = Filter(must=filter_conditions)

            # Search Qdrant
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=top_k,
                score_threshold=min_score
            )

            # Convert to RetrievedChunk objects
            chunks = []
            for point in search_result:
                chunk = RetrievedChunk(
                    chunk_id=UUID(str(point.id)),
                    content=point.payload.get("content", ""),
                    score=point.score,
                    chapter=point.payload.get("chapter", ""),
                    section=point.payload.get("section", ""),
                    page=point.payload.get("page"),
                    url=point.payload.get("url", ""),
                    metadata=point.payload
                )
                chunks.append(chunk)

            self.logger.info(f"Vector search returned {len(chunks)} results")
            return chunks

        except Exception as e:
            self.logger.error(f"Vector search failed: {e}", exc_info=True)
            raise

    def bm25_search(
        self,
        query: str,
        top_k: int = 20,
        chapter_filter: Optional[str] = None,
        section_filter: Optional[str] = None
    ) -> List[RetrievedChunk]:
        """
        Perform BM25 keyword search.

        Args:
            query: Search query
            top_k: Number of results to return
            chapter_filter: Optional chapter filter
            section_filter: Optional section filter

        Returns:
            List of retrieved chunks sorted by BM25 score
        """
        try:
            # Build filter for Qdrant scroll
            filter_conditions = []
            if chapter_filter:
                filter_conditions.append(
                    FieldCondition(key="chapter", match=MatchValue(value=chapter_filter))
                )
            if section_filter:
                filter_conditions.append(
                    FieldCondition(key="section", match=MatchValue(value=section_filter))
                )

            query_filter = None
            if filter_conditions:
                query_filter = Filter(must=filter_conditions)

            # Retrieve all documents (or large batch)
            # Note: For production, consider implementing pagination or limiting to top N by vector search
            scroll_result = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=1000,  # Limit to avoid memory issues
                with_payload=True,
                with_vectors=False
            )

            points, _ = scroll_result

            if not points:
                self.logger.info("BM25 search: No documents found")
                return []

            # Prepare documents for BM25
            documents = [(UUID(str(p.id)), p.payload.get("content", "")) for p in points]

            # Score documents with BM25
            bm25_scores = self.bm25.score_documents(query, documents)

            # Convert to RetrievedChunk objects
            chunks = []
            point_map = {UUID(str(p.id)): p for p in points}

            for chunk_id, score in bm25_scores[:top_k]:
                if score <= 0:
                    continue

                point = point_map[chunk_id]
                chunk = RetrievedChunk(
                    chunk_id=chunk_id,
                    content=point.payload.get("content", ""),
                    score=score,
                    chapter=point.payload.get("chapter", ""),
                    section=point.payload.get("section", ""),
                    page=point.payload.get("page"),
                    url=point.payload.get("url", ""),
                    metadata=point.payload
                )
                chunks.append(chunk)

            self.logger.info(f"BM25 search returned {len(chunks)} results")
            return chunks

        except Exception as e:
            self.logger.error(f"BM25 search failed: {e}", exc_info=True)
            raise

    def reciprocal_rank_fusion(
        self,
        vector_results: List[RetrievedChunk],
        bm25_results: List[RetrievedChunk],
        k: int = 60
    ) -> List[RetrievedChunk]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).

        RRF score = sum(1 / (k + rank_i)) for each ranking

        Args:
            vector_results: Results from vector search
            bm25_results: Results from BM25 search
            k: RRF parameter (default: 60)

        Returns:
            Fused results sorted by RRF score
        """
        # Create rank maps
        vector_ranks = {chunk.chunk_id: idx for idx, chunk in enumerate(vector_results)}
        bm25_ranks = {chunk.chunk_id: idx for idx, chunk in enumerate(bm25_results)}

        # Collect all unique chunks
        all_chunk_ids = set(vector_ranks.keys()) | set(bm25_ranks.keys())

        # Build chunk map
        chunk_map = {}
        for chunk in vector_results:
            chunk_map[chunk.chunk_id] = chunk
        for chunk in bm25_results:
            chunk_map[chunk.chunk_id] = chunk

        # Calculate RRF scores
        rrf_scores = {}
        for chunk_id in all_chunk_ids:
            score = 0.0

            # Add vector search contribution
            if chunk_id in vector_ranks:
                score += 1.0 / (k + vector_ranks[chunk_id])

            # Add BM25 contribution
            if chunk_id in bm25_ranks:
                score += 1.0 / (k + bm25_ranks[chunk_id])

            rrf_scores[chunk_id] = score

        # Sort by RRF score
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        # Create fused results
        fused_results = []
        for chunk_id in sorted_ids:
            chunk = chunk_map[chunk_id]
            # Update score to RRF score
            chunk.score = rrf_scores[chunk_id]
            fused_results.append(chunk)

        self.logger.info(f"RRF fusion combined {len(fused_results)} unique chunks")
        return fused_results

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        retrieval_top_k: Optional[int] = None,
        chapter_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        use_hybrid: bool = True,
        min_score: float = 0.0
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks using hybrid search.

        Args:
            query: Search query
            top_k: Final number of results to return after fusion
            retrieval_top_k: Number of results to retrieve from each method before fusion
            chapter_filter: Optional chapter filter
            section_filter: Optional section filter
            use_hybrid: Whether to use hybrid search (if False, only vector search)
            min_score: Minimum similarity score for vector search

        Returns:
            List of top-K retrieved chunks
        """
        settings = get_settings()

        if retrieval_top_k is None:
            retrieval_top_k = settings.retrieval_top_k

        try:
            # Perform vector search
            self.logger.info(f"Performing vector search (top_k={retrieval_top_k})")
            vector_results = self.vector_search(
                query=query,
                top_k=retrieval_top_k,
                chapter_filter=chapter_filter,
                section_filter=section_filter,
                min_score=min_score
            )

            # If not using hybrid, return vector results only
            if not use_hybrid:
                return vector_results[:top_k]

            # Perform BM25 search
            self.logger.info(f"Performing BM25 search (top_k={retrieval_top_k})")
            bm25_results = self.bm25_search(
                query=query,
                top_k=retrieval_top_k,
                chapter_filter=chapter_filter,
                section_filter=section_filter
            )

            # Fuse results
            self.logger.info("Fusing results with RRF")
            fused_results = self.reciprocal_rank_fusion(vector_results, bm25_results)

            # Return top-K
            final_results = fused_results[:top_k]

            self.logger.info(
                f"Retrieved {len(final_results)} chunks for query: {query[:50]}...",
                extra={
                    "extra_fields": {
                        "query": query,
                        "num_results": len(final_results),
                        "vector_count": len(vector_results),
                        "bm25_count": len(bm25_results)
                    }
                }
            )

            return final_results

        except Exception as e:
            self.logger.error(f"Hybrid retrieval failed: {e}", exc_info=True)
            raise
