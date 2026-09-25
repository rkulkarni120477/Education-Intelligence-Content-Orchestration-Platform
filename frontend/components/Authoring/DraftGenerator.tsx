'use client'

import React, { useState } from 'react'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { Badge } from '@/components/Common/Badge'
import { Skeleton } from '@/components/Common/Skeleton'

export interface DraftSection {
  id: string
  title: string
  type: 'introduction' | 'objectives' | 'activities' | 'assessments' | 'resources' | 'closure'
  content: string
  isEditing?: boolean
  isRegenerating?: boolean
  citations?: string[]
}

interface DraftGeneratorProps {
  artifactTitle: string
  artifactType: 'lesson' | 'activity' | 'assessment'
  sections: DraftSection[]
  onSectionChange: (sectionId: string, content: string) => void
  onRegenerateSection: (sectionId: string) => void
  onSaveDraft: () => void
  isGenerating?: boolean
  isLoading?: boolean
  generationProgress?: number
}

const sectionDefaults = {
  introduction: { icon: '📖', label: 'Introduction' },
  objectives: { icon: '🎯', label: 'Learning Objectives' },
  activities: { icon: '🎬', label: 'Activities' },
  assessments: { icon: '📝', label: 'Assessments' },
  resources: { icon: '📚', label: 'Resources' },
  closure: { icon: '✨', label: 'Closure' },
}

export const DraftGenerator: React.FC<DraftGeneratorProps> = ({
  artifactTitle,
  artifactType,
  sections,
  onSectionChange,
  onRegenerateSection,
  onSaveDraft,
  isGenerating = false,
  isLoading = false,
  generationProgress = 0,
}) => {
  const [expandedId, setExpandedId] = useState<string>(sections[0]?.id || '')
  const [editingId, setEditingId] = useState<string>('')

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-[#0F172A]">{artifactTitle}</h2>
            <p className="text-slate-600 mt-1">
              AI-generated {artifactType} draft — edit sections, regenerate parts, save as draft
            </p>
          </div>
          <Button
            variant="success"
            onClick={onSaveDraft}
            disabled={isGenerating || isLoading}
            isLoading={isLoading}
          >
            💾 Save Draft
          </Button>
        </div>
      </div>

      {/* Generation Progress */}
      {isGenerating && (
        <Card variant="outlined" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <div className="space-y-3">
              <p className="font-bold text-blue-800">Generating your {artifactType}...</p>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${generationProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-blue-700">{generationProgress}% complete</p>
            </div>
          </Card.Body>
        </Card>
      )}

      {/* Sections */}
      <div className="space-y-3">
        {sections.map((section) => {
          const config = sectionDefaults[section.type]
          const isExpanded = expandedId === section.id
          const isEditing = editingId === section.id

          return (
            <Card key={section.id} variant="outlined">
              {/* Section Header */}
              <button
                onClick={() => setExpandedId(isExpanded ? '' : section.id)}
                className="w-full text-left p-4 hover:bg-[#FFFFFF] transition"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{config.icon}</span>
                    <div>
                      <h3 className="text-lg font-bold text-[#0F172A]">{config.label}</h3>
                      {!isExpanded && (
                        <p className="text-sm text-slate-600 line-clamp-1">
                          {section.content.substring(0, 100)}...
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {section.citations && section.citations.length > 0 && (
                      <Badge variant="default">
                        {section.citations.length} source{section.citations.length !== 1 ? 's' : ''}
                      </Badge>
                    )}
                    <span className="text-[#1E40AF] font-bold">
                      {isExpanded ? '−' : '+'}
                    </span>
                  </div>
                </div>
              </button>

              {/* Expanded Section */}
              {isExpanded && (
                <>
                  <hr className="border-[#E8DCC8]" />

                  <Card.Body className="space-y-4">
                    {isEditing ? (
                      /* Edit Mode */
                      <div className="space-y-3">
                        <textarea
                          value={section.content}
                          onChange={(e) => onSectionChange(section.id, e.target.value)}
                          className="w-full px-4 py-3 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white font-mono text-sm h-64 resize-none"
                        />

                        <div className="flex gap-2">
                          <Button
                            variant="primary"
                            onClick={() => setEditingId('')}
                            className="flex-1"
                          >
                            ✓ Save Edit
                          </Button>
                          <Button
                            variant="secondary"
                            onClick={() => setEditingId('')}
                            className="flex-1"
                          >
                            ✗ Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      /* View Mode */
                      <>
                        <div className="prose prose-sm max-w-none">
                          <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                            {section.content}
                          </p>
                        </div>

                        {/* Citations */}
                        {section.citations && section.citations.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-[#E8DCC8]">
                            <p className="text-sm font-bold text-[#0F172A] mb-2">Sources</p>
                            <ul className="space-y-2">
                              {section.citations.map((citation, idx) => (
                                <li key={idx} className="text-xs text-slate-600 flex gap-2">
                                  <span className="text-[#1E40AF] font-bold">[{idx + 1}]</span>
                                  <span>{citation}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-2 pt-2">
                          <Button
                            variant="tertiary"
                            onClick={() => setEditingId(section.id)}
                            className="flex-1"
                            disabled={section.isRegenerating}
                          >
                            ✎ Edit
                          </Button>
                          <Button
                            variant="secondary"
                            onClick={() => onRegenerateSection(section.id)}
                            isLoading={section.isRegenerating}
                            disabled={section.isRegenerating}
                            className="flex-1"
                          >
                            🔄 Regenerate
                          </Button>
                        </div>

                        {section.isRegenerating && (
                          <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
                            <p className="text-sm text-blue-800">Regenerating section...</p>
                          </div>
                        )}
                      </>
                    )}
                  </Card.Body>
                </>
              )}
            </Card>
          )
        })}
      </div>

      {/* Action Footer */}
      <Card variant="default" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <div className="flex items-start gap-4">
            <span className="text-2xl">💡</span>
            <div className="flex-1">
              <p className="font-bold text-blue-800">Draft Management Tips</p>
              <ul className="text-sm text-blue-700 space-y-1 list-disc list-inside mt-2">
                <li>Edit any section independently — your changes are preserved</li>
                <li>Regenerate a section if you want a different approach</li>
                <li>All sources and citations are included for transparency</li>
                <li>Save drafts regularly — you can version and compare later</li>
                <li>Publish when ready — students will see the final version</li>
              </ul>
            </div>
          </div>
        </Card.Body>
      </Card>

      {/* Save Button (sticky) */}
      <div className="flex gap-2">
        <Button
          variant="secondary"
          onClick={() => {/* Navigate back */}}
          className="flex-1"
        >
          ← Back
        </Button>
        <Button
          variant="success"
          onClick={onSaveDraft}
          disabled={isGenerating || isLoading}
          isLoading={isLoading}
          className="flex-1"
        >
          💾 Save & Preview
        </Button>
      </div>
    </div>
  )
}

DraftGenerator.displayName = 'DraftGenerator'
