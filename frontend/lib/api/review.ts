import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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

export const useReviewQueue = (status?: string) => {
  return useQuery({
    queryKey: ['reviews', status],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/reviews', {
        params: { status }
      })
      return data.items as ReviewItem[]
    },
  })
}

export const useReviewItem = (itemId: string) => {
  return useQuery({
    queryKey: ['reviews', itemId],
    queryFn: async () => {
      const { data } = await apiClient.get(`/v1/reviews/${itemId}`)
      return data.item as ReviewItem & {
        content: string
        preview?: string
        metrics?: Record<string, any>
      }
    },
    enabled: !!itemId,
  })
}

export const useApproveReview = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ itemId, notes }: { itemId: string; notes?: string }) => {
      const { data } = await apiClient.post(`/v1/reviews/${itemId}/approve`, {
        notes
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export const useRejectReview = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      itemId,
      reason,
      notes,
    }: {
      itemId: string
      reason?: string
      notes?: string
    }) => {
      const { data } = await apiClient.post(`/v1/reviews/${itemId}/reject`, {
        reason,
        notes
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export const useRequestRevision = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      itemId,
      changes,
      notes,
    }: {
      itemId: string
      changes: string[]
      notes?: string
    }) => {
      const { data } = await apiClient.post(`/v1/reviews/${itemId}/revision`, {
        required_changes: changes,
        notes
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

export const useReviewStats = () => {
  return useQuery({
    queryKey: ['reviews', 'stats'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/reviews/stats')
      return data.stats
    },
  })
}
