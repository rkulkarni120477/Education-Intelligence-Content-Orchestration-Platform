from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from database.models import Content
from knowledge.embeddings import EmbeddingManager, chunk_text

logger = logging.getLogger(__name__)


class ContentStudioAgent(BaseAgent):
    """AI Content Studio Agent - Content creation and management"""

    def __init__(self, db: Session):
        super().__init__("content_studio", db)
        self.embedding_manager = EmbeddingManager()

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process content creation and management tasks"""
        try:
            action = agent_input.data.get("action", "ingest")

            if action == "ingest":
                return await self._ingest_content(agent_input)
            elif action == "process":
                return await self._process_content(agent_input)
            elif action == "chunk_and_embed":
                return await self._chunk_and_embed(agent_input)
            else:
                return AgentOutput(
                    status="failed",
                    data={},
                    errors=[f"Unknown action: {action}"]
                )
        except Exception as e:
            logger.error(f"Content Studio Agent error: {e}")
            return AgentOutput(
                status="failed",
                data={},
                errors=[str(e)]
            )

    async def _ingest_content(self, agent_input: AgentInput) -> AgentOutput:
        """Ingest content from various sources"""
        content_type = agent_input.data.get("content_type", "document")
        title = agent_input.data.get("title", "Untitled")
        raw_content = agent_input.data.get("content", "")
        source = agent_input.data.get("source")

        # Create content record
        content = Content(
            title=title,
            content_type=content_type,
            source=source,
            raw_content=raw_content,
            metadata=agent_input.data.get("metadata", {}),
            status="ingested"
        )
        self.db.add(content)
        self.db.commit()

        return AgentOutput(
            status="success",
            data={
                "content_id": content.id,
                "title": content.title,
                "content_type": content.content_type,
                "message": f"Content ingested successfully"
            }
        )

    async def _process_content(self, agent_input: AgentInput) -> AgentOutput:
        """Process and validate content"""
        content_id = agent_input.data.get("content_id")

        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        # Validate content
        validation_errors = self._validate_content(content)
        if validation_errors:
            return AgentOutput(
                status="requires_review",
                data={"content_id": content_id},
                errors=validation_errors,
                requires_human_review=True,
                review_reason="Content validation failed"
            )

        content.status = "indexed"
        self.db.commit()

        return AgentOutput(
            status="success",
            data={
                "content_id": content_id,
                "status": "processed",
                "validation_passed": True
            }
        )

    async def _chunk_and_embed(self, agent_input: AgentInput) -> AgentOutput:
        """Chunk content and create embeddings"""
        content_id = agent_input.data.get("content_id")
        chunk_size = agent_input.data.get("chunk_size", 500)

        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        # Chunk text
        chunks = chunk_text(content.raw_content, chunk_size=chunk_size)

        # Create embeddings
        embeddings = self.embedding_manager.embed_batch([c for c in chunks])

        # Store embeddings
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.embedding_manager.store_embedding(
                self.db, content_id, idx, chunk, embedding
            )

        return AgentOutput(
            status="success",
            data={
                "content_id": content_id,
                "chunks_created": len(chunks),
                "embeddings_created": len(embeddings),
                "message": "Content chunked and embedded successfully"
            }
        )

    def _validate_content(self, content: Content) -> list:
        """Validate content quality"""
        errors = []

        if not content.title:
            errors.append("Content title is required")

        if not content.raw_content:
            errors.append("Content body is empty")

        if len(content.raw_content) < 10:
            errors.append("Content is too short")

        return errors
