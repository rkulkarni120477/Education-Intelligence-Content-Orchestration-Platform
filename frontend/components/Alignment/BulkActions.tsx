'use client'

import React, { useState } from 'react'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Badge } from '@/components/Common/Badge'

interface BulkActionsProps {
  selectedCount: number
  selectedIds: string[]
  onApproveSelected: (notes?: string) => Promise<void>
  onRejectSelected: (reason?: string, notes?: string) => Promise<void>
  onDeferSelected: () => Promise<void>
  onClearSelection: () => void
  isLoading?: boolean
}

type ActionMode = 'choose' | 'approve' | 'reject' | 'defer'

export const BulkActions: React.FC<BulkActionsProps> = ({
  selectedCount,
  selectedIds,
  onApproveSelected,
  onRejectSelected,
  onDeferSelected,
  onClearSelection,
  isLoading = false,
}) => {
  const [mode, setMode] = useState<ActionMode>('choose')
  const [notes, setNotes] = useState('')
  const [reason, setReason] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  if (selectedCount === 0) return null

  const handleApprove = async () => {
    setIsSubmitting(true)
    try {
      await onApproveSelected(notes)
      setNotes('')
      setMode('choose')
      onClearSelection()
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReject = async () => {
    setIsSubmitting(true)
    try {
      await onRejectSelected(reason, notes)
      setNotes('')
      setReason('')
      setMode('choose')
      onClearSelection()
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDefer = async () => {
    setIsSubmitting(true)
    try {
      await onDeferSelected()
      setMode('choose')
      onClearSelection()
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card variant="outlined" className="border-[#8B5A3C] bg-[#FFF8F0]">
      <Card.Header>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">✓</span>
            <h3 className="font-bold text-[#6B4423]">Bulk Actions</h3>
            <Badge variant="info">{selectedCount} selected</Badge>
          </div>
          <button
            onClick={onClearSelection}
            className="text-sm text-slate-600 hover:text-slate-800"
          >
            Clear
          </button>
        </div>
      </Card.Header>

      <Card.Body>
        {mode === 'choose' && (
          <div className="grid grid-cols-3 gap-2">
            <Button
              variant="success"
              onClick={() => setMode('approve')}
              disabled={isLoading || isSubmitting}
              className="text-sm"
            >
              ✓ Approve All
            </Button>

            <Button
              variant="danger"
              onClick={() => setMode('reject')}
              disabled={isLoading || isSubmitting}
              className="text-sm"
            >
              ✗ Reject All
            </Button>

            <Button
              variant="secondary"
              onClick={() => setMode('defer')}
              disabled={isLoading || isSubmitting}
              className="text-sm"
            >
              ⏸ Defer All
            </Button>
          </div>
        )}

        {mode === 'approve' && (
          <div className="space-y-2">
            <textarea
              placeholder="Optional notes for all approved items..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white text-sm h-16 resize-none"
            />
            <div className="flex gap-2">
              <Button
                variant="success"
                onClick={handleApprove}
                isLoading={isSubmitting}
                className="flex-1 text-sm"
              >
                ✓ Approve {selectedCount}
              </Button>
              <Button
                variant="secondary"
                onClick={() => setMode('choose')}
                disabled={isSubmitting}
                className="flex-1 text-sm"
              >
                Back
              </Button>
            </div>
          </div>
        )}

        {mode === 'reject' && (
          <div className="space-y-2">
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white text-sm"
            >
              <option value="">Select reason...</option>
              <option value="quality">Quality issues</option>
              <option value="alignment">Poor alignment</option>
              <option value="incomplete">Incomplete</option>
              <option value="other">Other</option>
            </select>

            <textarea
              placeholder="Feedback for rejection..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-3 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white text-sm h-16 resize-none"
            />

            <div className="flex gap-2">
              <Button
                variant="danger"
                onClick={handleReject}
                isLoading={isSubmitting}
                disabled={!reason}
                className="flex-1 text-sm"
              >
                ✗ Reject {selectedCount}
              </Button>
              <Button
                variant="secondary"
                onClick={() => setMode('choose')}
                disabled={isSubmitting}
                className="flex-1 text-sm"
              >
                Back
              </Button>
            </div>
          </div>
        )}

        {mode === 'defer' && (
          <div className="space-y-2">
            <p className="text-sm text-slate-700">
              Defer {selectedCount} alignment{selectedCount !== 1 ? 's' : ''} for later review?
            </p>
            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={handleDefer}
                isLoading={isSubmitting}
                className="flex-1 text-sm"
              >
                ⏸ Defer {selectedCount}
              </Button>
              <Button
                variant="tertiary"
                onClick={() => setMode('choose')}
                disabled={isSubmitting}
                className="flex-1 text-sm"
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </Card.Body>
    </Card>
  )
}

BulkActions.displayName = 'BulkActions'
