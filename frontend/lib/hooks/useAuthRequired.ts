import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth'

export const useAuthRequired = () => {
  const router = useRouter()
  const { user, token, isAuthenticated } = useAuthStore()

  useEffect(() => {
    // Check if running in browser
    if (typeof window === 'undefined') return

    if (!isAuthenticated()) {
      router.push('/')
    }
  }, [isAuthenticated, router])

  return { user, token, isAuthenticated: isAuthenticated() }
}
