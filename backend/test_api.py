"""Test script for backend API endpoints"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n🧪 Testing API Endpoints")
    print("=" * 50)
    print("\n✓ Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ Health check passed")
            print(f"     Response: {response.json()}")
            return True
        else:
            print(f"  ❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False

def test_add_documents():
    """Test adding documents to vector store"""
    print("\n✓ Test 2: Add Documents")
    try:
        payload = {
            "documents": [
                "Python is a powerful programming language",
                "Machine learning transforms industries",
                "Education technology is evolving rapidly"
            ],
            "metadatas": [
                {"topic": "programming", "id": 1},
                {"topic": "ml", "id": 2},
                {"topic": "edtech", "id": 3}
            ],
            "collection": "academian_content"
        }

        response = requests.post(f"{BASE_URL}/api/documents/add", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Documents added successfully")
            print(f"     Count: {len(result.get('ids', []))}")
            return True, result.get('ids', [])
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            print(f"     Response: {response.text}")
            return False, []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False, []

def test_search_documents():
    """Test searching documents"""
    print("\n✓ Test 3: Search Documents")
    try:
        payload = {
            "query": "machine learning and education",
            "n_results": 3,
            "collection": "academian_content"
        }

        response = requests.post(f"{BASE_URL}/api/documents/search", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Search completed successfully")
            print(f"     Results: {len(result.get('results', {}).get('documents', [[]])[0])}")
            return True
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_collection_stats():
    """Test getting collection statistics"""
    print("\n✓ Test 4: Collection Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/collections/academian_content/stats", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Statistics retrieved successfully")
            print(f"     Count: {result.get('stats', {}).get('count', 0)}")
            return True
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🚀 Backend API Test Suite")

    # Test health check first
    if not test_health():
        print("\n❌ Backend is not responding. Make sure it's running on port 8000")
        print("   Start it with: python -m uvicorn app:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # Test document operations
    success, ids = test_add_documents()

    if success:
        test_search_documents()
        test_collection_stats()

    print("\n" + "=" * 50)
    print("✅ API tests completed!")

if __name__ == "__main__":
    main()
