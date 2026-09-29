import { useState, useCallback } from 'react'
import { apiClient } from '../api/client'
import { useCustomContentStore } from '../stores/custom-content'

export interface StreamEvent {
  type: 'start' | 'chunk' | 'end' | 'error'
  content: string
  message_id?: string
}

export const useMessageStream = (conversationId: string | null) => {
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamContent, setStreamContent] = useState('')
  const [streamError, setStreamError] = useState<string | null>(null)
  const { addMessage } = useCustomContentStore()

  const sendMessageStream = useCallback(
    async (prompt: string, fileIds: string[] = []): Promise<void> => {
      if (!conversationId) {
        setStreamError('No conversation selected')
        return
      }

      if (!prompt.trim()) {
        setStreamError('Message cannot be empty')
        return
      }

      setIsStreaming(true)
      setStreamError(null)
      setStreamContent('')

      try {
        // Create EventSource for SSE
        const apiUrl = `/api/v1/custom-content/conversations/${conversationId}/messages/stream`
        const body = new URLSearchParams({
          prompt: prompt,
          file_ids: JSON.stringify(fileIds),
        })

        // Use fetch for streaming SSE
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: body.toString(),
        })

        if (!response.ok) {
          throw new Error(`Server error: ${response.statusText}`)
        }

        const reader = response.body?.getReader()
        if (!reader) {
          throw new Error('No response body')
        }

        const decoder = new TextDecoder()
        let buffer = ''
        let messageId: string | null = null

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })

          // Process complete SSE messages
          const lines = buffer.split('\n')
          buffer = lines[lines.length - 1] // Keep incomplete line

          for (let i = 0; i < lines.length - 1; i++) {
            const line = lines[i]

            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                const event: StreamEvent = data

                if (event.type === 'start') {
                  setStreamContent('')
                } else if (event.type === 'chunk') {
                  setStreamContent((prev) => prev + event.content)
                } else if (event.type === 'end') {
                  messageId = event.message_id || null
                } else if (event.type === 'error') {
                  setStreamError(event.content)
                }
              } catch (parseError) {
                console.error('Failed to parse SSE event:', parseError)
              }
            }
          }
        }

        // Message saved on backend, sync to store
        if (messageId && streamContent) {
          // The message was already saved by backend, but we can refresh the conversation
          // to get the latest data
          await useCustomContentStore.getState().selectConversation(conversationId)
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Stream failed'
        setStreamError(errorMsg)
        console.error('Stream error:', error)
      } finally {
        setIsStreaming(false)
      }
    },
    [conversationId]
  )

  const cancelStream = useCallback(() => {
    setIsStreaming(false)
    setStreamError(null)
  }, [])

  return {
    isStreaming,
    streamContent,
    streamError,
    sendMessageStream,
    cancelStream,
  }
}
