"""
Storer module initialization.

This module provides the base Storer interface and concrete implementations
for storing processed document chunks in vector databases.
"""

from .base import Storer
from .qdrant_storer import QdrantStorer

__all__ = ['Storer', 'QdrantStorer']