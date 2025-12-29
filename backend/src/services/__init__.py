"""
Services module for textbook chatbot.

Provides core services for embeddings, retrieval, and LLM integration.
"""
from src.services.embeddings import EmbeddingGenerator, EmbeddingCache

__all__ = [
    'EmbeddingGenerator',
    'EmbeddingCache'
]
