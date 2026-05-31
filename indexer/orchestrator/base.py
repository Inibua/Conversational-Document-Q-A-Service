"""
Base Orchestrator class.

The Orchestrator configures the other four components and calls them in order:
1. Discoverer, 2. Collector, 3. Processor, 4. Storer
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging


class Orchestrator(ABC):
    """
    Abstract base class for Orchestrator.
    
    The Orchestrator coordinates the Discoverer, Collector, Processor, and Storer
    components to implement the document indexing workflow.
    """
    
    def __init__(self, config: Dict, db_session=None, vector_store=None):
        """
        Initialize the orchestrator.
        
        Args:
            config: Configuration dictionary for all components
            db_session: SQLAlchemy database session (optional, required for some implementations)
            vector_store: Vector store instance (optional, required for storer)
        """
        self.config = config
        self.db_session = db_session
        self.vector_store = vector_store
        self.logger = logging.getLogger(__name__)
        
        # Configure logging to exclude PII and confidential information
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def run(self) -> bool:
        """
        Run the complete indexing pipeline.
        
        Returns:
            True if the pipeline executed successfully, False otherwise
        """
        pass
    
    def _create_components(self):
        """
        Create and configure all components (discoverer, collector, processor, storer).
        
        Returns:
            Tuple of (discoverer, collector, processor, storer) instances
        """
        # This should be implemented by child classes based on their needs
        pass
    
    def _convert_discoverer_to_collector_format(self, documents: List[Dict]) -> List[Dict]:
        """
        Convert discovered documents to format expected by collector.
        
        Args:
            documents: List of document metadata from discoverer
            
        Returns:
            List of document metadata formatted for collector
        """
        return [
            {
                'path': doc.path,
                'source_type': doc.source_type,
                'metadata': {'discovered_at': str(doc.modified_time)},
                'status': doc.status
            }
            for doc in documents
        ]
    
    def _convert_collector_to_processor_format(self, collected_docs: List[Dict]) -> List[Dict]:
        """
        Convert collected documents to format expected by processor.
        
        Args:
            collected_docs: List of collected documents from collector
            
        Returns:
            List of collected documents formatted for processor
        """
        result = []
        for doc in collected_docs:
            if hasattr(doc, 'status') and doc.status.value == 'collected':
                result.append({
                    'path': doc.path,
                    'source_type': doc.source_type,
                    'content_type': doc.content_type,
                    'raw_content': doc.raw_content,
                    'encoding': doc.encoding,
                    'status': doc.status.value
                })
        return result
    
    def _convert_processor_to_storer_format(self, processed_chunks: List[Dict]) -> List[Dict]:
        """
        Convert processed chunks to format expected by storer.
        
        Args:
            processed_chunks: List of processed chunks from processor
            
        Returns:
            List of processed chunks formatted for storer
        """
        result = []
        for chunk in processed_chunks:
            if hasattr(chunk, 'status') and chunk.status.value == 'processed':
                result.append({
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'status': chunk.status.value,
                    'source_document_path': chunk.source_document_path,
                    'source_type': chunk.source_type,
                    'content_type': chunk.content_type,
                    'chunk_index': chunk.chunk_index,
                    'total_chunks': chunk.total_chunks,
                    'processed_at': chunk.processed_at.isoformat() if chunk.processed_at else None,
                    'chunk_id': chunk.chunk_id
                })
        return result
    
    def _log_pipeline_step(self, step_name: str, results: list, success_count: int) -> None:
        """
        Log information about a pipeline step.
        
        Args:
            step_name: Name of the step (e.g., "Discovery")
            results: List of results from the step
            success_count: Number of successful results
        """
        self.logger.info(f"=== Step {step_name} ===-")
        self.logger.info(f"{step_name} completed: {success_count}/{len(results)} successful.")
        
        # Log any failures - handle different status formats (Enum vs string)
        failures = []
        for r in results:
            if not hasattr(r, 'status'):
                failures.append(r)
            elif hasattr(r, 'status') and hasattr(r.status, 'value'):  # Enum status
                if r.status.value not in ['collected', 'processed', 'stored', 'pending']:
                    failures.append(r)
            elif hasattr(r, 'status'):  # String status
                if r.status not in ['collected', 'processed', 'stored', 'pending']:
                    failures.append(r)
        
        if failures:
            self.logger.warning(f"{step_name} had {len(failures)} failures.")
