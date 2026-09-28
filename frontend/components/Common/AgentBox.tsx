'use client'

import React from 'react'

interface AgentBoxProps {
  agentName?: string
  progress?: number
  isVisible?: boolean
}

export function AgentBox({ agentName, progress = 0, isVisible = false }: AgentBoxProps) {
  if (!isVisible || !agentName) return null

  return (
    <div className="mx-3 mb-4 p-3 bg-white/10 rounded-lg border border-orange-500/30 animate-pulse">
      <div className="space-y-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-300 mb-1">Executing Agent</p>
          <p className="text-sm font-medium text-white truncate">{agentName}</p>
        </div>

        <div className="space-y-1">
          <div className="flex justify-between items-center">
            <span className="text-xs text-slate-400">Progress</span>
            <span className="text-xs text-orange-400">{Math.round(progress)}%</span>
          </div>

          <div className="w-full bg-slate-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-orange-500 h-full rounded-full transition-all duration-300 ease-out shadow-lg shadow-orange-500/50"
              style={{ width: `${Math.min(progress, 100)}%` }}
              role="progressbar"
              aria-valuenow={Math.round(progress)}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${agentName} execution progress`}
            />
          </div>
        </div>

        <div className="text-xs text-slate-400 pt-1">
          Processing...
        </div>
      </div>
    </div>
  )
}
