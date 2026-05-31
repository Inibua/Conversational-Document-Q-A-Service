"""
Example usage of the Processor module.

This script demonstrates how to use the DocumentProcessor to process
collected documents into chunks with metadata.
"""
import os
import sys
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from indexer.discoverer import LocalFileDiscoverer
from indexer.collector import LocalFileCollector, CollectionStatus
from indexer.processor import DocumentProcessor, ProcessingStatus


def main():
    """Main function to demonstrate processor usage."""
    
    # Create mock database session (in a real application, this would be a SQLAlchemy session)
    mock_db_session = MagicMock()
    
    # Configuration for all components
    config = {
        'discoverer': {
            'root_path': 'data_to_ingest',
            'file_extensions': ['.txt', '.md'],
            'exclude_patterns': ['.git', '__pycache__']
        },
        'collector': {
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_mime_types': ['text/plain', 'text/markdown']
        },
        'processor': {
            'chunk_size': 500,  # Smaller chunks for demo
            'chunk_overlap': 100,
            'supported_content_types': ['text/plain', 'text/markdown']
        }
    }
    
    print("=== Document Processing Pipeline ===")
    print()
    
    # Step 1: Discovery
    print("Step 1: Discovering documents...")
    discoverer = LocalFileDiscoverer(config['discoverer'], mock_db_session)
    discovered_documents = discoverer.discover()
    print(f"Discovered {len(discovered_documents)} documents")
    print()
    
    # Step 2: Collection
    print("Step 2: Collecting document content...")
    collector = LocalFileCollector(config['collector'], mock_db_session)
    
    # Convert discovered documents to metadata list for collector
    document_metadata_list = [
        {
            'path': doc.path,
            'source_type': doc.source_type,
            'metadata': {'discovered_at': str(doc.modified_time)}
        }
        for doc in discovered_documents
    ]
    
    collected_documents = collector.collect(document_metadata_list)
    successful_collections = [doc for doc in collected_documents if doc.status == CollectionStatus.COLLECTED]
    print(f"Successfully collected {len(successful_collections)} documents")
    print()
    
    # Step 3: Processing
    print("Step 3: Processing documents into chunks...")
    processor = DocumentProcessor(config['processor'], mock_db_session)
    
    # Convert collected documents to format expected by processor
    collected_docs_for_processing = []
    for doc in successful_collections:
        collected_doc = {
            'path': doc.path,
            'source_type': doc.source_type,
            'content_type': doc.content_type,
            'raw_content': doc.raw_content,
            'encoding': doc.encoding,
            'status': doc.status.value
        }
        collected_docs_for_processing.append(collected_doc)
    
    processed_chunks = processor.process(collected_docs_for_processing)
    
    successful_chunks = [chunk for chunk in processed_chunks if chunk.status == ProcessingStatus.PROCESSED]
    failed_chunks = [chunk for chunk in processed_chunks if chunk.status == ProcessingStatus.FAILED]
    
    print(f"Processing results:")
    print(f"  Successful chunks: {len(successful_chunks)}")
    print(f"  Failed chunks: {len(failed_chunks)}")
    print()
    
    # Display processed chunks
    print("Processed Chunks:")
    for i, chunk in enumerate(successful_chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  Document: {chunk.source_document_path}")
        print(f"  Chunk ID: {chunk.chunk_id}")
        print(f"  Status: {chunk.status.value}")
        print(f"  Position: {chunk.chunk_index + 1}/{chunk.total_chunks}")
        print(f"  Content Length: {len(chunk.content)} characters")
        print(f"  Content Preview: {chunk.content[:100]}...")
        print(f"  Metadata: {chunk.metadata}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())