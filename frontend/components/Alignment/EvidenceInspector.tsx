'use client'

import React from 'react'
import { Alignment } from '@/lib/api/alignments'
import { Card } from '@/components/Common/Card'
import { SourceReference } from '@/components/Common/SourceReference'
import { ConfidenceBadge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

interface EvidenceItem {
  source?: string
  page?: number
  text?: string
}

interface EvidenceInspectorProps {
  alignment: Alignment | null
  isLoading?: boolean
}

export const EvidenceInspector: React.FC<EvidenceInspectorProps> = ({
  alignment,
  isLoading = false,
}) => {
  if (!alignment) {
    return (
      <Card variant="outlined" className="h-full">
        <Card.Body>
          <p className="text-center text-slate-500">Select a candidate to view evidence</p>
        </Card.Body>
      </Card>
    )
  }

  if (isLoading) {
    return (
      <Card variant="outlined" className="h-full space-y-4">
        <Skeleton className="h-6 w-1/2" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-32 w-full" />
      </Card>
    )
  }

  const confidencePercent = Math.round(alignment.confidence * 100)

  return (
    <Card variant="outlined" className="h-full overflow-auto">
      <Card.Header>
        <div className="flex items-start justify-between gap-2">
          <div>
            <h3 className="text-lg font-bold text-[#0F172A]">Evidence & Rationale</h3>
            <p className="text-sm text-slate-500 mt-1">
              Why this {alignment.target_type === 'standard' ? 'standard' : 'objective'} matches
            </p>
          </div>
          <ConfidenceBadge confidence={alignment.confidence} />
        </div>
      </Card.Header>

      <Card.Body className="space-y-6">
        {/* Confidence Explanation */}
        <div>
          <h4 className="text-sm font-bold text-[#0F172A] mb-2">Match Confidence</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-700">Confidence Score</span>
              <span className="text-lg font-bold text-[#1E40AF]">{confidencePercent}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all ${
                  confidencePercent >= 80
                    ? 'bg-green-500'
                    : confidencePercent >= 60
                      ? 'bg-amber-500'
                      : 'bg-red-500'
                }`}
                style={{ width: `${confidencePercent}%` }}
              ></div>
            </div>
            <p className="text-xs text-slate-500">
              {confidencePercent >= 80
                ? 'Strong match based on content analysis'
                : confidencePercent >= 60
                  ? 'Moderate match, review evidence carefully'
                  : 'Weak match, consider alternatives'}
            </p>
          </div>
        </div>

        {/* Evidence Section */}
        {alignment.evidence && alignment.evidence.length > 0 ? (
          <div>
            <h4 className="text-sm font-bold text-[#0F172A] mb-3">
              Supporting Evidence ({alignment.evidence.length} items)
            </h4>
            <div className="space-y-3">
              {alignment.evidence.map((evidence, idx) => {
                // Handle both string and object evidence formats
                const evidenceItem = typeof evidence === 'string'
                  ? { source: evidence, text: evidence }
                  : (evidence as EvidenceItem)

                return (
                  <div key={idx} className="bg-slate-50 rounded border border-slate-200 p-3">
                    <p className="text-xs font-semibold text-slate-600 mb-1">
                      {evidenceItem.source || 'Source'}
                      {evidenceItem.page && ` (p. ${evidenceItem.page})`}
                    </p>
                    <p className="text-sm text-slate-800">
                      {evidenceItem.text || JSON.stringify(evidence)}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>
        ) : (
          <div className="bg-amber-50 border-l-4 border-amber-400 p-3 rounded">
            <p className="text-sm text-amber-800">
              ⚠️ No detailed evidence available. Review the content and standard carefully.
            </p>
          </div>
        )}

        {/* Alignment Details */}
        <div>
          <h4 className="text-sm font-bold text-[#0F172A] mb-3">Alignment Details</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between py-2 border-b border-slate-200">
              <span className="text-slate-600">Alignment Status</span>
              <span className="font-medium text-[#0F172A] capitalize">
                {alignment.status}
              </span>
            </div>

            <div className="flex justify-between py-2 border-b border-slate-200">
              <span className="text-slate-600">Created</span>
              <span className="font-medium text-slate-700">
                {new Date(alignment.created_at).toLocaleDateString()}
              </span>
            </div>

            {alignment.reviewed_at && (
              <div className="flex justify-between py-2 border-b border-slate-200">
                <span className="text-slate-600">Reviewed</span>
                <span className="font-medium text-slate-700">
                  {new Date(alignment.reviewed_at).toLocaleDateString()}
                </span>
              </div>
            )}

            <div className="flex justify-between py-2">
              <span className="text-slate-600">Alignment ID</span>
              <code className="text-xs bg-slate-100 px-2 py-1 rounded">
                {alignment.id.substring(0, 8)}...
              </code>
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
          <p className="text-sm text-blue-800">
            💡 <strong>Tip:</strong> Use the evidence above to make your decision. High confidence (80%+)
            alignments are recommended for approval.
          </p>
        </div>
      </Card.Body>
    </Card>
  )
}

EvidenceInspector.displayName = 'EvidenceInspector'
