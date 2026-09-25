/**
 * Recommendations Dashboard Component
 *
 * Displays curriculum improvement recommendations with
 * prioritization, filtering, and approval workflow.
 */

'use client';

import React, { useState, useMemo } from 'react';
import { useRecommendations, useApproveRecommendation, useUpdateRecommendation } from '@/lib/api/skillMapping';
import type { RecommendationItem } from '@/lib/types/phase5';

interface RecommendationsDashboardProps {
  workflowId: string;
}

export function RecommendationsDashboard({ workflowId }: RecommendationsDashboardProps) {
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data, isLoading, error } = useRecommendations(workflowId);
  const approveMutation = useApproveRecommendation(workflowId);
  const updateMutation = useUpdateRecommendation(workflowId);

  const recommendations = data?.recommendations || [];

  const filtered = useMemo(() => {
    return recommendations.filter((rec: RecommendationItem) => {
      const matchesPriority = filterPriority === 'all' || rec.priority === filterPriority;
      const matchesSearch =
        rec.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rec.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesPriority && matchesSearch;
    });
  }, [recommendations, filterPriority, searchQuery]);

  const grouped = useMemo(() => {
    const groups: Record<string, RecommendationItem[]> = {
      critical: [],
      high: [],
      medium: [],
      low: [],
    };
    filtered.forEach((rec: RecommendationItem) => {
      groups[rec.priority]?.push(rec);
    });
    return groups;
  }, [filtered]);

  const handleApprove = async (recId: string) => {
    try {
      await approveMutation.mutateAsync({ recommendationId: recId });
    } catch (err) {
      console.error('Failed to approve recommendation:', err);
    }
  };

  const handleMarkImplemented = async (recId: string) => {
    try {
      await updateMutation.mutateAsync({
        recommendationId: recId,
        status: 'implemented',
      });
    } catch (err) {
      console.error('Failed to update recommendation:', err);
    }
  };

  if (isLoading) {
    return <div className="p-6 text-center">Loading recommendations...</div>;
  }

  if (error) {
    return <div className="p-6 text-center text-red-500">Failed to load recommendations</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Curriculum Improvement Recommendations</h2>
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search recommendations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border rounded"
          />
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="px-4 py-2 border rounded bg-white"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-5 gap-3">
        <StatCard label="Total" value={recommendations.length} color="blue" />
        <StatCard label="Critical" value={grouped.critical.length} color="red" />
        <StatCard label="High" value={grouped.high.length} color="orange" />
        <StatCard label="Medium" value={grouped.medium.length} color="yellow" />
        <StatCard label="Low" value={grouped.low.length} color="green" />
      </div>

      {/* Recommendations by Priority */}
      <div className="space-y-6">
        {(['critical', 'high', 'medium', 'low'] as const).map((priority) => (
          <PrioritySection
            key={priority}
            priority={priority}
            recommendations={grouped[priority]}
            expandedId={expandedId}
            onToggleExpand={(id) => setExpandedId(expandedId === id ? null : id)}
            onApprove={handleApprove}
            onMarkImplemented={handleMarkImplemented}
            isLoading={approveMutation.isLoading || updateMutation.isLoading}
          />
        ))}
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: number;
  color: 'blue' | 'red' | 'orange' | 'yellow' | 'green';
}

function StatCard({ label, value, color }: StatCardProps) {
  const bgColor = {
    blue: 'bg-blue-50',
    red: 'bg-red-50',
    orange: 'bg-orange-50',
    yellow: 'bg-yellow-50',
    green: 'bg-green-50',
  }[color];

  const textColor = {
    blue: 'text-blue-800',
    red: 'text-red-800',
    orange: 'text-orange-800',
    yellow: 'text-yellow-800',
    green: 'text-green-800',
  }[color];

  return (
    <div className={`${bgColor} p-3 rounded-lg`}>
      <div className="text-xs text-gray-600">{label}</div>
      <div className={`text-2xl font-bold ${textColor}`}>{value}</div>
    </div>
  );
}

interface PrioritySectionProps {
  priority: 'critical' | 'high' | 'medium' | 'low';
  recommendations: RecommendationItem[];
  expandedId: string | null;
  onToggleExpand: (id: string) => void;
  onApprove: (id: string) => void;
  onMarkImplemented: (id: string) => void;
  isLoading: boolean;
}

function PrioritySection({
  priority,
  recommendations,
  expandedId,
  onToggleExpand,
  onApprove,
  onMarkImplemented,
  isLoading,
}: PrioritySectionProps) {
  const priorityConfig = {
    critical: { label: 'Critical', bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700' },
    high: { label: 'High', bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700' },
    medium: { label: 'Medium', bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700' },
    low: { label: 'Low', bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-700' },
  }[priority];

  if (recommendations.length === 0) return null;

  return (
    <div className={`border-2 ${priorityConfig.border} rounded-lg overflow-hidden`}>
      <div className={`${priorityConfig.bg} px-4 py-3 border-b font-semibold ${priorityConfig.text}`}>
        {priorityConfig.label} Priority ({recommendations.length})
      </div>

      <div className="space-y-2 p-4">
        {recommendations.map((rec) => (
          <RecommendationItem
            key={rec.id}
            recommendation={rec}
            isExpanded={expandedId === rec.id}
            onToggleExpand={() => onToggleExpand(rec.id)}
            onApprove={() => onApprove(rec.id)}
            onMarkImplemented={() => onMarkImplemented(rec.id)}
            isLoading={isLoading}
          />
        ))}
      </div>
    </div>
  );
}

interface RecommendationItemProps {
  recommendation: RecommendationItem;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onApprove: () => void;
  onMarkImplemented: () => void;
  isLoading: boolean;
}

function RecommendationItem({
  recommendation,
  isExpanded,
  onToggleExpand,
  onApprove,
  onMarkImplemented,
  isLoading,
}: RecommendationItemProps) {
  const effortColor = {
    small: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    large: 'bg-red-100 text-red-800',
  }[recommendation.estimatedEffort];

  const statusColor = {
    proposed: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    implemented: 'bg-purple-100 text-purple-800',
  }[recommendation.status];

  return (
    <div className="border rounded-lg p-3 hover:bg-gray-50">
      <div
        className="flex items-start justify-between cursor-pointer"
        onClick={onToggleExpand}
      >
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900">{recommendation.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
        </div>
        <span className="ml-4 text-gray-400">{isExpanded ? '▼' : '▶'}</span>
      </div>

      {/* Tags */}
      <div className="flex gap-2 mt-3">
        <span className={`text-xs px-2 py-1 rounded ${effortColor}`}>
          {recommendation.estimatedEffort} effort
        </span>
        <span className={`text-xs px-2 py-1 rounded ${statusColor}`}>
          {recommendation.status}
        </span>
        {recommendation.affectedSkills.length > 0 && (
          <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-800">
            {recommendation.affectedSkills.length} skills
          </span>
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t space-y-3">
          <div>
            <h5 className="font-medium text-sm text-gray-900 mb-1">Rationale</h5>
            <p className="text-sm text-gray-600">{recommendation.rationale}</p>
          </div>

          {recommendation.implementationSteps.length > 0 && (
            <div>
              <h5 className="font-medium text-sm text-gray-900 mb-1">Implementation Steps</h5>
              <ol className="list-decimal list-inside space-y-1">
                {recommendation.implementationSteps.map((step, idx) => (
                  <li key={idx} className="text-sm text-gray-600">
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {recommendation.expectedImpact && (
            <div>
              <h5 className="font-medium text-sm text-gray-900 mb-1">Expected Impact</h5>
              <p className="text-sm text-gray-600">{recommendation.expectedImpact}</p>
            </div>
          )}

          {/* Actions */}
          {recommendation.status === 'proposed' && (
            <div className="flex gap-2 pt-2">
              <button
                onClick={onApprove}
                disabled={isLoading}
                className="flex-1 bg-green-600 text-white py-2 rounded text-sm font-medium hover:bg-green-700 disabled:bg-gray-400"
              >
                Approve
              </button>
            </div>
          )}

          {recommendation.status === 'approved' && (
            <div className="flex gap-2 pt-2">
              <button
                onClick={onMarkImplemented}
                disabled={isLoading}
                className="flex-1 bg-purple-600 text-white py-2 rounded text-sm font-medium hover:bg-purple-700 disabled:bg-gray-400"
              >
                Mark Implemented
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
