'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useCustomContentStore } from '@/lib/stores/custom-content'
import { useFileUpload, UploadProgress } from '@/lib/hooks/useFileUpload'
import { useMessageStream } from '@/lib/hooks/useMessageStream'

interface ChatPanelProps {
  conversationId: string | null
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ conversationId }) => {
  const [prompt, setPrompt] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [dragActive, setDragActive] = useState(false)
  const { conversations } = useCustomContentStore()
  const { uploadFiles, uploads } = useFileUpload(conversationId)
  const { isStreaming, streamContent, streamError, sendMessageStream, cancelStream } =
    useMessageStream(conversationId)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const conversation = conversations.find((c) => c.id === conversationId)
  const messages = conversation?.messages || []
  const hasStreamingMessage = streamContent.length > 0 || isStreaming

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamContent])

  const handleSendMessage = async () => {
    if (!prompt.trim() || !conversationId) return

    const messageText = prompt
    const messageFiles = [...selectedFiles]

    // Clear input immediately
    setPrompt('')
    setSelectedFiles([])

    // Stream response from AI
    await sendMessageStream(messageText, messageFiles)
  }

  const handleFileUploadChange = async (files: FileList | null) => {
    if (!files || !conversationId) return

    try {
      const uploaded = await uploadFiles(files)
      uploaded.forEach((file) => {
        setSelectedFiles((prev) => [...prev, file.id])
      })
    } catch (error) {
      console.error('Error uploading files:', error)
    }
  }

  const handleRemoveFile = (fileId: string) => {
    setSelectedFiles((prev) => prev.filter((id) => id !== fileId))
  }

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    handleFileUploadChange(e.dataTransfer.files)
  }

  if (!conversationId) {
    return (
      <div className="flex items-center justify-center h-full text-ink-muted">
        <p>No conversation selected</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-surface">
      {/* Header */}
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">Chat</h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-ink-muted">
            <p className="text-sm">No messages yet.</p>
            <p className="text-xs mt-2">Start by uploading a file and asking a question.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-primary text-white'
                    : 'bg-page text-ink'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
              </div>
            </div>
          ))
        )}

        {/* Streaming Message */}
        {hasStreamingMessage && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-page text-ink">
              <p className="text-sm whitespace-pre-wrap break-words">{streamContent}</p>
              {isStreaming && (
                <div className="flex items-center gap-2 mt-2">
                  <span className="animate-spin">⏳</span>
                  <span className="text-xs text-ink-muted">Generating...</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Error Message */}
        {streamError && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-error/10 text-error border border-error/20">
              <p className="text-sm">{streamError}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Upload Progress */}
      {Object.values(uploads).length > 0 && (
        <div className="border-t border-border px-4 py-2 bg-page/50 space-y-2">
          {Object.values(uploads).map((upload) => (
            <UploadProgressChip key={upload.fileId} upload={upload} />
          ))}
        </div>
      )}

      {/* Attached Files */}
      {selectedFiles.length > 0 && (
        <div className="border-t border-border px-4 py-2 bg-page/50">
          <div className="flex flex-wrap gap-2">
            {selectedFiles.map((fileId) => {
              const file = conversation?.files.find((f) => f.id === fileId)
              return (
                <div
                  key={fileId}
                  className="flex items-center gap-2 bg-surface border border-border rounded-full px-3 py-1 text-sm"
                >
                  <span>📎</span>
                  <span className="text-xs text-ink-muted">{file?.name || fileId}</span>
                  <button
                    onClick={() => handleRemoveFile(fileId)}
                    className="hover:text-error"
                  >
                    ✕
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Composer */}
      <div
        className={`border-t border-border p-4 bg-surface space-y-3 transition-colors ${
          dragActive ? 'bg-primary/5' : ''
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {dragActive && (
          <div className="absolute inset-0 flex items-center justify-center bg-primary/10 border-2 border-dashed border-primary rounded-lg pointer-events-none">
            <p className="text-sm font-medium text-primary">Drop files to upload</p>
          </div>
        )}

        <div className="relative">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
            placeholder="Describe the content you want to create..."
            className="w-full bg-page text-ink p-3 rounded-lg border border-border resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
            rows={3}
            disabled={isStreaming}
          />

          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={(e) => handleFileUploadChange(e.currentTarget.files)}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 hover:bg-white/10 rounded transition-colors disabled:opacity-50"
              title="Upload file"
              disabled={isStreaming}
            >
              📎
            </button>

            <button
              onClick={() => {
                if (isStreaming) {
                  cancelStream()
                } else {
                  handleSendMessage()
                }
              }}
              disabled={(!prompt.trim() && !isStreaming)}
              className="ml-auto p-2 bg-primary hover:bg-primary-hover rounded-full text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title={isStreaming ? 'Cancel' : 'Send'}
            >
              {isStreaming ? '⏹️' : '↑'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

const UploadProgressChip: React.FC<{ upload: UploadProgress }> = ({ upload }) => {
  const progressPercent = Math.round(upload.progress)
  const isError = upload.status === 'error'
  const isCompleted = upload.status === 'completed'

  return (
    <div
      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
        isError
          ? 'bg-error/10 text-error'
          : isCompleted
            ? 'bg-success/10 text-success'
            : 'bg-primary/10 text-primary'
      }`}
    >
      <span className="flex-shrink-0">
        {isError ? '✕' : isCompleted ? '✓' : '⏳'}
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-xs truncate">{upload.fileName}</p>
        {!isCompleted && !isError && (
          <div className="w-full bg-white/20 rounded-full h-1 mt-1">
            <div
              className="bg-primary h-1 rounded-full transition-all"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
      </div>
      {isError && <p className="text-xs">{upload.error}</p>}
    </div>
  )
}
