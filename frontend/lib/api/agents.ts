/**
 * Agents API - Monitor workflow agents and AI provider usage
 */

import { apiClient } from './client'

export interface AgentInfo {
  id: string
  name: string
  description: string
  agent_type: string
  status: string
  workflow_count: number
  last_used?: string
}

export interface AIProviderStats {
  provider: string
  model?: string
  credential_label?: string
  workflow_agent?: string
  requests: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  estimated_cost?: number
  last_used?: string
  status: string
}

export interface AgentListResponse {
  agents: AgentInfo[]
  total: number
}

export interface AIStatsResponse {
  stats: AIProviderStats[]
  total_requests: number
  total_tokens: number
  estimated_total_cost?: number
  period: string
  start_date: string
  end_date: string
}

export async function getAgents(): Promise<AgentListResponse> {
  const response = await apiClient.get<AgentListResponse>('/api/v1/agents')
  return response.data
}

export async function getAgentDetails(agentId: string): Promise<any> {
  const response = await apiClient.get(`/api/v1/agents/${agentId}`)
  return response.data
}

export async function getAIStatistics(period: string = '30d'): Promise<AIStatsResponse> {
  const response = await apiClient.get<AIStatsResponse>(
    `/api/v1/agents/stats/ai-usage?period=${encodeURIComponent(period)}`
  )
  return response.data
}
