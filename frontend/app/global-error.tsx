'use client'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <html>
      <body>
        <div className="min-h-screen bg-page flex items-center justify-center px-4">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-ink mb-4">Critical Error</h1>
            <p className="text-ink-muted mb-8 max-w-md">
              {error.message || 'A critical error occurred. Please refresh the page.'}
            </p>
            <button
              onClick={reset}
              className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-hover transition"
            >
              Refresh Page
            </button>
          </div>
        </div>
      </body>
    </html>
  )
}
