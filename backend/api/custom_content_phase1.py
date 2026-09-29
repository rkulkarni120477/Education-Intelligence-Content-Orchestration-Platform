"""Custom Content Development API Routes.

Endpoints for:
- Conversation management (CRUD)
- File upload, download, deletion
- Agent interaction with streaming
- Message history
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from database.db import get_db
from database.models import (
    CustomContentConversation,
    CustomContentMessage,
    CustomContentFile,
    User
)
from auth.tenant_context import get_current_tenant_id
from services.custom_content_file_service import CustomContentFileService
import logging
import uuid
from datetime import datetime
from pathlib import Path
import io

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1/custom-content", tags=["custom-content"])


# ===== RESPONSE MODELS =====

class FileInfo(BaseModel):
    """File information."""
    id: str
    name: str
    file_type: str  # 'upload' | 'generated'
    mime_type: Optional[str]
    size: int
    created_at: str
    is_generated: bool

    class Config:
        from_attributes = True


class MessageInfo(BaseModel):
    """Message information."""
    id: str
    role: str  # 'user' | 'assistant'
    content: str
    message_type: str
    created_at: str
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class ConversationInfo(BaseModel):
    """Conversation information."""
    id: str
    title: str
    description: Optional[str]
    is_archived: bool
    created_at: str
    updated_at: str
    message_count: int = 0
    file_count: int = 0

    class Config:
        from_attributes = True


class ConversationDetail(ConversationInfo):
    """Full conversation with messages and files."""
    messages: List[MessageInfo] = []
    files: List[FileInfo] = []


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class SendMessageRequest(BaseModel):
    """Request to send a message to the agent."""
    prompt: str = Field(..., min_length=1)
    file_ids: List[str] = Field(default_factory=list)
    context_file_id: Optional[str] = None


class UpdateConversationRequest(BaseModel):
    """Request to update conversation metadata."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_archived: Optional[bool] = None


# ===== CONVERSATION ENDPOINTS =====

@router.post("/conversations", response_model=ConversationInfo)
async def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> ConversationInfo:
    """Create a new conversation."""
    try:
        user_id = "current_user"  # TODO: Get from request context

        conversation = CustomContentConversation(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            title=request.title,
            description=request.description,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"✓ Created conversation {conversation.id}")
        return ConversationInfo(
            id=conversation.id,
            title=conversation.title,
            description=conversation.description,
            is_archived=conversation.is_archived,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
        )

    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/conversations", response_model=List[ConversationInfo])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> List[ConversationInfo]:
    """List user's conversations."""
    try:
        user_id = "current_user"  # TODO: Get from request context

        conversations = db.query(CustomContentConversation).filter(
            CustomContentConversation.tenant_id == tenant_id,
            CustomContentConversation.user_id == user_id,
            CustomContentConversation.is_archived == False,
        ).order_by(
            CustomContentConversation.updated_at.desc()
        ).offset(skip).limit(limit).all()

        return [
            ConversationInfo(
                id=conv.id,
                title=conv.title,
                description=conv.description,
                is_archived=conv.is_archived,
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                message_count=len(conv.messages) if conv.messages else 0,
                file_count=len(conv.files) if conv.files else 0,
            )
            for conv in conversations
        ]

    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> ConversationDetail:
    """Get conversation with full history."""
    try:
        conversation = db.query(CustomContentConversation).filter(
            CustomContentConversation.id == conversation_id,
            CustomContentConversation.tenant_id == tenant_id,
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        messages = [
            MessageInfo(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                message_type=msg.message_type,
                created_at=msg.created_at.isoformat(),
                metadata=msg.metadata or {},
            )
            for msg in (conversation.messages or [])
        ]

        files = [
            FileInfo(
                id=f.id,
                name=f.name,
                file_type=f.file_type,
                mime_type=f.mime_type,
                size=f.size,
                created_at=f.created_at.isoformat(),
                is_generated=f.is_generated,
            )
            for f in (conversation.files or [])
        ]

        return ConversationDetail(
            id=conversation.id,
            title=conversation.title,
            description=conversation.description,
            is_archived=conversation.is_archived,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
            message_count=len(messages),
            file_count=len(files),
            messages=messages,
            files=files,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/conversations/{conversation_id}", response_model=ConversationInfo)
async def update_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> ConversationInfo:
    """Update conversation metadata."""
    try:
        conversation = db.query(CustomContentConversation).filter(
            CustomContentConversation.id == conversation_id,
            CustomContentConversation.tenant_id == tenant_id,
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        if request.title:
            conversation.title = request.title
        if request.description is not None:
            conversation.description = request.description
        if request.is_archived is not None:
            conversation.is_archived = request.is_archived

        db.commit()
        db.refresh(conversation)

        return ConversationInfo(
            id=conversation.id,
            title=conversation.title,
            description=conversation.description,
            is_archived=conversation.is_archived,
            created_at=conversation.created_at.isoformat(),
            updated_at=conversation.updated_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== FILE ENDPOINTS =====

@router.post("/conversations/{conversation_id}/files/upload", response_model=FileInfo)
async def upload_file(
    conversation_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> FileInfo:
    """Upload a file to a conversation."""
    try:
        user_id = "current_user"  # TODO: Get from request context

        # Verify conversation exists
        conversation = db.query(CustomContentConversation).filter(
            CustomContentConversation.id == conversation_id,
            CustomContentConversation.tenant_id == tenant_id,
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Create uploads directory
        upload_dir = Path(__file__).resolve().parent.parent / "data" / "uploads" / "custom-content"
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_id = str(uuid.uuid4())
        suffix = Path(file.filename or "upload").suffix.lower()
        file_path = upload_dir / f"{file_id}{suffix}"

        # Read and save file content
        content = await file.read()
        with file_path.open("wb") as f:
            f.write(content)

        # Create database record
        db_file = CustomContentFile(
            id=file_id,
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
            name=file.filename or "upload",
            file_type="upload",
            mime_type=file.content_type,
            path=str(file_path),
            size=len(content),
            is_generated=False,
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        logger.info(f"✓ Uploaded file {db_file.id} to conversation {conversation_id}")

        return FileInfo(
            id=db_file.id,
            name=db_file.name,
            file_type=db_file.file_type,
            mime_type=db_file.mime_type,
            size=db_file.size,
            created_at=db_file.created_at.isoformat(),
            is_generated=db_file.is_generated,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/files/{file_id}", response_model=FileInfo)
async def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> FileInfo:
    """Get file metadata."""
    try:
        db_file = db.query(CustomContentFile).filter(
            CustomContentFile.id == file_id,
            CustomContentFile.tenant_id == tenant_id,
        ).first()

        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        return FileInfo(
            id=db_file.id,
            name=db_file.name,
            file_type=db_file.file_type,
            mime_type=db_file.mime_type,
            size=db_file.size,
            created_at=db_file.created_at.isoformat(),
            is_generated=db_file.is_generated,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> Dict[str, str]:
    """Delete a file."""
    try:
        db_file = db.query(CustomContentFile).filter(
            CustomContentFile.id == file_id,
            CustomContentFile.tenant_id == tenant_id,
        ).first()

        if not db_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Delete file from disk
        file_path = Path(db_file.path)
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file from disk: {file_path}")

        # Delete from database
        db.delete(db_file)
        db.commit()

        logger.info(f"✓ Deleted file {file_id}")

        return {"status": "success", "message": "File deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== MESSAGE ENDPOINTS (placeholder for agent integration) =====

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> Dict[str, Any]:
    """Send a message and start agent processing.

    This endpoint will be connected to the agent in Phase 5-6.
    For now, it returns a placeholder response.
    """
    try:
        # Verify conversation exists
        conversation = db.query(CustomContentConversation).filter(
            CustomContentConversation.id == conversation_id,
            CustomContentConversation.tenant_id == tenant_id,
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        logger.info(f"Message sent to conversation {conversation_id}: {request.prompt[:50]}...")

        return {
            "status": "accepted",
            "message": "Message queued for processing (agent integration coming in Phase 5)",
            "conversation_id": conversation_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
