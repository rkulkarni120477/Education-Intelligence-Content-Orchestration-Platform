import { useQuery, UseQueryResult } from 'react-query'
import { apiClient } from './client'

export interface AnalyticsDashboard {
  overview: {
    total_content_items: number
    total_alignments: number
    approved_alignments: number
    pending_alignments: number
    rejected_alignments: number
  }
  coverage: {
    fully_aligned: number
    partially_aligned: number
    not_aligned: number
    alignment_percentage: number
  }
  standards: {
    frameworks: number
    standards: number
    covered_standards: number
    coverage_rate: number
  }
  timeline: {
    labels: string[]
    alignments_created: number[]
    alignments_approved: number[]
  }
  quality: {
    avg_confidence_score: number
    high_confidence: number
    medium_confidence: number
    low_confidence: number
  }
  performance: {
    avg_review_time: number
    avg_approval_rate: number
    top_reviewer: string
    reviews_completed: number
  }
}

export interface AlignmentAnalytics {
  by_standard_framework: Array<{
    name: string
    aligned: number
    pending: number
    rejected: number
  }>
  by_content_type: Array<{
    type: string
    count: number
    aligned: number
  }>
  confidence_distribution: Record<string, number>
}

export interface CoverageAnalytics {
  total_standards: number
  covered_standards: number
  coverage_percentage: number
  by_grade: Array<{
    grade: string
    total: number
    covered: number
    coverage: number
  }>
  by_subject: Array<{
    subject: string
    coverage: number
  }>
}

export const useDashboardAnalytics = (
  period: string = 'week'
): UseQueryResult<AnalyticsDashboard, Error> => {
  return useQuery(
    ['analytics', 'dashboard', period],
    async () => {
      const response = await apiClient.get<{ data: AnalyticsDashboard }>(
        `/api/v1/analytics/dashboard?period=${period}`
      )
      return response.data.data
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useAlignmentAnalytics = (
  subject?: string,
  grade?: string
): UseQueryResult<AlignmentAnalytics, Error> => {
  return useQuery(
    ['analytics', 'alignments', subject, grade],
    async () => {
      const params = new URLSearchParams()
      if (subject) params.append('subject', subject)
      if (grade) params.append('grade', grade)

      const response = await apiClient.get<{ analytics: AlignmentAnalytics }>(
        `/api/v1/analytics/alignments?${params.toString()}`
      )
      return response.data.analytics
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}

export const useCoverageAnalytics = (): UseQueryResult<CoverageAnalytics, Error> => {
  return useQuery(
    ['analytics', 'coverage'],
    async () => {
      const response = await apiClient.get<{ coverage: CoverageAnalytics }>(
        '/api/v1/analytics/coverage'
      )
      return response.data.coverage
    },
    {
      staleTime: 5 * 60 * 1000,
    }
  )
}
