"""
Collector module for the indexer component.

This module contains the base Collector class and its implementations
for collecting raw documents from various sources.
"""
from .base import Collector, CollectedDocument, CollectionStatus
from .local_file_collector import LocalFileCollector

__all__ = ["Collector", "LocalFileCollector", "CollectedDocument", "CollectionStatus"]