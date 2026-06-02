"""
Local File Discoverer implementation.

The LocalFileDiscoverer searches a local file system path for documents
that need to be processed.
"""
import os
import logging
from typing import List, Dict
from datetime import datetime
from indexer.discoverer.base import Discoverer, DocumentMetadata
from paths import ROOT_DIR


class LocalFileDiscoverer(Discoverer):
    """
    Discoverer implementation for local file systems.
    
    This discoverer searches a configured local directory for files
    and determines which ones need to be processed.
    """
    
    def __init__(self, config: Dict, db_session):
        """
        Initialize the local file discoverer.
        
        Args:
            config: Configuration dictionary containing:
                   - root_path: Root directory to search for documents
                   - file_extensions: List of file extensions to include
                   - exclude_patterns: List of patterns to exclude
            db_session: SQLAlchemy database session
        """
        super().__init__(config, db_session)
        self.root_path = config.get('root_path', ROOT_DIR)
        self.file_extensions = config.get('file_extensions', ['.md'])
        self.exclude_patterns = config.get('exclude_patterns', [])
        
        self.logger = logging.getLogger(f"{__name__}.LocalFileDiscoverer")
        
        # Validate root path exists
        if not os.path.exists(self.root_path):
            raise ValueError(f"Root path does not exist: {self.root_path}")
        
        if not os.path.isdir(self.root_path):
            raise ValueError(f"Root path is not a directory: {self.root_path}")
    
    def discover(self) -> List[DocumentMetadata]:
        """
        Discover documents in the local file system that need processing.
        
        Returns:
            List of DocumentMetadata objects for documents that need processing
        """
        discovered_documents = []
        
        self.logger.info(f"Starting discovery in path: {self.root_path}")
        
        try:
            # Walk through the directory tree
            for root, dirs, files in os.walk(self.root_path):
                
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if self._should_include_path(os.path.join(root, d))]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if file should be included
                    if not self._should_include_path(file_path):
                        continue
                    
                    # Check file extension
                    if not self._has_valid_extension(file):
                        continue
                    
                    # Get file metadata
                    try:
                        file_stats = os.stat(file_path)
                        
                        document_metadata = DocumentMetadata(
                            path=file_path,
                            size=file_stats.st_size,
                            modified_time=datetime.fromtimestamp(file_stats.st_mtime),
                            source_type='local_file'
                        )
                        
                        # Check if document should be processed
                        if self.should_process_document(document_metadata):
                            discovered_documents.append(document_metadata)
                            self.logger.info(f"Discovered document: {file_path}")
                            
                            # Update document status in database
                            self.update_document_status(document_metadata)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing file {file_path}: {str(e)}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error during discovery: {str(e)}")
            raise
        
        self.logger.info(f"Discovery completed. Found {len(discovered_documents)} documents to process.")
        return discovered_documents
    
    def _has_valid_extension(self, filename: str) -> bool:
        """
        Check if a file has a valid extension.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if the file has a valid extension, False otherwise
        """
        file_ext = os.path.splitext(filename)[1].lower()
        return file_ext in self.file_extensions
    
    def _should_include_path(self, path: str) -> bool:
        """
        Check if a path should be included based on exclusion patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be included, False if it should be excluded
        """
        if not self.exclude_patterns:
            return True
        
        path_str = str(path)
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                self.logger.debug(f"Excluding path due to pattern {pattern}: {path}")
                return False
        
        return True