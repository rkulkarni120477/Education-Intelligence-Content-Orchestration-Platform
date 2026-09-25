'use client'

import React, { ReactNode, ReactElement } from 'react'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'

interface Props {
  children: ReactNode
  fallback?: ReactElement
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
  resetKeys?: Array<string | number>
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
  errorCount: number
}

export class AdvancedErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0,
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState((prevState) => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1,
    }))

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo)
    }

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }
  }

  componentDidUpdate(prevProps: Props) {
    // Reset error boundary if reset keys changed
    if (
      this.props.resetKeys &&
      prevProps.resetKeys &&
      this.props.resetKeys.some((key, index) => key !== prevProps.resetKeys?.[index])
    ) {
      this.resetError()
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="p-4">
          <Card variant="outlined" className="border-red-300 bg-red-50">
            <Card.Header>
              <h2 className="text-xl font-bold text-red-800">⚠️ Something Went Wrong</h2>
            </Card.Header>

            <Card.Body className="space-y-4">
              <p className="text-red-700">
                We encountered an error while loading this page. Please try again.
              </p>

              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="space-y-2">
                  <p className="font-bold text-red-800">Error Details:</p>
                  <div className="bg-white p-3 rounded border border-red-200 overflow-auto max-h-40">
                    <code className="text-xs text-red-700 whitespace-pre-wrap">
                      {this.state.error.toString()}
                    </code>
                  </div>

                  {this.state.errorInfo && (
                    <div className="bg-white p-3 rounded border border-red-200 overflow-auto max-h-40">
                      <code className="text-xs text-red-700 whitespace-pre-wrap">
                        {this.state.errorInfo.componentStack}
                      </code>
                    </div>
                  )}
                </div>
              )}

              <p className="text-sm text-red-600">
                Error occurrences: {this.state.errorCount}
              </p>

              <div className="flex gap-2">
                <Button variant="primary" onClick={this.resetError}>
                  Try Again
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => window.location.href = '/home'}
                >
                  Go Home
                </Button>
              </div>
            </Card.Body>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

AdvancedErrorBoundary.displayName = 'AdvancedErrorBoundary'
