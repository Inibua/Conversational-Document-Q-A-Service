"""
Basic Orchestrator implementation.

A simple orchestrator that coordinates all components of the indexing pipeline:
Discoverer, Collector, Processor, and Storer.
"""
from typing import Dict, Optional
from indexer.discoverer.base import Discoverer
from indexer.collector.base import Collector
from indexer.processor.base import Processor
from indexer.storer.base import Storer
from indexer.orchestrator.base import Orchestrator
from paths import ROOT_DIR


class BasicOrchestrator(Orchestrator):
    """
    A basic implementation of the indexing orchestrator pipeline.
    
    This orchestrator manages the Discoverer, Collector, Processor, and Storer components
    to implement the full document indexing workflow.
    """
    
    def __init__(self, config: Dict, db_session=None, vector_store=None):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config: Configuration dictionary for all components
            db_session: SQLAlchemy database session (optional)
            vector_store: Vector store instance (optional, required for storage)
        """
        super().__init__(config, db_session, vector_store)
    
    def run(self) -> bool:
        """
        Run the complete indexing pipeline.
        
        Returns:
            True if the pipeline executed successfully, False otherwise
        """
        self.logger.info("Starting indexing pipeline...")
        
        try:
            # Create all components
            discoverer, collector, processor, storer = self._create_components()
            
            # Step 1: Discovery
            self.logger.info("=== Step 1: Discovery ===")
            discovered_docs = discoverer.discover()
            self._log_pipeline_step("Discovery", discovered_docs, len(discovered_docs))
            
            # Convert documents for collector
            documents_for_collection = self._convert_discoverer_to_collector_format(discovered_docs)
            
            # Step 2: Collection
            if documents_for_collection:
                self.logger.info("=== Step 2: Collection ===")
                collected_docs = collector.collect(documents_for_collection)
                successful_collections = sum(1 for doc in collected_docs if 
                                           hasattr(doc, 'status') and doc.status.value == 'collected')
                self._log_pipeline_step("Collection", collected_docs, successful_collections)
            else:
                self.logger.info("No documents to collect.")
                collected_docs = []
            
            # Step 3: Processing
            if collected_docs and successful_collections > 0:
                self.logger.info("=== Step 3: Processing ===")
                collected_docs_for_processing = self._convert_collector_to_processor_format(collected_docs)
                processed_chunks = processor.process(collected_docs_for_processing)
                successful_processing = sum(1 for chunk in processed_chunks if 
                                           hasattr(chunk, 'status') and chunk.status.value == 'processed')
                self._log_pipeline_step("Processing", processed_chunks, successful_processing)
            else:
                self.logger.info("No documents to process.")
                processed_chunks = []
            
            # Step 4: Storage
            if processed_chunks and successful_processing > 0:
                self.logger.info("=== Step 4: Storage ===")
                chunks_for_storage = self._convert_processor_to_storer_format(processed_chunks)
                stored_ids = storer.store(chunks_for_storage)
                self._log_pipeline_step("Storage", chunks_for_storage, len(stored_ids))
                
                # Log storage successes
                self.logger.info(f"Successfully stored {len(stored_ids)} chunks in vector database.")
            else:
                self.logger.info("No chunks to store.")
            
            self.logger.info("Indexing pipeline completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in indexing pipeline: {str(e)}")
            self.logger.exception("Pipeline error details:")
            return False
    
    def _create_components(self):
        """
        Create and configure all components.
        
        Returns:
            Tuple of (discoverer, collector, processor, storer) instances
        """
        # Import components here to avoid circular imports
        from indexer.discoverer import LocalFileDiscoverer
        from indexer.collector import LocalFileCollector
        from indexer.processor import DocumentProcessor
        from indexer.storer import QdrantStorer
        from vector_store.qdrant_vector_store import QdrantVectorStore
        
        # Create vector store
        if self.vector_store is None:
            vector_store_config = {
                'embedding_model': self.config.get('storer', {}).get('embedding_model', 'all-MiniLM-L6-v2'),
                'qdrant_host': self.config.get('storer', {}).get('qdrant_host', 'localhost'),
                'qdrant_port': self.config.get('storer', {}).get('qdrant_port', 6333),
                'collection_name': self.config.get('storer', {}).get('collection_name', 'documents'),
                'vector_size': self.config.get('storer', {}).get('vector_size', 384)
            }
            self.vector_store = QdrantVectorStore(vector_store_config)
        
        # Create discoverer
        discoverer_config = {
            'root_path': self.config.get('discoverer', {}).get('root_path', f'{ROOT_DIR}/data_to_ingest'),
            'file_extensions': self.config.get('discoverer', {}).get('file_extensions', ['.md']),
            'exclude_patterns': self.config.get('discoverer', {}).get('exclude_patterns', ['.git', '__pycache__']),
            'db_session': self.db_session
        }
        discoverer = LocalFileDiscoverer(discoverer_config, self.db_session)
        
        # Create collector
        collector_config = {
            'max_file_size': self.config.get('collector', {}).get('max_file_size', 10 * 1024 * 1024),
            'supported_mime_types': self.config.get('collector', {}).get('supported_mime_types', [
                'text/plain', 'text/markdown', 'application/pdf'
            ]),
            'db_session': self.db_session
        }
        collector = LocalFileCollector(collector_config, self.db_session)
        
        # Create processor
        processor_config = {
            'chunk_size': self.config.get('processor', {}).get('chunk_size', 300),
            'chunk_overlap': self.config.get('processor', {}).get('chunk_overlap', 50),
            'supported_content_types': self.config.get('processor', {}).get('supported_content_types', [
                'text/plain', 'text/markdown', 'application/pdf'
            ]),
            'db_session': self.db_session
        }
        processor = DocumentProcessor(processor_config, self.db_session)
        
        # Create storer
        storer_config = {
            'embedding_model': self.config.get('storer', {}).get('embedding_model', 'all-MiniLM-L6-v2'),
            'collection_name': self.config.get('storer', {}).get('collection_name', 'documents')
        }
        storer = QdrantStorer(storer_config, self.vector_store)
        
        return discoverer, collector, processor, storer


def create_orchestrator(config: Optional[Dict] = None, db_session=None, vector_store=None) -> Orchestrator:
    """
    Factory function to create an appropriate orchestrator instance.
    
    Args:
        config: Configuration dictionary
        db_session: Optional database session
        vector_store: Optional vector store instance
        
    Returns:
        An orchestrator instance
    """
    # For now, always return BasicOrchestrator
    # This can be extended to support different orchestrator types
    return BasicOrchestrator(config, db_session, vector_store)


if __name__ == "__main__":
    orch = create_orchestrator({})
    orch.run()
