"""
Base Collector class.

The Collector interface/base class states all the functions needed to be implemented.
Each Collector child class implements the methods. Each child contains specific
functionality based on the source location containing the files to be collected.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class CollectionStatus(Enum):
    """Status of document collection."""
    PENDING = "pending"
    COLLECTED = "collected"
    FAILED = "failed"


@dataclass
class CollectedDocument:
    """Represents a collected document with its raw content and metadata."""
    
    # Document identification
    document_id: Optional[str] = None
    path: str = ""
    source_type: str = ""
    
    # Content
    raw_content: bytes = b""
    content_type: str = "text/plain"
    encoding: str = "utf-8"
    
    # Metadata
    size: int = 0
    collected_at: Optional[datetime] = None
    status: CollectionStatus = CollectionStatus.PENDING
    
    # Additional metadata
    metadata: Dict = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.metadata is None:
            self.metadata = {}
        if self.collected_at is None:
            self.collected_at = datetime.now()


class Collector(ABC):
    """
    Abstract base class for all collectors.
    
    The Collector reads a source of information (local file storage, confluence, webpage)
    and stores the read raw document, updating the documents table with status "collected".
    """
    
    def __init__(self, config: Dict, db_session):
        """
        Initialize the collector.
        
        Args:
            config: Configuration dictionary for the collector
            db_session: SQLAlchemy database session for updating document status
        """
        self.config = config
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def collect(self, document_metadata_list: List[Dict]) -> List[CollectedDocument]:
        """
        Collect raw documents based on discovered document metadata.
        
        Args:
            document_metadata_list: List of document metadata from discoverer
            
        Returns:
            List of CollectedDocument objects containing raw content and metadata
        """
        pass
    
    def update_document_status(self, collected_document: CollectedDocument) -> None:
        """
        Update the document status in the database to "collected".
        
        Args:
            collected_document: The collected document to update
        """
        try:
            # This would be implemented with actual SQLAlchemy code
            # For now, we'll just log the action
            self.logger.info(
                f"Updating document status: path={collected_document.path}, "
                f"status={collected_document.status.value}"
            )
            # TODO: Implement actual database update using SQLAlchemy
            # Example: 
            # document = self.db_session.query(Document).filter_by(path=collected_document.path).first()
            # if document:
            #     document.status = collected_document.status.value
            #     document.raw_content = collected_document.raw_content
            #     document.collected_at = collected_document.collected_at
            #     self.db_session.commit()
        except Exception as e:
            self.logger.error(f"Error updating document status: {str(e)}")
            raise
    
    def validate_document(self, document_metadata: Dict) -> bool:
        """
        Validate that a document can be collected.
        
        Args:
            document_metadata: Metadata for the document to validate
            
        Returns:
            True if the document is valid for collection, False otherwise
        """
        try:
            # Basic validation - can be extended by child classes
            required_fields = ['path', 'source_type']
            for field in required_fields:
                if field not in document_metadata:
                    self.logger.warning(f"Document missing required field: {field}")
                    return False
            
            # Check that path exists (for local files)
            if document_metadata['source_type'] == 'local_file':
                import os
                if not os.path.exists(document_metadata['path']):
                    self.logger.warning(f"Document path does not exist: {document_metadata['path']}")
                    return False
                
                if not os.path.isfile(document_metadata['path']):
                    self.logger.warning(f"Document path is not a file: {document_metadata['path']}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating document: {str(e)}")
            return False
    
    def create_collected_document(self, document_metadata: Dict, raw_content: bytes, 
                                 content_type: str = "text/plain", 
                                 encoding: str = "utf-8") -> CollectedDocument:
        """
        Create a CollectedDocument object from raw content and metadata.
        
        Args:
            document_metadata: Original document metadata
            raw_content: Raw content of the document
            content_type: MIME type of the content
            encoding: Character encoding
            
        Returns:
            CollectedDocument object
        """
        return CollectedDocument(
            path=document_metadata['path'],
            source_type=document_metadata['source_type'],
            raw_content=raw_content,
            content_type=content_type,
            encoding=encoding,
            size=len(raw_content),
            status=CollectionStatus.COLLECTED,
            metadata=document_metadata.get('metadata', {})
        )