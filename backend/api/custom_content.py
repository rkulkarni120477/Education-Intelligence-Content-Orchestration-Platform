"""Custom Content Development API Routes - Phase 3: LLM Integration.

Endpoints for:
- Conversation management (CRUD)
- File upload, download, deletion, rename
- Agent interaction with streaming
- Message history with LLM integration
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional, AsyncGenerator
from pydantic import BaseModel, Field
from database.db import get_db
from database.models import (
    CustomContentConversation,
    CustomContentMessage,
    CustomContentFile,
)
from auth.tenant_context import get_current_tenant_id
from services.custom_content_file_service import CustomContentFileService
from services.llm_service import LLMService
import logging
import uuid
from datetime import datetime
from pathlib import Path
import io
import json

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
    message_metadata: Dict[str, Any] = {}

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


class UpdateConversationRequest(BaseModel):
    """Request to update conversation metadata."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_archived: Optional[bool] = None


class SendMessageRequest(BaseModel):
    """Request to send a message to the agent."""
    prompt: str = Field(..., min_length=1)
    file_ids: List[str] = Field(default_factory=list)
    context_file_id: Optional[str] = None


class RenameFileRequest(BaseModel):
    """Request to rename a file."""
    new_name: str = Field(..., min_length=1, max_length=255)


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
                message_metadata=msg.message_metadata or {},
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

        # Read file content
        content = await file.read()
        filename = file.filename or "upload"

        # Validate file
        is_valid, error_msg = CustomContentFileService.validate_file(filename, len(content))
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Save file
        file_id, file_path, file_size = CustomContentFileService.save_file(content, filename)

        # Get MIME type
        mime_type = CustomContentFileService.get_mime_type(filename)

        # Create database record
        db_file = CustomContentFile(
            id=file_id,
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
            name=filename,
            file_type="upload",
            mime_type=mime_type,
            path=file_path,
            size=file_size,
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


@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Download a file."""
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

        file_path = Path(db_file.path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )

        return FileResponse(
            path=file_path,
            media_type=db_file.mime_type or "application/octet-stream",
            filename=db_file.name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/files/{file_id}", response_model=FileInfo)
async def rename_file(
    file_id: str,
    request: RenameFileRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> FileInfo:
    """Rename a file."""
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

        # Validate new name
        if not request.new_name or len(request.new_name) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )

        old_name = db_file.name
        db_file.name = request.new_name
        db.commit()
        db.refresh(db_file)

        logger.info(f"✓ Renamed file {file_id} from {old_name} to {request.new_name}")

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
        logger.error(f"Error renaming file: {str(e)}")
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
        CustomContentFileService.delete_file(db_file.path)

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


# ===== MESSAGE ENDPOINTS =====

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
) -> Dict[str, Any]:
    """Send a message to the conversation (creates user message).

    Returns immediately. Use /messages/stream endpoint for streaming responses.
    """
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

        # Create user message
        user_message = CustomContentMessage(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            role="user",
            content=request.prompt,
            message_type="text",
            message_metadata={"file_ids": request.file_ids} if request.file_ids else {},
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        logger.info(f"Created user message {user_message.id} in conversation {conversation_id}")

        return {
            "status": "success",
            "message_id": user_message.id,
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


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: str,
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Stream AI response with file context.

    Sends message and returns streaming response via SSE.
    """
    def event_generator():
        try:
            user_id = "current_user"  # TODO: Get from request context

            # Verify conversation exists
            conversation = db.query(CustomContentConversation).filter(
                CustomContentConversation.id == conversation_id,
                CustomContentConversation.tenant_id == tenant_id,
            ).first()

            if not conversation:
                yield f"data: {json.dumps({'type': 'error', 'content': 'Conversation not found'})}\n\n"
                return

            # Create user message
            user_message = CustomContentMessage(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                role="user",
                content=request.prompt,
                message_type="text",
                message_metadata={"file_ids": request.file_ids} if request.file_ids else {},
            )
            db.add(user_message)
            db.commit()
            db.refresh(user_message)

            logger.info(
                f"[{tenant_id}] User message {user_message.id} in conversation {conversation_id}"
            )

            # Load files for context
            files = []
            if request.file_ids:
                files = db.query(CustomContentFile).filter(
                    CustomContentFile.id.in_(request.file_ids),
                    CustomContentFile.tenant_id == tenant_id,
                    CustomContentFile.conversation_id == conversation_id,
                ).all()

            # Get conversation history for context
            history_messages = db.query(CustomContentMessage).filter(
                CustomContentMessage.conversation_id == conversation_id,
                CustomContentMessage.id != user_message.id,
            ).order_by(
                CustomContentMessage.created_at.desc()
            ).limit(10).all()

            # Reverse to chronological order
            history_messages = list(reversed(history_messages))

            conversation_history = [
                {
                    "role": msg.role,
                    "content": msg.content,
                }
                for msg in history_messages[-5:]  # Last 5 messages for context
            ]

            # Signal start of streaming
            yield f"data: {json.dumps({'type': 'start', 'content': ''})}\n\n"

            # Stream response from LLM
            assistant_content = ""
            for chunk in LLMService.stream_message(
                prompt=request.prompt,
                files=files,
                conversation_history=conversation_history,
                tenant_id=tenant_id,
            ):
                assistant_content += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

            # Create assistant message in database
            assistant_message = CustomContentMessage(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
                message_type="text",
                message_metadata={
                    "model": LLMService.get_model_info()["model_id"],
                    "file_ids": request.file_ids,
                },
            )
            db.add(assistant_message)

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(assistant_message)

            logger.info(
                f"[{tenant_id}] Assistant message {assistant_message.id} "
                f"created ({len(assistant_content)} chars)"
            )

            # Signal completion
            yield f"data: {json.dumps({'type': 'end', 'content': '', 'message_id': assistant_message.id})}\n\n"

        except Exception as e:
            logger.error(f"Error in stream_message: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
