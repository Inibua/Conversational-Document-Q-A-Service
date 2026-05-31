"""
Qdrant Vector Store Implementation

This module provides a concrete implementation of the VectorStore interface
using Qdrant as the vector database.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, Filter, FieldCondition, MatchValue
import uuid
from .base import VectorStore


class QdrantVectorStore(VectorStore):
    """
    Qdrant implementation of the VectorStore interface.
    
    This class provides concrete implementations for all required vector store operations
    using Qdrant as the backend vector database.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Qdrant vector store.
        
        Args:
            config: Configuration dictionary containing:
                   - embedding_model: The embedding model to use
                   - qdrant_host: Qdrant server host (default: localhost)
                   - qdrant_port: Qdrant server port (default: 6333)
                   - collection_name: Name of the Qdrant collection
                   - vector_size: Size of the embedding vectors
        """
        super().__init__(config)
        
        # Extract Qdrant-specific configuration
        self.host = config.get('qdrant_host', 'localhost')
        self.port = config.get('qdrant_port', 6333)
        self.collection_name = config.get('collection_name', 'documents')
        self.vector_size = config.get('vector_size', 768)  # Default for many embedding models
        
        # Initialize Qdrant client
        self.client = QdrantClient(host=self.host, port=self.port)
        
        # Initialize collection if it doesn't exist
        self._init_collection()
        
        self.logger.info(f"QdrantVectorStore initialized with collection: {self.collection_name}")
    
    def _init_collection(self):
        """Initialize the Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
                )
                self.logger.info(f"Created new collection: {self.collection_name}")
            else:
                self.logger.info(f"Using existing collection: {self.collection_name}")
                
        except Exception as e:
            self.logger.error(f"Error initializing collection: {e}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed a piece of text using the configured embedding algorithm.
        
        For this implementation, we'll assume the embedding is done externally
        and this method is a placeholder. In a real implementation, this would
        call the actual embedding model.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        self.logger.debug(f"Embedding text: {text[:50]}...")
        
        # Placeholder implementation - in a real scenario, this would call
        # the actual embedding model (e.g., SentenceTransformer, OpenAI, etc.)
        # For now, we return a dummy vector of the correct size
        # In practice, you would use self.embedding_model.encode(text)
        
        # This is where you would integrate with your actual embedding model
        # For example, if using sentence-transformers:
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer(self.embedding_model)
        # return model.encode(text).tolist()
        
        self.logger.warning("embed_text is a placeholder - implement with actual embedding model")
        return [0.0] * self.vector_size  # Dummy vector
    
    def insert_entry(self, 
                    vectors: List[List[float]], 
                    metadata: List[Dict[str, Any]], 
                    ids: Optional[List[str]] = None) -> List[str]:
        """
        Insert embeddings and metadata into the Qdrant vector database.
        
        Args:
            vectors: List of embedding vectors
            metadata: List of metadata dictionaries corresponding to vectors
            ids: Optional list of IDs for the entries
            
        Returns:
            List of generated or provided IDs for the inserted entries
        """
        if len(vectors) != len(metadata):
            raise ValueError("Vectors and metadata lists must have the same length")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]
        elif len(ids) != len(vectors):
            raise ValueError("IDs list must have the same length as vectors list")
        
        # Create point structures for Qdrant
        points = []
        for i, (vector, meta, point_id) in enumerate(zip(vectors, metadata, ids)):
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=meta
            )
            points.append(point)
        
        try:
            # Insert points into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            self.logger.info(f"Inserted {len(points)} entries into collection: {self.collection_name}")
            return ids
            
        except Exception as e:
            self.logger.error(f"Error inserting entries: {e}")
            raise
    
    def retrieve_lexical(self, 
                        query: str, 
                        limit: int = 10,
                        filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform lexical retrieval (keyword search) using Qdrant.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search
            
        Returns:
            List of retrieved results with metadata
        """
        self.logger.debug(f"Performing lexical search for query: {query}")
        
        try:
            # For lexical search, we can use Qdrant's full-text search capability
            # This would typically involve searching in text fields of the payload
            # For now, we'll do a simple search across all text fields
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                scroll_filter=self._build_filter(filters) if filters else None
            )
            
            # Extract results
            results = []
            for point in search_result[0]:  # search_result[0] contains the points
                result = {
                    'id': point.id,
                    'payload': point.payload,
                    'score': 1.0  # Lexical search doesn't have similarity scores
                }
                results.append(result)
            
            self.logger.info(f"Lexical search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing lexical search: {e}")
            raise
    
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
            List of retrieved results with metadata and similarity scores
        """
        self.logger.debug(f"Performing semantic search for query: {query}")
        
        try:
            # Embed the query
            query_vector = self.embed_text(query)
            
            # Perform vector search using the current Qdrant API
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,  # Use 'query' parameter for vector search
                limit=limit,
                query_filter=self._build_filter(filters) if filters else None,
                with_payload=True,
                with_vectors=False
            )
            
            # Extract results from the QueryResponse object
            results = []
            for point in search_result.points:
                result = {
                    'id': point.id,
                    'payload': point.payload,
                    'score': point.score
                }
                results.append(result)
            
            self.logger.info(f"Semantic search returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Error performing semantic search: {e}")
            raise
    
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
            rerank: Whether to rerank results (simple implementation)
            
        Returns:
            List of retrieved results with metadata and scores
        """
        self.logger.debug(f"Performing hybrid search for query: {query}")
        
        try:
            # Get semantic results
            semantic_results = self.retrieve_semantic(query, limit * 2, filters)
            
            # Get lexical results
            lexical_results = self.retrieve_lexical(query, limit * 2, filters)
            
            # Combine results (simple approach - could be improved with actual reranking)
            combined_results = {}
            
            # Add semantic results with their scores
            for result in semantic_results:
                combined_results[result['id']] = result
                combined_results[result['id']]['semantic_score'] = result['score']
                combined_results[result['id']]['lexical_score'] = 0.0
            
            # Add lexical results
            for result in lexical_results:
                if result['id'] in combined_results:
                    combined_results[result['id']]['lexical_score'] = 1.0
                else:
                    result['semantic_score'] = 0.0
                    result['lexical_score'] = 1.0
                    combined_results[result['id']] = result
            
            # Convert to list and sort by combined score
            results_list = list(combined_results.values())
            if rerank:
                # Simple reranking: combine scores
                for result in results_list:
                    # Normalize scores (assuming semantic scores are between 0-1)
                    semantic_score = result.get('semantic_score', 0.0)
                    lexical_score = result.get('lexical_score', 0.0)
                    result['combined_score'] = (semantic_score + lexical_score) / 2
            
                # Sort by combined score
                results_list.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Limit results
            results_list = results_list[:limit]
            
            self.logger.info(f"Hybrid search returned {len(results_list)} results")
            return results_list
            
        except Exception as e:
            self.logger.error(f"Error performing hybrid search: {e}")
            raise
    
    def _build_filter(self, filters: Dict[str, Any]) -> Filter:
        """
        Build Qdrant filter from dictionary filters.
        
        Args:
            filters: Dictionary of filters to apply
            
        Returns:
            Qdrant Filter object
        """
        must_conditions = []
        
        for key, value in filters.items():
            condition = FieldCondition(
                key=key,
                match=MatchValue(value=value)
            )
            must_conditions.append(condition)
        
        return Filter(must=[must_conditions]) if must_conditions else None