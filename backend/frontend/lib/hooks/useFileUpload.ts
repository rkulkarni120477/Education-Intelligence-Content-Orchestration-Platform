import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'
import { CustomContentFile } from '../stores/custom-content'

export interface UploadProgress {
  fileId: string
  fileName: string
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
}

export const useFileUpload = (conversationId: string | null) => {
  const [uploads, setUploads] = useState<Record<string, UploadProgress>>({})

  const uploadFile = useCallback(
    async (file: File): Promise<CustomContentFile | null> => {
      if (!conversationId) {
        console.error('No conversation selected')
        return null
      }

      const uploadId = Math.random().toString(36)

      try {
        // Set initial upload state
        setUploads((prev) => ({
          ...prev,
          [uploadId]: {
            fileId: uploadId,
            fileName: file.name,
            progress: 0,
            status: 'uploading',
          },
        }))

        const formData = new FormData()
        formData.append('file', file)

        const response = await apiClient.post<CustomContentFile>(
          `/api/v1/custom-content/conversations/${conversationId}/files/upload`,
          formData,
          {
            headers: { 'Content-Type': 'multipart/form-data' },
            // Note: Axios doesn't support upload progress on FormData easily
            // For a more complete implementation, would use XMLHttpRequest or fetch
          }
        )

        const uploadedFile = response.data

        // Update upload state
        setUploads((prev) => ({
          ...prev,
          [uploadId]: {
            fileId: uploadedFile.id,
            fileName: uploadedFile.name,
            progress: 100,
            status: 'completed',
          },
        }))

        // Clear after 2 seconds
        setTimeout(() => {
          setUploads((prev) => {
            const next = { ...prev }
            delete next[uploadId]
            return next
          })
        }, 2000)

        return uploadedFile
      } catch (error: any) {
        const errorMsg = error.message || 'Upload failed'

        setUploads((prev) => ({
          ...prev,
          [uploadId]: {
            fileId: uploadId,
            fileName: file.name,
            progress: 0,
            status: 'error',
            error: errorMsg,
          },
        }))

        throw error
      }
    },
    [conversationId]
  )

  const uploadFiles = useCallback(
    async (files: FileList): Promise<CustomContentFile[]> => {
      const uploadedFiles: CustomContentFile[] = []

      for (let i = 0; i < files.length; i++) {
        try {
          const file = files[i]
          const uploaded = await uploadFile(file)
          if (uploaded) {
            uploadedFiles.push(uploaded)
          }
        } catch (error) {
          console.error('Error uploading file:', error)
        }
      }

      return uploadedFiles
    },
    [uploadFile]
  )

  const downloadFile = useCallback(async (fileId: string, fileName: string) => {
    try {
      const response = await apiClient.get(
        `/api/v1/custom-content/files/${fileId}/download`,
        { responseType: 'blob' }
      )

      // Create blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', fileName)
      document.body.appendChild(link)
      link.click()
      link.parentNode?.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading file:', error)
      throw error
    }
  }, [])

  const deleteFile = useCallback(async (fileId: string) => {
    try {
      await apiClient.delete(`/api/v1/custom-content/files/${fileId}`)
    } catch (error) {
      console.error('Error deleting file:', error)
      throw error
    }
  }, [])

  const renameFile = useCallback(
    async (fileId: string, newName: string): Promise<CustomContentFile | null> => {
      try {
        const response = await apiClient.patch<CustomContentFile>(
          `/api/v1/custom-content/files/${fileId}`,
          { new_name: newName }
        )
        return response.data
      } catch (error) {
        console.error('Error renaming file:', error)
        throw error
      }
    },
    []
  )

  return {
    uploads,
    uploadFile,
    uploadFiles,
    downloadFile,
    deleteFile,
    renameFile,
  }
}
