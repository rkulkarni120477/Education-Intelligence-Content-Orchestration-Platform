from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from typing import Dict, Any, Optional, List
import logging
from sqlalchemy.orm import Session
from database.models import Content, ContentEmbedding, KnowledgeContext
from knowledge.embeddings import EmbeddingManager
from knowledge.context import KnowledgeContextManager

logger = logging.getLogger(__name__)


class KnowledgeIntelligenceAgent(BaseAgent):
    """Knowledge Intelligence Agent - Centralized knowledge management"""

    def __init__(self, db: Session):
        super().__init__("knowledge_intelligence", db)
        self.embedding_manager = EmbeddingManager()

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process knowledge management tasks"""
        try:
            action = agent_input.data.get("action", "search")

            if action == "search":
                return await self._search_knowledge(agent_input)
            elif action == "extract_concepts":
                return await self._extract_concepts(agent_input)
            elif action == "build_knowledge_graph":
                return await self._build_knowledge_graph(agent_input)
            elif action == "ingest_knowledge":
                return await self._ingest_knowledge(agent_input)
            elif action == "retrieve_context":
                return await self._retrieve_context(agent_input)
            else:
                return AgentOutput(
                    status="failed",
                    data={},
                    errors=[f"Unknown action: {action}"]
                )
        except Exception as e:
            logger.error(f"Knowledge Intelligence Agent error: {e}")
            return AgentOutput(
                status="failed",
                data={},
                errors=[str(e)]
            )

    async def _search_knowledge(self, agent_input: AgentInput) -> AgentOutput:
        """Search knowledge base using semantic similarity"""
        query = agent_input.data.get("query", "")
        top_k = agent_input.data.get("top_k", 5)
        content_type = agent_input.data.get("content_type")

        if not query:
            return AgentOutput(
                status="failed",
                data={},
                errors=["Query is required"]
            )

        # Embed query
        query_embedding = self.embedding_manager.embed_text(query)

        # Search embeddings
        all_embeddings = self.db.query(ContentEmbedding).all()

        results = []
        for emb in all_embeddings:
            similarity = self.embedding_manager.similarity(
                query_embedding, emb.embedding
            )
            results.append({
                "content_id": emb.content_id,
                "chunk_index": emb.chunk_index,
                "text": emb.text_chunk[:200],  # Preview
                "similarity_score": similarity
            })

        # Sort and limit
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = results[:top_k]

        return AgentOutput(
            status="success",
            data={
                "query": query,
                "results_count": len(results),
                "results": results
            }
        )

    async def _extract_concepts(self, agent_input: AgentInput) -> AgentOutput:
        """Extract key concepts from content"""
        content_id = agent_input.data.get("content_id")

        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return AgentOutput(
                status="failed",
                data={},
                errors=[f"Content not found: {content_id}"]
            )

        # Extract concepts using LLM
        prompt = f"""Extract 5-10 key concepts from the following text:

{content.raw_content[:1000]}

Return as a JSON array of concepts."""

        try:
            concepts_text = await self.invoke_llm(prompt)
            # Parse concepts (in production, use proper JSON parsing)
            concepts = concepts_text.split("\n")
            concepts = [c.strip().strip('"').strip(",") for c in concepts if c.strip()]

            return AgentOutput(
                status="success",
                data={
                    "content_id": content_id,
                    "concepts": concepts[:10],
                    "concept_count": len(concepts)
                }
            )
        except Exception as e:
            return AgentOutput(
                status="failed",
                data={},
                errors=[str(e)]
            )

    async def _build_knowledge_graph(self, agent_input: AgentInput) -> AgentOutput:
        """Build knowledge graph from content"""
        content_ids = agent_input.data.get("content_ids", [])

        if not content_ids:
            # Use all content
            contents = self.db.query(Content).all()
            content_ids = [c.id for c in contents]

        # Build graph structure
        nodes = []
        edges = []

        for content_id in content_ids[:10]:  # Limit for performance
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if content:
                nodes.append({
                    "id": content.id,
                    "label": content.title,
                    "type": content.content_type
                })

        # Create edges based on semantic similarity
        embeddings = self.db.query(ContentEmbedding).filter(
            ContentEmbedding.content_id.in_(content_ids[:10])
        ).all()

        for i, emb1 in enumerate(embeddings):
            for emb2 in embeddings[i+1:]:
                similarity = self.embedding_manager.similarity(
                    emb1.embedding, emb2.embedding
                )
                if similarity > 0.7:  # High similarity threshold
                    edges.append({
                        "source": emb1.content_id,
                        "target": emb2.content_id,
                        "weight": similarity
                    })

        return AgentOutput(
            status="success",
            data={
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
        )

    async def _ingest_knowledge(self, agent_input: AgentInput) -> AgentOutput:
        """Ingest external knowledge sources"""
        knowledge_source = agent_input.data.get("source")
        knowledge_data = agent_input.data.get("data")
        knowledge_type = agent_input.data.get("type", "general")

        if not knowledge_source or not knowledge_data:
            return AgentOutput(
                status="failed",
                data={},
                errors=["Knowledge source and data are required"]
            )

        # Store in knowledge context
        context_key = f"knowledge:{knowledge_type}:{knowledge_source}"
        KnowledgeContextManager.set_context(
            self.db,
            context_key,
            knowledge_data,
            metadata={"source": knowledge_source, "type": knowledge_type}
        )

        return AgentOutput(
            status="success",
            data={
                "source": knowledge_source,
                "type": knowledge_type,
                "context_key": context_key,
                "message": f"Knowledge from {knowledge_source} ingested successfully"
            }
        )

    async def _retrieve_context(self, agent_input: AgentInput) -> AgentOutput:
        """Retrieve contextual information for agents"""
        context_type = agent_input.data.get("type", "general")
        agent_type = agent_input.data.get("agent_type")
        max_items = agent_input.data.get("max_items", 10)

        # Retrieve relevant contexts
        contexts = KnowledgeContextManager.list_contexts(self.db, f"{context_type}:")

        retrieved_contexts = []
        for context in contexts[:max_items]:
            retrieved_contexts.append({
                "key": context.key,
                "value": context.value,
                "version": context.version,
                "updated_at": context.updated_at.isoformat()
            })

        return AgentOutput(
            status="success",
            data={
                "context_type": context_type,
                "agent_type": agent_type,
                "contexts_retrieved": len(retrieved_contexts),
                "contexts": retrieved_contexts
            }
        )
