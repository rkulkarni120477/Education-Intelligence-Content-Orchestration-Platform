'use client'

import { QueryClientProvider } from 'react-query'
import { queryClient } from '@/lib/api/query-client'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
