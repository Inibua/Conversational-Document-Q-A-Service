"""
Vector Store Package

This package contains implementations of various vector stores for the
Conversational Document Q&A Service.
"""

from .base import VectorStore
from .qdrant_vector_store import QdrantVectorStore

__all__ = [
    'VectorStore',
    'QdrantVectorStore'
]