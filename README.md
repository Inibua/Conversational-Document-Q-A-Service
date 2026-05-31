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
5. Install dependencies with uv: uv pip install -r setup/requirements.txt
6. Run the setup/setup_qdrant.py
7. Run the setup/setup_postgres_17.py
8. Run the setup/setup_database.py