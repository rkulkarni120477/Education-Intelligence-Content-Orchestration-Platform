import { useQuery, useMutation, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface Assessment {
  id: string
  tenant_id: string
  title: string
  assessment_type: string
  description?: string
  status: 'draft' | 'review' | 'published' | 'archived'
  model?: string
  model_version?: string
  prompt_version?: string
  blueprint?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface AssessmentItem {
  id: string
  tenant_id: string
  assessment_id: string
  type: string
  question: string
  answer_key?: Record<string, any>
  distractors?: string[]
  rationale?: string
  cognitive_level?: string
  sequence: number
  created_at: string
  updated_at: string
}

export interface AssessmentDetail {
  assessment: Assessment
  items: AssessmentItem[]
  validationIssues?: {
    type: string
    message: string
    itemId?: string
  }[]
}

// Fetch assessments
export const useAssessments = (status?: string): UseQueryResult<Assessment[], Error> => {
  return useQuery(
    ['assessments', status],
    async () => {
      const params = new URLSearchParams()
      if (status) params.append('status', status)

      const response = await apiClient.get<Assessment[]>(
        `/api/v1/assessments?${params.toString()}`
      )
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch assessment detail with items
export const useAssessment = (assessmentId: string): UseQueryResult<AssessmentDetail, Error> => {
  return useQuery(
    ['assessment', assessmentId],
    async () => {
      const response = await apiClient.get<AssessmentDetail>(`/api/v1/assessments/${assessmentId}`)
      return response.data
    },
    {
      enabled: !!assessmentId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch assessment items
export const useAssessmentItems = (
  assessmentId: string
): UseQueryResult<AssessmentItem[], Error> => {
  return useQuery(
    ['assessment-items', assessmentId],
    async () => {
      const response = await apiClient.get<AssessmentItem[]>(
        `/api/v1/assessments/${assessmentId}/items`
      )
      return response.data
    },
    {
      enabled: !!assessmentId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Validate assessment
export const useValidateAssessment = (): UseMutationResult<
  { valid: boolean; issues: any[] },
  Error,
  { id: string },
  unknown
> => {
  return useMutation(async ({ id }) => {
    const response = await apiClient.post<{ valid: boolean; issues: any[] }>(
      `/api/v1/assessments/${id}/validate`,
      {}
    )
    return response.data
  })
}

// Mutation: Create assessment
export const useCreateAssessment = (): UseMutationResult<
  Assessment,
  Error,
  Omit<Assessment, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<Assessment>('/api/v1/assessments', data)
    return response.data
  })
}

// Mutation: Update assessment
export const useUpdateAssessment = (): UseMutationResult<
  Assessment,
  Error,
  { id: string; data: Partial<Assessment> },
  unknown
> => {
  return useMutation(async ({ id, data }) => {
    const response = await apiClient.put<Assessment>(`/api/v1/assessments/${id}`, data)
    return response.data
  })
}

// Mutation: Add assessment item
export const useAddAssessmentItem = (): UseMutationResult<
  AssessmentItem,
  Error,
  Omit<AssessmentItem, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<AssessmentItem>('/api/v1/assessment-items', data)
    return response.data
  })
}

// Mutation: Update assessment item
export const useUpdateAssessmentItem = (): UseMutationResult<
  AssessmentItem,
  Error,
  { id: string; data: Partial<AssessmentItem> },
  unknown
> => {
  return useMutation(async ({ id, data }) => {
    const response = await apiClient.put<AssessmentItem>(`/api/v1/assessment-items/${id}`, data)
    return response.data
  })
}

// Mutation: Delete assessment item
export const useDeleteAssessmentItem = (): UseMutationResult<
  void,
  Error,
  { id: string },
  unknown
> => {
  return useMutation(async ({ id }) => {
    await apiClient.delete(`/api/v1/assessment-items/${id}`)
  })
}

// Mutation: Publish assessment
export const usePublishAssessment = (): UseMutationResult<
  Assessment,
  Error,
  { id: string },
  unknown
> => {
  return useMutation(async ({ id }) => {
    const response = await apiClient.post<Assessment>(`/api/v1/assessments/${id}/publish`, {})
    return response.data
  })
}
