import { create } from 'zustand'
import { apiClient } from '../api/client'

export interface CustomContentFile {
  id: string
  name: string
  file_type: 'upload' | 'generated'
  mime_type?: string
  size: number
  created_at: string
  is_generated: boolean
  content?: string
}

export interface CustomContentMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  message_type: string
  created_at: string
  metadata?: Record<string, any>
}

export interface Conversation {
  id: string
  title: string
  description?: string
  is_archived: boolean
  created_at: string
  updated_at: string
  message_count: number
  file_count: number
  messages?: CustomContentMessage[]
  files?: CustomContentFile[]
}

export interface CustomContentStore {
  // State
  conversations: Conversation[]
  activeConversationId: string | null
  isLoading: boolean
  error: string | null

  // Conversation methods
  createConversation: (data: { title: string; description?: string }) => Promise<Conversation>
  selectConversation: (id: string) => Promise<void>
  updateConversation: (id: string, data: Partial<Conversation>) => Promise<void>
  listConversations: () => Promise<void>
  archiveConversation: (id: string) => Promise<void>

  // File methods
  uploadFile: (conversationId: string, file: File) => Promise<CustomContentFile>
  deleteFile: (fileId: string) => Promise<void>
  downloadFile: (fileId: string) => Promise<void>

  // Message methods
  sendMessage: (conversationId: string, prompt: string, fileIds: string[]) => Promise<void>

  // Utility
  setError: (error: string | null) => void
  clearError: () => void
}

export const useCustomContentStore = create<CustomContentStore>((set, get) => ({
  conversations: [],
  activeConversationId: null,
  isLoading: false,
  error: null,

  createConversation: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post<Conversation>(
        '/api/v1/custom-content/conversations',
        data
      )
      const conversation = response.data

      set((state) => ({
        conversations: [conversation, ...state.conversations],
        activeConversationId: conversation.id,
        isLoading: false,
      }))

      return conversation
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to create conversation'
      set({ error: errorMsg, isLoading: false })
      throw error
    }
  },

  selectConversation: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<Conversation>(
        `/api/v1/custom-content/conversations/${id}`
      )
      const conversation = response.data

      set((state) => ({
        conversations: state.conversations.map((c) =>
          c.id === id ? conversation : c
        ),
        activeConversationId: id,
        isLoading: false,
      }))
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to load conversation'
      set({ error: errorMsg, isLoading: false })
      throw error
    }
  },

  updateConversation: async (id, data) => {
    set({ error: null })
    try {
      const response = await apiClient.patch<Conversation>(
        `/api/v1/custom-content/conversations/${id}`,
        data
      )
      const conversation = response.data

      set((state) => ({
        conversations: state.conversations.map((c) =>
          c.id === id ? conversation : c
        ),
      }))
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to update conversation'
      set({ error: errorMsg })
      throw error
    }
  },

  listConversations: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<Conversation[]>(
        '/api/v1/custom-content/conversations?limit=50'
      )
      set({ conversations: response.data, isLoading: false })
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to load conversations'
      set({ error: errorMsg, isLoading: false })
      throw error
    }
  },

  archiveConversation: async (id) => {
    try {
      await get().updateConversation(id, { is_archived: true })
      set((state) => ({
        conversations: state.conversations.filter((c) => c.id !== id),
      }))
    } catch (error) {
      throw error
    }
  },

  uploadFile: async (conversationId, file) => {
    set({ error: null })
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await apiClient.post<CustomContentFile>(
        `/api/v1/custom-content/conversations/${conversationId}/files/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      )

      const uploadedFile = response.data

      // Update conversation files
      set((state) => ({
        conversations: state.conversations.map((c) => {
          if (c.id === conversationId) {
            return {
              ...c,
              files: [...(c.files || []), uploadedFile],
              file_count: (c.file_count || 0) + 1,
            }
          }
          return c
        }),
      }))

      return uploadedFile
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to upload file'
      set({ error: errorMsg })
      throw error
    }
  },

  deleteFile: async (fileId) => {
    set({ error: null })
    try {
      await apiClient.delete(`/api/v1/custom-content/files/${fileId}`)

      set((state) => ({
        conversations: state.conversations.map((c) => ({
          ...c,
          files: (c.files || []).filter((f) => f.id !== fileId),
          file_count: Math.max(0, (c.file_count || 0) - 1),
        })),
      }))
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to delete file'
      set({ error: errorMsg })
      throw error
    }
  },

  downloadFile: async (fileId) => {
    set({ error: null })
    try {
      const response = await apiClient.get(
        `/api/v1/custom-content/files/${fileId}/download`,
        { responseType: 'blob' }
      )

      // Create blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      // TODO: Get filename from response headers
      link.setAttribute('download', `file-${fileId}`)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to download file'
      set({ error: errorMsg })
      throw error
    }
  },

  sendMessage: async (conversationId, prompt, fileIds) => {
    set({ error: null })
    try {
      // TODO: Implement streaming with EventSource in Phase 6
      const response = await apiClient.post(
        `/api/v1/custom-content/conversations/${conversationId}/messages`,
        {
          prompt,
          file_ids: fileIds,
          context_file_id: null,
        }
      )

      // TODO: Handle streaming events
      console.log('Message sent:', response.data)
    } catch (error: any) {
      const errorMsg = error.message || 'Failed to send message'
      set({ error: errorMsg })
      throw error
    }
  },

  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}))
