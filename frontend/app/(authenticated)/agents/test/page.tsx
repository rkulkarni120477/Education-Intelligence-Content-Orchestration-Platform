'use client'

import React, { useState, useEffect } from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'

interface TestResult {
  agent_id: string
  agent_name: string
  agent_type: string
  status: string
  passed: boolean
  error_message: string | null
  duration_ms?: number
  details?: Record<string, any>
}

export default function AgentTestPage() {
  const { isAuthenticated } = useAuthRequired()
  const [results, setResults] = useState<TestResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState({
    total: 0,
    passed: 0,
    failed: 0,
  })

  useEffect(() => {
    if (!isAuthenticated) return

    const runTests = async () => {
      try {
        setLoading(true)
        const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/agents/tests/run-all`
        const token = localStorage.getItem('token') || ''

        console.log('Fetching tests from:', apiUrl)
        console.log('Token available:', !!token)

        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        })

        console.log('Response status:', response.status)
        const contentType = response.headers.get('content-type')
        console.log('Response content-type:', contentType)

        if (!response.ok) {
          const errorText = await response.text()
          console.error('API Error Response:', errorText)
          throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 200)}`)
        }

        const data = await response.json()
        console.log('Test results received:', data)

        setResults(data.results || [])
        setSummary({
          total: data.total_tests || 0,
          passed: data.passed || 0,
          failed: data.failed || 0,
        })
      } catch (error) {
        console.error('Test execution failed:', error)
        const errorMsg = error instanceof Error ? error.message : 'Unknown error occurred'
        setError(errorMsg)
        setResults([])
        setSummary({
          total: 0,
          passed: 0,
          failed: 0,
        })
      } finally {
        setLoading(false)
      }
    }

    runTests()
  }, [isAuthenticated])

  const getStatusColor = (passed: boolean) => {
    return passed ? '#10b981' : '#ef4444'
  }

  const getStatusIcon = (passed: boolean) => {
    return passed ? '✓' : '✗'
  }

  const handleClose = () => {
    window.close()
  }

  if (!isAuthenticated) return null

  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', backgroundColor: '#f9fafb', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#1e40af', color: 'white', padding: '2rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '2rem', fontWeight: 'bold' }}>
          Agent Diagnostic Tests
        </h1>
        <p style={{ margin: 0, opacity: 0.9 }}>
          Running comprehensive tests on all 13 workflow agents
        </p>
      </div>

      {/* Main Content */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem' }}>
        {/* Summary Card */}
        <div
          style={{
            backgroundColor: 'white',
            borderRadius: '0.5rem',
            padding: '1.5rem',
            marginBottom: '2rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          }}
        >
          <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', fontWeight: '600' }}>
            Test Summary
          </h2>

          {loading ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div
                style={{
                  display: 'inline-block',
                  width: '40px',
                  height: '40px',
                  border: '4px solid #e5e7eb',
                  borderTop: '4px solid #1e40af',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                }}
              />
              <p style={{ marginTop: '1rem', color: '#6b7280' }}>Running all tests...</p>
              <style>{`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              `}</style>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              <div style={{ padding: '1rem', backgroundColor: '#f0fdf4', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#1e40af' }}>
                  {summary.total}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Total Tests</div>
              </div>
              <div style={{ padding: '1rem', backgroundColor: '#f0fdf4', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
                  {summary.passed}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Passed</div>
              </div>
              <div style={{ padding: '1rem', backgroundColor: '#fef2f2', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ef4444' }}>
                  {summary.failed}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Failed</div>
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div
            style={{
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '0.5rem',
              padding: '1.5rem',
              marginBottom: '2rem',
            }}
          >
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#dc2626', fontWeight: '600' }}>
              Error Running Tests
            </h3>
            <p style={{ margin: 0, color: '#991b1b', fontSize: '0.875rem' }}>
              {error}
            </p>
          </div>
        )}

        {/* Test Results */}
        {!loading && results.length > 0 && (
          <div
            style={{
              backgroundColor: 'white',
              borderRadius: '0.5rem',
              overflow: 'hidden',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              marginBottom: '2rem',
            }}
          >
            <div style={{ padding: '1.5rem', borderBottom: '1px solid #e5e7eb' }}>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>Test Results</h2>
            </div>

            <div style={{ overflow: 'x' }}>
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                }}
              >
                <thead>
                  <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '1px solid #e5e7eb' }}>
                    <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>
                      Status
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>
                      Agent Name
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>
                      Type
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>
                      Duration
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'left', fontWeight: '600', color: '#1f2937' }}>
                      Details
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result, index) => (
                    <tr
                      key={result.agent_id}
                      style={{
                        borderBottom: index < results.length - 1 ? '1px solid #e5e7eb' : 'none',
                        backgroundColor: index % 2 === 0 ? '#ffffff' : '#f9fafb',
                      }}
                    >
                      <td style={{ padding: '1rem' }}>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '2rem',
                            height: '2rem',
                            borderRadius: '50%',
                            backgroundColor: getStatusColor(result.passed),
                            color: 'white',
                            fontWeight: 'bold',
                          }}
                        >
                          {getStatusIcon(result.passed)}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', fontWeight: '500', color: '#1f2937' }}>
                        {result.agent_name}
                      </td>
                      <td style={{ padding: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>
                        <span
                          style={{
                            padding: '0.25rem 0.75rem',
                            backgroundColor: '#e0e7ff',
                            borderRadius: '0.25rem',
                            color: '#4338ca',
                            display: 'inline-block',
                          }}
                        >
                          {result.agent_type}
                        </span>
                      </td>
                      <td style={{ padding: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>
                        {result.duration_ms ? `${result.duration_ms}ms` : 'N/A'}
                      </td>
                      <td style={{ padding: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>
                        {result.error_message ? (
                          <span style={{ color: '#ef4444' }}>{result.error_message}</span>
                        ) : (
                          <span style={{ color: '#10b981' }}>✓ Working</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Close Button */}
        {!loading && (
          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <button
              onClick={handleClose}
              style={{
                padding: '0.75rem 2rem',
                backgroundColor: '#1e40af',
                color: 'white',
                border: 'none',
                borderRadius: '0.5rem',
                fontSize: '1rem',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#1e3a8a'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#1e40af'
              }}
            >
              Close Test Page
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
