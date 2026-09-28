'use client'

import React, { useState, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import {
  useCandidateAlignments,
  useApprovedAlignments,
  useApproveAlignment,
  useRejectAlignment,
  downloadAlignmentTemplate,
  useUploadAlignmentCandidates,
  Alignment,
} from '@/lib/api/alignments'
import { CandidatesList } from '@/components/Alignment/CandidatesList'
import { EvidenceInspector } from '@/components/Alignment/EvidenceInspector'
import { ActionButtons } from '@/components/Alignment/ActionButtons'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Skeleton } from '@/components/Common/Skeleton'

export default function AlignmentWorkspacePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isAuthenticated } = useAuthRequired()

  // Get context from URL params
  const contentId = searchParams.get('content_id')
  const objectiveId = searchParams.get('objective_id')
  const standardId = searchParams.get('standard_id')
  const frameworkId = searchParams.get('framework_id')

  const [selectedAlignmentId, setSelectedAlignmentId] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'candidates' | 'approved'>('candidates')
  const [candidateFile, setCandidateFile] = useState<File | null>(null)

  // Fetch candidate alignments (all candidates if no specific content/standard)
  const candidatesQuery = useCandidateAlignments(contentId || standardId || undefined, frameworkId || undefined)
  const approvedQuery = useApprovedAlignments(contentId || standardId || undefined, frameworkId || undefined)
  const approveMutation = useApproveAlignment()
  const rejectMutation = useRejectAlignment()
  const uploadCandidatesMutation = useUploadAlignmentCandidates()

  if (!isAuthenticated) return null

  const candidates = candidatesQuery.data || []
  const approved = approvedQuery.data || []

  // Show appropriate list based on active tab
  const currentList = activeTab === 'candidates' ? candidates : approved
  const currentQuery = activeTab === 'candidates' ? candidatesQuery : approvedQuery

  const selectedAlignment = currentList.find((a) => a.id === selectedAlignmentId) || currentList[0]

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

  const handleCandidateUpload = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!candidateFile) return
    await uploadCandidatesMutation.mutateAsync(candidateFile)
    setCandidateFile(null)
    await candidatesQuery.refetch()
  }

  // Statistics for all alignments
  const allAlignments = [...candidates, ...approved]
  const approvedCount = approved.length
  const rejectedCount = 0 // TODO: fetch rejected alignments if needed
  const pendingCount = candidates.length
  const avgConfidenceCandidates = candidates.length > 0
    ? Math.round((candidates.reduce((sum, a) => sum + a.confidence, 0) / candidates.length) * 100)
    : 0
  const avgConfidenceApproved = approved.length > 0
    ? Math.round((approved.reduce((sum, a) => sum + a.confidence, 0) / approved.length) * 100)
    : 0

  // Show confidence for current tab
  const avgConfidence = activeTab === 'candidates' ? avgConfidenceCandidates : avgConfidenceApproved

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#0F172A]">Alignment Workspace</h1>
        <p className="text-[#1E40AF] mt-2">
          Review and approve candidate standard alignments based on evidence
        </p>
      </div>

      <Card variant="outlined">
        <Card.Header>
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold text-[#0F172A]">Bulk Candidate Upload</h2>
              <p className="text-sm text-slate-600 mt-1">Download the Excel template, fill in candidate alignments, and upload it here.</p>
            </div>
            <button type="button" onClick={() => void downloadAlignmentTemplate()} className="text-sm font-medium text-[#1E40AF] underline hover:text-[#0F172A]">
              Download Excel Template
            </button>
          </div>
        </Card.Header>
        <Card.Body>
          <form onSubmit={handleCandidateUpload} className="flex flex-col md:flex-row md:items-center gap-3">
            <input
              type="file"
              accept=".xlsx,.xlsm"
              onChange={(event) => setCandidateFile(event.target.files?.[0] || null)}
              className="block w-full text-sm text-slate-600 file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:font-medium file:text-slate-700"
            />
            <Button type="submit" isLoading={uploadCandidatesMutation.isLoading} disabled={!candidateFile}>
              Upload Candidates
            </Button>
          </form>
          {candidateFile && <p className="text-xs text-slate-500 mt-2">Selected: {candidateFile.name}</p>}
          {uploadCandidatesMutation.data && <p className="text-sm text-green-700 mt-2">{uploadCandidatesMutation.data.message}</p>}
          {uploadCandidatesMutation.error && <p className="text-sm text-red-600 mt-2">{uploadCandidatesMutation.error.message}</p>}
        </Card.Body>
      </Card>

      {/* Context Information */}
      <Card variant="outlined" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <p className="text-sm text-blue-800">
            {contentId || standardId ? (
              <>
                {contentId && '📄 '}Reviewing alignments for:{' '}
                <strong>{contentId || standardId}</strong>
              </>
            ) : (
              <>
                📋 Reviewing <strong>all alignment candidates</strong> ready for your approval
              </>
            )}
          </p>
        </Card.Body>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-[#1E40AF]">{pendingCount}</p>
            <p className="text-xs text-slate-600 mt-1">Candidates</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-green-600">{approvedCount}</p>
            <p className="text-xs text-slate-600 mt-1">Approved</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-red-600">{rejectedCount}</p>
            <p className="text-xs text-slate-600 mt-1">Rejected</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-amber-600">{pendingCount}</p>
            <p className="text-xs text-slate-600 mt-1">Pending</p>
          </Card.Body>
        </Card>

        <Card variant="outlined">
          <Card.Body className="text-center">
            <p className="text-2xl font-bold text-[#1E40AF]">{avgConfidence}%</p>
            <p className="text-xs text-slate-600 mt-1">Avg Confidence</p>
          </Card.Body>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => {
            setActiveTab('candidates')
            setSelectedAlignmentId('')
          }}
          className={`pb-3 px-4 font-semibold transition-colors ${
            activeTab === 'candidates'
              ? 'text-[#1E40AF] border-b-2 border-[#1E40AF]'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          📋 Pending Candidates ({pendingCount})
        </button>
        <button
          onClick={() => {
            setActiveTab('approved')
            setSelectedAlignmentId('')
          }}
          className={`pb-3 px-4 font-semibold transition-colors ${
            activeTab === 'approved'
              ? 'text-[#1E40AF] border-b-2 border-[#1E40AF]'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          ✓ Approved ({approvedCount})
        </button>
      </div>

      {/* Main Workspace */}
      {currentQuery.isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <Skeleton className="lg:col-span-1 h-96 rounded-lg" />
          <Skeleton className="lg:col-span-2 h-96 rounded-lg" />
          <Skeleton className="lg:col-span-1 h-96 rounded-lg" />
        </div>
      ) : currentList.length === 0 ? (
        <Card variant="outlined">
          <Card.Body>
            <p className="text-center text-slate-600 py-12">
              {activeTab === 'candidates'
                ? 'No candidate alignments waiting for review'
                : 'No approved alignments yet'}
            </p>
          </Card.Body>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Candidates/Approved List */}
          <div className="lg:col-span-1">
            <h3 className="text-lg font-bold text-[#0F172A] mb-3">
              {activeTab === 'candidates' ? '📋 Candidates' : '✓ Approved'}
            </h3>
            <div className="max-h-96 overflow-auto">
              <CandidatesList
                candidates={currentList}
                selectedId={selectedAlignmentId}
                onSelect={handleSelectAlignment}
                isLoading={currentQuery.isLoading}
              />
            </div>
          </div>

          {/* Evidence Inspector */}
          <div className="lg:col-span-2">
            <h3 className="text-lg font-bold text-[#0F172A] mb-3">Evidence</h3>
            <div className="max-h-96 overflow-auto">
              <EvidenceInspector
                alignment={selectedAlignment || null}
                isLoading={currentQuery.isLoading}
              />
            </div>
          </div>

          {/* Action Buttons - Only show for candidates */}
          <div className="lg:col-span-1">
            <h3 className="text-lg font-bold text-[#0F172A] mb-3">
              {activeTab === 'candidates' ? 'Decision' : 'Status'}
            </h3>
            {activeTab === 'candidates' ? (
              <ActionButtons
                alignmentId={selectedAlignment?.id || ''}
                isLoading={approveMutation.isLoading || rejectMutation.isLoading}
                onApprove={handleApprove}
                onReject={handleReject}
                onDefer={handleDefer}
                onEdit={handleEdit}
              />
            ) : (
              <Card variant="outlined">
                <Card.Body className="text-center">
                  <p className="text-2xl font-bold text-green-600">✓</p>
                  <p className="text-sm text-slate-600 mt-2">Approved</p>
                  <p className="text-xs text-slate-500 mt-2">
                    Confidence: {Math.round((selectedAlignment?.confidence || 0) * 100)}%
                  </p>
                </Card.Body>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Workflow Tips */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card variant="default" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <p className="font-bold text-blue-800 mb-2">💡 Candidate Review Workflow</p>
            <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
              <li>Review ranked candidates (highest confidence first)</li>
              <li>Read the evidence and rationale for each match</li>
              <li>Use high-confidence (80%+) alignments as a guide</li>
              <li>Approve valid alignments, reject incorrect ones, or defer uncertain ones</li>
              <li>Edit if you disagree with the mapping but still want to align</li>
            </ol>
          </Card.Body>
        </Card>

        <Card variant="default" className="bg-green-50 border-green-200">
          <Card.Body>
            <p className="font-bold text-green-800 mb-2">✓ Approved Alignments</p>
            <p className="text-sm text-green-700 mb-3">
              View all approved alignments in the <strong>"Approved"</strong> tab.
            </p>
            <div className="text-sm text-green-700 space-y-1">
              <p>✓ Total approved: <strong>{approvedCount}</strong></p>
              <p>✓ Avg confidence: <strong>{avgConfidenceApproved}%</strong></p>
              <p>✓ Ready for use in lessons and curriculum</p>
            </div>
          </Card.Body>
        </Card>
      </div>
    </div>
  )
}
