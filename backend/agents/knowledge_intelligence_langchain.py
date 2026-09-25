"""
Knowledge Intelligence Agent using LangChain
Ingests curriculum content, chunks it, tags it, and builds a knowledge graph.
"""

import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentChunk(BaseModel):
    """Represents a chunk of course content"""
    chunk_id: str
    source_module: str
    content: str
    chunk_type: str  # 'learning_objective', 'reading', 'assessment', etc.
    bloom_level: str  # Bloom's taxonomy level
    tags: List[str]
    embedded: bool = False


class KnowledgeGraph(BaseModel):
    """Represents the knowledge graph structure"""
    nodes: List[Dict[str, Any]]  # Courses, modules, outcomes, skills
    edges: List[Dict[str, Any]]  # Relationships between nodes
    total_nodes: int
    total_relationships: int


class KnowledgeIntelligenceAgentLangChain:
    """
    LangChain-based Knowledge Intelligence Agent

    Responsibilities:
    - Ingest IMSCC packages
    - Chunk content by module/lesson
    - Tag content with taxonomy (topics, Bloom's level, assessment type)
    - Build knowledge graph linking: course → module → outcome → skill
    """

    def __init__(self, db=None):
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.chunks: List[ContentChunk] = []
        self.knowledge_graph: Optional[KnowledgeGraph] = None

    async def process_curriculum(
        self,
        courses: Dict[str, Any],
        curriculum_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process curriculum files and build knowledge base.

        Args:
            courses: Dictionary of parsed course structures
            curriculum_metadata: Metadata about the curriculum

        Returns:
            Processing results with chunks and knowledge graph
        """
        self.logger.info(f"Processing {len(courses)} courses for knowledge intelligence")

        try:
            # Step 1: Chunk content by module and lesson
            await self._chunk_content(courses)
            self.logger.info(f"Created {len(self.chunks)} content chunks")

            # Step 2: Tag content with taxonomy
            await self._tag_content_taxonomy()
            self.logger.info("Tagged all chunks with taxonomy")

            # Step 3: Build knowledge graph
            self.knowledge_graph = await self._build_knowledge_graph(courses)
            self.logger.info(f"Built knowledge graph with {self.knowledge_graph.total_nodes} nodes")

            # Step 4: Create embeddings (placeholder for now)
            # In production, use OpenAI embeddings or similar
            await self._create_embeddings()

            return {
                "status": "completed",
                "chunks_created": len(self.chunks),
                "chunk_types": self._get_chunk_type_distribution(),
                "knowledge_graph": {
                    "total_nodes": self.knowledge_graph.total_nodes,
                    "total_relationships": self.knowledge_graph.total_relationships,
                    "node_types": self._get_node_type_distribution()
                },
                "taxonomy_coverage": self._get_taxonomy_coverage(),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error processing curriculum: {str(e)}")
            raise

    async def _chunk_content(self, courses: Dict[str, Any]) -> None:
        """Chunk content by module and learning objectives"""
        chunk_id = 0

        for course_path, course_data in courses.items():
            course_title = course_data.get('course_title', 'Unknown Course')

            # Process modules
            modules = course_data.get('modules', [])
            for module in modules:
                module_title = module.get('title', 'Unknown Module')

                # Chunk 1: Learning outcomes
                learning_outcomes = module.get('learning_outcomes', [])
                if learning_outcomes:
                    chunk_id += 1
                    chunk_content = "\n".join(learning_outcomes)
                    self.chunks.append(ContentChunk(
                        chunk_id=f"chunk_{chunk_id}",
                        source_module=f"{course_title} > {module_title}",
                        content=chunk_content,
                        chunk_type="learning_objectives",
                        bloom_level="remember",
                        tags=["learning_outcome"]
                    ))

                # Chunk 2: Content items
                content_items = module.get('content_items', [])
                for item in content_items:
                    chunk_id += 1
                    item_title = item.get('title', 'Unknown Item')
                    item_type = item.get('resource_type', 'resource')

                    self.chunks.append(ContentChunk(
                        chunk_id=f"chunk_{chunk_id}",
                        source_module=f"{course_title} > {module_title}",
                        content=f"{item_title}\nType: {item_type}",
                        chunk_type=item_type,
                        bloom_level="understand",
                        tags=[item_type, module_title.lower().replace(" ", "_")]
                    ))

                # Chunk 3: Assessments
                assessments = module.get('assessment_items', [])
                for assessment in assessments:
                    chunk_id += 1
                    assessment_title = assessment.get('title', 'Assessment')

                    self.chunks.append(ContentChunk(
                        chunk_id=f"chunk_{chunk_id}",
                        source_module=f"{course_title} > {module_title}",
                        content=f"Assessment: {assessment_title}",
                        chunk_type="assessment",
                        bloom_level="apply",
                        tags=["assessment", "evaluation"]
                    ))

    async def _tag_content_taxonomy(self) -> None:
        """Tag content with curriculum taxonomy"""
        # Bloom's taxonomy levels
        bloom_keywords = {
            "remember": ["list", "define", "identify", "label", "name"],
            "understand": ["explain", "describe", "discuss", "summarize"],
            "apply": ["solve", "demonstrate", "use", "implement"],
            "analyze": ["compare", "contrast", "examine", "distinguish"],
            "evaluate": ["judge", "justify", "support", "defend"],
            "create": ["design", "develop", "construct", "produce"]
        }

        # Topic keywords based on cybersecurity
        topic_keywords = {
            "networking": ["network", "tcp/ip", "protocols", "routing"],
            "cloud": ["cloud", "aws", "azure", "infrastructure"],
            "security": ["security", "encryption", "authentication", "access"],
            "incident response": ["incident", "response", "forensics", "recovery"],
            "compliance": ["compliance", "standard", "regulation", "requirement"]
        }

        for chunk in self.chunks:
            content_lower = chunk.content.lower()

            # Determine Bloom's level
            for level, keywords in bloom_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    chunk.bloom_level = level
                    break

            # Add topic tags
            for topic, keywords in topic_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    if topic not in chunk.tags:
                        chunk.tags.append(topic)

    async def _build_knowledge_graph(self, courses: Dict[str, Any]) -> KnowledgeGraph:
        """Build knowledge graph linking courses, modules, outcomes, and skills"""
        nodes = []
        edges = []
        node_id = 0

        # Create course nodes
        for course_path, course_data in courses.items():
            course_title = course_data.get('course_title', 'Unknown')
            node_id += 1
            course_node_id = node_id

            nodes.append({
                "id": f"node_{course_node_id}",
                "type": "course",
                "name": course_title,
                "metadata": {
                    "credit_hours": course_data.get('credit_hours', 3),
                    "description": course_data.get('course_description', '')
                }
            })

            # Create module nodes and link to course
            modules = course_data.get('modules', [])
            for module in modules:
                module_title = module.get('title', 'Unknown Module')
                node_id += 1
                module_node_id = node_id

                nodes.append({
                    "id": f"node_{module_node_id}",
                    "type": "module",
                    "name": module_title,
                    "parent_course": course_title
                })

                edges.append({
                    "source": f"node_{course_node_id}",
                    "target": f"node_{module_node_id}",
                    "relationship": "contains_module"
                })

                # Create learning outcome nodes
                for outcome in module.get('learning_outcomes', []):
                    node_id += 1
                    outcome_node_id = node_id

                    nodes.append({
                        "id": f"node_{outcome_node_id}",
                        "type": "learning_outcome",
                        "name": outcome
                    })

                    edges.append({
                        "source": f"node_{module_node_id}",
                        "target": f"node_{outcome_node_id}",
                        "relationship": "teaches"
                    })

        return KnowledgeGraph(
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_relationships=len(edges)
        )

    async def _create_embeddings(self) -> None:
        """Create vector embeddings for chunks (placeholder)"""
        # In production, use:
        # from langchain.embeddings.openai import OpenAIEmbeddings
        # embeddings = OpenAIEmbeddings()
        # vector = embeddings.embed_query(chunk.content)

        for chunk in self.chunks:
            # Simple placeholder: mark as embedded
            chunk.embedded = True

        self.logger.info(f"Created embeddings for {len(self.chunks)} chunks")

    def _get_chunk_type_distribution(self) -> Dict[str, int]:
        """Get distribution of chunk types"""
        distribution = {}
        for chunk in self.chunks:
            distribution[chunk.chunk_type] = distribution.get(chunk.chunk_type, 0) + 1
        return distribution

    def _get_node_type_distribution(self) -> Dict[str, int]:
        """Get distribution of node types in knowledge graph"""
        distribution = {}
        if self.knowledge_graph:
            for node in self.knowledge_graph.nodes:
                node_type = node.get('type', 'unknown')
                distribution[node_type] = distribution.get(node_type, 0) + 1
        return distribution

    def _get_taxonomy_coverage(self) -> Dict[str, int]:
        """Get Bloom's taxonomy coverage"""
        coverage = {}
        for chunk in self.chunks:
            level = chunk.bloom_level
            coverage[level] = coverage.get(level, 0) + 1
        return coverage

    def get_chunks_for_skill(self, skill: str) -> List[ContentChunk]:
        """Get all chunks related to a specific skill"""
        return [chunk for chunk in self.chunks if skill.lower() in [tag.lower() for tag in chunk.tags]]

    def get_related_content(self, chunk_id: str, limit: int = 5) -> List[ContentChunk]:
        """Get content chunks related to a given chunk"""
        source_chunk = next((c for c in self.chunks if c.chunk_id == chunk_id), None)
        if not source_chunk:
            return []

        # Find chunks with overlapping tags
        related = []
        for chunk in self.chunks:
            if chunk.chunk_id == chunk_id:
                continue

            overlap = len(set(chunk.tags) & set(source_chunk.tags))
            if overlap > 0:
                related.append((chunk, overlap))

        # Sort by overlap count and return top N
        related.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in related[:limit]]
