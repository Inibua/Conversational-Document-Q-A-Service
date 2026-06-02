#!/usr/bin/env python3
"""
Demonstration script showing how the frontend components work.

This script demonstrates:
1. How to use the CLI interface functions programmatically
2. How to test server connectivity
3. Example usage patterns
"""

import sys
import os

# Add the frontend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from cli_interface import check_server_health, invoke_llm, SESSION_ID, USER_ID

def demo_cli_functions():
    """Demonstrate the CLI interface functions."""
    print("Frontend Components Demo")
    print("=" * 50)
    
    print(f"Session ID: {SESSION_ID}")
    print(f"User ID: {USER_ID}")
    print()
    
    # Demo 1: Check server health
    print("Demo 1: Checking server health...")
    print("-" * 30)
    
    healthy = check_server_health()
    
    if healthy:
        print("Server is healthy and ready!")
        
        # Demo 2: Invoke LLM with a sample question
        print("\nDemo 2: Invoking LLM with a sample question...")
        print("-" * 40)
        
        sample_question = "What is the purpose of this document Q&A service?"
        print(f"Question: {sample_question}")
        
        response = invoke_llm(sample_question)
        
        if response:
            print(f"Response: {response}")
        else:
            print("No response received from LLM.")
    else:
        print("Server is not healthy. Cannot proceed with LLM invocation.")
    
    print("\nDemo completed!")

def show_usage_examples():
    """Show various usage examples."""
    print("\nUsage Examples")
    print("=" * 50)
    
    examples = [
        {
            "description": "Basic question about document processing",
            "question": "How does the document processing work?"
        },
        {
            "description": "Question about specific features",
            "question": "What file formats are supported?"
        },
        {
            "description": "Technical question about the system",
            "question": "How is session management implemented?"
        },
        {
            "description": "Question about limitations",
            "question": "What are the current limitations of the system?"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}: {example['description']}")
        print(f"Question: {example['question']}")
        print("-" * 60)

def main():
    """Run the demonstration."""
    demo_cli_functions()
    show_usage_examples()
    
    print("\n" + "=" * 50)
    print("For more information, see:")
    print("- frontend/README.md - Component documentation")
    print("- frontend/example_usage.md - Usage examples")
    print("- Run 'python cli_interface.py' for interactive CLI")
    print("- Run 'streamlit run streamlit_interface.py' for web interface")

if __name__ == "__main__":
    main()