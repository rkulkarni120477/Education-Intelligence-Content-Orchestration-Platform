/**
 * Coverage Visualization Component
 *
 * Displays skill coverage metrics with progress bars,
 * coverage breakdown, and gap identification.
 */

'use client';

import React from 'react';
import { useCoverageReport, useGapAnalysis } from '@/lib/api/skillMapping';

interface CoverageVisualizationProps {
  workflowId: string;
}

export function CoverageVisualization({ workflowId }: CoverageVisualizationProps) {
  const { data: coverageData, isLoading: coverageLoading } = useCoverageReport(workflowId);
  const { data: gapsData } = useGapAnalysis(workflowId);

  if (coverageLoading) {
    return <div className="p-6 text-center">Loading coverage data...</div>;
  }

  const coverage = coverageData?.coverage;
  const gaps = gapsData?.gaps || [];

  if (!coverage) {
    return (
      <div className="p-6 text-center text-gray-500">
        No coverage data available
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <h2 className="text-2xl font-bold">Skill Coverage Analysis</h2>

      {/* Overall Coverage */}
      <OverallCoverageCard coverage={coverage.overallCoverage} />

      {/* Coverage Breakdown */}
      <CoverageBreakdown coverage={coverage} />

      {/* Skill Coverage Details */}
      <SkillCoverageTable coverage={coverage} />

      {/* Gap Summary */}
      <GapSummary gaps={gaps} />
    </div>
  );
}

interface OverallCoverageCardProps {
  coverage: number;
}

function OverallCoverageCard({ coverage }: OverallCoverageCardProps) {
  const percentage = Math.round(coverage * 100);
  const color =
    percentage >= 80
      ? 'text-green-600'
      : percentage >= 60
        ? 'text-yellow-600'
        : 'text-red-600';

  const bgColor =
    percentage >= 80
      ? 'bg-green-50'
      : percentage >= 60
        ? 'bg-yellow-50'
        : 'bg-red-50';

  return (
    <div className={`${bgColor} rounded-lg p-6 text-center`}>
      <div className="text-sm text-gray-600 mb-2">Overall Skill Coverage</div>
      <div className={`text-5xl font-bold ${color} mb-4`}>{percentage}%</div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all ${
            percentage >= 80
              ? 'bg-green-500'
              : percentage >= 60
                ? 'bg-yellow-500'
                : 'bg-red-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

interface CoverageBreakdownProps {
  coverage: {
    coveredSkills: string[];
    partiallyCoveredSkills: string[];
    uncoveredSkills: string[];
  };
}

function CoverageBreakdown({ coverage }: CoverageBreakdownProps) {
  const total =
    coverage.coveredSkills.length +
    coverage.partiallyCoveredSkills.length +
    coverage.uncoveredSkills.length;

  return (
    <div className="grid grid-cols-3 gap-4">
      <BreakdownCard
        label="Covered"
        count={coverage.coveredSkills.length}
        total={total}
        color="green"
        description=">= 80% coverage"
      />
      <BreakdownCard
        label="Partially Covered"
        count={coverage.partiallyCoveredSkills.length}
        total={total}
        color="yellow"
        description="10-80% coverage"
      />
      <BreakdownCard
        label="Uncovered"
        count={coverage.uncoveredSkills.length}
        total={total}
        color="red"
        description="< 10% coverage"
      />
    </div>
  );
}

interface BreakdownCardProps {
  label: string;
  count: number;
  total: number;
  color: 'green' | 'yellow' | 'red';
  description: string;
}

function BreakdownCard({
  label,
  count,
  total,
  color,
  description,
}: BreakdownCardProps) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
  const bgColor = {
    green: 'bg-green-50 border-green-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    red: 'bg-red-50 border-red-200',
  }[color];

  const textColor = {
    green: 'text-green-700',
    yellow: 'text-yellow-700',
    red: 'text-red-700',
  }[color];

  const barColor = {
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  }[color];

  return (
    <div className={`border-2 ${bgColor} rounded-lg p-4`}>
      <div className="flex items-baseline gap-2 mb-2">
        <div className={`text-3xl font-bold ${textColor}`}>{count}</div>
        <div className="text-sm text-gray-600">{percentage}%</div>
      </div>
      <div className="font-medium text-gray-900 mb-1">{label}</div>
      <div className="text-xs text-gray-600 mb-3">{description}</div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
}

interface SkillCoverageTableProps {
  coverage: {
    coverageBySkill: Record<string, number>;
    totalAlignments: number;
  };
}

function SkillCoverageTable({ coverage }: SkillCoverageTableProps) {
  const skills = Object.entries(coverage.coverageBySkill)
    .sort(([, a], [, b]) => b - a);

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 font-semibold text-sm">
        Skill Coverage Details
      </div>
      <div className="divide-y">
        {skills.map(([skillId, percent]) => {
          const percentage = Math.round(percent * 100);
          const color =
            percentage >= 80
              ? 'green'
              : percentage >= 50
                ? 'yellow'
                : 'red';

          const colorClass = {
            green: 'bg-green-100 text-green-800',
            yellow: 'bg-yellow-100 text-yellow-800',
            red: 'bg-red-100 text-red-800',
          }[color];

          const barColor = {
            green: 'bg-green-500',
            yellow: 'bg-yellow-500',
            red: 'bg-red-500',
          }[color];

          return (
            <div key={skillId} className="px-4 py-3 flex items-center justify-between">
              <div className="flex-1">
                <div className="font-medium text-gray-900 mb-1">{skillId}</div>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${barColor}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
              <div className="ml-4 text-right">
                <span className={`text-sm font-bold px-2 py-1 rounded ${colorClass}`}>
                  {percentage}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

interface GapSummaryProps {
  gaps: Array<{
    id: string;
    skillName: string;
    gapSeverity: 'critical' | 'high' | 'medium' | 'low';
    currentCoverage: number;
  }>;
}

function GapSummary({ gaps }: GapSummaryProps) {
  const critical = gaps.filter((g) => g.gapSeverity === 'critical');
  const high = gaps.filter((g) => g.gapSeverity === 'high');
  const medium = gaps.filter((g) => g.gapSeverity === 'medium');
  const low = gaps.filter((g) => g.gapSeverity === 'low');

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-4 py-3 font-semibold text-sm">
        Gap Summary
      </div>
      <div className="p-4 space-y-3">
        <GapSeverityRow severity="Critical" gaps={critical} color="red" />
        <GapSeverityRow severity="High" gaps={high} color="orange" />
        <GapSeverityRow severity="Medium" gaps={medium} color="yellow" />
        <GapSeverityRow severity="Low" gaps={low} color="green" />
      </div>
    </div>
  );
}

interface GapSeverityRowProps {
  severity: string;
  gaps: Array<{ skillName: string; currentCoverage: number }>;
  color: string;
}

function GapSeverityRow({ severity, gaps, color }: GapSeverityRowProps) {
  const bgColor = {
    red: 'bg-red-50',
    orange: 'bg-orange-50',
    yellow: 'bg-yellow-50',
    green: 'bg-green-50',
  }[color];

  const textColor = {
    red: 'text-red-700',
    orange: 'text-orange-700',
    yellow: 'text-yellow-700',
    green: 'text-green-700',
  }[color];

  if (gaps.length === 0) return null;

  return (
    <div className={`${bgColor} p-3 rounded`}>
      <div className={`font-medium ${textColor} mb-2`}>
        {severity} ({gaps.length})
      </div>
      <div className="space-y-1">
        {gaps.map((gap) => (
          <div key={gap.skillName} className="text-sm text-gray-700 flex justify-between">
            <span>{gap.skillName}</span>
            <span className="font-medium">
              {Math.round(gap.currentCoverage * 100)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
