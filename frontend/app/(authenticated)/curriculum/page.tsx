'use client'

import React, { useState, useMemo } from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import {
  useCurricula,
  useCurriculumStructure,
  useCreateCurriculum,
  useCreateCurriculumUnit,
  useCreateObjective,
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

interface DraftUnit {
  title: string
  description: string
  objectives: { objective: string; cognitive_level: string }[]
}

export default function CurriculumNavigatorPage() {
  const { isAuthenticated } = useAuthRequired()
  const [selectedCurriculumId, setSelectedCurriculumId] = useState<string>('')
  const [selectedObjectiveId, setSelectedObjectiveId] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')
  const [showCreateWorkflow, setShowCreateWorkflow] = useState(false)
  const [curriculumDraft, setCurriculumDraft] = useState({
    name: '', description: '', version: '1.0', grade: '', subject: '',
  })
  const [draftUnits, setDraftUnits] = useState<DraftUnit[]>([
    { title: '', description: '', objectives: [{ objective: '', cognitive_level: 'understand' }] },
  ])

  // Fetch curricula
  const curriculaQuery = useCurricula()
  const createCurriculumMutation = useCreateCurriculum()
  const createUnitMutation = useCreateCurriculumUnit()
  const createObjectiveMutation = useCreateObjective()

  // Fetch structure for selected curriculum
  const structureQuery = useCurriculumStructure(selectedCurriculumId)

  // Get selected objective detail
  const selectedObjective = structureQuery.data?.objectives.find(
    (o) => o.id === selectedObjectiveId
  ) || null

  const curricula = curriculaQuery.data || []
  const selectedCurriculum = curricula.find((c) => c.id === selectedCurriculumId)

  // Convert curriculum structure to tree items
  const treeItems: TreeItem[] = useMemo(() => {
    if (!structureQuery.data?.units) return []

    const buildTree = (units: CurriculumUnit[], parentId?: string): TreeItem[] => {
      return units
        .filter((u) => (u.parent_id ?? undefined) === parentId)
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

  if (!isAuthenticated) return null

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

  const resetCurriculumDraft = () => {
    setCurriculumDraft({ name: '', description: '', version: '1.0', grade: '', subject: '' })
    setDraftUnits([{ title: '', description: '', objectives: [{ objective: '', cognitive_level: 'understand' }] }])
  }

  const handleCreateCurriculum = async (event: React.FormEvent) => {
    event.preventDefault()
    const curriculum = await createCurriculumMutation.mutateAsync({
      ...curriculumDraft,
      status: 'draft',
    })

    for (const [unitIndex, draftUnit] of draftUnits.entries()) {
      const unit = await createUnitMutation.mutateAsync({
        curriculum_id: curriculum.id,
        title: draftUnit.title,
        description: draftUnit.description || undefined,
        sequence: unitIndex + 1,
      })

      for (const draftObjective of draftUnit.objectives) {
        if (draftObjective.objective.trim()) {
          await createObjectiveMutation.mutateAsync({
            unit_id: unit.id,
            objective: draftObjective.objective.trim(),
            cognitive_level: draftObjective.cognitive_level,
          })
        }
      }
    }

    resetCurriculumDraft()
    setShowCreateWorkflow(false)
    handleCurriculumSelect(curriculum.id)
  }

  const updateUnit = (unitIndex: number, changes: Partial<DraftUnit>) => {
    setDraftUnits((units) => units.map((unit, index) => index === unitIndex ? { ...unit, ...changes } : unit))
  }

  const addUnit = () => {
    setDraftUnits((units) => [
      ...units,
      { title: '', description: '', objectives: [{ objective: '', cognitive_level: 'understand' }] },
    ])
  }

  const addObjective = (unitIndex: number) => {
    setDraftUnits((units) => units.map((unit, index) => index === unitIndex
      ? { ...unit, objectives: [...unit.objectives, { objective: '', cognitive_level: 'understand' }] }
      : unit))
  }

  const updateObjective = (unitIndex: number, objectiveIndex: number, changes: Partial<DraftUnit['objectives'][number]>) => {
    setDraftUnits((units) => units.map((unit, index) => index === unitIndex
      ? { ...unit, objectives: unit.objectives.map((objective, index) => index === objectiveIndex ? { ...objective, ...changes } : objective) }
      : unit))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-[#0F172A]">Curriculum Navigator</h1>
          <p className="text-[#1E40AF] mt-2">
            Explore your curriculum structure and align content to learning objectives
          </p>
        </div>
        <Button type="button" onClick={() => setShowCreateWorkflow((visible) => !visible)}>
          {showCreateWorkflow ? 'Close Creation' : 'Create Curriculum'}
        </Button>
      </div>

      {showCreateWorkflow && (
        <Card variant="outlined">
          <Card.Header>
            <h2 className="text-lg font-bold text-[#0F172A]">Create Curriculum</h2>
            <p className="text-sm text-slate-600 mt-1">Define curriculum metadata, units, and measurable learning objectives.</p>
          </Card.Header>
          <form onSubmit={handleCreateCurriculum}>
            <Card.Body className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input required placeholder="Curriculum name" value={curriculumDraft.name} onChange={(e) => setCurriculumDraft({ ...curriculumDraft, name: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
                <input placeholder="Version" value={curriculumDraft.version} onChange={(e) => setCurriculumDraft({ ...curriculumDraft, version: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
                <input placeholder="Grade range" value={curriculumDraft.grade} onChange={(e) => setCurriculumDraft({ ...curriculumDraft, grade: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
                <input placeholder="Subject" value={curriculumDraft.subject} onChange={(e) => setCurriculumDraft({ ...curriculumDraft, subject: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
              </div>
              <textarea placeholder="Curriculum description" value={curriculumDraft.description} onChange={(e) => setCurriculumDraft({ ...curriculumDraft, description: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg h-20 resize-none" />

              {draftUnits.map((unit, unitIndex) => (
                <div key={unitIndex} className="border border-slate-200 rounded-lg p-4 space-y-3">
                  <h3 className="font-bold text-[#0F172A]">Unit {unitIndex + 1}</h3>
                  <input required placeholder="Unit title" value={unit.title} onChange={(e) => updateUnit(unitIndex, { title: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
                  <textarea placeholder="Unit description" value={unit.description} onChange={(e) => updateUnit(unitIndex, { description: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg h-16 resize-none" />
                  <div className="space-y-2">
                    {unit.objectives.map((objective, objectiveIndex) => (
                      <div key={objectiveIndex} className="grid grid-cols-1 md:grid-cols-[1fr_150px] gap-2">
                        <input placeholder="Learning objective" value={objective.objective} onChange={(e) => updateObjective(unitIndex, objectiveIndex, { objective: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
                        <select value={objective.cognitive_level} onChange={(e) => updateObjective(unitIndex, objectiveIndex, { cognitive_level: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg">
                          {['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'].map((level) => <option key={level} value={level}>{level}</option>)}
                        </select>
                      </div>
                    ))}
                  </div>
                  <Button type="button" variant="secondary" size="sm" onClick={() => addObjective(unitIndex)}>Add Objective</Button>
                </div>
              ))}
              <Button type="button" variant="secondary" onClick={addUnit}>Add Unit</Button>
              {(createCurriculumMutation.error || createUnitMutation.error || createObjectiveMutation.error) && <p className="text-sm text-red-600">{(createCurriculumMutation.error || createUnitMutation.error || createObjectiveMutation.error)?.message || 'Unable to create curriculum'}</p>}
            </Card.Body>
            <Card.Footer>
              <Button type="submit" isLoading={createCurriculumMutation.isLoading || createUnitMutation.isLoading || createObjectiveMutation.isLoading}>Create Curriculum</Button>
              <Button type="button" variant="secondary" onClick={resetCurriculumDraft}>Clear</Button>
            </Card.Footer>
          </form>
        </Card>
      )}

      {/* Curriculum Selector */}
      <div>
        <h2 className="text-lg font-bold text-[#0F172A] mb-3">Select Curriculum</h2>
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
                    ? 'border-[#1E40AF] bg-[#FFFFFF]'
                    : 'border-[#3B82F6] hover:border-[#1E40AF]'
                }`}
              >
                <p className="font-bold text-[#0F172A] truncate">{curriculum.name}</p>
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
                <h3 className="text-lg font-bold text-[#0F172A]">Structure</h3>
                <input
                  type="text"
                  placeholder="Search units & objectives..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full mt-3 px-3 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] text-sm"
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
          <h3 className="text-lg font-bold text-[#0F172A] mb-3">Curriculum Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#1E40AF]">
                  {structureQuery.data.units.length}
                </p>
                <p className="text-sm text-slate-600 mt-2">Units</p>
              </Card.Body>
            </Card>

            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#1E40AF]">
                  {structureQuery.data.objectives.length}
                </p>
                <p className="text-sm text-slate-600 mt-2">Learning Objectives</p>
              </Card.Body>
            </Card>

            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#1E40AF]">
                  {structureQuery.data.objectives.filter(o => o.cognitive_level).length}
                </p>
                <p className="text-sm text-slate-600 mt-2">With Cognitive Levels</p>
              </Card.Body>
            </Card>

            <Card variant="outlined">
              <Card.Body className="text-center">
                <p className="text-3xl font-bold text-[#1E40AF]">
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
