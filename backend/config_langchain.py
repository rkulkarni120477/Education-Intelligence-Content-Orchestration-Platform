"""
LangChain Configuration
Setup for OpenAI, embeddings, and agent tools
"""

import logging
from typing import Optional
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class LangChainConfig:
    """Configuration for LangChain integrations"""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

    # Embeddings Configuration
    EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")

    # Vector Store Configuration
    VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "chroma")  # chroma, pinecone, weaviate
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "curriculum_content")

    # Agent Configuration
    AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "300"))
    AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "false").lower() == "true"

    # Caching
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))

    @classmethod
    def validate_config(cls) -> bool:
        """Validate critical configuration"""
        if not cls.OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set. LangChain agents will not work.")
            return False

        logger.info(f"LangChain Config: Model={cls.OPENAI_MODEL}, Embeddings={cls.EMBEDDINGS_MODEL}")
        return True


# Initialize LangChain components
def initialize_langchain():
    """Initialize LangChain with OpenAI"""
    try:
        from langchain.chat_models import ChatOpenAI
        from langchain.embeddings import OpenAIEmbeddings

        # Initialize LLM
        llm = ChatOpenAI(
            model_name=LangChainConfig.OPENAI_MODEL,
            temperature=LangChainConfig.OPENAI_TEMPERATURE,
            max_tokens=LangChainConfig.OPENAI_MAX_TOKENS,
            openai_api_key=LangChainConfig.OPENAI_API_KEY
        )

        # Initialize Embeddings
        embeddings = OpenAIEmbeddings(
            model=LangChainConfig.EMBEDDINGS_MODEL,
            openai_api_key=LangChainConfig.OPENAI_API_KEY
        )

        logger.info("LangChain initialized with OpenAI")
        return llm, embeddings

    except ImportError:
        logger.error("LangChain packages not installed. Install with: pip install langchain openai")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize LangChain: {str(e)}")
        raise


# Prompt Templates for agents
class PromptTemplates:
    """Prompt templates for curriculum agents"""

    # Content Generation Template
    GENERATE_MODULE_PROMPT = """You are an expert instructional designer and subject matter expert in cybersecurity education.

Based on the following information, create a comprehensive course module that fills a skill gap:

**Module Title:** {module_title}
**Target Skill/Competency:** {competency}
**Bloom's Level:** {bloom_level}
**Duration:** {estimated_hours} hours
**Target Audience:** {target_audience}
**Learning Outcomes:**
{learning_outcomes}

**Curriculum Context:**
- Existing curriculum covers: {covered_topics}
- Missing topics: {gap_areas}
- Related courses: {related_courses}

Please generate:
1. **Module Overview** - 2-3 sentence description
2. **Learning Outcomes** - 3-5 specific outcomes aligned to {bloom_level}
3. **Content Structure** - Outline with 3-5 lessons
4. **Lesson Details** - For first lesson:
   - Lesson title
   - Duration estimate
   - Key concepts
   - Learning activities
   - Assessment methods
5. **Resources Needed** - Tools, materials, prerequisites
6. **Assessment Strategy** - How to measure learning
7. **Accessibility Notes** - WCAG 2.1 AA compliance considerations

Format the output as clear, organized sections with bullet points."""

    # Gap Analysis Prompt
    ANALYZE_GAP_PROMPT = """Analyze the following curriculum gap and provide recommendations:

**Competency:** {competency_name}
**Required by Roles:** {roles}
**Current Coverage:** {current_coverage}%
**Target Coverage:** {target_coverage}%

**Existing Curriculum:**
{existing_content}

**Industry Standards:**
{industry_standards}

Provide:
1. **Gap Analysis** - What's missing and why it matters
2. **Recommended Topics** - Specific topics to add
3. **Sequence** - Order of topic introduction
4. **Depth vs Breadth** - How deeply to cover each topic
5. **Practice Activities** - Hands-on exercises needed
6. **Assessment Methods** - How to measure competency
7. **Prerequisites** - What students should know first"""

    # Content Review Prompt
    REVIEW_CONTENT_PROMPT = """Review the following generated course content for quality and alignment:

**Content Type:** {content_type}
**Target Competency:** {competency}
**Target Audience:** {target_audience}

**Content to Review:**
{content}

**Review Criteria:**
- Accuracy (Is it technically correct?)
- Clarity (Is it easy to understand?)
- Completeness (Does it cover the competency?)
- Alignment (Does it match curriculum goals?)
- Accessibility (Is it WCAG compliant?)
- Engagement (Is it engaging and interactive?)

Provide:
1. **Overall Assessment** - Pass/Needs Revision/Fail
2. **Strengths** - What works well
3. **Issues** - What needs improvement
4. **Specific Recommendations** - How to fix issues
5. **Accessibility Compliance** - WCAG items to address
6. **Suggested Revisions** - Concrete edits needed"""

    # Accessibility Check Prompt
    CHECK_ACCESSIBILITY_PROMPT = """Check the following content for WCAG 2.1 AA accessibility compliance:

**Content:**
{content}

**Checklist Items:**
- Is all text clear and at appropriate reading level?
- Are all images properly described with alt text?
- Is color not the only means of conveying information?
- Is the content structured with proper headings?
- Are lists properly formatted?
- Are hyperlinks descriptive?
- Can content be understood without color?
- Is there sufficient contrast (4.5:1 for normal text)?

Provide:
1. **Compliance Status** - WCAG AA Pass/Fail
2. **Accessibility Issues Found** - List with severity
3. **Alt Text Recommendations** - For images
4. **Readability Issues** - Sentence complexity, etc.
5. **Structure Recommendations** - Heading hierarchy, etc.
6. **Color/Contrast Issues** - Specific items
7. **Remediation Steps** - How to fix each issue"""


def get_llm():
    """Get initialized LLM instance"""
    try:
        from langchain.chat_models import ChatOpenAI
        return ChatOpenAI(
            model_name=LangChainConfig.OPENAI_MODEL,
            temperature=LangChainConfig.OPENAI_TEMPERATURE,
            openai_api_key=LangChainConfig.OPENAI_API_KEY
        )
    except Exception as e:
        logger.error(f"Failed to get LLM: {str(e)}")
        return None


def get_embeddings():
    """Get initialized embeddings instance"""
    try:
        from langchain.embeddings import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=LangChainConfig.EMBEDDINGS_MODEL,
            openai_api_key=LangChainConfig.OPENAI_API_KEY
        )
    except Exception as e:
        logger.error(f"Failed to get embeddings: {str(e)}")
        return None
