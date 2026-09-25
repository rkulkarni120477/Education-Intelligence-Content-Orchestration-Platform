'use client'

import React, { useState, useMemo } from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import {
  useCurricula,
  useCurriculumStructure,
  useLearningObjective: getLearningObjectiveByIdFromUnitQuery,
  Curriculum,
  CurriculumUnit,
  LearningObjective,
} from '@/lib/api/curriculum'
import { TreeView } from '@/components/Common/TreeNode'
import { ObjectiveDetail } from '@/components/Curriculum/ObjectiveDetail'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { StatusBadge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

interface TreeItem {
  id: string
  label: string
  code?: string
  children?: TreeItem[]
  data?: Record<string, any>
  type?: 'unit' | 'objective'
}

export default function CurriculumNavigatorPage() {
  const { isAuthenticated } = useAuthRequired()
  const [selectedCurriculumId, setSelectedCurriculumId] = useState<string>('')
  const [selectedObjectiveId, setSelectedObjectiveId] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch curricula
  const curriculaQuery = useCurricula()

  // Fetch structure for selected curriculum
  const structureQuery = useCurriculumStructure(selectedCurriculumId)

  // Get selected objective detail
  const selectedObjective = structureQuery.data?.objectives.find(
    (o) => o.id === selectedObjectiveId
  ) || null

  if (!isAuthenticated) return null

  const curricula = curriculaQuery.data || []
  const selectedCurriculum = curricula.find((c) => c.id === selectedCurriculumId)

  // Convert curriculum structure to tree items
  const treeItems: TreeItem[] = useMemo(() => {
    if (!structureQuery.data?.units) return []

    const buildTree = (units: CurriculumUnit[], parentId?: string): TreeItem[] => {
      return units
        .filter((u) => u.parent_id === parentId)
        .map((unit) => {
          // Get objectives for this unit
          const unitObjectives = structureQuery.data!.objectives
            .filter((o) => o.unit_id === unit.id)
            .map((obj) => ({
              id: obj.id,
              label: obj.objective.substring(0, 60) + (obj.objective.length > 60 ? '...' : ''),
              code: obj.cognitive_level,
              data: obj,
              type: 'objective' as const,
            }))

          return {
            id: unit.id,
            label: unit.title,
            code: `Unit ${unit.sequence || ''}`,
            type: 'unit' as const,
            children: [
              ...buildTree(units, unit.id),
              ...unitObjectives,
            ],
            data: unit,
          }
        })
    }

    return buildTree(structureQuery.data.units)
  }, [structureQuery.data])

  const handleCurriculumSelect = (curriculumId: string) => {
    setSelectedCurriculumId(curriculumId)
    setSelectedObjectiveId('')
    setSearchQuery('')
  }

  const handleItemSelect = (item: TreeItem) => {
    if (item.type === 'objective') {
      setSelectedObjectiveId(item.id)
    }
  }

  const handleAlignClick = (objectiveId: string) => {
    // Navigate to alignment workflow
    window.location.href = `/alignment?objective_id=${objectiveId}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#6B4423]">Curriculum Navigator</h1>
        <p className="text-[#8B5A3C] mt-2">
          Explore your curriculum structure and align content to learning objectives
        </p>
      </div>

      {/* Curriculum Selector */}
      <div>
        <h2 className="text-lg font-bold text-[#6B4423] mb-3">Select Curriculum</h2>
        {curriculaQuery.isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-20 rounded-lg" />
            ))}
          </div>
        ) : curricula.length === 0 ? (
          <Card variant="outlined">
            <Card.Body>
              <p className="text-center text-slate-600">No curricula available</p>
            </Card.Body>
          </Card>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {curricula.map((curriculum) => (
              <button
                key={curriculum.id}
                onClick={() => handleCurriculumSelect(curriculum.id)}
                className={`p-4 rounded-lg border-2 transition text-left ${
                  selectedCurriculumId === curriculum.id
                    ? 'border-[#8B5A3C] bg-[#FFF8F0]'
                    : 'border-[#D2B48C] hover:border-[#8B5A3C]'
                }`}
              >
                <p className="font-bold text-[#6B4423] truncate">{curriculum.name}</p>
                <div className="flex gap-1 mt-2 flex-wrap">
                  {curriculum.grade && (
                    <span className="text-xs px-2 py-1 bg-slate-200 rounded">
                      Grade {curriculum.grade}
                    </span>
                  )}
                  {curriculum.subject && (
                    <span className="text-xs px-2 py-1 bg-slate-200 rounded">
                      {curriculum.subject}
                    </span>
                  )}
                </div>
                <StatusBadge status={curriculum.status} />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Content */}
      {selectedCurriculumId && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Curriculum Tree */}
          <div className="lg:col-span-1">
            <Card variant="default" className="h-full">
              <Card.Header>
                <h3 className="text-lg font-bold text-[#6B4423]">Structure</h3>
                <input
                  type="text"
                  placeholder="Search units & objectives..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full mt-3 px-3 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] text-sm"
                />
              </Card.Header>

              <Card.Body className="max-h-96 overflow-auto">
                {structureQuery.isLoading ? (
                  <div className="space-y-2">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Skeleton key={i} className="h-8 w-full" />
                    ))}
                  </div>
                ) : treeItems.length === 0 ? (
                  <p className="text-center text-slate-600 py-8">
                    No curriculum structure found
                  </p>
                ) : (
                  <TreeView
                    items={treeItems}
                    onSelect={handleItemSelect}
                    selectedId={selectedObjectiveId}
                    expandRoot={true}
                    searchQuery={searchQuery}
                  />
                )}
              </Card.Body>
            </Card>
          </div>

          {/* Objective Details */}
          <div className="lg:col-span-2">
            <ObjectiveDetail
              objective={selectedObjective || null}
              curriculum={selectedCurriculum || null}
              isLoading={structureQuery.isLoading}
              onAlignClick={handleAlignClick}
            />
          </div>
        </div>
      )}

      {/* Curriculum Stats */}
      {selectedCurriculumId && structureQuery.data && (
        <div>
          <h3 className="text-lg font-bold text-[#6B4423] mb-3">Curriculum Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#8B5A3C]">
                  {structureQuery.data.units.length}
                </p>
                <p className="text-sm text-slate-600 mt-2">Units</p>
              </Card.Body>
            </Card>

            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#8B5A3C]">
                  {structureQuery.data.objectives.length}
                </p>
                <p className="text-sm text-slate-600 mt-2">Learning Objectives</p>
              </Card.Body>
            </Card>

            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#8B5A3C]">
                  {structureQuery.data.objectives.filter(o => o.cognitive_level).length}
                </p>
                <p className="text-sm text-slate-600 mt-2">With Cognitive Levels</p>
              </Card.Body>
            </Card>

            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#8B5A3C]">
                  {new Date(selectedCurriculum?.created_at || '').toLocaleDateString()}
                </p>
                <p className="text-sm text-slate-600 mt-2">Created</p>
              </Card.Body>
            </Card>
          </div>
        </div>
      )}

      {/* Info Card */}
      {!selectedCurriculumId && (
        <Card variant="default" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <p className="font-bold text-blue-800 mb-2">📖 How to use Curriculum Navigator</p>
            <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
              <li>Select a curriculum above to explore its structure</li>
              <li>View units, sub-units, and learning objectives in the left panel</li>
              <li>Click any objective to view full details and cognitive level</li>
              <li>Click "Align Standards" to map standards to this objective</li>
              <li>Use search to quickly find units and objectives by name or level</li>
            </ul>
          </Card.Body>
        </Card>
      )}
    </div>
  )
}
