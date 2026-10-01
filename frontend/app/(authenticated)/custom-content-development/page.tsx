'use client'

import React, { useState, useEffect, useRef } from 'react'
import { useCustomContentStore } from '@/lib/stores/custom-content'
import { FileExplorer } from '@/components/CustomContentDevelopment/FileExplorer'
import { Editor } from '@/components/CustomContentDevelopment/Editor'
import { ChatPanel } from '@/components/CustomContentDevelopment/ChatPanel'
import { ResizablePanels } from '@/components/CustomContentDevelopment/ResizablePanels'
import { toast } from 'react-hot-toast'

export default function CustomContentDevelopmentPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedFileId, setSelectedFileId] = useState<string | null>(null)
  const initialized = useRef(false)

  const {
    activeConversationId,
    createConversation,
    selectConversation,
    listConversations,
  } = useCustomContentStore()

  // Reload persisted conversations and recover from stale active IDs.
  useEffect(() => {
    if (initialized.current) return
    initialized.current = true

    const initializeConversation = async () => {
      setIsLoading(true)
      try {
        await listConversations()

        const state = useCustomContentStore.getState()
        const activeConversation = state.conversations.find(
          (conversation) => conversation.id === state.activeConversationId
        )
        const conversationToSelect = activeConversation ?? state.conversations[0]

        if (conversationToSelect) {
          await selectConversation(conversationToSelect.id)
        } else {
          await createConversation({
            title: 'New Conversation',
            description: 'Custom content development session',
          })
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : 'Failed to initialize conversation'
        setError(errorMsg)
        toast.error(errorMsg)
      } finally {
        setIsLoading(false)
      }
    }

    void initializeConversation()
  }, [createConversation, listConversations, selectConversation])

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-error mb-2">Error</h1>
          <p className="text-ink-muted">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-page">
      {/* Header */}
      <header className="bg-surface border-b border-border px-6 py-4">
        <h1 className="text-2xl font-semibold text-ink">Custom Content Development</h1>
        <p className="text-sm text-ink-muted mt-1">
          Upload files, chat with an AI agent, and generate custom content
        </p>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-ink-muted">Loading conversation...</p>
            </div>
          </div>
        ) : (
          <ResizablePanels
            panels={[
              { id: 'explorer', defaultWidth: 240, min: 160, max: 400 },
              { id: 'editor', defaultWidth: undefined, min: 300 }, // flex
              { id: 'chat', defaultWidth: 400, min: 300, max: 600 }
            ]}
            persistKey="custom-content-panel-widths"
          >
            {(layoutState) => (
              <>
                {/* File Explorer Panel */}
                {layoutState.explorer.isVisible && (
                  <div
                    style={{ width: `${layoutState.explorer.width}px` }}
                    className="border-r border-border bg-surface flex flex-col"
                  >
                    <FileExplorer
                      conversationId={activeConversationId}
                      onSelectFile={setSelectedFileId}
                    />
                  </div>
                )}

                {/* Editor Panel */}
                {layoutState.editor.isVisible && (
                  <div
                    style={{ flex: 1, minWidth: '300px' }}
                    className="border-r border-border bg-page flex flex-col"
                  >
                    <Editor conversationId={activeConversationId} selectedFileId={selectedFileId} />
                  </div>
                )}

                {/* Chat Panel */}
                {layoutState.chat.isVisible && (
                  <div
                    style={{ width: `${layoutState.chat.width}px` }}
                    className="bg-surface flex flex-col"
                  >
                    <ChatPanel conversationId={activeConversationId} />
                  </div>
                )}
              </>
            )}
          </ResizablePanels>
        )}
      </div>
    </div>
  )
}
