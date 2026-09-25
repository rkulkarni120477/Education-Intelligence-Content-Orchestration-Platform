"""
Workforce Alignment Workflow State Definition.

Defines the typed state for the LangGraph workforce alignment workflow.
This represents the complete state carried through the graph execution.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class WorkforceAlignmentState(BaseModel):
    """Complete state for workforce alignment workflow execution."""

    # ===== CONTEXT & IDENTIFICATION =====
    tenant_id: str = Field(..., description="Tenant identifier for multi-tenancy")
    request_id: str = Field(..., description="Unique workflow request ID")
    initiating_user_id: str = Field(..., description="User who initiated the workflow")
    workflow_execution_id: Optional[str] = Field(None, description="Database workflow_execution ID")

    # ===== PROGRAM & COURSE SCOPE =====
    program_id: str = Field(..., description="Institution program identifier")
    program_name: str = Field(..., description="Program name")
    course_ids: List[str] = Field(default_factory=list, description="Curriculum/course IDs to align")

    # ===== INPUT ASSETS (IMMUTABLE) =====
    input_package_id: str = Field(..., description="Course package ID (immutable)")
    input_package_format: str = Field(..., description="Package format: imscc, zip, upload")
    input_skill_framework_id: str = Field(..., description="Skill framework ID (e.g., O*NET)")
    input_style_guide_id: Optional[str] = Field(None, description="Style guide ID")

    # ===== REQUIREMENTS EXTRACTION & CONFIRMATION =====
    requirements_profile_id: Optional[str] = Field(None, description="Created requirements profile ID")
    target_role_ids: List[str] = Field(default_factory=list, description="Target workforce role IDs")
    required_skill_ids: List[str] = Field(default_factory=list, description="Required skill IDs")
    requirements_extracted: bool = Field(False, description="Requirements extraction completed")
    requirements_confirmed: bool = Field(False, description="Requirements confirmed by human")
    confirmed_by_user_id: Optional[str] = Field(None, description="User who confirmed requirements")
    requirements_edit_notes: Optional[str] = Field(None, description="Notes on requirement edits")
    extracted_target_roles: List[Dict[str, str]] = Field(default_factory=list, description="Extracted target roles from LLM")
    extracted_required_skills: List[Dict[str, str]] = Field(default_factory=list, description="Extracted required skills from LLM")
    extracted_constraints: Dict[str, Any] = Field(default_factory=dict, description="Extracted constraints from requirements")
    extracted_accessibility_requirements: List[str] = Field(default_factory=list, description="Extracted accessibility requirements")
    extracted_style_guidelines: List[str] = Field(default_factory=list, description="Extracted style/branding guidelines")
    extraction_ambiguities: List[Dict[str, str]] = Field(default_factory=list, description="Ambiguities detected during extraction")
    extraction_confidence: float = Field(1.0, description="Confidence score of requirements extraction (0-1)")

    # ===== COURSE INGESTION & STRUCTURE =====
    course_structure_extracted: bool = Field(False, description="Course structure extraction completed")
    course_package_version_id: Optional[str] = Field(None, description="Course package version ID")
    extraction_errors: List[str] = Field(default_factory=list, description="Extraction error details")
    course_hierarchy_data: Dict[str, Any] = Field(default_factory=dict, description="Extracted course hierarchy")
    extracted_learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives extracted from course")
    content_embeddings: Dict[str, List[float]] = Field(default_factory=dict, description="Embeddings for course content items")

    # ===== SKILL MAPPING & COVERAGE =====
    skill_mappings_generated: bool = Field(False, description="Skill mappings generated")
    candidate_skill_alignments: List[Dict[str, Any]] = Field(default_factory=list, description="Proposed skill alignments")
    coverage_report_id: Optional[str] = Field(None, description="Coverage report ID")
    gap_analysis_id: Optional[str] = Field(None, description="Gap analysis ID")
    skill_mappings_reviewed: bool = Field(False, description="Skill mappings reviewed by human")
    approved_skill_alignments: List[str] = Field(default_factory=list, description="Approved alignment IDs")
    rejected_skill_alignments: List[str] = Field(default_factory=list, description="Rejected alignment IDs")
    coverage_by_skill: Dict[str, float] = Field(default_factory=dict, description="Coverage percentage by skill ID")
    total_alignments: int = Field(0, description="Total skill-to-content alignments created")
    covered_skills: List[str] = Field(default_factory=list, description="Skills with >= 80% coverage")
    uncovered_skills: List[str] = Field(default_factory=list, description="Skills with < 10% coverage")
    overall_coverage_percentage: float = Field(0.0, description="Weighted average skill coverage (0-1)")
    critical_gaps_identified: List[Dict[str, Any]] = Field(default_factory=list, description="Critical skill gaps")

    # ===== RECOMMENDATIONS =====
    recommendations_generated: bool = Field(False, description="Recommendations generated")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Generated recommendations")
    approved_recommendations: List[str] = Field(default_factory=list, description="Approved recommendation IDs")
    recommendations_reviewed: bool = Field(False, description="Recommendations reviewed")

    # ===== DRAFT MATERIALS =====
    draft_generation_complete: bool = Field(False, description="Draft content generation completed")
    draft_artifact_ids: List[str] = Field(default_factory=list, description="Generated draft artifact IDs")
    draft_validation_passed: bool = Field(False, description="Draft validation passed")
    draft_validation_errors: List[str] = Field(default_factory=list, description="Draft validation error details")

    # ===== ACCESSIBILITY =====
    accessibility_audit_id: Optional[str] = Field(None, description="Accessibility audit ID")
    accessibility_findings: List[Dict[str, Any]] = Field(default_factory=list, description="Accessibility findings")
    accessibility_remediated: bool = Field(False, description="Accessibility issues remediated")
    accessibility_review_complete: bool = Field(False, description="Accessibility review complete")
    accessibility_approved: bool = Field(False, description="Accessibility approved by reviewer")

    # ===== EXPORT & FINAL APPROVAL =====
    export_format: str = Field("imscc", description="Target export format: imscc, zip, pdf, docx")
    export_profile: str = Field("1EdTech-CC-1.3", description="Export profile/version")
    export_validation_passed: bool = Field(False, description="Export validation passed")
    export_validation_errors: List[str] = Field(default_factory=list, description="Export validation errors")
    final_approval_complete: bool = Field(False, description="Final approval received")
    final_approved_by_user_id: Optional[str] = Field(None, description="User who approved for export")
    final_approval_timestamp: Optional[datetime] = Field(None, description="Final approval timestamp")

    # ===== HUMAN CHECKPOINTS =====
    current_checkpoint: Optional[str] = Field(None, description="Current checkpoint name")
    human_interrupt_pending: bool = Field(False, description="Workflow waiting for human decision")
    human_interrupt_reason: Optional[str] = Field(None, description="Reason for human interrupt")
    human_decision: Optional[Dict[str, Any]] = Field(None, description="Human's decision data")
    human_decision_timestamp: Optional[datetime] = Field(None, description="When decision was made")

    # ===== WORKFLOW STATUS & TRACKING =====
    workflow_status: str = Field("pending", description="Overall workflow status")
    # pending, requirements, ingestion, analysis, recommendations, generation, accessibility, approval, completed, failed
    current_node: str = Field("start", description="Currently executing node")
    completed_nodes: List[str] = Field(default_factory=list, description="Nodes that have completed")

    # ===== ERROR & RETRY HANDLING =====
    error_message: Optional[str] = Field(None, description="Overall error message if failed")
    last_node_error: Optional[str] = Field(None, description="Error from last node")
    retry_count: int = Field(0, description="Number of retries so far")
    max_retries: int = Field(3, description="Maximum allowed retries")

    # ===== MODEL & SYSTEM VERSIONS =====
    graph_version: str = Field("1.0.0", description="LangGraph workflow version")
    model_name: str = Field("claude-opus-5-5", description="LLM model name")
    model_version: Optional[str] = Field(None, description="LLM model version")
    prompt_versions: Dict[str, str] = Field(default_factory=dict, description="Prompt versions used")

    # ===== RETRIEVAL & EVIDENCE =====
    retrieved_context_refs: List[Dict[str, str]] = Field(default_factory=list, description="Retrieved context references")
    evidence_references: List[Dict[str, Any]] = Field(default_factory=list, description="All evidence references in workflow")

    # ===== METADATA & TIMESTAMPS =====
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Workflow creation time")
    started_at: Optional[datetime] = Field(None, description="Workflow start time")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Workflow completion time")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

    def to_checkpoint_dict(self) -> Dict[str, Any]:
        """Convert to dict for checkpoint serialization."""
        return self.dict()

    @classmethod
    def from_checkpoint_dict(cls, data: Dict[str, Any]) -> "WorkforceAlignmentState":
        """Restore from checkpoint dict."""
        return cls(**data)
