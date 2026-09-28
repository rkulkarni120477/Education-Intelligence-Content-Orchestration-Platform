'use client'

import { useState } from 'react'
import { useAuthStore } from '@/lib/stores/auth'

export default function LoginPage() {
  const login = useAuthStore((state) => state.login)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.')
      setLoading(false)
      return
    }

    try {
      await login(email.trim(), password)
      window.location.href = '/home'
    } catch (err: any) {
      setError(err.message || 'Sign in failed. Check your email and password.')
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-page flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo and Branding */}
        <div className="text-center mb-8">
          <img src="/academian-logo.png" alt="Academian Logo" className="h-32 mx-auto mb-6" />
          <h1 className="text-4xl font-semibold text-ink">Education Intelligence</h1>
          <p className="text-ink-muted text-lg mt-2">&amp; Content Orchestration Platform</p>
        </div>

        {/* Login Form */}
        <form onSubmit={handleLogin} className="bg-surface rounded-lg shadow-md p-8 border border-border">
          <h2 className="text-2xl font-semibold text-ink mb-6">Sign In</h2>

          {error && (
            <div role="alert" className="bg-red-50 border border-error text-error px-4 py-3 rounded-md mb-4 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-ink mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="rkulkarni@academian.com"
                className="w-full px-4 py-3 border border-border rounded-md focus-visible:border-primary bg-surface"
                required
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-ink mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-border rounded-md focus-visible:border-primary bg-surface"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-6 bg-primary text-white font-semibold py-3 rounded-md hover:bg-primary-hover transition disabled:opacity-60"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          <p className="text-center text-ink-muted text-sm mt-4">
            AWS IAM authentication coming soon
          </p>
        </form>

        {/* Footer */}
        <p className="text-center text-ink-muted text-xs mt-6">
          © 2026 Academian Education. All rights reserved.
        </p>
      </div>
    </main>
  )
}
