"""
Indexer package.

This package contains the components for discovering, collecting, processing,
and storing documents for a RAG application.
"""

# Import discoverer components
from .discoverer import Discoverer, LocalFileDiscoverer, DocumentMetadata

# Import collector components
from .collector import Collector, LocalFileCollector, CollectedDocument, CollectionStatus

# Import processor components
from .processor import Processor, DocumentProcessor, ProcessedChunk, ProcessingStatus

__all__ = [
    'Discoverer',
    'LocalFileDiscoverer', 
    'DocumentMetadata',
    'Collector',
    'LocalFileCollector',
    'CollectedDocument',
    'CollectionStatus',
    'Processor',
    'DocumentProcessor',
    'ProcessedChunk',
    'ProcessingStatus'
]