'use client'

import React from 'react'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'

interface MetadataFormProps {
  artifactType: 'lesson' | 'activity' | 'assessment' | ''
  onTypeSelect: (type: 'lesson' | 'activity' | 'assessment') => void
  metadata: {
    title: string
    description: string
    grade?: string
    subject?: string
    duration?: number
    audience?: string
  }
  onMetadataChange: (metadata: Partial<MetadataFormProps['metadata']>) => void
  onNext: () => void
  isLoading?: boolean
}

const subjectOptions = ['Mathematics', 'English', 'Science', 'History', 'Social Studies', 'Arts', 'Physical Education']
const gradeOptions = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
const audienceOptions = ['Individual Student', 'Small Group', 'Whole Class', 'Self-Paced']

export const MetadataForm: React.FC<MetadataFormProps> = ({
  artifactType,
  onTypeSelect,
  metadata,
  onMetadataChange,
  onNext,
  isLoading = false,
}) => {
  const isComplete = artifactType && metadata.title && metadata.grade && metadata.subject

  return (
    <div className="space-y-6">
      {/* Artifact Type Selection */}
      <div>
        <h3 className="text-lg font-bold text-[#6B4423] mb-3">What are you creating?</h3>
        <div className="grid grid-cols-3 gap-3">
          {(['lesson', 'activity', 'assessment'] as const).map((type) => (
            <button
              key={type}
              onClick={() => onTypeSelect(type)}
              className={`p-4 rounded-lg border-2 transition ${
                artifactType === type
                  ? 'border-[#8B5A3C] bg-[#FFF8F0]'
                  : 'border-[#D2B48C] hover:border-[#8B5A3C]'
              }`}
            >
              <p className="font-bold text-[#6B4423] capitalize">{type}</p>
              <p className="text-xs text-slate-600 mt-1">
                {type === 'lesson' && 'Complete lesson plan'}
                {type === 'activity' && 'Learning activity'}
                {type === 'assessment' && 'Quiz or test'}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Metadata Fields */}
      {artifactType && (
        <Card variant="outlined">
          <Card.Header>
            <h3 className="text-lg font-bold text-[#6B4423]">Basic Information</h3>
          </Card.Header>

          <Card.Body className="space-y-4">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">
                Title *
              </label>
              <input
                type="text"
                value={metadata.title}
                onChange={(e) => onMetadataChange({ title: e.target.value })}
                placeholder={`e.g., "Introduction to Fractions"`}
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">
                Description
              </label>
              <textarea
                value={metadata.description}
                onChange={(e) => onMetadataChange({ description: e.target.value })}
                placeholder="Brief overview of what students will learn..."
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white h-24 resize-none"
              />
            </div>

            {/* Grade and Subject */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-[#6B4423] mb-2">
                  Grade *
                </label>
                <select
                  value={metadata.grade || ''}
                  onChange={(e) => onMetadataChange({ grade: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
                >
                  <option value="">Select grade...</option>
                  {gradeOptions.map((g) => (
                    <option key={g} value={g}>
                      Grade {g}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-[#6B4423] mb-2">
                  Subject *
                </label>
                <select
                  value={metadata.subject || ''}
                  onChange={(e) => onMetadataChange({ subject: e.target.value })}
                  className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
                >
                  <option value="">Select subject...</option>
                  {subjectOptions.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Duration (for lessons/activities) */}
            {artifactType !== 'assessment' && (
              <div>
                <label className="block text-sm font-medium text-[#6B4423] mb-2">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  value={metadata.duration || ''}
                  onChange={(e) => onMetadataChange({ duration: parseInt(e.target.value) })}
                  placeholder="45"
                  className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
                />
              </div>
            )}

            {/* Audience */}
            <div>
              <label className="block text-sm font-medium text-[#6B4423] mb-2">
                Intended Audience
              </label>
              <select
                value={metadata.audience || ''}
                onChange={(e) => onMetadataChange({ audience: e.target.value })}
                className="w-full px-4 py-2 border-2 border-[#D2B48C] rounded-lg focus:outline-none focus:border-[#8B5A3C] bg-white"
              >
                <option value="">Select audience...</option>
                {audienceOptions.map((a) => (
                  <option key={a} value={a}>
                    {a}
                  </option>
                ))}
              </select>
            </div>
          </Card.Body>

          <Card.Footer>
            <div className="flex gap-2">
              <Button
                variant="primary"
                onClick={onNext}
                disabled={!isComplete || isLoading}
                isLoading={isLoading}
              >
                Continue to Content Selection
              </Button>
            </div>
          </Card.Footer>
        </Card>
      )}

      {/* Info */}
      <Card variant="default" className="bg-blue-50 border-blue-200">
        <Card.Body>
          <p className="font-bold text-blue-800 mb-2">💡 Creating an {artifactType || 'artifact'}</p>
          <p className="text-sm text-blue-700">
            {artifactType === 'lesson' && 'Lessons include objectives, activities, and assessments organized around learning goals.'}
            {artifactType === 'activity' && 'Activities are standalone interactive experiences that reinforce learning objectives.'}
            {artifactType === 'assessment' && 'Assessments measure student understanding through tests and quizzes.'}
          </p>
        </Card.Body>
      </Card>
    </div>
  )
}

MetadataForm.displayName = 'MetadataForm'
