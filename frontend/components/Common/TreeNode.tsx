'use client'

import React, { useState } from 'react'

interface TreeItem {
  id: string
  label: string
  code?: string
  children?: TreeItem[]
  data?: Record<string, any>
}

interface TreeNodeProps {
  item: TreeItem
  level: number
  onSelect: (item: TreeItem) => void
  selectedId?: string
  defaultExpanded?: boolean
}

export const TreeNode: React.FC<TreeNodeProps> = ({
  item,
  level,
  onSelect,
  selectedId,
  defaultExpanded = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const hasChildren = item.children && item.children.length > 0
  const isSelected = selectedId === item.id

  return (
    <div>
      {/* Node */}
      <div
        className={`
          flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition
          ${isSelected ? 'bg-[#8B5A3C] text-white' : 'hover:bg-[#FFF8F0]'}
        `}
        style={{ marginLeft: `${level * 1.5}rem` }}
        onClick={() => onSelect(item)}
      >
        {/* Expand/Collapse Button */}
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsExpanded(!isExpanded)
            }}
            className="flex-shrink-0 w-5 h-5 flex items-center justify-center text-[#6B4423] hover:bg-[#D2B48C] rounded transition"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? '▼' : '▶'}
          </button>
        ) : (
          <div className="w-5" /> /* Spacer */
        )}

        {/* Label */}
        <div className="flex-1 min-w-0">
          <p className={`truncate ${isSelected ? 'font-bold' : 'font-medium'}`}>
            {item.label}
          </p>
          {item.code && (
            <p className={`text-xs truncate ${isSelected ? 'text-[#F5DEB3]' : 'text-slate-500'}`}>
              {item.code}
            </p>
          )}
        </div>
      </div>

      {/* Children */}
      {hasChildren && isExpanded && (
        <div>
          {item.children!.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              level={level + 1}
              onSelect={onSelect}
              selectedId={selectedId}
              defaultExpanded={false}
            />
          ))}
        </div>
      )}
    </div>
  )
}

TreeNode.displayName = 'TreeNode'

/* Reusable Tree View Component */
interface TreeViewProps {
  items: TreeItem[]
  onSelect: (item: TreeItem) => void
  selectedId?: string
  expandRoot?: boolean
  searchQuery?: string
}

export const TreeView: React.FC<TreeViewProps> = ({
  items,
  onSelect,
  selectedId,
  expandRoot = true,
  searchQuery = '',
}) => {
  // Filter items based on search query
  const filterItems = (items: TreeItem[], query: string): TreeItem[] => {
    if (!query.trim()) return items

    const lowerQuery = query.toLowerCase()
    return items
      .filter((item) => {
        const matchLabel = item.label.toLowerCase().includes(lowerQuery)
        const matchCode = item.code?.toLowerCase().includes(lowerQuery)
        const hasMatchingChildren = item.children && filterItems(item.children, query).length > 0

        return matchLabel || matchCode || hasMatchingChildren
      })
      .map((item) => ({
        ...item,
        children: item.children ? filterItems(item.children, query) : item.children,
      }))
  }

  const filteredItems = filterItems(items, searchQuery)

  if (filteredItems.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        <p>No items found matching "{searchQuery}"</p>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {filteredItems.map((item) => (
        <TreeNode
          key={item.id}
          item={item}
          level={0}
          onSelect={onSelect}
          selectedId={selectedId}
          defaultExpanded={expandRoot}
        />
      ))}
    </div>
  )
}

TreeView.displayName = 'TreeView'
