"""
Test retrieval from Qdrant vector store.

This script demonstrates that the stored documents can be retrieved.
"""
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

from vector_store.qdrant_vector_store import QdrantVectorStore


def main():
    """Test retrieval from Qdrant."""
    
    # Configuration for the vector store
    config = {
        'embedding_model': 'all-MiniLM-L6-v2',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'documents',
        'vector_size': 768
    }
    
    try:
        # Create vector store instance
        vector_store = QdrantVectorStore(config)
        
        print("Testing retrieval from Qdrant vector store...")
        print()
        
        # Test semantic search
        print("=== Semantic Search ===")
        query = "test document"
        results = vector_store.retrieve_semantic(query, limit=5)
        
        print(f"Query: '{query}'")
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            payload = result['payload']
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Source: {payload.get('source_document_path', 'unknown')}")
            print(f"   Content preview: {payload.get('content', '')[:50]}...")
            print()
        
        # Test lexical search
        print("=== Lexical Search ===")
        results = vector_store.retrieve_lexical(query, limit=5)
        
        print(f"Query: '{query}'")
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            payload = result['payload']
            print(f"{i}. Source: {payload.get('source_document_path', 'unknown')}")
            print(f"   Content preview: {payload.get('content', '')[:50]}...")
            print()
        
        print("Retrieval test completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error testing retrieval: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())