"""
Base Discoverer class.

The Discoverer interface/base class states all the functions needed to be implemented.
Each Discoverer child class implements the methods. Each child contains specific
functionality based on the source location to be discovered.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Metadata for a discovered document."""
    path: str
    size: int
    modified_time: datetime
    source_type: str
    status: str = "pending"


class Discoverer(ABC):
    """
    Abstract base class for all discoverers.
    
    The Discoverer searches a space (local file storage, confluence, webpage, etc.)
    and decides if an artifact needs to be added for processing based on criteria
    like if the file has already been processed.
    """
    
    def __init__(self, config: Dict, db_session):
        """
        Initialize the discoverer.
        
        Args:
            config: Configuration dictionary for the discoverer
            db_session: SQLAlchemy database session for updating document status
        """
        self.config = config
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)
        
        # Configure logging to exclude PII and confidential information
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    def discover(self) -> List[DocumentMetadata]:
        """
        Discover documents that need to be processed.
        
        Returns:
            List of DocumentMetadata objects for documents that need processing
        """
        pass
    
    def update_document_status(self, document_metadata: DocumentMetadata) -> None:
        """
        Update the document status in the database.
        
        Args:
            document_metadata: Metadata for the document to update
        """
        try:
            # This would be implemented with actual SQLAlchemy code
            # For now, we'll just log the action
            self.logger.info(
                f"Updating document status: path={document_metadata.path}, "
                f"status={document_metadata.status}"
            )
            # TODO: Implement actual database update using SQLAlchemy
        except Exception as e:
            self.logger.error(f"Error updating document status: {str(e)}")
            raise
    
    def should_process_document(self, document_metadata: DocumentMetadata) -> bool:
        """
        Determine if a document should be processed.
        
        Args:
            document_metadata: Metadata for the document to check
            
        Returns:
            True if the document should be processed, False otherwise
        """
        # Check if document has already been processed
        # This would query the database in a real implementation
        # For now, we'll assume all documents should be processed
        self.logger.info(
            f"Checking if document should be processed: path={document_metadata.path}"
        )
        return True