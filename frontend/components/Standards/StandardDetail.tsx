'use client'

import React from 'react'
import { Standard, StandardFramework } from '@/lib/api/standards'
import { Card } from '@/components/Common/Card'
import { Badge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

interface StandardDetailProps {
  standard: Standard | null
  framework: StandardFramework | null
  isLoading?: boolean
  onAlignClick?: (standardId: string) => void
}

export const StandardDetail: React.FC<StandardDetailProps> = ({
  standard,
  framework,
  isLoading = false,
  onAlignClick,
}) => {
  if (!standard) {
    return (
      <Card variant="outlined" className="h-full">
        <Card.Body>
          <p className="text-center text-slate-500">Select a standard to view details</p>
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
        <Skeleton className="h-4 w-2/3" />
      </Card>
    )
  }

  return (
    <Card variant="outlined" className="h-full overflow-auto">
      <Card.Header>
        <h3 className="text-lg font-bold text-[#6B4423]">{standard.code}</h3>
        {framework && (
          <p className="text-sm text-slate-500 mt-1">
            {framework.name} {framework.version && `v${framework.version}`}
          </p>
        )}
      </Card.Header>

      <Card.Body className="space-y-6">
        {/* Main Description */}
        <div>
          <h4 className="text-sm font-bold text-[#6B4423] mb-2">Description</h4>
          <p className="text-slate-700 leading-relaxed">{standard.description}</p>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-4">
          {standard.grade && (
            <div>
              <p className="text-xs font-medium text-[#6B4423] mb-1">Grade</p>
              <p className="text-slate-700">Grade {standard.grade}</p>
            </div>
          )}

          {standard.subject && (
            <div>
              <p className="text-xs font-medium text-[#6B4423] mb-1">Subject</p>
              <p className="text-slate-700">{standard.subject}</p>
            </div>
          )}

          {standard.domain && (
            <div>
              <p className="text-xs font-medium text-[#6B4423] mb-1">Domain</p>
              <p className="text-slate-700">{standard.domain}</p>
            </div>
          )}

          {standard.strand && (
            <div>
              <p className="text-xs font-medium text-[#6B4423] mb-1">Strand</p>
              <p className="text-slate-700">{standard.strand}</p>
            </div>
          )}

          {standard.version && (
            <div>
              <p className="text-xs font-medium text-[#6B4423] mb-1">Version</p>
              <p className="text-slate-700">{standard.version}</p>
            </div>
          )}

          <div>
            <p className="text-xs font-medium text-[#6B4423] mb-1">Created</p>
            <p className="text-slate-700 text-sm">
              {new Date(standard.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Structure Info */}
        {standard.parent_id && (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
            <p className="text-sm text-blue-800">
              This is a sub-standard within a larger standard hierarchy.
            </p>
          </div>
        )}

        {/* Actions */}
        {onAlignClick && (
          <div className="pt-4 border-t border-[#D2B48C]">
            <button
              onClick={() => onAlignClick(standard.id)}
              className="w-full px-4 py-2 bg-[#8B5A3C] text-white rounded-lg font-medium hover:bg-[#6B4423] transition"
            >
              Align Content to This Standard
            </button>
          </div>
        )}
      </Card.Body>
    </Card>
  )
}

StandardDetail.displayName = 'StandardDetail'
