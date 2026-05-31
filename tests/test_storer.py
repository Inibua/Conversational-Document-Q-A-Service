"""
Test cases for the Storer components.

This module contains unit tests for the base Storer and QdrantStorer implementations.
"""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add project root to path
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from indexer.storer import QdrantStorer
from vector_store.qdrant_vector_store import QdrantVectorStore


class TestQdrantStorer(unittest.TestCase):
    """Test cases for QdrantStorer."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock vector store
        self.mock_vector_store = MagicMock(spec=QdrantVectorStore)
        
        # Configure mock vector store
        self.mock_vector_store.embed_text.return_value = [0.1, 0.2, 0.3]  # Dummy embedding
        
        # Make insert_entry return IDs based on the number of vectors
        def mock_insert_entry(vectors, metadata, ids=None):
            return [f'id{i}' for i in range(len(vectors))]
        
        self.mock_vector_store.insert_entry.side_effect = mock_insert_entry
        
        # Storer configuration
        self.config = {
            'embedding_model': 'test-model',
            'collection_name': 'test_collection'
        }
        
        # Create storer instance
        self.storer = QdrantStorer(self.config, self.mock_vector_store)
    
    def test_initialize_storer(self):
        """Test that storer initializes correctly."""
        self.assertEqual(self.storer.collection_name, 'test_collection')
        self.assertIsNotNone(self.storer.logger)
    
    def test_store_empty_chunks(self):
        """Test storing empty list of chunks."""
        result = self.storer.store([])
        self.assertEqual(result, [])
        self.mock_vector_store.embed_text.assert_not_called()
        self.mock_vector_store.insert_entry.assert_not_called()
    
    def test_store_valid_chunks(self):
        """Test storing valid processed chunks."""
        # Create test chunks
        test_chunks = [
            {
                'content': 'This is test content 1',
                'metadata': {'source': 'test1.txt'},
                'status': 'processed',
                'source_document_path': 'test1.txt',
                'source_type': 'file',
                'content_type': 'text/plain',
                'chunk_index': 0,
                'total_chunks': 1,
                'processed_at': datetime.now().isoformat()
            },
            {
                'content': 'This is test content 2',
                'metadata': {'source': 'test2.txt'},
                'status': 'processed',
                'source_document_path': 'test2.txt',
                'source_type': 'file',
                'content_type': 'text/plain',
                'chunk_index': 0,
                'total_chunks': 1,
                'processed_at': datetime.now().isoformat()
            }
        ]
        
        # Store chunks
        result = self.storer.store(test_chunks)
        
        # Verify results
        self.assertEqual(len(result), 2)
        self.assertEqual(result, ['id0', 'id1'])
        
        # Verify embed_text was called for each chunk
        self.mock_vector_store.embed_text.assert_any_call('This is test content 1')
        self.mock_vector_store.embed_text.assert_any_call('This is test content 2')
        
        # Verify insert_entry was called with correct parameters
        self.mock_vector_store.insert_entry.assert_called_once()
        call_args = self.mock_vector_store.insert_entry.call_args
        
        # Check vectors parameter
        vectors = call_args[0][0]
        self.assertEqual(len(vectors), 2)
        self.assertEqual(vectors[0], [0.1, 0.2, 0.3])
        self.assertEqual(vectors[1], [0.1, 0.2, 0.3])
        
        # Check metadata parameter
        metadata_list = call_args[0][1]
        self.assertEqual(len(metadata_list), 2)
        self.assertIn('source_document_path', metadata_list[0])
        self.assertIn('source_type', metadata_list[0])
        self.assertIn('chunk_index', metadata_list[0])
    
    def test_store_invalid_chunks(self):
        """Test that invalid chunks are filtered out."""
        # Create test chunks with some invalid ones
        test_chunks = [
            {
                'content': 'Valid content',
                'metadata': {},
                'status': 'processed',
                'source_document_path': 'valid.txt'
            },
            {
                'content': '',  # Invalid: empty content
                'metadata': {},
                'status': 'processed',
                'source_document_path': 'invalid1.txt'
            },
            {
                'content': 'Missing status field',
                'metadata': {},
                'source_document_path': 'invalid3.txt'
            }
        ]
        
        # Store chunks
        result = self.storer.store(test_chunks)
        
        # Should only store the valid chunk
        self.assertEqual(len(result), 1)
        self.mock_vector_store.embed_text.assert_called_once_with('Valid content')
    
    def test_prepare_chunk_metadata(self):
        """Test metadata preparation for chunks."""
        # Create test chunk
        test_chunk = {
            'content': 'Test content',
            'metadata': {'custom_field': 'custom_value'},
            'status': 'processed',
            'source_document_path': 'test.txt',
            'source_type': 'file',
            'content_type': 'text/plain',
            'chunk_index': 1,
            'total_chunks': 3,
            'processed_at': datetime.now().isoformat()
        }
        
        # Prepare metadata
        metadata = self.storer._prepare_chunk_metadata(test_chunk)
        
        # Verify metadata contains expected fields
        self.assertEqual(metadata['source_document_path'], 'test.txt')
        self.assertEqual(metadata['source_type'], 'file')
        self.assertEqual(metadata['content_type'], 'text/plain')
        self.assertEqual(metadata['chunk_index'], 1)
        self.assertEqual(metadata['total_chunks'], 3)
        self.assertEqual(metadata['custom_field'], 'custom_value')
        self.assertEqual(metadata['chunk_size'], len('Test content'))
    
    def test_validate_processed_chunk(self):
        """Test chunk validation."""
        # Valid chunk
        valid_chunk = {
            'content': 'Valid content',
            'metadata': {},
            'status': 'processed'
        }
        self.assertTrue(self.storer.validate_processed_chunk(valid_chunk))
        
        # Invalid: empty content
        invalid_chunk1 = {
            'content': '',
            'metadata': {},
            'status': 'processed'
        }
        self.assertFalse(self.storer.validate_processed_chunk(invalid_chunk1))
        
        # Invalid: wrong status
        invalid_chunk2 = {
            'content': 'Content',
            'metadata': {},
            'status': 'failed'
        }
        self.assertFalse(self.storer.validate_processed_chunk(invalid_chunk2))
        
        # Invalid: missing required field
        invalid_chunk3 = {
            'content': 'Content',
            'status': 'processed'
            # Missing 'metadata' field
        }
        self.assertFalse(self.storer.validate_processed_chunk(invalid_chunk3))


if __name__ == '__main__':
    unittest.main()