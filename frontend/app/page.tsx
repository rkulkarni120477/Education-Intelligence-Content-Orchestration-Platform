'use client'

import { useState } from 'react'

const VALID_CREDENTIALS = {
  email: 'rkulkarni@academian.com',
  password: 'P@ssw0rd'
}

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    console.log('Login attempt:', { email, password: '***' })
    console.log('Valid credentials:', VALID_CREDENTIALS.email)

    if (!email.trim() || !password.trim()) {
      setError('Please enter both email and password.')
      setLoading(false)
      return
    }

    if (email.trim() === VALID_CREDENTIALS.email && password === VALID_CREDENTIALS.password) {
      try {
        const authData = {
          email: email.trim(),
          timestamp: new Date().toISOString(),
          authenticated: true
        }
        console.log('Setting auth token:', authData)
        localStorage.setItem('auth_token', JSON.stringify(authData))
        const storedData = localStorage.getItem('auth_token')
        console.log('Verified auth token in localStorage:', storedData)
        console.log('Auth token set, redirecting to /home...')
        setTimeout(() => {
          console.log('Executing redirect to /home')
          window.location.href = '/home'
        }, 100)
      } catch (err) {
        console.error('Error setting auth token:', err)
        setError('Failed to save session. Please try again.')
        setLoading(false)
      }
    } else {
      console.log('Credentials mismatch')
      console.log('Email match:', email.trim() === VALID_CREDENTIALS.email)
      console.log('Password match:', password === VALID_CREDENTIALS.password)
      setError('Invalid email or password.')
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
