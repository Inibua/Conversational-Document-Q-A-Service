"""
Test cases for the Discoverer module.
"""
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from indexer.discoverer import Discoverer, LocalFileDiscoverer, DocumentMetadata


class TestDocumentMetadata(unittest.TestCase):
    """Test cases for DocumentMetadata dataclass."""
    
    def test_document_metadata_creation(self):
        """Test that DocumentMetadata can be created correctly."""
        metadata = DocumentMetadata(
            path="/path/to/file.txt",
            size=1024,
            modified_time=datetime.now(),
            source_type="local_file"
        )
        
        self.assertEqual(metadata.path, "/path/to/file.txt")
        self.assertEqual(metadata.size, 1024)
        self.assertEqual(metadata.source_type, "local_file")
        self.assertEqual(metadata.status, "pending")


class TestDiscovererBase(unittest.TestCase):
    """Test cases for the base Discoverer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = MagicMock()
        self.config = {
            'root_path': '/tmp',
            'file_extensions': ['.txt', '.md']
        }
    
    def test_discoverer_initialization(self):
        """Test that Discoverer can be initialized."""
        # We can't instantiate the abstract base class directly,
        # but we can test that it has the expected methods
        self.assertTrue(hasattr(Discoverer, 'discover'))
        self.assertTrue(hasattr(Discoverer, 'update_document_status'))
        self.assertTrue(hasattr(Discoverer, 'should_process_document'))


class TestLocalFileDiscoverer(unittest.TestCase):
    """Test cases for the LocalFileDiscoverer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.mock_db_session = MagicMock()
        
        # Create some test files
        self.test_files = [
            "test1.txt",
            "test2.md",
            "test3.pdf",
            "excluded.log"
        ]
        
        for file in self.test_files:
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write("test content")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary directory and its contents
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)
    
    def test_local_file_discoverer_initialization(self):
        """Test that LocalFileDiscoverer can be initialized."""
        config = {
            'root_path': self.test_dir,
            'file_extensions': ['.txt', '.md'],
            'exclude_patterns': []
        }
        
        discoverer = LocalFileDiscoverer(config, self.mock_db_session)
        
        self.assertEqual(discoverer.root_path, self.test_dir)
        self.assertEqual(discoverer.file_extensions, ['.txt', '.md'])
        self.assertEqual(discoverer.exclude_patterns, [])
    
    def test_discover_with_valid_files(self):
        """Test that discover finds files with valid extensions."""
        config = {
            'root_path': self.test_dir,
            'file_extensions': ['.txt', '.md'],
            'exclude_patterns': []
        }
        
        discoverer = LocalFileDiscoverer(config, self.mock_db_session)
        discovered = discoverer.discover()
        
        # Should find test1.txt and test2.md, but not test3.pdf or excluded.log
        self.assertEqual(len(discovered), 2)
        
        discovered_paths = [doc.path for doc in discovered]
        self.assertTrue(any('test1.txt' in path for path in discovered_paths))
        self.assertTrue(any('test2.md' in path for path in discovered_paths))
        self.assertFalse(any('test3.pdf' in path for path in discovered_paths))
        self.assertFalse(any('excluded.log' in path for path in discovered_paths))
    
    def test_discover_with_exclusion_patterns(self):
        """Test that discover excludes files matching patterns."""
        # Create a subdirectory with a file that should be excluded
        excluded_dir = os.path.join(self.test_dir, "excluded_dir")
        os.makedirs(excluded_dir)
        
        with open(os.path.join(excluded_dir, "test_excluded.txt"), 'w') as f:
            f.write("test content")
        
        config = {
            'root_path': self.test_dir,
            'file_extensions': ['.txt', '.md'],
            'exclude_patterns': ['excluded']
        }
        
        discoverer = LocalFileDiscoverer(config, self.mock_db_session)
        discovered = discoverer.discover()
        
        # Should find test1.txt and test2.md, but not the file in excluded_dir
        self.assertEqual(len(discovered), 2)
        
        discovered_paths = [doc.path for doc in discovered]
        self.assertFalse(any('excluded_dir' in path for path in discovered_paths))
    
    def test_has_valid_extension(self):
        """Test the _has_valid_extension method."""
        config = {
            'root_path': self.test_dir,
            'file_extensions': ['.txt', '.md']
        }
        
        discoverer = LocalFileDiscoverer(config, self.mock_db_session)
        
        self.assertTrue(discoverer._has_valid_extension("file.txt"))
        self.assertTrue(discoverer._has_valid_extension("file.md"))
        self.assertFalse(discoverer._has_valid_extension("file.pdf"))
        self.assertFalse(discoverer._has_valid_extension("file.log"))
    
    def test_should_include_path(self):
        """Test the _should_include_path method."""
        config = {
            'root_path': self.test_dir,
            'exclude_patterns': ['excluded', 'temp']
        }
        
        discoverer = LocalFileDiscoverer(config, self.mock_db_session)
        
        self.assertTrue(discoverer._should_include_path("/path/to/file.txt"))
        self.assertFalse(discoverer._should_include_path("/path/to/excluded/file.txt"))
        self.assertFalse(discoverer._should_include_path("/path/to/temp/file.txt"))
    
    def test_invalid_root_path(self):
        """Test that LocalFileDiscoverer raises error for invalid root path."""
        config = {
            'root_path': '/nonexistent/path',
            'file_extensions': ['.txt']
        }
        
        with self.assertRaises(ValueError):
            LocalFileDiscoverer(config, self.mock_db_session)
    
    def test_root_path_not_directory(self):
        """Test that LocalFileDiscoverer raises error if root path is not a directory."""
        # Create a file instead of a directory
        test_file = tempfile.NamedTemporaryFile(delete=False)
        test_file.close()
        
        try:
            config = {
                'root_path': test_file.name,
                'file_extensions': ['.txt']
            }
            
            with self.assertRaises(ValueError):
                LocalFileDiscoverer(config, self.mock_db_session)
        finally:
            os.unlink(test_file.name)


if __name__ == '__main__':
    unittest.main()