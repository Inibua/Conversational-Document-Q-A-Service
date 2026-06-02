# Conversational-Document-Q-A-Service
Simple RAG based python APP.

Contains 3 parts.
1. Ingestion app
2. Backend App containing LLM communication
3. Small Frontend

# Techstack
Streamlit, Langchain, Ollama, Postres 17, Qdrant, Docling, SQLAlchemy

# Installation
1. Install docker
2. Install Ollama
3. Install uv (pip install uv)
4. Create virtual environment with uv: uv venv
5. Install dependencies with uv: uv pip install -r requirements.txt
6. Run the setup/setup_qdrant.py
7. Run the setup/setup_postgres_17.py
8. Run the setup/setup_database.py

# Backend API

The backend is a FastAPI application that provides two endpoints:

1. `/health` - Returns the status of the server
2. `/invoke` - Main endpoint used to interact with the LLM agent

## Running the Backend

Navigate to the `backend` directory and run:

```bash
# Using the bash script (Linux/Mac)
bash run.sh

# Using the batch file (Windows)
run.bat

# Or directly with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

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