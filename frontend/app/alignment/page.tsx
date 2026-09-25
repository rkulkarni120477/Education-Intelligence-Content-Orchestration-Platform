'use client'

import React, { useState, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import {
  useCandidateAlignments,
  useApproveAlignment,
  useRejectAlignment,
  Alignment,
} from '@/lib/api/alignments'
import { CandidatesList } from '@/components/Alignment/CandidatesList'
import { EvidenceInspector } from '@/components/Alignment/EvidenceInspector'
import { ActionButtons } from '@/components/Alignment/ActionButtons'
import { Card } from '@/components/Common/Card'
import { Skeleton } from '@/components/Common/Skeleton'

export default function AlignmentWorkspacePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isAuthenticated } = useAuthRequired()

  // Get context from URL params
  const contentId = searchParams.get('content_id') || ''
  const objectiveId = searchParams.get('objective_id') || ''
  const standardId = searchParams.get('standard_id') || ''
  const frameworkId = searchParams.get('framework_id') || ''

  const [selectedAlignmentId, setSelectedAlignmentId] = useState<string>('')

  // Fetch candidate alignments
  const candidatesQuery = useCandidateAlignments(contentId || standardId, frameworkId)
  const approveMutation = useApproveAlignment()
  const rejectMutation = useRejectAlignment()

  if (!isAuthenticated) return null

  const candidates = candidatesQuery.data || []
  const selectedAlignment = candidates.find((a) => a.id === selectedAlignmentId) || candidates[0]

  const handleSelectAlignment = (alignment: Alignment) => {
    setSelectedAlignmentId(alignment.id)
  }

  const handleApprove = async () => {
    if (!selectedAlignment) return
    try {
      await approveMutation.mutateAsync({ id: selectedAlignment.id })
      // Refresh candidates
      candidatesQuery.refetch()
      // Move to next candidate
      const currentIdx = candidates.findIndex((a) => a.id === selectedAlignmentId)
      if (currentIdx < candidates.length - 1) {
        setSelectedAlignmentId(candidates[currentIdx + 1].id)
      }
    } catch (error) {
      console.error('Approve failed:', error)
    }
  }

  const handleReject = async () => {
    if (!selectedAlignment) return
    try {
      await rejectMutation.mutateAsync({ id: selectedAlignment.id, reason: 'Rejected by reviewer' })
      // Refresh candidates
      candidatesQuery.refetch()
      // Move to next candidate
      const currentIdx = candidates.findIndex((a) => a.id === selectedAlignmentId)
      if (currentIdx < candidates.length - 1) {
        setSelectedAlignmentId(candidates[currentIdx + 1].id)
      }
    } catch (error) {
      console.error('Reject failed:', error)
    }
  }

  const handleDefer = async () => {
    // Move to next candidate
    const currentIdx = candidates.findIndex((a) => a.id === selectedAlignmentId)
    if (currentIdx < candidates.length - 1) {
      setSelectedAlignmentId(candidates[currentIdx + 1].id)
    }
  }

  const handleEdit = () => {
    // Open edit modal/page
    console.log('Edit alignment:', selectedAlignmentId)
  }

  // Statistics
  const approved = candidates.filter((a) => a.status === 'approved').length
  const rejected = candidates.filter((a) => a.status === 'rejected').length
  const pending = candidates.filter((a) => a.status === 'candidate').length
  const avgConfidence = candidates.length > 0
    ? Math.round((candidates.reduce((sum, a) => sum + a.confidence, 0) / candidates.length) * 100)
    : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#6B4423]">Alignment Workspace</h1>
        <p className="text-[#8B5A3C] mt-2">
          Review and approve candidate standard alignments based on evidence
        </p>
      </div>

      {/* Context Information */}
      {(contentId || standardId) && (
        <Card variant="outlined" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <p className="text-sm text-blue-800">
              {contentId && '📄 '}Reviewing alignments for:{' '}
              <strong>{contentId || standardId}</strong>
            </p>
          </Card.Body>
        </Card>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-[#8B5A3C]">{candidates.length}</p>
            <p className="text-xs text-slate-600 mt-1">Candidates</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-green-600">{approved}</p>
            <p className="text-xs text-slate-600 mt-1">Approved</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-red-600">{rejected}</p>
            <p className="text-xs text-slate-600 mt-1">Rejected</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-amber-600">{pending}</p>
            <p className="text-xs text-slate-600 mt-1">Pending</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-[#8B5A3C]">{avgConfidence}%</p>
            <p className="text-xs text-slate-600 mt-1">Avg Confidence</p>
          </Card.Body>
        </Card>
      </div>

      {/* Main Workspace */}
      {candidatesQuery.isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <Skeleton className="lg:col-span-1 h-96 rounded-lg" />
          <Skeleton className="lg:col-span-2 h-96 rounded-lg" />
          <Skeleton className="lg:col-span-1 h-96 rounded-lg" />
        </div>
      ) : candidates.length === 0 ? (
        <Card variant="outlined">
          <Card.Body>
            <p className="text-center text-slate-600 py-12">
              No candidate alignments found
            </p>
          </Card.Body>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Candidates List */}
          <div className="lg:col-span-1">
            <h3 className="text-lg font-bold text-[#6B4423] mb-3">Candidates</h3>
            <div className="max-h-96 overflow-auto">
              <CandidatesList
                candidates={candidates}
                selectedId={selectedAlignmentId}
                onSelect={handleSelectAlignment}
                isLoading={candidatesQuery.isLoading}
              />
            </div>
          </div>

          {/* Evidence Inspector */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-bold text-[#6B4423] mb-3">Evidence</h3>
            <div className="max-h-96 overflow-auto">
              <EvidenceInspector
                alignment={selectedAlignment || null}
                isLoading={candidatesQuery.isLoading}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="lg:col-span-1">
            <h3 className="text-lg font-bold text-[#6B4423] mb-3">Decision</h3>
            <ActionButtons
              alignmentId={selectedAlignment?.id || ''}
              isLoading={approveMutation.isLoading || rejectMutation.isLoading}
              onApprove={handleApprove}
              onReject={handleReject}
              onDefer={handleDefer}
              onEdit={handleEdit}
            />
          </div>
        </div>
      )}

      {/* Workflow Tips */}
      <Card variant="default" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <p className="font-bold text-blue-800 mb-2">💡 Alignment Review Workflow</p>
          <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
            <li>Review the ranked candidates (sorted by confidence)</li>
            <li>Read the evidence and rationale for each match</li>
            <li>Use high-confidence (80%+) alignments as a guide</li>
            <li>Approve valid alignments, reject incorrect ones, or defer uncertain ones</li>
            <li>Edit if you disagree with the mapping but still want to align</li>
          </ol>
        </Card.Body>
      </Card>
    </div>
  )
}
