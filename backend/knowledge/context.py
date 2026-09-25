from typing import Any, Dict, List, Optional
from database.models import KnowledgeContext
from sqlalchemy.orm import Session
import json
from datetime import datetime


class KnowledgeContextManager:
    """Manages shared knowledge context across all agents"""

    @staticmethod
    def set_context(db: Session, key: str, value: Any, metadata: Optional[Dict] = None) -> KnowledgeContext:
        """Store or update a knowledge context entry"""
        existing = db.query(KnowledgeContext).filter(KnowledgeContext.key == key).first()

        if existing:
            existing.value = value if isinstance(value, dict) else {"data": value}
            existing.metadata = metadata
            existing.version += 1
            existing.updated_at = datetime.utcnow()
        else:
            existing = KnowledgeContext(
                key=key,
                value=value if isinstance(value, dict) else {"data": value},
                metadata=metadata or {},
                version=1
            )
            db.add(existing)

        db.commit()
        db.refresh(existing)
        return existing

    @staticmethod
    def get_context(db: Session, key: str) -> Optional[Any]:
        """Retrieve a knowledge context entry"""
        context = db.query(KnowledgeContext).filter(KnowledgeContext.key == key).first()
        return context.value if context else None

    @staticmethod
    def delete_context(db: Session, key: str) -> bool:
        """Delete a knowledge context entry"""
        result = db.query(KnowledgeContext).filter(KnowledgeContext.key == key).delete()
        db.commit()
        return result > 0

    @staticmethod
    def list_contexts(db: Session, prefix: Optional[str] = None) -> List[KnowledgeContext]:
        """List all context entries, optionally filtered by prefix"""
        query = db.query(KnowledgeContext)
        if prefix:
            query = query.filter(KnowledgeContext.key.startswith(prefix))
        return query.all()

    @staticmethod
    def get_context_version(db: Session, key: str) -> Optional[int]:
        """Get current version of a context entry"""
        context = db.query(KnowledgeContext).filter(KnowledgeContext.key == key).first()
        return context.version if context else None

    @staticmethod
    def merge_context(db: Session, key: str, updates: Dict) -> KnowledgeContext:
        """Merge updates into existing context"""
        context = db.query(KnowledgeContext).filter(KnowledgeContext.key == key).first()

        if context:
            if isinstance(context.value, dict):
                context.value.update(updates)
            else:
                context.value = {"data": context.value, **updates}
            context.version += 1
            context.updated_at = datetime.utcnow()
        else:
            context = KnowledgeContext(
                key=key,
                value=updates,
                version=1
            )
            db.add(context)

        db.commit()
        db.refresh(context)
        return context


class ContextualInformation:
    """Provides contextual information to agents"""

    @staticmethod
    def get_agent_context(db: Session, agent_type: str) -> Dict[str, Any]:
        """Get all context relevant to a specific agent type"""
        contexts = KnowledgeContext.query.filter(
            KnowledgeContext.key.startswith(f"{agent_type}:")
        ).all()

        result = {}
        for context in contexts:
            key_suffix = context.key.split(":", 1)[1]
            result[key_suffix] = context.value

        return result

    @staticmethod
    def get_shared_skills(db: Session) -> Dict[str, Any]:
        """Get shared skills and competencies"""
        return KnowledgeContextManager.get_context(db, "shared:skills") or {}

    @staticmethod
    def get_shared_standards(db: Session) -> Dict[str, Any]:
        """Get shared standards and frameworks"""
        return KnowledgeContextManager.get_context(db, "shared:standards") or {}

    @staticmethod
    def get_content_guidelines(db: Session) -> Dict[str, Any]:
        """Get content creation guidelines"""
        return KnowledgeContextManager.get_context(db, "shared:content_guidelines") or {}
