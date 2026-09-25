'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import {
  useReviewQueue,
  useReviewItem,
  useApproveReview,
  useRejectReview,
  useRequestRevision,
  useReviewStats,
  type ReviewItem,
} from '@/lib/api/review'
import { ReviewCard } from '@/components/Review/ReviewCard'
import { ReviewDecision } from '@/components/Review/ReviewDecision'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Badge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

type FilterStatus = 'all' | 'pending' | 'approved' | 'rejected' | 'revision'

export default function ReviewInboxPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthRequired()

  const [filterStatus, setFilterStatus] = useState<FilterStatus>('pending')
  const [selectedItemId, setSelectedItemId] = useState<string>('')

  // Queries
  const queue = useReviewQueue(filterStatus === 'all' ? undefined : filterStatus)
  const selectedItem = useReviewItem(selectedItemId)
  const stats = useReviewStats()

  // Mutations
  const approveMutation = useApproveReview()
  const rejectMutation = useRejectReview()
  const revisionMutation = useRequestRevision()

  if (!isAuthenticated) return null

  const items = queue.data || []
  const selected = items.find((item) => item.id === selectedItemId)

  const handleSelectItem = (item: ReviewItem) => {
    setSelectedItemId(item.id)
  }

  const handleApprove = async (notes: string) => {
    await approveMutation.mutateAsync({ itemId: selectedItemId, notes })
    // Move to next item
    const currentIdx = items.findIndex((i) => i.id === selectedItemId)
    if (currentIdx < items.length - 1) {
      setSelectedItemId(items[currentIdx + 1].id)
    } else {
      setSelectedItemId('')
    }
  }

  const handleReject = async (reason: string, notes: string) => {
    await rejectMutation.mutateAsync({ itemId: selectedItemId, reason, notes })
    // Move to next item
    const currentIdx = items.findIndex((i) => i.id === selectedItemId)
    if (currentIdx < items.length - 1) {
      setSelectedItemId(items[currentIdx + 1].id)
    } else {
      setSelectedItemId('')
    }
  }

  const handleRequestChanges = async (changes: string[], notes: string) => {
    await revisionMutation.mutateAsync({
      itemId: selectedItemId,
      changes,
      notes,
    })
    // Move to next item
    const currentIdx = items.findIndex((i) => i.id === selectedItemId)
    if (currentIdx < items.length - 1) {
      setSelectedItemId(items[currentIdx + 1].id)
    } else {
      setSelectedItemId('')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#0F172A]">Review Inbox</h1>
        <p className="text-[#1E40AF] mt-2">
          Approve, reject, or request changes to submissions
        </p>
      </div>

      {/* Statistics */}
      {stats.data && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-2xl font-bold text-amber-600">
                {stats.data.pending || 0}
              </p>
              <p className="text-xs text-slate-600 mt-1">Pending</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {stats.data.approved || 0}
              </p>
              <p className="text-xs text-slate-600 mt-1">Approved</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-2xl font-bold text-red-600">
                {stats.data.rejected || 0}
              </p>
              <p className="text-xs text-slate-600 mt-1">Rejected</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-2xl font-bold text-blue-600">
                {stats.data.revision || 0}
              </p>
              <p className="text-xs text-slate-600 mt-1">Revision</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-2xl font-bold text-[#1E40AF]">
                {Math.round(stats.data.avgResolutionTime || 0)}h
              </p>
              <p className="text-xs text-slate-600 mt-1">Avg Time</p>
            </Card.Body>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card variant="outlined">
        <Card.Body>
          <div className="flex flex-wrap gap-2">
            {(['all', 'pending', 'approved', 'rejected', 'revision'] as const).map(
              (status) => (
                <button
                  key={status}
                  onClick={() => {
                    setFilterStatus(status)
                    setSelectedItemId('')
                  }}
                  className={`px-4 py-2 rounded-lg font-medium transition capitalize ${
                    filterStatus === status
                      ? 'bg-[#1E40AF] text-white'
                      : 'bg-[#E8EFFE] text-[#0F172A] hover:bg-[#3B82F6]'
                  }`}
                >
                  {status}
                </button>
              )
            )}
          </div>
        </Card.Body>
      </Card>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Queue List */}
        <div className="lg:col-span-1">
          <h3 className="text-lg font-bold text-[#0F172A] mb-3">
            Queue ({items.length})
          </h3>

          {queue.isLoading ? (
            <div className="space-y-3">
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
              <Skeleton className="h-32 w-full" />
            </div>
          ) : items.length === 0 ? (
            <Card variant="outlined">
              <Card.Body>
                <p className="text-center text-slate-600 py-8">No items in queue</p>
              </Card.Body>
            </Card>
          ) : (
            <div className="space-y-3 max-h-96 overflow-auto">
              {items.map((item) => (
                <ReviewCard
                  key={item.id}
                  item={item}
                  onSelect={handleSelectItem}
                  isSelected={selectedItemId === item.id}
                />
              ))}
            </div>
          )}
        </div>

        {/* Item Details */}
        <div className="lg:col-span-2">
          {!selectedItemId ? (
            <Card variant="outlined">
              <Card.Body>
                <div className="text-center py-12">
                  <p className="text-2xl mb-3">📋</p>
                  <p className="text-slate-600">Select an item to review</p>
                </div>
              </Card.Body>
            </Card>
          ) : selectedItem.isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-40 w-full" />
              <Skeleton className="h-24 w-full" />
            </div>
          ) : selectedItem.data ? (
            <div className="space-y-4">
              {/* Item Header */}
              <Card variant="outlined">
                <Card.Header>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h2 className="text-2xl font-bold text-[#0F172A]">
                        {selectedItem.data.title}
                      </h2>
                      <p className="text-sm text-slate-600 mt-1">
                        Submitted by{' '}
                        <strong>{selectedItem.data.creator.name}</strong> (
                        {selectedItem.data.creator.email})
                      </p>
                    </div>
                    <Badge
                      variant={
                        selectedItem.data.status === 'pending'
                          ? 'warning'
                          : selectedItem.data.status === 'approved'
                            ? 'success'
                            : 'error'
                      }
                    >
                      {selectedItem.data.status}
                    </Badge>
                  </div>
                </Card.Header>

                <Card.Body className="space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-slate-600 uppercase">Type</p>
                      <p className="font-bold text-[#0F172A] capitalize">
                        {selectedItem.data.type}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-600 uppercase">Priority</p>
                      <p className="font-bold text-[#0F172A] capitalize">
                        {selectedItem.data.priority}
                      </p>
                    </div>
                  </div>

                  {selectedItem.data.summary && (
                    <div>
                      <p className="text-xs text-slate-600 uppercase">Summary</p>
                      <p className="text-sm text-slate-700 mt-1">
                        {selectedItem.data.summary}
                      </p>
                    </div>
                  )}
                </Card.Body>
              </Card>

              {/* Content Preview */}
              {selectedItem.data.content && (
                <Card variant="outlined">
                  <Card.Header>
                    <h3 className="font-bold text-[#0F172A]">Content Preview</h3>
                  </Card.Header>

                  <Card.Body>
                    <div className="bg-slate-50 p-4 rounded-lg max-h-64 overflow-auto">
                      <p className="text-sm text-slate-700 whitespace-pre-wrap">
                        {selectedItem.data.content.substring(0, 500)}
                        {selectedItem.data.content.length > 500 ? '...' : ''}
                      </p>
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Metrics */}
              {selectedItem.data.metrics && (
                <Card variant="outlined">
                  <Card.Header>
                    <h3 className="font-bold text-[#0F172A]">Metrics</h3>
                  </Card.Header>

                  <Card.Body>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(selectedItem.data.metrics).map(
                        ([key, value]) => (
                          <div key={key}>
                            <p className="text-xs text-slate-600 uppercase">
                              {key.replace(/_/g, ' ')}
                            </p>
                            <p className="text-lg font-bold text-[#0F172A]">
                              {typeof value === 'number'
                                ? value.toFixed(2)
                                : String(value)}
                            </p>
                          </div>
                        )
                      )}
                    </div>
                  </Card.Body>
                </Card>
              )}

              {/* Decision Panel */}
              {selectedItem.data.status === 'pending' && (
                <ReviewDecision
                  itemId={selectedItemId}
                  onApprove={handleApprove}
                  onReject={handleReject}
                  onRequestChanges={handleRequestChanges}
                  isLoading={
                    approveMutation.isLoading ||
                    rejectMutation.isLoading ||
                    revisionMutation.isLoading
                  }
                />
              )}
            </div>
          ) : null}
        </div>
      </div>

      {/* Help */}
      <Card variant="default" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <p className="font-bold text-blue-800 mb-2">💡 Review Workflow</p>
          <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
            <li>Review submissions in your queue</li>
            <li>
              <strong>Approve:</strong> Accept the submission as-is
            </li>
            <li>
              <strong>Reject:</strong> Decline the submission with feedback
            </li>
            <li>
              <strong>Request Changes:</strong> Ask for specific revisions before approval
            </li>
            <li>Track progress through statistics dashboard</li>
          </ul>
        </Card.Body>
      </Card>
    </div>
  )
}
