'use client'

import React from 'react'
import { ContentAsset } from '@/lib/api/content'
import { Card } from '@/components/Common/Card'
import { StatusBadge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'
import { Button } from '@/components/Common/Button'

interface LibraryGridProps {
  assets: ContentAsset[]
  isLoading?: boolean
  onAssetClick: (asset: ContentAsset) => void
  onApprove?: (assetId: string) => void
  onReject?: (assetId: string) => void
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export const LibraryGrid: React.FC<LibraryGridProps> = ({
  assets,
  isLoading = false,
  onAssetClick,
  onApprove,
  onReject,
  currentPage,
  totalPages,
  onPageChange,
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-64 rounded-lg" />
        ))}
      </div>
    )
  }

  if (assets.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-[#8B5A3C] text-lg font-medium mb-2">No content found</p>
        <p className="text-slate-500">Upload content to get started</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {assets.map((asset) => (
          <Card
            key={asset.id}
            variant="outlined"
            className="cursor-pointer hover:shadow-md transition"
            onClick={() => onAssetClick(asset)}
          >
            <Card.Header>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-[#6B4423] truncate hover:text-[#8B5A3C]">
                    {asset.title}
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    {asset.content_type} • {asset.file_size ? `${(asset.file_size / 1024 / 1024).toFixed(1)}MB` : 'N/A'}
                  </p>
                </div>
              </div>
            </Card.Header>

            <Card.Body className="space-y-3">
              {/* Status Badge */}
              <div>
                <StatusBadge status={asset.status} />
              </div>

              {/* Metadata */}
              <div className="space-y-2 text-sm">
                {asset.subject && (
                  <p>
                    <span className="font-medium text-[#6B4423]">Subject:</span>{' '}
                    <span className="text-slate-600">{asset.subject}</span>
                  </p>
                )}
                {asset.grade && (
                  <p>
                    <span className="font-medium text-[#6B4423]">Grade:</span>{' '}
                    <span className="text-slate-600">{asset.grade}</span>
                  </p>
                )}
              </div>

              {/* Description */}
              {asset.description && (
                <p className="text-sm text-slate-600 line-clamp-2">
                  {asset.description}
                </p>
              )}

              {/* Tags */}
              {asset.tags && asset.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {asset.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-1 bg-slate-100 text-slate-700 rounded"
                    >
                      {tag}
                    </span>
                  ))}
                  {asset.tags.length > 3 && (
                    <span className="text-xs px-2 py-1 text-slate-500">
                      +{asset.tags.length - 3} more
                    </span>
                  )}
                </div>
              )}

              {/* Progress for processing items */}
              {(asset.status === 'processing' || asset.status === 'extracting') && asset.upload_progress !== undefined && (
                <div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-[#8B5A3C] h-2 rounded-full transition-all"
                      style={{ width: `${asset.upload_progress}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{asset.upload_progress}% processed</p>
                </div>
              )}

              {/* Error message */}
              {asset.status === 'failed' && (
                <p className="text-xs text-red-600 font-medium">Processing failed</p>
              )}
            </Card.Body>

            {/* Actions for review_required items */}
            {asset.status === 'review_required' && (onApprove || onReject) && (
              <Card.Footer>
                <div className="flex gap-2">
                  {onApprove && (
                    <Button
                      type="button"
                      variant="success"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        onApprove(asset.id)
                      }}
                    >
                      Approve
                    </Button>
                  )}
                  {onReject && (
                    <Button
                      type="button"
                      variant="danger"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        onReject(asset.id)
                      }}
                    >
                      Reject
                    </Button>
                  )}
                </div>
              </Card.Footer>
            )}
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <Button
            variant="secondary"
            size="sm"
            disabled={currentPage === 1}
            onClick={() => onPageChange(currentPage - 1)}
          >
            Previous
          </Button>

          <div className="flex gap-1">
            {Array.from({ length: Math.min(5, totalPages) }).map((_, i) => {
              const pageNum = Math.max(1, currentPage - 2) + i
              if (pageNum > totalPages) return null

              return (
                <Button
                  key={pageNum}
                  variant={pageNum === currentPage ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => onPageChange(pageNum)}
                >
                  {pageNum}
                </Button>
              )
            })}
          </div>

          <Button
            variant="secondary"
            size="sm"
            disabled={currentPage === totalPages}
            onClick={() => onPageChange(currentPage + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}

LibraryGrid.displayName = 'LibraryGrid'
