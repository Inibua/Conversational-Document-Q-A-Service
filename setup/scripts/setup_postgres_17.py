#!/usr/bin/env python3
"""
Script to setup PostgreSQL 17 using Docker Compose
"""

import subprocess
import sys
import os


def setup_postgres():
    """Setup PostgreSQL 17 service using Docker Compose"""
    try:
        # Get the project root directory
        project_root = os.path.join(os.path.dirname(__file__), "../..")
        project_root = os.path.abspath(project_root)

        # Check if Docker is installed and running
        subprocess.run(["docker", "version"], check=True, capture_output=True)
        
        # Run PostgreSQL Docker Compose
        compose_file = os.path.join(project_root, "setup", "compose", "postgres-compose.yml")
        subprocess.run(["docker-compose", "-f", compose_file, "up", "-d"], check=True)
        
        print("PostgreSQL 17 service started successfully!")
        print("PostgreSQL is now running on localhost:5432")
        print("Database: conversational_doc_db")
        print("User: postgres")
        print("Password: postgres")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        print("Please make sure Docker is installed and running.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_postgres()