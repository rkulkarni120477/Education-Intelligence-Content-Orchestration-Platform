'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
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
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const { tenant } = useTenantStore()
  const [isClient, setIsClient] = useState(false)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  useEffect(() => {
    setIsClient(true)
    // Verify user is authenticated
    if (!user) {
      router.push('/')
    }
  }, [user, router])

  if (!isClient || !user) return null

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* Sidebar */}
      <aside
        className={`${
          isSidebarOpen ? 'w-64' : 'w-20'
        } bg-gradient-to-b from-[#6B4423] to-[#8B5A3C] text-white transition-all duration-300 flex flex-col`}
      >
        {/* Logo/Header */}
        <div className="p-4 border-b border-[#8B5A3C]">
          <div className="flex items-center justify-between">
            <div className={isSidebarOpen ? 'block' : 'hidden'}>
              <h2 className="text-xl font-bold">Academian</h2>
              <p className="text-xs text-[#D2B48C]">Education Platform</p>
            </div>
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-1 hover:bg-[#5A3A1F] rounded"
              aria-label="Toggle sidebar"
            >
              {isSidebarOpen ? '◀' : '▶'}
            </button>
          </div>
        </div>

        {/* Tenant Info */}
        {tenant && isSidebarOpen && (
          <div className="px-4 py-3 bg-[#5A3A1F] text-sm border-b border-[#8B5A3C]">
            <p className="text-[#D2B48C] text-xs uppercase">Workspace</p>
            <p className="font-medium truncate">{tenant.name}</p>
          </div>
        )}

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {navigationItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-3 text-[#D2B48C] hover:bg-[#5A3A1F] hover:text-white transition"
              title={item.label}
            >
              <span className="text-lg">{item.icon}</span>
              {isSidebarOpen && <span className="text-sm">{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* User Info & Logout */}
        <div className="border-t border-[#8B5A3C] p-4">
          {isSidebarOpen ? (
            <div className="space-y-3">
              <div className="text-sm">
                <p className="text-[#D2B48C] text-xs uppercase">User</p>
                <p className="font-medium truncate">{user.name || user.email}</p>
                <p className="text-xs text-[#D2B48C] capitalize">
                  {user.role.replace(/_/g, ' ')}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="w-full px-3 py-2 bg-[#5A3A1F] hover:bg-[#4A2C18] rounded text-sm transition"
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              onClick={handleLogout}
              className="w-full px-2 py-2 bg-[#5A3A1F] hover:bg-[#4A2C18] rounded text-sm transition"
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
        <header className="bg-white border-b-2 border-[#D2B48C] px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-[#6B4423]">Academian Education Platform</h1>
            <div className="text-sm text-slate-600">
              {tenant && <span>{tenant.name} • </span>}
              {user.email}
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
