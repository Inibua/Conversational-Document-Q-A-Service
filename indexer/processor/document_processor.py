"""
Document Processor implementation.

The DocumentProcessor processes raw documents by converting them to markdown,
chunking the content, and creating metadata for each chunk.
"""
import logging
from typing import List, Dict
from datetime import datetime
import hashlib
import re
from .base import Processor, ProcessedChunk, ProcessingStatus


class DocumentProcessor(Processor):
    """
    Processor implementation for document processing.
    
    This processor handles the core document processing pipeline:
    1. Convert raw content to text/markdown
    2. Clean and normalize the text
    3. Chunk the content
    4. Create metadata for each chunk
    5. Store processed chunks
    """
    
    def __init__(self, config: Dict, db_session):
        """
        Initialize the document processor.
        
        Args:
            config: Configuration dictionary containing:
                   - chunk_size: Maximum size of each chunk in characters
                   - chunk_overlap: Overlap between chunks in characters
                   - supported_content_types: List of supported content types
            db_session: SQLAlchemy database session
        """
        super().__init__(config, db_session)
        self.chunk_size = config.get('chunk_size', 1000)  # Default: 1000 characters
        self.chunk_overlap = config.get('chunk_overlap', 200)  # Default: 200 characters
        self.supported_content_types = config.get('supported_content_types', [
            'text/plain', 'text/markdown', 'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ])
        
        self.logger = logging.getLogger(f"{__name__}.DocumentProcessor")
    
    def process(self, collected_documents: List[Dict]) -> List[ProcessedChunk]:
        """
        Process collected documents into chunks with metadata.
        
        Args:
            collected_documents: List of collected document data from collector
            
        Returns:
            List of ProcessedChunk objects containing chunked content and metadata
        """
        processed_chunks = []
        
        self.logger.info(f"Starting processing of {len(collected_documents)} documents")
        
        for doc in collected_documents:
            try:
                # Validate document before processing
                if not self.validate_collected_document(doc):
                    self.logger.warning(f"Skipping invalid document: {doc['path']}")
                    continue
                
                # Check if content type is supported
                if doc['content_type'] not in self.supported_content_types:
                    self.logger.warning(
                        f"Skipping unsupported content type ({doc['content_type']}): {doc['path']}"
                    )
                    continue
                
                self.logger.info(f"Processing document: {doc['path']}")
                
                # Step 1: Convert to text/markdown
                text_content = self.convert_to_text(doc)
                
                # Step 2: Clean and normalize text
                cleaned_content = self.clean_text(text_content)
                
                # Step 3: Chunk the content
                chunks = self.chunk_text(cleaned_content, doc)
                
                # Add chunks to results
                processed_chunks.extend(chunks)
                
                self.logger.info(
                    f"Successfully processed: {doc['path']} "
                    f"({len(cleaned_content)} chars -> {len(chunks)} chunks)"
                )
                
            except Exception as e:
                self.logger.error(f"Error processing document {doc['path']}: {str(e)}")
                
                # Create failed chunk record
                failed_chunk = ProcessedChunk(
                    source_document_path=doc['path'],
                    source_type=doc['source_type'],
                    content="",
                    status=ProcessingStatus.FAILED,
                    metadata={'error': str(e)}
                )
                processed_chunks.append(failed_chunk)
        
        # Store all processed chunks
        self.store_processed_chunks(processed_chunks)
        
        self.logger.info(
            f"Processing completed. "
            f"Successful: {sum(1 for chunk in processed_chunks if chunk.status == ProcessingStatus.PROCESSED)}, "
            f"Failed: {sum(1 for chunk in processed_chunks if chunk.status == ProcessingStatus.FAILED)}"
        )
        
        return processed_chunks
    
    def convert_to_text(self, collected_document: Dict) -> str:
        """
        Convert collected document content to text/markdown.
        
        Args:
            collected_document: Collected document data
            
        Returns:
            Text content as string
        """
        try:
            # For now, we'll handle basic text and markdown directly
            # In a real implementation, this would use docling or similar libraries
            # to convert PDF, Word, etc. to text/markdown
            
            raw_content = collected_document['raw_content']
            content_type = collected_document['content_type']
            encoding = collected_document.get('encoding', 'utf-8')
            
            # Decode binary content to string
            text_content = raw_content.decode(encoding, errors='replace')
            
            # For text/plain and text/markdown, return as-is
            if content_type in ['text/plain', 'text/markdown']:
                return text_content
            
            # For other types, we would use appropriate converters
            # This is a placeholder for future implementation
            self.logger.warning(
                f"Direct text conversion for {content_type} - "
                f"would use docling in real implementation"
            )
            
            return text_content
            
        except Exception as e:
            self.logger.error(f"Error converting document to text: {str(e)}")
            raise
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Normalize line endings first
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Remove excessive newlines (3+ become 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Normalize other whitespace (but preserve single newlines)
        text = re.sub(r'[ \t\f\v]+', ' ', text)
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str, collected_document: Dict) -> List[ProcessedChunk]:
        """
        Chunk text content into smaller pieces with overlap.
        
        Args:
            text: Text content to chunk
            collected_document: Original collected document data
            
        Returns:
            List of ProcessedChunk objects
        """
        if not text:
            return []
        
        chunks = []
        text_length = len(text)
        
        # Calculate number of chunks needed
        if text_length <= self.chunk_size:
            # Single chunk
            chunk_content = text
            chunk = self.create_processed_chunk(
                collected_document=collected_document,
                chunk_content=chunk_content,
                chunk_index=0,
                total_chunks=1
            )
            
            # Generate chunk ID
            chunk.chunk_id = self.generate_chunk_id(collected_document, 0, chunk_content)
            chunks.append(chunk)
            
        else:
            # Multiple chunks with overlap
            start = 0
            chunk_index = 0
            
            while start < text_length:
                # Calculate end position
                end = min(start + self.chunk_size, text_length)
                
                # Extract chunk
                chunk_content = text[start:end]
                
                # Create chunk
                chunk = self.create_processed_chunk(
                    collected_document=collected_document,
                    chunk_content=chunk_content,
                    chunk_index=chunk_index,
                    total_chunks=0  # Will be updated later
                )
                
                # Generate chunk ID
                chunk.chunk_id = self.generate_chunk_id(collected_document, chunk_index, chunk_content)
                chunks.append(chunk)
                
                # Move start position (with overlap)
                if end == text_length:
                    break  # Last chunk
                start = end - self.chunk_overlap
                chunk_index += 1
            
            # Update total chunks count
            total_chunks = len(chunks)
            for i, chunk in enumerate(chunks):
                chunk.total_chunks = total_chunks
        
        return chunks
    
    def generate_chunk_id(self, collected_document: Dict, chunk_index: int, chunk_content: str) -> str:
        """
        Generate a unique ID for a chunk.
        
        Args:
            collected_document: Original collected document
            chunk_index: Index of this chunk
            chunk_content: Content of this chunk
            
        Returns:
            Unique chunk ID
        """
        # Create a hash-based ID using document path and chunk index
        unique_string = f"{collected_document['path']}:{chunk_index}:{len(chunk_content)}"
        return hashlib.md5(unique_string.encode('utf-8')).hexdigest()
    
    def validate_collected_document(self, collected_document: Dict) -> bool:
        """
        Validate that a collected document can be processed.
        
        Args:
            collected_document: Collected document data to validate
            
        Returns:
            True if the document is valid for processing, False otherwise
        """
        # Call parent validation first
        if not super().validate_collected_document(collected_document):
            return False
        
        # Additional validation specific to document processing
        try:
            # Check content type is supported
            if collected_document['content_type'] not in self.supported_content_types:
                self.logger.warning(
                    f"Unsupported content type for processing: {collected_document['content_type']}"
                )
                return False
            
            # Check that we can decode the content
            try:
                encoding = collected_document.get('encoding', 'utf-8')
                collected_document['raw_content'].decode(encoding, errors='replace')
            except Exception as e:
                self.logger.warning(f"Cannot decode document content: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating document for processing: {str(e)}")
            return False