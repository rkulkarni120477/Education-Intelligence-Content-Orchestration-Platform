import { useQuery, UseQueryResult } from 'react-query'
import { apiClient } from './client'

export interface UserProfile {
  id: string
  email: string
  username: string
  full_name: string | null
  first_name: string | null
  last_name: string | null
  age: number | null
  date_of_birth: string | null
  city: string | null
  state: string | null
  country: string | null
  address: string | null
  zip_code: string | null
  mobile_number: string | null
}

export const useUserProfile = (): UseQueryResult<UserProfile, Error> =>
  useQuery('user-profile', async () => {
    const response = await apiClient.get<UserProfile>('/api/users/profile')
    return response.data
  }, {
    staleTime: 5 * 60 * 1000,
  })