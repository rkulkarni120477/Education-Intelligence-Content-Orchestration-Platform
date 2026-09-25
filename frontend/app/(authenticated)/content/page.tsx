'use client'

import React, { useState } from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { useContentAssets, useSearchContent, useApproveContent, useRejectContent, ContentAsset } from '@/lib/api/content'
import { SearchBar } from '@/components/Content/SearchBar'
import { UploadWidget } from '@/components/Content/UploadWidget'
import { LibraryGrid } from '@/components/Content/LibraryGrid'
import { AssetPreview } from '@/components/Content/AssetPreview'
import { Card } from '@/components/Common/Card'

export default function ContentLibraryPage() {
  const { user, isAuthenticated } = useAuthRequired()
  const [currentPage, setCurrentPage] = useState(1)
  const [filters, setFilters] = useState<{ status?: string; subject?: string; grade?: string }>({})
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAsset, setSelectedAsset] = useState<ContentAsset | null>(null)
  const [showPreview, setShowPreview] = useState(false)
  const [showUpload, setShowUpload] = useState(false)

  // API calls
  const listQuery = useContentAssets(currentPage, 20, filters)
  const searchQuery_ = useSearchContent(searchQuery)
  const approveMutation = useApproveContent()
  const rejectMutation = useRejectContent()

  // Determine which data to show
  const displayAssets = searchQuery ? (searchQuery_.data || []) : (listQuery.data?.items || [])
  const isLoading = searchQuery ? searchQuery_.isLoading : listQuery.isLoading
  const totalPages = searchQuery ? 1 : (listQuery.data?.pages || 1)

  if (!isAuthenticated) return null

  const handleApprove = async (assetId: string) => {
    try {
      await approveMutation.mutateAsync({ id: assetId })
      // Refresh data
      listQuery.refetch()
      setShowPreview(false)
    } catch (error: any) {
      console.error('Approve failed:', error.message)
    }
  }

  const handleReject = async (assetId: string) => {
    try {
      await rejectMutation.mutateAsync({ id: assetId, reason: 'Rejected by user' })
      // Refresh data
      listQuery.refetch()
      setShowPreview(false)
    } catch (error: any) {
      console.error('Reject failed:', error.message)
    }
  }

  const handleAssetClick = (asset: ContentAsset) => {
    setSelectedAsset(asset)
    setShowPreview(true)
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#0F172A]">Content Library</h1>
        <p className="text-[#1E40AF] mt-2">
          Manage your educational content, track processing status, and approve assets
        </p>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-4">
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="px-4 py-2 bg-[#1E40AF] text-white rounded-lg font-medium hover:bg-[#0F172A] transition"
        >
          {showUpload ? '✕ Hide Upload' : '+ Upload Content'}
        </button>
        <p className="text-sm text-slate-600 flex items-center">
          {displayAssets.length} assets found
        </p>
      </div>

      {/* Upload Widget */}
      {showUpload && (
        <UploadWidget
          onUploadComplete={(jobId) => {
            setShowUpload(false)
            listQuery.refetch()
          }}
          onError={(error) => {
            console.error('Upload error:', error)
          }}
        />
      )}

      {/* Search and Filters */}
      <SearchBar
        onSearch={(query) => {
          setSearchQuery(query)
          setCurrentPage(1)
        }}
        onFilter={(newFilters) => {
          setFilters(newFilters)
          setCurrentPage(1)
          setSearchQuery('') // Clear search when filtering
        }}
        isLoading={isLoading}
      />

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-3xl font-bold text-[#1E40AF]">
              {displayAssets.filter(a => a.status === 'published').length}
            </p>
            <p className="text-sm text-slate-600 mt-2">Published</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-3xl font-bold text-amber-600">
              {displayAssets.filter(a => a.status === 'uploaded' || a.status === 'extracted').length}
            </p>
            <p className="text-sm text-slate-600 mt-2">Processing</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-3xl font-bold text-orange-600">
              {displayAssets.filter(a => a.status === 'review_required').length}
            </p>
            <p className="text-sm text-slate-600 mt-2">Pending Review</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-3xl font-bold text-red-600">
              {displayAssets.filter(a => a.status === 'failed').length}
            </p>
            <p className="text-sm text-slate-600 mt-2">Failed</p>
          </Card.Body>
        </Card>
      </div>

      {/* Content Grid */}
      <div>
        <LibraryGrid
          assets={displayAssets}
          isLoading={isLoading}
          onAssetClick={handleAssetClick}
          onApprove={handleApprove}
          onReject={handleReject}
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      </div>

      {/* Asset Preview Modal */}
      <AssetPreview
        asset={selectedAsset}
        isOpen={showPreview}
        onClose={() => setShowPreview(false)}
        onApprove={() => selectedAsset && handleApprove(selectedAsset.id)}
        onReject={() => selectedAsset && handleReject(selectedAsset.id)}
        isApproving={approveMutation.isLoading}
        isRejecting={rejectMutation.isLoading}
      />
    </div>
  )
}
