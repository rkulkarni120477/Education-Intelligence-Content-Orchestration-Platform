'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
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
  { href: '/admin', label: 'Admin', icon: '⚙️' },
]

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { logout } = useAuthStore()
  const { tenant } = useTenantStore()
  const [isClient, setIsClient] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [displayUser, setDisplayUser] = useState<any>(null)

  useEffect(() => {
    setIsClient(true)

    // Load user from localStorage (no auth guard)
    const authToken = localStorage.getItem('auth_token')
    if (authToken) {
      try {
        const parsed = JSON.parse(authToken)
        setDisplayUser({
          id: parsed.email,
          email: parsed.email,
          name: parsed.email.split('@')[0],
          role: 'curriculum_designer',
          tenant_id: 'default',
          created_at: new Date().toISOString(),
        })
      } catch (e) {
        // Fallback user if parsing fails
        setDisplayUser({
          id: 'user',
          email: 'user@example.com',
          name: 'User',
          role: 'curriculum_designer',
          tenant_id: 'default',
          created_at: new Date().toISOString(),
        })
      }
    }
  }, [])

  if (!isClient) {
    return <div className="min-h-screen bg-white"></div>
  }

  const handleLogout = () => {
    logout()
    localStorage.removeItem('auth_token')
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-gradient-to-b from-[#0F172A] to-[#1E40AF] text-white transition-all duration-300 flex flex-col`}
      >
        {/* Logo/Header */}
        <div className="p-4 border-b border-[#1E40AF]">
          <div className="flex items-center justify-between">
            <div className={isSidebarOpen ? 'block' : 'hidden'}>
              <h2 className="text-xl font-bold">Academian</h2>
              <p className="text-xs text-[#3B82F6]">Education Platform</p>
            </div>
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-1 hover:bg-[#1E3A8A] rounded"
              aria-label="Toggle sidebar"
            >
              {isSidebarOpen ? '◀' : '▶'}
            </button>
          </div>
        </div>

        {/* Tenant Info */}
        {tenant && isSidebarOpen && (
          <div className="px-4 py-3 bg-[#1E3A8A] text-sm border-b border-[#1E40AF]">
            <p className="text-[#3B82F6] text-xs uppercase">Workspace</p>
            <p className="font-medium truncate">{tenant.name}</p>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-3 text-[#3B82F6] hover:bg-[#1E3A8A] hover:text-white transition"
              title={item.label}
            >
              <span className="text-lg">{item.icon}</span>
              {isSidebarOpen && <span className="text-sm">{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* User Info & Logout */}
        <div className="border-t border-[#1E40AF] p-4">
          {isSidebarOpen ? (
            <div className="space-y-3">
              <div className="text-sm">
                <p className="text-[#3B82F6] text-xs uppercase">User</p>
                <p className="font-medium truncate">{displayUser?.name || 'User'}</p>
                <p className="text-xs text-[#3B82F6] capitalize">
                  {displayUser?.role?.replace(/_/g, ' ')}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full px-3 py-2 bg-[#1E3A8A] hover:bg-[#0F1E3C] rounded text-sm transition"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full px-2 py-2 bg-[#1E3A8A] hover:bg-[#0F1E3C] rounded text-sm transition"
              title="Logout"
            >
              🚪
            </button>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col">
        {/* Top Navigation */}
        <header className="bg-white border-b-2 border-[#3B82F6] px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-[#0F172A]">Academian Education Platform</h1>
            <div className="text-sm text-slate-600">
              {tenant && <span>{tenant.name} • </span>}
              {displayUser?.email}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto bg-white">
          <div className="max-w-7xl mx-auto px-6 py-8">{children}</div>
        </div>
      </main>
    </div>
  )
}
