#!/usr/bin/env python3
"""
Script to setup Qdrant using Docker Compose
"""

import subprocess
import sys
import os

def setup_qdrant():
    """Setup Qdrant service using Docker Compose"""
    try:
        # Get the project root directory
        project_root = os.path.join(os.path.dirname(__file__), "../..")
        project_root = os.path.abspath(project_root)

        # Check if Docker is installed and running
        subprocess.run(["docker", "version"], check=True, capture_output=True)
        
        # Run Qdrant Docker Compose
        compose_file = os.path.join(project_root, "setup", "compose", "qdrant-compose.yml")
        subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], check=True)
        
        print("Qdrant service started successfully!")
        print("Qdrant is now running on http://localhost:6333")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        print("Please make sure Docker is installed and running.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_qdrant()