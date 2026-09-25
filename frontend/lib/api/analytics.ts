import { useQuery } from '@tanstack/react-query'
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

export const useDashboardAnalytics = (period: string = 'week') => {
  return useQuery({
    queryKey: ['analytics', 'dashboard', period],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/analytics/dashboard', {
        params: { period }
      })
      return data.data as AnalyticsDashboard
    },
  })
}

export const useAlignmentAnalytics = (subject?: string, grade?: string) => {
  return useQuery({
    queryKey: ['analytics', 'alignments', subject, grade],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/analytics/alignments', {
        params: { subject, grade }
      })
      return data.analytics as AlignmentAnalytics
    },
  })
}

export const useCoverageAnalytics = () => {
  return useQuery({
    queryKey: ['analytics', 'coverage'],
    queryFn: async () => {
      const { data } = await apiClient.get('/v1/analytics/coverage')
      return data.coverage as CoverageAnalytics
    },
  })
}
