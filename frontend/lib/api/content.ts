import { useQuery, useMutation, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface ContentAsset {
  id: string
  tenant_id: string
  title: string
  description?: string
  content_type: string
  source_url?: string
  file_path?: string
  file_size?: number
  mime_type?: string
  grade?: string
  subject?: string
  tags?: string[]
  status: 'uploaded' | 'processing' | 'extracted' | 'review_required' | 'published' | 'failed'
  upload_progress?: number
  extracted_text?: string
  metadata?: Record<string, any>
  version: number
  created_at: string
  updated_at: string
  created_by?: string
}

export interface IngestionJob {
  id: string
  tenant_id: string
  content_id: string
  status: 'queued' | 'scanning' | 'extracting' | 'enriching' | 'review_required' | 'completed' | 'failed'
  progress: number
  stage: string
  error?: string
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface ProcessingJob {
  id: string
  tenant_id: string
  content_id: string
  job_type: string
  status: 'processing' | 'completed' | 'failed'
  progress: number
  created_at: string
  updated_at: string
}

// Fetch content assets
export const useContentAssets = (
  page: number = 1,
  limit: number = 20,
  filters?: { status?: string; subject?: string; grade?: string; tags?: string[] }
): UseQueryResult<{ items: ContentAsset[]; total: number; pages: number }, Error> => {
  return useQuery(
    ['content-assets', page, limit, filters],
    async () => {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('limit', limit.toString())

      if (filters?.status) params.append('status', filters.status)
      if (filters?.subject) params.append('subject', filters.subject)
      if (filters?.grade) params.append('grade', filters.grade)
      if (filters?.tags?.length) params.append('tags', filters.tags.join(','))

      const response = await apiClient.get<any>(`/api/v1/content?${params.toString()}`)
      const data = response.data
      return {
        items: data.items || data.content || [],
        total: data.total ?? 0,
        pages: data.pages ?? Math.ceil((data.total ?? 0) / limit),
      }
    },
    {
      staleTime: 2 * 60 * 1000, // 2 minutes (content can change)
    }
  )
}

// Search content
export const useSearchContent = (
  query: string
): UseQueryResult<ContentAsset[], Error> => {
  return useQuery(
    ['content-search', query],
    async () => {
      const response = await apiClient.get<ContentAsset[]>(
        `/api/v1/content/search?q=${encodeURIComponent(query)}`
      )
      return response.data
    },
    {
      enabled: !!query,
      staleTime: 1 * 60 * 1000,
    }
  )
}

// Fetch single content asset
export const useContentAsset = (contentId: string): UseQueryResult<ContentAsset, Error> => {
  return useQuery(
    ['content', contentId],
    async () => {
      const response = await apiClient.get<ContentAsset>(`/api/v1/content/${contentId}`)
      return response.data
    },
    {
      enabled: !!contentId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch ingestion job status
export const useIngestionJob = (jobId: string): UseQueryResult<IngestionJob, Error> => {
  return useQuery(
    ['ingestion-job', jobId],
    async () => {
      const response = await apiClient.get<IngestionJob>(`/api/v1/content/ingestion/${jobId}`)
      return response.data
    },
    {
      enabled: !!jobId,
      refetchInterval: 2000, // Poll every 2 seconds while processing
      staleTime: 0, // Always refetch
    }
  )
}

// Fetch processing jobs
export const useProcessingJobs = (): UseQueryResult<ProcessingJob[], Error> => {
  return useQuery(
    ['processing-jobs'],
    async () => {
      const response = await apiClient.get<any>('/api/v1/content/jobs?status=processing')
      const data = response.data
      return Array.isArray(data) ? data : data.jobs || []
    },
    {
      refetchInterval: 3000, // Poll every 3 seconds
      staleTime: 0,
    }
  )
}

// Mutation: Upload content
export const useUploadContent = (): UseMutationResult<
  IngestionJob,
  Error,
  {
    file: File
    title: string
    description?: string
    subject?: string
    grade?: string
    tags?: string[]
  },
  unknown
> => {
  return useMutation(async ({ file, title, description, subject, grade, tags }) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    if (description) formData.append('description', description)
    if (subject) formData.append('subject', subject)
    if (grade) formData.append('grade', grade)
    if (tags?.length) formData.append('tags', JSON.stringify(tags))

    const response = await apiClient.post<IngestionJob>('/api/v1/content/upload', formData)
    return response.data
  })
}

// Mutation: Update content asset
export const useUpdateContent = (): UseMutationResult<
  ContentAsset,
  Error,
  { id: string; data: Partial<ContentAsset> },
  unknown
> => {
  return useMutation(async ({ id, data }) => {
    const response = await apiClient.put<ContentAsset>(`/api/v1/content/${id}`, data)
    return response.data
  })
}

// Mutation: Approve content for use
export const useApproveContent = (): UseMutationResult<
  ContentAsset,
  Error,
  { id: string; notes?: string },
  unknown
> => {
  return useMutation(async ({ id, notes }) => {
    const response = await apiClient.post<ContentAsset>(`/api/v1/content/${id}/approve`, {
      notes,
    })
    return response.data
  })
}

// Mutation: Reject content
export const useRejectContent = (): UseMutationResult<
  ContentAsset,
  Error,
  { id: string; reason: string },
  unknown
> => {
  return useMutation(async ({ id, reason }) => {
    const response = await apiClient.post<ContentAsset>(`/api/v1/content/${id}/reject`, {
      reason,
    })
    return response.data
  })
}

// Mutation: Delete content
export const useDeleteContent = (): UseMutationResult<
  void,
  Error,
  { id: string },
  unknown
> => {
  return useMutation(async ({ id }) => {
    await apiClient.delete(`/api/v1/content/${id}`)
  })
}

// Mutation: Retry failed ingestion
export const useRetryIngestion = (): UseMutationResult<
  IngestionJob,
  Error,
  { contentId: string },
  unknown
> => {
  return useMutation(async ({ contentId }) => {
    const response = await apiClient.post<IngestionJob>(
      `/api/v1/content/${contentId}/retry-ingestion`,
      {}
    )
    return response.data
  })
}
