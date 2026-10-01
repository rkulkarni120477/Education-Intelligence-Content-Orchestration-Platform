#!/usr/bin/env python3
"""Test LLM connection to AWS Bedrock."""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env", override=True)

from services.bedrock_runtime import BEDROCK_MODEL_ID, BEDROCK_REGION

print("=" * 60)
print("LLM CONNECTIVITY TEST")
print("=" * 60)

# Test 1: Check supported credential configuration
print("\n1. Checking Bedrock configuration...")
bearer_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
print(f"   AWS_REGION: {BEDROCK_REGION}")
print(f"   BEDROCK_MODEL_ID: {BEDROCK_MODEL_ID}")
print(f"   AWS_BEARER_TOKEN_BEDROCK: {'SET' if bearer_key else 'NOT SET'}")

if not bearer_key and not (aws_key and aws_secret):
    print("\nBedrock credentials were not found in backend/.env or the environment.")
    sys.exit(1)

# Test 6: Import LLM Service
print("\n6. Testing LLMService import...")
try:
    from services.llm_service import LLMService
    print("   ✅ LLMService imported")
except Exception as e:
    print(f"   ❌ Failed to import LLMService: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 7: Test LLMService.stream_message
print("\n7. Testing LLMService.stream_message()...")
try:
    prompt = "Reply with exactly: BEDROCK_OK"
    files = []
    history = []

    print(f"   Calling LLMService.stream_message('{prompt}')...")

    response_text = ""
    for chunk in LLMService.stream_message(
        prompt=prompt,
        files=files,
        conversation_history=history,
        tenant_id="test-tenant"
    ):
        response_text += chunk
        print(f"   📝 {chunk}", end='', flush=True)

    if not response_text or "**Error**" in response_text:
        print("\n   ❌ LLM service returned an error or an empty response")
        sys.exit(1)

    print(f"\n   ✅ LLM Response: {response_text}")

except Exception as e:
    print(f"   ❌ LLMService.stream_message failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED - LLM CONNECTIVITY WORKING!")
print("=" * 60)
