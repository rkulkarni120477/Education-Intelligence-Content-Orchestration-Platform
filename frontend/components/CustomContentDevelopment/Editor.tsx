'use client'

import React, { useState, useEffect } from 'react'
import { useCustomContentStore } from '@/lib/stores/custom-content'

interface EditorTab {
  id: string
  name: string
  content: string
  isDirty: boolean
  isGenerating: boolean
  type: 'markdown' | 'plain' | 'html' | 'json' | 'code'
}

interface EditorProps {
  conversationId: string | null
  selectedFileId?: string | null
}

export const Editor: React.FC<EditorProps> = ({ conversationId, selectedFileId }) => {
  const { conversations } = useCustomContentStore()
  const [openTabs, setOpenTabs] = useState<EditorTab[]>([
    {
      id: 'welcome',
      name: 'Welcome',
      content: '# Welcome to Custom Content Development\n\nUpload files and chat with an AI agent to generate custom content.',
      isDirty: false,
      isGenerating: false,
      type: 'markdown',
    },
  ])
  const [activeTabId, setActiveTabId] = useState('welcome')

  // Handle file selection
  useEffect(() => {
    if (!selectedFileId || !conversationId) return

    const conversation = conversations.find((c) => c.id === conversationId)
    const file = conversation?.files.find((f) => f.id === selectedFileId)

    if (file) {
      // Check if file is already open
      if (openTabs.find((t) => t.id === file.id)) {
        setActiveTabId(file.id)
        return
      }

      // Determine file type for syntax highlighting
      const ext = file.name.split('.').pop()?.toLowerCase() || ''
      const typeMap: Record<string, EditorTab['type']> = {
        md: 'markdown',
        txt: 'plain',
        json: 'json',
        html: 'html',
        css: 'plain',
        js: 'code',
        ts: 'code',
        tsx: 'code',
        jsx: 'code',
      }

      const newTab: EditorTab = {
        id: file.id,
        name: file.name,
        content: file.content || '',
        isDirty: false,
        isGenerating: false,
        type: typeMap[ext] || 'plain',
      }

      setOpenTabs((tabs) => [...tabs, newTab])
      setActiveTabId(file.id)
    }
  }, [selectedFileId, conversationId, conversations])

  const activeTab = openTabs.find((t) => t.id === activeTabId)

  const handleContentChange = (newContent: string) => {
    setOpenTabs((tabs) =>
      tabs.map((t) =>
        t.id === activeTabId ? { ...t, content: newContent, isDirty: true } : t
      )
    )
  }

  const handleCloseTab = (tabId: string) => {
    setOpenTabs((tabs) => tabs.filter((t) => t.id !== tabId))
    if (activeTabId === tabId && openTabs.length > 1) {
      const nextTab = openTabs.find((t) => t.id !== tabId)
      if (nextTab) setActiveTabId(nextTab.id)
    }
  }

  const handleSave = () => {
    if (activeTab) {
      setOpenTabs((tabs) =>
        tabs.map((t) =>
          t.id === activeTabId ? { ...t, isDirty: false } : t
        )
      )
    }
  }

  return (
    <div className="flex flex-col h-full bg-page">
      {/* Tabs */}
      <div className="border-b border-border bg-surface flex overflow-x-auto">
        {openTabs.map((tab) => (
          <div
            key={tab.id}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors text-sm whitespace-nowrap ${
              activeTabId === tab.id
                ? 'border-primary text-ink'
                : 'border-transparent text-ink-muted hover:text-ink'
            }`}
          >
            <button type="button" onClick={() => setActiveTabId(tab.id)} className="flex items-center gap-2">
              <span>{tab.name}</span>
              {tab.isDirty && <span className="w-2 h-2 rounded-full bg-primary"></span>}
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation()
                handleCloseTab(tab.id)
              }}
              className="hover:bg-white/10 rounded p-0.5"
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      {/* Toolbar */}
      <div className="border-b border-border bg-surface px-4 py-2 flex items-center gap-2 text-sm">
        <button className="px-2 py-1 hover:bg-white/10 rounded transition-colors" title="Copy">
          📋
        </button>
        <button className="px-2 py-1 hover:bg-white/10 rounded transition-colors" title="Download">
          ⬇️
        </button>
        <button
          className="px-2 py-1 hover:bg-white/10 rounded transition-colors disabled:opacity-50"
          onClick={handleSave}
          disabled={!activeTab?.isDirty}
          title="Save (Ctrl+S)"
        >
          💾
        </button>
        <button className="px-2 py-1 hover:bg-white/10 rounded transition-colors" title="Preview">
          👁️
        </button>
        <button className="px-2 py-1 hover:bg-white/10 rounded transition-colors" title="Ask agent to revise">
          ✨
        </button>
      </div>

      {/* Editor Area */}
      <div className="flex-1 overflow-hidden flex">
        {activeTab ? (
          <textarea
            value={activeTab.content}
            onChange={(e) => handleContentChange(e.target.value)}
            className="flex-1 p-4 bg-page text-ink font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-primary/50"
            placeholder="Start typing or paste content here..."
          />
        ) : (
          <div className="flex items-center justify-center flex-1 text-ink-muted">
            <p>No file open</p>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="border-t border-border bg-surface px-4 py-2 text-xs text-ink-muted flex justify-between">
        <div>
          {activeTab && `${activeTab.content.length} characters`}
        </div>
        <div>
          {activeTab?.isGenerating && (
            <span className="flex items-center gap-1">
              <span className="animate-spin">⏳</span>
              Generating...
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
