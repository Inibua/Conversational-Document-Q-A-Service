"""
Example usage of the Collector module.

This script demonstrates how to use the LocalFileCollector to collect
raw content from documents discovered by the discoverer.
"""
import os
import sys
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from indexer.discoverer import LocalFileDiscoverer
from indexer.collector import LocalFileCollector, CollectionStatus


def main():
    """Main function to demonstrate collector usage."""
    
    # Create mock database session (in a real application, this would be a SQLAlchemy session)
    mock_db_session = MagicMock()
    
    # Configuration for the discoverer
    discoverer_config = {
        'root_path': 'data_to_ingest',
        'file_extensions': ['.txt', '.md'],
        'exclude_patterns': ['.git', '__pycache__']
    }
    
    # Configuration for the collector
    collector_config = {
        'max_file_size': 10 * 1024 * 1024,  # 10MB
        'supported_mime_types': ['text/plain', 'text/markdown']
    }
    
    print("=== Document Collection Pipeline ===")
    print()
    
    # Step 1: Discovery
    print("Step 1: Discovering documents...")
    discoverer = LocalFileDiscoverer(discoverer_config, mock_db_session)
    discovered_documents = discoverer.discover()
    print(f"Discovered {len(discovered_documents)} documents")
    print()
    
    # Convert discovered documents to metadata list for collector
    document_metadata_list = []
    for doc in discovered_documents:
        doc_metadata = {
            'path': doc.path,
            'source_type': doc.source_type,
            'metadata': {
                'discovered_at': str(doc.modified_time),
                'file_size': doc.size
            }
        }
        document_metadata_list.append(doc_metadata)
    
    # Step 2: Collection
    print("Step 2: Collecting document content...")
    collector = LocalFileCollector(collector_config, mock_db_session)
    collected_documents = collector.collect(document_metadata_list)
    
    print(f"Collection results:")
    print(f"  Successful: {sum(1 for doc in collected_documents if doc.status == CollectionStatus.COLLECTED)}")
    print(f"  Failed: {sum(1 for doc in collected_documents if doc.status == CollectionStatus.FAILED)}")
    print()
    
    # Display collected documents
    for i, doc in enumerate(collected_documents, 1):
        print(f"Document {i}:")
        print(f"  Path: {doc.path}")
        print(f"  Status: {doc.status.value}")
        print(f"  Size: {doc.size} bytes")
        print(f"  Content Type: {doc.content_type}")
        print(f"  Collected At: {doc.collected_at}")
        
        # Display a preview of the content (first 100 chars)
        content_preview = doc.raw_content[:100].decode(doc.encoding, errors='replace')
        print(f"  Content Preview: {content_preview}...")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())