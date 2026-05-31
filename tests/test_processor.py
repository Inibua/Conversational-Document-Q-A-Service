"""
Test cases for the Processor module.
"""
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from indexer.processor import Processor, DocumentProcessor, ProcessedChunk, ProcessingStatus


class TestProcessedChunk(unittest.TestCase):
    """Test cases for ProcessedChunk dataclass."""
    
    def test_processed_chunk_creation(self):
        """Test that ProcessedChunk can be created correctly."""
        chunk = ProcessedChunk(
            source_document_path="/path/to/file.txt",
            source_type="local_file",
            content="This is chunk content",
            chunk_index=0,
            total_chunks=1,
            status=ProcessingStatus.PROCESSED
        )
        
        self.assertEqual(chunk.source_document_path, "/path/to/file.txt")
        self.assertEqual(chunk.source_type, "local_file")
        self.assertEqual(chunk.content, "This is chunk content")
        self.assertEqual(chunk.chunk_index, 0)
        self.assertEqual(chunk.total_chunks, 1)
        self.assertEqual(chunk.status, ProcessingStatus.PROCESSED)
        self.assertIsNotNone(chunk.processed_at)
        self.assertIsNotNone(chunk.metadata)
    
    def test_processed_chunk_defaults(self):
        """Test that ProcessedChunk defaults work correctly."""
        chunk = ProcessedChunk(
            source_document_path="/path/to/file.txt",
            source_type="local_file"
        )
        
        self.assertEqual(chunk.content, "")
        self.assertEqual(chunk.content_type, "text/markdown")
        self.assertEqual(chunk.chunk_index, 0)
        self.assertEqual(chunk.total_chunks, 1)
        self.assertEqual(chunk.status, ProcessingStatus.PENDING)  # Default status
        self.assertIsNotNone(chunk.processed_at)
        self.assertIsNotNone(chunk.metadata)


class TestProcessorBase(unittest.TestCase):
    """Test cases for the base Processor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = MagicMock()
        self.config = {
            'chunk_size': 1000,
            'chunk_overlap': 200
        }
    
    def test_processor_initialization(self):
        """Test that Processor can be initialized."""
        # We can't instantiate the abstract base class directly,
        # but we can test that it has the expected methods
        self.assertTrue(hasattr(Processor, 'process'))
        self.assertTrue(hasattr(Processor, 'store_processed_chunks'))
        self.assertTrue(hasattr(Processor, 'validate_collected_document'))
        self.assertTrue(hasattr(Processor, 'create_processed_chunk'))
    
    def test_create_processed_chunk(self):
        """Test the create_processed_chunk method."""
        # Create a concrete processor to test the method
        processor = DocumentProcessor(self.config, self.mock_db_session)
        
        collected_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'content_type': 'text/plain',
            'raw_content': b'test content',
            'status': 'collected'
        }
        
        chunk = processor.create_processed_chunk(
            collected_document=collected_doc,
            chunk_content="test chunk",
            chunk_index=0,
            total_chunks=1,
            metadata={'custom': 'metadata'}
        )
        
        self.assertEqual(chunk.source_document_path, '/test/file.txt')
        self.assertEqual(chunk.source_type, 'local_file')
        self.assertEqual(chunk.content, "test chunk")
        self.assertEqual(chunk.chunk_index, 0)
        self.assertEqual(chunk.total_chunks, 1)
        self.assertEqual(chunk.status, ProcessingStatus.PROCESSED)
        self.assertIn('custom', chunk.metadata)
        self.assertEqual(chunk.metadata['custom'], 'metadata')


class TestDocumentProcessor(unittest.TestCase):
    """Test cases for the DocumentProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_session = MagicMock()
        self.config = {
            'chunk_size': 100,  # Small chunk size for testing
            'chunk_overlap': 20,
            'supported_content_types': ['text/plain', 'text/markdown']
        }
        self.processor = DocumentProcessor(self.config, self.mock_db_session)
    
    def test_document_processor_initialization(self):
        """Test that DocumentProcessor can be initialized."""
        self.assertEqual(self.processor.chunk_size, 100)
        self.assertEqual(self.processor.chunk_overlap, 20)
        self.assertEqual(self.processor.supported_content_types, ['text/plain', 'text/markdown'])
    
    def test_process_single_small_document(self):
        """Test processing a single small document that fits in one chunk."""
        collected_docs = [
            {
                'path': '/test/file1.txt',
                'source_type': 'local_file',
                'content_type': 'text/plain',
                'raw_content': b'This is a short test document.',
                'encoding': 'utf-8',
                'status': 'collected'
            }
        ]
        
        processed_chunks = self.processor.process(collected_docs)
        
        # Should create one chunk
        self.assertEqual(len(processed_chunks), 1)
        self.assertEqual(processed_chunks[0].status, ProcessingStatus.PROCESSED)
        self.assertEqual(processed_chunks[0].chunk_index, 0)
        self.assertEqual(processed_chunks[0].total_chunks, 1)
        self.assertIn('This is a short test document.', processed_chunks[0].content)
    
    def test_process_document_requiring_chunking(self):
        """Test processing a document that requires multiple chunks."""
        # Create content that will require multiple chunks with our small chunk size
        long_content = "This is a longer document. " * 20  # ~600 characters
        
        collected_docs = [
            {
                'path': '/test/file2.txt',
                'source_type': 'local_file',
                'content_type': 'text/plain',
                'raw_content': long_content.encode('utf-8'),
                'encoding': 'utf-8',
                'status': 'collected'
            }
        ]
        
        processed_chunks = self.processor.process(collected_docs)
        
        # Should create multiple chunks
        self.assertGreater(len(processed_chunks), 1)
        
        # Check that chunks are properly numbered
        for i, chunk in enumerate(processed_chunks):
            self.assertEqual(chunk.chunk_index, i)
            self.assertEqual(chunk.total_chunks, len(processed_chunks))
            self.assertEqual(chunk.status, ProcessingStatus.PROCESSED)
            self.assertIsNotNone(chunk.chunk_id)
    
    def test_process_multiple_documents(self):
        """Test processing multiple documents."""
        collected_docs = [
            {
                'path': '/test/file1.txt',
                'source_type': 'local_file',
                'content_type': 'text/plain',
                'raw_content': b'First document content.',
                'encoding': 'utf-8',
                'status': 'collected'
            },
            {
                'path': '/test/file2.md',
                'source_type': 'local_file',
                'content_type': 'text/markdown',
                'raw_content': b'# Second Document\n\nContent here.',
                'encoding': 'utf-8',
                'status': 'collected'
            }
        ]
        
        processed_chunks = self.processor.process(collected_docs)
        
        # Should create chunks for both documents
        self.assertEqual(len(processed_chunks), 2)
        
        # Check that both documents are represented
        paths = [chunk.source_document_path for chunk in processed_chunks]
        self.assertIn('/test/file1.txt', paths)
        self.assertIn('/test/file2.md', paths)
    
    def test_process_with_unsupported_content_type(self):
        """Test processing documents with unsupported content types."""
        collected_docs = [
            {
                'path': '/test/file.pdf',
                'source_type': 'local_file',
                'content_type': 'application/pdf',  # Not in supported list
                'raw_content': b'PDF content',
                'encoding': 'utf-8',
                'status': 'collected'
            }
        ]
        
        processed_chunks = self.processor.process(collected_docs)
        
        # Should skip unsupported content type
        self.assertEqual(len(processed_chunks), 0)
    
    def test_process_with_invalid_document(self):
        """Test processing invalid documents."""
        collected_docs = [
            {
                'path': '/test/file.txt',
                'source_type': 'local_file',
                'content_type': 'text/plain',
                # Missing required fields
                'status': 'failed'  # Not collected
            }
        ]
        
        processed_chunks = self.processor.process(collected_docs)
        
        # Should skip invalid document
        self.assertEqual(len(processed_chunks), 0)
    
    def test_convert_to_text(self):
        """Test the convert_to_text method."""
        collected_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'content_type': 'text/plain',
            'raw_content': b'Hello World!',
            'encoding': 'utf-8',
            'status': 'collected'
        }
        
        text = self.processor.convert_to_text(collected_doc)
        self.assertEqual(text, "Hello World!")
    
    def test_clean_text(self):
        """Test the clean_text method."""
        dirty_text = "  This  has   extra  \n\n\n  spaces and\r\nline breaks.  "
        clean_text = self.processor.clean_text(dirty_text)
        
        # Should preserve meaningful newlines but clean up excessive ones
        self.assertIn("This has extra", clean_text)
        self.assertIn("line breaks", clean_text)
        # Should not have excessive whitespace
        self.assertNotIn("  ", clean_text)
        # Should normalize line endings
        self.assertNotIn("\r", clean_text)
    
    def test_chunk_text_single_chunk(self):
        """Test chunking text that fits in a single chunk."""
        collected_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'content_type': 'text/plain',
            'raw_content': b'Short content',
            'encoding': 'utf-8',
            'status': 'collected'
        }
        
        chunks = self.processor.chunk_text("Short content", collected_doc)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].chunk_index, 0)
        self.assertEqual(chunks[0].total_chunks, 1)
        self.assertEqual(chunks[0].content, "Short content")
        self.assertIsNotNone(chunks[0].chunk_id)
    
    def test_chunk_text_multiple_chunks(self):
        """Test chunking text that requires multiple chunks."""
        # Create content that will require multiple chunks
        long_content = "A" * 250  # 250 characters with chunk_size=100, overlap=20
        
        collected_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'content_type': 'text/plain',
            'raw_content': b'A' * 250,
            'encoding': 'utf-8',
            'status': 'collected'
        }
        
        chunks = self.processor.chunk_text(long_content, collected_doc)
        
        # Should create multiple chunks
        self.assertGreater(len(chunks), 1)
        
        # Check chunk properties
        for i, chunk in enumerate(chunks):
            self.assertEqual(chunk.chunk_index, i)
            self.assertEqual(chunk.total_chunks, len(chunks))
            self.assertIsNotNone(chunk.chunk_id)
            # Check for overlap (except first chunk)
            if i > 0:
                self.assertTrue(len(chunk.content) > 0)
    
    def test_generate_chunk_id(self):
        """Test the generate_chunk_id method."""
        collected_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file'
        }
        
        chunk_id1 = self.processor.generate_chunk_id(collected_doc, 0, "content1")
        chunk_id2 = self.processor.generate_chunk_id(collected_doc, 1, "content2")
        
        # Should generate different IDs for different chunks
        self.assertNotEqual(chunk_id1, chunk_id2)
        # Should be consistent for same inputs
        chunk_id1_again = self.processor.generate_chunk_id(collected_doc, 0, "content1")
        self.assertEqual(chunk_id1, chunk_id1_again)
        # Should be 32 character hex string (MD5 hash)
        self.assertEqual(len(chunk_id1), 32)
    
    def test_validate_collected_document(self):
        """Test the validate_collected_document method."""
        # Valid document
        valid_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'content_type': 'text/plain',
            'raw_content': b'test content',
            'encoding': 'utf-8',
            'status': 'collected'
        }
        self.assertTrue(self.processor.validate_collected_document(valid_doc))
        
        # Invalid document (missing fields)
        invalid_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file'
            # Missing content_type, raw_content, status
        }
        self.assertFalse(self.processor.validate_collected_document(invalid_doc))
        
        # Document with failed collection
        failed_doc = {
            'path': '/test/file.txt',
            'source_type': 'local_file',
            'content_type': 'text/plain',
            'raw_content': b'test content',
            'encoding': 'utf-8',
            'status': 'failed'  # Not collected
        }
        self.assertFalse(self.processor.validate_collected_document(failed_doc))
        
        # Document with unsupported content type
        unsupported_doc = {
            'path': '/test/file.pdf',
            'source_type': 'local_file',
            'content_type': 'application/pdf',  # Not in supported list
            'raw_content': b'PDF content',
            'encoding': 'utf-8',
            'status': 'collected'
        }
        self.assertFalse(self.processor.validate_collected_document(unsupported_doc))


if __name__ == '__main__':
    unittest.main()