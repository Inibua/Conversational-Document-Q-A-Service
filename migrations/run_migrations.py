#!/usr/bin/env python3
"""
Database migration script for the Conversational Document Q&A Service
"""

import os
import sys
import psycopg2
from pathlib import Path


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', 5432),
            'database': os.getenv('DB_NAME', 'conversational_doc_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        
        print(f"Connecting to database with params: {conn_params}")
        conn = psycopg2.connect(**conn_params)
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def run_migration(migration_file):
    """Run a single migration file"""
    try:
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        print(f"Running migration: {migration_file}")
        cur.execute(sql)
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"Successfully applied migration: {migration_file}")
        return True
        
    except Exception as e:
        print(f"Error running migration {migration_file}: {e}")
        return False

def run_all_migrations():
    """Run all migration files in order"""
    migrations_dir = Path(__file__).parent
    print(f"Looking for migrations in: {migrations_dir}")
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    print(f"Found migration files: {migration_files}")
    
    if not migration_files:
        print("No migration files found")
        return
    
    print(f"Found {len(migration_files)} migration files")
    
    success_count = 0
    for migration_file in migration_files:
        if run_migration(migration_file):
            success_count += 1
        else:
            print(f"Failed to apply migration: {migration_file}")
            break
    
    print(f"\nApplied {success_count}/{len(migration_files)} migrations successfully")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Run specific migration
        migration_file = sys.argv[1]
        if os.path.exists(migration_file):
            run_migration(migration_file)
        else:
            print(f"Migration file not found: {migration_file}")
    else:
        # Run all migrations
        run_all_migrations()

if __name__ == "__main__":
    main()