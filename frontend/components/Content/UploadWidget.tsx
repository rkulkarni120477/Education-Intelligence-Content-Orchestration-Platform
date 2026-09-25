'use client'

import React, { useState } from 'react'
import { useUploadContent } from '@/lib/api/content'
import { Button } from '@/components/Common/Button'
import { Card } from '@/components/Common/Card'
import { Badge } from '@/components/Common/Badge'

interface UploadWidgetProps {
  onUploadComplete?: (jobId: string) => void
  onError?: (error: string) => void
}

const subjectOptions = ['Mathematics', 'English', 'Science', 'History', 'Social Studies', 'Arts', 'Physical Education']
const gradeOptions = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

export const UploadWidget: React.FC<UploadWidgetProps> = ({ onUploadComplete, onError }) => {
  const uploadMutation = useUploadContent()
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [subject, setSubject] = useState('')
  const [grade, setGrade] = useState('')
  const [tags, setTags] = useState('')
  const [isDragging, setIsDragging] = useState(false)

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFiles = e.dataTransfer.files
    if (droppedFiles.length > 0) {
      setFile(droppedFiles[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      onError?.('Please select a file to upload')
      return
    }

    if (!title.trim()) {
      onError?.('Please enter a title')
      return
    }

    try {
      const result = await uploadMutation.mutateAsync({
        file,
        title: title.trim(),
        description: description.trim() || undefined,
        subject: subject || undefined,
        grade: grade || undefined,
        tags: tags ? tags.split(',').map(t => t.trim()) : undefined,
      })

      // Reset form
      setFile(null)
      setTitle('')
      setDescription('')
      setSubject('')
      setGrade('')
      setTags('')

      onUploadComplete?.(result.id)
    } catch (error: any) {
      onError?.(error.message || 'Upload failed')
    }
  }

  return (
    <Card variant="outlined" className="max-w-2xl">
      <Card.Header>
        <h3 className="text-lg font-bold text-[#0F172A]">Upload New Content</h3>
        <p className="text-sm text-[#1E40AF] mt-1">
          Upload a PDF, Word document, or image to add to your library
        </p>
      </Card.Header>

      <form onSubmit={handleSubmit}>
        <Card.Body className="space-y-4">
          {/* File Upload Area */}
          <div
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
              isDragging
                ? 'border-[#1E40AF] bg-[#FFFFFF]'
                : 'border-[#3B82F6] hover:border-[#1E40AF] hover:bg-[#FFFFFF]'
            }`}
          >
            {file ? (
              <div>
                <p className="text-[#0F172A] font-medium">✓ File selected</p>
                <p className="text-sm text-[#1E40AF]">{file.name}</p>
                <p className="text-xs text-slate-500 mt-2">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <Button
                  type="button"
                  variant="tertiary"
                  size="sm"
                  onClick={() => setFile(null)}
                  className="mt-3"
                >
                  Change file
                </Button>
              </div>
            ) : (
              <div>
                <p className="text-[#0F172A] font-medium mb-2">
                  Drag and drop your file here, or click to select
                </p>
                <p className="text-sm text-slate-500">
                  Supported: PDF, DOCX, PPTX, JPG, PNG (Max 50MB)
                </p>
                <input
                  type="file"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-input"
                  accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png"
                />
                <label
                  htmlFor="file-input"
                  className="inline-block mt-4 px-4 py-2 bg-[#1E40AF] text-white rounded-lg cursor-pointer hover:bg-[#0F172A] transition"
                >
                  Select File
                </label>
              </div>
            )}
          </div>

          {/* Form Fields */}
          <div>
            <label className="block text-sm font-medium text-[#0F172A] mb-2">
              Title *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., 'Introduction to Algebra'"
              className="w-full px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[#0F172A] mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Brief description of the content..."
              className="w-full px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white h-20 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Subject
              </label>
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white"
              >
                <option value="">Select a subject...</option>
                {subjectOptions.map(s => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-[#0F172A] mb-2">
                Grade
              </label>
              <select
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
                className="w-full px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white"
              >
                <option value="">Select a grade...</option>
                {gradeOptions.map(g => (
                  <option key={g} value={g}>
                    Grade {g}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-[#0F172A] mb-2">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="e.g., algebra, interactive, video"
              className="w-full px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white"
            />
          </div>

          {/* Upload Status */}
          {uploadMutation.error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg text-sm">
              {(uploadMutation.error as any).message || 'Upload failed'}
            </div>
          )}
        </Card.Body>

        <Card.Footer>
          <div className="flex gap-2">
            <Button
              type="submit"
              variant="primary"
              isLoading={uploadMutation.isLoading}
              disabled={!file || !title.trim()}
            >
              {uploadMutation.isLoading ? 'Uploading...' : 'Upload Content'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setFile(null)
                setTitle('')
                setDescription('')
                setSubject('')
                setGrade('')
                setTags('')
              }}
            >
              Clear
            </Button>
          </div>
        </Card.Footer>
      </form>
    </Card>
  )
}

UploadWidget.displayName = 'UploadWidget'
