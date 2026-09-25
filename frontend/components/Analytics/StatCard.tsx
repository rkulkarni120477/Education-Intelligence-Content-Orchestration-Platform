'use client'

import React from 'react'
import { Card } from '@/components/Common/Card'

interface StatCardProps {
  label: string
  value: string | number
  change?: number
  icon?: string
  trend?: 'up' | 'down' | 'neutral'
  color?: 'primary' | 'success' | 'danger' | 'warning' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

const colorClasses = {
  primary: 'text-[#8B5A3C]',
  success: 'text-green-600',
  danger: 'text-red-600',
  warning: 'text-amber-600',
  info: 'text-blue-600',
}

const bgClasses = {
  primary: 'bg-[#FFF8F0]',
  success: 'bg-green-50',
  danger: 'bg-red-50',
  warning: 'bg-amber-50',
  info: 'bg-blue-50',
}

const sizeClasses = {
  sm: { value: 'text-2xl', label: 'text-sm' },
  md: { value: 'text-3xl', label: 'text-base' },
  lg: { value: 'text-4xl', label: 'text-lg' },
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  change,
  icon,
  trend = 'neutral',
  color = 'primary',
  size = 'md',
}) => {
  const sizeConfig = sizeClasses[size]

  return (
    <Card variant="outlined" className={bgClasses[color]}>
      <Card.Body>
        <div className="space-y-2">
          <div className="flex items-start justify-between">
            <div>
              <p className={`${sizeConfig.label} text-slate-600`}>{label}</p>
              <p className={`${sizeConfig.value} font-bold ${colorClasses[color]} mt-1`}>
                {value}
              </p>
            </div>
            {icon && <span className="text-3xl">{icon}</span>}
          </div>

          {change !== undefined && (
            <div className="flex items-center gap-1 mt-2">
              <span
                className={`text-sm font-bold ${
                  trend === 'up'
                    ? 'text-green-600'
                    : trend === 'down'
                      ? 'text-red-600'
                      : 'text-slate-600'
                }`}
              >
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
                {Math.abs(change)}%
              </span>
              <span className="text-xs text-slate-600">from last period</span>
            </div>
          )}
        </div>
      </Card.Body>
    </Card>
  )
}

StatCard.displayName = 'StatCard'
