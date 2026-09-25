"""Agents API - Monitor registered workflow agents and AI provider usage."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from database.db import get_db
from database.models import (
    WorkflowExecution, AgentRun, Tenant
)
from auth.tenant_context import get_current_tenant_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/agents", tags=["agents"])


# ===== RESPONSE MODELS =====

class AgentInfo(BaseModel):
    """Information about a registered agent/workflow node."""
    id: str
    name: str
    description: str
    agent_type: str
    status: str  # active, disabled, degraded, not_configured
    workflow_count: int
    last_used: Optional[datetime] = None

    class Config:
        from_attributes = True


class AIProviderStats(BaseModel):
    """AI provider usage statistics."""
    provider: str
    model: Optional[str] = None
    credential_label: Optional[str] = None  # Safe alias, never the actual key
    workflow_agent: Optional[str] = None
    requests: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: Optional[float] = None
    last_used: Optional[datetime] = None
    status: str  # active, inactive, error


class AgentListResponse(BaseModel):
    """List of registered agents."""
    agents: List[AgentInfo]
    total: int


class AIStatsResponse(BaseModel):
    """AI provider usage statistics."""
    stats: List[AIProviderStats]
    total_requests: int
    total_tokens: int
    estimated_total_cost: Optional[float] = None
    period: str  # "24h", "7d", "30d", "custom"
    start_date: datetime
    end_date: datetime


# ===== HARDCODED AGENT REGISTRY =====
# In production, this would be loaded from database or configuration

REGISTERED_AGENTS = {
    "validate_request_and_access": {
        "name": "Request Validator",
        "description": "Validates workflow request, tenant context, and user permissions",
        "agent_type": "validation",
        "status": "active",
    },
    "inspect_package_contents": {
        "name": "Package Inspector",
        "description": "Inspects course package contents and validates format",
        "agent_type": "validation",
        "status": "active",
    },
    "extract_requirements": {
        "name": "Requirements Extractor",
        "description": "Extracts institution requirements using Claude AI",
        "agent_type": "ai_powered",
        "status": "active",
    },
    "ingest_and_normalize_course_materials": {
        "name": "Course Ingestion Engine",
        "description": "Ingests and normalizes course materials from packages",
        "agent_type": "data_processing",
        "status": "active",
    },
    "retrieve_authorized_context": {
        "name": "Context Retriever",
        "description": "Retrieves authorized context for analysis",
        "agent_type": "retrieval",
        "status": "active",
    },
    "map_workforce_skills": {
        "name": "Skill Mapper",
        "description": "Maps workforce skills to course content using AI",
        "agent_type": "ai_powered",
        "status": "active",
    },
    "calculate_coverage_and_gaps": {
        "name": "Gap Analyzer",
        "description": "Calculates skill coverage and identifies gaps",
        "agent_type": "analysis",
        "status": "active",
    },
    "draft_recommendations": {
        "name": "Recommendation Engine",
        "description": "Drafts course improvement recommendations",
        "agent_type": "ai_powered",
        "status": "active",
    },
    "generate_course_updates": {
        "name": "Content Generator",
        "description": "Generates updated course materials",
        "agent_type": "data_processing",
        "status": "active",
    },
    "accessibility_check": {
        "name": "Accessibility Auditor",
        "description": "Runs accessibility audit on course materials",
        "agent_type": "compliance",
        "status": "active",
    },
    "persist_artifacts": {
        "name": "Data Persister",
        "description": "Persists workflow results to database",
        "agent_type": "storage",
        "status": "active",
    },
    "emit_audit_events": {
        "name": "Audit Logger",
        "description": "Emits audit events for compliance tracking",
        "agent_type": "compliance",
        "status": "active",
    },
}

# AI Provider configurations (safe, non-secret metadata)
AI_PROVIDERS = {
    "anthropic": {
        "provider": "Anthropic",
        "models": ["claude-opus-5-5", "claude-sonnet-5", "claude-haiku-4-5"],
        "status": "active",
    },
    "openai": {
        "provider": "OpenAI",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "status": "active",
    },
}


# ===== API ENDPOINTS =====

@router.get("/", response_model=AgentListResponse)
async def list_agents(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """
    Get list of registered agents and their workflow usage.

    Shows all available agents/workflow nodes and how many times each
    has been used in executions within the current tenant.
    """
    try:
        agents_list = []

        for agent_id, agent_config in REGISTERED_AGENTS.items():
            # Count workflows using this agent
            workflow_count = db.query(func.count(AgentRun.id)).filter(
                AgentRun.tenant_id == tenant_id,
                AgentRun.agent_name == agent_id,
            ).scalar() or 0

            # Get last usage time
            last_run = db.query(AgentRun).filter(
                AgentRun.tenant_id == tenant_id,
                AgentRun.agent_name == agent_id,
            ).order_by(AgentRun.completed_at.desc()).first()

            agent = AgentInfo(
                id=agent_id,
                name=agent_config["name"],
                description=agent_config["description"],
                agent_type=agent_config["agent_type"],
                status=agent_config["status"],
                workflow_count=workflow_count,
                last_used=last_run.completed_at if last_run else None,
            )
            agents_list.append(agent)

        # Sort by last_used (most recent first)
        agents_list.sort(
            key=lambda x: x.last_used or datetime.min,
            reverse=True
        )

        logger.info(f"✓ Listed {len(agents_list)} agents for tenant {tenant_id}")

        return AgentListResponse(
            agents=agents_list,
            total=len(agents_list),
        )

    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent_details(
    agent_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """
    Get detailed information about a specific agent.

    Includes description, workflows using it, recent runs, and configuration.
    """
    try:
        if agent_id not in REGISTERED_AGENTS:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent_config = REGISTERED_AGENTS[agent_id]

        # Get agent runs
        recent_runs = db.query(AgentRun).filter(
            AgentRun.tenant_id == tenant_id,
            AgentRun.agent_name == agent_id,
        ).order_by(AgentRun.completed_at.desc()).limit(10).all()

        # Calculate stats
        total_runs = db.query(func.count(AgentRun.id)).filter(
            AgentRun.tenant_id == tenant_id,
            AgentRun.agent_name == agent_id,
        ).scalar() or 0

        successful_runs = db.query(func.count(AgentRun.id)).filter(
            AgentRun.tenant_id == tenant_id,
            AgentRun.agent_name == agent_id,
            AgentRun.status == "completed",
        ).scalar() or 0

        failed_runs = db.query(func.count(AgentRun.id)).filter(
            AgentRun.tenant_id == tenant_id,
            AgentRun.agent_name == agent_id,
            AgentRun.status == "failed",
        ).scalar() or 0

        return {
            "id": agent_id,
            "name": agent_config["name"],
            "description": agent_config["description"],
            "agent_type": agent_config["agent_type"],
            "status": agent_config["status"],
            "stats": {
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "success_rate": (successful_runs / total_runs * 100) if total_runs > 0 else 0,
            },
            "recent_runs": [
                {
                    "id": run.id,
                    "status": run.status,
                    "started_at": run.started_at,
                    "completed_at": run.completed_at,
                    "error_message": run.error_message,
                }
                for run in recent_runs
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/ai-usage", response_model=AIStatsResponse)
async def get_ai_statistics(
    period: str = Query("30d", description="Time period: 24h, 7d, 30d"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """
    Get AI provider usage statistics.

    Shows request counts, token consumption, and estimated costs
    for the selected time period.
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "24h":
            start_date = end_date - timedelta(hours=24)
        elif period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=30)

        stats_list = []
        total_requests = 0
        total_tokens = 0
        estimated_total_cost = 0.0

        # Get statistics from agent runs (simplified; in production, would use dedicated telemetry)
        for agent_id, agent_config in REGISTERED_AGENTS.items():
            if agent_config["agent_type"] != "ai_powered":
                continue

            # Count requests
            request_count = db.query(func.count(AgentRun.id)).filter(
                AgentRun.tenant_id == tenant_id,
                AgentRun.agent_name == agent_id,
                AgentRun.status == "completed",
                AgentRun.completed_at >= start_date,
                AgentRun.completed_at <= end_date,
            ).scalar() or 0

            if request_count == 0:
                continue

            # Placeholder token counts (in production, would be from actual provider metrics)
            input_tokens = request_count * 500  # Estimated
            output_tokens = request_count * 300  # Estimated
            total_agent_tokens = input_tokens + output_tokens

            # Estimated cost (Anthropic Claude 3.5 Sonnet pricing)
            # Input: $3/M tokens, Output: $15/M tokens
            estimated_cost = (input_tokens * 3 / 1_000_000) + (output_tokens * 15 / 1_000_000)

            stat = AIProviderStats(
                provider="Anthropic",
                model="claude-opus-5-5",
                credential_label="anthropic-key-prod",  # Safe label only
                workflow_agent=agent_id,
                requests=request_count,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_agent_tokens,
                estimated_cost=estimated_cost,
                last_used=db.query(AgentRun).filter(
                    AgentRun.tenant_id == tenant_id,
                    AgentRun.agent_name == agent_id,
                ).order_by(AgentRun.completed_at.desc()).first().completed_at,
                status="active" if request_count > 0 else "inactive",
            )

            stats_list.append(stat)
            total_requests += request_count
            total_tokens += total_agent_tokens
            estimated_total_cost += estimated_cost

        logger.info(f"✓ AI usage stats: {total_requests} requests, {total_tokens} tokens for tenant {tenant_id}")

        return AIStatsResponse(
            stats=stats_list,
            total_requests=total_requests,
            total_tokens=total_tokens,
            estimated_total_cost=estimated_total_cost,
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

    except Exception as e:
        logger.error(f"Error getting AI statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
