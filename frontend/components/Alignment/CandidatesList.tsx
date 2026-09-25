'use client'

import React from 'react'
import { Alignment } from '@/lib/api/alignments'
import { Card } from '@/components/Common/Card'
import { ConfidenceBadge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

interface CandidatesListProps {
  candidates: Alignment[]
  selectedId?: string
  onSelect: (alignment: Alignment) => void
  isLoading?: boolean
}

export const CandidatesList: React.FC<CandidatesListProps> = ({
  candidates,
  selectedId,
  onSelect,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-24 rounded-lg" />
        ))}
      </div>
    )
  }

  if (candidates.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <p>No candidate alignments</p>
      </div>
    )
  }

  // Sort by confidence (highest first)
  const sorted = [...candidates].sort((a, b) => b.confidence - a.confidence)

  return (
    <div className="space-y-2">
      {sorted.map((alignment, index) => {
        const isSelected = selectedId === alignment.id
        const confidencePercent = Math.round(alignment.confidence * 100)

        return (
          <button
            key={alignment.id}
            onClick={() => onSelect(alignment)}
            className={`
              w-full p-4 rounded-lg border-2 transition text-left
              ${
                isSelected
                  ? 'border-[#1E40AF] bg-[#FFFFFF]'
                  : 'border-[#3B82F6] hover:border-[#1E40AF] hover:bg-[#FFFFFF]'
              }
            `}
          >
            {/* Rank */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <div className="flex-shrink-0 w-6 h-6 bg-[#1E40AF] text-white rounded-full flex items-center justify-center text-sm font-bold">
                  {index + 1}
                </div>
                <div>
                  <p className="font-bold text-[#0F172A]">
                    {alignment.target_type === 'standard' ? 'Standard' : 'Objective'}
                  </p>
                  <p className="text-xs text-slate-500">
                    ID: {alignment.standard_id || alignment.objective_id}
                  </p>
                </div>
              </div>
              <ConfidenceBadge confidence={alignment.confidence} />
            </div>

            {/* Score breakdown */}
            <div className="ml-8 space-y-1">
              {/* Confidence meter */}
              <div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      confidencePercent >= 80
                        ? 'bg-green-500'
                        : confidencePercent >= 60
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                    }`}
                    style={{ width: `${confidencePercent}%` }}
                  ></div>
                </div>
              </div>

              {/* Status and alignment info */}
              <div className="flex gap-2 text-xs">
                <span className="px-2 py-1 bg-slate-100 rounded text-slate-600">
                  {alignment.status === 'candidate' ? '🔍 Candidate' : alignment.status}
                </span>
                {alignment.evidence && alignment.evidence.length > 0 && (
                  <span className="px-2 py-1 bg-blue-100 rounded text-blue-700">
                    📎 {alignment.evidence.length} evidence
                  </span>
                )}
              </div>
            </div>
          </button>
        )
      })}
    </div>
  )
}

CandidatesList.displayName = 'CandidatesList'
