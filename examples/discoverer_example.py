"""
Example usage of the Discoverer module.

This script demonstrates how to use the LocalFileDiscoverer to find
documents in a local directory that need to be processed.
"""
import os
import sys
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from indexer.discoverer import LocalFileDiscoverer, DocumentMetadata


def main():
    """Main function to demonstrate discoverer usage."""
    
    # Create a mock database session (in a real application, this would be a SQLAlchemy session)
    mock_db_session = MagicMock()
    
    # Configuration for the discoverer
    config = {
        'root_path': 'data_to_ingest',  # Path to search for documents
        'file_extensions': ['.txt', '.md', '.pdf', '.docx'],  # File extensions to include
        'exclude_patterns': ['.git', '__pycache__', '.venv']  # Patterns to exclude
    }
    
    print("Creating LocalFileDiscoverer...")
    discoverer = LocalFileDiscoverer(config, mock_db_session)
    
    print(f"Searching for documents in: {config['root_path']}")
    print(f"Looking for files with extensions: {config['file_extensions']}")
    print(f"Excluding patterns: {config['exclude_patterns']}")
    print()
    
    try:
        # Discover documents
        discovered_documents = discoverer.discover()
        
        print(f"Found {len(discovered_documents)} documents to process:")
        print()
        
        for i, doc in enumerate(discovered_documents, 1):
            print(f"{i}. Path: {doc.path}")
            print(f"   Size: {doc.size} bytes")
            print(f"   Modified: {doc.modified_time}")
            print(f"   Source: {doc.source_type}")
            print(f"   Status: {doc.status}")
            print()
            
    except Exception as e:
        print(f"Error during discovery: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())