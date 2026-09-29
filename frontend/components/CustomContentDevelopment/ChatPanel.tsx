'use client'

import React, { useState, useRef, useEffect } from 'react'
import { useCustomContentStore } from '@/lib/stores/custom-content'

interface ChatPanelProps {
  conversationId: string | null
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ conversationId }) => {
  const [prompt, setPrompt] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { conversations, sendMessage } = useCustomContentStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const conversation = conversations.find((c) => c.id === conversationId)
  const messages = conversation?.messages || []

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = async () => {
    if (!prompt.trim() || !conversationId) return

    setIsLoading(true)
    try {
      await sendMessage(conversationId, prompt, selectedFiles)
      setPrompt('')
      setSelectedFiles([])
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.currentTarget.files
    if (!files || !conversationId) return

    Array.from(files).forEach(async (file) => {
      try {
        const { uploadFile } = useCustomContentStore.getState()
        const uploadedFile = await uploadFile(conversationId, file)
        setSelectedFiles((prev) => [...prev, uploadedFile.id])
      } catch (error) {
        console.error('Error uploading file:', error)
      }
    })
  }

  const handleRemoveFile = (fileId: string) => {
    setSelectedFiles((prev) => prev.filter((id) => id !== fileId))
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

        {/* Agent Status Steps (placeholder for streaming) */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-page text-ink px-4 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <span className="animate-spin">⏳</span>
                <span className="text-sm">Processing...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Attached Files */}
      {selectedFiles.length > 0 && (
        <div className="border-t border-border px-4 py-2 bg-page/50">
          <div className="flex flex-wrap gap-2">
            {selectedFiles.map((fileId) => (
              <div
                key={fileId}
                className="flex items-center gap-2 bg-surface border border-border rounded-full px-3 py-1 text-sm"
              >
                <span>📎</span>
                <span className="text-xs text-ink-muted">{fileId}</span>
                <button
                  onClick={() => handleRemoveFile(fileId)}
                  className="hover:text-error"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Composer */}
      <div className="border-t border-border p-4 bg-surface space-y-3">
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
            disabled={isLoading}
          />

          <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={handleFileUpload}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 hover:bg-white/10 rounded transition-colors disabled:opacity-50"
              title="Upload file"
              disabled={isLoading}
            >
              📎
            </button>

            <button
              onClick={handleSendMessage}
              disabled={!prompt.trim() || isLoading}
              className="ml-auto p-2 bg-primary hover:bg-primary-hover rounded-full text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title={isLoading ? 'Stop' : 'Send'}
            >
              {isLoading ? '⏹️' : '↑'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
