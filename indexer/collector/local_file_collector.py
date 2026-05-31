"""
Local File Collector implementation.

The LocalFileCollector reads raw content from local files and prepares them
for processing in the RAG pipeline.
"""
import os
import logging
from typing import List, Dict
from datetime import datetime
import mimetypes
from .base import Collector, CollectedDocument, CollectionStatus


class LocalFileCollector(Collector):
    """
    Collector implementation for local file systems.
    
    This collector reads raw content from files discovered by the LocalFileDiscoverer
    and prepares them for further processing.
    """
    
    def __init__(self, config: Dict, db_session):
        """
        Initialize the local file collector.
        
        Args:
            config: Configuration dictionary containing:
                   - max_file_size: Maximum file size to collect (in bytes)
                   - supported_mime_types: List of supported MIME types
            db_session: SQLAlchemy database session
        """
        super().__init__(config, db_session)
        self.max_file_size = config.get('max_file_size', 10 * 1024 * 1024)  # Default: 10MB
        self.supported_mime_types = config.get('supported_mime_types', [
            'text/plain', 'text/markdown', 'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ])
        
        self.logger = logging.getLogger(f"{__name__}.LocalFileCollector")
    
    def collect(self, document_metadata_list: List[Dict]) -> List[CollectedDocument]:
        """
        Collect raw content from local files.
        
        Args:
            document_metadata_list: List of document metadata from discoverer
            
        Returns:
            List of CollectedDocument objects with raw content
        """
        collected_documents = []
        
        self.logger.info(f"Starting collection of {len(document_metadata_list)} documents")
        
        for doc_metadata in document_metadata_list:
            try:
                # Validate document before collection
                if not self.validate_document(doc_metadata):
                    self.logger.warning(f"Skipping invalid document: {doc_metadata['path']}")
                    continue
                
                # Check file size limit
                file_size = os.path.getsize(doc_metadata['path'])
                if file_size > self.max_file_size:
                    self.logger.warning(
                        f"Skipping file exceeding size limit ({file_size} > {self.max_file_size}): "
                        f"{doc_metadata['path']}"
                    )
                    continue
                
                # Determine MIME type
                mime_type, encoding = mimetypes.guess_type(doc_metadata['path'])
                if not mime_type:
                    mime_type = self.detect_file_type(doc_metadata['path'])
                
                if mime_type and mime_type not in self.supported_mime_types:
                    self.logger.warning(
                        f"Skipping unsupported file type ({mime_type}): {doc_metadata['path']}"
                    )
                    continue
                
                # Read file content
                self.logger.info(f"Collecting file: {doc_metadata['path']}")
                
                with open(doc_metadata['path'], 'rb') as file:
                    raw_content = file.read()
                
                # Create collected document
                collected_doc = self.create_collected_document(
                    document_metadata=doc_metadata,
                    raw_content=raw_content,
                    content_type=mime_type or 'application/octet-stream',
                    encoding=encoding or 'utf-8'
                )
                
                # Update document status
                self.update_document_status(collected_doc)
                collected_documents.append(collected_doc)
                
                self.logger.info(
                    f"Successfully collected: {doc_metadata['path']} "
                    f"({len(raw_content)} bytes, {mime_type or 'unknown'})"
                )
                
            except Exception as e:
                self.logger.error(f"Error collecting document {doc_metadata['path']}: {str(e)}")
                
                # Create failed document record
                failed_doc = CollectedDocument(
                    path=doc_metadata['path'],
                    source_type=doc_metadata['source_type'],
                    status=CollectionStatus.FAILED,
                    metadata={'error': str(e)}
                )
                self.update_document_status(failed_doc)
                collected_documents.append(failed_doc)
        
        self.logger.info(
            f"Collection completed. "
            f"Successful: {sum(1 for doc in collected_documents if doc.status == CollectionStatus.COLLECTED)}, "
            f"Failed: {sum(1 for doc in collected_documents if doc.status == CollectionStatus.FAILED)}"
        )
        
        return collected_documents
    
    def validate_document(self, document_metadata: Dict) -> bool:
        """
        Validate that a local file document can be collected.
        
        Args:
            document_metadata: Metadata for the document to validate
            
        Returns:
            True if the document is valid for collection, False otherwise
        """
        # Call parent validation first
        if not super().validate_document(document_metadata):
            return False
        
        # Additional local file specific validation
        try:
            file_path = document_metadata['path']
            
            # Check file permissions
            if not os.access(file_path, os.R_OK):
                self.logger.warning(f"No read permission for file: {file_path}")
                return False
            
            # Check if file is empty
            if os.path.getsize(file_path) == 0:
                self.logger.warning(f"File is empty: {file_path}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating local file document: {str(e)}")
            return False
    
    def detect_file_type(self, file_path: str) -> str:
        """
        Detect the file type and return appropriate MIME type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected MIME type
        """
        # Use mimetypes module for basic detection
        mime_type, encoding = mimetypes.guess_type(file_path)
        
        if mime_type:
            return mime_type
        
        # Fallback detection based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        extension_map = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.markdown': 'text/markdown',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html'
        }
        
        return extension_map.get(file_ext, 'application/octet-stream')