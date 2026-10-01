"""Shared Amazon Bedrock Converse client supporting bearer API keys."""

import os
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import boto3
import requests

BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-6")
BEDROCK_REGION = os.getenv("AWS_REGION", "us-east-1")


def _normalize_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = []
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, str):
            content = [{"text": content}]
        elif isinstance(content, dict):
            content = [content]
        normalized.append({"role": message.get("role", "user"), "content": content})
    return normalized


def converse(
    model_id: str,
    messages: List[Dict[str, Any]],
    *,
    system: Optional[str] = None,
    inference_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Call Bedrock Converse using a bearer API key or the boto3 credential chain."""
    request_messages = _normalize_messages(messages)
    config = inference_config or {"maxTokens": 2048, "temperature": 0.7}
    bearer_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

    if bearer_token:
        payload: Dict[str, Any] = {
            "messages": request_messages,
            "inferenceConfig": config,
        }
        if system:
            payload["system"] = [{"text": system}]

        endpoint = (
            f"https://bedrock-runtime.{BEDROCK_REGION}.amazonaws.com/model/"
            f"{quote(model_id, safe='.:/')}/converse"
        )
        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=int(os.getenv("LLM_RESPONSE_TIMEOUT", "300")),
        )
        if not response.ok:
            try:
                error = response.json()
                message = error.get("message", error.get("__type", response.text))
            except ValueError:
                message = response.text
            raise RuntimeError(f"Bedrock Converse failed ({response.status_code}): {message}")
        return response.json()

    client = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
    request: Dict[str, Any] = {
        "modelId": model_id,
        "messages": request_messages,
        "inferenceConfig": config,
    }
    if system:
        request["system"] = [{"text": system}]
    return client.converse(**request)


def response_text(response: Dict[str, Any]) -> str:
    """Extract text blocks from a Bedrock Converse response."""
    content = response.get("output", {}).get("message", {}).get("content", [])
    return "".join(block.get("text", "") for block in content if isinstance(block, dict))