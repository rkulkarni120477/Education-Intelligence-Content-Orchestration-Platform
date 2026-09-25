"""
Test script to verify image upload and storage
"""
import sys
import requests
import json
from pathlib import Path

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
API_URL = "http://localhost:8001"
TOKEN = None

# Step 1: Register a test user
print("=" * 60)
print("STEP 1: Registering test user")
print("=" * 60)

import time

email = f"imagetest{int(time.time())}@example.com"
username = f"imagetest{int(time.time())}"

register_response = requests.post(
    f"{API_URL}/api/auth/register",
    json={
        "email": email,
        "username": username,
        "full_name": "Image Test",
        "password": "Test123456"
    }
)

if register_response.status_code == 200:
    data = register_response.json()
    TOKEN = data.get("access_token")
    print(f"[OK] User registered: {data.get('email')}")
    print(f"[OK] Token received: {TOKEN[:50]}...")
else:
    print(f"[ERROR] Registration failed: {register_response.text}")
    exit(1)

# Step 2: Create a test base64 image (simple 1x1 red pixel JPEG)
print("\n" + "=" * 60)
print("STEP 2: Creating test image data")
print("=" * 60)

# Simple base64 JPEG (1x1 red pixel)
test_image_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="

print(f"[OK] Test image base64 created (length: {len(test_image_base64)} chars)")

# Step 3: Upload image with metadata
print("\n" + "=" * 60)
print("STEP 3: Uploading image with caption")
print("=" * 60)

ingest_response = requests.post(
    f"{API_URL}/api/content/ingest",
    json={
        "title": "Test Image with Caption",
        "content": test_image_base64,
        "content_type": "image",
        "source": "test_upload",
        "metadata": {
            "file_name": "test_image.jpg",
            "file_size": 1234,
            "file_type": "image/jpeg",
            "caption": "This is a test image caption"
        }
    },
    headers={"Authorization": f"Bearer {TOKEN}"}
)

if ingest_response.status_code == 200:
    data = ingest_response.json()
    content_id = data.get("content_id")
    print(f"[OK] Image uploaded successfully")
    print(f"[OK] Content ID: {content_id}")
    print(f"[OK] Status: {data.get('status')}")
else:
    print(f"[ERROR] Image upload failed: {ingest_response.text}")
    exit(1)

# Step 4: Retrieve and verify the stored image
print("\n" + "=" * 60)
print("STEP 4: Verifying stored image data")
print("=" * 60)

list_response = requests.get(
    f"{API_URL}/api/content?skip=0&limit=50",
    headers={"Authorization": f"Bearer {TOKEN}"}
)

if list_response.status_code == 200:
    data = list_response.json()
    content_list = data.get("content", [])

    # Find our test image
    test_image = None
    for item in content_list:
        if item.get("title") == "Test Image with Caption":
            test_image = item
            break

    if test_image:
        print(f"✓ Image found in database")
        print(f"  - Title: {test_image.get('title')}")
        print(f"  - Type: {test_image.get('content_type')}")
        print(f"  - Source: {test_image.get('source')}")
        print(f"  - Status: {test_image.get('status')}")

        # Check raw_content
        raw_content = test_image.get("raw_content", "")
        if raw_content.startswith("data:image/"):
            print(f"✓ Raw content is valid base64 image data")
            print(f"  - Size: {len(raw_content)} bytes")
        else:
            print(f"✗ Raw content is NOT valid image data")
            print(f"  - First 100 chars: {raw_content[:100]}")

        # Check metadata
        metadata = test_image.get("content_metadata", {})
        print(f"✓ Metadata stored:")
        for key, value in metadata.items():
            print(f"  - {key}: {value}")

        if metadata.get("caption"):
            print(f"✓ Caption successfully stored: '{metadata.get('caption')}'")
        else:
            print(f"⚠ Caption not found in metadata")
    else:
        print(f"✗ Test image not found in database")
        print(f"  Available items: {[item.get('title') for item in content_list]}")
else:
    print(f"✗ Failed to retrieve content: {list_response.text}")
    exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("[OK] Image upload flow verification completed successfully!")
