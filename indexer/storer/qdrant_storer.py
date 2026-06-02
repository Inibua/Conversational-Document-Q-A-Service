"""
Qdrant Storer implementation.

The QdrantStorer stores processed document chunks in a Qdrant vector database.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from .base import Storer


class QdrantStorer(Storer):
    """
    Qdrant implementation of the Storer interface.
    
    This class provides concrete implementations for storing processed chunks
    in a Qdrant vector database.
    """
    
    def __init__(self, config: Dict, vector_store):
        """
        Initialize the Qdrant storer.
        
        Args:
            config: Configuration dictionary containing:
                   - embedding_model: The embedding model to use
                   - collection_name: Name of the Qdrant collection
            vector_store: Qdrant vector store instance
        """
        super().__init__(config, vector_store)
        self.collection_name = config.get('collection_name', 'documents')
        self.logger = logging.getLogger(f"{__name__}.QdrantStorer")
    
    def store(self, processed_chunks: List[Dict]) -> List[str]:
        """
        Store processed chunks in the Qdrant vector database.
        
        Args:
            processed_chunks: List of processed chunks to store
            
        Returns:
            List of generated IDs for the stored entries
        """
        if not processed_chunks:
            self.logger.info("No processed chunks to store")
            return []
        
        self.logger.info(f"Starting storage of {len(processed_chunks)} processed chunks")
        
        # Validate all chunks first
        valid_chunks = []
        for chunk in processed_chunks:
            if self.validate_processed_chunk(chunk):
                valid_chunks.append(chunk)
            else:
                self.logger.warning(f"Skipping invalid chunk from: {chunk.get('source_document_path', 'unknown')}")
        
        if not valid_chunks:
            self.logger.warning("No valid chunks to store")
            return []
        
        # Prepare data for vector store
        vectors = []
        metadata_list = []
        ids = []
        
        for chunk in valid_chunks:
            try:
                # Generate embedding for the chunk content
                # In a real implementation, this would use the actual embedding model
                # For now, we'll use the vector store's embed_text method as placeholder
                vector = self.vector_store.embed_text(chunk['content'])
                
                # Prepare metadata
                chunk_metadata = self._prepare_chunk_metadata(chunk)
                
                # Generate or use existing ID
                chunk_id = chunk.get('chunk_id')
                if not chunk_id:
                    chunk_id = str(uuid.uuid4())
                
                vectors.append(vector)
                metadata_list.append(chunk_metadata)
                ids.append(chunk_id)
                
                self.logger.debug(f"Prepared chunk {chunk_id} for storage")
                
            except Exception as e:
                self.logger.error(f"Error preparing chunk for storage: {str(e)}")
                continue
        
        if not vectors:
            self.logger.warning("No valid vectors to store")
            return []
        
        # Store in vector database
        try:
            stored_ids = self.vector_store.insert_entry(vectors, metadata_list, ids)
            self.logger.info(f"Successfully stored {len(stored_ids)} chunks in Qdrant")
            return stored_ids
            
        except Exception as e:
            self.logger.error(f"Error storing chunks in vector database: {str(e)}")
            raise
    
    def _prepare_chunk_metadata(self, processed_chunk: Dict) -> Dict[str, Any]:
        """
        Prepare metadata for a processed chunk for storage in vector database.
        
        Args:
            processed_chunk: Processed chunk data
            
        Returns:
            Dictionary of metadata suitable for vector storage
        """
        metadata = {
            'source_document_path': processed_chunk.get('source_document_path', ''),
            'source_type': processed_chunk.get('source_type', ''),
            'content_type': processed_chunk.get('content_type', 'text/markdown'),
            'chunk_index': processed_chunk.get('chunk_index', 0),
            'total_chunks': processed_chunk.get('total_chunks', 1),
            'processed_at': processed_chunk.get('processed_at', datetime.now().isoformat()),
            'status': processed_chunk.get('status', 'processed'),
            'chunk_size': len(processed_chunk.get('content', '')),
            'content': processed_chunk.get('content', '')
        }
        
        # Add any additional metadata from the chunk
        if 'metadata' in processed_chunk and processed_chunk['metadata']:
            metadata.update(processed_chunk['metadata'])
        
        # Redact sensitive information if needed
        # This is a placeholder for future PII redaction
        metadata = self._redact_sensitive_info(metadata)
        
        return metadata
    
    def _redact_sensitive_info(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact sensitive information from metadata.
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Metadata with sensitive information redacted
        """
        # This is a placeholder for future implementation
        # In a real implementation, this would identify and redact PII
        # For now, we'll just return the metadata as-is
        
        # Example of what could be done:
        # sensitive_fields = ['email', 'phone', 'ssn', 'credit_card']
        # for field in sensitive_fields:
        #     if field in metadata:
        #         metadata[field] = '[REDACTED]'
        
        return metadata