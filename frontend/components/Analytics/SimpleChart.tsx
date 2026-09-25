'use client'

import React from 'react'
import { Card } from '@/components/Common/Card'

interface ChartDataPoint {
  label: string
  value: number
}

interface SimpleChartProps {
  title: string
  data: ChartDataPoint[]
  maxValue?: number
  color?: string
}

export const SimpleChart: React.FC<SimpleChartProps> = ({
  title,
  data,
  maxValue,
  color = '#8B5A3C',
}) => {
  const max = maxValue || Math.max(...data.map((d) => d.value), 1)
  const scale = 100 / max

  return (
    <Card variant="outlined">
      <Card.Header>
        <h3 className="font-bold text-[#6B4423]">{title}</h3>
      </Card.Header>

      <Card.Body>
        <div className="space-y-4">
          {data.map((point) => (
            <div key={point.label}>
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-medium text-[#6B4423]">{point.label}</p>
                <p className="text-sm font-bold text-[#8B5A3C]">{point.value}</p>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${point.value * scale}%`,
                    backgroundColor: color,
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </Card.Body>
    </Card>
  )
}

SimpleChart.displayName = 'SimpleChart'
