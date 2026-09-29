'use client'

import React, { useState, useRef, useEffect, ReactNode } from 'react'

export interface PanelConfig {
  id: string
  defaultWidth?: number
  min: number
  max?: number
}

export interface LayoutState {
  [panelId: string]: {
    width: number
    isVisible: boolean
  }
}

interface ResizablePanelsProps {
  panels: PanelConfig[]
  persistKey: string
  children: (layoutState: LayoutState) => ReactNode
}

export const ResizablePanels: React.FC<ResizablePanelsProps> = ({
  panels,
  persistKey,
  children,
}) => {
  // Initialize layout state with proper defaults
  const initializeLayoutState = (): LayoutState => {
    if (typeof window === 'undefined') {
      // Server-side rendering
      const layout: LayoutState = {}
      panels.forEach((panel) => {
        layout[panel.id] = {
          width: panel.defaultWidth || 300,
          isVisible: true,
        }
      })
      return layout
    }

    const savedLayout = localStorage.getItem(persistKey)
    const layout: LayoutState = {}

    panels.forEach((panel) => {
      const saved = savedLayout ? JSON.parse(savedLayout)[panel.id] : null
      const width = saved?.width || panel.defaultWidth || 300

      layout[panel.id] = {
        width: Math.max(panel.min, Math.min(width, panel.max || 800)),
        isVisible: saved?.isVisible !== false,
      }
    })

    return layout
  }

  const [layoutState, setLayoutState] = useState<LayoutState>(initializeLayoutState)
  const [isDragging, setIsDragging] = useState<string | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Persist layout to localStorage when it changes
  useEffect(() => {
    if (typeof window === 'undefined') return
    if (Object.keys(layoutState).length === 0) return

    localStorage.setItem(persistKey, JSON.stringify(layoutState))
  }, [layoutState, persistKey])

  const handleDragStart = (panelId: string) => {
    setIsDragging(panelId)
  }

  const handleDragMove = (e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return

    const containerRect = containerRef.current.getBoundingClientRect()
    const movementX = e.movementX || 0

    setLayoutState((prev) => {
      const newState = { ...prev }
      const panelConfig = panels.find((p) => p.id === isDragging)

      if (panelConfig) {
        const newWidth = prev[isDragging].width + movementX
        const constrainedWidth = Math.max(
          panelConfig.min,
          Math.min(newWidth, panelConfig.max || 800)
        )

        newState[isDragging] = {
          ...prev[isDragging],
          width: constrainedWidth,
        }
      }

      return newState
    })
  }

  const handleDragEnd = () => {
    setIsDragging(null)
  }

  // Handle mouse move and end globally
  useEffect(() => {
    if (!isDragging) return

    window.addEventListener('mousemove', handleDragMove as any)
    window.addEventListener('mouseup', handleDragEnd)

    return () => {
      window.removeEventListener('mousemove', handleDragMove as any)
      window.removeEventListener('mouseup', handleDragEnd)
    }
  }, [isDragging])

  const togglePanelVisibility = (panelId: string) => {
    setLayoutState((prev) => ({
      ...prev,
      [panelId]: {
        ...prev[panelId],
        isVisible: !prev[panelId].isVisible,
      },
    }))
  }

  return (
    <div
      ref={containerRef}
      className="flex h-full w-full bg-page"
      style={{ userSelect: isDragging ? 'none' : 'auto' }}
    >
      {children(layoutState)}

      {/* Draggable dividers */}
      {panels.map((panel, index) => {
        if (index === panels.length - 1) return null // No divider after last panel

        const currentPanelVisible = layoutState[panel.id]?.isVisible !== false
        const nextPanel = panels[index + 1]
        const nextPanelVisible = layoutState[nextPanel.id]?.isVisible !== false

        if (!currentPanelVisible || !nextPanelVisible) return null

        return (
          <div
            key={`divider-${panel.id}`}
            className="w-1 bg-border hover:bg-primary hover:opacity-50 cursor-col-resize transition-colors"
            onMouseDown={() => handleDragStart(panel.id)}
            onDoubleClick={() => togglePanelVisibility(panel.id)}
          />
        )
      })}
    </div>
  )
}
