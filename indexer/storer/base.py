"""
Base Storer class.

The Storer interface/base class states all the functions needed to be implemented.
Each child storer class must implement the methods. Each child contains specific
functionality based on the vector store to use.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging


class Storer(ABC):
    """
    Abstract base class for all storers.
    
    The Storer reads the chunks and metadata from the db. Formats them for the 
    appropriate vector store, then uses a vector store to store in a vector db.
    """
    
    def __init__(self, config: Dict, vector_store):
        """
        Initialize the storer.
        
        Args:
            config: Configuration dictionary for the storer
            vector_store: Vector store instance to use for storing embeddings
        """
        self.config = config
        self.vector_store = vector_store
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def store(self, processed_chunks: List[Dict]) -> List[str]:
        """
        Store processed chunks in the vector database.
        
        Args:
            processed_chunks: List of processed chunks to store
            
        Returns:
            List of generated IDs for the stored entries
        """
        pass
    
    def validate_processed_chunk(self, processed_chunk: Dict) -> bool:
        """
        Validate that a processed chunk can be stored.
        
        Args:
            processed_chunk: Processed chunk data to validate
            
        Returns:
            True if the chunk is valid for storing, False otherwise
        """
        try:
            # Basic validation
            required_fields = ['content', 'metadata', 'status']
            for field in required_fields:
                if field not in processed_chunk:
                    self.logger.warning(f"Processed chunk missing required field: {field}")
                    return False
            
            # Check that content is not empty
            if not processed_chunk['content']:
                self.logger.warning("Processed chunk has no content")
                return False
            
            # Check that processing was successful
            if processed_chunk['status'] != 'processed':
                self.logger.warning(f"Chunk was not successfully processed: {processed_chunk.get('source_document_path', 'unknown')}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating processed chunk: {str(e)}")
            return False