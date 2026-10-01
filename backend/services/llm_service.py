"""LLM service for AWS Bedrock integration with streaming support."""

import logging
import os
from typing import Generator, List, Optional

from database.models import CustomContentFile
from services.bedrock_runtime import BEDROCK_MODEL_ID, BEDROCK_REGION, converse, response_text

logger = logging.getLogger(__name__)

MAX_FILE_CONTEXT_SIZE = int(os.getenv("LLM_MAX_FILE_CONTEXT_SIZE", 1000000))
STREAM_TIMEOUT = int(os.getenv("LLM_RESPONSE_TIMEOUT", 300))


class LLMService:
    """Handle LLM operations via AWS Bedrock."""

    @staticmethod
    def _build_file_context(files: List[CustomContentFile]) -> str:
        """Build context string from uploaded files.

        Args:
            files: List of CustomContentFile objects

        Returns:
            Formatted file context string
        """
        if not files:
            return ""

        context_parts = ["## Uploaded Files Context\n"]

        total_size = 0
        for file in files:
            # Add file metadata
            file_size_mb = file.size / (1024 * 1024)
            context_parts.append(f"\n### File: {file.name} ({file_size_mb:.2f}MB)")
            context_parts.append(f"Type: {file.mime_type}")
            context_parts.append(f"Uploaded: {file.created_at.isoformat()}\n")

            # Add file content (if available and not too large)
            if file.content and total_size < MAX_FILE_CONTEXT_SIZE:
                remaining_space = MAX_FILE_CONTEXT_SIZE - total_size
                content_to_add = file.content[:remaining_space]
                context_parts.append(f"```\n{content_to_add}\n```\n")
                total_size += len(content_to_add)

        if total_size >= MAX_FILE_CONTEXT_SIZE:
            context_parts.append("\n[... additional file content truncated due to size limits]\n")

        return "".join(context_parts)

    @staticmethod
    def _build_system_prompt(file_context: str, conversation_context: str = "") -> str:
        """Build system prompt with file context.

        Args:
            file_context: Context from uploaded files
            conversation_context: Previous conversation summary

        Returns:
            System prompt string
        """
        prompt_parts = [
            "You are a helpful AI assistant specialized in content creation and analysis.",
            "Your role is to help users create, analyze, and refine content based on their needs.",
            "",
        ]

        if file_context:
            prompt_parts.extend([
                "You have access to the following user-uploaded files:",
                file_context,
                "",
            ])

        if conversation_context:
            prompt_parts.extend([
                "Previous conversation context:",
                conversation_context,
                "",
            ])

        prompt_parts.extend([
            "Guidelines:",
            "- Be specific and actionable in your responses",
            "- Reference the uploaded files when relevant",
            "- Ask clarifying questions if needed",
            "- Provide structured output when helpful",
            "- Be concise but thorough",
        ])

        return "\n".join(prompt_parts)

    @classmethod
    def stream_message(
        cls,
        prompt: str,
        files: List[CustomContentFile],
        conversation_history: List[dict],
        tenant_id: str,
    ) -> Generator[str, None, None]:
        """Stream message response from Bedrock.

        Args:
            prompt: User message prompt
            files: List of uploaded files for context
            conversation_history: Previous messages (format: [{"role": "user"|"assistant", "content": "..."}])
            tenant_id: Tenant ID for logging

        Yields:
            Text chunks as they arrive from LLM
        """
        try:
            # Build file context
            file_context = cls._build_file_context(files)

            # Build system prompt
            system_prompt = cls._build_system_prompt(file_context)

            # Build messages for Bedrock API
            messages = []

            # Add conversation history
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": prompt,
            })

            logger.info(
                f"[{tenant_id}] Streaming message with {len(files)} files, "
                f"{len(conversation_history)} history items"
            )

            response = converse(
                BEDROCK_MODEL_ID,
                messages,
                system=system_prompt,
                inference_config={"maxTokens": 2048, "temperature": 0.7},
            )
            text = response_text(response)
            if text:
                yield text

            usage_stats = response.get("usage", {})
            logger.info(
                f"[{tenant_id}] Stream complete. Usage: "
                f"input={usage_stats.get('inputTokens', 0)}, "
                f"output={usage_stats.get('outputTokens', 0)}"
            )

        except Exception as e:
            logger.error(f"[{tenant_id}] Unexpected error in stream_message: {str(e)}", exc_info=True)
            yield f"\n\n**Error**: An unexpected error occurred: {str(e)}"

    @classmethod
    def get_model_info(cls) -> dict:
        """Get current model configuration.

        Returns:
            Model info dictionary
        """
        return {
            "model_id": BEDROCK_MODEL_ID,
            "region": BEDROCK_REGION,
            "max_context_size": MAX_FILE_CONTEXT_SIZE,
            "stream_timeout": STREAM_TIMEOUT,
        }
