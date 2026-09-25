import { useQuery, useMutation, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface StandardFramework {
  id: string
  name: string
  authority: string
  jurisdiction: string
  version: string
  description: string
  created_at: string
  updated_at: string
}

export interface Standard {
  id: string
  tenant_id: string
  framework_id: string
  parent_id?: string
  code: string
  description: string
  grade?: string
  subject?: string
  domain?: string
  strand?: string
  version: string
  created_at: string
  updated_at: string
}

export interface StandardHierarchy {
  framework: StandardFramework
  standards: Standard[]
  hierarchy: {
    id: string
    code: string
    label: string
    children: any[]
  }[]
}

// Fetch all frameworks
export const useFrameworks = (): UseQueryResult<StandardFramework[], Error> => {
  return useQuery(
    ['frameworks'],
    async () => {
      const response = await apiClient.get<StandardFramework[]>('/api/v1/standards/frameworks')
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 30 * 60 * 1000, // 30 minutes
    }
  )
}

// Fetch standards in a framework
export const useStandards = (frameworkId: string): UseQueryResult<Standard[], Error> => {
  return useQuery(
    ['standards', frameworkId],
    async () => {
      const response = await apiClient.get<Standard[]>(
        `/api/v1/standards/frameworks/${frameworkId}/standards`
      )
      return response.data
    },
    {
      enabled: !!frameworkId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch standard hierarchy
export const useStandardHierarchy = (
  frameworkId: string
): UseQueryResult<StandardHierarchy, Error> => {
  return useQuery(
    ['standard-hierarchy', frameworkId],
    async () => {
      const response = await apiClient.get<StandardHierarchy>(
        `/api/v1/standards/frameworks/${frameworkId}/hierarchy`
      )
      return response.data
    },
    {
      enabled: !!frameworkId,
      staleTime: 10 * 60 * 1000,
    }
  )
}

// Fetch single standard detail
export const useStandard = (standardId: string): UseQueryResult<Standard, Error> => {
  return useQuery(
    ['standard', standardId],
    async () => {
      const response = await apiClient.get<Standard>(`/api/v1/standards/${standardId}`)
      return response.data
    },
    {
      enabled: !!standardId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Search standards
export const useSearchStandards = (
  query: string,
  frameworkId?: string
): UseQueryResult<Standard[], Error> => {
  return useQuery(
    ['standards-search', query, frameworkId],
    async () => {
      const params = new URLSearchParams()
      if (query) params.append('q', query)
      if (frameworkId) params.append('framework_id', frameworkId)

      const response = await apiClient.get<Standard[]>(
        `/api/v1/standards/search?${params.toString()}`
      )
      return response.data
    },
    {
      enabled: !!query,
      staleTime: 1 * 60 * 1000, // 1 minute for search
    }
  )
}

// Get standards by grade and subject
export const useStandardsByGradeSubject = (
  frameworkId: string,
  grade?: string,
  subject?: string
): UseQueryResult<Standard[], Error> => {
  return useQuery(
    ['standards-grade-subject', frameworkId, grade, subject],
    async () => {
      const params = new URLSearchParams()
      if (grade) params.append('grade', grade)
      if (subject) params.append('subject', subject)

      const response = await apiClient.get<Standard[]>(
        `/api/v1/standards/frameworks/${frameworkId}/by-grade-subject?${params.toString()}`
      )
      return response.data
    },
    {
      enabled: !!frameworkId && (!!grade || !!subject),
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Mutation: Create standard framework
export const useCreateFramework = (): UseMutationResult<
  StandardFramework,
  Error,
  Omit<StandardFramework, 'id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<StandardFramework>(
      '/api/v1/standards/frameworks',
      data
    )
    return response.data
  })
}

// Mutation: Create standard
export const useCreateStandard = (): UseMutationResult<
  Standard,
  Error,
  Omit<Standard, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<Standard>('/api/v1/standards', data)
    return response.data
  })
}
