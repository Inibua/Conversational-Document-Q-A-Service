# Purpose:
The indexer executes the process of ingesting data and saving it in a format appropriate for a RAG application.
The indexer contains four main parts used to discover, collect, process and store the data appropriately.

# Components:
1. Discoverer
   * The Discoverer interface/base class states all the functions needed to be implemented (e.g. discover)
   * Each Discoverer child class implements the methods. Each child contains specific functionality based on the source location to be discovered.
   * The Discoverer searches a space (local file storage, confluence, webpage, for now only a local file path).
   * The Discoverer decides if an artifact needs to be added for processing based on criteria like if the file has already been processed.
   * The Discoverer uses sqlalchemy to update the documents table with the status of "pending", i.e. creates jobs for which files need to be collected, processed and stored.
2. Collector
   * The Collector interface/base class states all the functions needed to be implemented (e.g. collect).
   * Each Collector child class implements the methods. Each child contains specific functionality based on the source location containing the files to be collected.
   * The Collector reads a source of information (local file storage, confluence, webpage).
   * The Collector uses sqlalchemy to store the read raw document and updates the documents table with status "collected".
3. Processor
   * The Processor interface/base class states all the functions needed to be implemented (e.g. process)
   * Each child processor class must implement the methods. Each child contains specific functionality. For this case one child class should be enough, but this structure allows possible changes in the future.
   * The Processor reads the stored raw documents, uses docling to convert to docling document. Adds additional processing, for now only export to markdown. Finally chunks the markdown and creates metadata.
   * The processor uses sqlalchemy to store the chunks and their metadata.
4. Storer
   * The storer interface/base class states all the functions needed to be implemented (e.g. store)
   * Each child storer class must implement the methods. Each child contains specific functionality. For this case The difference is most probably which vector store to use. Will use inheritance for starters, can be reworked in the future.
   * The storer reads the chunks and metadata from the db. Formats them for the appropriate vector store, then uses a vector store to store in a vector db.
5. Orchestrator
   * The orchestrator configures the other four components and calls them in order: 1. Discoverer, 2. Collector, 3. Processor, 4. Storer

# Logging:
1. Implemented at each step.
2. Exclude PII and confidential information such as passwords, emails, names (can be redacted)
3. Structured, so that it can easily be analyzed and traced

# Testing.
1. Aim for 100% unit test coverage. Use fake data like fake classes with dicts to simulate the db.
2. Testing should be split in function and behavioral tests