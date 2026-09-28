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
  full_name?: string
  first_name?: string | null
  last_name?: string | null
  age?: number | null
  date_of_birth?: string | null
  city?: string | null
  state?: string | null
  country?: string | null
  address?: string | null
  zip_code?: string | null
  mobile_number?: string | null
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
        const token = localStorage.getItem('auth_token')
        if (!token) return

        try {
          const legacySession = JSON.parse(token)
          if (legacySession.email && legacySession.authenticated) {
            localStorage.removeItem('auth_token')
            return
          }
        } catch {
          const storedUser = localStorage.getItem('auth_user')
          if (storedUser) set({ user: JSON.parse(storedUser), token })
        }
      }
    } catch (err) {
      console.error('Failed to initialize auth from storage:', err)
    }
  },

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post<{
        access_token: string
        user_id: string
        email: string
        username: string
        tenant_id: string
        organization_id?: string
        full_name?: string | null
        first_name?: string | null
        last_name?: string | null
        age?: number | null
        date_of_birth?: string | null
        city?: string | null
        state?: string | null
        country?: string | null
        address?: string | null
        zip_code?: string | null
        mobile_number?: string | null
        role?: string
        created_at?: string
      }>(
        '/api/auth/login',
        { email, password }
      )

      const data = response.data
      const user: User = {
        id: data.user_id,
        email: data.email,
        name: [data.first_name, data.last_name].filter(Boolean).join(' ') || data.full_name || data.email,
        full_name: data.full_name || undefined,
        first_name: data.first_name,
        last_name: data.last_name,
        age: data.age,
        date_of_birth: data.date_of_birth,
        city: data.city,
        state: data.state,
        country: data.country,
        address: data.address,
        zip_code: data.zip_code,
        mobile_number: data.mobile_number,
        role: (data.role || 'teacher') as UserRole,
        tenant_id: data.tenant_id,
        organization_id: data.organization_id,
        created_at: data.created_at || new Date().toISOString(),
      }

      get().setToken(data.access_token)
      localStorage.setItem('auth_user', JSON.stringify(user))
      set({ user, token: data.access_token, isLoading: false })
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
    localStorage.removeItem('auth_user')
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
