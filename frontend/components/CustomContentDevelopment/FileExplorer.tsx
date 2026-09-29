'use client'

import React, { useMemo } from 'react'
import { useCustomContentStore } from '@/lib/stores/custom-content'

interface FileExplorerProps {
  conversationId: string | null
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ conversationId }) => {
  const { conversations } = useCustomContentStore()

  const conversation = useMemo(
    () => conversations.find((c) => c.id === conversationId),
    [conversations, conversationId]
  )

  const files = conversation?.files || []
  const uploadedFiles = files.filter((f) => f.file_type === 'upload')
  const generatedFiles = files.filter((f) => f.file_type === 'generated')

  if (!conversationId) {
    return (
      <div className="flex items-center justify-center h-full text-ink-muted">
        <p>No conversation selected</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full overflow-hidden bg-surface">
      {/* Header */}
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold text-ink">File Explorer</h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {files.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-ink-muted p-4">
            <p className="text-sm">No files yet.</p>
            <p className="text-xs mt-2">Upload a file or ask the agent to create one.</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {/* Uploads Section */}
            {uploadedFiles.length > 0 && (
              <div>
                <div className="px-4 py-2 bg-page/50 text-xs font-semibold text-ink-muted">
                  Uploads ({uploadedFiles.length})
                </div>
                <div className="divide-y divide-border">
                  {uploadedFiles.map((file) => (
                    <FileItem key={file.id} file={file} />
                  ))}
                </div>
              </div>
            )}

            {/* Generated Section */}
            {generatedFiles.length > 0 && (
              <div>
                <div className="px-4 py-2 bg-page/50 text-xs font-semibold text-ink-muted">
                  Generated ({generatedFiles.length})
                </div>
                <div className="divide-y divide-border">
                  {generatedFiles.map((file) => (
                    <FileItem key={file.id} file={file} isNew />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

interface FileItemProps {
  file: any
  isNew?: boolean
}

const FileItem: React.FC<FileItemProps> = ({ file, isNew }) => {
  const [showMenu, setShowMenu] = React.useState(false)

  const fileIcon = getFileIcon(file.name)
  const fileSize = formatFileSize(file.size)

  return (
    <div
      className="px-4 py-2 hover:bg-primary/10 cursor-pointer transition-colors group relative"
      title={file.name}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <span className="text-lg flex-shrink-0">{fileIcon}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-ink truncate">{file.name}</p>
            <p className="text-xs text-ink-muted">{fileSize}</p>
          </div>
          {isNew && (
            <span className="flex-shrink-0 inline-flex items-center gap-1 bg-primary/20 text-primary px-2 py-1 rounded text-xs font-medium">
              New
            </span>
          )}
        </div>
        <button
          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-white/10 rounded transition-opacity"
          onClick={() => setShowMenu(!showMenu)}
        >
          ⋯
        </button>
      </div>

      {/* Context Menu */}
      {showMenu && (
        <div className="absolute right-0 top-full mt-1 bg-surface border border-border rounded-md shadow-lg z-10 min-w-48">
          <button className="w-full text-left px-4 py-2 hover:bg-primary/10 text-sm">
            Open
          </button>
          <button className="w-full text-left px-4 py-2 hover:bg-primary/10 text-sm">
            Rename
          </button>
          <button className="w-full text-left px-4 py-2 hover:bg-primary/10 text-sm">
            Download
          </button>
          <div className="border-t border-border" />
          <button className="w-full text-left px-4 py-2 hover:bg-error/10 text-error text-sm">
            Delete
          </button>
        </div>
      )}
    </div>
  )
}

function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase() || ''

  const iconMap: Record<string, string> = {
    md: '📝',
    txt: '📄',
    json: '{}',
    html: '🌐',
    css: '🎨',
    js: '⚙️',
    ts: '⚙️',
    jsx: '⚙️',
    tsx: '⚙️',
    pdf: '📕',
    docx: '📘',
    xlsx: '📊',
    csv: '📊',
    png: '🖼️',
    jpg: '🖼️',
    jpeg: '🖼️',
    gif: '🖼️',
    mp4: '🎬',
    mp3: '🎵',
  }

  return iconMap[ext] || '📄'
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}
