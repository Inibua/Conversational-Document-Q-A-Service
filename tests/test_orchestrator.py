"""
Test the basic orchestrator functionality.
"""
import os
import sys
import tempfile
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from indexer.orchestrator import create_orchestrator


def create_test_documents():
    """Create test documents in a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    
    # Create some test files
    test_files = []
    for i in range(3):
        filename = os.path.join(temp_dir, f"test{i}.txt")
        with open(filename, 'w') as f:
            f.write(f"This is test document {i} content.")
        test_files.append(filename)
    
    return temp_dir, test_files


def test_orchestrator_basic_functionality():
    """Test that the orchestrator can be created and run."""
    print("Testing orchestrator basic functionality...")
    
    # Create test documents
    temp_dir, test_files = create_test_documents()
    
    try:
        # Configuration for the orchestrator
        config = {
            'discoverer': {
                'root_path': temp_dir,
                'file_extensions': ['.txt'],
                'exclude_patterns': []
            },
            'collector': {
                'max_file_size': 10 * 1024 * 1024,
                'supported_mime_types': ['text/plain']
            },
            'processor': {
                'chunk_size': 500,
                'chunk_overlap': 100,
                'supported_content_types': ['text/plain']
            },
            'storer': {
                'embedding_model': 'all-MiniLM-L6-v2',
                'collection_name': 'test_documents'
            }
        }
        
        # Create mock database session and vector store
        mock_db_session = MagicMock()
        mock_vector_store = MagicMock()
        
        # Create orchestrator
        orchestrator = create_orchestrator(config, mock_db_session, mock_vector_store)
        
        # Test basic orchestrator methods
        assert orchestrator is not None, "Orchestrator should not be None"
        assert hasattr(orchestrator, 'run'), "Orchestrator should have run method"
        assert hasattr(orchestrator, '_create_components'), "Orchestrator should have _create_components method"
        
        print("✓ Orchestrator basic functionality test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator basic functionality test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up temp files
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_orchestrator_component_creation():
    """Test that orchestrator can create its component parts."""
    print("Testing orchestrator component creation...")
    
    temp_dir, _ = create_test_documents()
    
    try:
        config = {
            'discoverer': {
                'root_path': temp_dir,
                'file_extensions': ['.txt'],
                'exclude_patterns': []
            },
            'collector': {
                'max_file_size': 10 * 1024 * 1024,
                'supported_mime_types': ['text/plain']
            },
            'processor': {
                'chunk_size': 500,
                'chunk_overlap': 100,
                'supported_content_types': ['text/plain']
            },
            'storer': {
                'embedding_model': 'all-MiniLM-L6-v2',
                'collection_name': 'test_documents'
            }
        }
        
        mock_db_session = MagicMock()
        mock_vector_store = MagicMock()
        
        orchestrator = create_orchestrator(config, mock_db_session, mock_vector_store)
        
        # Test component creation
        discoverer, collector, processor, storer = orchestrator._create_components()
        
        assert discoverer is not None, "Discoverer should not be None"
        assert collector is not None, "Collector should not be None"
        assert processor is not None, "Processor should not be None"
        assert storer is not None, "Storer should not be None"
        
        print("✓ Orchestrator component creation test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Orchestrator component creation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("Running orchestrator tests...\n")
    
    test1_passed = test_orchestrator_basic_functionality()
    print()
    test2_passed = test_orchestrator_component_creation()
    
    if test1_passed and test2_passed:
        print("\n✓ All orchestrator tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some orchestrator tests failed!")
        sys.exit(1)