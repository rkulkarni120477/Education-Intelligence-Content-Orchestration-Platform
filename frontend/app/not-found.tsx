import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="min-h-screen bg-page flex items-center justify-center px-4">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-ink mb-4">404</h1>
        <p className="text-2xl font-semibold text-ink-muted mb-4">Page not found</p>
        <p className="text-ink-muted mb-8 max-w-md">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-block bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-hover transition"
        >
          Go Home
        </Link>
      </div>
    </div>
  )
}
