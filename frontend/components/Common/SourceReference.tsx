'use client'

import React from 'react'

interface SourceReferenceProps {
  source: string
  page?: number
  timestamp?: string
  excerpt?: string
  className?: string
}

export const SourceReference: React.FC<SourceReferenceProps> = ({
  source,
  page,
  timestamp,
  excerpt,
  className = '',
}) => {
  return (
    <div className={`bg-slate-50 border-l-4 border-[#8B5A3C] p-3 rounded ${className}`}>
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-[#6B4423]">Source Reference</p>
          <p className="text-xs text-slate-600 mt-1">{source}</p>
        </div>
      </div>

      {/* Location Info */}
      <div className="flex gap-3 mt-2 text-xs text-slate-500 flex-wrap">
        {page && (
          <span className="px-2 py-1 bg-slate-200 rounded">
            📄 Page {page}
          </span>
        )}
        {timestamp && (
          <span className="px-2 py-1 bg-slate-200 rounded">
            ⏱️ {timestamp}
          </span>
        )}
      </div>

      {/* Excerpt */}
      {excerpt && (
        <div className="mt-3 pt-3 border-t border-slate-200">
          <p className="text-xs font-medium text-slate-600 mb-1">Excerpt:</p>
          <p className="text-sm text-slate-700 italic line-clamp-3">
            "{excerpt}"
          </p>
        </div>
      )}
    </div>
  )
}

SourceReference.displayName = 'SourceReference'
