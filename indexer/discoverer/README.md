# Discoverer Module

The Discoverer module is responsible for finding documents that need to be processed in a RAG (Retrieval-Augmented Generation) application.

## Overview

The Discoverer component searches through various sources (local file systems, web pages, Confluence, etc.) to identify documents that need to be ingested into the system. It determines which documents should be processed based on criteria like file extensions, modification times, and whether they've been processed before.

## Architecture

```
Discoverer (Abstract Base Class)
│
├── LocalFileDiscoverer (Local file system implementation)
├── WebDiscoverer (Web/URL implementation - future)
├── ConfluenceDiscoverer (Confluence implementation - future)
└── ... (other source-specific implementations)
```

## Key Features

- **Source-agnostic design**: Base class defines the interface, allowing different source implementations
- **Configurable**: File extensions, exclusion patterns, and other parameters are configurable
- **Database integration**: Updates document status in the database (SQLAlchemy)
- **Logging**: Structured logging for monitoring and debugging
- **Extensible**: Easy to add new discoverer implementations for different sources

## Installation

The discoverer module is part of the indexer package. No additional installation is required beyond the main project dependencies.

## Usage

### Basic Example

```python
from indexer.discoverer import LocalFileDiscoverer
from unittest.mock import MagicMock

# Create a mock database session (replace with real SQLAlchemy session in production)
db_session = MagicMock()

# Configure the discoverer
config = {
    'root_path': 'path/to/documents',
    'file_extensions': ['.txt', '.md', '.pdf', '.docx'],
    'exclude_patterns': ['.git', '__pycache__', 'temp']
}

# Create and run the discoverer
discoverer = LocalFileDiscoverer(config, db_session)
discovered_documents = discoverer.discover()

# Process the discovered documents
for doc in discovered_documents:
    print(f"Found document: {doc.path} ({doc.size} bytes)")
```

### Integration with Orchestrator

In a complete system, the discoverer is used as the first step in the indexing pipeline:

```python
class Orchestrator:
    def run(self):
        # Step 1: Discovery
        discoverer = LocalFileDiscoverer(self.config['discoverer'], self.db_session)
        documents = discoverer.discover()
        
        # Step 2: Collection
        collector = LocalFileCollector(self.config['collector'], self.db_session)
        raw_documents = collector.collect(documents)
        
        # Step 3: Processing
        processor = DocumentProcessor(self.config['processor'], self.db_session)
        processed_chunks = processor.process(raw_documents)
        
        # Step 4: Storage
        storer = VectorStorer(self.config['storer'], self.db_session)
        storer.store(processed_chunks)
```

## Configuration

The discoverer is configured through a dictionary with the following options:

### LocalFileDiscoverer Configuration

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `root_path` | str | Root directory to search for documents | Current directory |
| `file_extensions` | list[str] | File extensions to include | `['.txt', '.md', '.pdf', '.docx']` |
| `exclude_patterns` | list[str] | Path patterns to exclude | `[]` |

Example:
```python
config = {
    'root_path': '/path/to/documents',
    'file_extensions': ['.txt', '.md'],
    'exclude_patterns': ['.git', 'temp', 'backup']
}
```

## API Reference

### `DocumentMetadata` Dataclass

Represents metadata about a discovered document.

**Attributes:**
- `path` (str): Full path to the document
- `size` (int): Size of the document in bytes
- `modified_time` (datetime): Last modification time
- `source_type` (str): Type of source (e.g., 'local_file')
- `status` (str): Processing status (default: 'pending')

### `Discoverer` Abstract Base Class

Base class for all discoverer implementations.

**Methods:**
- `discover() -> List[DocumentMetadata]`: Discover documents that need processing
- `update_document_status(document_metadata: DocumentMetadata) -> None`: Update document status in database
- `should_process_document(document_metadata: DocumentMetadata) -> bool`: Determine if document should be processed

### `LocalFileDiscoverer` Class

Implementation for local file system discovery.

**Methods:**
- `discover() -> List[DocumentMetadata]`: Discover documents in the configured directory
- `_has_valid_extension(filename: str) -> bool`: Check if file has valid extension
- `_should_include_path(path: str) -> bool`: Check if path should be included

## Testing

The discoverer module includes comprehensive unit tests. Run tests with:

```bash
PYTHONPATH=. python tests/test_discoverer.py
```

Tests cover:
- Document metadata creation
- Discoverer initialization
- File discovery with various configurations
- File extension filtering
- Path exclusion patterns
- Error handling

## Future Enhancements

- **Additional discoverer implementations**: WebDiscoverer, ConfluenceDiscoverer, etc.
- **Advanced filtering**: Size limits, date ranges, content-based filtering
- **Incremental discovery**: Track last discovery time to only find new/changed files
- **Parallel discovery**: Multi-threaded or distributed discovery for large file systems
- **Database integration**: Full SQLAlchemy implementation for document status tracking

## Logging

The discoverer uses Python's standard `logging` module with the following features:

- Structured log format: `timestamp - logger_name - level - message`
- Info level for normal operations
- Error level for exceptions and critical issues
- PII and confidential information is excluded from logs

Example log output:
```
2026-05-31 09:46:55,931 - indexer.discoverer.local_file_discoverer.LocalFileDiscoverer - INFO - Starting discovery in path: data_to_ingest
2026-05-31 09:46:55,932 - indexer.discoverer.local_file_discoverer.LocalFileDiscoverer - INFO - Discovered document: data_to_ingest\test1.txt
2026-05-31 09:46:55,932 - indexer.discoverer.local_file_discoverer.LocalFileDiscoverer - INFO - Discovery completed. Found 2 documents to process.
```

## Error Handling

The discoverer handles errors gracefully:

- Invalid root paths raise `ValueError` during initialization
- File system errors are caught and logged during discovery
- Individual file errors don't stop the entire discovery process
- Database errors are caught and logged

## Performance Considerations

- For large file systems, consider adjusting `exclude_patterns` to skip unnecessary directories
- The current implementation uses `os.walk()` which is memory-efficient
- Future enhancements may include parallel processing for very large directories