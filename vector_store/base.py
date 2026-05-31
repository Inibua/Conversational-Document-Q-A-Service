"""
Vector Store Interface Module

This module defines the base VectorStore interface that all concrete
vector store implementations must inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import logging


class VectorStore(ABC):
    """
    Abstract base class for all vector store implementations.
    
    This interface defines the contract that all concrete vector store
    implementations must follow.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the vector store with configuration.
        
        Args:
            config: Configuration dictionary containing embedding model
                   and other store-specific settings
        """
        self.config = config
        self.embedding_model = config.get('embedding_model')
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a piece of text using the configured embedding algorithm.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
    
    @abstractmethod
    def insert_entry(self, 
                    vectors: List[List[float]], 
                    metadata: List[Dict[str, Any]], 
                    ids: Optional[List[str]] = None) -> List[str]:
        """
        Insert embeddings and metadata into the vector database.
        
        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dictionaries corresponding to vectors
            ids: Optional list of IDs for the entries
            
        Returns:
            List of generated or provided IDs for the inserted entries
        """
        pass
    
    @abstractmethod
    def retrieve_lexical(self, 
                        query: str, 
                        limit: int = 10,
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform lexical retrieval (e.g., by keyword search).
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search
            
        Returns:
            List of retrieved results with metadata
        """
        pass
    
    @abstractmethod
    def retrieve_semantic(self, 
                         query: str, 
                         limit: int = 10,
                         filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic retrieval using cosine similarity on vectors.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search
            
        Returns:
            List of retrieved results with metadata
        """
        pass
    
    @abstractmethod
    def retrieve_hybrid(self, 
                       query: str, 
                       limit: int = 10,
                       filters: Optional[Dict[str, Any]] = None,
                       rerank: bool = True) -> List[Dict[str, Any]]:
        """
        Perform hybrid retrieval combining semantic and lexical search.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search
            rerank: Whether to rerank results (if supported)
            
        Returns:
            List of retrieved results with metadata
        """
        pass