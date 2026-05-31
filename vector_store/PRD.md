# Vector Stores
This is a package containing different vector store implementations. 
A vector store is used both by the indexing and the querying processes. I.e. indexer and backend
A vector store contains both writing and reading functionality.

## Components:
1. There is one main interface (VectorStore), which all concrete classes must inherit.
2. The VectorStore interface must state all the functions that a concrete vector store must implement
3. Each concrete implementation must have a config relevant for the specific vector store containing:
   1. embedding model
4. The mandatory functions are:
   1. embed_text (uses the embedding algorithm to embed a piece of text)
   2. insert_entry (inserts the embeddings and metadata in the concrete vector database)
   3. retrieve_lexical (given a query, perform a lexical retrieval, e.g. by keyword)
   4. retrieve_semantic (given a query, perform semantic retrieval, cos similarity on the vectors)
   5. retrieve_hybrid (given a query, perform hybrid retrieval, cos similarity on the vectors + keyword search, optionally rerank results)
5. Each concrete vector store must implement 1, 2, and at least one of 4, 5, 6

## Logging:
1. Implemented at each step.
2. Exclude PII and confidential information such as passwords, emails, names (can be redacted)
3. Structured, so that it can easily be analyzed and traced

## Testing.
1. Aim for 100% unit test coverage
2. Testing should be split in function and behavioral tests