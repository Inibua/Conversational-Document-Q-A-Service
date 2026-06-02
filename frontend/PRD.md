# Purpose
The frontend provides a simple UI to interact with the llm functionality provided by the backend server.

# Components:
1. Simple CLI interface from the terminal.
   * On startup it should first call the "health" endpoint to verify the status of the server.
   * If the server is healthy call the "invoke" endpoint of the server, with the input from the user.
   * Should pass a dummy session_id and user_id that the backend can use to manage sessions and chat history
   * The session_id and user_id can be randomly generated, but can also be hard coded to simulate chat resume
2. Streamlit interface.
   * On startup it should first call the "health" endpoint to verify the status of the server.
   * If the server is healthy call the "invoke" endpoint of the server, with the input from the user.
   * Should pass a dummy session_id and user_id that the backend can use to manage sessions and chat history
   * The session_id and user_id can be randomly generated, but can also be hard coded to simulate chat resume

# TechStack:
Python, Chainlit, 