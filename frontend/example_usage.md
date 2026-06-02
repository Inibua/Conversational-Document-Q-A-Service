# Example Usage

## CLI Interface Example

Here's how to use the CLI interface:

```bash
# Navigate to the frontend directory
cd frontend

# Run the CLI interface
python cli_interface.py
```

Example interaction:

```
Welcome to Conversational Document Q&A Service CLI
Session ID: test_session_123
User ID: test_user_456
Type 'quit' or 'exit' to end the session.

Server is healthy! Status: OK

You: What can you tell me about the document processing capabilities?

LLM Response: The system can process various document types including PDF, Word, and text files. It uses advanced NLP techniques to extract meaningful information and can answer questions based on the document content.

You: How does the session management work?

LLM Response: The system uses session IDs to maintain conversation context. Each session keeps track of the chat history, allowing for more coherent and context-aware responses throughout the conversation.

You: quit
Goodbye!
```

## Streamlit Interface Example

```bash
# Navigate to the frontend directory
cd frontend

# Run the Streamlit interface
streamlit run streamlit_interface.py
```

The Streamlit interface will open in your default web browser at `http://localhost:8501`.

### Features in the Streamlit Interface:

1. **Chat Interface**: Type your questions in the input box at the bottom
2. **Chat History**: All messages are displayed in a conversation format
3. **Session Info**: Shows your session ID and user ID in the sidebar
4. **Server Status**: Displays whether the backend server is healthy
5. **Clear Chat**: Use the "Clear Chat History" button to start a new conversation

### Example Workflow:

1. The interface automatically checks server health on startup
2. Type your question in the input box and press Enter
3. The interface sends your question to the backend
4. The LLM response appears in the chat
5. Continue the conversation or clear the chat when done

## Troubleshooting

### Common Issues:

**Server not available:**
- Make sure the backend server is running at `http://localhost:8000`
- Check that the server health endpoint is accessible

**Connection errors:**
- Verify your network connection
- Check that no firewall is blocking port 8000

**Import errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're using the correct Python version (3.14+)

### Checking Server Health Manually:

You can manually check if the backend is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status_code": 200, "text": "OK"}
```