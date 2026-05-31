#!/usr/bin/env python3
"""
Script to setup the database schema for the Conversational Document Q&A Service
"""

import subprocess
import sys
import os

def setup_database():
    """Setup the database schema by running migrations"""
    try:
        # Get project root directory
        project_root = os.path.join(os.path.dirname(__file__), "..")
        project_root = os.path.abspath(project_root)
        
        # Change to project root
        os.chdir(project_root)
        
        # Run the migrations script
        migrations_script = os.path.join(project_root, "migrations", "run_migrations.py")
        subprocess.run([sys.executable, migrations_script], check=True)
        
        print("Database schema setup completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during database setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()