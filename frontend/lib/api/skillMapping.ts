/**
 * Skill Mapping & Recommendations API Hooks
 *
 * React Query hooks for fetching and managing skill alignments,
 * recommendations, gap analysis, and coverage reports.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { API_BASE_URL } from './config';
import type {
  SkillAlignmentListResponse,
  SkillAlignmentItem,
  RecommendationListResponse,
  RecommendationItem,
  GapAnalysisListResponse,
  GapItem,
  CoverageReportResponse,
  AccessibilityAuditResponse,
  ApprovalRequest,
  ApprovalResponse,
} from '../types/phase5';

// ===== SKILL ALIGNMENT QUERIES =====

export function useSkillAlignments(workflowId: string, status?: string) {
  return useQuery({
    queryKey: ['alignments', workflowId, status],
    queryFn: async () => {
      const url = new URL(`${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/alignments`);
      if (status) url.searchParams.append('status', status);

      const response = await fetch(url.toString());
      if (!response.ok) throw new Error('Failed to fetch alignments');
      return response.json() as Promise<SkillAlignmentListResponse>;
    },
    enabled: !!workflowId,
  });
}

export function useApproveAlignment(workflowId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ alignmentId, notes }: { alignmentId: string; notes?: string }) => {
      const response = await fetch(
        `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/alignments/${alignmentId}/approve`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ approval_notes: notes }),
        }
      );
      if (!response.ok) throw new Error('Failed to approve alignment');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alignments', workflowId] });
    },
  });
}

// ===== RECOMMENDATION QUERIES =====

export function useRecommendations(
  workflowId: string,
  priority?: string,
  status?: string
) {
  return useQuery({
    queryKey: ['recommendations', workflowId, priority, status],
    queryFn: async () => {
      const url = new URL(`${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/recommendations`);
      if (priority) url.searchParams.append('priority', priority);
      if (status) url.searchParams.append('status_filter', status);

      const response = await fetch(url.toString());
      if (!response.ok) throw new Error('Failed to fetch recommendations');
      return response.json() as Promise<RecommendationListResponse>;
    },
    enabled: !!workflowId,
  });
}

export function useApproveRecommendation(workflowId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ recommendationId, notes }: { recommendationId: string; notes?: string }) => {
      const response = await fetch(
        `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/recommendations/${recommendationId}/approve`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ approval_notes: notes }),
        }
      );
      if (!response.ok) throw new Error('Failed to approve recommendation');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', workflowId] });
    },
  });
}

export function useUpdateRecommendation(workflowId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      recommendationId,
      status,
      notes,
    }: {
      recommendationId: string;
      status?: string;
      notes?: string;
    }) => {
      const response = await fetch(
        `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/recommendations/${recommendationId}`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            status,
            implementation_notes: notes,
          }),
        }
      );
      if (!response.ok) throw new Error('Failed to update recommendation');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', workflowId] });
    },
  });
}

// ===== GAP ANALYSIS QUERIES =====

export function useGapAnalysis(workflowId: string, severity?: string) {
  return useQuery({
    queryKey: ['gaps', workflowId, severity],
    queryFn: async () => {
      const url = new URL(`${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/gaps`);
      if (severity) url.searchParams.append('severity', severity);

      const response = await fetch(url.toString());
      if (!response.ok) throw new Error('Failed to fetch gaps');
      return response.json() as Promise<GapAnalysisListResponse>;
    },
    enabled: !!workflowId,
  });
}

// ===== COVERAGE REPORT QUERIES =====

export function useCoverageReport(workflowId: string) {
  return useQuery({
    queryKey: ['coverage', workflowId],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/coverage`
      );
      if (!response.ok) throw new Error('Failed to fetch coverage report');
      return response.json() as Promise<CoverageReportResponse>;
    },
    enabled: !!workflowId,
  });
}

// ===== ACCESSIBILITY AUDIT QUERIES =====

export function useAccessibilityAudit(workflowId: string) {
  return useQuery({
    queryKey: ['accessibility', workflowId],
    queryFn: async () => {
      const response = await fetch(
        `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/accessibility`
      );
      if (!response.ok) throw new Error('Failed to fetch accessibility audit');
      return response.json() as Promise<AccessibilityAuditResponse>;
    },
    enabled: !!workflowId,
  });
}

// ===== BATCH APPROVAL MUTATIONS =====

export function useBatchApproveAlignments(workflowId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (alignmentIds: string[]) => {
      const results = await Promise.all(
        alignmentIds.map(id =>
          fetch(
            `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/alignments/${id}/approve`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({}),
            }
          )
        )
      );

      if (results.some(r => !r.ok)) {
        throw new Error('Some approvals failed');
      }

      return results;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alignments', workflowId] });
    },
  });
}

export function useBatchApproveRecommendations(workflowId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (recommendationIds: string[]) => {
      const results = await Promise.all(
        recommendationIds.map(id =>
          fetch(
            `${API_BASE_URL}/v1/skill-mapping/workflows/${workflowId}/recommendations/${id}/approve`,
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({}),
            }
          )
        )
      );

      if (results.some(r => !r.ok)) {
        throw new Error('Some approvals failed');
      }

      return results;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', workflowId] });
    },
  });
}
