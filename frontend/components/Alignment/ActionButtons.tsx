'use client'

import React, { useState } from 'react'
import { Button } from '@/components/Common/Button'
import { Card } from '@/components/Common/Card'

interface ActionButtonsProps {
  alignmentId: string
  isLoading?: boolean
  onApprove: () => Promise<void>
  onReject: () => Promise<void>
  onDefer: () => Promise<void>
  onEdit: () => void
}

export const ActionButtons: React.FC<ActionButtonsProps> = ({
  alignmentId,
  isLoading = false,
  onApprove,
  onReject,
  onDefer,
  onEdit,
}) => {
  const [approveLoading, setApproveLoading] = useState(false)
  const [rejectLoading, setRejectLoading] = useState(false)
  const [deferLoading, setDeferLoading] = useState(false)
  const [feedback, setFeedback] = useState<'success' | 'error' | null>(null)

  const handleApprove = async () => {
    setApproveLoading(true)
    try {
      await onApprove()
      setFeedback('success')
      setTimeout(() => setFeedback(null), 3000)
    } catch (error) {
      setFeedback('error')
      setTimeout(() => setFeedback(null), 3000)
    } finally {
      setApproveLoading(false)
    }
  }

  const handleReject = async () => {
    setRejectLoading(true)
    try {
      await onReject()
      setFeedback('success')
      setTimeout(() => setFeedback(null), 3000)
    } catch (error) {
      setFeedback('error')
      setTimeout(() => setFeedback(null), 3000)
    } finally {
      setRejectLoading(false)
    }
  }

  const handleDefer = async () => {
    setDeferLoading(true)
    try {
      await onDefer()
      setFeedback('success')
      setTimeout(() => setFeedback(null), 3000)
    } catch (error) {
      setFeedback('error')
      setTimeout(() => setFeedback(null), 3000)
    } finally {
      setDeferLoading(false)
    }
  }

  return (
    <Card variant="outlined">
      <Card.Header>
        <h3 className="text-lg font-bold text-[#6B4423]">Your Decision</h3>
        <p className="text-sm text-slate-600 mt-1">Accept or reject this alignment</p>
      </Card.Header>

      <Card.Body className="space-y-3">
        {/* Feedback Message */}
        {feedback === 'success' && (
          <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded">
            <p className="text-sm text-green-800">✓ Alignment decision saved successfully</p>
          </div>
        )}

        {feedback === 'error' && (
          <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded">
            <p className="text-sm text-red-800">✗ Failed to save decision. Please try again.</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="space-y-2">
          <Button
            variant="success"
            onClick={handleApprove}
            isLoading={approveLoading}
            disabled={isLoading || rejectLoading || deferLoading}
            className="w-full"
          >
            ✓ Approve Alignment
          </Button>

          <Button
            variant="danger"
            onClick={handleReject}
            isLoading={rejectLoading}
            disabled={isLoading || approveLoading || deferLoading}
            className="w-full"
          >
            ✗ Reject Alignment
          </Button>

          <Button
            variant="secondary"
            onClick={handleDefer}
            isLoading={deferLoading}
            disabled={isLoading || approveLoading || rejectLoading}
            className="w-full"
          >
            ⏸ Defer Decision
          </Button>
        </div>

        {/* Edit Button */}
        <Button
          variant="tertiary"
          onClick={onEdit}
          disabled={isLoading || approveLoading || rejectLoading || deferLoading}
          className="w-full"
        >
          ✎ Edit Alignment
        </Button>
      </Card.Body>

      <Card.Footer>
        <div className="space-y-2 text-sm">
          <p className="font-medium text-[#6B4423]">What each action means:</p>
          <ul className="space-y-1 text-slate-600 text-xs">
            <li><strong>Approve:</strong> Confirms this is a valid alignment. Content will be marked as aligned.</li>
            <li><strong>Reject:</strong> This is not a valid alignment. Content will not be aligned to this standard.</li>
            <li><strong>Defer:</strong> Postpone the decision. You can come back to it later.</li>
          </ul>
        </div>
      </Card.Footer>
    </Card>
  )
}

ActionButtons.displayName = 'ActionButtons'
