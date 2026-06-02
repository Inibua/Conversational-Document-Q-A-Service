# Frontend Components

This directory contains the frontend interfaces for the Conversational Document Q&A Service.

## Components

### 1. CLI Interface (`cli_interface.py`)

A simple command-line interface that allows users to interact with the LLM service.

**Features:**
- Checks server health on startup
- Interactive chat session
- Uses dummy session_id and user_id for session management
- Simple text-based interface

**Usage:**
```bash
cd frontend
python cli_interface.py
```

**Example session:**
```
Welcome to Conversational Document Q&A Service CLI
Session ID: test_session_123
User ID: test_user_456
Type 'quit' or 'exit' to end the session.

Server is healthy! Status: OK

You: Hello, what can you tell me about the documents?

LLM Response: [LLM response here]

You: [your next question]
```

### 2. Streamlit Interface (`streamlit_interface.py`)

A web-based interface built with Streamlit for a more user-friendly experience.

**Features:**
- Responsive web interface
- Chat history display
- Server health monitoring
- Session information display
- Clear chat history functionality

**Usage:**
```bash
cd frontend
streamlit run streamlit_interface.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Configuration

Both interfaces connect to the backend server at `http://localhost:8000` by default. 

### Session Management

The interfaces use hardcoded session and user IDs to simulate chat resume:
- **Session ID**: `test_session_123`
- **User ID**: `test_user_456`

For production use, you can modify the code to use random UUIDs:

```python
# Replace the hardcoded values with:
SESSION_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
```

## Dependencies

- `requests` - For HTTP requests to the backend
- `streamlit` - For the web interface
- `uuid` - For session ID generation (optional)

All dependencies are listed in the project's `pyproject.toml` file.

## Backend Requirements

The frontend expects the backend to provide two endpoints:

1. **GET `/health`** - Returns server health status
   - Response: `{"status_code": 200, "text": "OK"}`

2. **POST `/invoke`** - Main LLM interaction endpoint
   - Request body: `{"prompt": "user input", "session_id": "...", "user_id": "..."}`
   - Response: `{"status_code": 200, "text": "LLM response"}`

## Development Notes

- The frontend components are designed to be simple and easy to modify
- Error handling is implemented for network issues and server errors
- The Streamlit interface includes basic styling for better user experience
- Both interfaces can be extended with additional features as needed