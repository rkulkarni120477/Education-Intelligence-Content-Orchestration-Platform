'use client'

import React, { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { MetadataForm } from '@/components/Authoring/MetadataForm'
import { ContentSelector } from '@/components/Authoring/ContentSelector'
import { DraftGenerator, type DraftSection } from '@/components/Authoring/DraftGenerator'
import { Card } from '@/components/Common/Card'
import { Button } from '@/components/Common/Button'
import { useCurricula, useCreateCurriculum, useCreateCurriculumUnit, useCreateObjective } from '@/lib/api/curriculum'
import { apiClient } from '@/lib/api/client'

type Step = 'metadata' | 'content' | 'generate' | 'review'

interface SelectedContent {
  id: string
  title: string
  type: 'content' | 'objective' | 'standard'
  confidence?: number
}

interface AuthoringState {
  artifactType: 'curriculum' | 'lesson' | 'activity' | 'assessment'
  metadata: {
    title: string
    description: string
    grade?: string
    subject?: string
    duration?: number
    audience?: string
  }
  selectedContent: SelectedContent[]
  draft: {
    sections: DraftSection[]
    savedAt?: string
  }
}

interface CurriculumDraftUnit {
  title: string
  description: string
  objectives: { objective: string; cognitive_level: string }[]
}

export default function AuthoringStudioPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuthRequired()

  const [currentStep, setCurrentStep] = useState<Step>('metadata')
  const [state, setState] = useState<AuthoringState>({
    artifactType: 'lesson',
    metadata: {
      title: '',
      description: '',
    },
    selectedContent: [],
    draft: {
      sections: [
        { id: 'intro', title: 'Introduction', type: 'introduction', content: '', citations: [] },
        { id: 'objectives', title: 'Objectives', type: 'objectives', content: '', citations: [] },
        { id: 'activities', title: 'Activities', type: 'activities', content: '', citations: [] },
        { id: 'assessments', title: 'Assessments', type: 'assessments', content: '', citations: [] },
        { id: 'resources', title: 'Resources', type: 'resources', content: '', citations: [] },
        { id: 'closure', title: 'Closure', type: 'closure', content: '', citations: [] },
      ],
    },
  })

  const [isLoading, setIsLoading] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [isGenerating, setIsGenerating] = useState(false)
  const [curriculumPlan, setCurriculumPlan] = useState<{
    mode: 'existing' | 'new'
    curriculumId: string
    name: string
    description: string
    version: string
    units: CurriculumDraftUnit[]
  }>({
    mode: 'existing', curriculumId: '', name: '', description: '', version: '1.0',
    units: [{ title: '', description: '', objectives: [{ objective: '', cognitive_level: 'understand' }] }],
  })
  const curriculaQuery = useCurricula()
  const createCurriculumMutation = useCreateCurriculum()
  const createUnitMutation = useCreateCurriculumUnit()
  const createObjectiveMutation = useCreateObjective()

  if (!isAuthenticated) return null

  const stepTitles = {
    metadata: 'Basic Information',
    content: 'Select Content & Objectives',
    generate: 'AI Generation',
    review: 'Review & Edit',
  }

  const stepNumbers = {
    metadata: 1,
    content: 2,
    generate: 3,
    review: 4,
  }

  // Step 1: Metadata
  const handleMetadataSubmit = () => {
    setCurrentStep('content')
  }

  // Step 2: Content Selection
  const handleAddContent = (items: SelectedContent[]) => {
    setState((prev) => ({
      ...prev,
      selectedContent: items,
    }))
  }

  const handleRemoveContent = (id: string) => {
    setState((prev) => ({
      ...prev,
      selectedContent: prev.selectedContent.filter((item) => item.id !== id),
    }))
  }

  const handleContentSubmit = async () => {
    setCurrentStep('generate')
    // Trigger AI generation
    simulateGeneration()
  }

  // Simulate AI generation (in real implementation, would call API)
  const simulateGeneration = async () => {
    setIsGenerating(true)
    setGenerationProgress(0)

    // Simulate progress
    const interval = setInterval(() => {
      setGenerationProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval)
          return 95
        }
        return prev + Math.random() * 15
      })
    }, 500)

    // In real implementation, would call API to generate sections
    await new Promise((resolve) => setTimeout(resolve, 4000))

    // Update sections with generated content (mock data)
    const mockSections: DraftSection[] = [
      {
        id: 'intro',
        title: 'Introduction',
        type: 'introduction',
        content: `Welcome to this lesson on ${state.metadata.subject}! In this module, we'll explore fundamental concepts that will build a strong foundation for future learning. This lesson is designed for ${state.metadata.audience || 'your learning style'} and includes interactive activities, real-world examples, and assessment tools to help you master the content.

Throughout this lesson, you'll discover why these concepts matter in the real world and how they connect to other areas of study. Take your time working through each section, and don't hesitate to revisit concepts that need clarification.`,
        citations: ['Content Library - Resource 1', 'Standards Framework - Grade ${state.metadata.grade}'],
      },
      {
        id: 'objectives',
        title: 'Learning Objectives',
        type: 'objectives',
        content: `By the end of this lesson, you will be able to:

1. Understand and explain core concepts related to ${state.metadata.subject}
2. Apply these concepts to solve problems and answer questions
3. Analyze real-world scenarios using the knowledge gained
4. Create original work that demonstrates mastery of the material
5. Collaborate effectively with peers on learning activities`,
        citations: ['Curriculum Standards', 'Learning Objectives Database'],
      },
      {
        id: 'activities',
        title: 'Activities',
        type: 'activities',
        content: `Interactive Learning Activities:

ACTIVITY 1: Exploration (15 min)
- Start with guided discovery of key concepts
- Use interactive tools to experiment with ideas
- Discuss observations with classmates

ACTIVITY 2: Direct Application (20 min)
- Work through structured practice problems
- Apply concepts to new situations
- Receive immediate feedback on your work

ACTIVITY 3: Collaborative Project (${state.metadata.duration ? state.metadata.duration - 35 : 25} min)
- Team up with classmates for deeper exploration
- Create a presentation or artifact
- Share your learning with the group

ACTIVITY 4: Reflection (10 min)
- Reflect on what you've learned
- Consider how concepts connect to prior knowledge
- Prepare questions for clarification`,
        citations: ['Activity Library', 'Pedagogical Best Practices'],
      },
      {
        id: 'assessments',
        title: 'Assessments',
        type: 'assessments',
        content: `Assessment Methods:

FORMATIVE ASSESSMENTS (During Learning):
- Quick checks for understanding after each major concept
- Interactive quizzes to practice skills
- Peer feedback during collaborative activities
- Self-reflection prompts

SUMMATIVE ASSESSMENT (End of Lesson):
- Comprehensive assessment of mastery
- Multiple question formats (multiple choice, short answer, application)
- Real-world scenario analysis
- Project or portfolio demonstration

SCORING CRITERIA:
- Accuracy of factual knowledge (40%)
- Application and analysis (35%)
- Communication and clarity (15%)
- Effort and engagement (10%)`,
        citations: ['Assessment Framework', 'Standards Alignment Data'],
      },
      {
        id: 'resources',
        title: 'Resources',
        type: 'resources',
        content: `Additional Learning Resources:

PRIMARY SOURCES:
- Textbook chapter on ${state.metadata.subject}
- Videos demonstrating key concepts
- Interactive simulations and virtual labs
- Case studies from real-world applications

SUPPLEMENTARY MATERIALS:
- Practice problem sets with solutions
- Glossary of key terms
- Study guides for review
- Reference sheets and formulas

EXTERNAL LINKS:
- Khan Academy lessons (if applicable)
- Subject-specific educational websites
- Multimedia resources
- Library and database access

SUPPORT:
- Office hours with instructor
- Peer study groups
- Tutoring resources
- Discussion forum for questions`,
        citations: ['Resource Database', 'Content Library Catalog'],
      },
      {
        id: 'closure',
        title: 'Closure',
        type: 'closure',
        content: `Wrapping Up This Lesson:

KEY TAKEAWAYS:
- You've learned essential concepts in ${state.metadata.subject}
- You can apply these ideas to new problems
- You understand why this content matters
- You're prepared for the next lesson

REFLECTION QUESTIONS:
1. What was the most important concept you learned?
2. How does this connect to what you already knew?
3. Where might you use these skills in the real world?
4. What would you like to learn more about?

NEXT STEPS:
- Review your assessment results
- Complete any recommended extension activities
- Prepare for the next lesson in this unit
- Seek help if you have remaining questions

CONGRATULATIONS!
You've completed this lesson. Great work on your learning journey!`,
        citations: ['Instructional Design Best Practices'],
      },
    ]

    setState((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        sections: mockSections,
      },
    }))

    setGenerationProgress(100)
    clearInterval(interval)
    setIsGenerating(false)
    setCurrentStep('review')
  }

  // Step 3/4: Review & Edit
  const handleSectionChange = (sectionId: string, content: string) => {
    setState((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        sections: prev.draft.sections.map((section) =>
          section.id === sectionId ? { ...section, content } : section
        ),
      },
    }))
  }

  const handleRegenerateSection = async (sectionId: string) => {
    setState((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        sections: prev.draft.sections.map((section) =>
          section.id === sectionId ? { ...section, isRegenerating: true } : section
        ),
      },
    }))

    // Simulate regeneration
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setState((prev) => ({
      ...prev,
      draft: {
        ...prev.draft,
        sections: prev.draft.sections.map((section) =>
          section.id === sectionId
            ? {
                ...section,
                isRegenerating: false,
                content: `[Regenerated section for ${section.title}]\n\n${section.content}`,
              }
            : section
        ),
      },
    }))
  }

  const handleSaveDraft = async () => {
    setIsLoading(true)
    try {
      let curriculumId = curriculumPlan.curriculumId
      if (state.artifactType === 'curriculum' || curriculumPlan.mode === 'new') {
        const curriculum = await createCurriculumMutation.mutateAsync({
          name: curriculumPlan.name,
          description: curriculumPlan.description,
          version: curriculumPlan.version,
          grade: state.metadata.grade,
          subject: state.metadata.subject,
          status: 'draft',
        })
        curriculumId = curriculum.id
        for (const [index, unitDraft] of curriculumPlan.units.entries()) {
          const unit = await createUnitMutation.mutateAsync({
            curriculum_id: curriculumId,
            title: unitDraft.title,
            description: unitDraft.description || undefined,
            sequence: index + 1,
          })
          for (const objectiveDraft of unitDraft.objectives) {
            if (objectiveDraft.objective.trim()) {
              await createObjectiveMutation.mutateAsync({
                unit_id: unit.id,
                objective: objectiveDraft.objective.trim(),
                cognitive_level: objectiveDraft.cognitive_level,
              })
            }
          }
        }
      }

      if (state.artifactType === 'curriculum') {
        router.push('/curriculum')
        return
      }

      await apiClient.post('/api/v1/lessons', {
        curriculum_id: curriculumId,
        title: state.metadata.title,
        description: state.metadata.description,
        grade: state.metadata.grade,
        subject: state.metadata.subject,
        duration: state.metadata.duration,
        audience: state.metadata.audience,
        content_ids: state.selectedContent.filter((item) => item.type === 'content').map((item) => item.id),
        objective_ids: state.selectedContent.filter((item) => item.type === 'objective').map((item) => item.id),
        sections: state.draft.sections,
      })
      router.push('/curriculum')
    } catch (error) {
      console.error('Failed to save authored lesson:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const updatePlan = (changes: Partial<typeof curriculumPlan>) => setCurriculumPlan((plan) => ({ ...plan, ...changes }))
  const updatePlanUnit = (unitIndex: number, changes: Partial<CurriculumDraftUnit>) => updatePlan({ units: curriculumPlan.units.map((unit, index) => index === unitIndex ? { ...unit, ...changes } : unit) })
  const addPlanUnit = () => updatePlan({ units: [...curriculumPlan.units, { title: '', description: '', objectives: [{ objective: '', cognitive_level: 'understand' }] }] })
  const addPlanObjective = (unitIndex: number) => updatePlan({ units: curriculumPlan.units.map((unit, index) => index === unitIndex ? { ...unit, objectives: [...unit.objectives, { objective: '', cognitive_level: 'understand' }] } : unit) })
  const updatePlanObjective = (unitIndex: number, objectiveIndex: number, changes: Partial<CurriculumDraftUnit['objectives'][number]>) => updatePlan({ units: curriculumPlan.units.map((unit, index) => index === unitIndex ? { ...unit, objectives: unit.objectives.map((objective, index) => index === objectiveIndex ? { ...objective, ...changes } : objective) } : unit) })

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FFFFFF] to-white">
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {(['metadata', 'content', 'generate', 'review'] as const).map((step, idx) => (
              <div key={step} className="flex items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                    currentStep === step
                      ? 'bg-[#1E40AF] text-white'
                      : idx < Object.keys(stepNumbers).indexOf(currentStep)
                        ? 'bg-green-500 text-white'
                        : 'bg-[#3B82F6] text-[#0F172A]'
                  }`}
                >
                  {stepNumbers[step]}
                </div>
                <div className="ml-2">
                  <p className="text-sm font-bold text-[#0F172A]">{stepTitles[step]}</p>
                </div>

                {idx < 3 && (
                  <div
                    className={`w-12 h-0.5 mx-4 ${
                      idx < Object.keys(stepNumbers).indexOf(currentStep)
                        ? 'bg-green-500'
                        : 'bg-[#3B82F6]'
                    }`}
                  ></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          {currentStep === 'metadata' && (
            <div className="space-y-6">
              <Card variant="outlined">
                <Card.Header><h3 className="text-lg font-bold text-[#0F172A]">Curriculum Placement</h3></Card.Header>
                <Card.Body className="space-y-4">
                  <div className="flex gap-3">
                    <Button type="button" variant={curriculumPlan.mode === 'existing' ? 'primary' : 'secondary'} onClick={() => updatePlan({ mode: 'existing' })}>Existing Curriculum</Button>
                    <Button type="button" variant={curriculumPlan.mode === 'new' ? 'primary' : 'secondary'} onClick={() => updatePlan({ mode: 'new' })}>Create Curriculum</Button>
                  </div>
                  {curriculumPlan.mode === 'existing' ? (
                    <select value={curriculumPlan.curriculumId} onChange={(e) => updatePlan({ curriculumId: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" required>
                      <option value="">Select curriculum...</option>
                      {(curriculaQuery.data || []).map((curriculum) => <option key={curriculum.id} value={curriculum.id}>{curriculum.name} v{curriculum.version}</option>)}
                    </select>
                  ) : (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <input required placeholder="New curriculum name" value={curriculumPlan.name} onChange={(e) => updatePlan({ name: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
                        <input required placeholder="Version" value={curriculumPlan.version} onChange={(e) => updatePlan({ version: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg" />
                      </div>
                      <textarea placeholder="Curriculum description" value={curriculumPlan.description} onChange={(e) => updatePlan({ description: e.target.value })} className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg h-16 resize-none" />
                      {curriculumPlan.units.map((unit, unitIndex) => <div key={unitIndex} className="border border-slate-200 rounded-lg p-3 space-y-2">
                        <input required placeholder={`Unit ${unitIndex + 1} title`} value={unit.title} onChange={(e) => updatePlanUnit(unitIndex, { title: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
                        <input placeholder="Unit description" value={unit.description} onChange={(e) => updatePlanUnit(unitIndex, { description: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
                        {unit.objectives.map((objective, objectiveIndex) => <div key={objectiveIndex} className="grid grid-cols-1 md:grid-cols-[1fr_150px] gap-2">
                          <input placeholder="Learning objective" value={objective.objective} onChange={(e) => updatePlanObjective(unitIndex, objectiveIndex, { objective: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg" />
                          <select value={objective.cognitive_level} onChange={(e) => updatePlanObjective(unitIndex, objectiveIndex, { cognitive_level: e.target.value })} className="w-full px-3 py-2 border border-slate-300 rounded-lg">{['remember', 'understand', 'apply', 'analyze', 'evaluate', 'create'].map((level) => <option key={level} value={level}>{level}</option>)}</select>
                        </div>)}
                        <Button type="button" variant="secondary" size="sm" onClick={() => addPlanObjective(unitIndex)}>Add Objective</Button>
                      </div>)}
                      <Button type="button" variant="secondary" onClick={addPlanUnit}>Add Unit</Button>
                    </div>
                  )}
                </Card.Body>
              </Card>
              <MetadataForm
                artifactType={state.artifactType}
                onTypeSelect={(type) => {
                  setState((prev) => ({ ...prev, artifactType: type }))
                  if (type === 'curriculum') updatePlan({ mode: 'new', curriculumId: '' })
                }}
                metadata={state.metadata}
                onMetadataChange={(metadata) => setState((prev) => ({ ...prev, metadata: { ...prev.metadata, ...metadata } }))}
                onNext={handleMetadataSubmit}
                isLoading={isLoading}
              />
            </div>
          )}

          {currentStep === 'content' && (
            <ContentSelector
              artifactType={state.artifactType}
              selectedContent={state.selectedContent}
              onAddContent={handleAddContent}
              onRemoveContent={handleRemoveContent}
              onNext={handleContentSubmit}
              isLoading={isLoading}
            />
          )}

          {currentStep === 'generate' && (
            <div className="flex items-center justify-center py-12">
              <Card variant="outlined" className="w-full max-w-md">
                <Card.Body className="text-center space-y-4">
                  <div className="text-5xl">🔨</div>
                  <p className="font-bold text-[#0F172A]">Generating Your {state.artifactType}</p>
                  <p className="text-slate-600">
                    AI is creating a personalized draft based on your selections...
                  </p>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-[#1E40AF] h-2 rounded-full transition-all"
                      style={{ width: `${generationProgress}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-slate-600">{Math.round(generationProgress)}% complete</p>
                </Card.Body>
              </Card>
            </div>
          )}

          {currentStep === 'review' && (
            <DraftGenerator
              artifactTitle={state.metadata.title || `New ${state.artifactType}`}
              artifactType={state.artifactType}
              sections={state.draft.sections}
              onSectionChange={handleSectionChange}
              onRegenerateSection={handleRegenerateSection}
              onSaveDraft={handleSaveDraft}
              isLoading={isLoading}
              isGenerating={isGenerating}
              generationProgress={generationProgress}
            />
          )}
        </div>
      </div>
    </div>
  )
}
