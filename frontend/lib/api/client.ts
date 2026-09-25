import axios, { AxiosInstance, AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiError {
  message: string
  status: number
  code?: string
}

export class ApiClientError extends Error implements ApiError {
  status: number
  code?: string

  constructor(message: string, status: number, code?: string) {
    super(message)
    this.status = status
    this.code = code
    this.name = 'ApiClientError'
  }
}

class ApiClient {
  private instance: AxiosInstance
  private tenantId: string | null = null

  constructor() {
    this.instance = axios.create({
      baseURL: API_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor: add tenant ID and auth token
    this.instance.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        if (this.tenantId) {
          config.headers['X-Tenant-ID'] = this.tenantId
        }

        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor: handle errors
    this.instance.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken()
          if (typeof window !== 'undefined') {
            window.location.href = '/'
          }
        }

        const message = (error.response?.data as any)?.message || error.message || 'API Error'
        const status = error.response?.status || 500

        throw new ApiClientError(message, status)
      }
    )
  }

  setTenantId(tenantId: string) {
    this.tenantId = tenantId
  }

  getTenantId(): string | null {
    return this.tenantId
  }

  setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token')
    }
    return null
  }

  clearToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  get<T>(url: string) {
    return this.instance.get<T>(url)
  }

  post<T>(url: string, data?: any) {
    return this.instance.post<T>(url, data)
  }

  put<T>(url: string, data?: any) {
    return this.instance.put<T>(url, data)
  }

  delete<T>(url: string) {
    return this.instance.delete<T>(url)
  }

  patch<T>(url: string, data?: any) {
    return this.instance.patch<T>(url, data)
  }
}

export const apiClient = new ApiClient()
