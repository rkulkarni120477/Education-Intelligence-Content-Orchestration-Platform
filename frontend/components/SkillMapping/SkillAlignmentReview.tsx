/**
 * Skill Alignment Review Component
 *
 * Displays skill-to-content alignments with approval workflow.
 * Allows reviewers to approve, reject, or request clarification.
 */

'use client';

import React, { useState } from 'react';
import { useSkillAlignments, useApproveAlignment, useBatchApproveAlignments } from '@/lib/api/skillMapping';
import type { SkillAlignmentItem } from '@/lib/types/phase5';

interface SkillAlignmentReviewProps {
  workflowId: string;
}

export function SkillAlignmentReview({ workflowId }: SkillAlignmentReviewProps) {
  const [selectedAlignments, setSelectedAlignments] = useState<Set<string>>(new Set());
  const [filterStatus, setFilterStatus] = useState<string>('candidate');
  const [reviewNotes, setReviewNotes] = useState<string>('');

  const { data, isLoading, error } = useSkillAlignments(workflowId, filterStatus);
  const approveMutation = useApproveAlignment(workflowId);
  const batchApproveMutation = useBatchApproveAlignments(workflowId);

  const handleSelectAlignment = (alignmentId: string) => {
    const newSelected = new Set(selectedAlignments);
    if (newSelected.has(alignmentId)) {
      newSelected.delete(alignmentId);
    } else {
      newSelected.add(alignmentId);
    }
    setSelectedAlignments(newSelected);
  };

  const handleApproveSelected = async () => {
    if (selectedAlignments.size === 0) return;

    try {
      await batchApproveMutation.mutateAsync(Array.from(selectedAlignments));
      setSelectedAlignments(new Set());
      setReviewNotes('');
    } catch (err) {
      console.error('Failed to approve alignments:', err);
    }
  };

  const handleApproveOne = async (alignmentId: string) => {
    try {
      await approveMutation.mutateAsync({ alignmentId, notes: reviewNotes });
      setReviewNotes('');
    } catch (err) {
      console.error('Failed to approve alignment:', err);
    }
  };

  if (isLoading) {
    return <div className="p-6 text-center">Loading alignments...</div>;
  }

  if (error) {
    return <div className="p-6 text-center text-red-500">Failed to load alignments</div>;
  }

  const alignments = data?.alignments || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Skill Alignment Review</h2>
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border rounded bg-white"
          >
            <option value="candidate">Candidates</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Total Alignments</div>
          <div className="text-2xl font-bold">{data?.total || 0}</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Selected for Approval</div>
          <div className="text-2xl font-bold">{selectedAlignments.size}</div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Confidence Avg</div>
          <div className="text-2xl font-bold">
            {alignments.length > 0
              ? (
                  (alignments.reduce((sum: number, a: any) => sum + a.confidence, 0) /
                    alignments.length) *
                  100
                ).toFixed(0) + '%'
              : 'N/A'}
          </div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Skills Mapped</div>
          <div className="text-2xl font-bold">
            {new Set(alignments.map((a: any) => a.skillId)).size}
          </div>
        </div>
      </div>

      {/* Alignment List */}
      <div className="space-y-3">
        {alignments.map((alignment: any) => (
          <AlignmentCard
            key={alignment.id}
            alignment={alignment}
            isSelected={selectedAlignments.has(alignment.id)}
            onSelect={() => handleSelectAlignment(alignment.id)}
            onApprove={() => handleApproveOne(alignment.id)}
            isLoading={approveMutation.isLoading}
          />
        ))}
      </div>

      {/* Batch Actions */}
      {selectedAlignments.size > 0 && (
        <div className="border-t pt-4 space-y-4">
          <textarea
            value={reviewNotes}
            onChange={(e) => setReviewNotes(e.target.value)}
            placeholder="Add review notes (optional)..."
            className="w-full p-3 border rounded text-sm"
            rows={3}
          />
          <button
            onClick={handleApproveSelected}
            disabled={batchApproveMutation.isLoading}
            className="w-full bg-green-600 text-white py-2 rounded font-medium hover:bg-green-700 disabled:bg-gray-400"
          >
            {batchApproveMutation.isLoading
              ? 'Approving...'
              : `Approve Selected (${selectedAlignments.size})`}
          </button>
        </div>
      )}
    </div>
  );
}

interface AlignmentCardProps {
  alignment: SkillAlignmentItem;
  isSelected: boolean;
  onSelect: () => void;
  onApprove: () => void;
  isLoading: boolean;
}

function AlignmentCard({
  alignment,
  isSelected,
  onSelect,
  onApprove,
  isLoading,
}: AlignmentCardProps) {
  return (
    <div
      className={`border rounded-lg p-4 cursor-pointer transition ${
        isSelected ? 'bg-blue-50 border-blue-300' : 'hover:bg-gray-50'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={isSelected}
          onChange={onSelect}
          className="mt-1"
          onClick={(e) => e.stopPropagation()}
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-bold text-lg">{alignment.skillName}</span>
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {alignment.alignmentType}
            </span>
            <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">
              {alignment.proficiencyLevel}
            </span>
          </div>

          <p className="text-gray-600 text-sm mb-2">{alignment.contentTitle}</p>

          {/* Confidence and Evidence */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Confidence:</span>
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full"
                  style={{ width: `${alignment.confidence * 100}%` }}
                />
              </div>
              <span className="text-sm font-medium">
                {(alignment.confidence * 100).toFixed(0)}%
              </span>
            </div>

            {alignment.evidence.length > 0 && (
              <div className="bg-gray-50 p-2 rounded text-sm">
                <p className="font-medium text-gray-700 mb-1">Evidence:</p>
                {alignment.evidence.map((ev, idx) => (
                  <p key={idx} className="text-gray-600 italic text-xs">
                    "{ev.quote}" — {ev.reference}
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Status and Actions */}
        <div className="flex flex-col gap-2">
          <span
            className={`text-xs px-2 py-1 rounded font-medium ${
              alignment.status === 'approved'
                ? 'bg-green-100 text-green-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}
          >
            {alignment.status}
          </span>
          {alignment.status === 'candidate' && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onApprove();
              }}
              disabled={isLoading}
              className="text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 disabled:bg-gray-400"
            >
              Approve
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
