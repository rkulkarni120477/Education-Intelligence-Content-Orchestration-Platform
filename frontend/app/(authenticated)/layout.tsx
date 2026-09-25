'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { useAuthStore } from '@/lib/stores/auth'
import { useTenantStore } from '@/lib/stores/tenant'

const navigationItems = [
  { href: '/home', label: 'Home', icon: '🏠' },
  { href: '/content', label: 'Content Library', icon: '📚' },
  { href: '/standards', label: 'Standards', icon: '📋' },
  { href: '/curriculum', label: 'Curriculum', icon: '📖' },
  { href: '/alignment', label: 'Alignment', icon: '🎯' },
  { href: '/authoring', label: 'Authoring Studio', icon: '✏️' },
  { href: '/review', label: 'Review Inbox', icon: '👀' },
  { href: '/analytics', label: 'Analytics', icon: '📊' },
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

  if (!isAuthenticated) return null

  const handleLogout = () => {
    logout()
    window.location.href = '/'
  }

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
            <div className={isSidebarOpen ? 'block' : 'hidden'}>
              <h2 className="text-xl font-bold">Education Intelligence</h2>
              <p className="text-xs text-slate-300">&amp; Content Orchestration Platform</p>
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

        <div className="border-t border-white/10 p-4">
          {isSidebarOpen ? (
            <div className="space-y-3">
              <div className="text-sm">
                <p className="text-slate-300 text-xs uppercase tracking-wide">User</p>
                <p className="font-medium truncate">{user?.name || user?.email}</p>
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
            <div className="text-sm text-ink-muted">
              {tenant && <span>{tenant.name} · </span>}
              {user?.email}
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
