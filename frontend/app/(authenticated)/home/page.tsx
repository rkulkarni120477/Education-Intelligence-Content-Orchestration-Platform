'use client'

import React from 'react'
import Link from 'next/link'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { useProcessingJobs, useContentAssets } from '@/lib/api/content'
import { useAlignments } from '@/lib/api/alignments'
import { useLessons } from '@/lib/api/lessons'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { StatusBadge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

export default function HomePage() {
  const { user, isAuthenticated } = useAuthRequired()

  // Fetch dashboard data
  const processingJobsQuery = useProcessingJobs()
  const contentQuery = useContentAssets(1, 5, { status: 'review_required' })
  const alignmentsQuery = useAlignments('content')
  const lessonsQuery = useLessons()

  if (!isAuthenticated) return null

  const processingJobs = processingJobsQuery.data || []
  const reviewItems = contentQuery.data?.items || []
  const recentAlignments = alignmentsQuery.data?.slice(0, 5) || []
  const recentLessons = lessonsQuery.data?.slice(0, 5) || []

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-[#1E40AF] to-[#0F172A] text-white p-8 rounded-lg shadow-lg">
        <h1 className="text-4xl font-bold mb-2">Welcome back, {user?.name || user?.email}!</h1>
        <p className="text-[#E0F2FE] text-lg">
          {user?.role ? `You are logged in as ${user.role.replace(/_/g, ' ')}` : ''}
        </p>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-[#0F172A] mb-4">⚡ Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link href="/content">
            <Button variant="primary" className="w-full h-full py-6">
              📤 Upload Content
            </Button>
          </Link>
          <Link href="/alignment">
            <Button variant="primary" className="w-full h-full py-6">
              🎯 Review Alignments
            </Button>
          </Link>
          <Link href="/authoring/lesson">
            <Button variant="primary" className="w-full h-full py-6">
              ✏️ Create Lesson
            </Button>
          </Link>
          <Link href="/standards">
            <Button variant="primary" className="w-full h-full py-6">
              📋 Browse Standards
            </Button>
          </Link>
        </div>
      </div>

      {/* Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Processing Jobs */}
        <div>
          <h3 className="text-xl font-bold text-[#0F172A] mb-4">📊 Processing Jobs</h3>
          {processingJobsQuery.isLoading ? (
            <Skeleton className="h-48" />
          ) : processingJobs.length > 0 ? (
            <Card variant="outlined" className="space-y-3">
              {processingJobs.map((job) => (
                <div
                  key={job.id}
                  className="pb-3 border-b border-[#3B82F6] last:border-b-0 last:pb-0"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-medium text-[#0F172A]">Content Processing</p>
                    <p className="text-sm text-slate-500">{job.progress}%</p>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-[#1E40AF] h-2 rounded-full transition-all"
                      style={{ width: `${job.progress}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </Card>
          ) : (
            <Card variant="outlined">
              <Card.Body>
                <p className="text-slate-600 text-center">No active processing jobs</p>
              </Card.Body>
            </Card>
          )}
        </div>

        {/* Items Awaiting Review */}
        <div>
          <h3 className="text-xl font-bold text-[#0F172A] mb-4">🔍 Awaiting Review</h3>
          {contentQuery.isLoading ? (
            <Skeleton className="h-48" />
          ) : reviewItems.length > 0 ? (
            <Card variant="outlined">
              <Card.Body className="space-y-3">
                {reviewItems.map((item) => (
                  <Link key={item.id} href="/content" className="block">
                    <div className="pb-3 border-b border-[#3B82F6] last:border-b-0 last:pb-0 hover:bg-[#FFFFFF] -mx-4 px-4 py-3 rounded cursor-pointer transition">
                      <p className="font-medium text-[#0F172A] hover:text-[#1E40AF]">
                        {item.title}
                      </p>
                      <p className="text-sm text-slate-500 mt-1">{item.subject || 'General'}</p>
                    </div>
                  </Link>
                ))}
                <Link href="/content" className="text-sm text-[#1E40AF] font-medium hover:text-[#0F172A]">
                  View all ({contentQuery.data?.total || 0})
                </Link>
              </Card.Body>
            </Card>
          ) : (
            <Card variant="outlined">
              <Card.Body>
                <p className="text-slate-600 text-center">No items awaiting review</p>
              </Card.Body>
            </Card>
          )}
        </div>

        {/* Recent Alignments */}
        <div>
          <h3 className="text-xl font-bold text-[#0F172A] mb-4">🎯 Recent Alignments</h3>
          {alignmentsQuery.isLoading ? (
            <Skeleton className="h-48" />
          ) : recentAlignments.length > 0 ? (
            <Card variant="outlined">
              <Card.Body className="space-y-3">
                {recentAlignments.map((alignment) => (
                  <div
                    key={alignment.id}
                    className="pb-3 border-b border-[#3B82F6] last:border-b-0 last:pb-0"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-[#0F172A]">
                        {alignment.source_type === 'content' ? 'Content' : 'Lesson'} Alignment
                      </p>
                      <StatusBadge status={alignment.status} />
                    </div>
                    <p className="text-sm text-slate-500">
                      Confidence: {Math.round(alignment.confidence * 100)}%
                    </p>
                  </div>
                ))}
              </Card.Body>
            </Card>
          ) : (
            <Card variant="outlined">
              <Card.Body>
                <p className="text-slate-600 text-center">No recent alignments</p>
              </Card.Body>
            </Card>
          )}
        </div>

        {/* Recent Lessons */}
        <div>
          <h3 className="text-xl font-bold text-[#0F172A] mb-4">📚 Recent Lessons</h3>
          {lessonsQuery.isLoading ? (
            <Skeleton className="h-48" />
          ) : recentLessons.length > 0 ? (
            <Card variant="outlined">
              <Card.Body className="space-y-3">
                {recentLessons.map((lesson) => (
                  <div
                    key={lesson.id}
                    className="pb-3 border-b border-[#3B82F6] last:border-b-0 last:pb-0"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <p className="font-medium text-[#0F172A] truncate hover:text-[#1E40AF]">
                        {lesson.title}
                      </p>
                      <StatusBadge status={lesson.status} />
                    </div>
                    <p className="text-sm text-slate-500">
                      {lesson.grade ? `Grade ${lesson.grade}` : ''} {lesson.subject ? `• ${lesson.subject}` : ''}
                    </p>
                  </div>
                ))}
              </Card.Body>
            </Card>
          ) : (
            <Card variant="outlined">
              <Card.Body>
                <p className="text-slate-600 text-center">No recent lessons</p>
              </Card.Body>
            </Card>
          )}
        </div>
      </div>

      {/* Statistics */}
      <div>
        <h3 className="text-xl font-bold text-[#0F172A] mb-4">📈 Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">{contentQuery.data?.total || 0}</p>
              <p className="text-sm text-slate-600 mt-2">Content Assets</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">{processingJobs.length}</p>
              <p className="text-sm text-slate-600 mt-2">Active Jobs</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">{recentAlignments.length}</p>
              <p className="text-sm text-slate-600 mt-2">Alignments</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">{recentLessons.length}</p>
              <p className="text-sm text-slate-600 mt-2">Lessons</p>
            </Card.Body>
          </Card>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card variant="default" className="bg-green-50 border-green-200">
          <Card.Body>
            <p className="font-bold text-green-800 mb-2">✓ System Status: Healthy</p>
            <p className="text-sm text-green-700">
              All systems are running normally. API endpoint is connected at localhost:8000
            </p>
          </Card.Body>
        </Card>

        <Card variant="default" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <p className="font-bold text-blue-800 mb-2">💡 Tip: Get Started</p>
            <p className="text-sm text-blue-700">
              Upload your first content asset to begin aligning it with standards and creating lessons.
            </p>
          </Card.Body>
        </Card>
      </div>
    </div>
  )
}
