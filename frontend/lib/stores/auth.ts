import { create } from 'zustand'
import { apiClient } from '../api/client'

export type UserRole =
  | 'tenant_admin'
  | 'standards_admin'
  | 'curriculum_admin'
  | 'content_admin'
  | 'instructional_designer'
  | 'curriculum_designer'
  | 'teacher'
  | 'reviewer'
  | 'approver'

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  tenant_id: string
  organization_id?: string
  created_at: string
}

export interface AuthStore {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null

  setUser: (user: User) => void
  setToken: (token: string) => void
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  clearError: () => void
  isAuthenticated: () => boolean
  hasRole: (role: UserRole | UserRole[]) => boolean
  initializeFromStorage: () => void
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,

  setUser: (user) => set({ user }),

  setToken: (token) => {
    apiClient.setToken(token)
    set({ token })
  },

  initializeFromStorage: () => {
    try {
      if (typeof window !== 'undefined') {
        const authData = localStorage.getItem('auth_token')
        if (authData) {
          const data = JSON.parse(authData)
          if (data.email && data.authenticated) {
            const user = {
              id: data.email,
              email: data.email,
              name: data.email.split('@')[0],
              role: 'curriculum_designer' as const,
              tenant_id: 'default',
              created_at: new Date().toISOString(),
            }
            set({ user, token: 'demo_token' })
          }
        }
      }
    } catch (err) {
      console.error('Failed to initialize auth from storage:', err)
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post<{ access_token: string; user: User }>(
        '/api/v1/auth/login',
        { email, password }
      )

      const { access_token, user } = response.data

      get().setToken(access_token)
      set({ user, token: access_token, isLoading: false })
    } catch (error: any) {
      const errorMessage = error.message || 'Login failed'
      set({ error: errorMessage, isLoading: false })
      throw error
    }
  },

  logout: () => {
    apiClient.clearToken()
    set({ user: null, token: null, error: null })
    localStorage.removeItem('auth_token')
  },

  clearError: () => set({ error: null }),

  isAuthenticated: () => {
    const { user, token } = get()
    return !!user && !!token
  },

  hasRole: (roles) => {
    const { user } = get()
    if (!user) return false

    const roleList = Array.isArray(roles) ? roles : [roles]
    return roleList.includes(user.role)
  },
}))
