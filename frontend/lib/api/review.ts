import { useQuery, useMutation, useQueryClient, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface ReviewItem {
  id: string
  type: 'lesson' | 'assessment' | 'activity' | 'content'
  title: string
  creator: {
    id: string
    name: string
    email: string
  }
  submittedAt: string
  status: 'pending' | 'approved' | 'rejected' | 'revision'
  priority: 'low' | 'medium' | 'high'
  summary?: string
  metadata?: Record<string, any>
}

export interface ReviewDecision {
  status: 'approved' | 'rejected' | 'revision'
  notes: string
  requiredChanges?: string[]
}

export const useReviewQueue = (status?: string): UseQueryResult<ReviewItem[], Error> => {
  return useQuery(['reviews', status], async () => {
    const params = new URLSearchParams()
    if (status) params.append('status', status)

    const response = await apiClient.get<{ items: ReviewItem[] }>(
      `/api/v1/reviews?${params.toString()}`
    )
    return response.data.items
  })
}

export const useReviewItem = (
  itemId: string
): UseQueryResult<
  ReviewItem & { content: string; preview?: string; metrics?: Record<string, any> },
  Error
> => {
  return useQuery(
    ['reviews', itemId],
    async () => {
      const response = await apiClient.get<{
        item: ReviewItem & { content: string; preview?: string; metrics?: Record<string, any> }
      }>(`/api/v1/reviews/${itemId}`)
      return response.data.item
    },
    {
      enabled: !!itemId,
    }
  )
}

export const useApproveReview = (): UseMutationResult<
  any,
  Error,
  { itemId: string; notes?: string },
  unknown
> => {
  const queryClient = useQueryClient()

  return useMutation(
    async ({ itemId, notes }) => {
      const response = await apiClient.post(`/api/v1/reviews/${itemId}/approve`, { notes })
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['reviews'])
      },
    }
  )
}

export const useRejectReview = (): UseMutationResult<
  any,
  Error,
  { itemId: string; reason?: string; notes?: string },
  unknown
> => {
  const queryClient = useQueryClient()

  return useMutation(
    async ({ itemId, reason, notes }) => {
      const response = await apiClient.post(`/api/v1/reviews/${itemId}/reject`, {
        reason,
        notes,
      })
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['reviews'])
      },
    }
  )
}

export const useRequestRevision = (): UseMutationResult<
  any,
  Error,
  { itemId: string; changes: string[]; notes?: string },
  unknown
> => {
  const queryClient = useQueryClient()

  return useMutation(
    async ({ itemId, changes, notes }) => {
      const response = await apiClient.post(`/api/v1/reviews/${itemId}/revision`, {
        required_changes: changes,
        notes,
      })
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['reviews'])
      },
    }
  )
}

export const useReviewStats = (): UseQueryResult<any, Error> => {
  return useQuery(['reviews', 'stats'], async () => {
    const response = await apiClient.get<{ stats: any }>('/api/v1/reviews/stats')
    return response.data.stats
  })
}
