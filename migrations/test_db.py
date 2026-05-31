#!/usr/bin/env python3
"""
Test script to verify database connectivity and check existing tables
"""

import psycopg2
import os

def test_database():
    """Test database connectivity and list existing tables"""
    try:
        # Connect to the database
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
        
        # Create cursor
        cur = conn.cursor()
        
        # Check existing tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cur.fetchall()
        print(f"\nExisting tables in public schema:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check specifically for our tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('documents', 'discovered_documents', 'chunked_docs')
        """)
        
        our_tables = cur.fetchall()
        print(f"\nOur expected tables:")
        for table in our_tables:
            print(f"  - {table[0]} (FOUND)")
        
        missing_tables = set(['documents', 'discovered_documents', 'chunked_docs']) - set([t[0] for t in our_tables])
        for table in missing_tables:
            print(f"  - {table} (MISSING)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_database()