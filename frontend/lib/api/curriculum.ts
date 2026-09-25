import { useQuery, useMutation, UseQueryResult, UseMutationResult } from 'react-query'
import { apiClient } from './client'

export interface Curriculum {
  id: string
  tenant_id: string
  name: string
  description: string
  version: string
  grade?: string
  subject?: string
  status: 'draft' | 'published' | 'archived'
  created_at: string
  updated_at: string
}

export interface CurriculumUnit {
  id: string
  tenant_id: string
  curriculum_id: string
  parent_id?: string
  title: string
  description?: string
  sequence: number
  created_at: string
  updated_at: string
}

export interface LearningObjective {
  id: string
  tenant_id: string
  unit_id: string
  objective: string
  cognitive_level?: string
  created_at: string
  updated_at: string
}

export interface CurriculumStructure {
  curriculum: Curriculum
  units: CurriculumUnit[]
  objectives: LearningObjective[]
}

// Fetch all curricula
export const useCurricula = (): UseQueryResult<Curriculum[], Error> => {
  return useQuery(
    ['curricula'],
    async () => {
      const response = await apiClient.get<Curriculum[]>('/api/v1/curricula')
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch curriculum detail
export const useCurriculum = (curriculumId: string): UseQueryResult<Curriculum, Error> => {
  return useQuery(
    ['curriculum', curriculumId],
    async () => {
      const response = await apiClient.get<Curriculum>(`/api/v1/curricula/${curriculumId}`)
      return response.data
    },
    {
      enabled: !!curriculumId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch curriculum structure
export const useCurriculumStructure = (
  curriculumId: string
): UseQueryResult<CurriculumStructure, Error> => {
  return useQuery(
    ['curriculum-structure', curriculumId],
    async () => {
      const response = await apiClient.get<CurriculumStructure>(
        `/api/v1/curricula/${curriculumId}/structure`
      )
      return response.data
    },
    {
      enabled: !!curriculumId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch curriculum units
export const useCurriculumUnits = (
  curriculumId: string
): UseQueryResult<CurriculumUnit[], Error> => {
  return useQuery(
    ['curriculum-units', curriculumId],
    async () => {
      const response = await apiClient.get<CurriculumUnit[]>(
        `/api/v1/curricula/${curriculumId}/units`
      )
      return response.data
    },
    {
      enabled: !!curriculumId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch learning objectives for a unit
export const useUnitObjectives = (
  unitId: string
): UseQueryResult<LearningObjective[], Error> => {
  return useQuery(
    ['unit-objectives', unitId],
    async () => {
      const response = await apiClient.get<LearningObjective[]>(
        `/api/v1/curriculum-units/${unitId}/objectives`
      )
      return response.data
    },
    {
      enabled: !!unitId,
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Fetch all learning objectives
export const useLearningObjectives = (): UseQueryResult<LearningObjective[], Error> => {
  return useQuery(
    ['learning-objectives'],
    async () => {
      const response = await apiClient.get<LearningObjective[]>('/api/v1/learning-objectives')
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

// Analyze curriculum coverage
export const useCurriculumCoverage = (
  curriculumId: string,
  frameworkId?: string
): UseQueryResult<any, Error> => {
  return useQuery(
    ['curriculum-coverage', curriculumId, frameworkId],
    async () => {
      const params = new URLSearchParams()
      if (frameworkId) params.append('framework_id', frameworkId)

      const response = await apiClient.get<any>(
        `/api/v1/curricula/${curriculumId}/coverage?${params.toString()}`
      )
      return response.data
    },
    {
      enabled: !!curriculumId,
      staleTime: 10 * 60 * 1000,
    }
  )
}

// Mutation: Create curriculum
export const useCreateCurriculum = (): UseMutationResult<
  Curriculum,
  Error,
  Omit<Curriculum, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<Curriculum>('/api/v1/curricula', data)
    return response.data
  })
}

// Mutation: Create curriculum unit
export const useCreateCurriculumUnit = (): UseMutationResult<
  CurriculumUnit,
  Error,
  Omit<CurriculumUnit, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<CurriculumUnit>('/api/v1/curriculum-units', data)
    return response.data
  })
}

// Mutation: Create learning objective
export const useCreateObjective = (): UseMutationResult<
  LearningObjective,
  Error,
  Omit<LearningObjective, 'id' | 'tenant_id' | 'created_at' | 'updated_at'>,
  unknown
> => {
  return useMutation(async (data) => {
    const response = await apiClient.post<LearningObjective>(
      '/api/v1/learning-objectives',
      data
    )
    return response.data
  })
}
