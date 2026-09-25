'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'

const menuItems = [
  {
    id: 'knowledge-intelligence',
    label: 'Knowledge Intelligence',
    icon: '🧠',
    submenu: ['Upload & Ingest Content', 'View Content', 'Search Content', 'Reports', 'Metadata Enrichment', 'Recommendations']
  },
  {
    id: 'workforce-skills',
    label: 'Workforce Skills Management',
    icon: '👥',
    submenu: ['New Organization Setup', 'Workforce Skills Management', 'Workforce Skills Compliance', 'Reports', 'Skills Extraction', 'Competency Mapping', 'Learning Pathway Generation', 'Gap Insights']
  },
  {
    id: 'content-studio',
    label: 'Content Studio',
    icon: '✏️',
    submenu: ['Content Shortlisting', 'Content Search', 'Content Transformation', 'Reports', 'Blueprint Authoring', 'Assessment Creation', 'Versioning', 'Publishing Packages']
  },
  {
    id: 'accessibility',
    label: 'Accessibility',
    icon: '♿',
    submenu: ['Accessibility Analysis', 'Accessibility Support', 'Reports', 'WCAG Checks', 'Issue Detection', 'Remediation Suggestions', 'Compliance Reporting']
  },
  {
    id: 'standards',
    label: 'Standards & Skills',
    icon: '📋',
    submenu: ['Standards Ingestion', 'Crosswalks', 'Certification Mapping', 'Outcome Alignment']
  },
  {
    id: 'administration',
    label: 'Administration',
    icon: '⚙️',
    submenu: ['User Management', 'Orchestration']
  },
  {
    id: 'orchestration',
    label: 'Orchestration',
    icon: '🎯',
    submenu: ['Planner/Supervisor', 'Workflow State', 'Task Routing', 'Tool/API Invocation', 'Memory/Context', 'Review Gates', 'Notifications']
  }
]

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const [activeMenu, setActiveMenu] = useState('knowledge-intelligence')
  const [openSubmenu, setOpenSubmenu] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(true)
  const [userEmail, setUserEmail] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const authToken = localStorage.getItem('auth_token')
      if (authToken) {
        try {
          const auth = JSON.parse(authToken)
          if (auth.authenticated) {
            setIsAuthenticated(true)
            setUserEmail(auth.email)
            setIsLoading(false)
            return
          }
        } catch (err) {
          console.error('Auth parse error:', err)
        }
      }
      setIsAuthenticated(false)
      setIsLoading(false)
      window.location.href = '/'
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    window.location.href = '/'
  }

  if (isLoading) {
    return <div className="min-h-screen bg-white flex items-center justify-center">Loading...</div>
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <nav className="bg-gradient-to-r from-[#6B4423] to-[#8B5A3C] text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image
              src="/academian-logo.png"
              alt="Academian Logo"
              width={50}
              height={50}
            />
            <div>
              <h1 className="text-2xl font-bold">Academian</h1>
              <p className="text-[#F5DEB3] text-sm">Education Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-[#F5DEB3] text-sm">{userEmail}</span>
            <button
              onClick={handleLogout}
              className="bg-[#D2B48C] text-[#6B4423] px-4 py-2 rounded-lg font-semibold hover:bg-white transition"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Main Menu */}
        <div className="bg-[#5A3A1F] border-t-2 border-[#8B5A3C]">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex overflow-x-auto space-x-1">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveMenu(item.id)
                    setOpenSubmenu(activeMenu === item.id ? null : item.id)
                  }}
                  className={`px-4 py-3 whitespace-nowrap font-medium transition ${
                    activeMenu === item.id
                      ? 'bg-[#8B5A3C] text-white border-b-2 border-[#D2B48C]'
                      : 'text-[#D2B48C] hover:bg-[#6B4423]'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Submenu */}
        {openSubmenu && (
          <div className="bg-[#8B5A3C] border-t border-[#A0826D]">
            <div className="max-w-7xl mx-auto px-6 py-3">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {menuItems.find(m => m.id === openSubmenu)?.submenu.map((item) => (
                  <button
                    key={item}
                    className="text-left px-3 py-2 text-[#F5DEB3] hover:bg-[#6B4423] rounded transition text-sm"
                  >
                    • {item}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  )
}
