#!/usr/bin/env python3
"""
Main setup script to initialize the entire Conversational Document Q&A Service
"""

import subprocess
import sys
import os

def main_setup():
    """Run all setup steps in sequence"""
    try:
        print("=== Conversational Document Q&A Service Setup ===\n")
        
        # Get the project root directory
        project_root = os.path.join(os.path.dirname(__file__), "../..")
        project_root = os.path.abspath(project_root)
        
        # Step 1: Setup Qdrant
        print("Step 1: Setting up Qdrant service...")
        setup_qdrant_script = os.path.join(project_root, "setup", "scripts", "setup_qdrant.py")
        subprocess.run([sys.executable, setup_qdrant_script], check=True)
        print("✓ Qdrant service started successfully!\n")
        
        # Step 2: Setup PostgreSQL
        print("Step 2: Setting up PostgreSQL service...")
        setup_postgres_script = os.path.join(project_root, "setup", "scripts", "setup_postgres_17.py")
        subprocess.run([sys.executable, setup_postgres_script], check=True)
        print("✓ PostgreSQL service started successfully!\n")
        
        print("=== Setup Complete! ===")
        print("\nYour environment is ready with:")
        print("- Virtual environment with all dependencies")
        print("- Qdrant vector database running on port 6333")
        print("- PostgreSQL 17 database running on port 5432")
        print("\nTo activate the virtual environment, run:")
        if os.name == 'nt':  # Windows
            print("  .venv\\Scripts\\activate")
        else:  # Unix/Linux/Mac
            print("  source .venv/bin/activate")
            
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main_setup()