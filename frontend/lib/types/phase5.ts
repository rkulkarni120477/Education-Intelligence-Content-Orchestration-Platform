/**
 * Phase 5: Frontend Types & Interfaces
 *
 * Type definitions for skill mapping, recommendations,
 * coverage visualization, and approval workflows.
 */

// ===== SKILL ALIGNMENT TYPES =====

export interface SkillAlignmentItem {
  id: string;
  skillId: string;
  skillName: string;
  contentId: string;
  contentTitle: string;
  alignmentType: 'introduces' | 'reinforces' | 'assesses' | 'covers';
  proficiencyLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  confidence: number; // 0-1
  evidence: Array<{
    quote: string;
    reference: string;
  }>;
  supportingObjectives: string[];
  status: 'candidate' | 'approved' | 'rejected';
  reviewedBy?: string;
  reviewedAt?: string;
  reviewNotes?: string;
}

export interface SkillAlignmentListResponse {
  status: 'success' | 'error';
  workflowId: string;
  alignments: SkillAlignmentItem[];
  total: number;
}

// ===== RECOMMENDATION TYPES =====

export interface RecommendationItem {
  id: string;
  type: 'add_content' | 'reorder_content' | 'enhance_assessment' | 'add_practice' | 'improve_clarity' | 'add_accessibility' | 'improve_sequencing';
  priority: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  description: string;
  rationale: string;
  implementationSteps: string[];
  affectedSkills: string[];
  estimatedEffort: 'small' | 'medium' | 'large';
  expectedImpact: string;
  status: 'proposed' | 'approved' | 'rejected' | 'implemented';
  approvedBy?: string;
  approvedAt?: string;
  approvalNotes?: string;
  implementationNotes?: string;
  implementedAt?: string;
}

export interface RecommendationListResponse {
  status: 'success' | 'error';
  workflowId: string;
  recommendations: RecommendationItem[];
  total: number;
}

// ===== GAP ANALYSIS TYPES =====

export interface GapItem {
  id: string;
  skillId: string;
  skillName: string;
  requiredProficiency: string;
  currentCoverage: number; // 0-1
  gapSeverity: 'critical' | 'high' | 'medium' | 'low';
  gapDescription: string;
  recommendations: Array<{
    title: string;
    description: string;
  }>;
}

export interface GapAnalysisListResponse {
  status: 'success' | 'error';
  workflowId: string;
  gaps: GapItem[];
  total: number;
}

// ===== COVERAGE TYPES =====

export interface CoverageMetrics {
  totalSkills: number;
  totalAlignments: number;
  coveredSkills: string[];
  partiallyCoveredSkills: string[];
  uncoveredSkills: string[];
  coverageBySkill: Record<string, number>;
  overallCoverage: number; // 0-1
  alignmentConfidence: number; // 0-1
}

export interface CoverageReportResponse {
  status: 'success' | 'error';
  workflowId: string;
  coverage: CoverageMetrics | null;
  message?: string;
}

// ===== ACCESSIBILITY TYPES =====

export interface AccessibilityFinding {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  remediation: string;
  wcagCriteria?: string;
}

export interface AccessibilityAuditResponse {
  status: 'success' | 'error';
  workflowId: string;
  audit: {
    id: string;
    scope: string;
    totalFindings: number;
    criticalIssues: number;
    highIssues: number;
    mediumIssues: number;
    lowIssues: number;
    findings: AccessibilityFinding[];
    remediationComplete: boolean;
    status: 'in_progress' | 'completed';
  } | null;
}

// ===== WORKFLOW STATUS TYPES =====

export interface WorkflowPhase {
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  completedAt?: string;
}

export interface WorkflowProgressState {
  phases: WorkflowPhase[];
  currentPhase: string;
  progressPercent: number;
  nextAction: string;
}

// ===== APPROVAL WORKFLOW TYPES =====

export interface ApprovalRequest {
  alignmentIds?: string[];
  recommendationIds?: string[];
  approvalNotes: string;
}

export interface ApprovalResponse {
  status: 'success' | 'error';
  message: string;
  approvedCount: number;
}

// ===== REPORT TYPES =====

export interface WorkflowReport {
  workflowId: string;
  programName: string;
  generatedAt: string;
  coverage: CoverageMetrics;
  gaps: GapItem[];
  recommendations: RecommendationItem[];
  accessibility: AccessibilityAuditResponse;
}

export interface ReportGenerationRequest {
  format: 'pdf' | 'docx' | 'html';
  includeEvidence: boolean;
  includeCoverageChart: boolean;
  includeRecommendations: boolean;
  includeAccessibility: boolean;
}

export interface ReportGenerationResponse {
  status: 'success' | 'error';
  reportUrl?: string;
  message?: string;
}

// ===== UI STATE TYPES =====

export interface FilterState {
  alignmentStatus?: 'candidate' | 'approved' | 'rejected';
  recommendationPriority?: 'critical' | 'high' | 'medium' | 'low';
  gapSeverity?: 'critical' | 'high' | 'medium' | 'low';
  searchQuery?: string;
}

export interface SortState {
  field: 'confidence' | 'priority' | 'severity' | 'created' | 'updated';
  order: 'asc' | 'desc';
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

// ===== NOTIFICATION TYPES =====

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number; // milliseconds
}
