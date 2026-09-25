'use client'

import React from 'react'
import { Card } from '@/components/Common/Card'
import { Badge } from '@/components/Common/Badge'
import { Button } from '@/components/Common/Button'
import type { ReviewItem } from '@/lib/api/review'

interface ReviewCardProps {
  item: ReviewItem
  onSelect: (item: ReviewItem) => void
  isSelected?: boolean
}

const typeEmoji = {
  lesson: '📖',
  assessment: '📝',
  activity: '🎬',
  content: '📄',
}

const statusConfig = {
  pending: { label: 'Pending', color: 'warning' },
  approved: { label: 'Approved', color: 'success' },
  rejected: { label: 'Rejected', color: 'danger' },
  revision: { label: 'Revision', color: 'warning' },
} as const

const priorityConfig = {
  low: { color: 'info', bg: 'bg-blue-100' },
  medium: { color: 'warning', bg: 'bg-amber-100' },
  high: { color: 'danger', bg: 'bg-red-100' },
} as const

export const ReviewCard: React.FC<ReviewCardProps> = ({
  item,
  onSelect,
  isSelected = false,
}) => {
  const submittedDate = new Date(item.submittedAt)
  const daysAgo = Math.floor(
    (Date.now() - submittedDate.getTime()) / (1000 * 60 * 60 * 24)
  )

  return (
    <Card
      variant="outlined"
      className={`cursor-pointer transition hover:bg-[#FFF8F0] ${
        isSelected ? 'ring-2 ring-[#8B5A3C] bg-[#FFF8F0]' : ''
      }`}
      onClick={() => onSelect(item)}
    >
      <Card.Body>
        <div className="flex items-start justify-between gap-4">
          {/* Left: Item Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start gap-3">
              <span className="text-2xl flex-shrink-0">
                {typeEmoji[item.type]}
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="text-lg font-bold text-[#6B4423] truncate">
                  {item.title}
                </h3>
                <p className="text-sm text-slate-600 mt-1">
                  Submitted by{' '}
                  <strong>{item.creator.name}</strong>{' '}
                  {daysAgo === 0 ? 'today' : `${daysAgo}d ago`}
                </p>
              </div>
            </div>

            {/* Badges */}
            <div className="flex items-center gap-2 flex-wrap mt-3">
              <Badge
                variant={statusConfig[item.status].color}
              >
                {statusConfig[item.status].label}
              </Badge>
              <span
                className={`px-2 py-1 rounded text-xs font-medium capitalize ${
                  priorityConfig[item.priority].bg
                }`}
              >
                {item.priority} priority
              </span>
              {item.type && (
                <span className="text-xs text-slate-600 bg-slate-100 px-2 py-1 rounded">
                  {item.type}
                </span>
              )}
            </div>

            {/* Summary */}
            {item.summary && (
              <p className="text-sm text-slate-700 mt-3 line-clamp-2">
                {item.summary}
              </p>
            )}
          </div>

          {/* Right: Action Button */}
          <div className="flex-shrink-0">
            <Button
              variant="tertiary"
              onClick={(e) => {
                e.stopPropagation()
                onSelect(item)
              }}
            >
              →
            </Button>
          </div>
        </div>
      </Card.Body>
    </Card>
  )
}

ReviewCard.displayName = 'ReviewCard'
