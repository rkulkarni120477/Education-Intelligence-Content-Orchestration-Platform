'use client'

import React, { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { MetadataForm } from '@/components/Authoring/MetadataForm'
import { ContentSelector } from '@/components/Authoring/ContentSelector'
import { DraftGenerator, type DraftSection } from '@/components/Authoring/DraftGenerator'
import { Card } from '@/components/Common/Card'

type Step = 'metadata' | 'content' | 'generate' | 'review'

interface SelectedContent {
  id: string
  title: string
  type: 'content' | 'objective' | 'standard'
  confidence?: number
}

interface AuthoringState {
  artifactType: 'lesson' | 'activity' | 'assessment'
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
    // In real implementation, would call API to save draft
    await new Promise((resolve) => setTimeout(resolve, 1500))
    setIsLoading(false)
    // Show success and redirect
    router.push('/authoring/drafts')
  }

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
            <MetadataForm
              artifactType={state.artifactType}
              onTypeSelect={(type) => setState((prev) => ({ ...prev, artifactType: type }))}
              metadata={state.metadata}
              onMetadataChange={(metadata) =>
                setState((prev) => ({ ...prev, metadata: { ...prev.metadata, ...metadata } }))
              }
              onNext={handleMetadataSubmit}
              isLoading={isLoading}
            />
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
