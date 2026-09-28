import { useState, useEffect, useCallback } from 'react'

export interface AgentExecutionState {
  agentName: string | null
  progress: number
  isExecuting: boolean
  executionId: string | null
}

const INITIAL_STATE: AgentExecutionState = {
  agentName: null,
  progress: 0,
  isExecuting: false,
  executionId: null,
}

export function useAgentExecution() {
  const [state, setState] = useState<AgentExecutionState>(INITIAL_STATE)

  const startAgentExecution = useCallback((agentName: string, executionId: string) => {
    setState({
      agentName,
      progress: 0,
      isExecuting: true,
      executionId,
    })
  }, [])

  const updateProgress = useCallback((progress: number) => {
    setState((prev) => ({
      ...prev,
      progress: Math.min(progress, 100),
    }))
  }, [])

  const completeAgentExecution = useCallback(() => {
    setState(INITIAL_STATE)
  }, [])

  const setAgentName = useCallback((agentName: string | null) => {
    setState((prev) => ({
      ...prev,
      agentName,
    }))
  }, [])

  return {
    state,
    startAgentExecution,
    updateProgress,
    completeAgentExecution,
    setAgentName,
  }
}

let executionStore: AgentExecutionState = INITIAL_STATE

export function getAgentExecutionState(): AgentExecutionState {
  return executionStore
}

export function setAgentExecutionState(newState: Partial<AgentExecutionState>) {
  executionStore = { ...executionStore, ...newState }
}

export function resetAgentExecutionState() {
  executionStore = INITIAL_STATE
}
