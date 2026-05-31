# Purpose:
Manual management of the migrations of the postgres schema.

# Components:
## Table: Documents
doc_id: UUID (can be doc_name)
doc_name: unique TEXT
source: "local" (for now, can be then confluence, scrape, etc, can be enforced with LKP Table)
source_uri: TEXT
status: "pending", "collected", "processed", "finished" (can be enforced with LKP Table)
created_at: TIMESTAMP When the entry was first created.
last_updated: TIMESTAMP Last time the entry was updated

## Table: Discovered Documents
id: UUID
doc_id: Foreign key (ref to documents)
text: TEXT field with the doc data
last_updated: TIMESTAMP

## Table: Chunked Docs:
chunk_id: UUID of the chunk
doc_id: Foreign key (ref to documents)
chunk_text: TEXT
chunk_idx: Integer
page_ref: INTEGER
etc. (other metadata fields)
last_updated: TIMESTAMP