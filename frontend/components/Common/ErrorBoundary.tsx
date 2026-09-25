'use client'

import React, { ReactNode } from 'react'
import { Card } from './Card'
import { Button } from './Button'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: (error: Error, reset: () => void) => ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  reset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback?.(this.state.error!, this.reset) || (
          <div className="min-h-screen bg-white p-6 flex items-center justify-center">
            <Card className="max-w-md w-full" variant="outlined">
              <Card.Header>
                <h1 className="text-xl font-bold text-red-800">Something went wrong</h1>
              </Card.Header>
              <Card.Body>
                <p className="text-sm text-slate-700 mb-4">
                  {this.state.error?.message || 'An unexpected error occurred'}
                </p>
                <details className="text-xs text-slate-500 mb-4">
                  <summary className="cursor-pointer font-medium">Error details</summary>
                  <pre className="mt-2 p-2 bg-slate-100 rounded overflow-auto max-h-48">
                    {this.state.error?.stack}
                  </pre>
                </details>
              </Card.Body>
              <Card.Footer>
                <div className="flex gap-2">
                  <Button variant="primary" size="sm" onClick={this.reset}>
                    Try again
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => (window.location.href = '/')}
                  >
                    Go home
                  </Button>
                </div>
              </Card.Footer>
            </Card>
          </div>
        )
      )
    }

    return this.props.children
  }
}
