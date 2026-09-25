'use client'

import React, { useState } from 'react'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Skeleton } from '@/components/Common/Skeleton'

interface SelectedContent {
  id: string
  title: string
  type: 'content' | 'objective' | 'standard'
  confidence?: number
}

interface ContentSelectorProps {
  artifactType: 'lesson' | 'activity' | 'assessment'
  frameId?: string
  curriculumId?: string
  selectedContent: SelectedContent[]
  onAddContent: (items: SelectedContent[]) => void
  onRemoveContent: (id: string) => void
  onNext: () => void
  isLoading?: boolean
}

export const ContentSelector: React.FC<ContentSelectorProps> = ({
  artifactType,
  frameId,
  curriculumId,
  selectedContent,
  onAddContent,
  onRemoveContent,
  onNext,
  isLoading = false,
}) => {
  const [tab, setTab] = useState<'content' | 'objectives' | 'standards'>('content')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedId, setExpandedId] = useState<string>('')

  // Mock data - in real implementation, would fetch based on context
  const mockContent = [
    { id: 'content-1', title: 'Introduction to Fractions', type: 'content' as const },
    { id: 'content-2', title: 'Comparing Fractions', type: 'content' as const },
    { id: 'content-3', title: 'Adding Fractions with Like Denominators', type: 'content' as const },
  ]

  const mockObjectives = [
    { id: 'obj-1', title: 'Students will understand fraction concepts', type: 'objective' as const },
    { id: 'obj-2', title: 'Students will compare fractions', type: 'objective' as const },
    { id: 'obj-3', title: 'Students will add fractions', type: 'objective' as const },
  ]

  const mockStandards = [
    { id: 'std-1', title: 'CCSS.MATH.3.NF.A.1: Understand a fraction 1/b', type: 'standard' as const },
    { id: 'std-2', title: 'CCSS.MATH.4.NF.A.1: Explain fraction equivalence', type: 'standard' as const },
    { id: 'std-3', title: 'CCSS.MATH.4.NF.A.2: Compare fractions', type: 'standard' as const },
  ]

  const itemsToShow =
    tab === 'content' ? mockContent :
    tab === 'objectives' ? mockObjectives :
    mockStandards

  const filteredItems = itemsToShow.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const isSelected = (id: string) => selectedContent.some(item => item.id === id)

  const handleToggleItem = (item: typeof mockContent[0]) => {
    if (isSelected(item.id)) {
      onRemoveContent(item.id)
    } else {
      onAddContent([...selectedContent, item])
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-[#0F172A] mb-2">Select Content & Objectives</h2>
        <p className="text-slate-600">
          Choose the content and learning objectives this {artifactType} will align to
        </p>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Selection Panel */}
        <div className="lg:col-span-2">
          <Card variant="outlined">
            <Card.Header>
              <div className="flex gap-2 mb-4">
                {(['content', 'objectives', 'standards'] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTab(t)}
                    className={`px-4 py-2 rounded-lg font-medium transition ${
                      tab === t
                        ? 'bg-[#1E40AF] text-white'
                        : 'bg-[#F0E6D8] text-[#0F172A] hover:bg-[#3B82F6]'
                    }`}
                  >
                    {tab === 'content' && 'Content'}
                    {tab === 'objectives' && 'Objectives'}
                    {tab === 'standards' && 'Standards'}
                  </button>
                ))}
              </div>

              <input
                type="text"
                placeholder={`Search ${tab}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white"
              />
            </Card.Header>

            <Card.Body className="max-h-96 overflow-auto space-y-2">
              {isLoading ? (
                <>
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                  <Skeleton className="h-12 w-full" />
                </>
              ) : filteredItems.length === 0 ? (
                <p className="text-center text-slate-500 py-8">No {tab} found</p>
              ) : (
                filteredItems.map((item) => (
                  <label
                    key={item.id}
                    className="block p-3 border-2 border-[#E8DCC8] rounded-lg hover:bg-[#FFFFFF] cursor-pointer transition"
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={isSelected(item.id)}
                        onChange={() => handleToggleItem(item)}
                        className="w-5 h-5 mt-1 accent-[#1E40AF] cursor-pointer"
                      />
                      <div className="flex-1">
                        <p className="font-medium text-[#0F172A]">{item.title}</p>
                        <p className="text-xs text-slate-600 mt-1">
                          {tab === 'content' && 'Content Item'}
                          {tab === 'objectives' && 'Learning Objective'}
                          {tab === 'standards' && 'Standards Standard'}
                        </p>
                      </div>
                    </div>
                  </label>
                ))
              )}
            </Card.Body>
          </Card>
        </div>

        {/* Selected Summary */}
        <div>
          <Card variant="outlined" className="h-fit">
            <Card.Header>
              <h3 className="text-lg font-bold text-[#0F172A]">Selected Items</h3>
              <p className="text-sm text-slate-600 mt-1">{selectedContent.length} selected</p>
            </Card.Header>

            <Card.Body className="max-h-96 overflow-auto space-y-2">
              {selectedContent.length === 0 ? (
                <p className="text-center text-slate-500 py-8">No items selected yet</p>
              ) : (
                selectedContent.map((item) => (
                  <div
                    key={item.id}
                    className="p-3 bg-[#FFFFFF] border-l-4 border-[#1E40AF] rounded flex items-start justify-between"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-[#0F172A] text-sm">{item.title}</p>
                      <p className="text-xs text-slate-600 mt-1 capitalize">{item.type}</p>
                    </div>
                    <button
                      onClick={() => onRemoveContent(item.id)}
                      className="text-red-600 hover:text-red-800 font-bold ml-2"
                    >
                      ×
                    </button>
                  </div>
                ))
              )}
            </Card.Body>

            <Card.Footer>
              <Button
                variant="primary"
                onClick={onNext}
                disabled={selectedContent.length === 0 || isLoading}
                isLoading={isLoading}
                className="w-full"
              >
                Continue to Generation
              </Button>
            </Card.Footer>
          </Card>
        </div>
      </div>

      {/* Info Box */}
      <Card variant="default" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <p className="font-bold text-blue-800 mb-2">💡 Content Selection Tips</p>
          <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
            <li>Select 1-3 content items for focused learning</li>
            <li>Choose objectives that align with your content</li>
            <li>Mix standards from different levels for depth</li>
            <li>You can always edit the {artifactType} after generation</li>
          </ul>
        </Card.Body>
      </Card>
    </div>
  )
}

ContentSelector.displayName = 'ContentSelector'
