#!/usr/bin/env python3
"""
Streamlit interface for the Conversational Document Q&A Service.

This Streamlit app:
1. Checks server health on startup
2. Provides a chat interface for user interaction
3. Sends requests to the backend invoke endpoint
4. Uses dummy session_id and user_id for session management
"""

import streamlit as st
import requests
import uuid
import json

# Configuration
BACKEND_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"
INVOKE_ENDPOINT = f"{BACKEND_URL}/invoke"

# Dummy session and user IDs (can be hardcoded or randomly generated)
# Using hardcoded values to simulate chat resume
SESSION_ID = "test_session_123"
USER_ID = "test_user_456"

# Alternatively, use random UUIDs:
# SESSION_ID = str(uuid.uuid4())
# USER_ID = str(uuid.uuid4())

def check_server_health():
    """Check if the backend server is healthy."""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            return True, health_data.get('text', 'OK')
        else:
            return False, f"Server returned status code: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Error connecting to server: {e}"

def invoke_llm(prompt):
    """Invoke the LLM with the given prompt."""
    try:
        payload = {
            "message": prompt,
            "session_id": SESSION_ID,
            "user_id": USER_ID
        }
        
        response = requests.post(INVOKE_ENDPOINT, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return True, result.get('text', 'No response text')
        else:
            return False, f"Server returned status code: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return False, f"Error invoking LLM: {e}"

def main():
    """Main Streamlit application."""
    # Set page config
    st.set_page_config(
        page_title="Conversational Document Q&A",
        page_icon="💬",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 800px;
            margin: 0 auto;
        }
        .user-message {
            background-color: #0e2333;
            padding: 10px 15px;
            border-radius: 15px 15px 0 15px;
            margin-left: auto;
            max-width: 70%;
        }
        .bot-message {
            background-color: #053605;
            padding: 10px 15px;
            border-radius: 15px 15px 15px 0;
            margin-right: auto;
            max-width: 70%;
        }
        .message-header {
            font-weight: bold;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'server_healthy' not in st.session_state:
        st.session_state.server_healthy = None
    
    # Title and description
    st.title("💬 Conversational Document Q&A Service")
    st.markdown("""
        Ask questions about your documents and get intelligent answers powered by AI.
    """)
    
    # Show session info
    st.sidebar.header("Session Info")
    st.sidebar.markdown(f"**Session ID:** `{SESSION_ID}`")
    st.sidebar.markdown(f"**User ID:** `{USER_ID}`")
    
    # Check server health
    if st.session_state.server_healthy is None:
        with st.spinner("Checking server health..."):
            healthy, message = check_server_health()
            st.session_state.server_healthy = healthy
            
        if st.session_state.server_healthy:
            st.sidebar.success(f"✅ Server is healthy: {message}")
        else:
            st.sidebar.error(f"❌ Server connection failed: {message}")
    elif st.session_state.server_healthy:
        st.sidebar.success("✅ Server is healthy")
    else:
        st.sidebar.error("❌ Server connection failed")
    
    # Chat interface
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
                <div class='user-message'>
                    <div class='message-header'>You</div>
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='bot-message'>
                    <div class='message-header'>Assistant</div>
                    <div>{message['content']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Chat input
    st.markdown("---")
    
    if st.session_state.server_healthy:
        user_input = st.chat_input("Type your message here...", disabled=not st.session_state.server_healthy)
        
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Display user message immediately
            st.markdown(f"""
                <div class='user-message'>
                    <div class='message-header'>You</div>
                    <div>{user_input}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Invoke LLM
            with st.spinner("Thinking..."):
                success, response = invoke_llm(user_input)
                
                if success:
                    # Add bot response to chat history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    
                    # Display bot response
                    st.markdown(f"""
                        <div class='bot-message'>
                            <div class='message-header'>Assistant</div>
                            <div>{response}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"Error: {response}")
    else:
        st.warning("Cannot send messages while server is unavailable.")
    
    # Clear chat button
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

if __name__ == "__main__":
    main()