'use client'

import React from 'react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen bg-page flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-ink mb-4">Something went wrong</h1>
        <p className="text-ink-muted mb-8 max-w-md">
          {error.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <button
          onClick={reset}
          className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-hover transition"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
