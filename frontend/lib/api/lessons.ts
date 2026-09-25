import { useQuery, useMutation, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface Lesson {
  id: string
  tenant_id: string
  curriculum_id: string
  title: string
  description?: string
  duration_minutes?: number
  grade?: string
  subject?: string
  status: 'draft' | 'review' | 'published' | 'archived'
  model?: string
  model_version?: string
  prompt_version?: string
  content?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Activity {
  id: string
  tenant_id: string
  lesson_id: string
  type: string
  title: string
  instructions?: string
  duration_minutes?: number
  differentiation?: Record<string, any>
  status: 'draft' | 'published'
  created_at: string
  updated_at: string
}

export interface LessonStructure {
  lesson: Lesson
  activities: Activity[]
  sections: {
    id: string
    type: string
    title: string
    content: string
  }[]
}

// Fetch lessons
export const useLessons = (curriculumId?: string): UseQueryResult<Lesson[], Error> => {
  return useQuery(
    ['lessons', curriculumId],
    async () => {
      const params = new URLSearchParams()
      if (curriculumId) params.append('curriculum_id', curriculumId)

      const response = await apiClient.get<Lesson[]>(`/api/v1/lessons?${params.toString()}`)
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch lesson detail
export const useLesson = (lessonId: string): UseQueryResult<LessonStructure, Error> => {
  return useQuery(
    ['lesson', lessonId],
    async () => {
      const response = await apiClient.get<LessonStructure>(`/api/v1/lessons/${lessonId}`)
      return response.data
    },
    {
      enabled: !!lessonId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch lesson activities
export const useLessonActivities = (lessonId: string): UseQueryResult<Activity[], Error> => {
  return useQuery(
    ['lesson-activities', lessonId],
    async () => {
      const response = await apiClient.get<Activity[]>(`/api/v1/lessons/${lessonId}/activities`)
      return response.data
    },
    {
      enabled: !!lessonId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Mutation: Create lesson
export const useCreateLesson = (): UseMutationResult<
  Lesson,
  Error,
  Omit<Lesson, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<Lesson>('/api/v1/lessons', data)
    return response.data
  })
}

// Mutation: Update lesson
export const useUpdateLesson = (): UseMutationResult<
  Lesson,
  Error,
  { id: string; data: Partial<Lesson> },
  unknown
> => {
  return useMutation(async ({ id, data }) => {
    const response = await apiClient.put<Lesson>(`/api/v1/lessons/${id}`, data)
    return response.data
  })
}

// Mutation: Add activity to lesson
export const useAddActivity = (): UseMutationResult<
  Activity,
  Error,
  Omit<Activity, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<Activity>('/api/v1/activities', data)
    return response.data
  })
}

// Mutation: Update activity
export const useUpdateActivity = (): UseMutationResult<
  Activity,
  Error,
  { id: string; data: Partial<Activity> },
  unknown
> => {
  return useMutation(async ({ id, data }) => {
    const response = await apiClient.put<Activity>(`/api/v1/activities/${id}`, data)
    return response.data
  })
}

// Mutation: Publish lesson
export const usePublishLesson = (): UseMutationResult<
  Lesson,
  Error,
  { id: string },
  unknown
> => {
  return useMutation(async ({ id }) => {
    const response = await apiClient.post<Lesson>(`/api/v1/lessons/${id}/publish`, {})
    return response.data
  })
}

// Mutation: Regenerate lesson section
export const useRegenerateSection = (): UseMutationResult<
  Lesson,
  Error,
  { id: string; section: string; context?: Record<string, any> },
  unknown
> => {
  return useMutation(async ({ id, section, context }) => {
    const response = await apiClient.post<Lesson>(
      `/api/v1/lessons/${id}/regenerate-section`,
      {
        section,
        context,
      }
    )
    return response.data
  })
}

// Mutation: Delete lesson
export const useDeleteLesson = (): UseMutationResult<void, Error, { id: string }, unknown> => {
  return useMutation(async ({ id }) => {
    await apiClient.delete(`/api/v1/lessons/${id}`)
  })
}
