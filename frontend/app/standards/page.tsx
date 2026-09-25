'use client'

import React, { useState, useMemo } from 'react'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { useFrameworks, useStandardHierarchy, useStandard, Standard, StandardFramework } from '@/lib/api/standards'
import { TreeView } from '@/components/Common/TreeNode'
import { StandardDetail } from '@/components/Standards/StandardDetail'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Skeleton } from '@/components/Common/Skeleton'

interface TreeItem {
  id: string
  label: string
  code?: string
  children?: TreeItem[]
  data?: Record<string, any>
}

export default function StandardsExplorerPage() {
  const { isAuthenticated } = useAuthRequired()
  const [selectedFrameworkId, setSelectedFrameworkId] = useState<string>('')
  const [selectedStandardId, setSelectedStandardId] = useState<string>('')
  const [searchQuery, setSearchQuery] = useState('')

  // Fetch frameworks
  const frameworksQuery = useFrameworks()

  // Fetch hierarchy for selected framework
  const hierarchyQuery = useStandardHierarchy(selectedFrameworkId)

  // Fetch selected standard detail
  const standardDetailQuery = useStandard(selectedStandardId)

  if (!isAuthenticated) return null

  const frameworks = frameworksQuery.data || []
  const selectedFramework = frameworks.find(f => f.id === selectedFrameworkId)

  // Convert hierarchy to tree items
  const treeItems: TreeItem[] = useMemo(() => {
    if (!hierarchyQuery.data?.hierarchy) return []

    const convertToTreeItem = (item: any): TreeItem => ({
      id: item.id,
      label: item.label,
      code: item.code,
      children: item.children?.map(convertToTreeItem),
      data: item,
    })

    return hierarchyQuery.data.hierarchy.map(convertToTreeItem)
  }, [hierarchyQuery.data])

  const handleFrameworkSelect = (frameworkId: string) => {
    setSelectedFrameworkId(frameworkId)
    setSelectedStandardId('')
    setSearchQuery('')
  }

  const handleStandardSelect = (item: TreeItem) => {
    setSelectedStandardId(item.id)
  }

  const handleAlignClick = (standardId: string) => {
    // Navigate to alignment workflow
    window.location.href = `/alignment?standard_id=${standardId}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#0F172A]">Standards Explorer</h1>
        <p className="text-[#1E40AF] mt-2">
          Browse educational standards frameworks and create alignments with your content
        </p>
      </div>

      {/* Framework Selector */}
      <div>
        <h2 className="text-lg font-bold text-[#0F172A] mb-3">Select Framework</h2>
        {frameworksQuery.isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-16 rounded-lg" />
            ))}
          </div>
        ) : frameworks.length === 0 ? (
          <Card variant="outlined">
            <Card.Body>
              <p className="text-center text-slate-600">No frameworks available</p>
            </Card.Body>
          </Card>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {frameworks.map((framework) => (
              <button
                key={framework.id}
                onClick={() => handleFrameworkSelect(framework.id)}
                className={`p-4 rounded-lg border-2 transition text-left ${
                  selectedFrameworkId === framework.id
                    ? 'border-[#1E40AF] bg-[#FFFFFF]'
                    : 'border-[#3B82F6] hover:border-[#1E40AF]'
                }`}
              >
                <p className="font-bold text-[#0F172A]">{framework.name}</p>
                <p className="text-xs text-slate-600 mt-1">{framework.authority}</p>
                {framework.version && (
                  <p className="text-xs text-slate-500 mt-1">v{framework.version}</p>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Main Content */}
      {selectedFrameworkId && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Standards Tree */}
          <div className="lg:col-span-1">
            <Card variant="default" className="h-full">
              <Card.Header>
                <h3 className="text-lg font-bold text-[#0F172A]">Standards</h3>
                <input
                  type="text"
                  placeholder="Search standards..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full mt-3 px-3 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] text-sm"
                />
              </Card.Header>

              <Card.Body className="max-h-96 overflow-auto">
                {hierarchyQuery.isLoading ? (
                  <div className="space-y-2">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Skeleton key={i} className="h-8 w-full" />
                    ))}
                  </div>
                ) : treeItems.length === 0 ? (
                  <p className="text-center text-slate-600 py-8">No standards found</p>
                ) : (
                  <TreeView
                    items={treeItems}
                    onSelect={handleStandardSelect}
                    selectedId={selectedStandardId}
                    expandRoot={true}
                    searchQuery={searchQuery}
                  />
                )}
              </Card.Body>
            </Card>
          </div>

          {/* Standard Details */}
          <div className="lg:col-span-2">
            <StandardDetail
              standard={standardDetailQuery.data || null}
              framework={selectedFramework || null}
              isLoading={standardDetailQuery.isLoading}
              onAlignClick={handleAlignClick}
            />
          </div>
        </div>
      )}

      {/* Info Card */}
      {!selectedFrameworkId && (
        <Card variant="default" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <p className="font-bold text-blue-800 mb-2">📋 How to use Standards Explorer</p>
            <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside">
              <li>Select a standards framework above (e.g., Common Core, State Standards)</li>
              <li>Browse the standards hierarchy in the left panel</li>
              <li>Click any standard to view full details</li>
              <li>Click "Align Content" to create alignment mappings</li>
              <li>Use search to quickly find standards by code or description</li>
            </ul>
          </Card.Body>
        </Card>
      )}
    </div>
  )
}
