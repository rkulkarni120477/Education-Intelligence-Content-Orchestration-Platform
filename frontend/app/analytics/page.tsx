'use client'

import React, { useState } from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import {
  useDashboardAnalytics,
  useAlignmentAnalytics,
  useCoverageAnalytics,
} from '@/lib/api/analytics'
import { StatCard } from '@/components/Analytics/StatCard'
import { SimpleChart } from '@/components/Analytics/SimpleChart'
import { Card } from '@/components/Common/Card'
import { Skeleton } from '@/components/Common/Skeleton'

type Period = 'week' | 'month' | 'quarter' | 'year'

export default function AnalyticsPage() {
  const { isAuthenticated } = useAuthRequired()
  const [period, setPeriod] = useState<Period>('week')

  // Queries
  const dashboard = useDashboardAnalytics(period)
  const alignmentAnalytics = useAlignmentAnalytics()
  const coverageAnalytics = useCoverageAnalytics()

  if (!isAuthenticated) return null

  const data = dashboard.data
  const alignment = alignmentAnalytics.data
  const coverage = coverageAnalytics.data

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#6B4423]">Analytics & Reporting</h1>
        <p className="text-[#8B5A3C] mt-2">
          Track alignment progress, coverage metrics, and platform performance
        </p>
      </div>

      {/* Period Selector */}
      <Card variant="outlined">
        <Card.Body>
          <div className="flex flex-wrap gap-2">
            {(['week', 'month', 'quarter', 'year'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
                  period === p
                    ? 'bg-[#8B5A3C] text-white'
                    : 'bg-[#F0E6D8] text-[#6B4423] hover:bg-[#D2B48C]'
                }`}
              >
                Last {p}
              </button>
            ))}
          </div>
        </Card.Body>
      </Card>

      {/* Overview Cards */}
      {dashboard.isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <StatCard
            label="Total Content"
            value={data.overview.total_content_items}
            icon="📄"
            color="primary"
          />
          <StatCard
            label="Total Alignments"
            value={data.overview.total_alignments}
            icon="🎯"
            color="info"
            change={12}
            trend="up"
          />
          <StatCard
            label="Approved"
            value={data.overview.approved_alignments}
            icon="✓"
            color="success"
          />
          <StatCard
            label="Pending"
            value={data.overview.pending_alignments}
            icon="⏳"
            color="warning"
          />
          <StatCard
            label="Rejected"
            value={data.overview.rejected_alignments}
            icon="✗"
            color="danger"
          />
        </div>
      ) : null}

      {/* Main Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Coverage Overview */}
        {dashboard.isLoading ? (
          <Skeleton className="h-64" />
        ) : data ? (
          <Card variant="outlined">
            <Card.Header>
              <h3 className="text-lg font-bold text-[#6B4423]">Content Alignment Status</h3>
            </Card.Header>

            <Card.Body>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-medium text-[#6B4423]">Overall Coverage</p>
                    <p className="text-lg font-bold text-[#8B5A3C]">
                      {data.coverage.alignment_percentage.toFixed(1)}%
                    </p>
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-3">
                    <div
                      className="h-3 rounded-full bg-green-500"
                      style={{ width: `${data.coverage.alignment_percentage}%` }}
                    ></div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mt-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {data.coverage.fully_aligned}
                    </p>
                    <p className="text-xs text-slate-600">Fully Aligned</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-amber-600">
                      {data.coverage.partially_aligned}
                    </p>
                    <p className="text-xs text-slate-600">Partial</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-600">
                      {data.coverage.not_aligned}
                    </p>
                    <p className="text-xs text-slate-600">Not Aligned</p>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>
        ) : null}

        {/* Standards Coverage */}
        {dashboard.isLoading ? (
          <Skeleton className="h-64" />
        ) : data ? (
          <Card variant="outlined">
            <Card.Header>
              <h3 className="text-lg font-bold text-[#6B4423]">Standards Coverage</h3>
            </Card.Header>

            <Card.Body>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-slate-600">{data.standards.frameworks} Frameworks</p>
                  <p className="text-2xl font-bold text-[#8B5A3C]">
                    {data.standards.covered_standards} / {data.standards.standards}
                  </p>
                  <p className="text-sm text-slate-600 mt-1">
                    {data.standards.coverage_rate.toFixed(1)}% Coverage
                  </p>
                </div>

                <div className="w-full bg-slate-200 rounded-full h-3">
                  <div
                    className="h-3 rounded-full bg-blue-500"
                    style={{ width: `${data.standards.coverage_rate}%` }}
                  ></div>
                </div>
              </div>
            </Card.Body>
          </Card>
        ) : null}
      </div>

      {/* Quality Metrics */}
      {dashboard.isLoading ? (
        <Skeleton className="h-80" />
      ) : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card variant="outlined">
            <Card.Header>
              <h3 className="text-lg font-bold text-[#6B4423]">Quality Metrics</h3>
            </Card.Header>

            <Card.Body>
              <div className="space-y-4">
                <div>
                  <p className="text-sm font-medium text-[#6B4423] mb-2">
                    Average Confidence Score
                  </p>
                  <p className="text-3xl font-bold text-[#8B5A3C]">
                    {(data.quality.avg_confidence_score * 100).toFixed(0)}%
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="text-center">
                    <p className="text-xl font-bold text-green-600">
                      {data.quality.high_confidence}
                    </p>
                    <p className="text-xs text-slate-600">High (80%+)</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-amber-600">
                      {data.quality.medium_confidence}
                    </p>
                    <p className="text-xs text-slate-600">Medium (60-80%)</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-red-600">
                      {data.quality.low_confidence}
                    </p>
                    <p className="text-xs text-slate-600">Low (&lt;60%)</p>
                  </div>
                </div>
              </div>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Header>
              <h3 className="text-lg font-bold text-[#6B4423]">Review Performance</h3>
            </Card.Header>

            <Card.Body>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-600">Avg Review Time</p>
                  <p className="text-3xl font-bold text-[#8B5A3C]">
                    {data.performance.avg_review_time}h
                  </p>
                </div>

                <div>
                  <p className="text-sm text-slate-600">Approval Rate</p>
                  <p className="text-3xl font-bold text-green-600">
                    {(data.performance.avg_approval_rate * 100).toFixed(0)}%
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-200">
                  <p className="text-xs text-slate-600">Top Reviewer</p>
                  <p className="text-sm font-bold text-[#6B4423] mt-1">
                    {data.performance.top_reviewer}
                  </p>
                  <p className="text-xs text-slate-600">
                    {data.performance.reviews_completed} reviews completed
                  </p>
                </div>
              </div>
            </Card.Body>
          </Card>
        </div>
      ) : null}

      {/* Timeline Charts */}
      {dashboard.isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      ) : data ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SimpleChart
            title="Alignments Created"
            data={data.timeline.labels.map((label, idx) => ({
              label,
              value: data.timeline.alignments_created[idx],
            }))}
            color="#8B5A3C"
          />

          <SimpleChart
            title="Alignments Approved"
            data={data.timeline.labels.map((label, idx) => ({
              label,
              value: data.timeline.alignments_approved[idx],
            }))}
            color="#22c55e"
          />
        </div>
      ) : null}

      {/* Alignment Distribution */}
      {alignmentAnalytics.isLoading ? (
        <Skeleton className="h-96" />
      ) : alignment ? (
        <Card variant="outlined">
          <Card.Header>
            <h3 className="text-lg font-bold text-[#6B4423]">Alignment by Framework</h3>
          </Card.Header>

          <Card.Body>
            <div className="space-y-4">
              {alignment.by_standard_framework.map((framework) => (
                <div key={framework.name}>
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-sm font-medium text-[#6B4423]">{framework.name}</p>
                    <p className="text-xs text-slate-600">
                      {framework.aligned}/{framework.aligned + framework.pending + framework.rejected}
                    </p>
                  </div>

                  <div className="flex h-2 gap-0.5 rounded-full overflow-hidden bg-slate-200">
                    <div
                      className="bg-green-500"
                      style={{
                        width: `${(framework.aligned / (framework.aligned + framework.pending + framework.rejected)) * 100}%`,
                      }}
                    ></div>
                    <div
                      className="bg-amber-500"
                      style={{
                        width: `${(framework.pending / (framework.aligned + framework.pending + framework.rejected)) * 100}%`,
                      }}
                    ></div>
                    <div
                      className="bg-red-500"
                      style={{
                        width: `${(framework.rejected / (framework.aligned + framework.pending + framework.rejected)) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      ) : null}

      {/* Coverage by Grade */}
      {coverageAnalytics.isLoading ? (
        <Skeleton className="h-80" />
      ) : coverage ? (
        <Card variant="outlined">
          <Card.Header>
            <h3 className="text-lg font-bold text-[#6B4423]">Coverage by Grade</h3>
          </Card.Header>

          <Card.Body>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {coverage.by_grade.map((grade) => (
                <div key={grade.grade} className="text-center">
                  <p className="text-2xl font-bold text-[#8B5A3C]">
                    {grade.coverage.toFixed(0)}%
                  </p>
                  <p className="text-sm text-slate-600 mt-1">Grade {grade.grade}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {grade.covered}/{grade.total}
                  </p>
                </div>
              ))}
            </div>
          </Card.Body>
        </Card>
      ) : null}

      {/* Help */}
      <Card variant="default" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <p className="font-bold text-blue-800 mb-2">📊 Analytics Dashboard</p>
          <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
            <li>
              <strong>Overview:</strong> Total content, alignments, and status breakdown
            </li>
            <li>
              <strong>Coverage:</strong> Alignment status and standards framework coverage
            </li>
            <li>
              <strong>Quality:</strong> Confidence scores and content quality metrics
            </li>
            <li>
              <strong>Performance:</strong> Review times, approval rates, and reviewer stats
            </li>
            <li>
              <strong>Timeline:</strong> Trends over the selected period
            </li>
          </ul>
        </Card.Body>
      </Card>
    </div>
  )
}
