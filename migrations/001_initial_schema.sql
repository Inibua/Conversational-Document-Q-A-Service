-- Initial schema migration for Conversational Document Q&A Service
-- Version: 1.0
-- Date: 2026-05-30

-- Create Documents table
CREATE TABLE documents (
    doc_id UUID PRIMARY KEY,
    doc_name TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL DEFAULT 'local',
    source_uri TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create Discovered Documents table
CREATE TABLE discovered_documents (
    id UUID PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    text TEXT,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create Chunked Docs table
CREATE TABLE chunked_docs (
    chunk_id UUID PRIMARY KEY,
    doc_id UUID NOT NULL REFERENCES documents(doc_id) ON DELETE CASCADE,
    chunk_text TEXT,
    chunk_idx INTEGER NOT NULL,
    page_ref INTEGER,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_documents_doc_name ON documents(doc_name);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_discovered_documents_doc_id ON discovered_documents(doc_id);
CREATE INDEX idx_chunked_docs_doc_id ON chunked_docs(doc_id);
CREATE INDEX idx_chunked_docs_chunk_idx ON chunked_docs(chunk_idx);

-- Create a function to automatically update the last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update last_updated timestamps
CREATE TRIGGER update_documents_last_updated 
    BEFORE UPDATE ON documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_last_updated_column();

CREATE TRIGGER update_discovered_documents_last_updated 
    BEFORE UPDATE ON discovered_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_last_updated_column();

CREATE TRIGGER update_chunked_docs_last_updated 
    BEFORE UPDATE ON chunked_docs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_last_updated_column();