'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Badge } from '@/components/Common/Badge'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'

interface Draft {
  id: string
  title: string
  type: 'lesson' | 'activity' | 'assessment'
  grade: string
  subject: string
  status: 'draft' | 'published'
  createdAt: string
  lastModified: string
  contentCount: number
  sectionCount: number
}

export default function DraftsPage() {
  const { isAuthenticated } = useAuthRequired()

  // Mock data - would fetch from API
  const [drafts] = useState<Draft[]>([
    {
      id: 'draft-1',
      title: 'Introduction to Fractions',
      type: 'lesson',
      grade: '4',
      subject: 'Mathematics',
      status: 'draft',
      createdAt: '2026-09-24T10:30:00Z',
      lastModified: '2026-09-24T14:45:00Z',
      contentCount: 3,
      sectionCount: 6,
    },
    {
      id: 'draft-2',
      title: 'Photosynthesis Process',
      type: 'lesson',
      grade: '7',
      subject: 'Science',
      status: 'published',
      createdAt: '2026-09-22T09:00:00Z',
      lastModified: '2026-09-23T16:20:00Z',
      contentCount: 2,
      sectionCount: 6,
    },
    {
      id: 'draft-3',
      title: 'Quadratic Equations Quiz',
      type: 'assessment',
      grade: '9',
      subject: 'Mathematics',
      status: 'draft',
      createdAt: '2026-09-24T11:15:00Z',
      lastModified: '2026-09-24T13:30:00Z',
      contentCount: 1,
      sectionCount: 3,
    },
  ])

  const [sortBy, setSortBy] = useState<'modified' | 'created' | 'title'>('modified')
  const [filterType, setFilterType] = useState<'all' | 'lesson' | 'activity' | 'assessment'>('all')
  const [filterStatus, setFilterStatus] = useState<'all' | 'draft' | 'published'>('all')

  if (!isAuthenticated) return null

  const filteredDrafts = drafts
    .filter((draft) => filterType === 'all' || draft.type === filterType)
    .filter((draft) => filterStatus === 'all' || draft.status === filterStatus)
    .sort((a, b) => {
      if (sortBy === 'modified') {
        return new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
      }
      if (sortBy === 'created') {
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      }
      return a.title.localeCompare(b.title)
    })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffMins = Math.floor(diffMs / (1000 * 60))

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const typeEmoji = {
    lesson: '📖',
    activity: '🎬',
    assessment: '📝',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-[#6B4423]">Authoring Drafts</h1>
            <p className="text-[#8B5A3C] mt-2">Manage and edit your lesson and assessment drafts</p>
          </div>
          <Link href="/authoring">
            <Button variant="primary">+ Create New</Button>
          </Link>
        </div>
      </div>

      {/* Filters */}
      <Card variant="outlined">
        <Card.Body>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'modified' | 'created' | 'title')}
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
              >
                <option value="modified">Last Modified</option>
                <option value="created">Created Date</option>
                <option value="title">Title (A-Z)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">Type</label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value as 'all' | 'lesson' | 'activity' | 'assessment')}
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
              >
                <option value="all">All Types</option>
                <option value="lesson">Lessons</option>
                <option value="activity">Activities</option>
                <option value="assessment">Assessments</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">Status</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as 'all' | 'draft' | 'published')}
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
              >
                <option value="all">All Status</option>
                <option value="draft">Drafts</option>
                <option value="published">Published</option>
              </select>
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Drafts List */}
      {filteredDrafts.length === 0 ? (
        <Card variant="outlined">
          <Card.Body>
            <div className="text-center py-12">
              <p className="text-2xl mb-3">📭</p>
              <p className="text-slate-600 mb-4">No drafts found</p>
              <Link href="/authoring">
                <Button variant="primary">Create Your First Draft</Button>
              </Link>
            </div>
          </Card.Body>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {filteredDrafts.map((draft) => (
            <Card key={draft.id} variant="outlined" className="hover:bg-[#FFF8F0] transition">
              <Card.Body>
                <div className="flex items-start justify-between gap-4">
                  {/* Draft Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{typeEmoji[draft.type]}</span>
                      <div>
                        <h3 className="text-lg font-bold text-[#6B4423]">{draft.title}</h3>
                        <p className="text-sm text-slate-600">
                          Grade {draft.grade} • {draft.subject}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                      <Badge variant={draft.status === 'draft' ? 'warning' : 'success'}>
                        {draft.status === 'draft' ? 'Draft' : 'Published'}
                      </Badge>
                      <span className="text-xs text-slate-500">
                        {draft.contentCount} content item{draft.contentCount !== 1 ? 's' : ''}
                      </span>
                      <span className="text-xs text-slate-500">
                        {draft.sectionCount} sections
                      </span>
                      <span className="text-xs text-slate-500">
                        Modified {formatDate(draft.lastModified)}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Link href={`/authoring/${draft.id}/edit`}>
                      <Button variant="secondary">Edit</Button>
                    </Link>
                    <Button variant="tertiary">⋮</Button>
                  </div>
                </div>
              </Card.Body>
            </Card>
          ))}
        </div>
      )}

      {/* Stats */}
      {filteredDrafts.length > 0 && (
        <Card variant="outlined" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-2xl font-bold text-blue-800">{drafts.length}</p>
                <p className="text-sm text-blue-700">Total Drafts</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-800">
                  {drafts.filter((d) => d.status === 'draft').length}
                </p>
                <p className="text-sm text-blue-700">In Progress</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-800">
                  {drafts.filter((d) => d.status === 'published').length}
                </p>
                <p className="text-sm text-blue-700">Published</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-blue-800">
                  {drafts.reduce((sum, d) => sum + d.contentCount, 0)}
                </p>
                <p className="text-sm text-blue-700">Content Items</p>
              </div>
            </div>
          </Card.Body>
        </Card>
      )}
    </div>
  )
}
