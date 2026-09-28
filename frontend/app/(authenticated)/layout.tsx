'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { useAuthStore } from '@/lib/stores/auth'
import { useTenantStore } from '@/lib/stores/tenant'
import { AgentBox } from '@/components/Common/AgentBox'
import { getAgentExecutionState } from '@/lib/hooks/useAgentExecution'
import { useAgentExecutionPolling } from '@/lib/hooks/useAgentExecutionPolling'

const navigationItems = [
  { href: '/home', label: 'Home', icon: '🏠' },
  { href: '/content', label: 'Content Library', icon: '📚' },
  { href: '/standards', label: 'Standards', icon: '📋' },
  { href: '/curriculum', label: 'Curriculum', icon: '📖' },
  { href: '/alignment', label: 'Alignment', icon: '🎯' },
  { href: '/authoring', label: 'Authoring Studio', icon: '✏️' },
  { href: '/review', label: 'Review Inbox', icon: '👀' },
  { href: '/analytics', label: 'Analytics', icon: '📊' },
  { href: '/agents', label: 'Agents', icon: '🤖' },
  { href: '/profile', label: 'Personal Information', icon: '👤' },
]

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { user, isAuthenticated } = useAuthRequired()
  const { logout } = useAuthStore()
  const { tenant } = useTenantStore()
  const pathname = usePathname()
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [agentState, setAgentState] = useState(getAgentExecutionState())

  useAgentExecutionPolling()

  useEffect(() => {
    const interval = setInterval(() => {
      setAgentState(getAgentExecutionState())
    }, 500)

    return () => clearInterval(interval)
  }, [])

  if (!isAuthenticated) return null

  const handleLogout = () => {
    logout()
    window.location.href = '/'
  }

  const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(' ')
    || user?.full_name
    || user?.name
    || user?.email

  return (
    <div className="min-h-screen bg-page flex">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-ink text-ink-inverse transition-all duration-200 flex flex-col shrink-0`}
      >
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center justify-between">
            <div className={isSidebarOpen ? 'flex items-center gap-2' : 'flex justify-center w-12'}>
              <img src="/academian-logo-icon.png" alt="Academian Logo" className={isSidebarOpen ? 'h-8' : 'h-6'} />
            </div>
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-1 hover:bg-white/10 rounded focus-visible:outline-none"
              aria-label={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
              aria-expanded={isSidebarOpen}
            >
              {isSidebarOpen ? '◀' : '▶'}
            </button>
          </div>
        </div>

        {tenant && isSidebarOpen && (
          <div className="px-4 py-3 bg-white/5 text-sm border-b border-white/10">
            <p className="text-slate-300 text-xs uppercase tracking-wide">Workspace</p>
            <p className="font-medium truncate">{tenant.name}</p>
          </div>
        )}

        <nav aria-label="Primary" className="flex-1 overflow-y-auto py-4">
          {navigationItems.map((item) => {
            const isActive = pathname?.startsWith(item.href)
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? 'page' : undefined}
                className={`flex items-center gap-3 px-4 py-3 transition ${
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-slate-300 hover:bg-white/10 hover:text-white'
                }`}
                title={item.label}
              >
                <span className="text-lg" aria-hidden="true">{item.icon}</span>
                {isSidebarOpen && <span className="text-sm">{item.label}</span>}
              </Link>
            )
          })}
        </nav>

        {isSidebarOpen && (
          <div className="px-0">
            <AgentBox
              agentName={agentState.agentName || undefined}
              progress={agentState.progress}
              isVisible={agentState.isExecuting}
            />
          </div>
        )}

        <div className="border-t border-white/10 p-4">
          {isSidebarOpen ? (
            <div className="space-y-3">
              <div className="text-sm">
                <p className="text-slate-300 text-xs uppercase tracking-wide">User</p>
                <p className="font-medium truncate">{displayName}</p>
                <p className="text-xs text-slate-300 capitalize">
                  {user?.role?.replace(/_/g, ' ')}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full px-3 py-2 bg-white/10 hover:bg-white/20 rounded-md text-sm transition"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full px-2 py-2 bg-white/10 hover:bg-white/20 rounded-md text-sm transition"
              aria-label="Logout"
            >
              🚪
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-surface border-b border-border px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold text-ink">Education Intelligence &amp; Content Orchestration Platform</h1>
            <div className="flex items-center gap-3">
              {user?.id && (
                <img
                  src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/users/profile/photo/${user.id}`}
                  alt={displayName || 'Profile'}
                  className="w-10 h-10 rounded-full border border-border object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none'
                  }}
                />
              )}
              <div className="text-sm text-ink-muted">
                {tenant && <span>{tenant.name} · </span>}
                {displayName} · {user?.email}
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-6 py-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
