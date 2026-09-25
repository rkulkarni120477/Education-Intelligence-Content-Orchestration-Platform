'use client'

import React from 'react'
import { ContentAsset } from '@/lib/api/content'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { StatusBadge } from '@/components/Common/Badge'

interface AssetPreviewProps {
  asset: ContentAsset | null
  isOpen: boolean
  onClose: () => void
  onApprove?: () => void
  onReject?: () => void
  isApproving?: boolean
  isRejecting?: boolean
}

export const AssetPreview: React.FC<AssetPreviewProps> = ({
  asset,
  isOpen,
  onClose,
  onApprove,
  onReject,
  isApproving = false,
  isRejecting = false,
}) => {
  if (!isOpen || !asset) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b-2 border-[#D2B48C] px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-[#6B4423]">{asset.title}</h2>
          <button
            onClick={onClose}
            className="text-2xl text-slate-500 hover:text-slate-700"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Status and Metadata */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-1">Status</p>
              <StatusBadge status={asset.status} />
            </div>

            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-1">File Type</p>
              <p className="text-slate-700">{asset.content_type}</p>
            </div>

            {asset.subject && (
              <div>
                <p className="text-sm font-medium text-[#6B4423] mb-1">Subject</p>
                <p className="text-slate-700">{asset.subject}</p>
              </div>
            )}

            {asset.grade && (
              <div>
                <p className="text-sm font-medium text-[#6B4423] mb-1">Grade</p>
                <p className="text-slate-700">Grade {asset.grade}</p>
              </div>
            )}

            {asset.file_size && (
              <div>
                <p className="text-sm font-medium text-[#6B4423] mb-1">File Size</p>
                <p className="text-slate-700">{(asset.file_size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            )}

            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-1">Version</p>
              <p className="text-slate-700">v{asset.version}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-1">Uploaded</p>
              <p className="text-slate-700 text-sm">{new Date(asset.created_at).toLocaleDateString()}</p>
            </div>

            {asset.created_by && (
              <div>
                <p className="text-sm font-medium text-[#6B4423] mb-1">Uploaded By</p>
                <p className="text-slate-700">{asset.created_by}</p>
              </div>
            )}
          </div>

          {/* Description */}
          {asset.description && (
            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-2">Description</p>
              <p className="text-slate-700 whitespace-pre-wrap">{asset.description}</p>
            </div>
          )}

          {/* Tags */}
          {asset.tags && asset.tags.length > 0 && (
            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-2">Tags</p>
              <div className="flex flex-wrap gap-2">
                {asset.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Extracted Text Preview */}
          {asset.extracted_text && (
            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-2">Extracted Text Preview</p>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 max-h-48 overflow-auto">
                <p className="text-sm text-slate-700 whitespace-pre-wrap">
                  {asset.extracted_text.substring(0, 500)}
                  {asset.extracted_text.length > 500 && '...'}
                </p>
              </div>
            </div>
          )}

          {/* Metadata */}
          {asset.metadata && Object.keys(asset.metadata).length > 0 && (
            <div>
              <p className="text-sm font-medium text-[#6B4423] mb-2">Additional Metadata</p>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-sm">
                {Object.entries(asset.metadata).map(([key, value]) => (
                  <div key={key} className="py-2 border-b border-slate-200 last:border-b-0">
                    <p className="font-medium text-slate-600">{key}</p>
                    <p className="text-slate-700">{String(value)}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {asset.status === 'failed' && (
            <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-medium">Processing Error</p>
              <p className="text-red-700 text-sm mt-1">
                This content failed to process. Please review and try again.
              </p>
            </div>
          )}
        </div>

        {/* Footer with Actions */}
        <div className="sticky bottom-0 bg-white border-t-2 border-[#D2B48C] px-6 py-4 flex gap-2 justify-end">
          {asset.status === 'review_required' && (
            <>
              {onApprove && (
                <Button
                  variant="success"
                  onClick={onApprove}
                  isLoading={isApproving}
                >
                  Approve
                </Button>
              )}
              {onReject && (
                <Button
                  variant="danger"
                  onClick={onReject}
                  isLoading={isRejecting}
                >
                  Reject
                </Button>
              )}
            </>
          )}

          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}

AssetPreview.displayName = 'AssetPreview'
