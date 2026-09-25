"""Test script for Chroma vector database integration"""

import sys
from database.vector_db import get_vector_store

def test_chroma_integration():
    """Test basic Chroma operations"""
    print("🧪 Testing Chroma Vector Database Integration")
    print("=" * 50)

    # Test 1: Initialize vector store
    print("\n✓ Test 1: Initializing vector store...")
    try:
        vector_store = get_vector_store("test_collection")
        print("  ✅ Vector store initialized successfully")
    except Exception as e:
        print(f"  ❌ Failed to initialize vector store: {e}")
        return False

    # Test 2: Add documents
    print("\n✓ Test 2: Adding documents...")
    try:
        test_documents = [
            "Python is a high-level programming language",
            "Machine learning is a subset of artificial intelligence",
            "Chroma is a vector database for embeddings",
            "FastAPI is a modern web framework for building APIs"
        ]

        test_metadatas = [
            {"topic": "programming", "id": 1},
            {"topic": "machine_learning", "id": 2},
            {"topic": "vector_db", "id": 3},
            {"topic": "web_framework", "id": 4}
        ]

        ids = vector_store.add_documents(test_documents, test_metadatas)
        print(f"  ✅ Successfully added {len(ids)} documents")
        print(f"     Document IDs: {ids}")
    except Exception as e:
        print(f"  ❌ Failed to add documents: {e}")
        return False

    # Test 3: Search documents
    print("\n✓ Test 3: Searching documents...")
    try:
        query = "artificial intelligence and machine learning"
        results = vector_store.search(query, n_results=2)

        print(f"  ✅ Search completed for query: '{query}'")
        if results and results['documents']:
            print(f"     Found {len(results['documents'][0])} results:")
            for i, doc in enumerate(results['documents'][0], 1):
                print(f"       {i}. {doc[:60]}...")
    except Exception as e:
        print(f"  ❌ Failed to search documents: {e}")
        return False

    # Test 4: Get collection stats
    print("\n✓ Test 4: Getting collection statistics...")
    try:
        stats = vector_store.get_stats()
        print(f"  ✅ Collection statistics retrieved:")
        print(f"     Name: {stats['collection_name']}")
        print(f"     Document count: {stats['count']}")
    except Exception as e:
        print(f"  ❌ Failed to get statistics: {e}")
        return False

    # Test 5: Update documents
    print("\n✓ Test 5: Updating documents...")
    try:
        update_id = ids[0]
        updated_doc = "Python is a versatile and beginner-friendly programming language"
        updated_metadata = {"topic": "programming", "id": 1, "updated": True}

        vector_store.update_documents([update_id], [updated_doc], [updated_metadata])
        print(f"  ✅ Successfully updated document: {update_id}")
    except Exception as e:
        print(f"  ❌ Failed to update documents: {e}")
        return False

    # Test 6: Delete documents
    print("\n✓ Test 6: Deleting documents...")
    try:
        delete_id = ids[3]
        vector_store.delete_documents([delete_id])
        print(f"  ✅ Successfully deleted document: {delete_id}")

        # Check updated count
        stats = vector_store.get_stats()
        print(f"     Remaining documents: {stats['count']}")
    except Exception as e:
        print(f"  ❌ Failed to delete documents: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ All tests passed successfully!")
    return True


if __name__ == "__main__":
    success = test_chroma_integration()
    sys.exit(0 if success else 1)
