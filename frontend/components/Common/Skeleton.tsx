import React from 'react'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'rect' | 'circle'
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'rect',
}) => {
  const baseStyles = 'bg-slate-200 animate-pulse rounded'

  const variantStyles: Record<string, string> = {
    text: 'h-4 w-full',
    rect: 'h-10 w-full',
    circle: 'h-10 w-10 rounded-full',
  }

  return <div className={`${baseStyles} ${variantStyles[variant]} ${className}`}></div>
}

// Skeleton group for loading a card
export const CardSkeleton: React.FC<{ lines?: number }> = ({ lines = 3 }) => (
  <div className="bg-white border-2 border-[#D2B48C] rounded-lg p-6 space-y-4">
    <Skeleton className="h-6 w-1/2" />
    {Array.from({ length: lines }).map((_, i) => (
      <Skeleton key={i} className="h-4 w-full" />
    ))}
  </div>
)

// Skeleton for a list
export const ListSkeleton: React.FC<{ count?: number }> = ({ count = 5 }) => (
  <div className="space-y-2">
    {Array.from({ length: count }).map((_, i) => (
      <Skeleton key={i} className="h-12 w-full rounded-lg" />
    ))}
  </div>
)

// Skeleton for table rows
export const TableRowSkeleton: React.FC<{ columns?: number }> = ({ columns = 4 }) => (
  <tr>
    {Array.from({ length: columns }).map((_, i) => (
      <td key={i} className="px-6 py-4">
        <Skeleton className="h-4 w-20" />
      </td>
    ))}
  </tr>
)
