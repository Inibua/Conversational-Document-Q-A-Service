# Conversational-Document-Q-A-Service
Simple RAG based python APP.

Contains 3 parts.
1. Ingestion app
2. Backend App containing LLM communication
3. Small Frontend

# Techstack:
Streamlit, Langchain, Ollama, Postres 17 (Optional), Qdrant, Docling, SQLAlchemy

# Installation:
1. Install docker
2. Install Ollama
3. Install uv globally
5. Install dependencies with uv: uv sync
6. Once .venv is created, set the project interpreter to be the one in the .venv folder.
7. Run the script ```setup/setup_all``` (Note you can comment the postgres part as it is not used)
9. Run the ```setup/setup_database.py``` (Optional, do if postgres setup is enabled and will be used, for now skip)
10. Run the ```indexer/orhestrator/basic.py``` this will ingest the md files and setup a vector DB.

# Running:
1. Run the ```backend/main.py```, wait for the server to start.
2. Run the ```frontend/cli_interface``` or in a terminal do ```streamlit run frontend/streamlit_interface.py```

# Knowledge base
The code is configured to work with .md files for simplicity, this is easily extended by modifying the config (currently hardcoded in the code).
In practice this config should live in config files or even a relational DB. It uses qdrant as a vector DB, I chose qdrant as it
is quite powerful, it support semantic, lexical, hybrid retrievals natively. It's really efficient. Has option for cloud and for docker image as it is locally.
Postgres with pg_vector and pg_textsearch is a strong alternative, especially with recent patches which made it faster and more efficient, still
according to some papers, qdrant is one of the top VectorDBs that support hundreds of millions of vectors efficiently. Postgres until a few months
struggled with only a few millions. There are even more alternatives like pinecone, went with qdrant as I have used it in the past.

The structure of the repo allows for simple extensions with different adapter classes. Vector stores handle embeddings as well.
My reasoning is since vector stores handle upsert and retrieve, where both are highly dependant on embeddings, and embeddings are usually a single model choice,
keeping them integrated in the vector store increases cohesion more than it increases coupling for this case.

Another component that can be separated is the chunking process. At the moment it is part of the processor. Similar reasons apply as embedding,
however it has more configurations compared to embedder.

## Vector Store
Base abstraction that child classes must follow for easy extension and integration of different Vector DBs. Enforce a simple interface
with minimal methods like embed (embedder is part of vector store as mentioned above), upsert, retrieve (semantic, lexical, hybrid).
Hybrid is usually the best practice, recent papers and blogs I've stumbled upon are stating that hybrid has the best performance compared to the other 2.
Especially weighted hybrid + rerank, where depending on the query the retrieval weights more either the semantic or lexical chunks. e.g.
question with containing exact wording like error codes, lexical is better, but more semantic question like "who likes to read and write books", semantic retrieval is usually the to-go approach.
Reranking helps with re-ordering the chunks, i.e. it performs a filter on the already retrieved chunks. This helps with improving accuracy.

# Indexer
Indexer is split in several parts where each part has it's own responsibility. Currently the orchestrator is a simple pipeline.
It can be easily extended to support checkpointing. In essence each part uses a relational DB where is stores is outputs and can also use
the DB as input. This allows for easy replayability and is quite robust when failures happens. Furthermore the implemented separation
can quite easily be fitted into an ETL pipeline software, e.g. apache airflow.

Current implementation reads from a local directory, but adding a new adapter e.g. confluence is just inheritance.

## Running:

Run the ```indexer/orchestrator/basic.py```. This will handle reading, processing, storing the documents in Qdrant.

## Components:
1. Discoverer - Creates jobs for sources to be processed based on criteria (already processed or e.g. when file is updated and needs re-ingestion)
2. Collector - Checks the jobs, collects the raw data from the job source, outputs the raw data with source metadata
3. Processor - Uses docling to process the raw data and outputs chunks with metadata.
4. Storer - Stores the chunks and metadata using a concrete vector db implementation.
5. Orchestrator - currently just a simple wrapper for the above 4 components.


# Backend API

The backend is a FastAPI application that provides two endpoints:

1. `/health` - Returns the status of the server
2. `/invoke` - Main endpoint used to interact with the LLM agent

For chat the correct protocol is usually Websockets. Went with HTTP for simplicity. HTTP can also work as it is the case, but it adds 

## Running the Backend

Run the ```backend/main.py```

## Agent
Using the agentic rag, i.e. the retrieval is a tool that the LLM uses when it needs to.
The agent is configured with SummarizationMiddleware and PIIMiddleware. The former compacts the context and the latter
enforces PII redaction (this case email)

### Health Check

```
GET /health
```

Returns:
```json
{
  "status_code": 200,
  "text": "OK"
}
```

### Invoke Agent

```
POST /invoke
```

Request Body:
```json
{
  "user_id": "unique_user_identifier",
  "message": "Your question here"
}
```

Response:
```json
{
  "status_code": 200,
  "text": "LLM's response to your question"
}
```


# Frontend
Simple cli interaction method and a streamlit one. Both methods use the HTTp - invoke endpoint to communicate with the backend.

## CLI
Run ```frontend/cli_interface``` for simple cli interaction

## UI

Use ```streamlit run frontend/streamlit_interface.py```

## More details
Check the ```frontend/README.MD```, it is AI generated but descriptive


# Contributions:
## Overview
The codebase was coded using AI (devstral-small-2, qwen-3-coder-next:480b with ollama and tried some other models for max 1 prompt but there were issues).
Coding agent was Pi (https://pi.dev/docs/latest), using free tier ollama (https://ollama.com). Tried self hosting smaller models or reduced context of models
to fit in RAM, but inference was extremely slow with entirely local setup. 1-3 t/s. This was unbearable for a coding agent.
Used claude for a few ideas and clarification.

Some fixes were applied manually as the LLM seemed to struggle and I wanted to concerve usage as much as I could, for more meaningful tasks.

All PRD.md files were created manually, so is this file. The rest of the .md files were generated by AI.

## Testing
Tests were generated with AI, unit test are under ```tests```.
Under ```small_integration``` there are integration tests. For the backlend you must start the backend. frontend should work as is.
They use the project interpreter.

## Logging
Logging can drastically be improved, I've almost exhausted the weekly budget for. If I had more budget and time I would definetely improve
by using structured logging and also keep a stack trace in a db so that we can save the execution flow. Another free way
is to use Langsmith for tracing as it is quite easy to setup

## AI traces
All traces are uploaded as ZIP file. pi-sessions and claude-logs