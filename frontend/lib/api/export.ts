import { apiClient } from './client'

export interface ExportFormat {
  format: 'csv' | 'pdf' | 'json'
  type: 'alignments' | 'coverage' | 'review' | 'full'
  filters?: {
    status?: string
    framework?: string
    grade?: string
    subject?: string
    dateRange?: {
      start: string
      end: string
    }
  }
}

export interface BulkOperation {
  action: 'approve' | 'reject' | 'defer'
  alignment_ids: string[]
  notes?: string
}

/**
 * Export alignment data in specified format
 */
export const exportAlignmentData = async (options: ExportFormat) => {
  try {
    const response = await apiClient.get('/v1/export/alignments', {
      params: {
        format: options.format,
        ...options.filters
      },
      responseType: options.format === 'pdf' ? 'blob' : 'json'
    })

    if (options.format === 'pdf') {
      // Handle PDF download
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `alignments-${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
    } else if (options.format === 'csv') {
      // Handle CSV download
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `alignments-${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
    } else {
      // Return JSON data
      return response.data
    }
  } catch (error) {
    console.error('Export failed:', error)
    throw error
  }
}

/**
 * Perform bulk operations on alignments
 */
export const performBulkOperation = async (operation: BulkOperation) => {
  try {
    const { data } = await apiClient.post('/v1/alignments/bulk', operation)
    return data
  } catch (error) {
    console.error('Bulk operation failed:', error)
    throw error
  }
}

/**
 * Generate coverage report
 */
export const generateCoverageReport = async (format: 'pdf' | 'csv' = 'pdf') => {
  try {
    const response = await apiClient.get('/v1/export/coverage-report', {
      params: { format },
      responseType: format === 'pdf' ? 'blob' : 'json'
    })

    if (format === 'pdf') {
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `coverage-report-${new Date().toISOString().split('T')[0]}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
    }

    return response.data
  } catch (error) {
    console.error('Report generation failed:', error)
    throw error
  }
}
