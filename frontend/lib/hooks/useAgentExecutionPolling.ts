import { useEffect } from 'react'
import { setAgentExecutionState } from './useAgentExecution'

const POLLING_INTERVAL = 500

export function useAgentExecutionPolling() {
  useEffect(() => {
    let pollInterval: NodeJS.Timeout

    const poll = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/agents/execution-status`
        )

        if (response.ok) {
          const data = await response.json()
          setAgentExecutionState({
            agentName: data.agent_name,
            executionId: data.execution_id,
            progress: data.progress || 0,
            isExecuting: data.is_executing || false,
          })
        }
      } catch (error) {
        console.debug('Error polling agent execution status:', error)
      }
    }

    pollInterval = setInterval(poll, POLLING_INTERVAL)
    poll()

    return () => clearInterval(pollInterval)
  }, [])
}
