"""API routes for Education Intelligence & Content Orchestration Platform"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, status, UploadFile, File, Form, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from database.db import SessionLocal, get_db
from database.models import Alignment, Content, Curriculum, LearningObjective, Lesson, Standard, User
from auth.tenant_context import get_current_tenant_id
# from api.courses import router as courses_router  # DISABLED: Models Course/Unit not defined in database.models
from services.alignment_service import AlignmentService
from api.standards import router as standards_router
from api.workforce_alignment import router as workforce_alignment_router
from api.skill_mapping import router as skill_mapping_router
from api.data_access import router as data_access_router
from api.agents import router as agents_router
from api.agent_tests import router as agent_tests_router
from api.agent_workflows import router as agent_workflows_router
from api.custom_content import router as custom_content_router
from services.content_governance import ContentGovernanceAgent
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
import json
import logging
import uuid
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api", tags=["api"])
logger = logging.getLogger(__name__)


def _get_vector_store(collection_name: str):
    """Load Chroma only when a vector operation is requested."""
    from database.vector_db import get_vector_store

    return get_vector_store(collection_name)

# Include standards routes
router.include_router(standards_router)

# Include workforce alignment workflow routes
router.include_router(workforce_alignment_router)

# Include skill mapping and recommendations routes (Phase 4)
router.include_router(skill_mapping_router)

# Include data access routes (content library, standards, curriculum, alignment)
router.include_router(data_access_router)

# Include agents and AI usage routes
router.include_router(agents_router)

# Include agent test endpoints
router.include_router(agent_tests_router)

# Include agent workflow execution routes
router.include_router(agent_workflows_router)

# Include custom content development routes
router.include_router(custom_content_router)

# Courses router disabled: dependency models removed as dead code
# router.include_router(courses_router)


class DocumentRequest(BaseModel):
    """Request model for adding documents"""
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    collection: str = "academian_content"


class SearchRequest(BaseModel):
    """Request model for searching documents"""
    query: str
    n_results: int = 5
    collection: str = "academian_content"


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    version: str = "1.0.0"


class AlignmentResponse(BaseModel):
    """Alignment response model"""
    id: str
    source_type: str
    source_id: str
    target_type: str
    standard_id: Optional[str] = None
    objective_id: Optional[str] = None
    score: float
    confidence: float
    evidence: List[str] = []
    status: str
    created_at: str
    reviewed_at: Optional[str] = None


class ApproveAlignmentRequest(BaseModel):
    """Request to approve an alignment"""
    notes: Optional[str] = None


class RejectAlignmentRequest(BaseModel):
    """Request to reject an alignment"""
    reason: Optional[str] = None
    notes: Optional[str] = None


class DraftSection(BaseModel):
    """Draft section content"""
    id: str
    title: str
    type: str
    content: str
    citations: Optional[List[str]] = []


class CreateLessonRequest(BaseModel):
    """Request to create a lesson"""
    title: str
    description: Optional[str] = None
    grade: str
    subject: str
    duration: Optional[int] = None
    audience: Optional[str] = None
    curriculum_id: Optional[str] = None
    content_ids: List[str] = []
    objective_ids: Optional[List[str]] = []
    sections: List[DraftSection]


class CreateAssessmentRequest(BaseModel):
    """Request to create an assessment"""
    title: str
    description: Optional[str] = None
    grade: str
    subject: str
    content_ids: List[str] = []
    objective_ids: Optional[List[str]] = []
    sections: List[DraftSection]


class ReviewItemResponse(BaseModel):
    """Review item in queue"""
    id: str
    type: str  # 'lesson', 'assessment', 'activity', 'content'
    title: str
    creator: Dict[str, str]
    submitted_at: str
    status: str  # 'pending', 'approved', 'rejected', 'revision'
    priority: str  # 'low', 'medium', 'high'
    summary: Optional[str] = None


class ApproveReviewRequest(BaseModel):
    """Request to approve a review"""
    notes: Optional[str] = None


class RejectReviewRequest(BaseModel):
    """Request to reject a review"""
    reason: Optional[str] = None


class ApproveContentRequest(BaseModel):
    notes: Optional[str] = None


class RejectContentRequest(BaseModel):
    reason: str
    notes: Optional[str] = None


class RequestRevisionRequest(BaseModel):
    """Request to ask for revisions"""
    required_changes: List[str]
    notes: Optional[str] = None


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Academian backend is running",
        "version": "1.0.0"
    }


@router.post("/documents/add")
async def add_documents(request: DocumentRequest):
    """Add documents to vector store"""
    try:
        vector_store = _get_vector_store(request.collection)
        ids = vector_store.add_documents(
            documents=request.documents,
            metadatas=request.metadatas
        )
        return {
            "status": "success",
            "message": f"Added {len(ids)} documents",
            "ids": ids
        }
    except Exception as e:
        logger.error(f"Error adding documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/documents/search")
async def search_documents(request: SearchRequest):
    """Search for documents in vector store"""
    try:
        vector_store = _get_vector_store(request.collection)
        results = vector_store.search(
            query=request.query,
            n_results=request.n_results
        )
        return {
            "status": "success",
            "results": results,
            "query": request.query
        }
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/collections/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """Get statistics for a collection"""
    try:
        vector_store = _get_vector_store(collection_name)
        stats = vector_store.get_stats()
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/documents/{collection_name}")
async def delete_documents(collection_name: str, ids: List[str]):
    """Delete documents from vector store"""
    try:
        vector_store = _get_vector_store(collection_name)
        vector_store.delete_documents(ids)
        return {
            "status": "success",
            "message": f"Deleted {len(ids)} documents"
        }
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/documents/upload/{collection_name}")
async def upload_documents(collection_name: str, file: UploadFile = File(...)):
    """Upload documents from a file"""
    try:
        content = await file.read()
        text = content.decode('utf-8')

        # Simple approach: split by newlines
        documents = [line.strip() for line in text.split('\n') if line.strip()]

        vector_store = _get_vector_store(collection_name)
        ids = vector_store.add_documents(
            documents=documents,
            metadatas=[{"source": file.filename, "index": i} for i in range(len(documents))]
        )

        return {
            "status": "success",
            "message": f"Uploaded {len(ids)} documents from {file.filename}",
            "count": len(ids)
        }
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Alignment Endpoints ====================

@router.get("/v1/alignments", response_model=Dict[str, Any])
async def list_alignments(
    source_type: Optional[str] = None,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """List alignments with optional filtering"""
    try:
        if source_id and source_type:
            alignments = AlignmentService.get_alignments_for_source(
                db, source_type, source_id, status
            )
        elif source_id:
            alignments = AlignmentService.get_alignments_for_standard(
                db, source_id, status
            )
        else:
            # Get all alignments with optional status filter
            # FIXED: Show all statuses by default (not just 'candidate')
            query = db.query(Alignment).filter(
                Alignment.tenant_id == get_current_tenant_id()
            )
            if status:
                query = query.filter(Alignment.status == status)
            alignments = query.order_by(Alignment.confidence.desc()).offset(skip).limit(limit).all()

        return {
            "status": "success",
            "total": len(alignments),
            "alignments": [
                {
                    "id": a.id,
                    "source_type": a.source_type,
                    "source_id": a.source_id,
                    "target_type": a.target_type,
                    "standard_id": a.standard_id,
                    "objective_id": a.objective_id,
                    "score": float(a.score) if a.score else 0.0,
                    "confidence": float(a.confidence) if a.confidence else 0.0,
                    "evidence": a.evidence or [],
                    "status": a.status,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "reviewed_at": a.reviewed_at.isoformat() if a.reviewed_at else None,
                }
                for a in alignments
            ]
        }
    except Exception as e:
        logger.error(f"Error listing alignments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/v1/alignments/template")
async def download_alignment_template():
    """Download the Excel template for bulk candidate alignment upload."""
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Alignment Candidates"
    headers = [
        "source_type", "source_id", "target_type", "standard_id", "objective_id",
        "score", "confidence", "evidence", "status",
    ]
    sheet.append(headers)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = "A1:I1"
    for cell in sheet[1]:
        cell.font = cell.font.copy(bold=True)
    for column in sheet.columns:
        sheet.column_dimensions[column[0].column_letter].width = 22

    instructions = workbook.create_sheet("Instructions")
    instructions.append(["Field", "Description"])
    instructions.append(["source_type", "Usually content, lesson, or objective."])
    instructions.append(["source_id", "ID of the source content, lesson, or objective."])
    instructions.append(["target_type", "Use standard or objective."])
    instructions.append(["standard_id", "Required when target_type is standard."])
    instructions.append(["objective_id", "Required when target_type is objective."])
    instructions.append(["score", "Optional decimal from 0 to 1."])
    instructions.append(["confidence", "Optional decimal from 0 to 1."])
    instructions.append(["evidence", "Optional supporting text or JSON array."])
    instructions.append(["status", "Optional; defaults to candidate."])
    instructions.freeze_panes = "A2"
    instructions.column_dimensions["A"].width = 22
    instructions.column_dimensions["B"].width = 80

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=alignment-candidates-template.xlsx"},
    )


@router.post("/v1/alignments/upload", response_model=Dict[str, Any])
async def upload_alignment_candidates(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Validate and import alignment candidates from an Excel workbook."""
    from openpyxl import load_workbook

    tenant_id = get_current_tenant_id()
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Upload an .xlsx Excel workbook")

    workbook = load_workbook(BytesIO(await file.read()), read_only=True, data_only=True)
    sheet = workbook["Alignment Candidates"] if "Alignment Candidates" in workbook.sheetnames else workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise HTTPException(status_code=400, detail="The workbook is empty")

    headers = [str(value).strip() if value is not None else "" for value in rows[0]]
    required = {"source_type", "source_id", "target_type"}
    missing = sorted(required - set(headers))
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")

    imported = []
    errors = []
    for row_number, values in enumerate(rows[1:], start=2):
        record = {headers[index]: values[index] if index < len(values) else None for index in range(len(headers))}
        if not any(value not in (None, "") for value in record.values()):
            continue
        source_type = str(record.get("source_type") or "").strip()
        source_id = str(record.get("source_id") or "").strip()
        target_type = str(record.get("target_type") or "").strip()
        standard_id = str(record.get("standard_id") or "").strip() or None
        objective_id = str(record.get("objective_id") or "").strip() or None

        if not source_type or not source_id or target_type not in {"standard", "objective"}:
            errors.append(f"Row {row_number}: source_type, source_id, and a valid target_type are required")
            continue
        if target_type == "standard" and not standard_id:
            errors.append(f"Row {row_number}: standard_id is required for target_type standard")
            continue
        if target_type == "objective" and not objective_id:
            errors.append(f"Row {row_number}: objective_id is required for target_type objective")
            continue

        if standard_id and not db.query(Standard).filter(Standard.id == standard_id, Standard.tenant_id == tenant_id).first():
            errors.append(f"Row {row_number}: standard_id was not found for this tenant")
            continue
        if objective_id and not db.query(LearningObjective).filter(LearningObjective.id == objective_id, LearningObjective.tenant_id == tenant_id).first():
            errors.append(f"Row {row_number}: objective_id was not found for this tenant")
            continue

        try:
            score = float(record.get("score") or 0)
            confidence = float(record.get("confidence") or 0)
            if not 0 <= score <= 1 or not 0 <= confidence <= 1:
                raise ValueError
        except (TypeError, ValueError):
            errors.append(f"Row {row_number}: score and confidence must be decimals from 0 to 1")
            continue

        evidence = record.get("evidence")
        if isinstance(evidence, str):
            try:
                evidence = json.loads(evidence)
            except json.JSONDecodeError:
                evidence = [evidence] if evidence else []
        evidence = evidence or []
        imported.append(Alignment(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            standard_id=standard_id,
            objective_id=objective_id,
            score=score,
            confidence=confidence,
            evidence=evidence,
            status=str(record.get("status") or "candidate").strip() or "candidate",
        ))

    if errors:
        raise HTTPException(status_code=400, detail={"message": "No rows were imported", "errors": errors})
    if not imported:
        raise HTTPException(status_code=400, detail="No candidate rows found")

    try:
        db.add_all(imported)
        db.commit()
    except Exception as error:
        db.rollback()
        logger.error("Bulk alignment import failed: %s", error)
        raise HTTPException(status_code=409, detail="Candidates could not be imported; check for duplicates")

    return {
        "status": "success",
        "imported_count": len(imported),
        "message": f"Imported {len(imported)} alignment candidates",
    }


@router.get("/v1/alignments/{alignment_id}", response_model=Dict[str, Any])
async def get_alignment(
    alignment_id: str,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get a specific alignment with evidence details"""
    try:
        alignment = db.query(Alignment).filter(Alignment.id == alignment_id).first()

        if not alignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alignment not found"
            )

        return {
            "status": "success",
            "alignment": {
                "id": alignment.id,
                "source_type": alignment.source_type,
                "source_id": alignment.source_id,
                "target_type": alignment.target_type,
                "standard_id": alignment.standard_id,
                "objective_id": alignment.objective_id,
                "score": float(alignment.score) if alignment.score else 0.0,
                "confidence": float(alignment.confidence) if alignment.confidence else 0.0,
                "evidence": alignment.evidence or [],
                "status": alignment.status,
                "created_at": alignment.created_at.isoformat() if alignment.created_at else None,
                "reviewed_at": alignment.reviewed_at.isoformat() if alignment.reviewed_at else None,
                "reviewed_by": alignment.reviewed_by,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/v1/alignments/{alignment_id}/approve", response_model=Dict[str, Any])
async def approve_alignment(
    alignment_id: str,
    req: ApproveAlignmentRequest = None,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Approve an alignment"""
    try:
        alignment = db.query(Alignment).filter(Alignment.id == alignment_id).first()

        if not alignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alignment not found"
            )

        # Update alignment status
        alignment.status = "approved"
        alignment.reviewed_at = db.func.now()
        db.commit()
        db.refresh(alignment)

        logger.info(f"Approved alignment: {alignment_id}")

        return {
            "status": "success",
            "message": "Alignment approved successfully",
            "alignment": {
                "id": alignment.id,
                "source_type": alignment.source_type,
                "source_id": alignment.source_id,
                "target_type": alignment.target_type,
                "standard_id": alignment.standard_id,
                "objective_id": alignment.objective_id,
                "score": float(alignment.score) if alignment.score else 0.0,
                "confidence": float(alignment.confidence) if alignment.confidence else 0.0,
                "evidence": alignment.evidence or [],
                "status": alignment.status,
                "created_at": alignment.created_at.isoformat() if alignment.created_at else None,
                "reviewed_at": alignment.reviewed_at.isoformat() if alignment.reviewed_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error approving alignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/v1/alignments/{alignment_id}/reject", response_model=Dict[str, Any])
async def reject_alignment(
    alignment_id: str,
    req: RejectAlignmentRequest = None,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Reject an alignment"""
    try:
        alignment = db.query(Alignment).filter(Alignment.id == alignment_id).first()

        if not alignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alignment not found"
            )

        # Update alignment status
        alignment.status = "rejected"
        alignment.reviewed_at = db.func.now()
        db.commit()
        db.refresh(alignment)

        logger.info(f"Rejected alignment: {alignment_id}")

        return {
            "status": "success",
            "message": "Alignment rejected successfully",
            "alignment": {
                "id": alignment.id,
                "source_type": alignment.source_type,
                "source_id": alignment.source_id,
                "target_type": alignment.target_type,
                "standard_id": alignment.standard_id,
                "objective_id": alignment.objective_id,
                "score": float(alignment.score) if alignment.score else 0.0,
                "confidence": float(alignment.confidence) if alignment.confidence else 0.0,
                "evidence": alignment.evidence or [],
                "status": alignment.status,
                "created_at": alignment.created_at.isoformat() if alignment.created_at else None,
                "reviewed_at": alignment.reviewed_at.isoformat() if alignment.reviewed_at else None,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error rejecting alignment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Authoring Endpoints ====================

@router.post("/v1/lessons", response_model=Dict[str, Any])
async def create_lesson(
    req: CreateLessonRequest,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new lesson"""
    try:
        tenant_id = get_current_tenant_id()
        if not req.curriculum_id:
            raise HTTPException(status_code=400, detail="curriculum_id is required")
        curriculum = db.query(Curriculum).filter(
            Curriculum.id == req.curriculum_id,
            Curriculum.tenant_id == tenant_id,
        ).first()
        if not curriculum:
            raise HTTPException(status_code=404, detail="Curriculum not found")

        lesson = Lesson(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            curriculum_id=curriculum.id,
            title=req.title,
            description=req.description,
            grade=req.grade,
            subject=req.subject,
            duration_minutes=req.duration,
            status="draft",
            content={
                "audience": req.audience,
                "content_ids": req.content_ids,
                "objective_ids": req.objective_ids or [],
                "sections": [s.model_dump() for s in req.sections],
            },
        )
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        return {
            "status": "success",
            "message": "Lesson created successfully",
            "lesson": {
                "id": lesson.id,
                "curriculum_id": lesson.curriculum_id,
                "title": lesson.title,
                "status": lesson.status,
                "created_at": lesson.created_at.isoformat(),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lesson: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v1/assessments", response_model=Dict[str, Any])
async def create_assessment(
    req: CreateAssessmentRequest,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Create a new assessment"""
    try:
        assessment_id = str(uuid.uuid4())
        assessment_data = {
            "id": assessment_id,
            "title": req.title,
            "description": req.description,
            "grade": req.grade,
            "subject": req.subject,
            "content_ids": req.content_ids,
            "objective_ids": req.objective_ids or [],
            "sections": [s.dict() for s in req.sections],
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        logger.info(f"Created assessment: {assessment_id}")
        return {
            "status": "success",
            "message": "Assessment created successfully",
            "assessment": assessment_data
        }
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== Review Endpoints ====================

@router.get("/v1/reviews", response_model=Dict[str, Any])
async def list_reviews(
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """List reviews in queue"""
    try:
        mock_reviews = [
            {
                "id": "review-1",
                "type": "lesson",
                "title": "Introduction to Fractions",
                "creator": {"id": "user-1", "name": "John Doe", "email": "john@example.com"},
                "submitted_at": datetime.utcnow().isoformat(),
                "status": "pending",
                "priority": "high",
                "summary": "Comprehensive lesson on basic fraction concepts"
            },
            {
                "id": "review-2",
                "type": "assessment",
                "title": "Photosynthesis Quiz",
                "creator": {"id": "user-2", "name": "Jane Smith", "email": "jane@example.com"},
                "submitted_at": datetime.utcnow().isoformat(),
                "status": "pending",
                "priority": "medium",
                "summary": "Assessment covering photosynthesis process and stages"
            },
        ]
        filtered = mock_reviews
        if status_filter and status_filter != "all":
            filtered = [r for r in mock_reviews if r["status"] == status_filter]
        return {"status": "success", "total": len(filtered), "items": filtered[skip:skip+limit]}
    except Exception as e:
        logger.error(f"Error listing reviews: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v1/reviews/{review_id}", response_model=Dict[str, Any])
async def get_review(
    review_id: str,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get review item details"""
    try:
        review_data = {
            "id": review_id,
            "type": "lesson",
            "title": "Introduction to Fractions",
            "creator": {"id": "user-1", "name": "John Doe", "email": "john@example.com"},
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "pending",
            "priority": "high",
            "summary": "Comprehensive lesson on basic fraction concepts",
            "content": "This lesson covers:\n\n1. Understanding fractions\n2. Comparing fractions\n3. Adding and subtracting fractions\n4. Real-world applications",
            "metrics": {
                "readability_score": 8.5,
                "alignment_score": 0.87,
                "accessibility_score": 0.92,
                "estimated_duration": 45
            }
        }
        return {"status": "success", "item": review_data}
    except Exception as e:
        logger.error(f"Error getting review: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v1/reviews/{review_id}/approve", response_model=Dict[str, Any])
async def approve_review(
    review_id: str,
    req: ApproveReviewRequest = None,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Approve a review submission"""
    try:
        logger.info(f"Approved review: {review_id}")
        return {
            "status": "success",
            "message": "Review approved successfully",
            "review_id": review_id,
            "decision": "approved",
            "approved_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error approving review: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v1/reviews/{review_id}/reject", response_model=Dict[str, Any])
async def reject_review(
    review_id: str,
    req: RejectReviewRequest = None,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Reject a review submission"""
    try:
        logger.info(f"Rejected review: {review_id}")
        return {
            "status": "success",
            "message": "Review rejected successfully",
            "review_id": review_id,
            "decision": "rejected",
            "reason": req.reason if req else None,
            "rejected_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error rejecting review: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v1/reviews/{review_id}/revision", response_model=Dict[str, Any])
async def request_revision(
    review_id: str,
    req: RequestRevisionRequest = None,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Request revision on a review submission"""
    try:
        logger.info(f"Requested revision for review: {review_id}")
        return {
            "status": "success",
            "message": "Revision requested successfully",
            "review_id": review_id,
            "decision": "revision",
            "required_changes": req.required_changes if req else [],
            "requested_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error requesting revision: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v1/reviews/stats", response_model=Dict[str, Any])
async def get_review_stats(
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get review statistics"""
    try:
        stats = {
            "pending": 12,
            "approved": 45,
            "rejected": 8,
            "revision": 5,
            "avgResolutionTime": 2.5
        }
        return {"status": "success", "stats": stats}
    except Exception as e:
        logger.error(f"Error getting review stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== Analytics Endpoints ====================

@router.get("/v1/analytics/dashboard", response_model=Dict[str, Any])
async def get_analytics_dashboard(
    period: str = "week",
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get analytics dashboard data"""
    try:
        dashboard_data = {
            "overview": {
                "total_content_items": 142,
                "total_alignments": 385,
                "approved_alignments": 298,
                "pending_alignments": 54,
                "rejected_alignments": 33
            },
            "coverage": {
                "fully_aligned": 28,
                "partially_aligned": 45,
                "not_aligned": 22,
                "alignment_percentage": 74.6
            },
            "standards": {
                "frameworks": 5,
                "standards": 187,
                "covered_standards": 152,
                "coverage_rate": 81.3
            },
            "timeline": {
                "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "alignments_created": [12, 19, 15, 22, 18, 14, 9],
                "alignments_approved": [8, 14, 11, 18, 15, 10, 6]
            },
            "quality": {
                "avg_confidence_score": 0.82,
                "high_confidence": 198,
                "medium_confidence": 145,
                "low_confidence": 42
            },
            "performance": {
                "avg_review_time": 2.3,
                "avg_approval_rate": 0.85,
                "top_reviewer": "Jane Smith",
                "reviews_completed": 145
            }
        }
        return {"status": "success", "period": period, "data": dashboard_data}
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v1/analytics/alignments", response_model=Dict[str, Any])
async def get_alignment_analytics(
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get alignment-specific analytics"""
    try:
        analytics = {
            "by_standard_framework": [
                {"name": "CCSS Math", "aligned": 87, "pending": 12, "rejected": 5},
                {"name": "CCSS ELA", "aligned": 65, "pending": 18, "rejected": 8},
                {"name": "NGSS", "aligned": 92, "pending": 14, "rejected": 3},
            ],
            "by_content_type": [
                {"type": "Documents", "count": 45, "aligned": 38},
                {"type": "Videos", "count": 32, "aligned": 28},
                {"type": "Interactive", "count": 28, "aligned": 24},
            ],
            "confidence_distribution": {
                "90-100%": 145,
                "80-89%": 98,
                "70-79%": 67,
                "60-69%": 42,
                "<60%": 33
            }
        }
        return {"status": "success", "analytics": analytics}
    except Exception as e:
        logger.error(f"Error getting alignment analytics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v1/analytics/coverage", response_model=Dict[str, Any])
async def get_coverage_analytics(
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get curriculum coverage analytics"""
    try:
        coverage = {
            "total_standards": 187,
            "covered_standards": 152,
            "coverage_percentage": 81.3,
            "by_grade": [
                {"grade": "3", "total": 24, "covered": 19, "coverage": 79.2},
                {"grade": "4", "total": 28, "covered": 24, "coverage": 85.7},
                {"grade": "5", "total": 31, "covered": 27, "coverage": 87.1},
                {"grade": "6", "total": 26, "covered": 21, "coverage": 80.8},
                {"grade": "7", "total": 29, "covered": 24, "coverage": 82.8},
                {"grade": "8", "total": 27, "covered": 23, "coverage": 85.2},
            ],
            "by_subject": [
                {"subject": "Mathematics", "coverage": 87.5},
                {"subject": "Language Arts", "coverage": 84.2},
                {"subject": "Science", "coverage": 78.9},
                {"subject": "Social Studies", "coverage": 76.3},
            ]
        }
        return {"status": "success", "coverage": coverage}
    except Exception as e:
        logger.error(f"Error getting coverage analytics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/v1/content/upload", response_model=Dict[str, Any])
async def upload_content(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    grade: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Save a content asset and process it after the upload response."""
    content = None
    file_path = None
    try:
        content_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        tenant_id = get_current_tenant_id()

        upload_dir = Path(__file__).resolve().parent.parent / "data" / "uploads" / "content"
        upload_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "upload").suffix.lower()
        file_path = upload_dir / f"{content_id}{suffix}"
        with file_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)

        try:
            parsed_tags = json.loads(tags) if tags else []
            if not isinstance(parsed_tags, list):
                parsed_tags = [str(parsed_tags)]
        except json.JSONDecodeError:
            parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        content = Content(
            id=content_id,
            tenant_id=tenant_id,
            title=title,
            content_type="document",
            source=str(file_path),
            content_metadata={
                "description": description,
                "subject": subject,
                "grade": grade,
                "tags": parsed_tags,
                "original_filename": file.filename,
                "mime_type": file.content_type,
                "file_path": str(file_path),
            },
            status="pending",
        )
        db.add(content)
        db.commit()
        db.refresh(content)

        background_tasks.add_task(
            _process_content_upload,
            content_id,
            tenant_id,
            title,
            str(file_path),
            suffix,
            file.content_type,
        )

        now = datetime.utcnow().isoformat()
        job = {
            "id": job_id,
            "tenant_id": tenant_id,
            "content_id": content_id,
            "status": "queued",
            "progress": 0,
            "stage": "queued",
            "title": title,
            "description": description,
            "subject": subject,
            "grade": grade,
            "tags": parsed_tags,
            "file_name": file.filename,
            "mime_type": file.content_type,
            "started_at": None,
            "completed_at": None,
            "created_at": now,
            "updated_at": now,
        }

        return {
            "status": "success",
            "message": "Content uploaded and queued for processing",
            "job": job,
        }
    except Exception as e:
        db.rollback()
        if file_path and file_path.exists():
            file_path.unlink()
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def _process_content_upload(
    content_id: str,
    tenant_id: str,
    title: str,
    file_path: str,
    suffix: str,
    mime_type: Optional[str],
) -> None:
    """Extract and index an uploaded asset without blocking the upload request."""
    db = SessionLocal()
    content = None
    try:
        content = db.query(Content).filter(
            Content.id == content_id,
            Content.tenant_id == tenant_id,
        ).first()
        if not content:
            raise ValueError(f"Content {content_id} not found")

        extracted_text = ""

        # Try multiple text extraction methods based on file type
        try:
            if suffix == ".pdf":
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
                    if extracted_text:
                        logger.info(f"Extracted text from PDF {content_id}: {len(extracted_text)} chars")
                    else:
                        logger.warning(f"PDF {content_id} contains no extractable text (may be scanned/image-based)")
                except Exception as pdf_error:
                    logger.warning(f"PDF extraction failed for {content_id}: {str(pdf_error)}")

            elif suffix == ".docx" or mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    extracted_text = "\n".join(para.text for para in doc.paragraphs if para.text.strip()).strip()
                    if extracted_text:
                        logger.info(f"Extracted text from DOCX {content_id}: {len(extracted_text)} chars")
                    else:
                        logger.warning(f"DOCX {content_id} contains no text")
                except Exception as docx_error:
                    logger.warning(f"DOCX extraction failed for {content_id}: {str(docx_error)}")

            elif suffix == ".txt" or mime_type == "text/plain":
                try:
                    extracted_text = Path(file_path).read_text(encoding="utf-8")
                    if extracted_text:
                        logger.info(f"Extracted text from TXT {content_id}: {len(extracted_text)} chars")
                except UnicodeDecodeError:
                    # Try with different encoding
                    try:
                        extracted_text = Path(file_path).read_text(encoding="latin-1")
                        logger.info(f"Extracted text from TXT {content_id} (latin-1): {len(extracted_text)} chars")
                    except Exception as txt_error:
                        logger.warning(f"TXT extraction failed for {content_id}: {str(txt_error)}")

            else:
                logger.info(f"Content {content_id} has unsupported file type {suffix} - storing as-is")

        except Exception as extraction_error:
            logger.warning(f"Text extraction skipped for {content_id}: {str(extraction_error)}")

        # Set status based on whether text was extracted
        status_value = "ingested"

        if extracted_text:
            content.raw_content = extracted_text
            try:
                chunks = [
                    extracted_text[index:index + 1000]
                    for index in range(0, len(extracted_text), 900)
                ]
                vector_store = _get_vector_store("academian_content")
                vector_store.add_documents(
                    documents=chunks,
                    metadatas=[{
                        "content_id": content_id,
                        "tenant_id": tenant_id,
                        "title": title,
                        "source": file_path,
                        "chunk_index": index,
                    } for index in range(len(chunks))],
                    ids=[f"{content_id}:{index}" for index in range(len(chunks))],
                )
                status_value = "indexed"
                logger.info(f"Indexed {len(chunks)} chunks for content {content_id}")
            except Exception as index_error:
                logger.error(f"Vector indexing failed for {content_id}: {str(index_error)}")
                status_value = "ingested"
        else:
            logger.warning(f"No text extracted for content {content_id} - marking as ingested without indexing")

        content.status = status_value
        if status_value == "indexed":
            try:
                governance = ContentGovernanceAgent.review(content)
                content.content_metadata = {
                    **(content.content_metadata or {}),
                    "governance": governance,
                }
                content.status = "review_required"
                logger.info(f"Governance review completed for {content_id}: {governance.get('recommendation')}")
            except Exception as gov_error:
                logger.error(f"Governance review failed for {content_id}: {str(gov_error)}")
                content.status = "indexed"

        db.commit()
        logger.info(f"Processed uploaded content {content_id} with status {content.status}")

    except Exception as e:
        db.rollback()
        try:
            content = db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.status = "failed"
                error_msg = f"{type(e).__name__}: {str(e)}"
                content.content_metadata = {
                    **(content.content_metadata or {}),
                    "processing_error": error_msg,
                }
                db.commit()
                logger.error(f"Content {content_id} marked as failed: {error_msg}")
        except Exception as rollback_error:
            logger.error(f"Error updating failed status for {content_id}: {str(rollback_error)}")
        logger.error(f"Error processing uploaded content {content_id}: {str(e)}", exc_info=True)
    finally:
        db.close()


@router.post("/v1/content/{content_id}/governance-review", response_model=Dict[str, Any])
async def review_content_governance(
    content_id: str,
    db: Session = Depends(get_db),
):
    """Run governance checks and recommend approval for indexed content."""
    tenant_id = get_current_tenant_id()
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.tenant_id == tenant_id,
    ).first()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    if content.status not in {"indexed", "review_required"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content must be indexed before governance review",
        )

    governance = ContentGovernanceAgent.review(content)
    content.content_metadata = {
        **(content.content_metadata or {}),
        "governance": governance,
    }
    content.status = "review_required"
    db.commit()
    db.refresh(content)
    return {
        "status": "success",
        "content_id": content.id,
        "content_status": content.status,
        "governance": governance,
    }


@router.post("/v1/content/{content_id}/approve", response_model=Dict[str, Any])
async def approve_content(
    content_id: str,
    request: ApproveContentRequest = ApproveContentRequest(),
    db: Session = Depends(get_db),
):
    """Approve governed content and publish it to the library."""
    tenant_id = get_current_tenant_id()
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.tenant_id == tenant_id,
    ).first()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    if content.status != "review_required":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content must be in review_required status before approval",
        )

    content.status = "published"
    content.content_metadata = {
        **(content.content_metadata or {}),
        "approval": {
            "decision": "approved",
            "notes": request.notes,
            "approved_at": datetime.utcnow().isoformat(),
        },
    }
    db.commit()
    db.refresh(content)
    return {
        "id": content.id,
        "title": content.title,
        "content_type": content.content_type,
        "status": content.status,
        "version": content.version,
        "created_at": content.created_at.isoformat() if content.created_at else None,
        "updated_at": content.updated_at.isoformat() if content.updated_at else None,
    }


@router.post("/v1/content/{content_id}/reject", response_model=Dict[str, Any])
async def reject_content(
    content_id: str,
    request: RejectContentRequest,
    db: Session = Depends(get_db),
):
    """Reject governed content and remove its stored file and vectors."""
    tenant_id = get_current_tenant_id()
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.tenant_id == tenant_id,
    ).first()
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    if content.status != "review_required":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Content must be in review_required status before rejection",
        )

    try:
        vector_store = _get_vector_store("academian_content")
        vector_result = vector_store.collection.get(where={"content_id": content_id})
        vector_ids = vector_result.get("ids", [])
        if vector_ids:
            vector_store.delete_documents(vector_ids)
    except Exception as error:
        logger.warning("Could not delete vectors for rejected content %s: %s", content_id, error)

    if content.source:
        source_path = Path(content.source)
        if source_path.is_file():
            source_path.unlink()

    rejection = {
        "decision": "rejected",
        "reason": request.reason,
        "rejected_at": datetime.utcnow().isoformat(),
    }
    db.delete(content)
    db.commit()
    return {
        "status": "success",
        "message": "Content rejected and deleted",
        "content_id": content_id,
        "rejection": rejection,
    }


@router.post("/v1/content/upload-legacy", response_model=Dict[str, Any])
async def upload_content_legacy(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    grade: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Upload a content asset and kick off its ingestion job"""
    content = None
    try:
        content_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())
        tenant_id = get_current_tenant_id()

        upload_dir = Path(__file__).resolve().parent.parent / "data" / "uploads" / "content"
        upload_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "upload").suffix.lower()
        file_path = upload_dir / f"{content_id}{suffix}"
        with file_path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                output.write(chunk)

        try:
            parsed_tags = json.loads(tags) if tags else []
            if not isinstance(parsed_tags, list):
                parsed_tags = [str(parsed_tags)]
        except json.JSONDecodeError:
            parsed_tags = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

        metadata = {
            "description": description,
            "subject": subject,
            "grade": grade,
            "tags": parsed_tags,
            "original_filename": file.filename,
            "mime_type": file.content_type,
            "file_path": str(file_path),
        }
        content = Content(
            id=content_id,
            tenant_id=tenant_id,
            title=title,
            content_type="document",
            source=str(file_path),
            content_metadata=metadata,
            status="pending",
        )
        db.add(content)
        db.commit()
        db.refresh(content)

        status_value = "ingested"
        extracted_text = ""
        if suffix == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(str(file_path))
            extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        elif file.content_type == "text/plain":
            extracted_text = file_path.read_text(encoding="utf-8")

        if extracted_text:
            content.raw_content = extracted_text
            chunks = [
                extracted_text[index:index + 1000]
                for index in range(0, len(extracted_text), 900)
            ]
            vector_store = _get_vector_store("academian_content")
            vector_store.add_documents(
                documents=chunks,
                metadatas=[{
                    "content_id": content_id,
                    "tenant_id": tenant_id,
                    "title": title,
                    "source": str(file_path),
                    "chunk_index": index,
                } for index in range(len(chunks))],
                ids=[f"{content_id}:{index}" for index in range(len(chunks))],
            )
            status_value = "indexed"

        content.status = status_value
        db.commit()
        db.refresh(content)

        job = {
            "id": job_id,
            "tenant_id": tenant_id,
            "content_id": content_id,
            "status": "completed",
            "progress": 100,
            "stage": status_value,
            "title": title,
            "description": description,
            "subject": subject,
            "grade": grade,
            "tags": tags.split(",") if tags else [],
            "file_name": file.filename,
            "mime_type": file.content_type,
            "started_at": content.created_at.isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "created_at": content.created_at.isoformat(),
            "updated_at": content.updated_at.isoformat(),
        }

        return {
            "status": "success",
            "message": "Content uploaded and processed successfully",
            "job": job,
        }
    except Exception as e:
        db.rollback()
        if content is not None:
            content.status = "failed"
            content.content_metadata = {
                **(content.content_metadata or {}),
                "processing_error": str(e),
            }
            db.add(content)
            db.commit()
        logger.error(f"Error uploading content: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/v1/lessons", response_model=Dict[str, Any])
async def get_lessons(
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get lessons (GET endpoint)"""
    try:
        lessons = [
            {
                "id": "lesson_1",
                "title": "Fractions Basics",
                "grade": "4",
                "subject": "Mathematics",
                "created_at": datetime.now().isoformat(),
            },
        ]
        return {
            "status": "success",
            "lessons": lessons,
            "total": 1,
        }
    except Exception as e:
        logger.error(f"Error getting lessons: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
