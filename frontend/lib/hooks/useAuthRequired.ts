import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth'

export const useAuthRequired = () => {
  const router = useRouter()
  const { user, token, isAuthenticated, initializeFromStorage } = useAuthStore()

  useEffect(() => {
    // Check if running in browser
    if (typeof window === 'undefined') return

    // Store is empty on a fresh page load, so hydrate it from localStorage first
    if (!isAuthenticated()) {
      initializeFromStorage()
    }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') return

    if (!isAuthenticated()) {
      router.push('/')
    }
  }, [user, token, isAuthenticated, router])

  return { user, token, isAuthenticated: isAuthenticated() }
}
