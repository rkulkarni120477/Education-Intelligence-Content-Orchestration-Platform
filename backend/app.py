from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Header
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime, timedelta
import uuid
import asyncio
from pydantic import BaseModel
import hashlib
import secrets

from config import get_settings
from database.db import init_db, get_db, SessionLocal
from auth.auth import (
    authenticate_user, create_user, decode_token, create_access_token, get_user_by_id,
    generate_password_reset_token, verify_password_reset_token, reset_password,
    generate_email_verification_token, verify_email_token, get_user_by_email, update_last_login
)
from database.models import User, Project, Workflow, Content, Skill, WorkflowExecution, AgentRun, UserPreferences, ApiKey
# Note: Lesson now defined in models.py as part of core domain model
# from database.content_models import Course, Unit, Lesson  # Commented to avoid model conflicts
from services.email_service import get_email_service
from middleware.tenant_middleware import TenantMiddleware

# Agent infrastructure
from agents.base_agent import AgentFactory
from agents.intake_agent import IntakeAgent
from agents.standards_agent import StandardsAgent
from agents.curriculum_agent import CurriculumAgent
from agents.alignment_agent import AlignmentAgent
from agents.lesson_agent import LessonAgent
from agents.assessment_agent import AssessmentAgent

from api_routes import router as api_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-Agent AI Platform for Educational Content Creation"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tenant middleware for multi-tenancy
app.add_middleware(TenantMiddleware)

# Register agents with factory
AgentFactory.register("intake", IntakeAgent)
AgentFactory.register("standards", StandardsAgent)
AgentFactory.register("curriculum", CurriculumAgent)
AgentFactory.register("alignment", AlignmentAgent)
AgentFactory.register("lesson", LessonAgent)
AgentFactory.register("assessment", AssessmentAgent)

logger.info("[OK] Agents registered: %s", ", ".join(AgentFactory.list_agents()))

# Include API routes
app.include_router(api_router)

# Generic project workflows are lightweight records until a persistent execution is created.
project_workflow_understanding: Dict[str, Dict[str, Any]] = {}
project_workflow_executions: Dict[str, Dict[str, Any]] = {}


async def _run_project_workflow(
    workflow_id: str,
    project_id: str,
    action: str,
    files: List[Dict[str, Any]],
    target_roles: List[str],
    understanding: Dict[str, Any]
):
    """Execute the agent pipeline after the monitor has been opened."""
    workflow_db = SessionLocal()
    try:
        project_workflow_executions[workflow_id]["status"] = "running"
        project_workflow_executions[workflow_id]["current_stage"] = "requirements"
        project_workflow_executions[workflow_id]["progress_percentage"] = 5

        requirement_agent = RequirementUnderstandingAgent(workflow_db)
        requirement_result = await requirement_agent.analyze_curriculum(
            imscc_files=files,
            target_roles=target_roles,
            course_design_data={},
            style_guide={}
        )
        requirement_analysis = requirement_result.dict()
        project_workflow_executions[workflow_id]["progress_percentage"] = 15
        project_workflow_executions[workflow_id]["agent_outputs"]["requirement_understanding"] = requirement_analysis

        orchestrator = OrchestratorAgent(workflow_db)
        workflow_execution = await orchestrator.execute_curriculum_workflow(
            project_id=project_id,
            requirement_analysis=requirement_analysis,
            imscc_files=files,
            target_roles=target_roles,
            use_case=action,
            workflow_id=workflow_id
        )

        understanding["outputs"] = [
            "Updated course materials",
            "Workforce skills alignment and gap report",
            "Accessibility compliance report"
        ]
        understanding["agents"] = [
            "Requirement Understanding Agent",
            "Orchestrator Agent",
            "Knowledge Intelligence Agent",
            "Workforce Skills Agent",
            "Content AI Studio Agent",
            "Accessibility Agent"
        ]
        project_workflow_understanding[workflow_id] = understanding
        project_workflow_executions[workflow_id].update({
            "status": workflow_execution.status,
            "current_stage": workflow_execution.current_stage,
            "progress_percentage": workflow_execution.progress_percentage,
            "checkpoints": [checkpoint.dict() for checkpoint in workflow_execution.checkpoints],
            "agent_outputs": workflow_execution.agent_outputs,
            "understanding": understanding
        })

        # Save to database
        from database.models import WorkflowExecution as DBWorkflowExecution
        db_execution = workflow_db.query(DBWorkflowExecution).filter(
            DBWorkflowExecution.id == workflow_id
        ).first()

        if db_execution:
            db_execution.status = workflow_execution.status
            db_execution.output_data = workflow_execution.agent_outputs
            db_execution.completed_at = workflow_execution.end_time
        else:
            db_execution = DBWorkflowExecution(
                id=workflow_id,
                workflow_id=workflow_id,
                status=workflow_execution.status,
                output_data=workflow_execution.agent_outputs,
                started_at=workflow_execution.start_time,
                completed_at=workflow_execution.end_time
            )
            workflow_db.add(db_execution)

        workflow_db.commit()
    except Exception as error:
        workflow_db.rollback()
        logger.exception("Error executing workflow %s", workflow_id)
        project_workflow_executions[workflow_id].update({
            "status": "failed",
            "current_stage": "failed",
            "errors": [str(error)]
        })
    finally:
        workflow_db.close()


# ==================== Startup Event ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Database initialized successfully")


# ==================== Health Check ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "name": settings.APP_NAME
    }


# ==================== Request Models ====================

class RegisterRequest(BaseModel):
    email: str
    username: str
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None


class UserPreferencesUpdate(BaseModel):
    email_notifications: Optional[Dict] = None
    notification_frequency: Optional[str] = None
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    marketing_emails: Optional[bool] = None
    analytics_enabled: Optional[bool] = None


class CreateApiKeyRequest(BaseModel):
    name: str
    permissions: List[str] = ["read"]


class IngestContentRequest(BaseModel):
    title: str
    content: str
    content_type: str = "document"
    source: Optional[str] = None
    metadata: Optional[Dict] = None


class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    primary_action: Optional[str] = None


# Dependency to get current user
async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


# Optional user dependency for demo/guest mode
async def get_current_user_optional(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        # Return a demo user for testing
        demo_user = db.query(User).filter(User.username == "demo_user").first()
        if not demo_user:
            # Create demo user if it doesn't exist
            demo_user = User(
                id=str(uuid.uuid4()),
                email="demo@example.com",
                username="demo_user",
                full_name="Demo User",
                hashed_password="demo",  # Not used in demo mode
                is_active=True,
                email_verified=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        return demo_user

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


# ==================== Authentication Endpoints ====================

@app.post("/api/auth/register")
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = db.query(User).filter(User.username == req.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = create_user(db, req.email, req.username, req.full_name, req.password)

    # Create default user preferences
    preferences = UserPreferences(user_id=user.id)
    db.add(preferences)
    db.commit()

    access_token, expires_in = create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    return {
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@app.post("/api/auth/login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login user"""
    user = authenticate_user(db, req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    # Update last login
    update_last_login(db, user)

    access_token, expires_in = create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    return {
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_admin": user.is_admin,
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@app.post("/api/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email"""
    user = get_user_by_email(db, req.email)

    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If an account exists with that email, a reset link has been sent"}

    if not user.is_active:
        return {"message": "Account is inactive"}

    # Generate reset token
    reset_token = generate_password_reset_token(db, user)

    # Send email
    email_service = get_email_service()
    reset_url = settings.PASSWORD_RESET_URL
    email_service.send_password_reset_email(
        user.email,
        user.full_name,
        reset_token,
        reset_url
    )

    return {"message": "If an account exists with that email, a reset link has been sent"}


@app.post("/api/auth/reset-password")
async def reset_password_endpoint(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password with token"""
    # Find user with valid reset token
    user = db.query(User).filter(
        User.password_reset_token == req.token
    ).first()

    if not user:
        # Try to hash and compare
        import hashlib
        token_hash = hashlib.sha256(req.token.encode()).hexdigest()
        user = db.query(User).filter(
            User.password_reset_token == token_hash
        ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Verify token
    if not verify_password_reset_token(db, user, req.token):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Reset password
    reset_password(db, user, req.new_password)

    return {"message": "Password reset successfully"}


@app.post("/api/auth/change-password")
async def change_password(req: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Change user password"""
    from auth.auth import verify_password

    # Verify current password
    if not verify_password(req.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # Update password
    reset_password(db, current_user, req.new_password)

    return {"message": "Password changed successfully"}


@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
        "email_verified": current_user.email_verified,
        "created_at": current_user.created_at.isoformat()
    }


# ==================== User Profile Endpoints ====================

@app.get("/api/users/profile")
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user profile"""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_admin": current_user.is_admin,
        "email_verified": current_user.email_verified,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "created_at": current_user.created_at.isoformat(),
        "preferences": preferences.to_dict() if preferences else None
    }


@app.put("/api/users/profile")
async def update_profile(
    req: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if req.full_name:
        current_user.full_name = req.full_name

    if req.email and req.email != current_user.email:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == req.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = req.email
        current_user.email_verified = False

    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name
    }


@app.get("/api/users/preferences")
async def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user preferences"""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    if not preferences:
        # Create default preferences if they don't exist
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
        db.commit()

    return {
        "id": preferences.id,
        "email_notifications": preferences.email_notifications,
        "notification_frequency": preferences.notification_frequency,
        "theme": preferences.theme,
        "language": preferences.language,
        "timezone": preferences.timezone,
        "marketing_emails": preferences.marketing_emails,
        "analytics_enabled": preferences.analytics_enabled
    }


@app.put("/api/users/preferences")
async def update_preferences(
    req: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()

    if not preferences:
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)

    if req.email_notifications is not None:
        preferences.email_notifications = req.email_notifications
    if req.notification_frequency is not None:
        preferences.notification_frequency = req.notification_frequency
    if req.theme is not None:
        preferences.theme = req.theme
    if req.language is not None:
        preferences.language = req.language
    if req.timezone is not None:
        preferences.timezone = req.timezone
    if req.marketing_emails is not None:
        preferences.marketing_emails = req.marketing_emails
    if req.analytics_enabled is not None:
        preferences.analytics_enabled = req.analytics_enabled

    db.commit()

    return {"message": "Preferences updated successfully"}


# ==================== API Keys Endpoints ====================

@app.get("/api/users/api-keys")
async def list_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List user's API keys"""
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()

    return {
        "api_keys": [
            {
                "id": key.id,
                "name": key.name,
                "permissions": key.permissions,
                "last_used": key.last_used.isoformat() if key.last_used else None,
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat()
            }
            for key in api_keys
        ]
    }


@app.post("/api/users/api-keys")
async def create_api_key(
    req: CreateApiKeyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new API key"""
    import secrets

    # Generate API key
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    api_key = ApiKey(
        user_id=current_user.id,
        name=req.name,
        key_hash=key_hash,
        permissions=req.permissions
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "key": key,  # Only return the key once on creation
        "permissions": api_key.permissions,
        "created_at": api_key.created_at.isoformat()
    }


@app.delete("/api/users/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete API key"""
    api_key = db.query(ApiKey).filter(
        ApiKey.id == key_id,
        ApiKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()

    return {"message": "API key deleted successfully"}


# ==================== Projects Endpoints ====================

@app.get("/api/projects")
async def list_projects(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """List all projects for the current user"""
    projects = db.query(Project).filter(Project.creator_id == current_user.id).all()

    return {
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "primary_action": p.primary_action,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                "content_count": len(p.contents)
            }
            for p in projects
        ]
    }


@app.post("/api/projects")
async def create_project(
    req: CreateProjectRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")

        project = Project(
            name=req.name,
            description=req.description,
            creator_id=current_user.id,
            status="active",
            primary_action=None
        )
        db.add(project)
        db.commit()
        db.refresh(project)

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "primary_action": project.primary_action,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "content_count": 0
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create project: {str(e)}")


@app.get("/api/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.creator_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "primary_action": project.primary_action,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        "content_count": len(project.contents)
    }


@app.put("/api/projects/{project_id}")
async def update_project(
    project_id: str,
    req: UpdateProjectRequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.creator_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        if req.name is not None:
            project.name = req.name
        if req.description is not None:
            project.description = req.description
        if req.status is not None:
            project.status = req.status
        if req.primary_action is not None:
            project.primary_action = req.primary_action

        db.commit()
        db.refresh(project)

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "primary_action": project.primary_action,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "content_count": len(project.contents)
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update project: {str(e)}")


@app.delete("/api/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.creator_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        db.delete(project)
        db.commit()
        return {"message": f"Project '{project.name}' deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


# ==================== Generic Workflow Endpoints ====================

@app.post("/api/projects/{project_id}/workflow")
async def create_project_workflow(
    project_id: str,
    req: Dict[str, Any],
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Create a workflow for any project action"""
    try:
        # Get project
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.creator_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        action = req.get("action", "generic")
        files = req.get("files", [])
        requirement_analysis = req.get("requirement_analysis", {})

        input_names = [
            file.get("filename", str(file)) if isinstance(file, dict) else str(file)
            for file in files
        ]
        understanding = {
            "purpose": requirement_analysis.get(
                "program_intent",
                f"Prepare the project for the {action} workflow."
            ),
            "inputs": input_names or ["Project requirements and selected workflow action"],
            "outputs": requirement_analysis.get(
                "key_requirements",
                ["Workflow-ready content and analysis"]
            ),
            "process": "Analyze requirements, apply the selected workflow, and prepare the configured outputs.",
            "agents": ["Requirement Understanding Agent", action],
            "deliverables": requirement_analysis.get(
                "extracted_outcomes",
                ["Workflow-ready content and analysis"]
            ),
            "timeline": "Processing"
        }

        # Create the monitor record - workflow will start when user clicks "Start" button
        target_roles = req.get("target_roles") or requirement_analysis.get("target_roles", [action])
        workflow_id = f"{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        project_workflow_understanding[workflow_id] = understanding
        project_workflow_executions[workflow_id] = {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": "pending",
            "current_stage": "ready",
            "progress_percentage": 0,
            "checkpoints": [],
            "agent_outputs": {},
            "understanding": understanding,
            "action": action,
            "files": files,
            "target_roles": target_roles
        }

        return {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": "pending",
            "current_stage": "initialization",
            "progress_percentage": 0,
            "checkpoints": [],
            "agent_outputs": {},
            "understanding": understanding
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating project workflow: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/projects/{project_id}/workflow/{workflow_id}/start")
async def start_project_workflow(
    project_id: str,
    workflow_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Start an initialized workflow"""
    try:
        # Verify project exists and belongs to user
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.creator_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get workflow info from in-memory storage
        if workflow_id not in project_workflow_executions:
            raise HTTPException(status_code=404, detail="Workflow not found")

        workflow_data = project_workflow_executions[workflow_id]

        # Start the workflow asynchronously
        asyncio.create_task(_run_project_workflow(
            workflow_id,
            project_id,
            workflow_data.get("action"),
            workflow_data.get("files", []),
            workflow_data.get("target_roles", []),
            workflow_data.get("understanding", {})
        ))

        # Update status to running
        project_workflow_executions[workflow_id]["status"] = "running"
        project_workflow_executions[workflow_id]["current_stage"] = "requirements"

        return {
            "workflow_id": workflow_id,
            "status": "running",
            "message": "Workflow started successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting workflow {workflow_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/projects/{project_id}/workflow/{workflow_id}")
async def get_project_workflow_status(
    project_id: str,
    workflow_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get workflow status for any project"""
    try:
        # Verify project exists and belongs to user
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.creator_id == current_user.id
        ).first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        execution = project_workflow_executions.get(workflow_id)
        if execution:
            return execution

        # Keep a useful response for workflows created by older clients.
        return {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": "running",
            "current_stage": "initialization",
            "progress_percentage": 0,
            "checkpoints": [],
            "understanding": project_workflow_understanding.get(workflow_id, {
                "purpose": "Requirement analysis has been initiated for this workflow.",
                "inputs": ["Project requirements and selected workflow action"],
                "outputs": ["Workflow-ready content and analysis"],
                "process": "Analyze requirements, apply the selected workflow, and prepare the configured outputs.",
                "agents": ["Requirement Understanding Agent"],
                "deliverables": ["Workflow-ready content and analysis"],
                "timeline": "Processing"
            })
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=404, detail="Workflow not found")


# ==================== Curriculum Workflow Endpoints ====================

@app.post("/api/curriculum/validate-inputs")
async def validate_curriculum_inputs(
    req: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Validate curriculum inputs before starting workflow"""
    try:
        agent = RequirementUnderstandingAgent(db)
        imscc_files = req.get("imscc_files", [])
        target_roles = req.get("target_roles", [])

        validation_result = await agent.validate_inputs(imscc_files, target_roles)

        return validation_result
    except Exception as e:
        logger.error(f"Error validating curriculum inputs: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/curriculum/analyze-requirements")
async def analyze_requirements(
    req: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze curriculum requirements using Requirement Understanding Agent"""
    try:
        agent = RequirementUnderstandingAgent(db)

        imscc_files = req.get("imscc_files", [])
        target_roles = req.get("target_roles", [])
        course_design_data = req.get("course_design_data", {})
        style_guide = req.get("style_guide", {})

        requirement_analysis = await agent.analyze_curriculum(
            imscc_files=imscc_files,
            target_roles=target_roles,
            course_design_data=course_design_data,
            style_guide=style_guide
        )

        return requirement_analysis.dict()
    except Exception as e:
        logger.error(f"Error analyzing requirements: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/curriculum/start-workflow")
async def start_curriculum_workflow(
    req: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start the curriculum alignment workflow.
    This triggers the Orchestrator Agent to coordinate all agents.
    """
    try:
        project_id = req.get("project_id")
        imscc_files = req.get("imscc_files", [])
        target_roles = req.get("target_roles", [])
        requirement_analysis = req.get("requirement_analysis", {})
        use_case = req.get("use_case", "cybersecurity_curriculum")

        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        orchestrator = OrchestratorAgent(db)

        workflow_execution = await orchestrator.execute_curriculum_workflow(
            project_id=project_id,
            requirement_analysis=requirement_analysis,
            imscc_files=imscc_files,
            target_roles=target_roles,
            use_case=use_case
        )

        return {
            "workflow_id": workflow_execution.workflow_id,
            "project_id": workflow_execution.project_id,
            "status": workflow_execution.status,
            "current_stage": workflow_execution.current_stage,
            "progress_percentage": workflow_execution.progress_percentage,
            "checkpoints": [
                {
                    "number": cp.checkpoint_number,
                    "stage": cp.stage,
                    "description": cp.description,
                    "required_reviewer": cp.required_reviewer,
                    "status": cp.status
                }
                for cp in workflow_execution.checkpoints
            ]
        }
    except Exception as e:
        logger.error(f"Error starting curriculum workflow: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/curriculum/workflow/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of a curriculum workflow"""
    try:
        orchestrator = OrchestratorAgent(db)
        workflow = orchestrator.get_workflow_status(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "current_stage": workflow.current_stage,
            "progress_percentage": workflow.progress_percentage,
            "checkpoints": [
                {
                    "number": cp.checkpoint_number,
                    "stage": cp.stage,
                    "description": cp.description,
                    "status": cp.status,
                    "reviewer_notes": cp.reviewer_notes
                }
                for cp in workflow.checkpoints
            ],
            "outputs": workflow.agent_outputs,
            "errors": workflow.errors
        }
    except Exception as e:
        logger.error(f"Error getting workflow status: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/curriculum/workflow/{workflow_id}/report")
async def generate_workflow_report(
    workflow_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Generate a Word document report from workflow execution results"""
    try:
        from services.document_generator import generate_workflow_report, save_report
        import os
        import tempfile

        orchestrator = OrchestratorAgent(db)
        workflow = orchestrator.get_workflow_status(workflow_id)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        project = db.query(Project).filter(Project.id == workflow.project_id).first()
        project_name = project.name if project else "Unknown Project"

        # Prepare agent outputs
        agent_outputs = {}
        if hasattr(workflow, 'agent_runs') and workflow.agent_runs:
            for agent_run in workflow.agent_runs:
                if agent_run.output_data:
                    agent_outputs[agent_run.agent_name] = agent_run.output_data

        # Generate document
        doc = generate_workflow_report(
            project_name=project_name,
            workflow_name=workflow.workflow_id,
            execution_data={
                'status': workflow.status,
                'summary': {
                    'current_stage': workflow.current_stage,
                    'progress_percentage': workflow.progress_percentage,
                    'total_checkpoints': len(workflow.checkpoints) if hasattr(workflow, 'checkpoints') else 0
                }
            },
            agent_outputs=agent_outputs
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            tmp_path = tmp.name

        save_report(doc, tmp_path)

        filename = f"workflow_report_{workflow_id}.docx"
        return FileResponse(
            path=tmp_path,
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating workflow report: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to generate report: {str(e)}")


@app.post("/api/curriculum/checkpoint/{workflow_id}/{checkpoint_number}/approve")
async def approve_checkpoint(
    workflow_id: str,
    checkpoint_number: int,
    req: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a HITL checkpoint to proceed to next stage"""
    try:
        orchestrator = OrchestratorAgent(db)
        reviewer_notes = req.get("reviewer_notes", "")

        success = await orchestrator.approve_checkpoint(
            workflow_id=workflow_id,
            checkpoint_number=checkpoint_number,
            reviewer_notes=reviewer_notes
        )

        if not success:
            raise HTTPException(status_code=404, detail="Workflow or checkpoint not found")

        return {"message": "Checkpoint approved", "workflow_id": workflow_id}
    except Exception as e:
        logger.error(f"Error approving checkpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/curriculum/checkpoint/{workflow_id}/{checkpoint_number}/reject")
async def reject_checkpoint(
    workflow_id: str,
    checkpoint_number: int,
    req: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a checkpoint and request revisions"""
    try:
        orchestrator = OrchestratorAgent(db)
        reviewer_notes = req.get("reviewer_notes", "Needs revision")

        success = await orchestrator.reject_checkpoint(
            workflow_id=workflow_id,
            checkpoint_number=checkpoint_number,
            reviewer_notes=reviewer_notes
        )

        if not success:
            raise HTTPException(status_code=404, detail="Workflow or checkpoint not found")

        return {"message": "Checkpoint rejected, revision requested", "workflow_id": workflow_id}
    except Exception as e:
        logger.error(f"Error rejecting checkpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== Content Endpoints ====================

@app.post("/api/content/ingest")
async def ingest_content(
    req: IngestContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ingest new content"""
    try:
        # Store content in database
        content = Content(
            title=req.title,
            content_type=req.content_type,
            source=req.source or "manual",
            raw_content=req.content,
            content_metadata=req.metadata or {}
        )
        db.add(content)
        db.commit()
        db.refresh(content)

        return {
            "success": True,
            "content_id": content.id,
            "title": content.title,
            "content_type": content.content_type,
            "status": content.status,
            "message": "Content ingested successfully! Processing started..."
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Content ingestion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest content: {str(e)}"
        )


@app.get("/api/content/{content_id}")
async def get_content(content_id: str, db: Session = Depends(get_db)):
    """Get content by ID"""
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    return {
        "id": content.id,
        "title": content.title,
        "content_type": content.content_type,
        "status": content.status,
        "created_at": content.created_at.isoformat()
    }


@app.get("/api/content")
async def list_content(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all content"""
    contents = db.query(Content).offset(skip).limit(limit).all()

    return {
        "total": db.query(Content).count(),
        "content": [
            {
                "id": c.id,
                "title": c.title,
                "content_type": c.content_type,
                "status": c.status,
                "source": c.source or "unknown",
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "raw_content": c.raw_content or "",
                "content_metadata": c.content_metadata or {}
            }
            for c in contents
        ]
    }


@app.delete("/api/content/{content_id}")
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete content by ID"""
    content = db.query(Content).filter(Content.id == content_id).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    try:
        db.delete(content)
        db.commit()

        return {
            "success": True,
            "message": f"Content '{content.title}' deleted successfully"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting content: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete content: {str(e)}"
        )


# ==================== Workflow Endpoints ====================

class CreateWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "draft"


@app.get("/api/workflows")
async def list_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all workflows for the current user"""
    workflows = db.query(Workflow).filter(Workflow.creator_id == current_user.id).all()

    return {
        "workflows": [
            {
                "id": w.id,
                "name": w.name,
                "description": w.description,
                "status": w.status,
                "is_template": w.is_template,
                "created_at": w.created_at.isoformat() if w.created_at else None,
                "updated_at": w.updated_at.isoformat() if w.updated_at else None,
                "execution_count": len(w.executions)
            }
            for w in workflows
        ]
    }


@app.post("/api/workflows")
async def create_workflow(
    req: CreateWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    try:
        workflow = Workflow(
            name=req.name,
            description=req.description,
            creator_id=current_user.id,
            definition={},
            status=req.status or "draft"
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "status": workflow.status,
            "is_template": workflow.is_template,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
            "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
            "execution_count": 0
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to create workflow: {str(e)}")


@app.get("/api/workflows/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.creator_id == current_user.id
    ).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "status": workflow.status,
        "is_template": workflow.is_template,
        "definition": workflow.definition or {},
        "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
        "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None,
        "execution_count": len(workflow.executions)
    }


@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.creator_id == current_user.id
    ).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    try:
        db.delete(workflow)
        db.commit()
        return {"message": f"Workflow '{workflow.name}' deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete workflow: {str(e)}")


@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow"""
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    orchestrator = WorkflowOrchestrator(db)
    execution_id = str(uuid.uuid4())

    # Execute workflow asynchronously
    result = await orchestrator.execute_workflow(
        execution_id,
        workflow_id,
        workflow.definition,
        input_data
    )

    return {
        "execution_id": execution_id,
        "status": result.status,
        "results": {k: v.dict() for k, v in result.results.items()}
    }


@app.get("/api/workflows/{workflow_id}/executions/{execution_id}")
async def get_execution_status(
    workflow_id: str,
    execution_id: str,
    db: Session = Depends(get_db)
):
    """Get workflow execution status"""
    execution = db.query(WorkflowExecution).filter(
        WorkflowExecution.id == execution_id,
        WorkflowExecution.workflow_id == workflow_id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return {
        "id": execution.id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "output_data": execution.output_data
    }


# ==================== Skills Endpoints ====================

@app.post("/api/skills")
async def create_skill(
    name: str,
    description: Optional[str] = None,
    category: Optional[str] = None,
    proficiency_level: str = "intermediate",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new skill"""
    skill = Skill(
        name=name,
        description=description,
        category=category,
        proficiency_level=proficiency_level
    )
    db.add(skill)
    db.commit()

    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "proficiency_level": skill.proficiency_level
    }


@app.get("/api/skills")
async def list_skills(category: Optional[str] = None, db: Session = Depends(get_db)):
    """List all skills"""
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)

    skills = query.all()

    return {
        "total": len(skills),
        "skills": [
            {
                "id": s.id,
                "name": s.name,
                "category": s.category,
                "proficiency_level": s.proficiency_level
            }
            for s in skills
        ]
    }


# ==================== Accessibility Endpoints ====================

@app.post("/api/accessibility/audit")
async def audit_content_accessibility(
    content_id: str,
    wcag_level: str = "AA",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Audit content for accessibility"""
    agent = AccessibilityAgent(db)

    from agents.base_agent import AgentInput
    agent_input = AgentInput(
        data={"action": "audit", "content_id": content_id, "wcag_level": wcag_level},
        user_id=current_user.id
    )

    result = await agent.process(agent_input)

    return {
        "status": result.status,
        "data": result.data,
        "errors": result.errors
    }


# ==================== Shutdown Event ====================

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
