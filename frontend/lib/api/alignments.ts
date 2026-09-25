import { useQuery, useMutation, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface Alignment {
  id: string
  tenant_id: string
  source_type: string
  source_id: string
  target_type: string
  standard_id?: string
  objective_id?: string
  score: number
  confidence: number
  evidence: string[]
  status: 'candidate' | 'approved' | 'rejected' | 'pending_review'
  reviewed_by?: string
  reviewed_at?: string
  created_at: string
  updated_at: string
}

export interface AlignmentEvidence {
  text: string
  source: string
  page?: number
  timestamp?: string
  confidence: number
}

export interface AlignmentDetail extends Alignment {
  evidence_details: AlignmentEvidence[]
  rationale: string
}

// Fetch alignments
export const useAlignments = (
  sourceType?: string,
  sourceId?: string
): UseQueryResult<Alignment[], Error> => {
  return useQuery(
    ['alignments', sourceType, sourceId],
    async () => {
      const params = new URLSearchParams()
      if (sourceType) params.append('source_type', sourceType)
      if (sourceId) params.append('source_id', sourceId)

      const response = await apiClient.get<{ alignments: Alignment[] }>(
        `/api/v1/alignments?${params.toString()}`
      )
      return Array.isArray(response.data) ? response.data : response.data.alignments || []
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch alignment detail with evidence
export const useAlignmentDetail = (
  alignmentId: string
): UseQueryResult<AlignmentDetail, Error> => {
  return useQuery(
    ['alignment', alignmentId],
    async () => {
      const response = await apiClient.get<AlignmentDetail>(`/api/v1/alignments/${alignmentId}`)
      return response.data
    },
    {
      enabled: !!alignmentId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch alignments for a standard
export const useAlignmentsForStandard = (
  standardId: string
): UseQueryResult<Alignment[], Error> => {
  return useQuery(
    ['alignments-for-standard', standardId],
    async () => {
      const response = await apiClient.get<Alignment[]>(
        `/api/v1/standards/${standardId}/alignments`
      )
      return response.data
    },
    {
      enabled: !!standardId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch candidate alignments for content
export const useCandidateAlignments = (
  contentId: string,
  frameworkId?: string
): UseQueryResult<Alignment[], Error> => {
  return useQuery(
    ['candidate-alignments', contentId, frameworkId],
    async () => {
      const params = new URLSearchParams()
      params.append('source_type', 'content')
      params.append('source_id', contentId)
      params.append('status', 'candidate')
      if (frameworkId) params.append('framework_id', frameworkId)

      const response = await apiClient.get<Alignment[]>(
        `/api/v1/alignments?${params.toString()}`
      )
      return response.data
    },
    {
      enabled: !!contentId,
      staleTime: 2 * 60 * 1000, // 2 minutes for candidates
    }
  )
}

// Calculate alignment coverage
export const useAlignmentCoverage = (
  curriculumId: string,
  frameworkId?: string
): UseQueryResult<any, Error> => {
  return useQuery(
    ['alignment-coverage', curriculumId, frameworkId],
    async () => {
      const params = new URLSearchParams()
      if (frameworkId) params.append('framework_id', frameworkId)

      const response = await apiClient.get<any>(
        `/api/v1/alignments/coverage/${curriculumId}?${params.toString()}`
      )
      return response.data
    },
    {
      enabled: !!curriculumId,
      staleTime: 10 * 60 * 1000,
    }
  )
}

// Mutation: Create alignment
export const useCreateAlignment = (): UseMutationResult<
  Alignment,
  Error,
  Omit<Alignment, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<Alignment>('/api/v1/alignments', data)
    return response.data
  })
}

// Mutation: Update alignment status
export const useUpdateAlignmentStatus = (): UseMutationResult<
  Alignment,
  Error,
  { id: string; status: string; notes?: string },
  unknown
> => {
  return useMutation(async ({ id, status, notes }) => {
    const response = await apiClient.put<Alignment>(`/api/v1/alignments/${id}`, {
      status,
      notes,
    })
    return response.data
  })
}

// Mutation: Review alignment (approve/reject/defer)
export const useReviewAlignment = (): UseMutationResult<
  Alignment,
  Error,
  { id: string; decision: 'approved' | 'rejected' | 'deferred'; comments?: string },
  unknown
> => {
  return useMutation(async ({ id, decision, comments }) => {
    const response = await apiClient.post<Alignment>(`/api/v1/alignments/${id}/review`, {
      decision,
      comments,
    })
    return response.data
  })
}

// Mutation: Approve alignment
export const useApproveAlignment = (): UseMutationResult<
  Alignment,
  Error,
  { id: string; edits?: Record<string, any> },
  unknown
> => {
  return useMutation(async ({ id, edits }) => {
    const response = await apiClient.post<Alignment>(`/api/v1/alignments/${id}/approve`, {
      edits,
    })
    return response.data
  })
}

// Mutation: Reject alignment
export const useRejectAlignment = (): UseMutationResult<
  Alignment,
  Error,
  { id: string; reason: string },
  unknown
> => {
  return useMutation(async ({ id, reason }) => {
    const response = await apiClient.post<Alignment>(`/api/v1/alignments/${id}/reject`, {
      reason,
    })
    return response.data
  })
}
