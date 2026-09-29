'use client'

import React, { useMemo, useState } from 'react'
import { useCustomContentStore } from '@/lib/stores/custom-content'
import { useFileUpload } from '@/lib/hooks/useFileUpload'

interface FileExplorerProps {
  conversationId: string | null
  onSelectFile?: (fileId: string) => void
}

export const FileExplorer: React.FC<FileExplorerProps> = ({ conversationId, onSelectFile }) => {
  const { conversations } = useCustomContentStore()
  const { downloadFile, deleteFile, renameFile } = useFileUpload(conversationId)
  const [editingFileId, setEditingFileId] = useState<string | null>(null)
  const [editingName, setEditingName] = useState('')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

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
                    <FileItem
                      key={file.id}
                      file={file}
                      isEditing={editingFileId === file.id}
                      editingName={editingName}
                      onEditStart={(name) => {
                        setEditingFileId(file.id)
                        setEditingName(name)
                      }}
                      onEditCancel={() => setEditingFileId(null)}
                      onEditSave={async () => {
                        if (editingName && editingName !== file.name) {
                          try {
                            await renameFile(file.id, editingName)
                            setEditingFileId(null)
                          } catch (error) {
                            console.error('Rename failed:', error)
                          }
                        } else {
                          setEditingFileId(null)
                        }
                      }}
                      onEditNameChange={setEditingName}
                      onDownload={() => downloadFile(file.id, file.name)}
                      onDeleteClick={() => setDeleteConfirmId(file.id)}
                      onSelectFile={() => onSelectFile?.(file.id)}
                    />
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
                    <FileItem
                      key={file.id}
                      file={file}
                      isNew
                      isEditing={editingFileId === file.id}
                      editingName={editingName}
                      onEditStart={(name) => {
                        setEditingFileId(file.id)
                        setEditingName(name)
                      }}
                      onEditCancel={() => setEditingFileId(null)}
                      onEditSave={async () => {
                        if (editingName && editingName !== file.name) {
                          try {
                            await renameFile(file.id, editingName)
                            setEditingFileId(null)
                          } catch (error) {
                            console.error('Rename failed:', error)
                          }
                        } else {
                          setEditingFileId(null)
                        }
                      }}
                      onEditNameChange={setEditingName}
                      onDownload={() => downloadFile(file.id, file.name)}
                      onDeleteClick={() => setDeleteConfirmId(file.id)}
                      onSelectFile={() => onSelectFile?.(file.id)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <DeleteConfirmDialog
          fileName={files.find((f) => f.id === deleteConfirmId)?.name || 'File'}
          onConfirm={async () => {
            try {
              await deleteFile(deleteConfirmId)
              setDeleteConfirmId(null)
            } catch (error) {
              console.error('Delete failed:', error)
            }
          }}
          onCancel={() => setDeleteConfirmId(null)}
        />
      )}
    </div>
  )
}

interface FileItemProps {
  file: any
  isNew?: boolean
  isEditing?: boolean
  editingName?: string
  onEditStart: (name: string) => void
  onEditCancel: () => void
  onEditSave: () => void
  onEditNameChange: (name: string) => void
  onDownload: () => void
  onDeleteClick: () => void
  onSelectFile: () => void
}

const FileItem: React.FC<FileItemProps> = ({
  file,
  isNew,
  isEditing,
  editingName,
  onEditStart,
  onEditCancel,
  onEditSave,
  onEditNameChange,
  onDownload,
  onDeleteClick,
  onSelectFile,
}) => {
  const [showMenu, setShowMenu] = React.useState(false)

  const fileIcon = getFileIcon(file.name)
  const fileSize = formatFileSize(file.size)

  if (isEditing) {
    return (
      <div className="px-4 py-2 bg-primary/5 border-l-2 border-primary">
        <div className="flex items-center gap-2">
          <span className="text-lg flex-shrink-0">{fileIcon}</span>
          <input
            type="text"
            value={editingName}
            onChange={(e) => onEditNameChange(e.target.value)}
            className="flex-1 bg-page text-ink px-2 py-1 rounded text-sm border border-primary focus:outline-none"
            autoFocus
          />
          <button
            onClick={onEditSave}
            className="p-1 hover:bg-primary/20 rounded text-primary text-sm"
            title="Save"
          >
            ✓
          </button>
          <button
            onClick={onEditCancel}
            className="p-1 hover:bg-error/20 rounded text-error text-sm"
            title="Cancel"
          >
            ✕
          </button>
        </div>
      </div>
    )
  }

  return (
    <div
      className="px-4 py-2 hover:bg-primary/10 transition-colors group relative"
      title={file.name}
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 flex-1 min-w-0" onClick={onSelectFile}>
          <span className="text-lg flex-shrink-0">{fileIcon}</span>
          <div className="flex-1 min-w-0 cursor-pointer">
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
          <button
            onClick={() => {
              onSelectFile()
              setShowMenu(false)
            }}
            className="w-full text-left px-4 py-2 hover:bg-primary/10 text-sm"
          >
            Open
          </button>
          <button
            onClick={() => {
              onEditStart(file.name)
              setShowMenu(false)
            }}
            className="w-full text-left px-4 py-2 hover:bg-primary/10 text-sm"
          >
            Rename
          </button>
          <button
            onClick={() => {
              onDownload()
              setShowMenu(false)
            }}
            className="w-full text-left px-4 py-2 hover:bg-primary/10 text-sm"
          >
            Download
          </button>
          <div className="border-t border-border" />
          <button
            onClick={() => {
              onDeleteClick()
              setShowMenu(false)
            }}
            className="w-full text-left px-4 py-2 hover:bg-error/10 text-error text-sm"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  )
}

interface DeleteConfirmDialogProps {
  fileName: string
  onConfirm: () => void
  onCancel: () => void
}

const DeleteConfirmDialog: React.FC<DeleteConfirmDialogProps> = ({
  fileName,
  onConfirm,
  onCancel,
}) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface border border-border rounded-lg shadow-lg p-6 max-w-sm">
        <h3 className="text-lg font-semibold text-ink mb-2">Delete File?</h3>
        <p className="text-sm text-ink-muted mb-6">
          Are you sure you want to delete <span className="font-medium text-ink">"{fileName}"</span>?
          This action cannot be undone.
        </p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-lg border border-border text-ink hover:bg-page transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-lg bg-error text-white hover:bg-error-hover transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
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
