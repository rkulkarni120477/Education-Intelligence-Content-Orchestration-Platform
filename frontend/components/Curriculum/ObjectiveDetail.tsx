'use client'

import React from 'react'
import { LearningObjective, Curriculum } from '@/lib/api/curriculum'
import { Card } from '@/components/Common/Card'
import { Badge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

interface ObjectiveDetailProps {
  objective: LearningObjective | null
  curriculum: Curriculum | null
  isLoading?: boolean
  onAlignClick?: (objectiveId: string) => void
}

const cognitiveLevel: Record<string, { label: string; color: string }> = {
  remember: { label: 'Remember', color: 'bg-blue-100 text-blue-800' },
  understand: { label: 'Understand', color: 'bg-green-100 text-green-800' },
  apply: { label: 'Apply', color: 'bg-yellow-100 text-yellow-800' },
  analyze: { label: 'Analyze', color: 'bg-orange-100 text-orange-800' },
  evaluate: { label: 'Evaluate', color: 'bg-red-100 text-red-800' },
  create: { label: 'Create', color: 'bg-purple-100 text-purple-800' },
}

export const ObjectiveDetail: React.FC<ObjectiveDetailProps> = ({
  objective,
  curriculum,
  isLoading = false,
  onAlignClick,
}) => {
  if (!objective) {
    return (
      <Card variant="outlined" className="h-full">
        <Card.Body>
          <p className="text-center text-slate-500">Select a learning objective to view details</p>
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

  const cognitiveInfo = objective.cognitive_level
    ? cognitiveLevel[objective.cognitive_level.toLowerCase()]
    : null

  return (
    <Card variant="outlined" className="h-full overflow-auto">
      <Card.Header>
        <h3 className="text-lg font-bold text-[#6B4423]">Learning Objective</h3>
        {curriculum && (
          <p className="text-sm text-slate-500 mt-1">
            {curriculum.name}
            {curriculum.grade && ` • Grade ${curriculum.grade}`}
            {curriculum.subject && ` • ${curriculum.subject}`}
          </p>
        )}
      </Card.Header>

      <Card.Body className="space-y-6">
        {/* Objective Statement */}
        <div>
          <h4 className="text-sm font-bold text-[#6B4423] mb-2">Objective</h4>
          <p className="text-slate-700 leading-relaxed">{objective.objective}</p>
        </div>

        {/* Cognitive Level */}
        {cognitiveInfo && (
          <div>
            <h4 className="text-sm font-bold text-[#6B4423] mb-2">Cognitive Level</h4>
            <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${cognitiveInfo.color}`}>
              {cognitiveInfo.label}
            </div>
            <p className="text-xs text-slate-500 mt-2 max-w-sm">
              Based on Bloom's Taxonomy levels of learning complexity
            </p>
          </div>
        )}

        {/* Metadata */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-[#6B4423] mb-1">Created</p>
            <p className="text-slate-700 text-sm">
              {new Date(objective.created_at).toLocaleDateString()}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-[#6B4423] mb-1">Last Updated</p>
            <p className="text-slate-700 text-sm">
              {new Date(objective.updated_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
          <p className="text-sm text-blue-800">
            This objective can be aligned with standards and used in lessons and assessments.
          </p>
        </div>

        {/* Actions */}
        {onAlignClick && (
          <div className="pt-4 border-t border-[#D2B48C] space-y-2">
            <button
              onClick={() => onAlignClick(objective.id)}
              className="w-full px-4 py-2 bg-[#8B5A3C] text-white rounded-lg font-medium hover:bg-[#6B4423] transition"
            >
              Align Standards to This Objective
            </button>
          </div>
        )}
      </Card.Body>
    </Card>
  )
}

ObjectiveDetail.displayName = 'ObjectiveDetail'
