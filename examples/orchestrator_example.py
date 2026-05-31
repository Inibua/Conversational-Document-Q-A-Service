"""
Simple Orchestrator Example

This demonstrates how to use the BasicOrchestrator to coordinate the indexing pipeline.
"""
import os
import sys
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from indexer.orchestrator import create_orchestrator


def main():
    """Main function to demonstrate the orchestrator."""
    
    # Configuration for the orchestrator
    config = {
        'discoverer': {
            'root_path': 'data_to_ingest',
            'file_extensions': ['.txt', '.md', '.pdf', '.docx'],
            'exclude_patterns': ['.git', '__pycache__', '.venv']
        },
        'collector': {
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_mime_types': ['text/plain', 'text/markdown', 'application/pdf']
        },
        'processor': {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'supported_content_types': ['text/plain', 'text/markdown', 'application/pdf']
        },
        'storer': {
            'embedding_model': 'all-MiniLM-L6-v2',
            'qdmant_host': 'localhost',
            'qdmant_port': 6333,
            'collection_name': 'documents',
            'vector_size': 768
        }
    }
    
    try:
        # Create mock database session and vector store
        # In a real application, these would be actual instances
        mock_db_session = MagicMock()
        mock_vector_store = MagicMock()
        
        # Create orchestrator
        orchestrator = create_orchestrator(config, mock_db_session, mock_vector_store)
        
        # Run the indexing pipeline
        success = orchestrator.run()
        
        if success:
            print("Orchestrator completed successfully!")
            return 0
        else:
            print("Orchestrator encountered errors during execution.")
            return 1
            
    except Exception as e:
        print(f"Error running orchestrator: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())