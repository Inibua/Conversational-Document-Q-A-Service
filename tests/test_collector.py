"""
Test cases for the Collector module.
"""
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from indexer.collector import Collector, LocalFileCollector, CollectedDocument, CollectionStatus


class TestCollectedDocument(unittest.TestCase):
    """Test cases for CollectedDocument dataclass."""
    
    def test_collected_document_creation(self):
        """Test that CollectedDocument can be created correctly."""
        doc = CollectedDocument(
            path="/path/to/file.txt",
            source_type="local_file",
            raw_content=b"test content",
            content_type="text/plain",
            size=12,
            status=CollectionStatus.COLLECTED
        )
        
        self.assertEqual(doc.path, "/path/to/file.txt")
        self.assertEqual(doc.source_type, "local_file")
        self.assertEqual(doc.raw_content, b"test content")
        self.assertEqual(doc.content_type, "text/plain")
        self.assertEqual(doc.size, 12)
        self.assertEqual(doc.status, CollectionStatus.COLLECTED)
        self.assertIsNotNone(doc.collected_at)
        self.assertIsNotNone(doc.metadata)
    
    def test_collected_document_defaults(self):
        """Test that CollectedDocument defaults work correctly."""
        doc = CollectedDocument(
            path="/path/to/file.txt",
            source_type="local_file"
        )
        
        self.assertEqual(doc.raw_content, b"")
        self.assertEqual(doc.content_type, "text/plain")
        self.assertEqual(doc.encoding, "utf-8")
        self.assertEqual(doc.size, 0)
        self.assertEqual(doc.status, CollectionStatus.PENDING)  # Default status
        self.assertIsNotNone(doc.collected_at)


class TestCollectorBase(unittest.TestCase):
    """Test cases for the base Collector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = MagicMock()
        self.config = {
            'max_file_size': 1024 * 1024  # 1MB
        }
    
    def test_collector_initialization(self):
        """Test that Collector can be initialized."""
        # We can't instantiate the abstract base class directly,
        # but we can test that it has the expected methods
        self.assertTrue(hasattr(Collector, 'collect'))
        self.assertTrue(hasattr(Collector, 'update_document_status'))
        self.assertTrue(hasattr(Collector, 'validate_document'))
        self.assertTrue(hasattr(Collector, 'create_collected_document'))
    
    def test_create_collected_document(self):
        """Test the create_collected_document method."""
        # Create a concrete collector to test the method
        collector = LocalFileCollector(self.config, self.mock_db_session)
        
        doc_metadata = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'metadata': {'author': 'test'}
        }
        
        raw_content = b"test content"
        
        collected_doc = collector.create_collected_document(
            document_metadata=doc_metadata,
            raw_content=raw_content,
            content_type="text/plain",
            encoding="utf-8"
        )
        
        self.assertEqual(collected_doc.path, '/test/file.txt')
        self.assertEqual(collected_doc.source_type, 'local_file')
        self.assertEqual(collected_doc.raw_content, raw_content)
        self.assertEqual(collected_doc.content_type, "text/plain")
        self.assertEqual(collected_doc.encoding, "utf-8")
        self.assertEqual(collected_doc.size, len(raw_content))
        self.assertEqual(collected_doc.status, CollectionStatus.COLLECTED)
        self.assertEqual(collected_doc.metadata, {'author': 'test'})


class TestLocalFileCollector(unittest.TestCase):
    """Test cases for the LocalFileCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.mock_db_session = MagicMock()
        
        # Create some test files
        self.test_files = {
            'test1.txt': 'This is a test text file.',
            'test2.md': '# Test Markdown\n\nThis is a markdown file.',
            'empty.txt': '',
            'large.txt': 'x' * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write(content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove the temporary directory and its contents
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)
    
    def test_local_file_collector_initialization(self):
        """Test that LocalFileCollector can be initialized."""
        config = {
            'max_file_size': 1024,
            'supported_mime_types': ['text/plain', 'text/markdown']
        }
        
        collector = LocalFileCollector(config, self.mock_db_session)
        
        self.assertEqual(collector.max_file_size, 1024)
        self.assertEqual(collector.supported_mime_types, ['text/plain', 'text/markdown'])
    
    def test_collect_valid_files(self):
        """Test that collect successfully processes valid files."""
        config = {
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_mime_types': ['text/plain', 'text/markdown']
        }
        
        collector = LocalFileCollector(config, self.mock_db_session)
        
        # Create document metadata for valid files
        doc_metadata_list = [
            {
                'path': os.path.join(self.test_dir, 'test1.txt'),
                'source_type': 'local_file'
            },
            {
                'path': os.path.join(self.test_dir, 'test2.md'),
                'source_type': 'local_file'
            }
        ]
        
        collected_docs = collector.collect(doc_metadata_list)
        
        # Should collect both valid files
        self.assertEqual(len(collected_docs), 2)
        
        # Check that both documents were collected successfully
        for doc in collected_docs:
            self.assertEqual(doc.status, CollectionStatus.COLLECTED)
            self.assertGreater(doc.size, 0)
            self.assertIsNotNone(doc.raw_content)
    
    def test_collect_with_size_limit(self):
        """Test that collect respects file size limits."""
        config = {
            'max_file_size': 1024,  # 1KB
            'supported_mime_types': ['text/plain']
        }
        
        collector = LocalFileCollector(config, self.mock_db_session)
        
        # Create document metadata including a large file
        doc_metadata_list = [
            {
                'path': os.path.join(self.test_dir, 'test1.txt'),
                'source_type': 'local_file'
            },
            {
                'path': os.path.join(self.test_dir, 'large.txt'),
                'source_type': 'local_file'
            }
        ]
        
        collected_docs = collector.collect(doc_metadata_list)
        
        # Should only collect the small file
        self.assertEqual(len(collected_docs), 1)
        self.assertEqual(collected_docs[0].status, CollectionStatus.COLLECTED)
        self.assertIn('test1.txt', collected_docs[0].path)
    
    def test_collect_empty_file(self):
        """Test that collect handles empty files appropriately."""
        config = {
            'max_file_size': 1024,
            'supported_mime_types': ['text/plain']
        }
        
        collector = LocalFileCollector(config, self.mock_db_session)
        
        # Create document metadata for empty file
        doc_metadata_list = [
            {
                'path': os.path.join(self.test_dir, 'empty.txt'),
                'source_type': 'local_file'
            }
        ]
        
        collected_docs = collector.collect(doc_metadata_list)
        
        # Empty file should be skipped during validation
        self.assertEqual(len(collected_docs), 0)
    
    def test_collect_nonexistent_file(self):
        """Test that collect handles nonexistent files."""
        config = {
            'max_file_size': 1024,
            'supported_mime_types': ['text/plain']
        }
        
        collector = LocalFileCollector(config, self.mock_db_session)
        
        # Create document metadata for nonexistent file
        doc_metadata_list = [
            {
                'path': '/nonexistent/path/file.txt',
                'source_type': 'local_file'
            }
        ]
        
        collected_docs = collector.collect(doc_metadata_list)
        
        # Nonexistent file should be skipped during validation
        self.assertEqual(len(collected_docs), 0)
    
    def test_collect_with_unsupported_file_type(self):
        """Test that collect handles unsupported file types."""
        # Create a file with unsupported extension
        unsupported_file = os.path.join(self.test_dir, 'test.unsupported')
        with open(unsupported_file, 'w') as f:
            f.write('test content')
        
        config = {
            'max_file_size': 1024,
            'supported_mime_types': ['text/plain']  # .unsupported not in list
        }
        
        collector = LocalFileCollector(config, self.mock_db_session)
        
        doc_metadata_list = [
            {
                'path': unsupported_file,
                'source_type': 'local_file'
            }
        ]
        
        collected_docs = collector.collect(doc_metadata_list)
        
        # Unsupported file type should be skipped
        self.assertEqual(len(collected_docs), 0)
    
    def test_validate_document(self):
        """Test the validate_document method."""
        config = {'max_file_size': 1024}
        collector = LocalFileCollector(config, self.mock_db_session)
        
        # Test valid document
        valid_doc = {
            'path': os.path.join(self.test_dir, 'test1.txt'),
            'source_type': 'local_file'
        }
        self.assertTrue(collector.validate_document(valid_doc))
        
        # Test invalid document (missing fields)
        invalid_doc = {'path': os.path.join(self.test_dir, 'test1.txt')}
        self.assertFalse(collector.validate_document(invalid_doc))
        
        # Test nonexistent file
        nonexistent_doc = {
            'path': '/nonexistent/file.txt',
            'source_type': 'local_file'
        }
        self.assertFalse(collector.validate_document(nonexistent_doc))
    
    def test_detect_file_type(self):
        """Test the detect_file_type method."""
        config = {}
        collector = LocalFileCollector(config, self.mock_db_session)
        
        # Test known file types
        self.assertEqual(collector.detect_file_type('test.txt'), 'text/plain')
        self.assertEqual(collector.detect_file_type('test.md'), 'text/markdown')
        self.assertEqual(collector.detect_file_type('test.pdf'), 'application/pdf')
        self.assertEqual(collector.detect_file_type('test.docx'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        
        # Test unknown file type
        self.assertEqual(collector.detect_file_type('test.xyz'), 'application/octet-stream')
    
    def test_collect_with_permission_error(self):
        """Test that collect handles permission errors gracefully."""
        # Create a file and make it read-only
        readonly_file = os.path.join(self.test_dir, 'readonly.txt')
        with open(readonly_file, 'w') as f:
            f.write('test content')
        
        # Change permissions to read-only (this might not work on all systems)
        try:
            os.chmod(readonly_file, 0o444)  # Read-only
            
            config = {
                'max_file_size': 1024,
                'supported_mime_types': ['text/plain']
            }
            
            collector = LocalFileCollector(config, self.mock_db_session)
            
            doc_metadata_list = [
                {
                    'path': readonly_file,
                    'source_type': 'local_file'
                }
            ]
            
            collected_docs = collector.collect(doc_metadata_list)
            
            # Should either collect successfully (if read permission is sufficient)
            # or fail gracefully
            if len(collected_docs) == 1:
                self.assertEqual(collected_docs[0].status, CollectionStatus.COLLECTED)
            else:
                self.assertEqual(len(collected_docs), 1)
                self.assertEqual(collected_docs[0].status, CollectionStatus.FAILED)
                
        finally:
            # Restore permissions
            if os.path.exists(readonly_file):
                os.chmod(readonly_file, 0o644)


if __name__ == '__main__':
    unittest.main()