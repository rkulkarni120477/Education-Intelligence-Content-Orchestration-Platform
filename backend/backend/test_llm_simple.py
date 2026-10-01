#!/usr/bin/env python3
"""Test LLM connection to AWS Bedrock - Simple version."""

import os
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

load_dotenv(backend_dir / ".env", override=True)

from services.bedrock_runtime import BEDROCK_MODEL_ID, BEDROCK_REGION

print("=" * 60)
print("LLM CONNECTIVITY TEST")
print("=" * 60)

# Check credentials
print("\n1. Checking Bedrock configuration...")
bearer_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
aws_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
print(f"   AWS_REGION: {BEDROCK_REGION}")
print(f"   BEDROCK_MODEL_ID: {BEDROCK_MODEL_ID}")
print(f"   AWS_BEARER_TOKEN_BEDROCK: {'SET' if bearer_key else 'NOT SET'}")

if not bearer_key and not (aws_key and aws_secret):
    print("\n   ERROR: Bedrock credentials not found!")
    sys.exit(1)

print("\n6. Testing LLMService...")
try:
    from services.llm_service import LLMService
    print("   SUCCESS: LLMService imported")

    print("\n7. Calling LLMService.stream_message()...")
    response_text = ""
    for chunk in LLMService.stream_message(
        prompt="Reply with exactly: BEDROCK_OK",
        files=[],
        conversation_history=[],
        tenant_id="test"
    ):
        response_text += chunk
        print(f"      {chunk}", end='', flush=True)

    if not response_text or "**Error**" in response_text:
        print("\n   ERROR: LLM service returned an error or an empty response")
        sys.exit(1)

    print(f"\n   SUCCESS: LLM service working")

except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS: LLM CONNECTION WORKING!")
print("=" * 60)
