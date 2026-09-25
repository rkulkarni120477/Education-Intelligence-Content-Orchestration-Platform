import { create } from 'zustand'
import { apiClient } from '../api/client'

export interface Tenant {
  id: string
  name: string
  slug: string
  type: string
  status: 'active' | 'inactive' | 'suspended'
  subscription_tier: string
  created_at: string
  updated_at: string
}

export interface Organization {
  id: string
  tenant_id: string
  name: string
  description?: string
  type?: string
  created_at: string
  updated_at: string
}

export interface TenantStore {
  tenant: Tenant | null
  organization: Organization | null
  tenants: Tenant[]
  organizations: Organization[]
  isLoading: boolean
  error: string | null

  setTenant: (tenant: Tenant) => void
  setOrganization: (org: Organization) => void
  setTenants: (tenants: Tenant[]) => void
  setOrganizations: (orgs: Organization[]) => void
  switchTenant: (tenantId: string) => Promise<void>
  switchOrganization: (orgId: string) => void
  clearError: () => void
}

export const useTenantStore = create<TenantStore>((set, get) => ({
  tenant: null,
  organization: null,
  tenants: [],
  organizations: [],
  isLoading: false,
  error: null,

  setTenant: (tenant) => {
    apiClient.setTenantId(tenant.id)
    set({ tenant })
  },

  setOrganization: (org) => set({ organization: org }),

  setTenants: (tenants) => set({ tenants }),

  setOrganizations: (orgs) => set({ organizations: orgs }),

  switchTenant: async (tenantId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<Tenant>(`/api/v1/tenants/${tenantId}`)
      const tenant = response.data

      get().setTenant(tenant)
      set({ isLoading: false })
    } catch (error: any) {
      const errorMessage = error.message || 'Failed to switch tenant'
      set({ error: errorMessage, isLoading: false })
      throw error
    }
  },

  switchOrganization: (orgId) => {
    const org = get().organizations.find((o) => o.id === orgId)
    if (org) {
      get().setOrganization(org)
    }
  },

  clearError: () => set({ error: null }),
}))
