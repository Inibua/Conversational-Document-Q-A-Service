"""
Test script for the FastAPI backend
"""

import requests
import time

# Base URL for the FastAPI backend
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_invoke():
    """Test the invoke endpoint"""
    print("Testing invoke endpoint...")
    
    # Test data
    test_data = {
        "user_id": "test_user_123",
        "message": "What is the capital of France?"
    }
    
    response = requests.post(f"{BASE_URL}/invoke", json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_invoke_with_knowledge_base():
    """Test the invoke endpoint with a question that should use the knowledge base"""
    print("Testing invoke endpoint with knowledge base tool...")
    
    # Test data
    test_data = {
        "user_id": "test_user_456",
        "message": "Can you tell me about artificial intelligence?"
    }
    
    response = requests.post(f"{BASE_URL}/invoke", json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


if __name__ == "__main__":
    print("Starting backend tests...\n")
    
    try:
        test_health()
        time.sleep(1)
        
        test_invoke()
        time.sleep(1)
        
        test_invoke_with_knowledge_base()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"Error: {e}")