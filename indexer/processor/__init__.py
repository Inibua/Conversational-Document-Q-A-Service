"""
Processor module for the indexer component.

This module contains the base Processor class and its implementations
for processing raw documents into chunks with metadata.
"""
from .base import Processor, ProcessedChunk, ProcessingStatus
from .document_processor import DocumentProcessor

__all__ = ["Processor", "DocumentProcessor", "ProcessedChunk", "ProcessingStatus"]