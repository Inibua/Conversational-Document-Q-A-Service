"""
Full Orchestrator example.

This demonstrates the complete indexing pipeline including the Storer component.
"""
import os
import sys
from unittest.mock import MagicMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from indexer.discoverer import LocalFileDiscoverer
from indexer.collector import LocalFileCollector, CollectionStatus
from indexer.processor import DocumentProcessor, ProcessingStatus
from indexer.storer import QdrantStorer
from vector_store.qdrant_vector_store import QdrantVectorStore


class FullOrchestrator:
    """
    A complete orchestrator that coordinates all components of the indexing pipeline.
    
    This orchestrator manages the Discoverer, Collector, Processor, and Storer components
    to implement the full document indexing workflow.
    """
    
    def __init__(self, config):
        """Initialize the orchestrator with configuration."""
        self.config = config
        self.db_session = MagicMock()  # In real app, this would be a SQLAlchemy session
    
    def run(self):
        """Run the complete indexing pipeline."""
        print("Starting complete indexing pipeline...")
        print()
        
        # Step 1: Discovery
        print("=== Step 1: Discovery ===")
        discoverer = self._create_discoverer()
        documents = discoverer.discover()
        print(f"Discovered {len(documents)} documents for processing.")
        print()
        
        # Convert to metadata list for collector
        document_metadata_list = [
            {
                'path': doc.path,
                'source_type': doc.source_type,
                'metadata': {'discovered_at': str(doc.modified_time)}
            }
            for doc in documents
        ]
        
        # Step 2: Collection
        print("=== Step 2: Collection ===")
        collector = self._create_collector()
        collected_docs = collector.collect(document_metadata_list)
        successful = sum(1 for doc in collected_docs if doc.status == CollectionStatus.COLLECTED)
        print(f"Successfully collected {successful}/{len(collected_docs)} documents.")
        print()
        
        # Step 3: Processing
        print("=== Step 3: Processing ===")
        processor = self._create_processor()
        
        # Convert collected documents to format expected by processor
        collected_docs_for_processing = []
        for doc in collected_docs:
            if doc.status == CollectionStatus.COLLECTED:
                collected_doc = {
                    'path': doc.path,
                    'source_type': doc.source_type,
                    'content_type': doc.content_type,
                    'raw_content': doc.raw_content,
                    'encoding': doc.encoding,
                    'status': doc.status.value
                }
                collected_docs_for_processing.append(collected_doc)
        
        processed_chunks = processor.process(collected_docs_for_processing)
        successful_chunks = sum(1 for chunk in processed_chunks if chunk.status == ProcessingStatus.PROCESSED)
        print(f"Successfully processed {successful_chunks}/{len(processed_chunks)} chunks.")
        print()
        
        # Step 4: Storage
        print("=== Step 4: Storage ===")
        storer = self._create_storer()
        
        # Convert processed chunks to format expected by storer
        processed_chunks_for_storage = []
        for chunk in processed_chunks:
            if chunk.status == ProcessingStatus.PROCESSED:
                chunk_data = {
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
                }
                processed_chunks_for_storage.append(chunk_data)
        
        stored_ids = storer.store(processed_chunks_for_storage)
        print(f"Successfully stored {len(stored_ids)} chunks in vector database.")
        print()
        
        print("Complete pipeline executed successfully!")
    
    def _create_discoverer(self):
        """Create and configure the discoverer."""
        discoverer_config = {
            'root_path': self.config.get('discoverer', {}).get('root_path', 'data_to_ingest'),
            'file_extensions': self.config.get('discoverer', {}).get('file_extensions', ['.txt', '.md', '.pdf', '.docx']),
            'exclude_patterns': self.config.get('discoverer', {}).get('exclude_patterns', ['.git', '__pycache__'])
        }
        
        return LocalFileDiscoverer(discoverer_config, self.db_session)
    
    def _create_collector(self):
        """Create and configure the collector."""
        collector_config = {
            'max_file_size': self.config.get('collector', {}).get('max_file_size', 10 * 1024 * 1024),
            'supported_mime_types': self.config.get('collector', {}).get('supported_mime_types', [
                'text/plain', 'text/markdown', 'application/pdf'
            ])
        }
        
        return LocalFileCollector(collector_config, self.db_session)
    
    def _create_processor(self):
        """Create and configure the processor."""
        processor_config = {
            'chunk_size': self.config.get('processor', {}).get('chunk_size', 1000),
            'chunk_overlap': self.config.get('processor', {}).get('chunk_overlap', 200),
            'supported_content_types': self.config.get('processor', {}).get('supported_content_types', [
                'text/plain', 'text/markdown', 'application/pdf'
            ])
        }
        
        return DocumentProcessor(processor_config, self.db_session)
    
    def _create_storer(self):
        """Create and configure the storer."""
        # Create vector store first
        vector_store_config = {
            'embedding_model': self.config.get('storer', {}).get('embedding_model', 'all-MiniLM-L6-v2'),
            'qdrant_host': self.config.get('storer', {}).get('qdrant_host', 'localhost'),
            'qdrant_port': self.config.get('storer', {}).get('qdrant_port', 6333),
            'collection_name': self.config.get('storer', {}).get('collection_name', 'documents'),
            'vector_size': self.config.get('storer', {}).get('vector_size', 768)
        }
        
        vector_store = QdrantVectorStore(vector_store_config)
        
        # Create storer
        storer_config = {
            'embedding_model': vector_store_config['embedding_model'],
            'collection_name': vector_store_config['collection_name']
        }
        
        return QdrantStorer(storer_config, vector_store)


def main():
    """Main function to demonstrate the complete orchestrator."""
    
    # Configuration for the orchestrator
    config = {
        'discoverer': {
            'root_path': 'data_to_ingest',
            'file_extensions': ['.txt', '.md', '.pdf', '.docx'],
            'exclude_patterns': ['.git', '__pycache__', '.venv']
        },
        'collector': {
            'max_file_size': 10 * 1024 * 1024,  # 10MB
            'supported_mime_types': ['text/plain', 'text/markdown', 'application/pdf']
        },
        'processor': {
            'chunk_size': 1000,
            'chunk_overlap': 200,
            'supported_content_types': ['text/plain', 'text/markdown', 'application/pdf']
        },
        'storer': {
            'embedding_model': 'all-MiniLM-L6-v2',
            'qdrant_host': 'localhost',
            'qdrant_port': 6333,
            'collection_name': 'documents',
            'vector_size': 768
        }
    }
    
    try:
        orchestrator = FullOrchestrator(config)
        orchestrator.run()
        return 0
    except Exception as e:
        print(f"Error running orchestrator: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())