# Database Migrations

This directory contains SQL migration scripts for the PostgreSQL database used in the Conversational Document Q&A Service.

## Migration Files

Migration files are named with a sequential number followed by a descriptive name:
- `001_initial_schema.sql` - Initial schema creation

## How to Run Migrations

### Option 1: Using psql command line

1. Make sure PostgreSQL is running (using the setup script or docker container)
2. Navigate to the project root directory
3. Run the migration using psql:

```bash
# For the initial schema migration
psql -h localhost -p 5432 -U postgres -d conversational_doc_db -f migrations/001_initial_schema.sql
```

### Option 2: Using a Python script

You can also create a Python script to run migrations:

```python
import psycopg2

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="conversational_doc_db",
    user="postgres",
    password="postgres"
)

# Read and execute the migration file
with open('migrations/001_initial_schema.sql', 'r') as f:
    sql = f.read()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()

conn.close()
```

### Option 3: Using Docker

If you're running PostgreSQL in Docker:

```bash
# Copy the migration file to the container
docker cp migrations/001_initial_schema.sql conversational-doc-postgres:/tmp/

# Execute the migration
docker exec -i conversational-doc-postgres psql -U postgres -d conversational_doc_db -f /tmp/001_initial_schema.sql
```

## Migration Best Practices

1. Always backup your database before running migrations
2. Test migrations on a development database first
3. Name migration files sequentially
4. Keep migration files idempotent when possible
5. Document the purpose of each migration

## Current Schema Overview

The database contains three main tables:

1. **documents** - Stores metadata about documents
2. **discovered_documents** - Stores the raw text content of documents
3. **chunked_docs** - Stores processed chunks of documents for vector search

For detailed schema information, see PRD.md