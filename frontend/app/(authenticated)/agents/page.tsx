'use client'

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuthRequired } from '@/lib/hooks/useAuthRequired'
import { getAgents, getAIStatistics } from '@/lib/api/agents'
import { Card } from '@/components/Common/Card'
import { Skeleton } from '@/components/Common/Skeleton'
import { Button } from '@/components/Common/Button'
import type { AgentInfo, AIProviderStats } from '@/lib/api/agents'

export default function AgentsPage() {
  const { isAuthenticated } = useAuthRequired()
  const [aiPeriod, setAiPeriod] = useState('30d')

  // Fetch agents list
  const agentsQuery = useQuery({
    queryKey: ['agents'],
    queryFn: () => getAgents(),
  })

  // Fetch AI statistics
  const aiStatsQuery = useQuery({
    queryKey: ['ai-stats', aiPeriod],
    queryFn: () => getAIStatistics(aiPeriod),
  })

  if (!isAuthenticated) return null

  const agents = agentsQuery.data?.agents || []
  const agentStats = aiStatsQuery.data || {
    stats: [],
    total_requests: 0,
    total_tokens: 0,
    estimated_total_cost: 0,
    period: aiPeriod,
    start_date: '',
    end_date: '',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-[#0F172A]">Agents & AI Usage</h1>
        <p className="text-[#1E40AF] mt-2">
          Monitor registered workflow agents and AI provider consumption
        </p>
      </div>

      {/* Agents Section */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-[#0F172A]">Workflow Agents</h2>

        {agentsQuery.isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : agents.length === 0 ? (
          <Card variant="outlined">
            <Card.Body className="text-center text-slate-600 py-8">
              No agents registered
            </Card.Body>
          </Card>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-[#3B82F6]">
            <table className="w-full">
              <thead className="bg-[#1E40AF] text-white">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold">Agent Name</th>
                  <th className="text-left px-4 py-3 font-semibold">Description</th>
                  <th className="text-center px-4 py-3 font-semibold">Status</th>
                  <th className="text-center px-4 py-3 font-semibold">Workflows</th>
                  <th className="text-left px-4 py-3 font-semibold">Last Used</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#3B82F6]">
                {agents.map((agent: AgentInfo) => (
                  <tr key={agent.id} className="hover:bg-blue-50 transition">
                    <td className="px-4 py-3 font-medium text-[#0F172A]">{agent.name}</td>
                    <td className="px-4 py-3 text-slate-600 text-sm max-w-md">{agent.description}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                        agent.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {agent.status === 'active' ? '🟢 Active' : '⚪ Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center font-semibold text-[#1E40AF]">
                      {agent.workflow_count}
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      {agent.last_used
                        ? new Date(agent.last_used).toLocaleDateString()
                        : 'Never'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Statistics Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-[#0F172A]">AI Statistics</h2>
          <div className="flex gap-2">
            {['24h', '7d', '30d'].map((period) => (
              <Button
                key={period}
                variant={aiPeriod === period ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => setAiPeriod(period)}
              >
                {period === '24h' ? 'Last 24h' : period === '7d' ? 'Last 7d' : 'Last 30d'}
              </Button>
            ))}
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">{agentStats.total_requests}</p>
              <p className="text-sm text-slate-600 mt-2">Total Requests</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">
                {(agentStats.total_tokens / 1000).toFixed(1)}K
              </p>
              <p className="text-sm text-slate-600 mt-2">Total Tokens</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">
                ${agentStats.estimated_total_cost?.toFixed(2) || '0.00'}
              </p>
              <p className="text-sm text-slate-600 mt-2">Est. Cost</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Body className="text-center">
              <p className="text-3xl font-bold text-[#1E40AF]">{agentStats.stats.length}</p>
              <p className="text-sm text-slate-600 mt-2">Active Providers</p>
            </Card.Body>
          </Card>
        </div>

        {/* AI Provider Usage Table */}
        {aiStatsQuery.isLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : agentStats.stats.length === 0 ? (
          <Card variant="outlined">
            <Card.Body className="text-center text-slate-600 py-8">
              No AI usage data available for this period
            </Card.Body>
          </Card>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-[#3B82F6]">
            <table className="w-full">
              <thead className="bg-[#1E40AF] text-white">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold">Provider</th>
                  <th className="text-left px-4 py-3 font-semibold">Model</th>
                  <th className="text-center px-4 py-3 font-semibold">Requests</th>
                  <th className="text-center px-4 py-3 font-semibold">Input Tokens</th>
                  <th className="text-center px-4 py-3 font-semibold">Output Tokens</th>
                  <th className="text-center px-4 py-3 font-semibold">Total Tokens</th>
                  <th className="text-right px-4 py-3 font-semibold">Est. Cost</th>
                  <th className="text-center px-4 py-3 font-semibold">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#3B82F6]">
                {agentStats.stats.map((stat: AIProviderStats, idx: number) => (
                  <tr key={idx} className="hover:bg-blue-50 transition">
                    <td className="px-4 py-3 font-medium text-[#0F172A]">{stat.provider}</td>
                    <td className="px-4 py-3 text-slate-600 text-sm">{stat.model || '—'}</td>
                    <td className="px-4 py-3 text-center font-semibold">{stat.requests}</td>
                    <td className="px-4 py-3 text-center text-slate-600">
                      {(stat.input_tokens / 1000).toFixed(1)}K
                    </td>
                    <td className="px-4 py-3 text-center text-slate-600">
                      {(stat.output_tokens / 1000).toFixed(1)}K
                    </td>
                    <td className="px-4 py-3 text-center font-semibold text-[#1E40AF]">
                      {(stat.total_tokens / 1000).toFixed(1)}K
                    </td>
                    <td className="px-4 py-3 text-right font-semibold text-[#1E40AF]">
                      ${stat.estimated_cost?.toFixed(4) || '0.0000'}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`text-xs font-semibold ${
                        stat.status === 'active' ? 'text-green-700' : 'text-gray-700'
                      }`}>
                        {stat.status === 'active' ? '✓' : '—'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer Note */}
        <Card variant="default" className="bg-blue-50 border-blue-200">
          <Card.Body>
            <p className="text-sm text-blue-800">
              <strong>Note:</strong> Token counts and costs are estimated based on detected API calls.
              For actual billing, consult your provider's usage dashboard.
              Credential labels shown are safe identifiers—actual keys are never displayed.
            </p>
          </Card.Body>
        </Card>
      </div>
    </div>
  )
}
