import React from 'react'

export type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info'
export type BadgeSize = 'sm' | 'md'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  size?: BadgeSize
  className?: string
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-slate-200 text-slate-800',
  success: 'bg-green-100 text-green-800 border border-green-300',
  warning: 'bg-amber-100 text-amber-800 border border-amber-300',
  error: 'bg-red-100 text-red-800 border border-red-300',
  info: 'bg-blue-100 text-blue-800 border border-blue-300',
}

const sizeStyles: Record<string, string> = {
  sm: 'px-2 py-1 text-xs font-medium',
  md: 'px-3 py-1.5 text-sm font-medium',
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}) => (
  <span
    className={`
      inline-block rounded-full
      ${variantStyles[variant]}
      ${sizeStyles[size]}
      ${className}
    `}
  >
    {children}
  </span>
)

Badge.displayName = 'Badge'

// Status-specific badges
export const StatusBadge: React.FC<{ status: string; className?: string }> = ({
  status,
  className = '',
}) => {
  const statusStyles: Record<string, { variant: BadgeVariant; label: string }> = {
    draft: { variant: 'default', label: 'Draft' },
    processing: { variant: 'info', label: 'Processing' },
    review: { variant: 'warning', label: 'Pending Review' },
    approved: { variant: 'success', label: 'Approved' },
    published: { variant: 'success', label: 'Published' },
    rejected: { variant: 'error', label: 'Rejected' },
    pending_review: { variant: 'warning', label: 'Pending Review' },
    candidate: { variant: 'info', label: 'Candidate' },
    failed: { variant: 'error', label: 'Failed' },
  }

  const style = statusStyles[status] || { variant: 'default', label: status }

  return (
    <Badge variant={style.variant} className={className}>
      {style.label}
    </Badge>
  )
}

StatusBadge.displayName = 'StatusBadge'

// Confidence badge for alignment
export const ConfidenceBadge: React.FC<{ confidence: number; className?: string }> = ({
  confidence,
  className = '',
}) => {
  let variant: BadgeVariant = 'default'
  let label = ''

  if (confidence >= 0.8) {
    variant = 'success'
    label = `${Math.round(confidence * 100)}% confident`
  } else if (confidence >= 0.6) {
    variant = 'warning'
    label = `${Math.round(confidence * 100)}% confident`
  } else {
    variant = 'error'
    label = `${Math.round(confidence * 100)}% confident`
  }

  return (
    <Badge variant={variant} className={className}>
      {label}
    </Badge>
  )
}

ConfidenceBadge.displayName = 'ConfidenceBadge'
