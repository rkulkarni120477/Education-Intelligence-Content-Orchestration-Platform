'use client'

import React, { useState } from 'react'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'

interface ReviewDecisionProps {
  itemId: string
  onApprove: (notes: string) => Promise<void>
  onReject: (reason: string, notes: string) => Promise<void>
  onRequestChanges: (changes: string[], notes: string) => Promise<void>
  isLoading?: boolean
}

type DecisionMode = 'choose' | 'approve' | 'reject' | 'changes'

export const ReviewDecision: React.FC<ReviewDecisionProps> = ({
  itemId,
  onApprove,
  onReject,
  onRequestChanges,
  isLoading = false,
}) => {
  const [mode, setMode] = useState<DecisionMode>('choose')
  const [notes, setNotes] = useState('')
  const [reason, setReason] = useState('')
  const [changes, setChanges] = useState([''])
  const [feedback, setFeedback] = useState<'success' | 'error' | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleApprove = async () => {
    setIsSubmitting(true)
    try {
      await onApprove(notes)
      setFeedback('success')
      setTimeout(() => {
        setFeedback(null)
        setMode('choose')
        setNotes('')
      }, 2000)
    } catch (error) {
      setFeedback('error')
      setTimeout(() => setFeedback(null), 3000)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleReject = async () => {
    setIsSubmitting(true)
    try {
      await onReject(reason, notes)
      setFeedback('success')
      setTimeout(() => {
        setFeedback(null)
        setMode('choose')
        setNotes('')
        setReason('')
      }, 2000)
    } catch (error) {
      setFeedback('error')
      setTimeout(() => setFeedback(null), 3000)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRequestChanges = async () => {
    setIsSubmitting(true)
    try {
      await onRequestChanges(changes.filter((c) => c.trim()), notes)
      setFeedback('success')
      setTimeout(() => {
        setFeedback(null)
        setMode('choose')
        setNotes('')
        setChanges([''])
      }, 2000)
    } catch (error) {
      setFeedback('error')
      setTimeout(() => setFeedback(null), 3000)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card variant="outlined">
      <Card.Header>
        <h3 className="text-lg font-bold text-[#6B4423]">Review Decision</h3>
        <p className="text-sm text-slate-600 mt-1">Make your decision on this submission</p>
      </Card.Header>

      <Card.Body className="space-y-4">
        {/* Feedback Message */}
        {feedback === 'success' && (
          <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded">
            <p className="text-sm text-green-800">✓ Decision saved successfully</p>
          </div>
        )}

        {feedback === 'error' && (
          <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded">
            <p className="text-sm text-red-800">✗ Failed to save decision. Please try again.</p>
          </div>
        )}

        {mode === 'choose' && (
          /* Decision Selection */
          <div className="space-y-2">
            <Button
              variant="success"
              onClick={() => setMode('approve')}
              disabled={isLoading || isSubmitting}
              className="w-full"
            >
              ✓ Approve Submission
            </Button>

            <Button
              variant="danger"
              onClick={() => setMode('reject')}
              disabled={isLoading || isSubmitting}
              className="w-full"
            >
              ✗ Reject Submission
            </Button>

            <Button
              variant="secondary"
              onClick={() => setMode('changes')}
              disabled={isLoading || isSubmitting}
              className="w-full"
            >
              📝 Request Changes
            </Button>
          </div>
        )}

        {mode === 'approve' && (
          /* Approve Form */
          <div className="space-y-3">
            <textarea
              placeholder="Optional approval notes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white h-24 resize-none"
            />

            <div className="flex gap-2">
              <Button
                variant="primary"
                onClick={handleApprove}
                isLoading={isSubmitting}
                className="flex-1"
              >
                ✓ Approve
              </Button>
              <Button
                variant="secondary"
                onClick={() => setMode('choose')}
                disabled={isSubmitting}
                className="flex-1"
              >
                Back
              </Button>
            </div>
          </div>
        )}

        {mode === 'reject' && (
          /* Reject Form */
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">
                Rejection Reason *
              </label>
              <select
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
              >
                <option value="">Select a reason...</option>
                <option value="quality">Quality issues</option>
                <option value="incomplete">Incomplete content</option>
                <option value="alignment">Misaligned with standards</option>
                <option value="accessibility">Accessibility concerns</option>
                <option value="other">Other</option>
              </select>
            </div>

            <textarea
              placeholder="Detailed feedback on why this is being rejected..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white h-24 resize-none"
            />

            <div className="flex gap-2">
              <Button
                variant="danger"
                onClick={handleReject}
                isLoading={isSubmitting}
                disabled={!reason}
                className="flex-1"
              >
                ✗ Reject
              </Button>
              <Button
                variant="secondary"
                onClick={() => setMode('choose')}
                disabled={isSubmitting}
                className="flex-1"
              >
                Back
              </Button>
            </div>
          </div>
        )}

        {mode === 'changes' && (
          /* Request Changes Form */
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">
                Required Changes
              </label>
              <div className="space-y-2">
                {changes.map((change, idx) => (
                  <div key={idx} className="flex gap-2">
                    <input
                      type="text"
                      placeholder={`Change ${idx + 1}...`}
                      value={change}
                      onChange={(e) => {
                        const newChanges = [...changes]
                        newChanges[idx] = e.target.value
                        setChanges(newChanges)
                      }}
                      className="flex-1 px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
                    />
                    {changes.length > 1 && (
                      <button
                        onClick={() => setChanges(changes.filter((_, i) => i !== idx))}
                        className="px-3 py-2 text-red-600 hover:text-red-800 font-bold"
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={() => setChanges([...changes, ''])}
                className="mt-2 text-sm text-[#8B5A3C] hover:underline font-medium"
              >
                + Add another change
              </button>
            </div>

            <textarea
              placeholder="Additional context or guidance for making changes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white h-20 resize-none"
            />

            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={handleRequestChanges}
                isLoading={isSubmitting}
                disabled={!changes.some((c) => c.trim())}
                className="flex-1"
              >
                📝 Request Changes
              </Button>
              <Button
                variant="tertiary"
                onClick={() => setMode('choose')}
                disabled={isSubmitting}
                className="flex-1"
              >
                Back
              </Button>
            </div>
          </div>
        )}
      </Card.Body>

      <Card.Footer>
        <p className="text-xs text-slate-600">
          {mode === 'choose'
            ? 'Choose an action to proceed with your review'
            : 'Fill in the details and submit your decision'}
        </p>
      </Card.Footer>
    </Card>
  )
}

ReviewDecision.displayName = 'ReviewDecision'
