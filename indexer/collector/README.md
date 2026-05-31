# Collector Module

The Collector module is responsible for collecting raw document content from various sources in a RAG (Retrieval-Augmented Generation) application.

## Overview

The Collector component reads raw content from documents identified by the Discoverer. It handles different source types (local files, web pages, Confluence, etc.), validates documents, and prepares them for further processing.

## Architecture

```
Collector (Abstract Base Class)
│
├── LocalFileCollector (Local file system implementation)
├── WebCollector (Web/URL implementation - future)
├── ConfluenceCollector (Confluence implementation - future)
└── ... (other source-specific implementations)
```

## Key Features

- **Source-agnostic design**: Base class defines the interface, allowing different source implementations
- **Content validation**: File size limits, MIME type checking, permission validation
- **Error handling**: Graceful handling of collection failures
- **Database integration**: Updates document status to "collected" in the database
- **Logging**: Structured logging for monitoring and debugging
- **Extensible**: Easy to add new collector implementations for different sources

## Installation

The collector module is part of the indexer package. No additional installation is required beyond the main project dependencies.

## Usage

### Basic Example

```python
from indexer.collector import LocalFileCollector, CollectionStatus
from unittest.mock import MagicMock

# Create a mock database session (replace with real SQLAlchemy session in production)
db_session = MagicMock()

# Configuration
config = {
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'supported_mime_types': ['text/plain', 'text/markdown', 'application/pdf']
}

# Create document metadata list (from discoverer)
document_metadata_list = [
    {
        'path': '/path/to/document1.txt',
        'source_type': 'local_file',
        'metadata': {'author': 'test'}
    },
    {
        'path': '/path/to/document2.md',
        'source_type': 'local_file'
    }
]

# Create and run the collector
collector = LocalFileCollector(config, db_session)
collected_documents = collector.collect(document_metadata_list)

# Process results
for doc in collected_documents:
    if doc.status == CollectionStatus.COLLECTED:
        print(f"Successfully collected: {doc.path}")
        print(f"Content type: {doc.content_type}")
        print(f"Size: {doc.size} bytes")
    else:
        print(f"Failed to collect: {doc.path}")
```

### Integration with Discoverer

```python
from indexer.discoverer import LocalFileDiscoverer
from indexer.collector import LocalFileCollector

# Step 1: Discovery
discoverer = LocalFileDiscoverer(discoverer_config, db_session)
discovered_docs = discoverer.discover()

# Convert to metadata list
document_metadata_list = [
    {
        'path': doc.path,
        'source_type': doc.source_type,
        'metadata': {'discovered_at': str(doc.modified_time)}
    }
    for doc in discovered_docs
]

# Step 2: Collection
collector = LocalFileCollector(collector_config, db_session)
collected_docs = collector.collect(document_metadata_list)
```

## Configuration

The collector is configured through a dictionary with the following options:

### LocalFileCollector Configuration

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `max_file_size` | int | Maximum file size to collect (in bytes) | 10,485,760 (10MB) |
| `supported_mime_types` | list[str] | List of supported MIME types | ['text/plain', 'text/markdown', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'] |

Example:
```python
config = {
    'max_file_size': 5 * 1024 * 1024,  # 5MB
    'supported_mime_types': ['text/plain', 'text/markdown']
}
```

## API Reference

### `CollectionStatus` Enum

Represents the status of document collection.

**Values:**
- `PENDING`: Document is waiting to be collected
- `COLLECTED`: Document was successfully collected
- `FAILED`: Document collection failed

### `CollectedDocument` Dataclass

Represents a collected document with its raw content and metadata.

**Attributes:**
- `document_id` (Optional[str]): Unique document identifier
- `path` (str): Full path to the document
- `source_type` (str): Type of source (e.g., 'local_file')
- `raw_content` (bytes): Raw content of the document
- `content_type` (str): MIME type of the content
- `encoding` (str): Character encoding
- `size` (int): Size of the content in bytes
- `collected_at` (Optional[datetime]): When the document was collected
- `status` (CollectionStatus): Collection status
- `metadata` (Dict): Additional metadata

### `Collector` Abstract Base Class

Base class for all collectors.

**Methods:**
- `collect(document_metadata_list: List[Dict]) -> List[CollectedDocument]`: Collect raw documents
- `update_document_status(collected_document: CollectedDocument) -> None`: Update document status
- `validate_document(document_metadata: Dict) -> bool`: Validate document for collection
- `create_collected_document(document_metadata: Dict, raw_content: bytes, content_type: str, encoding: str) -> CollectedDocument`: Create collected document object

### `LocalFileCollector` Class

Implementation for local file system collection.

**Methods:**
- `collect(document_metadata_list: List[Dict]) -> List[CollectedDocument]`: Collect documents from local files
- `validate_document(document_metadata: Dict) -> bool`: Validate local file document
- `detect_file_type(file_path: str) -> str`: Detect file MIME type

## Testing

The collector module includes comprehensive unit tests. Run tests with:

```bash
PYTHONPATH=. python tests/test_collector.py
```

Tests cover:
- CollectedDocument creation and defaults
- Collector initialization
- File collection with various configurations
- File size limits
- File type validation
- Empty file handling
- Nonexistent file handling
- Permission errors
- Error conditions and recovery

## Future Enhancements

- **Additional Collector Implementations**:
  - WebCollector for URL/content fetching
  - ConfluenceCollector for Confluence pages
  - DatabaseCollector for database content

- **Advanced Features**:
  - Incremental collection (only changed content)
  - Content deduplication
  - Parallel/async collection
  - Content compression and encryption

- **Enhanced Validation**:
  - Virus scanning
  - Content quality checks
  - Format validation

- **Performance Optimizations**:
  - Batch processing
  - Memory-mapped file reading
  - Streaming for large files

## Integration Points

The Collector integrates with other components:

1. **Discoverer**: Receives document metadata list
2. **Processor**: Passes collected documents for processing
3. **Database**: Updates document status and stores raw content
4. **Logging**: Consistent structured logging format

## Error Handling

The collector handles errors gracefully:

- **Validation Errors**: Invalid documents are skipped with warnings
- **File Errors**: Permission issues, missing files handled gracefully
- **Size Limits**: Files exceeding limits are skipped
- **Type Errors**: Unsupported file types are skipped
- **Database Errors**: Collection failures are logged and recorded

Failed collections create `CollectedDocument` objects with `status=FAILED` and error information in metadata.

## Performance Considerations

- **File Size Limits**: Configure appropriate limits for your use case
- **MIME Type Filtering**: Only collect supported file types
- **Memory Usage**: Large files are read in binary mode for efficiency
- **Batch Processing**: Process documents in batches for better performance

## Logging

The collector uses Python's standard `logging` module with structured format:

```
timestamp - logger_name - level - message
```

Example log output:
```
2026-05-31 10:08:34,818 - indexer.collector.local_file_collector.LocalFileCollector - INFO - Starting collection of 2 documents
2026-05-31 10:08:34,818 - indexer.collector.local_file_collector.LocalFileCollector - INFO - Collecting file: data_to_ingest\test1.txt
2026-05-31 10:08:34,818 - indexer.collector.local_file_collector.LocalFileCollector - INFO - Successfully collected: data_to_ingest\test1.txt (44 bytes, text/plain)
2026-05-31 10:08:34,818 - indexer.collector.local_file_collector.LocalFileCollector - INFO - Collection completed. Successful: 2, Failed: 0
```

## Best Practices

1. **Configuration**: Set appropriate file size limits and supported types
2. **Error Handling**: Monitor logs for failed collections
3. **Validation**: Use validation to filter out problematic documents early
4. **Memory Management**: Be mindful of memory usage with large files
5. **Security**: Validate all file paths to prevent directory traversal attacks
6. **Monitoring**: Track collection success/failure rates over time