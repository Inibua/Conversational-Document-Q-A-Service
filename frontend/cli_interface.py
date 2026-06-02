#!/usr/bin/env python3
"""
Simple CLI interface for the Conversational Document Q&A Service.

This CLI interface:
1. Checks server health on startup
2. Takes user input from the terminal
3. Sends requests to the backend invoke endpoint
4. Uses dummy session_id and user_id for session management
"""

import requests
import uuid
import json
import sys

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
        response = requests.get(HEALTH_ENDPOINT)
        if response.status_code == 200:
            health_data = response.json()
            print(f"Server is healthy! Status: {health_data.get('text', 'OK')}")
            return True
        else:
            print(f"Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")
        return False

def invoke_llm(prompt):
    """Invoke the LLM with the given prompt."""
    try:
        payload = {
            "message": prompt,
            "session_id": SESSION_ID,
            "user_id": USER_ID
        }
        
        response = requests.post(INVOKE_ENDPOINT, json=payload)
        print(response.status_code)
        print(response.json())
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nLLM Response: {result.get('text', 'No response text')}")
            return result.get('text', '')
        else:
            print(f"Error: Server returned status code {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error invoking LLM: {e}")
        return None

def main():
    """Main CLI loop."""
    print("Welcome to Conversational Document Q&A Service CLI")
    print(f"Session ID: {SESSION_ID}")
    print(f"User ID: {USER_ID}")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    # Check server health
    if not check_server_health():
        print("Cannot proceed without a healthy server.")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            user_input = input("\nYou: ")
            
            # Exit conditions
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
                
            # Invoke the LLM
            invoke_llm(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()