# Processor Module

The Processor module is responsible for processing raw documents into chunks with metadata for a RAG (Retrieval-Augmented Generation) application.

## Overview

The Processor component takes collected documents, converts them to a uniform format (markdown), chunks the content, and creates metadata for each chunk. This prepares the content for vector embedding and storage.

## Architecture

```
Processor (Abstract Base Class)
│
├── DocumentProcessor (Main implementation)
├── SpecializedProcessors (Future extensions)
└── ... (other processor types)
```

## Key Features

- **Document Conversion**: Converts various formats to markdown/text
- **Content Cleaning**: Normalizes and cleans text content
- **Chunking**: Splits documents into manageable chunks with overlap
- **Metadata Creation**: Generates rich metadata for each chunk
- **Database Integration**: Stores processed chunks and metadata
- **Error Handling**: Graceful handling of processing failures
- **Logging**: Structured logging for monitoring and debugging

## Installation

The processor module is part of the indexer package. No additional installation is required beyond the main project dependencies.

## Usage

### Basic Example

```python
from indexer.processor import DocumentProcessor, ProcessingStatus
from unittest.mock import MagicMock

# Create a mock database session (replace with real SQLAlchemy session in production)
db_session = MagicMock()

# Configuration
config = {
    'chunk_size': 1000,  # Characters per chunk
    'chunk_overlap': 200,  # Overlap between chunks
    'supported_content_types': ['text/plain', 'text/markdown', 'application/pdf']
}

# Collected documents (from collector)
collected_documents = [
    {
        'path': '/path/to/document1.txt',
        'source_type': 'local_file',
        'content_type': 'text/plain',
        'raw_content': b'Document content here...',
        'encoding': 'utf-8',
        'status': 'collected'
    }
]

# Create and run the processor
processor = DocumentProcessor(config, db_session)
processed_chunks = processor.process(collected_documents)

# Process results
for chunk in processed_chunks:
    if chunk.status == ProcessingStatus.PROCESSED:
        print(f"Chunk {chunk.chunk_index + 1}/{chunk.total_chunks}:")
        print(f"  ID: {chunk.chunk_id}")
        print(f"  Content: {chunk.content[:50]}...")
        print(f"  Metadata: {chunk.metadata}")
```

### Integration with Collector

```python
from indexer.collector import LocalFileCollector, CollectionStatus
from indexer.processor import DocumentProcessor, ProcessingStatus

# Step 1: Collection (assuming this is already done)
collector = LocalFileCollector(collector_config, db_session)
collected_docs = collector.collect(document_metadata_list)

# Step 2: Convert collected documents to processor format
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

# Step 3: Processing
processor = DocumentProcessor(processor_config, db_session)
processed_chunks = processor.process(collected_docs_for_processing)
```

## Configuration

The processor is configured through a dictionary with the following options:

### DocumentProcessor Configuration

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chunk_size` | int | Maximum size of each chunk in characters | 1000 |
| `chunk_overlap` | int | Overlap between chunks in characters | 200 |
| `supported_content_types` | list[str] | List of supported content types for processing | ['text/plain', 'text/markdown', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] |

Example:
```python
config = {
    'chunk_size': 500,  # Smaller chunks for more granular retrieval
    'chunk_overlap': 100,  # 20% overlap
    'supported_content_types': ['text/plain', 'text/markdown']
}
```

## API Reference

### `ProcessingStatus` Enum

Represents the status of document processing.

**Values:**
- `PENDING`: Document is waiting to be processed
- `PROCESSED`: Document was successfully processed
- `FAILED`: Document processing failed

### `ProcessedChunk` Dataclass

Represents a processed document chunk with its content and metadata.

**Attributes:**
- `document_id` (Optional[str]): Unique document identifier
- `chunk_id` (Optional[str]): Unique chunk identifier (MD5 hash)
- `source_document_path` (str): Path to source document
- `source_type` (str): Type of source (e.g., 'local_file')
- `content` (str): Processed content of the chunk
- `content_type` (str): Content type (default: 'text/markdown')
- `chunk_index` (int): Index of this chunk in the document
- `total_chunks` (int): Total number of chunks from this document
- `processed_at` (Optional[datetime]): When the chunk was processed
- `status` (ProcessingStatus): Processing status
- `metadata` (Dict): Additional metadata
- `embedding` (Optional[List[float]]): Vector embedding (to be filled by storer)

### `Processor` Abstract Base Class

Base class for all processors.

**Methods:**
- `process(collected_documents: List[Dict]) -> List[ProcessedChunk]`: Process documents into chunks
- `store_processed_chunks(processed_chunks: List[ProcessedChunk]) -> None`: Store processed chunks
- `validate_collected_document(collected_document: Dict) -> bool`: Validate document for processing
- `create_processed_chunk(collected_document: Dict, chunk_content: str, chunk_index: int, total_chunks: int, content_type: str, metadata: Dict) -> ProcessedChunk`: Create processed chunk

### `DocumentProcessor` Class

Main implementation for document processing.

**Methods:**
- `process(collected_documents: List[Dict]) -> List[ProcessedChunk]`: Process documents into chunks
- `convert_to_text(collected_document: Dict) -> str`: Convert document to text/markdown
- `clean_text(text: str) -> str`: Clean and normalize text
- `chunk_text(text: str, collected_document: Dict) -> List[ProcessedChunk]`: Chunk text content
- `generate_chunk_id(collected_document: Dict, chunk_index: int, chunk_content: str) -> str`: Generate unique chunk ID
- `validate_collected_document(collected_document: Dict) -> bool`: Validate document for processing

## Processing Pipeline

The DocumentProcessor follows this pipeline:

1. **Validation**: Check that documents are valid for processing
2. **Conversion**: Convert raw content to text/markdown format
3. **Cleaning**: Normalize whitespace, line endings, etc.
4. **Chunking**: Split content into chunks with configured size and overlap
5. **Metadata**: Create rich metadata for each chunk
6. **Storage**: Store processed chunks in database

## Chunking Strategy

The processor uses a sliding window approach with overlap:

- **Chunk Size**: Configurable maximum characters per chunk
- **Overlap**: Configurable number of characters to overlap between chunks
- **Preservation**: Maintains document structure and context
- **Identification**: Each chunk gets a unique MD5-based ID

Example with chunk_size=100, overlap=20:
```
Document: "This is a longer document that needs to be chunked..."
Chunk 1: "This is a longer document that needs to be chunked..." (100 chars)
Chunk 2: "needs to be chunked for better retrieval..." (100 chars, overlaps 20 with chunk 1)
```

## Metadata

Each chunk includes comprehensive metadata:

```python
{
    'source_path': '/path/to/document.txt',
    'source_type': 'local_file',
    'content_type': 'text/plain',
    'original_size': 1024,  # Original document size
    'chunk_size': 987,     # This chunk's size
    'content': 'chunk text used by LLM'
    # Additional custom metadata can be added
}
```

## Testing

The processor module includes comprehensive unit tests. Run tests with:

```bash
PYTHONPATH=. python tests/test_processor.py
```

Tests cover:
- ProcessedChunk creation and defaults
- Processor initialization
- Single document processing
- Multi-document processing
- Document chunking with various sizes
- Content conversion
- Text cleaning
- Chunk ID generation
- Document validation
- Error conditions and recovery

## Future Enhancements

- **Advanced Document Conversion**:
  - Integration with docling for PDF/Word conversion
  - HTML to markdown conversion
  - Image OCR and extraction

- **Enhanced Processing**:
  - Language detection
  - Entity recognition
  - Summarization
  - Keyword extraction

- **Improved Chunking**:
  - Semantic-aware chunking
  - Paragraph-aware splitting
  - Custom chunking strategies

- **Metadata Enhancement**:
  - Automatic tagging
  - Content classification
  - Quality scoring

- **Performance Optimizations**:
  - Parallel processing
  - Batch operations
  - Streaming for large documents

## Integration Points

The Processor integrates with other components:

1. **Collector**: Receives collected documents as input
2. **Storer**: Passes processed chunks for vector embedding
3. **Database**: Stores processed chunks and metadata
4. **Logging**: Consistent structured logging format

## Error Handling

The processor handles errors gracefully:

- **Validation Errors**: Invalid documents are skipped with warnings
- **Conversion Errors**: Unsupported formats are skipped
- **Processing Errors**: Failed chunks are recorded with error metadata
- **Database Errors**: Storage failures are logged and raised

Failed processing creates `ProcessedChunk` objects with `status=FAILED` and error information in metadata.

## Performance Considerations

- **Chunk Size**: Balance between granularity and context preservation
- **Overlap**: Sufficient overlap for context but not too much duplication
- **Memory Usage**: Process documents individually to manage memory
- **Batch Processing**: Process multiple documents in batches for efficiency

## Logging

The processor uses Python's standard `logging` module with structured format:

```
timestamp - logger_name - level - message
```

Example log output:
```
2026-05-31 10:12:54,273 - indexer.processor.document_processor.DocumentProcessor - INFO - Starting processing of 2 documents
2026-05-31 10:12:54,273 - indexer.processor.document_processor.DocumentProcessor - INFO - Processing document: data_to_ingest\test1.txt
2026-05-31 10:12:54,273 - indexer.processor.document_processor.DocumentProcessor - INFO - Successfully processed: data_to_ingest\test1.txt (43 chars -> 1 chunks)
2026-05-31 10:12:54,273 - indexer.processor.document_processor.DocumentProcessor - INFO - Storing processed chunk: document=data_to_ingest\test1.txt, chunk_id=779a3f8cbaae1463854eded09c90285b, status=processed
2026-05-31 10:12:54,273 - indexer.processor.document_processor.DocumentProcessor - INFO - Processing completed. Successful: 2, Failed: 0
```

## Best Practices

1. **Configuration**: Choose appropriate chunk size and overlap for your use case
2. **Content Types**: Only process supported content types
3. **Validation**: Use validation to filter out problematic documents early
4. **Memory Management**: Process large documents carefully
5. **Monitoring**: Track processing success/failure rates
6. **Quality Control**: Review chunk quality and adjust parameters as needed