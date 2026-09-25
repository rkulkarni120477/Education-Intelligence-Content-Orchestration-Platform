'use client'

import React, { useState } from 'react'
import { Button } from '@/components/Common/Button'

interface SearchBarProps {
  onSearch: (query: string) => void
  onFilter: (filters: {
    status?: string
    subject?: string
    grade?: string
  }) => void
  isLoading?: boolean
}

const statusOptions = ['uploaded', 'processing', 'extracted', 'review_required', 'published', 'failed']
const subjectOptions = ['Mathematics', 'English', 'Science', 'History', 'Social Studies', 'Arts', 'Physical Education']
const gradeOptions = ['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, onFilter, isLoading = false }) => {
  const [query, setQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [selectedStatus, setSelectedStatus] = useState<string>('')
  const [selectedSubject, setSelectedSubject] = useState<string>('')
  const [selectedGrade, setSelectedGrade] = useState<string>('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(query)
  }

  const handleFilterChange = () => {
    onFilter({
      status: selectedStatus || undefined,
      subject: selectedSubject || undefined,
      grade: selectedGrade || undefined,
    })
  }

  React.useEffect(() => {
    handleFilterChange()
  }, [selectedStatus, selectedSubject, selectedGrade])

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by title, description, or tags..."
          className="flex-1 px-4 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] bg-white"
        />
        <Button
          type="submit"
          variant="primary"
          isLoading={isLoading}
        >
          Search
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => setShowFilters(!showFilters)}
        >
          {showFilters ? 'Hide' : 'Show'} Filters
        </Button>
      </form>

      {/* Filters */}
      {showFilters && (
        <div className="bg-[#FFFFFF] border-2 border-[#3B82F6] rounded-lg p-4 grid grid-cols-3 gap-4">
          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-[#0F172A] mb-2">
              Status
            </label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] text-sm bg-white"
            >
              <option value="">All Statuses</option>
              {statusOptions.map(status => (
                <option key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Subject Filter */}
          <div>
            <label className="block text-sm font-medium text-[#0F172A] mb-2">
              Subject
            </label>
            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] text-sm bg-white"
            >
              <option value="">All Subjects</option>
              {subjectOptions.map(subject => (
                <option key={subject} value={subject}>
                  {subject}
                </option>
              ))}
            </select>
          </div>

          {/* Grade Filter */}
          <div>
            <label className="block text-sm font-medium text-[#0F172A] mb-2">
              Grade
            </label>
            <select
              value={selectedGrade}
              onChange={(e) => setSelectedGrade(e.target.value)}
              className="w-full px-3 py-2 border-2 border-[#3B82F6] rounded-lg focus:outline-none focus:border-[#1E40AF] text-sm bg-white"
            >
              <option value="">All Grades</option>
              {gradeOptions.map(grade => (
                <option key={grade} value={grade}>
                  Grade {grade}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}
    </div>
  )
}

SearchBar.displayName = 'SearchBar'
